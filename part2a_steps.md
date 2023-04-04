1. run ```kops create -f part2a.yaml```
2. run ```kops update cluster part2a.k8s.local --yes --admin```
3. Check whther cluster is up using: ```kops validate cluster --wait 10m```
4. Once it is running obtain parsec node name with: ```kubectl get nodes -o wide```
5. Label the parsec server name with ```kubectl label nodes <parsec-server-name> cca-project-nodetype=parsec```
6. Create the interference pod on the node: ```kubectl create -f interference-parsec/<INTERFERENCE_FILE>.yaml```
7. Run the benchmark Job with: ```kubectl create -f parsec-benchmarks/part2a/parsec-<JOB>.yaml```
8. Collect logs with ```kubectl logs $(kubectl get pods --selector=job-name=<job_name> \
--output=jsonpath='{.items[*].metadata.name}')```
9. Terminate the experiment (Job) repeat from _7_ when changing experiments and _6_ when changing the interference file.


## Tips for the future
 - We can test if a job has started running with ```kubectl describe pods/ibench-cpu```. Though I m not sure if the "Started event" means the interference has started
 - 
