# this script contains useful functions in order to solve tasks 4.2-4.4
from datetime import datetime
import numpy as np

import dateutil.parser
import pandas as pd

JOBS: set = {"blackscholes", "canneal", "dedup", "ferret", "freqmine", "radix", "vips", "all"}


def calc_and_print_runtimes():
    summary = []
    for i in range(3):
        with open(f"submission/part_4_4_results_group_054/jobs_{i + 1}.txt", 'r') as file:
            jobs = {}
            start_time = -1
            end_time = -1
            for line in file.readlines():
                tokens = line.replace("\n", "").split(" ")

                date = dateutil.parser.isoparse(tokens[0]).timestamp()  # POSIX timestamp (float in seconds)
                cmd = tokens[1]
                job = tokens[2]

                if job not in JOBS:
                    continue

                if cmd == "start":
                    if jobs.__contains__(job):
                        print("Error: Found invalid start")
                    if start_time == -1:
                        start_time = date

                    jobs[job] = {'last': date, 'total': 0.0}
                elif cmd == "pause":
                    if jobs[job]['last'] == -1:
                        print("Error: Found invalid pause")

                    last = jobs[job]['last']
                    total = jobs[job]['total']
                    jobs[job]['last'] = -1
                    jobs[job]['total'] = total + date - last
                elif cmd == "unpause":
                    if jobs[job]['last'] != -1:
                        print("Error: Found invalid unpause")

                    jobs[job]['last'] = date
                elif cmd == "end":
                    if jobs[job]['last'] == -1:
                        print("Error: Found invalid end")
                    end_time = date

                    last = jobs[job]['last']
                    total = jobs[job]['total']

                    jobs[job]['last'] = -1
                    jobs[job]['total'] = total + date - last
            jobs['all'] = {'total': end_time - start_time}
            summary.append(jobs)

    for job in JOBS:
        arr = np.array(list(map(lambda entry: entry[job]['total'], summary)))
        print("{:15s} avg: {:7.2f} std: {:5.2f}".format(job, arr.mean(), arr.std()))


if __name__ == "__main__":
    # delete lines 1-3 from file
    """
    df = pd.read_csv('submission/part_4_3_results_group_054/mcperf_1.txt', delim_whitespace=True)
    df = df.iloc[:720]
    p95 = df["p95"]
    print(p95[p95 > 1000].count())
    print(p95[p95 > 1000].count() / 720)
    """

    calc_and_print_runtimes()
