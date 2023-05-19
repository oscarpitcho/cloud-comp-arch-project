import logging
from enum import IntEnum
from typing import Optional

from docker.models.containers import Container

from scheduler_logger import SchedulerLogger, JobName

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s]  [%(filename)20s:%(lineno)4d] %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
)
logger = logging.getLogger(__name__)


class LoadLevel(IntEnum):
    LOW = 1
    HIGH = 2


class Job:

    def __init__(self, config: dict, container: Container, scheduler_logger: SchedulerLogger):
        self.name: JobName = JobName[config['name']]
        self.n_threads = config['n_threads']
        self.container = container
        self.scheduler_logger = scheduler_logger
        self.next_job: {int, Job} = {}
        self.cpus = set()  # on which cores the job may run
        self.activated = False
        self.finished = False
        self.only = False

    # called when a job gets activated on additional cores
    def start(self, core: int, load_level: LoadLevel):
        if self.finished:
            if self.next_job.__contains__(core):
                self.next_job[core].start(core, load_level)
            return
        self.activated = True
        self.container.reload()
        self.cpus.add(core)
        if core == 1 and load_level >= LoadLevel.HIGH:
            return
        if self.container.status == 'created':
            self.container.update(cpuset_cpus=Job.cores_as_string(self.cpus))
            self.container.start()
            self.scheduler_logger.job_start(self.name, self.cpus, self.n_threads)
            logger.info(f"[start] Start executing {self.name.value} on {self.cpus}.")
        elif self.container.status == 'running':
            self.container.update(cpuset_cpus=Job.cores_as_string(self.cpus))
            self.scheduler_logger.update_cores(self.name, self.cpus)
            logger.info(f"[start] Job {self.name.value} continues running on {self.cpus}.")
        elif self.container.status == 'paused':
            self.container.update(cpuset_cpus=Job.cores_as_string(self.cpus))
            self.container.unpause()
            self.scheduler_logger.job_unpause(self.name)
            self.scheduler_logger.update_cores(self.name, self.cpus)
            logger.info(f"[start] Job {self.name.value} continues running on {self.cpus}.")
        else:
            logger.warning(f"[start] Job {self.name.value} is in state {self.container.status}.")

    def contact(self, load_level_change: Optional[LoadLevel], remaining_jobs: int) -> bool:
        self.container.reload()
        if self.container.status == 'exited':
            exit_code = self.container.wait()['StatusCode']
            self.scheduler_logger.job_end(self.name)
            logger.info(f"[contact] Job {self.name.value} successfully finished on {self.cpus} and code {exit_code}.")
            self.finished = True
            return True
        if not self.only and remaining_jobs == 1:
            self.only = True
            self.cpus = {2, 3}
            if self.container.status == 'created':
                self.container.update(cpuset_cpus=Job.cores_as_string(self.cpus))
                self.container.start()
                self.scheduler_logger.job_start(self.name, self.cpus, self.n_threads)
                return False
            elif self.container.status == 'paused':
                self.container.unpause()
                self.scheduler_logger.job_unpause(self.name)
            self.container.update(cpuset_cpus=Job.cores_as_string(self.cpus))
            self.scheduler_logger.update_cores(self.name, self.cpus)
            logger.info(f"[contact] last job {self.name.value} initiated.")
            return False
        if not load_level_change:
            return False
        if self.cpus.__contains__(1) and load_level_change == LoadLevel.LOW:
            self.switch_more_cores()
        elif self.cpus.__contains__(1) and load_level_change >= LoadLevel.HIGH:
            self.switch_less_cores()
        return False

    def switch_more_cores(self):
        if self.container.status == 'created':
            self.container.update(cpuset_cpus=Job.cores_as_string(self.cpus))
            self.container.start()
            self.scheduler_logger.job_start(self.name, self.cpus, self.n_threads)
            logger.info(f"[more] Start executing {self.name.value} on {self.cpus}.")
        elif self.container.status == 'paused':
            self.container.unpause()
            self.scheduler_logger.job_unpause(self.name)
            logger.info(f"[more] Job {self.name.value} continues running on {self.cpus}.")
        elif self.container.status == 'running':
            self.container.update(cpuset_cpus=Job.cores_as_string(self.cpus))
            self.scheduler_logger.update_cores(self.name, self.cpus)
            logger.info(f"[more] Job {self.name.value} continues running on {self.cpus}.")
        else:
            logger.warning(f"[more] Job {self.name.value} is in state {self.container.status}.")

    def switch_less_cores(self):
        if self.container.status == 'running':
            if len(self.cpus) == 1:
                self.container.pause()
                self.scheduler_logger.job_pause(self.name)
                logger.info(f"[less] Job {self.name.value} is now paused.")
            else:
                self.container.update(cpuset_cpus=Job.cores_as_string(self.cpus.difference({1})))
                self.scheduler_logger.update_cores(self.name, self.cpus.difference({1}))
                logger.info(f"[less] Job {self.name.value} continues running on {self.cpus.difference({1})}.")

    @staticmethod
    def cores_as_string(cores: set):
        return ",".join(map(str, cores))

    @staticmethod
    def string_as_cores(val: str):
        return list(map(int, val.split(",")))
