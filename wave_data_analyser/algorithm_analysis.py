from wave_data_analyser import Wave
import input_reader
import statistics
from plotting import plot
from bokeh.plotting import figure, output_file, show
from bokeh.models import Label, Div
from bokeh.core.properties import value
from bokeh.transform import dodge
from bokeh.models import ColumnDataSource
from bokeh.models import LinearAxis, Range1d
from bokeh.layouts import gridplot, column, row


def __sort_help(element):
    return element["height"]


def save_wave_data(filenames_folder, saving_file):
    wheel_data = []
    filenames = input_reader.get_file_names(filenames_folder)

    for f in filenames:
        wave = Wave(f)

        wave_data = {}

        wave_data["height"] = input_reader.get_name_data(f)[0]
        wave_data["period"] = input_reader.get_name_data(f)[1]
        wave_data["average_height"] = wave.average_wave_height
        wave_data["average_period"] = wave.average_wave_period
        wave_data["estimated_period"] = wave.est_average_period
        wave_data["ex_size"] = wave.ex_size_vel
        wave_data["mean_weight_vel"] = wave.mean_vel_weight
        wave_data["acc_std_dev"] = wave.acc_std_dev
        wave_data["average_corected_height"] = wave.avg_cor_wave_height

        wheel_data.append(wave_data)

    wheel_data.sort(key=__sort_help)

    #writing to file:
    file = open(saving_file, "w+")
    file.write(str(list(wheel_data[0].keys())).replace("[", "").replace("]", "").replace("'", "") + "\n")
    for i in wheel_data:
        file.write(str(list(i.values())).replace("[", "").replace("]", "") + "\n")
    file.close()


def save_max_waves(filenames, saving_file):
    file = open(saving_file, "w+")
    for f in filenames:
        wave = Wave(f)
        num_waves = len(statistics.get_wave_data(wave, False)[4])
        file.write(f + ", " + str(num_waves) + "\n")
    file.close()


def get_max_waves(file_name):
    max_waves = {}
    file = open(file_name, "r")
    for line in file.readlines():
        line_data = line.split(",")
        max_waves[line_data[0]] = int(line_data[1].replace("\n", ""))
    file.close()
    return max_waves


def get_wave_count(file_name):
    error_allowed = 0.5
    wave = Wave(file_name)
    wave_heights = statistics.get_wave_data(wave, False)[4]
    act_wave_height = input_reader.get_name_data(file_name)[0]
    pos_wave_count = 0
    vel_wave_count = len(wave.vel_crests)-2
    if not len(wave.vel_crests) == len(wave.vel_troughs):
        print("warning! not same length of vel-crests and troughs!!")
    if vel_wave_count < 0:
        vel_wave_count = 0
    wave_list = []
    for i in range(0, len(wave_heights)):
        if act_wave_height*(1-error_allowed) < wave_heights[i] < act_wave_height*(1+error_allowed):
            pos_wave_count += 1
            wave_list.append(wave_heights[i])

    # get vel_wave_count within 2 std dev of the mean
    num_vel_waves = len(wave.vel_crests)-1
    vel_wave_heights = []
    for i in range(num_vel_waves):
        vel_wave_height = wave.drift_corrected_velocity[wave.vel_crests[i]] - wave.drift_corrected_velocity[wave.vel_troughs[i]]
        vel_wave_heights.append(vel_wave_height)
    vel_heights_std_dev = statistics.get_std_dev(vel_wave_heights)
    vel_heights_mean = statistics.get_mean(vel_wave_heights)
    reduced_vel_wave_count = 0
    for h in vel_wave_heights:
        if vel_heights_mean-vel_heights_std_dev*1.2 < h < vel_heights_mean+vel_heights_std_dev*1.2:
            reduced_vel_wave_count += 1
    reduced_vel_wave_count -= 1

    return [pos_wave_count, vel_wave_count, wave_heights, wave_list, reduced_vel_wave_count]


