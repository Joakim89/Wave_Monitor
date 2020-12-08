#writing to file:
#f = open("velocity-20cm-good.txt", "w+")
#for x in o1.velocities:
#    f.write(str(x) + "\n")

import numpy as np
from bokeh.plotting import figure, output_file, show
from bokeh.models import LinearAxis, Range1d


times = []
acc = []
radian = np.pi/2+0.005
time_step = 0.01
time_step2 = 0.0155
time = 0.0
acc_error = 0.01
for i in range(1000):
    time += time_step
    times.append(time)

    acc.append(np.sin(radian)+acc_error)
    radian += np.pi/200

vel = []
velocity = 0.0
for a in acc:
    velocity += a * time_step
    vel.append(velocity)

dis = []
distance = 0.0
for i in range(len(vel)):
    if i < 101:
        dis.append(0.0)
    else:
        distance += vel[i] * time_step
        dis.append(distance)

p = figure(y_range=(-2, 2), title="Double integration", x_axis_label='Time (s)', y_axis_label='Acceleration (m/s^2)')

vel_range = 1.29
p.extra_y_ranges = {"velocity": Range1d(start=-vel_range, end=vel_range)}
dis_range = 0.82
p.extra_y_ranges["distance"] = Range1d(start=-dis_range, end=dis_range)

p.line(times, acc, legend="Acceleration", color="green")
p.line(times, vel, legend="Velocity", color="orange", y_range_name="velocity")
p.add_layout(LinearAxis(y_range_name="velocity", axis_label="Velocity (m/s)",
                        axis_label_standoff=2), 'left')

p.line(times, dis, legend="Distance", color="blue", y_range_name="distance")
p.add_layout(LinearAxis(y_range_name="distance", axis_label="Distance (m)",
                        axis_label_standoff=2), 'left')

pos = 2
pos2 = 3
#p.line([pos, pos], [-4, 4], color="black")
#p.line([pos2, pos2], [-4, 4], color="black")


show(p)

#print(np.sin(np.pi/2))



