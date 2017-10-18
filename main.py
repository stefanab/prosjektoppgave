#!/usr/bin/env python

import RPi.GPIO as GPIO
from time import sleep
import signal
import sys
from motors import Motors
from reflectance_sensors import ReflectanceSensors

def cleanUp():
    motors.stop()
    GPIO.cleanup()
    sys.exit(0)


def main():
    motors    = Motors()
    infrared  = ReflectanceSensors()
	(infrared.update())
    print("setup")
        
	# To exit the program properly on keyboardinterrupt
    def signal_handler(signal, frame):
       motors.stop()
       GPIO.cleanup()
       sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    ##motors.forward(dur=1)
    iteration = 0
	while(!isGoal(infrared) && iteration < 5):
        (infrared.update())
	    motors.forward(dur=.3)
		sleep(1)
		iteration += 1
	   
    
##    motors.stop()
  ##  GPIO.cleanup()
##    
    
def isGoal(infrared):
	values = infrared.get_value()
	darks = 0
	for i in range(len(values)):
        value = values[i]
        if value > 0.2:
            darks += 1

        if value > 0.05:
            avg += (value * i * 1000);
            vSum += value;

			
	print("darks " + str(darks))
	
	if(darks >= 6):
		return true
	else:
		return false
	
	
	
if __name__ == "__main__":
    main()
	
	
