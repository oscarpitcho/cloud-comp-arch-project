import logging
import subprocess
from time import sleep

import docker
import psutil

from docker.client import DockerClient
from docker.models.containers import Container

from job import Job

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s]  [%(filename)20s:%(lineno)4d] %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
)
logger = logging.getLogger(__name__)

blackscholes = {
    'name': 'blackscholes',
    'image': 'anakli/cca:parsec_blackscholes',
    'n_threads': '1',
    'cpuset_cpus': '1'
}

canneal = {
    'image': 'anakli/cca:parsec_canneal',
    'name': 'canneal',
    'n_threads': '1',
    'cpuset_cpus': '1'
}

dedup = {
    'image': 'anakli/cca:parsec_dedup',
    'name': 'dedup',
    'n_threads': '1',
    'cpuset_cpus': '2'
}

ferret = {
    'image': 'anakli/cca:parsec_ferret',
    'name': 'ferret',
    'n_threads': '2',
    'cpuset_cpus': '2,3'
}

freqmine = {
    'image': 'anakli/cca:parsec_freqmine',
    'name': 'freqmine',
    'n_threads': '3',
    'cpuset_cpus': '1,2,3'
}

radix = {
    'image': 'anakli/cca:splash2x_radix',
    'name': 'splash2x.radix',
    'n_threads': '2',
    'cpuset_cpus': '2,3'
}

vips = {
    'image': 'anakli/cca:parsec_vips',
    'name': 'vips',
    'n_threads': '3',
    'cpuset_cpus': '1,2,3'
}

PARSEC_JOBS = [blackscholes, canneal, dedup, ferret, freqmine, radix, vips]
MEMCACHE_PROCESS_NAME = "memcache"


def initialize_jobs(client: DockerClient) -> {str, Job}:
    jobs: {str, Job} = {}
    for config in PARSEC_JOBS:
        name = config['name']
        cont: Container = client.containers.create(
            name=config['name'],
            image=config["image"],
            command=f"./bin/parsecmgmt -a run -p {name} -i native -n {config['n_threads']}",
            cpuset_cpus=config["cpuset_cpus"],
            detach=True
        )
        cont.reload()
        logger.info(f"Created container for {name}. Status: {cont.status}")

        job = Job(config, cont)
        jobs[name] = job
    return jobs


def get_memcached_pid():
    pid = None

    for process in psutil.process_iter():
        if MEMCACHE_PROCESS_NAME in process.name():
            pid = process.pid
            break
    return pid

# TODO: optimize to reach SLO. Options include specifying cores
#       e.g via: container.update(cpus=1.5)
#       pause some containers (i.e the ones critical to memcached)


def set_memcached_affinity(pid: int, cpu_affinity: str):
    command = f'sudo taskset -a -cp {cpu_affinity} {pid}'  # bind process to specific cpus
    subprocess.run(command.split(" "), stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    logger.info(f"Set affinity of memcached to {cpu_affinity}")


def run():
    logger.info("Start setting up environment...")
    client: DockerClient = docker.from_env()
    jobs: {str, Job} = initialize_jobs(client)

    job_canneal = jobs["canneal"]
    job_blackscholes = jobs["blackscholes"]
    job_dedup = jobs["dedup"]
    job_ferret = jobs["ferret"]
    job_freqmine = jobs["freqmine"]
    job_vips = jobs["vips"]
    job_radix = jobs["splash2x.radix"]

    job_canneal.next_job[1] = job_blackscholes
    job_dedup.next_job[2] = job_ferret
    job_blackscholes.next_job[1] = job_freqmine
    job_ferret.next_job[3] = job_freqmine
    job_ferret.next_job[2] = job_freqmine
    job_freqmine.next_job[1] = job_vips
    job_freqmine.next_job[2] = job_vips
    job_freqmine.next_job[3] = job_vips
    # job_vips.next_job[1] = job_radix
    job_vips.next_job[2] = job_radix
    job_vips.next_job[3] = job_radix

    remaining_jobs = {job_canneal, job_blackscholes, job_dedup, job_ferret, job_freqmine, job_vips, job_radix}

    logger.info("Environment created, start execution.")

    memcached_pid = get_memcached_pid()
    logger.info(f"Memcached PID: {memcached_pid}")
    memcached_process = psutil.Process(get_memcached_pid())
    set_memcached_affinity(memcached_pid, "0,1")

    try:
        # start first jobs
        job_canneal.start(core=1, load='high')
        job_dedup.start(core=2, load='high')
        job_ferret.start(core=3, load='high')

        sleep(0.5)

        while remaining_jobs:
            iteration_set = remaining_jobs.copy()
            utilizations = psutil.cpu_percent(percpu=True)

            status = 'medium'
            if utilizations[0] > 70:
                status = 'high'
            elif utilizations[0] < 45:
                status = 'low'
            # logger.info(f"Utilization: {utilizations}, status: {status}")
            # logger.info(f"Memcached utilization: {memcached_process.cpu_percent()}")

            for job in filter(lambda j: j.activated, iteration_set):
                if job.contact(status):
                    remaining_jobs.remove(job)
                    job.container.remove()
                    logger.info(f"Removed container for job {job.container.name}.")
                    for cpu in filter(lambda core: job.next_job.__contains__(core), job.cpus):
                        job.next_job[cpu].start(cpu, status)

            sleep(0.5)
    except KeyboardInterrupt:
        logger.info("Shutting down controller.")
        logger.info("Try to remove remaining containers")
        for job in remaining_jobs:
            job.container.reload()
            if job.container.status == "paused":
                job.container.unpause()
            job.container.reload()
            if job.container.status == "running":
                job.container.kill()
            job.container.remove()
            logger.info(f"Remove job {job.name}")
        logger.info("Shutdown completed")

    logger.info("Finished all jobs. Wait a minute before terminating mcperf.")


if __name__ == "__main__":
    run()
