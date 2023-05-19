
#!/usr/bin/env python3

import subprocess
import re
import os
import sys
import numpy as np
import time

import argparse


MCPERF_INSTALLATION_COMMAND = "sudo -i sh -c 'echo deb-src http://europe-west3.gce.archive.ubuntu.com/ubuntu/ bionic main restricted >> /etc/apt/sources.list' && sudo apt-get update && sudo apt-get install libevent-dev libzmq3-dev git make g++ --yes && sudo apt-get build-dep memcached --yes && git clone https://github.com/eth-easl/memcache-perf-dynamic.git && cd memcache-perf-dynamic && make"

CLIENT_AGENT_A = "client-agent-a"
CLIENT_AGENT_B = "client-agent-b"
CLIENT_MEASURE = "client-measure"

NODE_TWO_CORES = "node-a-2core"
NODE_FOUR_CORES = "node-b-4core"
NODE_EIGHT_CORES = "node-c-8core"

MEMCACHED_SERVICE_NAME = "some-memcached"
MEMCACHED_IP = None
NUMBER_RUNS = 1

NODES = [CLIENT_AGENT_A, CLIENT_AGENT_B, CLIENT_MEASURE, NODE_TWO_CORES, NODE_FOUR_CORES, NODE_EIGHT_CORES]

def run_benchmarks_and_wait():
    print("Deleting past jobs...")
    sh = subprocess.run("kubectl delete jobs --all", shell=True, capture_output=True)


    print("Launching the jobs...")
    sh = subprocess.run("kubectl create -f parsec-benchmarks/part3/parsec-canneal.yaml", shell=True, capture_output=True)
    sh = subprocess.run("kubectl create -f parsec-benchmarks/part3/parsec-ferret.yaml", shell=True, capture_output=True)
    sh = subprocess.run("kubectl create -f parsec-benchmarks/part3/parsec-freqmine.yaml", shell=True, capture_output=True)
    sh = subprocess.run("kubectl create -f parsec-benchmarks/part3/parsec-vips.yaml", shell=True, capture_output=True)
    sh = subprocess.run("kubectl create -f parsec-benchmarks/part3/parsec-radix.yaml", shell=True, capture_output=True)
    sh = subprocess.run("kubectl create -f parsec-benchmarks/part3/parsec-dedup.yaml", shell=True, capture_output=True)
    sh = subprocess.run("kubectl create -f parsec-benchmarks/part3/parsec-blackscholes.yaml", shell=True, capture_output=True)

    """print("Waiting for radix to finish...")
    RADIX_FINISHED = False
    while(not RADIX_FINISHED):
        sh = subprocess.run("kubectl get jobs | grep parsec-radix", shell=True, capture_output=True)
        if(not ("0/1" in sh.stdout.decode("utf-8"))):
            RADIX_FINISHED = True
    print("Radix finished!")

    sh = subprocess.run("kubectl create -f parsec-benchmarks/part3/parsec-dedup.yaml", shell=True, capture_output=True)
    print("Waiting for dedup to finish...")

    DEDUP_FINISHED = False
    while(not DEDUP_FINISHED):
        sh = subprocess.run("kubectl get jobs | grep parsec-dedup", shell=True, capture_output=True)
        if(not ("0/1" in sh.stdout.decode("utf-8"))):
            DEDUP_FINISHED = True

    print("Dedup finished!")
    sh = subprocess.run("kubectl create -f parsec-benchmarks/part3/parsec-blackscholes.yaml", shell=True, capture_output=True)
    print("Waiting for jobs to finish...")
"""

    JOBS_FINISHED = False
    while(not JOBS_FINISHED):
        sh = subprocess.run("kubectl get jobs", shell=True, capture_output=True)
        if(not ("0/1" in sh.stdout.decode("utf-8"))):
            JOBS_FINISHED = True

        time.sleep(5)
    print("Jobs finished!")






def main(args):
    if(not args.process_only):
      run_benchmarks_and_wait()
      time.sleep(10)

    print("Getting results...")


    sh = subprocess.run(f"kubectl get pods -o json > ./Task3/experiments/pods.json", shell=True, capture_output=True)
    sh = subprocess.run(f"python3 get_time.py ./Task3/experiments/pods.json > ./Task3/experiments/processed_results.txt", shell=True, capture_output=True)
    print("Done!")



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--process_only", action="store_true")
    args = parser.parse_args()
    main(args)




