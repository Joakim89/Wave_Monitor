from standard_dev import get_std_dev

file_name = "acc_data/readings_for_joakim.txt"
interval = 0.001

# read file and save to list
f = open(file_name, "r")
readings = []
for line in f.readlines():
    readings.append(float(line))
f.close()

# subtract average gravity
sum = 0.0
num_meas = 0
for i in readings:
    sum += i
    num_meas += 1
average_gravity = sum/num_meas
gravity = []
for j in readings:
    gravity.append(j-average_gravity)

gravity.sort()

# save gravity in file
file = open("acc_data/gravity.txt", "w+")
for x in gravity:
    file.write(str(x) + "\n")

# sort and save sorted readings in file
readings.sort()
file2 = open("acc_data/sorted_readings.txt", "w+")
for y in readings:
    file2.write(str(y) + "\n")

# count numbers of occurences within each interval and save in "columns" dictionary
max_error = max(gravity)
min_error = min(gravity)
error_range = max_error-min_error

columns = {}
x_values = []
y_values = []

pos = 0
k = -0.16
num = 0
while k <= 0.18:
    if pos < len(gravity) and gravity[pos] < (k + interval):
        num += 1
        pos += 1
    else:
        columns["value less than: " + str(round(k+interval, 5))] = num
        x_values.append(str(round(k, 3)) + "->" + str(round(k+interval, 3)))
        y_values.append(num)
        k += interval
        num = 0

# standard dev on gravity
std_dev = get_std_dev(gravity)

# normalized_gravity
#normalized_gravity = []
#for z in gravity:
#    normalized_gravity.append(z/std_dev)

# plotting
from bokeh.plotting import figure, output_file, show
import numpy as np

output_file("acc_data/Acceleration_error.html")

acc_error = figure(title="Acceleration error", x_axis_label='X (acceleration (m/s^2))', y_axis_label='Pr(x)')

hist, edges = np.histogram(gravity, density=True, bins=65)

acc_error.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], fill_color="navy", line_color="white", alpha=0.5)

sigma = std_dev
mu = 0
x = np.linspace(-0.2, 0.2, 1000)

pdf = 1/(sigma * np.sqrt(2*np.pi)) * np.exp(-(x-mu)**2 / (2*sigma**2))

acc_error.line(x, pdf, line_color="#ff8888", line_width=4, alpha=0.7, legend="PDF")

show(acc_error)



