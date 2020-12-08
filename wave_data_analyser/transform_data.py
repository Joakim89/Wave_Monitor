#import time as timer


def integrate(time, input, output):
    output.append(0.0)
    vel_or_dis = 0.0
    for i in range(1, len(input)):
        time_step = float(time[i])-float(time[i-1])
        vel_or_dis = vel_or_dis + input[i] * time_step
        output.append(vel_or_dis)


def height_correct(wave):
    a = wave.height_correct_factors[0]
    b = wave.height_correct_factors[1]
    avg_height = wave.average_wave_height
    #cor_height = a * avg_height + b
    cor_height = (avg_height-b)/a
    cor_factor = cor_height / avg_height
    for h in wave.drift_corrected_distance:
        wave.height_corrected_distance.append(h*cor_factor)


def drift_correct(input, output, ex_size, det_prec, crests_list, troughs_list):
    #start_time = timer.time()

    test1 = 0
    test2 = 0

    updated_last = False
    crests = 0
    troughs = 0
    last_crest = 0
    last_trough = 0
    last_drift_correct_pos = 0
    cumulative_relative_drift = 0.0
    i = ex_size

    reset = False
    left_positives = 0
    left_negatives = 0
    right_negatives = 0
    right_positives = 0

    right_list = []
    left_list = []

    while i < len(input) - 1:
        # left side
        if not left_list:
            for j in range(i - ex_size, int(i - ex_size / 2)):
                test1 += 1
                dir_value = input[j + 1] - input[j]
                left_list.append(dir_value)
                if dir_value > 0:
                    left_positives += 1
                else:
                    left_negatives += 1
        else:
            test1 += 1
            # remove start from list and add an extra value
            # also update left_positives and left_negatives accordingly
            dir_value = left_list.pop(0)
            if dir_value > 0:
                left_positives -= 1
            else:
                left_negatives -= 1

            dir_value = input[i - int(ex_size / 2)] - input[i - int(ex_size / 2) - 1]
            left_list.append(dir_value)
            if dir_value > 0:
                left_positives += 1
            else:
                left_negatives += 1

        # right side
        if not right_list:
            for k in range(int(i - ex_size / 2), i):
                test2 += 1
                dir_value = input[k + 1] - input[k]
                right_list.append(dir_value)
                if dir_value < 0:
                    right_negatives += 1
                else:
                    right_positives += 1
        else:
            test2 += 1
            dir_value = right_list.pop(0)
            if dir_value < 0:
                right_negatives -= 1
            else:
                right_positives -= 1

            dir_value = input[i] - input[i - 1]
            right_list.append(dir_value)
            if dir_value < 0:
                right_negatives += 1
            else:
                right_positives += 1

        if left_positives >= int(ex_size / 2) * det_prec and right_negatives >= int(ex_size / 2) * det_prec:
            crests += 1
            last_crest = i - int(ex_size / 2)
            i += ex_size - 1
            reset = True
            updated_last = False

        if left_negatives >= int(ex_size / 2) * det_prec and right_positives >= int(ex_size / 2) * det_prec:
            troughs += 1
            last_trough = i - int(ex_size / 2)
            i += ex_size - 1
            reset = True
            updated_last = True

        # reset troughs and crests
        if reset:
            right_negatives = 0
            right_positives = 0
            right_list = []

            left_positives = 0
            left_negatives = 0
            left_list = []
            reset = False

        if last_crest > 0 and last_trough > 0 and updated_last:
            crests_list.append(last_crest)
            troughs_list.append(last_trough)

            absolute_drift = (input[last_crest] + input[last_trough])/2
            drift_correct_pos = int((last_trough+last_crest)/2)

            relative_drift = absolute_drift - cumulative_relative_drift
            drift_factor = relative_drift / (drift_correct_pos - last_drift_correct_pos)

            cumulative_drift = 0.0
            for l in range(last_drift_correct_pos, drift_correct_pos):
                cumulative_drift = cumulative_drift + drift_factor
                output.append(
                    input[l] - cumulative_drift - cumulative_relative_drift)

            cumulative_relative_drift = cumulative_relative_drift + relative_drift
            last_crest = 0
            last_drift_correct_pos = drift_correct_pos
            last_trough = 0

        i += 1

    #print("crests: " + str(crests))
    #print("troughs: " + str(troughs))

    #print("test1: " + str(test1))
    #print("test2: " + str(test2))

    #end_time = timer.time()

    #print("driftcorrect time taken: " + str(end_time-start_time))
