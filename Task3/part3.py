
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

NODES = [CLIENT_AGENT_A, CLIENT_AGENT_B, CLIENT_MEASURE, NODE_TWO_CORES, NODE_FOUR_CORES, NODE_EIGHT_CORES]






def main(args):
    if(args.init_cluster):
        print("Initializing cluster...")
        sh = subprocess.run("kops delete cluster --name part3.k8s.local --yes", shell=True, capture_output=True)
        sh = subprocess.run("kops create -f part3.yaml", shell=True, capture_output=True)

        sh = subprocess.run("kops update cluster part3.k8s.local --yes --admin", shell=True, capture_output=True)

        print("Waiting for cluster to be ready...")
        sh = subprocess.run("kops validate cluster --wait 10m", shell=True, capture_output=False)
        
        if not sh.returncode == 0:
            print("Cluster failed to initialize. Deleting cluster and exiting..")
            sh = subprocess.run("kops delete cluster --name part3.k8s.local --yes", shell=True, capture_output=True)
            print("Cluster deleted.")

            sys.exit(1)
        print("Cluster is ready!")
    



    print("Getting node information...")
    # Execute the kubectl get nodes -o wide command
    result = subprocess.run(["kubectl", "get", "nodes", "-o", "wide"], capture_output=True, text=True)

    # Split the output into lines
    lines = result.stdout.split('\n')

    # Initialize an empty dictionary to store the final result
    final_result = {}

    # Iterate over each line
    for line in lines:
        # For each node
        for name in NODES:
            # If the node name is in the line
            if name in line:
                # Extract the full node name, internal IP, and external IP using regex
                print(f"line: {line}")
                match = re.search(rf"({name}-\w+)\s+\w+\s+\w+\s+\w+\s+[\w.]+\s+(\d+\.\d+\.\d+\.\d+)\s+(\d+\.\d+\.\d+\.\d+)", line)
                if match:

                    # Add the information to the final result dictionary
                    final_result[name] = {"NAME": match.group(1), "INTERNAL_IP": match.group(2), "EXTERNAL_IP": match.group(3)}
                    print(f"Found {name} with name {match.group(1)}, internal IP {match.group(2)}, and external IP {match.group(3)}")

    
    #Format of one KV pair - client-agent-a : {'NAME': 'client-agent-a-gxs4', 'INTERNAL_IP': '10.0.16.5', 'EXTERNAL_IP': '34.159.209.141'}
    node_infos = final_result

    if(args.init_vms or args.init_cluster):
        print("Configuring client and measure nodes...")

        for node in [CLIENT_AGENT_A, CLIENT_AGENT_B, CLIENT_MEASURE]:
            print(f"Configuring {node}...")


            ssh_command = f"""gcloud compute ssh ubuntu@{node_infos[node]["NAME"]} --command=\"{MCPERF_INSTALLATION_COMMAND}\""""

            print(f"sending command: {ssh_command}")
            sh = subprocess.run(ssh_command, shell=True)
            print(f"Configured {node}!")
            

        print(f"Starting memcached")
        sh = subprocess.run(f"""kubectl create -f memcache-t1-cpuset-part3.yaml""")

        print(f"Launching the load on agent A")
        sh = subprocess.run(f"""gcloud compute ssh ubuntu@{node_infos[CLIENT_AGENT_A]["NAME"]} --command='cd memcache-perf-dynamic && ./mcperf -T 2 -A'""", shell=True, capture_output=True)

        print(f"Launching the load on agent B")
        sh = subprocess.run(f"""gcloud compute ssh ubuntu@{node_infos[CLIENT_AGENT_B]["NAME"]} --command='cd memcache-perf-dynamic && ./mcperf -T 4 -A'""", shell=True, capture_output=True)



        #Getting the IP of the memcached service
        sh = subprocess.run(f"""kubectl get pods -o wide | grep {MEMCACHED_SERVICE_NAME}""", shell=True, capture_output=True)
        MEMCACHED_IP = sh.stdout.decode("utf-8").split()[5] #IP of service is sixth element in the output 

        print(f"Launching the measurement on the measure node")
        ssh_command = f"""gcloud compute ssh ubuntu@{node_infos[CLIENT_MEASURE]["NAME"]} \
            --command='cd memcache-perf-dynamic && ./mcperf -s {MEMCACHED_IP} --loadonly && \
                ./mcperf -s {MEMCACHED_IP} -a {node_infos[CLIENT_AGENT_A]["INTERNAL_IP"]} -a {node_infos[CLIENT_AGENT_B]["INTERNAL_IP"]} --noload -T 6 -C 4 -D 4 -Q 1000 -c 4 -t 10 --scan 30000:30500:5'"""
        
        sh = subprocess.run(ssh_command, shell=True, capture_output=True)
    

    else:
        print("Skipping VM configuration...")

    print("Deleting past jobs...")
    sh = subprocess.run("kubectl delete jobs --all", shell=True, capture_output=True)


    print("Launching the jobs...")
    sh = subprocess.run("kubectl create -f parsec-benchmarks/part3/parsec-blackscholes.yaml", shell=True, capture_output=True)
    sh = subprocess.run("kubectl create -f parsec-benchmarks/part3/parsec-canneal.yaml", shell=True, capture_output=True)
    sh = subprocess.run("kubectl create -f parsec-benchmarks/part3/parsec-dedup.yaml", shell=True, capture_output=True)
    sh = subprocess.run("kubectl create -f parsec-benchmarks/part3/parsec-ferret.yaml", shell=True, capture_output=True)
    sh = subprocess.run("kubectl create -f parsec-benchmarks/part3/parsec-freqmine.yaml", shell=True, capture_output=True)
    sh = subprocess.run("kubectl create -f parsec-benchmarks/part3/parsec-radix.yaml", shell=True, capture_output=True)
    sh = subprocess.run("kubectl create -f parsec-benchmarks/part3/parsec-vips.yaml", shell=True, capture_output=True)

    print("Waiting for jobs to finish...")

    JOBS_FINISHED = False
    while(not JOBS_FINISHED):
        sh = subprocess.run("kubectl get jobs", shell=True, capture_output=True)
        if(not ("0/1" in sh.stdout.decode("utf-8"))):
            JOBS_FINISHED = True

        time.sleep(5)

    print("Jobs finished!")

    sh = subprocess.run("kubectl get pods -o json > results.json", shell=True, capture_output=True)

    sh = subprocess.run("python3 get_time.py results.json", shell=True, capture_output=True)



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--init_cluster", help="Initialize the cluster. If already running, deletes cluster and starts a new one.",
                        action="store_true")
    parser.add_argument("--init_vms", help="Runs the configuration of the VMs. If init_cluster is set, this is done automatically.", action="store_true")
    args = parser.parse_args()
    main(args)

