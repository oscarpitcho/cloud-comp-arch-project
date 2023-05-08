#!/bin/bash

# ssh into memcached node and install memcached
./google-cloud-sdk/bin/gcloud compute ssh --ssh-key-file ~/.ssh/cloud-computing ubuntu@memcache-server-<id> --zone europe-west3-a
sudo apt update
sudo apt install -y python3 python3-pip memcached libmemcached-tools
sudo systemctl status memcached

# update memcached config
sudo vim /etc/memcached.conf
# toggle edit mode by typing: i
# search for line starting with -m and update to 1024
# search for line starting with -l and update to <internal-memcache-server IP> found in google cloud console
# add line -t 2 to run memcached with 2 threads
# save via typing ESC followed by :wq!

# check changes via
sudo systemctl restart memcached
sudo systemctl status memcached

sudo usermod -a -G docker $USER
newgrp docker

pip3 install psutil docker

docker pull anakli/cca:parsec_blackscholes
docker pull anakli/cca:parsec_canneal
docker pull anakli/cca:parsec_dedup
docker pull anakli/cca:parsec_ferret
docker pull anakli/cca:parsec_freqmine
docker pull anakli/cca:splash2x_radix
docker pull anakli/cca:parsec_vips

# run dynamic scheduler via
python3 ./dynamic_scheduler.py
