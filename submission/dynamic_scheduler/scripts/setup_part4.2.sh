#!/bin/bash

# configure paths accordingly to setup part 4.2
ethid="roester"
gcfolder="./google-cloud-sdk/bin"
projectfolder="./cloud-comp-arch-project"

echo "Start up Part 4.2 as user ${ethid}"

${gcfolder}/gsutil rm -r gs://cca-eth-2023-group-054-${ethid}/
${gcfolder}/gsutil mb gs://cca-eth-2023-group-054-${ethid}/

export KOPS_STATE_STORE=gs://cca-eth-2023-group-054-${ethid}/
PROJECT=`${gcfolder}/gcloud config get-value project`
kops create -f ${projectfolder}/part4.yaml
kops create secret --name part4.k8s.local sshpublickey admin -i ~/.ssh/cloud-computing.pub
kops update cluster --name part4.k8s.local --yes --admin
kops validate cluster --wait 10m
