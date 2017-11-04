#!/usr/bin/env python
import robot.bbcon as bbc # Behavior-based controller
from robot.reflectance_sensors import ReflectanceSensors
from robot.motors import Motors
import numpy as np
from constparimg import constantParametersImage, constantParametersNetwork
import tflearn
import tensorflow as tf
from tflearn.layers.conv import conv_2d, max_pool_2d
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.estimator import regression
from create_image_data_set import create_feature_sets_and_labels

# A subclass of Behavior which details the behavior of following a line. Assumtion is that lines will be dark.
class FindObject(bbc.Behavior):

    def __init__(self, bbcon, sensobs=[], model=None, trigger=None, act=True, pri=1):
        bbc.Behavior.__init__(self,bbcon, "object_search", sensobs=sensobs,act=act,pri=pri)
	self.last_value = None# Initially assume line was last seen on the left
        self.model = self.build_neural_network()

	# Determine if the behavior is currently active or not.  This needs to be subclassed for each behavior.
    def do_activation_test(self): return (not self.bbcon.is_gate_found())
    def do_deactivation_test(self): return self.bbcon.is_gate_found()

    def build_neural_network(self):
        param = constantParametersImage()
        n_classes = 2
        
        b_size = 128
        l_rate = 0.001
        convnet = input_data(shape=[None, param.height, param.width, param.channels], name='input')

        convnet = conv_2d(convnet, 32, 8, strides=4, activation='relu')
        #convnet = max_pool_2d(convnet, 2)

        convnet = conv_2d(convnet, 64, 4, strides=2, activation='relu')
        #convnet = max_pool_2d(convnet, 2)

        convnet = conv_2d(convnet, 64, 3, strides=1, activation='relu')
        #convnet = max_pool_2d(convnet, 2)

        convnet= fully_connected(convnet, 512, activation='relu')
        convnet = dropout(convnet, .8)

        convnet = fully_connected(convnet, n_classes, activation='softmax')

        convnet = regression(convnet, optimizer='adam', batch_size=b_size, learning_rate=l_rate, loss='categorical_crossentropy', name='targets')

        model = tflearn.DNN(convnet)
        model.load('tflearncnnmug.model')
        
        return model

    # This is the core method for behavior computation; it needs to be subclassed.
    # It's main jobs are a) read sensors, b) update the behavior's match_degree, c) set the motor requests.
    def sense_and_act(self):
        # We only have one sensor object which is the ReflectanceSensors
        sensob = self.sensobs[0]

        values = sensob.get_value() # Returns a 6 dimensional vector 
        print('image value')
        print(values)
        prediction = self.model.predict(values)
        
        print(prediction)
		

        # Use the self.last_value to determine what the motors should be set two
        return self.set_motors()

	
		
    def set_motors(self):
        # Our "error" is how far we are away from the center of the line, which
        # corresponds to position 2500.
        #error = self.last_value - self.middle_value; 
	
	# dark values are lower than light ones. Negative values means that there was more "Dark" on the left side.
	# Means we should turn left


	m1_speed = 0
        m2_speed = 0
        #  Get motor speed difference using proportional and derivative PID terms
        #  (the integral term is generally not very useful for line following).
        #  Here we are using a proportional constant of 1/4 and a derivative
        #  constant of 6, which should work decently for many Zumo motor choices.
        #  You probably want to use trial and error to tune these constants for
        #  your particular Zumo and line course.
        #speed_difference = error / 4 + 6 * self.sum_weighted_errors(error) 

        

        # Reset the previous error by shifting current errors one position and 
        # setting the first item in previous_error to the newly recorded error
        # i = len(self.previous_errors) - 1
        # while i > 0:
            # self.previous_errors[i] = self.previous_errors[i - 1] 
            # i -= 1

        # self.previous_errors[0] = error 

        # Get individual motor speeds.  The sign of speedDifference
        # determines if the robot turns left or right.


        # Here we constrain our motor speeds to be between 0 and MAX_SPEED.
        # Generally speaking, one motor will always be turning at MAX_SPEED
        # and the other will be at MAX_SPEED-|speedDifference| if that is positive,
        # else it will be stationary.  For some applications, you might want to
        # allow the motor speed to go negative so that it can spin in reverse.


        # If error is maximum (2500) then this motor request becomes essential for us to continue
        # following the line
        match_degree = 0
        self.set_match_degree(match_degree)

        # Set the motor_requests to be m1_speed and m2_speed
        self.set_motor_requests([int(m1_speed), int(m2_speed)])

