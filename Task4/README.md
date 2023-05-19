# Task 4 setup

- edit part4.yaml with corresponding <ethz-id>
- give permission to the user to execute the setup scripts (via chmod u=rwx <file>)- 
- configure setup_part4.2.sh according to your local setup
- run `setup_part4.2.sh`
- if gsutil throws permission error, run `gcloud auth application-default login`
- after approx. 10min, the output should now contain the running VMs
- check via running `kubectl get nodes -o wide`
- load scripts to the VMs via (remember to change paths and ids):

```
./google-cloud-sdk/bin/gcloud compute scp --scp-flag=-r ./cloud-comp-arch-project/Task4/dynamic_scheduler/ ubuntu@memcache-server-<id>:/home/ubuntu/ --zone europe-west3-a
./google-cloud-sdk/bin/gcloud compute scp --scp-flag=-r ./cloud-comp-arch-project/Task4/scripts/ ubuntu@client-agent-<id>:/home/ubuntu/ --zone europe-west3-a
./google-cloud-sdk/bin/gcloud compute scp --scp-flag=-r ./cloud-comp-arch-project/Task4/scripts/ ubuntu@client-measure-<id>:/home/ubuntu/ --zone europe-west3-a
```

- open terminal and enter into agent and measure server. Then run corresponding setup scripts. SSH via:
```
./google-cloud-sdk/bin/gcloud compute ssh --ssh-key-file ~/.ssh/cloud-computing ubuntu@client-agent-<id> --zone europe-west3-a
./google-cloud-sdk/bin/gcloud compute ssh --ssh-key-file ~/.ssh/cloud-computing ubuntu@client-measure-<id> --zone europe-west3-a
```
  
- open terminal and enter into memcache server and follow the instructions from `setup_memcached.sh`.

# Task 4 measuring

- start agent via `./mcperf -T 16 -A`
- start measure (-t flag is the total measurement time) via:
```
./mcperf -s <INTERNAL_MEMCACHED_IP> --loadonly
./mcperf -s <INTERNAL_MEMCACHED_IP> -a <INTERNAL_AGENT_IP> --noload -T 16 -C 4 -D 4 -Q 1000 -c 4 -t 900 --qps_interval 10 --qps_min 5000 --qps_max 100000
```
- start controller via: `python3 dynamic_scheduler/dynamic_scheduler.py`
  
- store log files locally via
`./google-cloud-sdk/bin/gcloud compute scp --scp-flag=-r ubuntu@memcache-server-<id>:/home/ubuntu/log20230519_101313.txt ./cloud-comp-arch-project/Task4/logs/ --zone europe-west3-a`

# Delete cluster

- delete cluster at the end via: `kops delete cluster --name part4.k8s.local --yes`