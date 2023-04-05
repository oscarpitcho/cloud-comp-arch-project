#!/usr/bin/env python3

import subprocess
import re
import numpy as np




res = {'parsec-blackscholes': {'no_int': [(0.898, 0.012, 0.839), (0.883, 0.012, 0.864)], 'ibench-cpu': [(1.147, 0.028, 1.042), (1.115, 0.012, 1.049)]}}
def main():
    for benchmark, interference_type_and_res in res.items():
        print(f"benchmark: {benchmark}, interference_type_and_res: {interference_type_and_res}")
        for interference_type, runs_res in interference_type_and_res.items():
            print(f"interference_type: {interference_type}, runs_res: {runs_res}")
            
    avg_res = {(benchmark, interference_type):np.asarray(runs_res).mean(axis=0)
               for benchmark, interference_type_and_res in res.items()
               for interference_type, runs_res in interference_type_and_res.items()}
    
    print(avg_res)
    print("Done")


if __name__ == "__main__":
    main()
