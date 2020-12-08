# module for different methods for doing operations concerning orienentation
from math import *
from bokeh.plotting import figure, output_file, show

# variables
gravity = 9.815
time = []
acc_vectors = []

angles_madgwick = []  # euler angles, alpha and beta, read from data file, in degrees
angles_acc = []  # euler angles, alpha and beta, calculated from acceleration

#rot_z_acc = []  # rotated z values, calculated from acceleration alone
#rot_z_madgwick = []  # rotated z values, calculated from madgwick


# read file and save to lists
def read_data():
    f = open("C:/Users/Joakim/Desktop/ITU - SDT DT/Thesis/Thesis-CODE_sensors_on_water/PYTHON_wave-data-analyser/acc_orientation_data/ws-40-3-orientation.txt", "r")
    for line in f.readlines():
        values = line.replace("(", "").replace(")", "").replace("\n", "").split(",")
        time.append(int(values[0]))
        acc_x = float(values[1])*gravity
        acc_y = float(values[2])*gravity
        acc_z = float(values[3])*gravity
        acc_vectors.append([acc_x, acc_y, acc_z])
        alpha = float(values[4])*-1
        beta = float(values[5])*-1
        angles_madgwick.append([alpha, beta])
    f.close()


def subtract_time():
    start_time = time[0]
    for i in range(len(time)):
        time[i] -= start_time
        time[i] /= 1000


# method for checking values of a tuple in a certain position
def print_tuple(pos):
    print("Tuple " + str(pos) + ":\n\tTimestep: " + str(time[pos]) + ", acc x: " + str(acc_vectors[pos][0])
          + ", acc y: " + str(acc_vectors[pos][1]) + ", acc z: " + str(acc_vectors[pos][2]) + ", alpha: "
          + str(angles_madgwick[pos][0]) + ", beta: " + str(angles_madgwick[pos][1]))


def get_vector_length(vector):
    return (vector[0]**2 + vector[1]**2 + vector[2]**2)**0.5


def get_vector_lengths(vectors):
    lengths = []
    for i in range(len(vectors)):
        length = get_vector_length(vectors[i])
        lengths.append(length)
    return lengths


# appends angle values from acceleration data, in radians
def vectors_to_angles(vector_list):
    angles = []
    for i in range(len(vector_list)):
        x = vector_list[i][0]
        y = vector_list[i][1]
        z = vector_list[i][2]

        a = atan(y/z)
        b = atan(x/z)

        angles.append([a, b])
    return angles


def turn_euler_180(angle):
    angle += 179.999
    if angle > 180:
        cor = angle % 180
        angle = -180 + cor

    return angle


def turn_beta_angles():
    for i in range(len(angles_madgwick)):
        angle = angles_madgwick[i][1]
        angles_madgwick[i][1] = turn_euler_180(angle)


def save_angles_to_file(angles, file_name):
    string_list = []
    for i in range(len(angles)):
        a = angles[i][0]
        b = angles[i][1]
        string_list.append(str(a) + "\t" + str(b) + "\t" + "0.0\n")
    save_list_to_file(string_list, file_name)


def save_list_to_file(string_list, file_name):
    file = open("orientation_data/" + file_name, "w+")
    for i in range(len(string_list)):
        file.write(string_list[i])


def angles_to_vectors(angle_vectors):
    vectors = []
    for i in range(len(angle_vectors)):
        alpha = radians(angle_vectors[i][0])
        beta = radians(angle_vectors[i][1])
        x = cos(beta)*cos(alpha)
        y = cos(beta)*sin(alpha)
        z = sin(beta)
        coordinates = [z, y, x]
        vectors.append(coordinates)
    return vectors


def angles_rad_to_degrees(angles_radians):
    angles_degrees = []
    for i in range(len(angles_radians)):
        a = degrees(angles_radians[i][0])
        b = degrees(angles_radians[i][1])
        angles_degrees.append([a, b])
    return angles_degrees


def dot_product(a, b):
    ax, ay, az = a[0], a[1], a[2]
    bx, by, bz = b[0], b[1], b[2]
    return ax*bx + ay*by + az*bz


def vector_angle(a, b):
    dp = dot_product(a, b)
    a_length, b_length = get_vector_length(a), get_vector_length(b)
    factor = dp/(a_length*b_length)
    if factor > 1:
        old_factor = factor
        factor = 1
        print("factor too high: " + str(old_factor) + ", new factor: " + str(factor))
    if factor < -1:
        old_factor = factor
        factor = -1
        print("factor too high: " + str(old_factor) + ", new factor: " + str(factor))
    return acos(factor)


