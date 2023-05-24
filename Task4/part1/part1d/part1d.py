import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

from utils import extract_results


# abbreviate x labels
def format_qps(x, pos):
    if x == 0:
        return "0"
    return f"{x/1000:.0f}K"


# create two subplots
fig, axs = plt.subplots(1, 2)

for i in range(1, 3):
    raw_data = extract_results(f"t2c{i}", 3)

    data = np.mean(raw_data, 0)
    qps = [qps for _, qps, _ in data]
    latency = [latency for _, _, latency in data]
    cpu_util = [cpu_util for cpu_util, _, _ in data]

    # std = np.std(raw_data, 0)
    # qps_std = [qps for _, qps, _ in std]
    # latency_std = [latency for _, _, latency in std]
    # cpu_util_std = [cpu_util for cpu_util, _, _ in std]

    ax = axs[i - 1]
    ax.plot(qps, latency, "o-", label="95th percentile latency")
    ax.axhline(y=1, color="#555", linestyle="--", linewidth=1, label="1ms SLO")
    ax.set_xlabel("QPS")
    ax.set_xlim([0, 130_000])
    ax.set_ylabel("Latency [ms]")
    ax.set_ylim([0, 2])
    ax.legend(loc="upper left")
    ax.grid(True, linestyle="--", linewidth=0.5, which="major")
    ax.xaxis.grid(True, linestyle="--", color="#e1e1e1", linewidth=0.5, which="minor")
    ax.set_title(
        f"Using 2 threads and {i} core{'' if i==1 else 's'}, averaged over 3 runs\n "
    )
    ax.locator_params(axis="y", nbins=10)
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(5000))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.1))

    # ax.errorbar(
    #     qps,
    #     latency,
    #     yerr=latency_std,
    #     xerr=qps_std,
    #     fmt="none",
    #     capsize=3,
    # )

    ax_twiny = ax.twinx()
    ax_twiny.plot(qps, cpu_util, "o--", color="orange", label="CPU utilization")
    ax_twiny.set_ylabel("CPU utilization [%]")
    ax_twiny.set_ylim([0, i * 100])
    ax_twiny.legend(loc="upper right")
    ax_twiny.locator_params(axis="y", nbins=10)
    ax_twiny.yaxis.set_minor_locator(ticker.MultipleLocator(5 * i))

    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_qps))

    # ax_twiny.errorbar(
    #     qps,
    #     cpu_util,
    #     yerr=cpu_util_std,
    #     xerr=qps_std,
    #     fmt="none",
    #     capsize=3,
    # )

# adjust spacing between subplots
plt.subplots_adjust(wspace=0.4)
plt.suptitle(
    "Memcached - 95th percentile latency and CPU utilization vs. QPS",
    y=0.97,
    fontsize=16,
)

plt.show()
