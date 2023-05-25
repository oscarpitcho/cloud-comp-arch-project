JOBS = ["blackscholes", "canneal", "dedup", "ferret", "freqmine", "radix", "vips"]


class Segment:
    def __init__(self, start, core):
        self.start = start
        self.end = -1
        self.core = core


class Job:
    def __init__(self, name):
        self.name = name
        self.cores = []
        self.active = {}
        self.segments = []
        self.running = False

    def start(self, time, cores):
        self.running = True
        self.cores = cores
        for core in cores:
            self.active[core] = Segment(time, core)

    def update_cores(self, time, cores):
        self.end(time)
        self.start(time, cores)

    def pause(self, time):
        self.end(time)

    def unpause(self, time):
        self.start(time, self.cores)

    def end(self, time):
        self.running = False
        next_active = self.active.copy()
        for segment in self.active.values():
            segment.end = time
            self.segments.append(segment)
            next_active.pop(segment.core)
        self.active = next_active
