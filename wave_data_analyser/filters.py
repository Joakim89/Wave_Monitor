import statistics


# method inspired by: https://github.com/denyssene/SimpleKalmanFilter/blob/master/src/SimpleKalmanFilter.cpp
def filter_readings(readings, output, q):
    error_estimate = 0.1
    error_measure = 0.1
    previous_estimate = 0.0

    for measured_value in readings:
        kalman_gain = error_estimate / (error_estimate + error_measure)
        current_estimate = previous_estimate + kalman_gain * (float(measured_value) - previous_estimate)
        error_estimate = (1 - kalman_gain) * error_estimate + abs(previous_estimate - current_estimate) * q
        previous_estimate = current_estimate

        output.append(current_estimate)


def anti_drift_filter(time, readings, output):
    if not len(time) == len(readings):
        print("time and readings not same length! method aborted!")
        return
    trendline = statistics.get_trendline_optimized(time, readings)[2]
    slope = trendline[0]
    b = trendline[1]
    for i in range(len(readings)):
        output.append(readings[i]-(slope*time[i]+b))