def compare_wave_counts(filenames, max_waves_file):
    max_waves = get_max_waves(max_waves_file)
    for file_name in filenames:
        wave_count = get_wave_count(file_name)[0]
        num_max_waves = max_waves[file_name]
        equal_string = ""
        if wave_count < num_max_waves:
            equal_string = " <- not enough waves found!"
        print("file name: " + str(file_name) + ": wave count: " + str(wave_count) + " ---- max waves: " +
              str(num_max_waves) + equal_string)


def get_wave_compare_info(filenames, max_waves_file):
    max_waves = get_max_waves(max_waves_file)
    info_list = []
    cor_list = []
    total_max_waves = 0
    total_wave_count = 0
    for f in filenames:
        line = []
        name_data = input_reader.get_name_data(f)
        height, period = name_data[0], name_data[1]
        num_max_waves = max_waves[f]
        total_max_waves += num_max_waves
        temp = get_wave_count(f)
        pos_wave_count, vel_wave_count, wave_heights, wave_list = temp[0], temp[1], temp[2], temp[3]
        total_wave_count += pos_wave_count
        std_dev_on_heights = statistics.get_std_dev(wave_list)
        line.append(height)
        line.append(period)
        line.append(pos_wave_count)
        line.append(vel_wave_count)
        line.append(num_max_waves)
        line.append(std_dev_on_heights)

        info_list.append(line)
        for i in range(0, len(wave_heights)):
            cor_list.append([height, wave_heights[i]])

    info_list.sort()
    waves_found = [total_wave_count, total_max_waves]
    return [info_list, waves_found, cor_list]


def get_correlation_fig(cor_list):
    cor_list.sort()
    act_heights = []
    calc_heights = []
    for v in cor_list:
        act_heights.append(v[0])
        calc_heights.append(v[1])

    cor = figure(title="Correlation", x_axis_label='Actual height (m)', y_axis_label='Calculated height (m)',
                 y_range=(0, 3.5), plot_height=500, plot_width=500)
    cor.circle(act_heights, calc_heights, size=3, legend="Actual height vs calculated height", color="blue")
    slope, b = statistics.get_trendline_optimized(act_heights, calc_heights)[2]

    cor.line([act_heights[0], act_heights[-1]], [act_heights[0]*slope+b, act_heights[-1]*slope+b],
             legend="Linear regression", color="red")
    correlation = statistics.get_correlation(act_heights, calc_heights)
    lab = Label(x=20, y=20, x_units='screen', y_units='screen',
                 text='Correlation: ' + str(round(correlation, 3)),
                 border_line_color='black', background_fill_color='white')
    cor.add_layout(lab)
    trendline_info = Label(x=20, y=40, x_units='screen', y_units='screen',
                 text='Trendline: y = ' + str(round(slope, 3)) + "x " + str(round(b, 3)),
                 border_line_color='black', background_fill_color='white')
    #cor.add_layout(trendline_info)

    return cor


def get_wf_fig(data, measurements):
    source = ColumnDataSource(data=data)

    p = figure(x_range=measurements, y_range=(0, 100), plot_height=500, plot_width=700, title="Wave detection info",
               x_axis_label='wave sets', y_axis_label='% waves found')

    p.vbar(x=dodge('wave sets', -0.18, range=p.x_range), top='% waves found', width=0.3, source=source,
           color="#225ea8", legend=value("% waves found"))

    p.extra_y_ranges = {"std_dev": Range1d(start=0, end=0.5)}
    p.vbar(x=dodge('wave sets', 0.18, range=p.x_range), top='standard deviation', width=0.3, source=source,
           color="#41b6c4", legend=value("standard deviation"), y_range_name="std_dev")
    p.add_layout(LinearAxis(y_range_name="std_dev", axis_label="standard deviation (m)",
                            axis_label_standoff=8), 'right')
    return p


