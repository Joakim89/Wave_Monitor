import statistics
import input_reader

from bokeh.plotting import figure, output_file, show
from bokeh.layouts import gridplot, column, row
from bokeh.models import Label, Div
import numpy as np


def plot(wave):
    output_file("Wave detection.html")

    acc = figure(title="Acceleration", x_axis_label='Time (s)', y_axis_label='Acceleration (m/s^2)')

    #acceleration trendline
    temp_list = statistics.get_trendline(wave.time, wave.acc_readings)
    #acc.line(temp_list[0], temp_list[1], legend="Linear regression", color="red")

    period_est = Label(x=20, y=20, x_units='screen', y_units='screen',
                 text='Estimated average period (s): ' + str(round(wave.est_average_period, 3)),
                 border_line_color='black', background_fill_color='white')
    #acc.add_layout(period_est)

    info = Label(x=20, y=40, x_units='screen', y_units='screen',
                 text='Standard deviation on acceleration (m/s^2): ' + str(round(wave.acc_std_dev, 3)),
                 border_line_color='black', background_fill_color='white')
    #acc.add_layout(info)

    acc.line(wave.time, wave.acc_readings, legend="Acceleration (m/s^2)", color="blue")
    #acc.line([0, 82], [0, 0], color="black")

    #acc.line(wave.time, wave.anti_drift_acc_readings, legend="Centered acceleration (m/s^2)", color="blue")
    acc.line(wave.time, wave.filtered_acc_readings, legend="Filtered acceleration (m/s^2)", color="red")


    #velocity figure
    vel = figure(title="Velocity", x_axis_label="Time (s)", y_axis_label="Velocity (m/s)")

    vel.line(wave.time, wave.velocities, legend="Velocity (m/s)")
    vel.line(wave.time, wave.drift_corrected_velocity, legend="Drift corrected velocity (m/s)", color="red")
    vel.line(wave.time, wave.filtered_velocity, legend="Filtered velocity (m/s)", color="green")

    ex_size = Label(x=20, y=20, x_units='screen', y_units='screen',
                 text='Ex-size: ' + str(round(wave.ex_size_vel, 3)),
                 border_line_color='black', background_fill_color='white')
    #vel.add_layout(ex_size)
    mean_weight = Label(x=20, y=40, x_units='screen', y_units='screen',
                 text='Mean weight: ' + str(round(wave.mean_vel_weight, 3)),
                 border_line_color='black', background_fill_color='white')
    #vel.add_layout(mean_weight)

    #distance figure
    dis = figure(title="Distance", x_axis_label="Time (s)", y_axis_label="Distance (m)")

    info2 = Label(x=20, y=40, x_units='screen', y_units='screen',
                     text='Average wave height (m): ' + str(round(wave.average_wave_height, 3)),
                     border_line_color='black', background_fill_color='white')
    #dis.add_layout(info2)

    info3 = Label(x=20, y=20, x_units='screen', y_units='screen',
                     text='Average wave period (s): ' + str(round(wave.average_wave_period, 2)),
                     border_line_color='black', background_fill_color='white')
    #dis.add_layout(info3)
    cor_avg_height = Label(x=20, y=60, x_units='screen', y_units='screen',
                     text='Corrected average height (m): ' + str(round(wave.avg_cor_wave_height, 3)),
                     border_line_color='black', background_fill_color='white')
    #dis.add_layout(cor_avg_height)

    #dis.line(wave.time, wave.distances, legend="Distance (m)")
    dis.line(wave.time, wave.drift_corrected_distance, legend="Drift corrected distance (m)", color="red")
    #dis.line(wave.time, wave.height_corrected_distance, legend="Height corrected distance (m)", color="yellow")

    p = gridplot([[acc, vel, dis]])

    name_data = input_reader.get_name_data(wave.file_name)
    wave_height = name_data[0]
    wave_period = name_data[1]

    show(column(Div(text="<h1>Wave data</h1>"), Div(text="<h3>Wave height: " + str(wave_height) + "m, "
                                                    + "wave period: " + str(wave_period) + "s</h3>"), p))


def plot_std_dev(wave1, wave2, wave3, bins):
    act_height = input_reader.get_name_data(wave1.file_name)[0]
    wave_heights = []
    wave_heights.extend(statistics.get_wave_data(wave1, False)[4])
    wave_heights.extend(statistics.get_wave_data(wave2, False)[4])
    wave_heights.extend(statistics.get_wave_data(wave3, False)[4])
    max_height = max(wave_heights)
    min_height = min(wave_heights)

    output_file("prob_dist_wave_heights.html")

    p = figure(title="Probability distribution of wave height, for " + str(act_height) + "m",
               x_axis_label='X (wave heights (m))', y_axis_label='Pr(x)', toolbar_location=None)

    hist, edges = np.histogram(wave_heights, density=True, bins=bins)

    p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], fill_color="navy", line_color="white",
                   alpha=0.5)

    bins_info = Label(x=20, y=40, x_units='screen', y_units='screen',
                     text='Bins: ' + str(bins),
                     border_line_color='black', background_fill_color='white')
    p.add_layout(bins_info)

    sigma = statistics.get_std_dev(wave_heights)
    mu = statistics.get_mean(wave_heights)
    x = np.linspace(min_height, max_height, 1000)

    pdf = 1 / (sigma * np.sqrt(2 * np.pi)) * np.exp(-(x - mu) ** 2 / (2 * sigma ** 2))

    p.line(x, pdf, line_color="#ff8888", line_width=4, alpha=0.7, legend="PDF")

    show(p)


def plot_pr_dist(wave1, wave2, wave3):
    for i in range(5, 20):
        plot_std_dev(wave1, wave2, wave3, i)
