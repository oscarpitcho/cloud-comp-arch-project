import pandas as pd
import numpy as np
import os

from matplotlib.ticker import FuncFormatter
from scipy.stats import bootstrap

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('TkAgg')  # workaround, otherwise I get error

DATA_FOLDER = os.path.join("..", "measurements", "task1")
INTERFERENCES = ["none", "ibench-cpu"]

if __name__ == '__main__':
    data = {}
    """ load all files into dictionary and stack data """
    for inter in INTERFERENCES:
        aggregate = []
        inter_path = os.path.join(DATA_FOLDER, inter)
        for file in os.listdir(inter_path):
            table = pd.read_csv(os.path.join(inter_path, file), delim_whitespace=True)
            df_info = table[["p95", "QPS", "target"]]
            np_info = df_info.to_numpy()
            aggregate.append(np_info)
        data[inter] = np.stack(aggregate)

    fig, ax = plt.subplots()
    plt.text(0, 9.3, "Data was averaged over 3 runs")
    plt.ylabel("95th Percentile Latency in ms")
    plt.xlabel("Queries Per Second")
    plt.xlim([0, 120000])
    plt.ylim([0, 9])
    plt.yticks(range(0, 9))
    plt.xticks(range(0, 120000, 10000))

    ax.xaxis.set_major_formatter(FuncFormatter(lambda x_val, tick_pos: "{:.0f}k".format(x_val / 1000)))

    for inter in INTERFERENCES:
        arr = data[inter]
        means = np.mean(arr, axis=0)
        arr = arr[:, means[:, 1] > means[:, 2] - 2500]  # filter greater than target - 2500
        means = means[means[:, 1] > means[:, 2] - 2500]

        ci = bootstrap((arr,), np.mean, confidence_level=0.95, random_state=10).confidence_interval

        ax.errorbar(x=means[:, 1],
                    y=means[:, 0] / 1000.,
                    xerr=[means[:, 1] - ci.low[:, 1], ci.high[:, 1] - means[:, 1]],
                    yerr=[(means[:, 0] - ci.low[:, 0]) / 1000., (ci.high[:, 0] - means[:, 0]) / 1000.],
                    capsize=4,
                    capthick=2,
                    elinewidth=1,
                    fmt='o-',
                    mec='white',
                    mew=.5,
                    label=inter
                    )
    ax.legend()

    plt.show()
