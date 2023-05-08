#!/bin/bash

INTERNAL_MEMCACHED="10.0.16.4"
INTERNAL_AGENT="10.0.16.3"

sudo apt-get update
sudo apt-get install libevent-dev libzmq3-dev git make g++ --yes
sudo apt-get build-dep memcached --yes
git clone https://github.com/eth-easl/memcache-perf-dynamic.git
cd memcache-perf-dynamic || exit
make

echo "Start measuring..."

./mcperf -s $INTERNAL_MEMCACHED --loadonly

# -t flag corresponds to the execution time
./mcperf -s $INTERNAL_MEMCACHED -a $INTERNAL_AGENT --noload -T 16 -C 4 -D 4 -Q 1000 -c 4 -t 10 --qps_interval 2 --qps_min 5000 --qps_max 100000
