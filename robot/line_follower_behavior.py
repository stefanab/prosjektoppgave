#!/usr/bin/env python
import bbcon as bbc # Behavior-based controller
from reflectance_sensors import ReflectanceSensors
from motors import Motors

# A subclass of Behavior which details the behavior of following a line
class FollowLine(bbc.Behavior):

    def __init__(self, bbcon, sensobs=[], trigger=None, act=True, pri=3):
        self.MAX_SPEED = 1000
        self.num_sensors = 6

        self.alpha = 0.75
        self.middle_value = 2500
        self.previous_errors = [0, 0, 0, 0, 0, 0]

        self.last_value = 0 # Initially assume line was last seen on the left
        bbc.Behavior.__init__(self,bbcon, "line_following",sensobs=sensobs,act=act,pri=pri)

	# Determine if the behavior is currently active or not.  This needs to be subclassed for each behavior.
    def do_activation_test(self): return (not self.bbcon.is_gate_found())
    def do_deactivation_test(self): return self.bbcon.is_gate_found()

    # This is the core method for behavior computation; it needs to be subclassed.
    # It's main jobs are a) read sensors, b) update the behavior's match_degree, c) set the motor requests.
    def sense_and_act(self):
        # We only have one sensor object which is the ReflectanceSensors
        sensob = self.sensobs[0]

        values = sensob.get_value() # Returns a 6 dimensional vector 

        print("Sensor values: " + '\n')
        print(values)

        avg = 0.0
        vSum = 0.0 
        onLine = 0
        for i in range(len(values)):
            value = values[i]
            if value > 0.2:
                onLine = 1

            if value > 0.05:
                avg += (value * i * 1000);
                vSum += value;

        if(onLine == 0):
            # If it last read to the left of center, set last_value to 0.
            if(self.last_value < self.middle_value): 
                self.last_value = 0

            # If it last read to the right of center, set last_value to max
            else:
                self.last_value = (self.num_sensors-1)*1000
        else:
            print("on line!")
            self.last_value = avg/vSum

        # Use the self.last_value to determine what the motors should be set two
        return self.set_motors()

    def set_motors(self):
        # Our "error" is how far we are away from the center of the line, which
        # corresponds to position 2500.
        error = self.last_value - self.middle_value; 

        print("error: " + str(error))

        #  Get motor speed difference using proportional and derivative PID terms
        #  (the integral term is generally not very useful for line following).
        #  Here we are using a proportional constant of 1/4 and a derivative
        #  constant of 6, which should work decently for many Zumo motor choices.
        #  You probably want to use trial and error to tune these constants for
        #  your particular Zumo and line course.
        speed_difference = error / 4 + 6 * self.sum_weighted_errors(error) 

        print("speed_difference: " + str(speed_difference))

        # Reset the previous error by shifting current errors one position and 
        # setting the first item in previous_error to the newly recorded error
        i = len(self.previous_errors) - 1
        while i > 0:
            self.previous_errors[i] = self.previous_errors[i - 1] 
            i -= 1

        self.previous_errors[0] = error 

        # Get individual motor speeds.  The sign of speedDifference
        # determines if the robot turns left or right.
        m1_speed = (self.MAX_SPEED + speed_difference)/4; # Divide by 4 so the robot doesn't go to fast
        m2_speed = (self.MAX_SPEED - speed_difference)/4;

        # Here we constrain our motor speeds to be between 0 and MAX_SPEED.
        # Generally speaking, one motor will always be turning at MAX_SPEED
        # and the other will be at MAX_SPEED-|speedDifference| if that is positive,
        # else it will be stationary.  For some applications, you might want to
        # allow the motor speed to go negative so that it can spin in reverse.
        if (m1_speed < 0):
            m1_speed = 0
        if (m2_speed < 0):
            m2_speed = 0
        if (m1_speed > self.MAX_SPEED):
            m1_speed = self.MAX_SPEED
        if (m2_speed > self.MAX_SPEED):
            m2_speed = self.MAX_SPEED

        # If error is maximum (2500) then this motor request becomes essential for us to continue
        # following the line
        match_degree = abs(error)/self.middle_value
        self.set_match_degree(match_degree)

        # Set the motor_requests to be m1_speed and m2_speed
        self.set_motor_requests([int(m1_speed), int(m2_speed)])

    def sum_weighted_errors(self, error):
        error_sum = 0
        i = 0
        for i in range(len(self.previous_errors)):
            error_sum += (error - self.previous_errors[i]) * (self.alpha**(i+1))
        return error_sum

