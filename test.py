#!/usr/bin/env python3

import subprocess
import re


def test():
    a = r"real\s*(\d*)m(\d*.\d*)s"
    out = subprocess.run("ls", shell=True, capture_output=True).stdout.decode("utf-8")
    with open("output.txt", "w") as file:
        file.write(out)

    measurement = re.findall(a, """Num of Runs: 100
        Size of data: 2621440

        real    2m1.117s
        user    0m1.062s
        sys     0m0.008s""")[0]

    seconds = int(measurement[0]) * 60. + float(measurement[1])

    print(seconds)


def main():
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


if __name__ == "__main__":
    # main()
    test()
