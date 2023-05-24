def merge_tuples(tuples):
    merged_dict = {}
    for key, value in tuples:
        if key in merged_dict:
            merged_dict[key].append(value)
        else:
            merged_dict[key] = [value]
    merged_tuples = [(key, values) for key, values in merged_dict.items()]
    return merged_tuples


def extract_results(config, runs):
    data_concat = []
    for i in range(1, runs + 1):
        filename = f"{config}/run{i}.txt"
        data_list = []

        # Read the file
        with open(filename, "r") as file:
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
            target_index = headers.index("target")

            # Iterate over the data lines and extract the values
            for line in lines[headers_line_index + 1 :]:
                if line.startswith("read"):
                    values = line.split()
                    p95 = float(values[p95_index]) / 1000.0
                    qps = float(values[qps_index])
                    target = int(values[target_index])
                    data_list.append((target, (qps, p95)))

        data_concat += data_list
    return merge_tuples(data_concat)


if __name__ == "__main__":
    print(extract_results("t1c1", 1))
