
#!/usr/bin/env python3

import subprocess
import re

benchmark = "parsec-blackscholes"
a = r"real\s*([0-9]*)m(\d*.\d*)s"
output = subprocess.run(f"""kubectl logs $(kubectl get pods --selector=job-name={benchmark} --output=jsonpath='{{.items[*].metadata.name}}\')""", shell=True, capture_output=True)


print(re.findall(a, """Num of Runs: 100
Size of data: 2621440

real    0m1.117s
user    0m1.062s
sys     0m0.008s""")[0])

print("Deleting job...")

print(subprocess.run(f"kubectl delete jobs/{benchmark}", shell=True))

print("Done")
