from os.path import dirname, join
import os


def read_acc_data(wave):
    current_dir = dirname(__file__)
    file_path = join(current_dir, wave.file_name)
    f = open(file_path, "r")
    line = f.readline()
    line_data = line.split(",")
    start_time = float(line_data[0])
    wave.time.append(0.0)
    wave.acc_readings.append(float(line_data[1]) - wave.average_gravity)
    for line in f.readlines():
        line_data = line.split(",")
        wave.time.append((float(line_data[0]) - start_time) / 1000)
        wave.acc_readings.append(float(line_data[1]) - wave.average_gravity)
    f.close()


# modified from stackoverflow: https://stackoverflow.com/questions/10377998/how-can-i-iterate-over-files-in-a-given-directory
def get_file_names(folder_location):
    folder = os.fsencode(folder_location)
    file_names = []
    for file in os.listdir(folder):
        file_name = folder_location + "/" + os.fsdecode(file)
        file_names.append(file_name)
    file_names.sort()
    return file_names


def get_name_data(file_name):
    name = file_name.split("-")
    wave_height = int(name[1])/100
    wave_period = int(name[2].split(".")[0])
    wave_data = [wave_height, wave_period]
    return wave_data


def read_file(file_name):
    current_dir = dirname(__file__)
    file_path = join(current_dir, file_name)
    some_readings = open(file_path, "r")
    temp = []
    for x in some_readings.readlines():
        temp.append(float(x))
    some_readings.close()
    return temp


def read_phone_data(wave):
    f = open(wave.file_name, "r")
    line = f.readline()
    line_data = line.split()
    start_time = float(line_data[1])
    wave.time.append(0.0)
    wave.acc_readings.append(float(line_data[4].replace(",", ".")) - wave.average_gravity)
    for line in f.readlines():
        line_data = line.split()
        wave.time.append((float(line_data[1]) - start_time) / 1000)
        wave.acc_readings.append(float(line_data[4].replace(",", ".")) - wave.average_gravity)
    f.close()
