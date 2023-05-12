import logging

from docker.models.containers import Container

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s]  [%(filename)20s:%(lineno)4d] %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
)
logger = logging.getLogger(__name__)


class Job:

    def __init__(self, config: dict, container: Container):
        self.name = config['name']
        self.container = container
        self.previous_load: str = 'high'
        self.next_job: {int, Job} = {}
        self.cpus = set()  # on which cores the job may run
        self.activated = False
        self.finished = False

    # called when a job gets activated on additional cores
    def start(self, core: int, load: str):
        if self.finished:
            if self.next_job.__contains__(core):
                self.next_job[core].start(core, load)
            return
        self.activated = True
        self.container.reload()
        self.cpus.add(core)
        if core == 1 and load == 'high':
            return
        if self.container.status == 'created':
            self.container.update(cpuset_cpus=Job.cores_as_string(self.cpus))
            self.container.start()
            logger.info(f"[start] Start executing {self.name} on {self.cpus}.")
        elif self.container.status == 'running':
            self.container.update(cpuset_cpus=Job.cores_as_string(self.cpus))
            logger.info(f"[start] Job {self.name} continues running on {self.cpus}.")
        elif self.container.status == 'paused':
            self.container.update(cpuset_cpus=Job.cores_as_string(self.cpus))
            self.container.unpause()
            logger.info(f"[start] Job {self.name} continues running on {self.cpus}.")
        else:
            logger.warning(f"[start] Job {self.name} is in state {self.container.status}.")

    def contact(self, load: str) -> bool:
        self.container.reload()
        if self.container.status == 'exited':
            exit_code = self.container.wait()['StatusCode']
            logger.info(f"[contact] Job {self.name} successfully finished on {self.cpus} and code {exit_code}.")
            self.finished = True
            return True
        if self.cpus.__contains__(1) and self.previous_load != 'low' and load == 'low':
            self.switch_more_cores()
        elif self.cpus.__contains__(1) and self.previous_load != 'high' and load == 'high':
            self.switch_less_cores()
        self.previous_load = load if load != 'medium' else self.previous_load
        return False

    def switch_more_cores(self):
        if self.container.status == 'created':
            self.container.update(cpuset_cpus=Job.cores_as_string(self.cpus))
            self.container.start()
            logger.info(f"[more] Start executing {self.name} on {self.cpus}.")
        elif self.container.status == 'paused':
            self.container.update(cpuset_cpus=Job.cores_as_string(self.cpus))
            self.container.unpause()
            logger.info(f"[more] Job {self.name} continues running on {self.cpus}.")
        elif self.container.status == 'running':
            self.container.update(cpuset_cpus=Job.cores_as_string(self.cpus))
            logger.info(f"[more] Job {self.name} continues running on {self.cpus}.")
        else:
            logger.warning(f"[more] Job {self.name} is in state {self.container.status}.")

    def switch_less_cores(self):
        if self.container.status == 'running':
            if len(self.cpus) == 1:
                self.container.pause()
                logger.info(f"[less] Job {self.name} is now paused.")
            else:
                self.container.update(cpuset_cpus=Job.cores_as_string(self.cpus.difference({1})))
                logger.info(f"[less] Job {self.name} continues running on {self.cpus}.")

    @staticmethod
    def cores_as_string(cores: set):
        return ",".join(map(str, cores))

    @staticmethod
    def string_as_cores(val: str):
        return list(map(int, val.split(",")))
