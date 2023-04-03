# Cloud Computing Architecture Project

This repository contains starter code for the Cloud Computing Architecture course project at ETH Zurich. Students will explore how to schedule latency-sensitive and batch applications in a cloud cluster. Please follow the instructions in the project handout.


# Part 1
Run code/task1.py to create the plot for the 95th percentile tail latency of running memcached together with iBench interference types.
Note that the target QPS can never be achieved. We therefore removed the datapoints where the measured QPS is significantly lower than the target QPS.

The following commands have to be issued to do benchmarking (remember to change yaml files of project according to your ethzid):

```shell
$ gsutil rm -r gs://cca-eth-2023-group-054-<ethzid>/
$ gsutil mb gs://cca-eth-2023-group-054-<ethzid>/
$ export KOPS_STATE_STORE=gs://cca-eth-2023-group-054-<ethzid>/
$ cd ~/.ssh && ssh-keygen -t rsa -b 4096 -f cloud-computing
$ PROJECT=`gcloud config get-value project`
$ kops create -f part1.yaml
$ kops create secret --name part1.k8s.local sshpublickey admin -i ~/.ssh/cloud-computing.pub
$ kops update cluster --name part1.k8s.local --yes --admin
$ kops validate cluster --wait 10m
$ kubectl get nodes -o wide
# run memcached
$ kubectl create -f memcache-t1-cpuset.yaml
$ kubectl expose pod some-memcached --name some-memcached-11211 --type LoadBalancer --port 11211 --protocol TCP
$ sleep 60
$ kubectl get service some-memcached-11211
$ kubectl get pods -o wide
# then ssh into client-agent and client-measure, install mcperf
$ gcloud compute ssh --ssh-key-file ~/.ssh/cloud-computing ubuntu@client-agent-<id> --zone europe-west3-a
$ gcloud compute ssh --ssh-key-file ~/.ssh/cloud-computing ubuntu@client-measure-<id> --zone europe-west3-a
$ sudo apt-get update && 
sudo apt-get install libevent-dev libzmq3-dev git make g++ --yes && 
sudo cp /etc/apt/sources.list /etc/apt/sources.list~ &&
sudo sed -Ei 's/^# deb-src /deb-src /' /etc/apt/sources.list &&
sudo apt-get update &&
sudo apt-get build-dep memcached --yes &&
cd && git clone https://github.com/shaygalon/memcache-perf.git &&
cd memcache-perf &&
git checkout 0afbe9b &&
make
# on client agent
$ ./mcperf -T 16 -A
# on client measure
$ ./mcperf -s <MEMCACHED_IP> --loadonly
$ ./mcperf -s <MEMCACHED_IP> -a <INTERNAL_AGENT_IP> --noload -T 16 -C 4 -D 4 -Q
# induce interference (from other terminal window)
$ kubectl create -f interference/ibench-<type>.yaml
$ kubectl get pods -o wide
# kill the interference job
$ kubectl delete pods ibench-<cpu>
# delete cluster after usage
$ kops delete cluster part1.k8s.local --yes
```

