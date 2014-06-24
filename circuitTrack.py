###################################################################################################################################################################
#
#   @witwiki #2231.24062014
#   This is a circuit track "race" for the AR Parrot
#   using the 'quadrotor.command' package. 
#   The objective is to hit each 3d Diamond marker using
#   visual motion estimation, EKF, PID control. 
#   The final computer vision and autononous nav project for AUTONAV TUMx [edX]
#
#   calculate the Predicted State function                      ----------> predictState(self, dt, x, u_linear_velocity, u_yaw_velocity)
#   calculate Predicted State (Motion Model) Jacobian           ----------> calculatePredictStateJacobian(self, dt, x, u_linear_velocity, u_yaw_velocity)
#   calculate the Predicted State Covariance                    ----------> predictCovariance(self, sigma, F, Q)
#   calculate the Kalman Gain                                   ----------> calculateKalmanGain(self, sigma_p, H, R)
#   calculate the Corrected State function                      ----------> correctState(self, K, x_predicted, z, z_predicted)
#   calculate the Corrected State Covariance                    ----------> correctCovariance(self, sigma_p, K, H)
#   calculate Predicted Measurement (Sensor Model) Jacobian     ----------> calculatePredictMeasurementJacobian(self, x, marker_position_world, marker_yaw_world)
#
###################################################################################################################################################################


import math
import numpy as np
from plot import plot, plot_trajectory, plot_covariance_2d

class UserCode:
    def __init__(self):
        pass
        
    def get_markers(self):
        '''
        place up to 30 markers in the world
        '''
        markers = [
             [0, 0], # marker at world position x = 0, y = 0
             [2, 0]  # marker at world position x = 2, y = 0
        ]
        
        #TODO: Add your markers where needed
       
        return markers
        
    def state_callback(self, t, dt, linear_velocity, yaw_velocity):
        '''
        called when a new odometry measurement arrives approx. 200Hz
    
        :param t - simulation time
        :param dt - time difference this last invocation
        :param linear_velocity - x and y velocity in local quadrotor coordinate frame (independet of roll and pitch)
        :param yaw_velocity - velocity around quadrotor z axis (independet of roll and pitch)

        :return tuple containing linear x and y velocity control commands in local quadrotor coordinate frame (independet of roll and pitch), and yaw velocity
        '''
        
        return np.ones((2,1)) * 0.1, 0


    def measurement_callback(self, marker_position_world, marker_yaw_world, marker_position_relative, marker_yaw_relative):
        '''
        called when a new marker measurement arrives max 30Hz, marker measurements are only available if the quadrotor is
        sufficiently close to a marker
            
        :param marker_position_world - x and y position of the marker in world coordinates 2x1 vector
        :param marker_yaw_world - orientation of the marker in world coordinates
        :param marker_position_relative - x and y position of the marker relative to the quadrotor 2x1 vector
        :param marker_yaw_relative - orientation of the marker relative to the quadrotor
        '''
        pass
    
