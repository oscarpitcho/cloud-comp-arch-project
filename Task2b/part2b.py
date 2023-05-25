import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('TkAgg')  # workaround, otherwise I get error

# Define the number of threads and the corresponding normalized time for each application
threads = [1, 2, 4, 8]
blackscholes = [
    [124.720, 126.294, 125.490],
    [73.493, 73.440, 74.433],
    [46.449, 48.462, 47.999],
    [36.294, 36.822, 36.792],
]
canneal = [
    [253.665, 287.122, 297.214],
    [178.793, 189.464, 180.960],
    [129.916, 122.922, 125.901],
    [98.270, 105.376, 101.616],
]
dedup = [
    [20.144, 21.163, 21.072],
    [12.510, 13.009, 13.621],
    [11.971, 11.535, 13.648],
    [10.531, 15.012, 10.411],
]
ferret = [
    [319.866, 321.016, 322.297],
    [163.202, 167.623, 166.574],
    [93.564, 94.576, 95.243],
    [80.858, 82.213, 81.418],
]
freqmine = [
    [490.176, 494.067, 493.848],
    [248.298, 255.132, 252.457],
    [126.162, 127.507, 127.530],
    [101.960, 103.461, 109.271],
]
radix = [
    [53.258, 56.147, 59.367],
    [27.274, 30.073, 32.478],
    [14.501, 15.888, 15.835],
    [9.693, 12.005, 10.595],
]
vips = [
    [99.540, 100.023, 100.431],
    [51.158, 52.159, 52.151],
    [26.382, 26.153, 26.397],
    [22.053, 23.451, 22.550],
]

# Compute the mean of the three runs for each application
blackscholes_mean = [(t[0] + t[1] + t[2]) / 3.0 for t in blackscholes]
canneal_mean = [(t[0] + t[1] + t[2]) / 3.0 for t in canneal]
dedup_mean = [(t[0] + t[1] + t[2]) / 3.0 for t in dedup]
ferret_mean = [(t[0] + t[1] + t[2]) / 3.0 for t in ferret]
freqmine_mean = [(t[0] + t[1] + t[2]) / 3.0 for t in freqmine]
radix_mean = [(t[0] + t[1] + t[2]) / 3.0 for t in radix]
vips_mean = [(t[0] + t[1] + t[2]) / 3.0 for t in vips]

print("blackscholes : ", blackscholes_mean)
print("canneal : ", canneal_mean)
print("dedup : ", dedup_mean)
print("ferret : ", ferret_mean)
print("freqmine : ", freqmine_mean)
print("radix : ", radix_mean)
print("vips : ", vips_mean)

# Compute the speedup for each application
blackscholes_speedup = [blackscholes_mean[0] / t for t in blackscholes_mean]
canneal_speedup = [canneal_mean[0] / t for t in canneal_mean]
dedup_speedup = [dedup_mean[0] / t for t in dedup_mean]
ferret_speedup = [ferret_mean[0] / t for t in ferret_mean]
freqmine_speedup = [freqmine_mean[0] / t for t in freqmine_mean]
radix_speedup = [radix_mean[0] / t for t in radix_mean]
vips_speedup = [vips_mean[0] / t for t in vips_mean]

# Set different marker styles for each application
marker_styles = ["o-", "s-", "D-", "*-", "x-", "^-", "v-"]

# Set different colors for each application
colors = ["#003f5c", "#374c80", "#7a5195", "#bc5090", "#ef5675", "#ff764a", "#ffa600"]

# Plot the speedup as a function of the number of threads for each application
plt.plot(
    threads,
    blackscholes_speedup,
    marker_styles[0],
    color=colors[0],
    label="blackscholes",
    linewidth=2,
)
plt.plot(
    threads,
    canneal_speedup,
    marker_styles[1],
    color=colors[1],
    label="canneal",
    linewidth=2,
)
plt.plot(
    threads,
    dedup_speedup,
    marker_styles[2],
    color=colors[2],
    label="dedup",
    linewidth=2,
)
plt.plot(
    threads,
    ferret_speedup,
    marker_styles[3],
    color=colors[3],
    label="ferret",
    linewidth=2,
)
plt.plot(
    threads,
    freqmine_speedup,
    marker_styles[4],
    color=colors[4],
    label="freqmine",
    linewidth=2,
)
plt.plot(
    threads,
    radix_speedup,
    marker_styles[5],
    color=colors[5],
    label="radix",
    linewidth=2,
)
plt.plot(
    threads, vips_speedup, marker_styles[6], color=colors[6], label="vips", linewidth=2
)

# Plot a diagonal line with slope 1 to show linear progression
plt.plot(threads, threads, "k--", label="linear progression")

# Set the x-axis and y-axis labels
plt.xlabel("Number of Threads")
plt.ylabel(
    "Speedup ($Time_1$ / $Time_n$) averaged over three runs", rotation=0, ha="left"
)

# Set the legend and show only 4 ticks on the x-axis
plt.legend()
plt.xticks(threads)

# Set the grid in the background
plt.grid(True, linestyle="--")

# Move the y-axis label to the top of the graph
plt.gca().yaxis.set_label_coords(0, 1.05)

# Show the plot
plt.show()
