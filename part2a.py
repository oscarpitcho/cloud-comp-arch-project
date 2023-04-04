
#!/usr/bin/env python3

import subprocess
import re
import os
import time



BENCHMARKS = ['parsec-blackscholes', 'parsec-canneal', 'parsec-dedup',
                 'parsec-ferret', 'parsec-freqmine', 'parsec-radix', 'parsec-vips']
INTERFERENCES = ['ibench-cpu', 'ibench-l1d', 'ibench-l1i', 'ibench-l2', 'ibench-llc', 'ibench-membw']

NUM_RUNS = 5

REGEX_REAL_TIME = r"real\s*([0-9]*)m(\d*.\d*)s"
REGEX_SYS_TIME = r"sys\s*([0-9]*)m(\d*.\d*)s"
REGEX_USER_TIME = r"user\s*([0-9]*)m(\d*.\d*)s"



def wait_for_interference_start(interference: str) -> None:
    while True:
        output = subprocess.run(f"kubectl get pods -o wide | grep {interference}", shell=True, capture_output=True)
        print(output.stdout.decode("utf-8"))
        if "Running" in output.stdout.decode("utf-8"):
            time.sleep(10)
            return
        #Wait one second before checking again
        time.sleep(1)

def wait_for_benchmark_completion(benchmark: str) -> None:
    while True:
        output = subprocess.run(f"kubectl get jobs -o wide | grep {benchmark}", shell=True, capture_output=True)
        print(output.stdout.decode("utf-8"))
        if "1/1" in output.stdout.decode("utf-8"):
            time.sleep(2)
            return
        #Wait one second before checking again
        time.sleep(1)
    
#Runs the benchmark and returns the real, sys and usr time   
def run_benchmark(benchmark: str, run: int):
    subprocess.run(f"kubectl create -f parsec-benchmarks/part2a/{benchmark}.yaml", shell=True)

    #This waits synchronously until benchmark is done
    wait_for_benchmark_completion(benchmark)
    
    output = subprocess.run(f"""kubectl logs $(kubectl get pods --selector=job-name={benchmark} --output=jsonpath='{{.items[*].metadata.name}}\')""", shell=True, capture_output=True)
    output = output.stdout.decode("utf-8")

    real_time_min, real_time_sec = re.findall(REGEX_REAL_TIME, output)[0]
    sys_time_min, sys_time_sec = re.findall(REGEX_SYS_TIME, output)[0]
    user_time_min, usr_time_sec = re.findall(REGEX_USER_TIME, output)[0]


    real_time = float(real_time_min) * 60 + float(real_time_sec)
    sys_time = float(sys_time_min) * 60 + float(sys_time_sec)
    user_time = float(user_time_min) * 60 + float(usr_time_sec)
    return (real_time, sys_time, user_time)


def main() -> int:
    print("Removing previous results folder...")
    subprocess.run("rm -r -f Task2a/results", shell=True)
    os.mkdir("Task2a/results")

    res = {}
    for benchmark in BENCHMARKS:
        res[benchmark] = {"no_int": [], "with_int": []}
        print("Running benchmark: " + benchmark + "...")
        os.mkdir("Task2a/results/" + benchmark)


        #Getting the result with no interference
        #for i in range(NUM_RUNS):
            #int_res = run_benchmark(benchmark, i)
            #res[benchmark]["no_int"].append(int_res)



        for interference in INTERFERENCES:
            print(subprocess.run("pwd", shell=True, capture_output=True).stdout.decode("utf-8"))
            subprocess.run(f"kubectl create -f interference-parsec/{interference}.yaml", shell=True)
            wait_for_interference_start(interference)

            print(f"Interference: {interference} started, running benchmark: {benchmark}...")
            for i in range(NUM_RUNS):

                int_res = run_benchmark(benchmark, i)
                res[benchmark]["with_int"].append(int_res)

                print(f"Run {i + 1} of {benchmark} with {interference} done")

                # Deleting benchmark job between runs
                subprocess.run(f"kubectl delete jobs/{benchmark}", shell=True)
                #Sleep one sec for safety
                time.sleep(1)
            
            #This is synchronous, we delete the interference before moving on to the next interference
            subprocess.run(f"kubectl delete -f interference-parsec/{interference}.yaml", shell=True)


    #Write results to file for later analysis
    # Format: {benchmark: {no_int: [(real, sys, usr), ...], with_int: [(real, sys, usr), ...]}}
    # with_int is a list of tuples, one for each interference
    # Each tuple is a list of 3 tuples, one for each run

    with open("Task2a/results/results.txt", "w") as f:
        f.write(str(res))   
        
        
if __name__ == "__main__":
    main()
    