#!/usr/bin/env python
import bbcon as bbc # Behavior-based controller
from reflectance_sensors import ReflectanceSensors
from motors import Motors
import math

# A subclass of Behavior which details the behavior of following a line. Assumtion is that lines will be dark.
class FindObject(bbc.Behavior):

    def __init__(self, bbcon, sensobs=[], model=None, trigger=None, act=True, pri=1):
        bbc.Behavior.__init__(self,bbcon, "object_search", sensobs=sensobs,act=act,pri=pri)
		self.last_value = None# Initially assume line was last seen on the left

	# Determine if the behavior is currently active or not.  This needs to be subclassed for each behavior.
    def do_activation_test(self): return (not self.bbcon.is_gate_found())
    def do_deactivation_test(self): return self.bbcon.is_gate_found()

    def checkHalt(self):
		sum = self.sum_colors()
		match = 0
                print("sum")
                print(sum)
		if sum == 6:
                    print("all white")
		    return True
		
		
		if(sum == 3):
		    first_color = self.colors[0]
		    if(first_color == 0):
			match = 1
			excpected = 1
			while(self.colors[match] == excpected and match < 6):
			    match += 1
			    if(excpected == 0):
                                excpected = 1
                            else:
                                excpeted = 0
			
		    elif(first_color == 1):
			match = 1
			excpected = 0
			while(self.colors[match] == excpected and match < 6):
			    match += 1
			    if(excpected == 0):
                                excpected = 1
                            else:
                                excpeted = 0
		
		if(match == 6):
                    print("match!")
		    return True
			
		return False

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
	    if(i < len(values)/2):
                valueLeft  = values[i]
		valueRight = values[len(values)-1-i]
                vSum += (valueLeft - valueRight ) * (10000/(100*i+1))  
			
	    if(values[i] < 0.7): self.colors[i] = 0
			    
	    elif(values[i] > 0.90): self.colors[i] = 1
			
	    else: self.colors[i] = 0

        print(self.colors)
	if(self.checkHalt()):
            print("requesting halt")
	    self.request_halt()
        else:
            print("no halt")
        self.last_value = vSum

        print(vSum)
		

        # Use the self.last_value to determine what the motors should be set two
        return self.set_motors()

	
		
    def set_motors(self):
        # Our "error" is how far we are away from the center of the line, which
        # corresponds to position 2500.
        #error = self.last_value - self.middle_value; 
	print("line location: " + str(self.last_value))
	# dark values are lower than light ones. Negative values means that there was more "Dark" on the left side.
	# Means we should turn left


	m1_speed = (self.MAX_SPEED + self.last_value)/2; # Divide by 4 so the robot doesn't go to fast
        m2_speed = (self.MAX_SPEED - self.last_value)/2;
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
        match_degree = abs(self.last_value)
        self.set_match_degree(match_degree)

        # Set the motor_requests to be m1_speed and m2_speed
        self.set_motor_requests([int(m1_speed), int(m2_speed)])

    def sum_colors(self):
	sum = 0
	for i in range(len(self.colors)):
	    sum += self.colors[i]
			
	return sum
		
    def sum_weighted_errors(self, error):
        error_sum = 0
        i = 0
        for i in range(len(self.previous_errors)):
            error_sum += (error - self.previous_errors[i]) * (self.alpha**(i+1))
        return error_sum