def get_rot_z_madgwick():
    rot_z = []
    dir_vectors = angles_to_vectors(angles_madgwick)
    for i in range(len(acc_vectors)):
        a = acc_vectors[i]
        b = dir_vectors[i]
        angle = vector_angle(a, b)
        acc_length = get_vector_length(a)
        rot_z.append(cos(angle)*acc_length)
    return rot_z


# Testing to see if the rotated values from Madgwick makes sense. Here, the angle between the z axis and the Madgwick
# direction, is used to adjust the z-direction value. This means the more the measurement unit is turned away from
# level, the more the z axis acc value is reduced. This pattern should be observed when looking at the graph. When
# the measurement device is turned, the z-axis value becomes lower. Adjusting the value for direction should make it
# even lower, proportionally to how low the value is in the first place. E.g. if the value is close to 9.8
# (average gravity) then the difference should be almost indistinguishable, whereas if the value is low (e.g. 7) then
# the difference between rotated and un-rotated should be clear.
def get_rot_z_test():
    rot_z = []
    dir_vectors = angles_to_vectors(angles_madgwick)
    z_values = get_one_list(acc_vectors, 2)
    a = [0, 0, 1]
    for i in range(len(z_values)):
        b = dir_vectors[i]
        angle = vector_angle(a, b)
        acc_length = z_values[i]
        rot_z.append(cos(angle)*acc_length)
    return rot_z


# test to check if the projection logic holds up. Works for a specific example, but can easily be expanded to
# explore more examples.
def projection_test():
    passed = False
    a = [0.71, 0.71, 0]
    b = [1, 0, 0]
    angle = vector_angle(a, b)
    acc_length = get_vector_length(a)
    if cos(angle) * acc_length == 0.71:
        passed = True
    return passed


def get_one_list(multi_list, pos):
    values = []
    for i in range(len(multi_list)):
        values.append(multi_list[i][pos])
    return values


# plotting
def plot_acc(rot_z_acc, rot_z_madgwick):
    z_values = get_one_list(acc_vectors, 2)

    output_file("orientation_data/rotated_acceleration.html")

    rot_acc = figure(title="Rotated acceleration", x_axis_label='Time (s)', y_axis_label='Acceleration (m/s^2)')

    rot_acc.line(time, rot_z_acc, line_color="red", line_width=1, alpha=0.7, legend="Rotated acceleration from acceleration")
    rot_acc.line(time, rot_z_madgwick, line_color="blue", line_width=1, alpha=0.7, legend="Rotated acceleration from madgwick")
    #rot_acc.line(time, z_values, line_color="green", line_width=1, alpha=0.7, legend="Acceleration on z-axis")


    show(rot_acc)


def plot_angles(angles_acc, angles_madgwick):
    alpha_mad = []
    beta_mad = []
    alpha_acc = []
    beta_acc = []
    for i in range(len(angles_acc)):
        alpha_mad.append(angles_madgwick[i][0])
        beta_mad.append(angles_madgwick[i][1])
        alpha_acc.append(angles_acc[i][0])
        beta_acc.append(angles_acc[i][1])

    output_file("orientation_data/angles_comparison.html")
    angles_fig = figure(title="angles", x_axis_label="time (s)", y_axis_label="Angle (degrees)")

    #angles_fig.line(time, alpha_mad, line_color="red", legend="Alpha Madgwick (degrees)")
    angles_fig.line(time, beta_mad, line_color="orange", legend="Beta Madgwick (degrees)")
    #angles_fig.line(time, alpha_acc, line_color="blue", legend="Alpha from acceleration (degrees)")
    angles_fig.line(time, beta_acc, line_color="purple", legend="Beta from acceleration (degrees)")

    show(angles_fig)


def initiate_program():
    read_data()
    subtract_time()
    turn_beta_angles()

# running program
initiate_program()

# madgwick angles to vectors:

save_angles_to_file(angles_rad_to_degrees(vectors_to_angles(acc_vectors)), "angles_acc.txt")
save_angles_to_file(angles_madgwick, "angles_madgwick.txt")

print(angles_madgwick)
vectors = angles_to_vectors(angles_madgwick)
angles = angles_rad_to_degrees(vectors_to_angles(vectors))
print(angles)

plot_acc(get_vector_lengths(acc_vectors), get_rot_z_madgwick())






