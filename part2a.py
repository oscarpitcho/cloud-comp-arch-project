
#!/usr/bin/env python3

import subprocess
import re
import os
import numpy as np
import time



BENCHMARKS = ['parsec-blackscholes', 'parsec-canneal', 'parsec-dedup','parsec-ferret', 'parsec-freqmine', 'parsec-radix', 'parsec-vips']
INTERFERENCES = ['ibench-cpu','ibench-l1d', 'ibench-l1i', 'ibench-l2', 'ibench-llc', 'ibench-membw']

NUM_RUNS = 5

REGEX_REAL_TIME = r"real\s*([0-9]*)m(\d*.\d*)s"
REGEX_SYS_TIME = r"sys\s*([0-9]*)m(\d*.\d*)s"
REGEX_USER_TIME = r"user\s*([0-9]*)m(\d*.\d*)s"


#Runs interference and returns once it has started.
def run_interference_and_wait(interference: str) -> None:
    subprocess.run(f"kubectl create -f interference-parsec/{interference}.yaml", shell=True)

    while True:
        output = subprocess.run(f"kubectl get pods -o wide | grep {interference}", shell=True, capture_output=True)
        print(output.stdout.decode("utf-8"))
        if "Running" in output.stdout.decode("utf-8"):
            time.sleep(10)
            return
        #Wait one second before checking again
        time.sleep(1)


#Runs benchmark and returns once it has completed.
def run_benchmark_and_wait(benchmark: str) -> None:
    subprocess.run(f"kubectl create -f parsec-benchmarks/part2a/{benchmark}.yaml", shell=True)

    while True:
        output = subprocess.run(f"kubectl get jobs -o wide | grep {benchmark}", shell=True, capture_output=True)
        print(output.stdout.decode("utf-8"))
        if "1/1" in output.stdout.decode("utf-8"):
            time.sleep(2)
            return
        #Wait one second before checking again
        time.sleep(1)
    
#Runs the benchmark and returns the real, sys and usr time, also deletes the job   
def run_benchmark(benchmark: str, run: int):

    #This waits synchronously until benchmark is done
    run_benchmark_and_wait(benchmark)
    
    output = subprocess.run(f"""kubectl logs $(kubectl get pods --selector=job-name={benchmark} --output=jsonpath='{{.items[*].metadata.name}}\')""", shell=True, capture_output=True)
    output = output.stdout.decode("utf-8")

    real_time_min, real_time_sec = re.findall(REGEX_REAL_TIME, output)[0]
    sys_time_min, sys_time_sec = re.findall(REGEX_SYS_TIME, output)[0]
    user_time_min, usr_time_sec = re.findall(REGEX_USER_TIME, output)[0]


    real_time = float(real_time_min) * 60 + float(real_time_sec)
    sys_time = float(sys_time_min) * 60 + float(sys_time_sec)
    user_time = float(user_time_min) * 60 + float(usr_time_sec)

    subprocess.run(f"kubectl delete jobs/{benchmark}", shell=True)
    return (real_time, sys_time, user_time)


def main() -> int:
    print("Removing previous results folder...")
    subprocess.run("rm -r -f Task2a/results", shell=True)
    os.mkdir("Task2a/results")



    res = {}

    for benchmark in BENCHMARKS:
        res[benchmark] = {}
        print(f"Running benchmark: {benchmark}..., with no interference")
        
        run_results = []
        for i in range(NUM_RUNS):

            int_res = run_benchmark(benchmark, i)
            run_results.append(int_res)
        
        res[benchmark]["no_int"] = run_results


    for interference in INTERFERENCES:
        print("Running interference: " + interference + "...")

        run_interference_and_wait(interference)


        for benchmark in BENCHMARKS:

            print("Running benchmark: " + benchmark  + ", with interference: " + interference + "...")

            run_results = []
            for i in range(NUM_RUNS):

                int_res = run_benchmark(benchmark, i)
                run_results.append(int_res)

                print(f"Run {i + 1} of {benchmark} with {interference} done")

                #Sleep one sec for safety
                time.sleep(1)
            
            res[benchmark][interference] = run_results

        #This is synchronous, we delete the interference before moving on to the next interference
        subprocess.run(f"kubectl delete -f interference-parsec/{interference}.yaml", shell=True)

    print(f"Writing results to file...")
    with open("Task2a/results/raw_results.txt", "w") as f:
        f.write(str(res))   


    print(f"Writing processed results to file..")
    avg_res = {(benchmark, interference_type):np.asarray(runs_res).mean(axis=0)
               for benchmark, interference_type_and_res in res.items()
               for interference_type, runs_res in interference_type_and_res.items()}
    
    
    with open("Task2a/results/avg_results.txt", "w") as f:
        f.write(str(avg_res))  

    print("Done!")
        
if __name__ == "__main__":
    main()
    