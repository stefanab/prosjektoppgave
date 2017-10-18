#!/usr/bin/env python

import RPi.GPIO as GPIO
from time import sleep
import signal
import sys
from robot.motors import Motors
from robot.reflectance_sensors import ReflectanceSensors
def main():
    motors    = Motors()
    infrared = ReflectanceSensors()
    print("setup")
	
##	# To exit the program properly on keyboardinterrupt
##    def signal_handler(signal, frame):
##        motors.stop()
##        GPIO.cleanup()
##        sys.exit(0)
##    signal.signal(signal.SIGINT, signal_handler)
    motors.forward(dur=1)
    
    (infrared.update())
    
##    motors.stop()
  ##  GPIO.cleanup()
##    
    
if __name__ == "__main__":
    main()
	
	