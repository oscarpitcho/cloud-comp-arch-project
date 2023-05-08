# Task 4 setup

- edit part4.yaml with corresponding <ethz-id>
- give permission to the user to execute the setup scripts (via chmod u=rwx <file>)
- if gsutil throws permission error, run `gcloud auth application-default login`
- configure setup_part4.2.sh according to your local setup
- run setup_part4.2.sh
- after approx. 10min, the output should now contain the running VMs
- edit scripts/setup_measure.sh to contain the correct ids/IP addresses
- load scripts to the VMs via (remember to change paths and ids):

```
./google-cloud-sdk/bin/gcloud compute scp --scp-flag=-r ./cloud-comp-arch-project/Task4/dynamic_scheduler.py ubuntu@memcache-server-<id>:/home/ubuntu/ --zone europe-west3-a
./google-cloud-sdk/bin/gcloud compute scp --scp-flag=-r ./cloud-comp-arch-project/Task4/scripts/ ubuntu@client-agent-<id>:/home/ubuntu/ --zone europe-west3-a
./google-cloud-sdk/bin/gcloud compute scp --scp-flag=-r ./cloud-comp-arch-project/Task4/scripts/ ubuntu@client-measure-<id>:/home/ubuntu/ --zone europe-west3-a
```

- enter into agent and measure server and run corresponding scripts. SSH via:
`./google-cloud-sdk/bin/gcloud compute ssh --ssh-key-file ~/.ssh/cloud-computing ubuntu@client-<machine>-<id> --zone europe-west3-a`
  
- ssh into memcache server and run commands from setup_memcached.sh. Also follow the commented instructions.