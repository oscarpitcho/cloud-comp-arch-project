import logging
import subprocess
from time import sleep

import docker
import psutil

from docker.client import DockerClient
from docker.models.containers import Container

from job import Job, LoadLevel
from scheduler_logger import SchedulerLogger, JobName

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s]  [%(filename)20s:%(lineno)4d] %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
)
logger = logging.getLogger(__name__)

blackscholes = {
    'name': 'BLACKSCHOLES',
    'image': 'anakli/cca:parsec_blackscholes',
    'n_threads': '1',
    'cpuset_cpus': '1',
    'type': 'parsec'
}

canneal = {
    'image': 'anakli/cca:parsec_canneal',
    'name': 'CANNEAL',
    'n_threads': '2',
    'cpuset_cpus': '1',
    'type': 'parsec'
}

dedup = {
    'image': 'anakli/cca:parsec_dedup',
    'name': 'DEDUP',
    'n_threads': '1',
    'cpuset_cpus': '2',
    'type': 'parsec'
}

ferret = {
    'image': 'anakli/cca:parsec_ferret',
    'name': 'FERRET',
    'n_threads': '2',
    'cpuset_cpus': '2,3',
    'type': 'parsec'
}

freqmine = {
    'image': 'anakli/cca:parsec_freqmine',
    'name': 'FREQMINE',
    'n_threads': '3',
    'cpuset_cpus': '1,2,3',
    'type': 'parsec'
}

radix = {
    'image': 'anakli/cca:splash2x_radix',
    'name': 'RADIX',
    'n_threads': '2',
    'cpuset_cpus': '2,3',
    'type': 'splash2x'
}

vips = {
    'image': 'anakli/cca:parsec_vips',
    'name': 'VIPS',
    'n_threads': '3',
    'cpuset_cpus': '1,2,3',
    'type': 'parsec'
}

PARSEC_JOBS = [blackscholes, canneal, dedup, ferret, freqmine, radix, vips]
MEMCACHE_PROCESS_NAME = "memcache"


def initialize_jobs(client: DockerClient, scheduler_logger: SchedulerLogger) -> {str, Job}:
    jobs: {str, Job} = {}
    for config in PARSEC_JOBS:
        name = JobName[config['name']].value
        cont: Container = client.containers.create(
            name=name,
            image=config["image"],
            command=f"./run -a run -S {config['type']} -p {name} -i native -n {config['n_threads']}",
            cpuset_cpus=config["cpuset_cpus"],
            detach=True
        )
        cont.reload()
        logger.info(f"Created container for {name}. Status: {cont.status}")

        job = Job(config, cont, scheduler_logger)
        jobs[name] = job
    return jobs


def get_memcached_pid():
    pid = None

    for process in psutil.process_iter():
        if MEMCACHE_PROCESS_NAME in process.name():
            pid = process.pid
            break
    return pid


def set_memcached_affinity(pid: int, cpu_affinity: str):
    command = f'sudo taskset -a -cp {cpu_affinity} {pid}'  # bind process to specific cpus
    subprocess.run(command.split(" "), stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    logger.info(f"Set affinity of memcached to {cpu_affinity}")


def run():
    logger.info("Find memcached PID")
    memcached_pid = get_memcached_pid()
    logger.info(f"Memcached PID: {memcached_pid}")
    memcached_process = psutil.Process(get_memcached_pid())
    set_memcached_affinity(memcached_pid, "0,1")

    logger.info("Start setting up environment...")
    scheduler_logger = SchedulerLogger()
    scheduler_logger.job_start(JobName.MEMCACHED, {0, 1}, '2')

    client: DockerClient = docker.from_env()
    jobs: {str, Job} = initialize_jobs(client, scheduler_logger)

    job_canneal = jobs[JobName.CANNEAL.value]
    job_blackscholes = jobs[JobName.BLACKSCHOLES.value]
    job_dedup = jobs[JobName.DEDUP.value]
    job_ferret = jobs[JobName.FERRET.value]
    job_freqmine = jobs[JobName.FREQMINE.value]
    job_vips = jobs[JobName.VIPS.value]
    job_radix = jobs[JobName.RADIX.value]

    job_blackscholes.next_job[1] = job_canneal
    job_dedup.next_job[2] = job_ferret
    job_canneal.next_job[1] = job_freqmine
    job_ferret.next_job[3] = job_freqmine
    job_ferret.next_job[2] = job_freqmine
    job_freqmine.next_job[1] = job_vips
    job_freqmine.next_job[2] = job_vips
    job_freqmine.next_job[3] = job_vips
    job_vips.next_job[2] = job_radix
    job_vips.next_job[3] = job_radix

    remaining_jobs = {job_canneal, job_blackscholes, job_dedup, job_ferret, job_freqmine, job_vips, job_radix}

    logger.info("Environment created, start execution.")

    try:
        prev_level = LoadLevel.HIGH

        # start first jobs
        job_blackscholes.start(core=1, load_level=prev_level)
        job_dedup.start(core=2, load_level=prev_level)
        job_ferret.start(core=3, load_level=prev_level)

        memcached_process.cpu_percent()  # always 0

        sleep(0.25)

        while remaining_jobs:
            iteration_set = remaining_jobs.copy()

            current_level = prev_level
            if prev_level == LoadLevel.HIGH:
                if memcached_process.cpu_percent() < 40:
                    current_level = LoadLevel.LOW
            else:
                if memcached_process.cpu_percent() > 40:
                    current_level = LoadLevel.HIGH
            status_change = current_level if current_level != prev_level else None
            prev_level = current_level

            if status_change:
                logger.info(f"Load level changed to: {status_change.name}")

            for job in filter(lambda j: j.activated, iteration_set):
                if job.contact(status_change, len(remaining_jobs)):
                    remaining_jobs.remove(job)
                    job.container.remove()
                    logger.info(f"Removed container for job {job.name.value}.")
                    for cpu in filter(lambda core: job.next_job.__contains__(core), job.cpus):
                        job.next_job[cpu].start(cpu, current_level)

            sleep(0.25)
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
            logger.info(f"Remove job {job.name.value}")
            scheduler_logger.custom_event(job.name, "shutdown")
        logger.info("Shutdown completed")

    scheduler_logger.end()
    logger.info("Finished all jobs or shutdown. Make sure that memcached is running for at least one minute.")


if __name__ == "__main__":
    run()
