def get_mean(input):
    sum = 0
    num_meas = 0
    for x in input:
        sum += x
        num_meas += 1

    return sum / num_meas


def get_std_dev(input):
    mean = get_mean(input)
    num_meas = 0
    sq_diffs = 0.0
    for x in input:
        sq_diffs += (mean - x) ** 2
        num_meas += 1

    variance = sq_diffs / num_meas
    std_dev = variance ** 0.5

    return std_dev
