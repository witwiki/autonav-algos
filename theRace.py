import math
import numpy as np
from plot import plot_trajectory, plot_point, plot_covariance_2d


class UserCode:
    def __init__(self):        
        # Initializations for Position Control

        self.Kpx = 5
        self.Kdx = 5
        self.lastX = 0

        self.Kpy = 5
        self.Kdy = 5
        self.lastY = 0

        #TODO: Play with the noise matrices
        #process noise
        pos_noise_std = 0.005
        yaw_noise_std = 0.005
        self.Q = np.array([
            [pos_noise_std*pos_noise_std,0,0],
            [0,pos_noise_std*pos_noise_std,0],
            [0,0,yaw_noise_std*yaw_noise_std]
        ]) 
        
        #measurement noise
        z_pos_noise_std = 0.005
        z_yaw_noise_std = 0.03
        self.R = np.array([
            [z_pos_noise_std*z_pos_noise_std,0,0],
            [0,z_pos_noise_std*z_pos_noise_std,0],
            [0,0,z_yaw_noise_std*z_yaw_noise_std]
        ])
        
        # state vector [x, y] in world coordinates 
        self.x = np.zeros((3,1))            # This is equivalent to self.position = np.zeros((3,1)) 
 
        # 3x3 state covariance matrix
        self.sigma = 0.01 * np.identity(3) 


    def get_markers(self):
        '''
        place up to 30 markers in the world
        '''
        markers = [
            [0, 0], # marker at world position x = 0, y = 0
            [1.25, 0.5],  # marker at world position x = 1.25, y = 0.5
            [3, 0.5],
            [4.5, 0.5],
            [3.5, 2],
            [1.25, 3.5],
            [3, 3.5],
            [4.5, 3.5],
            [4, 5.5],
            [5.5, 5.5],
            [7, 5.5],
            [4, 7],
            [4, 8.5],
            [5.5, 8.5],
            [7, 8.5],
            [9.5, 9.5],
            [9.5, 11],
            [9.5, 12.5],
            [8, 11],
            [6.5, 11]            
        ]
        
        return markers
        
    def rotation(self, yaw):
        '''
        create 2D rotation matrix from given angle
        '''
        s_yaw = math.sin(yaw)
        c_yaw = math.cos(yaw)
                
        return np.array([
            [c_yaw, -s_yaw], 
            [s_yaw,  c_yaw]
        ])
    
    def normalizeYaw(self, y):
        '''
        normalizes the given angle to the interval [-pi, +pi]
        '''
        while(y > math.pi):
            y -= 2 * math.pi
        while(y < -math.pi):
            y += 2 * math.pi
        return y
    
    def visualizeState(self):
        # visualize position state
        plot_trajectory("kalman", self.x[0:2])
        plot_covariance_2d("kalman", self.sigma[0:2,0:2])
    
    def predictState(self, dt, x, u_linear_velocity, u_yaw_velocity):
        '''
        predicts the next state using the current state and 
        the control inputs local linear velocity and yaw velocity
        '''
        x_p = np.zeros((3, 1))
        x_p[0:2] = x[0:2] + dt * np.dot(self.rotation(x[2]), u_linear_velocity)
        x_p[2]   = x[2]   + dt * u_yaw_velocity
        x_p[2]   = self.normalizeYaw(x_p[2])
        
        return x_p
    
    def calculatePredictStateJacobian(self, dt, x, u_linear_velocity, u_yaw_velocity):
        '''
        calculates the 3x3 Jacobian matrix for the predictState(...) function
        '''
        s_yaw = math.sin(x[2])
        c_yaw = math.cos(x[2])
        
        dRotation_dYaw = np.array([
            [-s_yaw, -c_yaw],
            [ c_yaw, -s_yaw]
        ])
        F = np.identity(3)
        F[0:2, 2] = dt * np.dot(dRotation_dYaw, u_linear_velocity)
        
        return F
    
    def predictCovariance(self, sigma, F, Q):
        '''
        predicts the next state covariance given the current covariance, 
        the Jacobian of the predictState(...) function F and the process noise Q
        '''
        return np.dot(F, np.dot(sigma, F.T)) + Q
    
    def calculateKalmanGain(self, sigma_p, H, R):
        '''
        calculates the Kalman gain
        '''
        return np.dot(np.dot(sigma_p, H.T), np.linalg.inv(np.dot(H, np.dot(sigma_p, H.T)) + R))
    
    def correctState(self, K, x_predicted, z, z_predicted):
        '''
        corrects the current state prediction using Kalman gain, the measurement and the predicted measurement
        
        :param K - Kalman gain
        :param x_predicted - predicted state 3x1 vector
        :param z - measurement 3x1 vector
        :param z_predicted - predicted measurement 3x1 vector
        :return corrected state as 3x1 vector
        '''
        
        # TODO: implement correction of predicted state x_predicted
        x_predicted = x_predicted + np.dot(K, (z - z_predicted))
        
        return x_predicted
    
    def correctCovariance(self, sigma_p, K, H):
        '''
        corrects the sate covariance matrix using Kalman gain and the Jacobian matrix of the predictMeasurement(...) function
        '''
        return np.dot(np.identity(3) - np.dot(K, H), sigma_p)
    
    def predictMeasurement(self, x, marker_position_world, marker_yaw_world):
        '''
        predicts a marker measurement given the current state and the marker position and orientation in world coordinates 
        '''
        z_predicted = Pose2D(self.rotation(x[2]), x[0:2]).inv() * Pose2D(self.rotation(marker_yaw_world), marker_position_world);
        
        return np.array([[z_predicted.translation[0], z_predicted.translation[1], z_predicted.yaw()]]).T
    
    def calculatePredictMeasurementJacobian(self, x, marker_position_world, marker_yaw_world):
        '''
        calculates the 3x3 Jacobian matrix of the predictMeasurement(...) function using the current state and 
        the marker position and orientation in world coordinates
        
        :param x - current state 3x1 vector
        :param marker_position_world - x and y position of the marker in world coordinates 2x1 vector
        :param marker_yaw_world - orientation of the marker in world coordinates
        :return - 3x3 Jacobian matrix of the predictMeasurement(...) function
        '''
        
        s_yaw = math.sin(x[2])
        c_yaw = math.cos(x[2])
        
        xM = marker_position_world[0]
        yM = marker_position_world[1]
        
        oneThree = -np.dot((xM - x[0]), s_yaw) + np.dot((yM - x[1]), c_yaw)
        twoThree = -np.dot((xM - x[0]), c_yaw) - np.dot((yM - x[1]), s_yaw)

        H = np.array([[-c_yaw,-s_yaw, oneThree],
                     [ s_yaw,-c_yaw, twoThree],
                     [0, 0,-1]])        
                     
        return H
    

    def compute_control_command(self, t, dt, measured, desired):
        #self.plot(state.position, state_desired.position)
        
        u = np.zeros((2,1))

        x_measured = measured[0]
        y_measured = measured[1]
        x_desired = desired[0]
        y_desired = desired[1]

        # For x coordinate
        velX = (x_measured - self.lastX) / dt
        uX = self.Kpx * (x_desired - x_measured) + self.Kdx * (0 - velX)
        
        self.lastX = x_measured;

        # For y coordinate
        velY = (y_measured - self.lastY) / dt
        uY = self.Kpy * (y_desired - y_measured) + self.Kdy * (0 - velY)
        
        self.lastY = y_measured;

        # Unify both coordinates
        u = np.array([[uX],
                      [uY]])

        return u


    def state_callback(self, t, dt, linear_velocity, yaw_velocity):
        '''
        called when a new odometry measurement arrives approx. 200Hz
        
        :param t - simulation time
        :param dt - time difference this last invocation
        :param linear_velocity - x and y velocity in local quadrotor coordinate frame (independet of roll and pitch)
        :param yaw_velocity - velocity around quadrotor z axis (independet of roll and pitch)

        :return tuple containing linear x and y velocity control commands in local quadrotor coordinate frame (independet of roll and pitch), and yaw velocity
        '''

        linear_velocity = np.zeros((2,1))
        yaw_velocity = 0.0


        #   ----------> Calculation of the EKF Prediction Step (200Hz) [Slide 10 L6.3]        
        ##  State Prediction Jacobian [F] here is in Slide 10 L6.3 represented as G
        F = self.calculatePredictStateJacobian(dt, self.x, linear_velocity, yaw_velocity)

        ##  The mean is calculated for the prediction step
        self.x = self.predictState(dt, self.x, linear_velocity, yaw_velocity)

        ##  The covariance is next and calculated for the prediction step using the Jacobian and process noise [Q]        
        self.sigma = self.predictCovariance(self.sigma, F, self.Q);
        
        self.visualizeState()


        # compute_control_command function under here

        linear_velocity = self.compute_control_command(t, dt, self.x, self.get_markers())

                
        return linear_velocity, yaw_velocity
    
    def measurement_callback(self, marker_position_world, marker_yaw_world, marker_position_relative, marker_yaw_relative):
        '''
        called when a new marker measurement arrives max 30Hz, marker measurements are only available if the quadrotor is
        sufficiently close to a marker
        
        :param marker_position_world - x and y position of the marker in world coordinates 2x1 vector
        :param marker_yaw_world - orientation of the marker in world coordinates
        :param marker_position_relative - x and y position of the marker relative to the quadrotor 2x1 vector
        :param marker_yaw_relative - orientation of the marker relative to the quadrotor
        '''

        # New Sensor/Camera reading arrives        
        z = np.array([[marker_position_relative[0], marker_position_relative[1], marker_yaw_relative]]).T
        z_predicted = self.predictMeasurement(self.x, marker_position_world, marker_yaw_world)
                
        #   ----------> Calculation of the EKF Correction Step (13Hz) [Slide 10 L6.3]
        ##  The Measurement Prediction Jacobian [H] is calculated so they can be applied to the correction step using global marker position coordinates and heading
        H = self.calculatePredictMeasurementJacobian(self.x, marker_position_world, marker_yaw_world)

        #   The Kalman gain is calculate using the Jacobian and measurement (from sensor) noise [R]
        K = self.calculateKalmanGain(self.sigma, H, self.R)

        ##  The mean is calculated for the correction step using Kalman gain [K], observations [z] and predicted observations [z_predicted]        
        self.x = self.correctState(K, self.x, z, z_predicted)

        ##  The covariance is next and calculated for the correction step using the Jacobian [H] and Kalman gain [K]
        self.sigma = self.correctCovariance(self.sigma, K, H)
        
        self.visualizeState()
    
class Pose2D:
    def __init__(self, rotation, translation):
        self.rotation = rotation
        self.translation = translation
        
    def inv(self):
        '''
        inversion of this Pose2D object
        
        :return - inverse of self
        '''
        inv_rotation = self.rotation.transpose()
        inv_translation = -np.dot(inv_rotation, self.translation)
        
        return Pose2D(inv_rotation, inv_translation)
    
    def yaw(self):
        from math import atan2
        return atan2(self.rotation[1,0], self.rotation[0,0])
        
    def __mul__(self, other):
        '''
        multiplication of two Pose2D objects, e.g.:
            a = Pose2D(...) # = self
            b = Pose2D(...) # = other
            c = a * b       # = return value
        
        :param other - Pose2D right hand side
        :return - product of self and other
        '''
        return Pose2D(np.dot(self.rotation, other.rotation), np.dot(self.rotation, other.translation) + self.translation)


