# Comment for future
- Kops refers to instance groups while kubernetes refers to nodes (which are instances)

# Start the cluster

1. run ```kops create -f part3.yaml```
2. run ```kops update cluster part3.k8s.local --yes --admin```. **Note**: When creating a script which initializes the clused the command of 2 and 3 can be cobined with the ``&&`` operator, this will ensure the program only continues when the cluster is up.
3. run ```kops validate cluster --wait 10m``` - wait until cluster is up


# Configuring the clients

1. using the ```gcloud compute ssh``` command, ssh into the client-agent and client-measure instances
2. Run: ```sudo sh -c "echo deb-src http://europe-west3.gce.archive.ubuntu.com/ubuntu/ bionic main restricted >> /etc/apt/sources.list" &&sudo apt-get update && sudo apt-get install libevent-dev libzmq3-dev git make g++ --yes && sudo apt-get build-dep memcached --yes && git clone https://github.com/eth-easl/memcache-perf-dynamic.git && cd memcache-perf-dynamic && make``` to install mcperf


# Configuring the memcached servers

1. Run ```kubectl label nodes <MEM_CACHED_NODE> cca-project-nodetype=memcached``` to label the memcached node. **TODO:** Choose which nodes will run memcached.
2. Run ```kubectl create -f memcache-t1-cpuset-part3.yaml``` to create the memcached pod. **TODO:** Yaml file needs to be changed to choose number of cores
3. Run ``` kubectl expose pod some-memcached --name some-memcached-11211 --type LoadBalancer --port 11211 --protocol TCP`` - This creates a service that allows to connect to the pod for memcached. It abstracts away the specificities of the pod and instead allows to directly connect to a service instead. If the pod fails for instance and is restarted, the users of the service will not see changes in the configuration.
4. ```sleep 60```
5. Run ```kubectl get service some-memcached-11211```


# Running the measurements:
1. Run ```./mcperf -T 2 -A``` on the client-agent-a machine
2. Run ```./mcperf -T 4 -A``` on the client-agent-b machine
3. On the client-measure machine:
   1. To obtain the IP run:
      1. Run ```kubectl get service``` or ```kubectl get pods -o wide``` to obtain the IP of the memcached server. One is the ip of the service exposed and one is the IP of the pod. TODO: THIS NEEDS TO BE CLARIFIED
      2. Run ```kubectl get nodes -o wide``` for the ip of the Agents
   2. Run ```./mcperf -s <MEMCACHED_IP> --loadonly```
   3. Run ```./mcperf -s <MEMCACHED_IP -a <INTERNAL_AGENT_A_IP -a <INTERNAL_AGENT_B_IP --noload -T 6 -C 4 -D 4 -Q 1000 -c 4 -t 10 --scan 30000:30500:5```


# Instructions using scripts
1. Start in the main directory of the project.
2. Run ```Python3 Task3/set_up.py --init_cluster```
3. Once the cluster is set this will print the command to start the mcperf measurement on _client-measure_ - Run the command
4. Run ```Python3 Task3/run_experiments.py```
5. Copy the terminal of mcperf and the files ```pods.json``` and ```processed_results.txt``` in appropriate folder.
6. **For successive runs**: 
   1. Repeat 2. without the flag ```--init_cluster``` - This will restart the mcperf processes on client agents
   2. Relaunch the mcperf command on client-measure
   3. Repeat 4. and 5.
   
   
# Running the Parsec jobs - TODO: Scheduling
1. Run ```kubectl create -f parsec-benchmarks/part3/parsec-<JOB_NAME>.yaml``` to create the blackscholes job. 
 - **TODO:** Right now with the config it's node selector is memcached, i.e. it will run on the same node as memcached. 
 - **TODO:** How many cores should each job get?


# Ideas
- **Problem:** On first run in single machine, it did not crash. 
  - **Sol1:**  Run all jobs + memcached node b which has the lowest RAM available (4GB)
    - **Results**
      - *CPU*: Maxed on some / all cores depending on the job running
      - *RAM*: Sometimes close to maxed but never. 
      - *SLO*: Way above 1ms during the job runs
      - **Summary**: ALL JOBS RUN SUCCESSFULLY
  - **Sol2**: From part2, parsec ferret is most susceptible to memory interference, i.e. it should need the most. We will run parsec-ferret with very low resource limit by modifying its corresponding yaml file
    - **Results**: Nothing crashes still
- Limit memory usage of Job to make sure it fails appropriately