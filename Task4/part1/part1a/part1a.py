import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator, FuncFormatter
from utils import extract_results

# data for each configuration
configurations = [
    (extract_results(config, 3), f"T={config[1]}, C={config[3]}")
    for config in ["t1c1", "t1c2", "t2c1", "t2c2"]
]

# define the symbols and colors for each line
# symbols = ["o", "s", "^", "d"]
colors = ["#ef476f", "#ffd166", "#06d6a0", "#118ab2"]

# iterate over each configuration
for i, (data, label) in enumerate(configurations):
    target_values = [target for target, _ in data]
    lat_values = [
        np.mean([point[1] for point in points]) for _, points in data
    ]  # compute the average of latency values for each QPS value
    lat_std = [
        np.std([point[1] for point in points]) for _, points in data
    ]  # compute the standard deviation of latency values for each QPS value
    qps_values = [np.mean([point[0] for point in points]) for _, points in data]
    qps_std = [np.std([point[0] for point in points]) for _, points in data]

    # plot the line for this configuration with the corresponding symbol and color
    plt.plot(qps_values, lat_values, color=colors[i], label=label)

    # plot the error bars for this configuration using the computed standard deviation
    plt.errorbar(
        qps_values,
        lat_values,
        yerr=lat_std,
        xerr=qps_std,
        fmt="none",
        color=colors[i],
        capsize=3,
    )


# abbreviate x labels
def format_qps(x, pos):
    if x == 0:
        return "0"
    return f"{x/1000:.0f}K"


plt.gca().xaxis.set_major_formatter(FuncFormatter(format_qps))

# set the x and y axis labels
plt.xlabel("QPS")
plt.ylabel("95th percentile latency (ms)")
# plt.ylabel("95th percentile latency (μs)", rotation=0, ha="left")
# plt.gca().yaxis.set_label_coords(0, 1.01)

# set the title of the plot
plt.suptitle(
    "Memcached - 95th percentile latency vs. QPS",
    y=0.97,
    fontsize=16,
)
plt.title(
    "For different Cores and Threads configurations\nAveraged across 3 runs",
    y=1.01,
    fontsize=12,
)

# add a black line at the 1 millisecond latency threshold
plt.axhline(y=1, color="#555", linestyle="--", linewidth=1, label="1ms SLO")

# add legend to the plot
plt.legend()

# add a dashed grid to the major ticks and a dotted grid to the minor ticks
plt.grid(True, linestyle="--", linewidth=0.5, which="major")
plt.grid(True, linestyle="--", color="#e1e1e1", linewidth=0.5, which="minor")
plt.locator_params(axis="x", nbins=13)
plt.locator_params(axis="y", nbins=10)
plt.xlim([0, 130_000])
plt.ylim([0, 2])
plt.gca().xaxis.set_minor_locator(MultipleLocator(5000))
plt.gca().yaxis.set_minor_locator(MultipleLocator(0.1))

# display the plot
plt.show()
