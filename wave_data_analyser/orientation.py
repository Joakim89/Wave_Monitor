# take a file and wave object as input. Set z-acc and time on wave object
from math import *
from orientation_help import *


class Orientation:

    # constructor
    def __init__(self, wave):
        # variables
        self.__gravity = wave.average_gravity
        self.__time = []
        self.__acc_vectors = []  # acceleration vectors, each vector is acceleration in 3 axis [x, y, z]
        self.__angles_madgwick = []  # euler angles, alpha and beta, read from data file, in degrees

        self.__read_data(wave.file_name)
        self.__subtract_time()
        self.__turn_beta_angles()

    # read file and save to lists
    def __read_data(self, file_name):
        f = open(file_name, "r")
        for line in f.readlines():
            values = line.replace("(", "").replace(")", "").replace("\n", "").split(",")
            self.__time.append(int(values[0]))
            acc_x = float(values[1])*self.__gravity
            acc_y = float(values[2])*self.__gravity
            acc_z = float(values[3])*self.__gravity
            self.__acc_vectors.append([acc_x, acc_y, acc_z])
            alpha = float(values[4])*-1
            beta = float(values[5])*-1
            self.__angles_madgwick.append([alpha, beta])
        f.close()

    # data processing
    def __subtract_time(self):
        start_time = self.__time[0]
        for i in range(len(self.__time)):
            self.__time[i] -= start_time
            self.__time[i] /= 1000

    def __turn_beta_angles(self):
        for i in range(len(self.__angles_madgwick)):
            angle = self.__angles_madgwick[i][1]
            self.__angles_madgwick[i][1] = turn_euler_180(angle)

    def __get_rot_z_madgwick(self):
        rot_z = []
        dir_vectors = angles_to_vectors(self.__angles_madgwick)
        for i in range(len(self.__acc_vectors)):
            a = self.__acc_vectors[i]
            b = dir_vectors[i]
            angle = vector_angle(a, b)
            acc_length = get_vector_length(a)
            rot_z.append(cos(angle)*acc_length)
        return rot_z

    def set_z_madg(self, wave):
        wave.acc_readings = subtract_gravity(self.__get_rot_z_madgwick(), self.__gravity*1.017)
        wave.time = self.__time

    def set_z_acc(self, wave):
        wave.acc_readings = subtract_gravity(get_vector_lengths(self.__acc_vectors), self.__gravity*1.017)
        wave.time = self.__time

    def set_z(self, wave):
        wave.acc_readings = subtract_gravity(get_one_list(self.__acc_vectors, 2), self.__gravity*1.017)
        wave.time = self.__time
