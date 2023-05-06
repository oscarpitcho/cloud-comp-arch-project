# Comment for future
- Kops refers to instance groups while kubernetes refers to nodes (which are instances)

# Start the cluster

1. run ```kops create -f part3.yaml```
2. run ```kops update cluster part3.k8s.local --yes --admin```. **Note**: When creating a script which initializes the clused the command of 2 and 3 can be cobined with the ``&&`` operator, this will ensure the program only continues when the cluster is up.
3. run ```kops validate cluster --wait 10m``` - wait until cluster is up


# Configuring the clients

1. using the ```gcloud compute ssh``` command, ssh into the client-agent and client-measure instances
2. Run: ```sudo apt-get update && sudo apt-get install libevent-dev libzmq3-dev git make g++ --yes && sudo apt-get build-dep memcached --yes && git clone https://github.com/eth-easl/memcache-perf-dynamic.git && cd memcache-perf-dynamic && make``` to install mcperf
