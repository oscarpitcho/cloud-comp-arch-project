import time
import psutil
import sys
from datetime import datetime

MEMCACHE_PROCESS_NAME = "memcache"


def get_memcached_pid():
    pid = None

    for process in psutil.process_iter():
        if MEMCACHE_PROCESS_NAME in process.name():
            pid = process.pid
            break
    return pid


if __name__ == "__main__":
    pid = 0
    if len(sys.argv) >= 2:
        pid = int(sys.argv[1])
    else:
        pid = get_memcached_pid()

    if pid == None:
        print("No process found.")
        exit()

    memcached_process = psutil.Process(pid)

    for i in range(60 * 5):
        print(
            round(datetime.now().timestamp() * 1000), memcached_process.cpu_percent(1)
        )