def get_wf_fig_with_vel(data, measurements):
    source = ColumnDataSource(data=data)

    p = figure(x_range=measurements, y_range=(0, 100), plot_height=500, plot_width=700, title="Wave info",
               x_axis_label='wave sets', y_axis_label='% waves found')

    p.vbar(x=dodge('wave sets', 0.0, range=p.x_range), top='% velocity waves found', width=0.2, source=source,
           color="red", legend=value("% velocity waves found"))

    p.vbar(x=dodge('wave sets', -0.25, range=p.x_range), top='% waves found', width=0.2, source=source,
           color="#225ea8", legend=value("% waves found"))

    p.extra_y_ranges = {"std_dev": Range1d(start=0, end=0.5)}
    p.vbar(x=dodge('wave sets', 0.25, range=p.x_range), top='standard deviation', width=0.2, source=source,
           color="#41b6c4", legend=value("standard deviation"), y_range_name="std_dev")
    p.add_layout(LinearAxis(y_range_name="std_dev", axis_label="standard deviation (m)",
                            axis_label_standoff=8), 'right')
    return p


def get_wave_info_fig(info_list, waves_found, incl_vel):
    measurements = []
    pos_percents = []
    vel_percents = []
    std_devs = []
    for info in info_list:
        meas_name = str(info[0]) + "m, " + str(info[1]) + "s"
        pos_percent = (info[2]/info[4])*100
        vel_percent = (info[3]/info[4])*100
        measurements.append(meas_name)
        pos_percents.append(pos_percent)
        vel_percents.append(vel_percent)
        std_devs.append(info[5])

    data = {}
    data['wave sets'] = measurements
    data['% waves found'] = pos_percents
    data['standard deviation'] = std_devs

    if incl_vel:
        data['% velocity waves found'] = vel_percents
        p = get_wf_fig_with_vel(data, measurements)
    else:
        p = get_wf_fig(data, measurements)

    total_wf = 100*(waves_found[0]/waves_found[1])
    lab = Label(x=20, y=20, x_units='screen', y_units='screen',
                 text='Total waves detected: ' + str(round(100)) + "%",
                 border_line_color='black', background_fill_color='white')
    p.add_layout(lab)

    p.x_range.range_padding = 0.05
    p.xgrid.grid_line_color = None
    p.legend.location = "top_left"
    p.legend.orientation = "horizontal"
    p.legend.label_text_font_size = "8pt"
    p.legend.glyph_height = 15
    p.legend.glyph_width = 15
    p.legend.label_height = 5
    p.xaxis.major_label_orientation = 1.3

    return p


def plot_results(plot, description):
    output_file("result_plot.html")
    filenames = input_reader.get_file_names("acc_orientation_data")
    max_waves_file = "orientation_max_waves.txt"
    info = get_wave_compare_info(filenames, max_waves_file)
    if plot == 1:
        show(get_wave_info_fig(info[0], info[1], False))
    elif plot == 2:
        show(get_correlation_fig(info[2]))
    elif plot == 3 or plot == 4:
        incl_vel = False
        if plot == 4:
            incl_vel = True
        wf = get_wave_info_fig(info[0], info[1], incl_vel)
        cor = get_correlation_fig(info[2])
        p = gridplot([[wf, cor]])
        show(column(Div(text="<h1>Master branch</h1>"), Div(text="<h3>" + description + "</h3>"), p))
    else:
        print("plot is not a valid value, must be either 1, 2, 3 or 4")


# running the analysis
z = "Full drift-correct, filtering and auto-adjust. No orientation"
madg = "Full drift-correct, filtering and auto-adjust. Madgwick orientation"
acc = "Full drift-correct, filtering and auto-adjust. Acceleration orientation"
anti = "Full drift-correct and . No auto-adjust or orientation"
#plot_results(3, "everything")

#save_wave_data("acc_orientation_data", "ori_wheel_data.csv")

wave = Wave("acc_orientation_data/ws-70-5-orientation.txt")
plot(wave)


def evaluate_data(cor_list):
    for x in cor_list:
        diff = (abs(x[0]-x[1])/x[0])*100
        x.append(diff)

    largest_error = 0
    average_error = 0
    for x in cor_list:
        if x[2] > largest_error:
            largest_error = x[2]
        average_error += x[2]
        print(x)

    average_error /= len(cor_list)
    print(largest_error)
    print(average_error)


filenames = input_reader.get_file_names("acc_orientation_data")
max_waves_file = "orientation_max_waves.txt"
#cor_list = get_wave_compare_info(filenames, max_waves_file)[2]
#evaluate_data(cor_list)