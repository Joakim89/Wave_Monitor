import filters
import math


# Method for estimating period, based on zero crossings on heavily filtered acceleration readings.
# The estimated period may be used to set ex-size and weight-vel to appropriate sizes. set q = 0.005
# also maybe try and set parameters using std dev on acc data? (maybe overcomplication)
def estimate_period(wave, update):
    time = wave.time
    filtered_acc = []
    filters.filter_readings(wave.anti_drift_acc_readings, filtered_acc, wave.period_est_weight)
    timesteps = []
    time_skip = 30
    num_meas = 0
    last_time = -1.0
    period_sum = 0.0

    i = 0
    while i < len(filtered_acc)-1:
        a = filtered_acc[i]
        b = filtered_acc[i+1]
        if a <= 0 <= b or a >= 0 >= b: #found zero crossing
            if last_time < 0:
                last_time = time[i]
            else:
                num_meas += 1
                current_time = time[i]
                period_sum += current_time - last_time
                last_time = current_time

            timesteps.append(time[i])
            i += time_skip - 1
        i += 1

    est_period = 2 * (period_sum / num_meas)
    wave.est_average_period = est_period
    # adjusting parameters:
    if update:
        ex_size = int(est_period * 13)
        if ex_size < 20:
            ex_size = 20
        if ex_size > 100:
            ex_size = 100
        wave.ex_size_vel = ex_size

        vel_weight = 0.13/est_period
        vel_weight *= 100
        vel_weight = math.ceil(vel_weight)
        vel_weight /= 100
        if vel_weight > 0.05:
            vel_weight = 0.05
        if vel_weight < 0.01:
            vel_weight = 0.01
        wave.mean_vel_weight = vel_weight


# distance should be drift-corrected distance
# returns a list with five values in this order:
# average wave height, average wave period, significant wave height, significant wave period and a list of wave heights
def get_wave_data(wave, height_correct):
    time = wave.time
    if height_correct:
        distance = wave.height_corrected_distance
    else:
        distance = wave.drift_corrected_distance
    crests_list = wave.pos_crests
    troughs_list = wave.pos_troughs
    wave_heights_sum = 0.0
    wave_periods_sum = 0.0
    wave_data = []
    wave_heights = []
    height_and_period = []
    num_meas = len(crests_list)-1
    if len(crests_list) != len(troughs_list):
        print("ERROR! crests list and troughs list do not have same length!")
        return wave_data
    if len(crests_list) < 2:
        print("ERROR, not enough waves found to calculate wave data")
        return [0, 0, 0, 0, []]
    for i in range(num_meas):
        wave_height = distance[crests_list[i]]-distance[troughs_list[i]]
        wave_heights_sum += wave_height
        wave_period = time[troughs_list[i+1]]-time[troughs_list[i]]
        wave_periods_sum += wave_period
        height_and_period.append([wave_height, wave_period])
        wave_heights.append(wave_height)

    average_wave_height = wave_heights_sum/num_meas
    average_wave_period = wave_periods_sum/num_meas

    height_and_period.sort()
    significant_height_sum = 0.0
    significant_period_sum = 0.0
    sig_num_meas = 0
    for i in range(int((2/3)*num_meas), num_meas):
        sig_num_meas += 1
        significant_height_sum += height_and_period[i][0]
        significant_period_sum += height_and_period[i][1]

    significant_wave_height = significant_height_sum/sig_num_meas
    significant_wave_period = significant_period_sum/sig_num_meas

    wave_data.append(average_wave_height)
    wave_data.append(average_wave_period)
    wave_data.append(significant_wave_height)
    wave_data.append(significant_wave_period)
    wave_data.append(wave_heights)

    if height_correct:
        wave.avg_cor_wave_height = average_wave_height
    else:
        wave.average_wave_height = average_wave_height
        wave.average_wave_period = average_wave_period
    return wave_data


def get_mean(input):
    sum = 0
    num_meas = 0
    for x in input:
        sum += x
        num_meas += 1

    return sum / num_meas


def get_std_dev(input):
    if len(input) == 0:
        return 0
    mean = get_mean(input)
    num_meas = 0
    sq_diffs = 0.0
    for x in input:
        sq_diffs += (mean - x) ** 2
        num_meas += 1

    variance = sq_diffs / num_meas
    std_dev = variance ** 0.5

    return std_dev


def get_covariance(input_x, input_y):
    x_mean = get_mean(input_x)
    y_mean = get_mean(input_y)

    sq_diffs = 0.0
    num_meas = len(input_y)
    for i in range(0, num_meas):
        sq_diffs += (input_x[i]-x_mean)*(input_y[i]-y_mean)

    covariance = sq_diffs/num_meas
    return covariance

    #Cov(x,y) = SUM [(xi - xm) * (yi - ym)] / (n - 1)


def get_correlation(input_x, input_y):
    x_std_dev = get_std_dev(input_x)
    y_std_dev = get_std_dev(input_y)
    covariance = get_covariance(input_x, input_y)
    correlation = covariance/(x_std_dev*y_std_dev)
    return correlation


# returns a list containing list x and y, each with two coordinates, constituting a trendline, followed by
# slope and b:
#      [X1, X2]
#      [Y1, Y2]
#      [slope, b]
# NB: if x_input and y-input is not exactly same length this may affect the precision of the trendline
# (could fix by cuttin x input, if they're not the same length, but not relevant so far)
def get_trendline(input_x, input_y):
    if not len(input_x) == len(input_y):
        print("NOT SAME LENGTH! trendline precision may be compromised")
    slope = get_correlation(input_x, input_y)*(get_std_dev(input_y)/get_std_dev(input_x))
    x_mean = get_mean(input_x)
    y_mean = get_mean(input_y)
    b = y_mean - slope*x_mean

    y2 = (input_x[-1] - input_x[0]) * slope

    x_list = [input_x[0], input_x[len(input_y) - 1]]
    y_list = [b, y2 + b]

    return [x_list, y_list, [slope, b]]


# returns a list containing list x and y, each with two coordinates, constituting a trendline, followed by
# slope and b:
#      [X1, X2]
#      [Y1, Y2]
#      [slope, b]
# lists must be same length, if not the method returns 0.
def get_trendline_optimized(input_x, input_y):
    if not len(input_x) == len(input_y):
        print("NOT SAME LENGTH! mission abort!")
        return 0
    x_sum = 0.0
    y_sum = 0.0
    x_sq_sum = 0.0
    xy_sum = 0.0
    n = len(input_x)
    for i in range(n):
        x_in, y_in = input_x[i], input_y[i]
        x_sum += x_in
        y_sum += y_in
        x_sq_sum += x_in**2
        xy_sum += x_in*y_in

    x_mean = x_sum/n
    y_mean = y_sum/n
    xy_mean = xy_sum/n
    x_sq_mean = x_sq_sum/n

    slope = (x_mean*y_mean - xy_mean) / (x_mean**2 - x_sq_mean)
    b = y_mean - slope*x_mean

    y2 = (input_x[-1] - input_x[0]) * slope

    x_list = [input_x[0], input_x[len(input_y) - 1]]
    y_list = [b, y2 + b]

    return [x_list, y_list, [slope, b]]
