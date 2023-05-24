def extract_results(config, runs):
    usages_runs = extract_cpu_results(config, runs)
    runs_data = []
    for i in range(1, runs + 1):
        file = f"{config}/memcached_{i}.txt"
        data = []

        with open(file, "r") as file:
            lines = file.readlines()

        # Find the index of the headers line
        headers_line_index = None
        for index, line in enumerate(lines):
            if line.startswith("#type"):
                headers_line_index = index
                break

        # Extract the relevant columns
        if headers_line_index is not None:
            headers = lines[headers_line_index].split()
            p95_index = headers.index("p95")
            qps_index = headers.index("QPS")
            time_index = headers.index("ts_start")
            # target_index = headers.index("target")

            # Iterate over the data lines and extract the values
            for line in lines[headers_line_index + 1 :]:
                if line.startswith("read"):
                    values = line.split()
                    p95 = float(values[p95_index]) / 1000.0
                    qps = float(values[qps_index])
                    time = int(values[time_index])
                    # target = int(values[target_index])
                    data.append((cpu_usage_at(time, usages_runs[i]), qps, p95))
        runs_data.append(data)
    return runs_data


def extract_cpu_results(config, runs):
    runs_data = {}
    for i in range(1, runs + 1):
        file = f"{config}/cpu_{i}.txt"

        with open(file, "r") as file:
            lines = file.readlines()

        runs_data[i] = list(
            map(lambda line: (int(line.split()[0]), float(line.split()[1])), lines)
        )
    return runs_data


def cpu_usage_at(time, usages):
    for usage in usages:
        if usage[0] >= time:
            return usage[1]


if __name__ == "__main__":
    pass
