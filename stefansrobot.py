#!/usr/bin/env python
from time import sleep
import signal
import sys
import RPi.GPIO as GPIO
import robot.bbcon as bbc # Behavior-based controller
from robot.reflectance_sensors import ReflectanceSensors
from robot.camera import Camera
from robot.motors import Motors
from robot.line_follower_behavior import FollowLine
from robot.camera_search_behavior import Camera_search
from robot.stop_follow_line_behavior import StopFollowLine
from robot.wander_behavior import Wander
from findobj_behavior import FindObject

# Sub class for a BBCon where objectives can be specified specified
class RobotController(bbc.BBCon):

    def __init__(self,agent,arb_type='Arbitrator',tdur=0.5,stoch=False):
    	self.found_gate = False
    	self.found_blob = False
    	# Call super class __init__ method for setup
    	bbc.BBCon.__init__(self, agent, arb_type, 0.1, stoch)

    # Getters and setters for determining if the blob has been found
    # which are used by the behaviors
    def set_gate_found(self, is_found): self.found_gate = is_found 
    def is_gate_found(self): return self.found_gate
    def set_blob_found(self, is_found): self.found_blob = is_found
    def is_blob_found(self): return self.found_blob

def bbrun():

    # Main function sets up motobs/sensobs and behavors
    sensobs = []
    # Calibration begins here. Students should slowly spin the robot around the
    # line in a circle trying hard not to lift it up off the ground. As of now,
    # calibration lasts 15 seconds which is plenty of time. Without proper
    # calibration, the line following behavior may not work properly.
    # Calibration determines the maximum and minimum values found by each sensor,
    # which is necessary for returning the normalized values (reals from 0 to 1)
    # of each sensor.
    # Edit: I have turned off calibration for now, because hard-coding the configuration
    # is working good enough and I don't have to use time on calibrating under testing
    motors = Motors()
    motors.stop()
    sleep(2)

    # To exit the program properly on keyboardinterrupt
    def signal_handler(signal, frame):
        motors.stop()
        GPIO.cleanup()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    reflectanceSensob = bbc.Sensob(ReflectanceSensors())
    cameraSensob      = bbc.Sensob(Camera())
    sensobs.append(reflectanceSensob)
    sensobs.append(cameraSensob)
    motob = bbc.Motob(motors)
    bbcon = RobotController(None) # None agent
    # Create the behaviors
    # The behaviors has priorities of 3,3,5,and 1 respectively
    followLineBehavior = FollowLine(bbcon, sensobs[0:1])
    findObjectBehavior = FindObject(bbcon, sensobs[1:2])	
    bbcon.add_behavior(followLineBehavior)
    bbcon.add_behavior(findObjectBehavior)
    
    bbcon.add_motob(motob)
    bbcon.add_sensob(reflectanceSensob)
    bbcon.add_sensob(cameraSensob)
    
    i = 0
    halt_flag = False
    while not halt_flag and i < 300:
          print("Iteration " + str(i))
          i += 1
          
          halt_flag = bbcon.run_one_timestep()


    # Called at the end
    motors.stop()
	
# If we run this file from the command line, via "python3 roborun.py", then this insures that bbrun gets called.
if __name__ == '__main__':
    bbrun()
