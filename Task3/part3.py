
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

NODES = [CLIENT_AGENT_A, CLIENT_AGENT_B, CLIENT_MEASURE, NODE_TWO_CORES, NODE_FOUR_CORES, NODE_EIGHT_CORES]

GET_NODES_HEADERS = {"NAME": 0, "STATUS": 1, "ROLES": 2, "AGE": 3, "VERSION": 4, "INTERNAL-IP": 5, "EXTERNAL-IP": 6}





def main(args):
    if(args.init_cluster):
        print("Initializing cluster...")
        sh = subprocess.run("kops delete cluster --name part3.k8s.local --yes", shell=True, capture_output=True)
        sh = subprocess.run("kops create -f part3.yaml", shell=True, capture_output=True)

        sh = subprocess.run("kops update cluster part3.k8s.local --yes --admin", shell=True, capture_output=True)

        print("Waiting for cluster to be ready...")
        sh = subprocess.run("kops validate cluster --wait 10m", shell=True, capture_output=True)
        
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
    else:
        print("Skipping VM configuration...")


    print("Creating the memcached deployment...")
    sh = subprocess.run("kubectl de")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--init_cluster", help="Initialize the cluster. If already running, deletes cluster and starts a new one.",
                        action="store_true")
    parser.add_argument("--init_vms", help="Runs the configuration of the VMs. If init_cluster is set, this is done automatically.", action="store_true")
    args = parser.parse_args()
    main(args)

