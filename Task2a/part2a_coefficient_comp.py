import json

dict = {('parsec-blackscholes', 'no_int'): [1.135, 0.012, 1.059], ('parsec-blackscholes', 'ibench-cpu'): [1.153, 0.008, 1.055], ('parsec-blackscholes', 'ibench-l1d'): [1.008, 0.   , 1.006], ('parsec-blackscholes', 'ibench-l1i'): [1.344, 0.02 , 1.269], ('parsec-blackscholes', 'ibench-l2'): [1.027, 0.012, 1.007], ('parsec-blackscholes', 'ibench-llc'): [1.284, 0.028, 1.16 ], ('parsec-blackscholes', 'ibench-membw'): [1.141, 0.02 , 1.064], ('parsec-canneal', 'no_int'): [12.402,  0.533, 11.462], ('parsec-canneal', 'ibench-cpu'): [11.765,  0.226, 10.873], ('parsec-canneal', 'ibench-l1d'): [12.905,  0.18 , 12.697], ('parsec-canneal', 'ibench-l1i'): [14.611,  0.21 , 13.867], ('parsec-canneal', 'ibench-l2'): [14.408,  0.665, 13.561], ('parsec-canneal', 'ibench-llc'): [21.052,  0.402, 19.818], ('parsec-canneal', 'ibench-membw'): [14.303,  0.241, 13.493], ('parsec-dedup', 'no_int'): [25.508,  7.092, 28.207], ('parsec-dedup', 'ibench-cpu'): [42.729,  6.918, 33.911], ('parsec-dedup', 'ibench-l1d'): [32.27 ,  7.126, 34.929], ('parsec-dedup', 'ibench-l1i'): [53.798,  7.527, 43.597], ('parsec-dedup', 'ibench-l2'): [32.947,  8.975, 34.029], ('parsec-dedup', 'ibench-llc'): [57.885,  9.706, 44.595], ('parsec-dedup', 'ibench-membw'): [43.071,  6.904, 33.951], ('parsec-ferret', 'no_int'): [ 6.056,  0.158, 10.955], ('parsec-ferret', 'ibench-cpu'): [11.602,  0.123, 10.855], ('parsec-ferret', 'ibench-l1d'): [ 6.209,  0.136, 11.134], ('parsec-ferret', 'ibench-l1i'): [14.125,  0.126, 13.261], ('parsec-ferret', 'ibench-l2'): [ 6.261,  0.127, 11.282], ('parsec-ferret', 'ibench-llc'): [16.397,  0.173, 14.954], ('parsec-ferret', 'ibench-membw'): [12.41 ,  0.107, 11.519], ('parsec-freqmine', 'no_int'): [6.448, 0.128, 6.305], ('parsec-freqmine', 'ibench-cpu'): [12.68 ,  0.144,  6.379], ('parsec-freqmine', 'ibench-l1d'): [6.55 , 0.107, 6.378], ('parsec-freqmine', 'ibench-l1i'): [13.388,  0.151,  6.616], ('parsec-freqmine', 'ibench-l2'): [6.513, 0.127, 6.322], ('parsec-freqmine', 'ibench-llc'): [12.281,  0.299, 11.559], ('parsec-freqmine', 'ibench-membw'): [12.078,  0.202, 11.212], ('parsec-radix', 'no_int'): [58.029,  4.472, 53.396], ('parsec-radix', 'ibench-cpu'): [67.196,  7.366, 56.428], ('parsec-radix', 'ibench-l1d'): [59.978,  3.926, 56.004], ('parsec-radix', 'ibench-l1i'): [64.784,  6.358, 56.16 ], ('parsec-radix', 'ibench-l2'): [60.459,  4.227, 56.185], ('parsec-radix', 'ibench-llc'): [102.059,  12.784,  84.629], ('parsec-radix', 'ibench-membw'): [62.49 ,  3.762, 56.491], ('parsec-vips', 'no_int'): [107.056,   2.757, 108.03 ], ('parsec-vips', 'ibench-cpu'): [179.311,   3.325, 169.65 ], ('parsec-vips', 'ibench-l1d'): [171.344,   3.86 , 169.997], ('parsec-vips', 'ibench-l1i'): [203.702,   3.828, 191.871], ('parsec-vips', 'ibench-l2'): [167.022,   3.201, 166.199], ('parsec-vips', 'ibench-llc'): [216.75 ,   5.663, 201.46 ], ('parsec-vips', 'ibench-membw'): [186.561,   4.855, 174.072]}


res = {}
for (benchmark, interference), values in dict.items():
    if benchmark not in res:
        res[benchmark] = {}
    res[benchmark][interference] = values[0]

norm_res = {}
for benchmark, interferences in res.items():
    if benchmark not in norm_res:
        norm_res[benchmark] = {}
    for int in interferences:
        norm_res[benchmark][int] = res[benchmark][int] / res[benchmark]['no_int']
        
print(f"norm_res: {norm_res}")
