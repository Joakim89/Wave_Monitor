import input_reader
import transform_data
import filters
import statistics
import plotting
from orientation import Orientation
from low_pass_filter import smooth


class Wave:
    def __init__(self, file_name):
        # parameters:
        self.average_gravity = 9.815
        self.ex_size_vel = 40  # default value, range: 20-100
        self.ex_size_rel = 0.5
        self.det_prec_vel = 0.9
        self.det_prec_rel = 1.0
        self.ex_size_dis = int(self.ex_size_vel * self.ex_size_rel)
        self.det_prec_dis = self.det_prec_vel * self.det_prec_rel
        self.mean_acc_weight = 0.05
        self.mean_vel_weight = 0.03  # default value, range: 0.01 - 0.05
        self.period_est_weight = 0.005
        # correct avg height x to corrected avg height y, with y = a*x + b, where:
        # [a, b] below.
        a = [1.0253, 0.0141]
        b = [0.965, -0.016]
        self.height_correct_factors = b

        # variables:
        self.file_name = file_name
        self.est_average_period = 0.0
        self.average_wave_height = 0.0
        self.average_wave_period = 0.0
        self.acc_std_dev = 0.0
        self.avg_cor_wave_height = 0.0
        self.time = []
        self.acc_readings = []
        self.anti_drift_acc_readings = []
        self.filtered_acc_readings = []
        self.distances = []
        self.velocities = []
        self.drift_corrected_velocity = []
        self.drift_corrected_distance = []
        self.height_corrected_distance = []
        self.filtered_velocity = []
        self.vel_crests = []
        self.vel_troughs = []
        self.pos_crests = []
        self.pos_troughs = []

        # running the program
        #input_reader.read_acc_data(self)

        ori = Orientation(self)
        ori.set_z_madg(self)

        self.acc_std_dev = statistics.get_std_dev(self.acc_readings)  # for analysis of the algorithm

        filters.anti_drift_filter(self.time, self.acc_readings, self.anti_drift_acc_readings)

        statistics.estimate_period(self, True)

        filters.filter_readings(self.anti_drift_acc_readings, self.filtered_acc_readings, self.mean_acc_weight)

        #self.filtered_acc_readings = smooth(self.anti_drift_acc_readings)

        transform_data.integrate(self.time, self.filtered_acc_readings, self.velocities)
        filters.filter_readings(self.velocities, self.filtered_velocity, self.mean_vel_weight)
        transform_data.drift_correct(self.filtered_velocity, self.drift_corrected_velocity, self.ex_size_vel,
                                     self.det_prec_vel, self.vel_crests, self.vel_troughs)
        transform_data.integrate(self.time, self.drift_corrected_velocity, self.distances)
        transform_data.drift_correct(self.distances, self.drift_corrected_distance, self.ex_size_dis,
                                     self.det_prec_dis, self.pos_crests, self.pos_troughs)

        statistics.get_wave_data(self, False)

        transform_data.height_correct(self)

        statistics.get_wave_data(self, True)

