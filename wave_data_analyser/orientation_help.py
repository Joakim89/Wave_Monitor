# helper methods for orientation
from math import *


def get_one_list(multi_list, pos):
    values = []
    for i in range(len(multi_list)):
        values.append(multi_list[i][pos])
    return values


def subtract_gravity(list, grav):
    for i in range(len(list)):
        list[i] = list[i] - grav
    return list


def turn_euler_180(angle):
    angle += 179.999
    if angle > 180:
        cor = angle % 180
        angle = -180 + cor
    return angle


def get_vector_length(vector):
    return (vector[0]**2 + vector[1]**2 + vector[2]**2)**0.5


def get_vector_lengths(vectors):
    lengths = []
    for i in range(len(vectors)):
        length = get_vector_length(vectors[i])
        lengths.append(length)
    return lengths


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

