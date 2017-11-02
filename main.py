#!/usr/bin/env python

import RPi.GPIO as GPIO
from time import sleep
import signal
import sys
from robot.motors import Motors
from robot.reflectance_sensors import ReflectanceSensors
from constparimg import constantParametersImage

def cleanUp():
    motors.stop()
    GPIO.cleanup()
    sys.exit(0)


def main():
    imgPars   = constantParametersImage()
    camera    = Camera(width=imgPars.width, height=imgPars.height)
    camera.sensor_get_value()
    motors    = Motors()
    infrared  = ReflectanceSensors()
    infrared.calibrate()
    infrared.update()
    sleep(5)
    print("setup")
        
    # To exit the program properly on keyboardinterrupt
    def signal_handler(signal, frame):
        motors.stop()
        GPIO.cleanup()
        sys.exit(0)
       
    signal.signal(signal.SIGINT, signal_handler)
    
    
    ##motors.forward(dur=1)
    iteration = 0
    # while(not isGoal(infrared) and iteration < 5):
	
        # motors.forward(dur=1)
        # infrared.update()
        # sleep(1)
        # iteration += 1
    motors.stop()
    GPIO.cleanup()
##    
    
def isGoal(infrared):
    values = infrared.get_value()
    darks = 0
    avg = 0
    vSum = 0
    print(values)
    for i in range(len(values)):
            value = values[i]
            if value < 0.8:
                darks += 1

            if value < 0.75:
                avg += (value * i * 1000);
                vSum += value;

            
    print("darks " + str(darks))
    
    if(darks >= 6):
        return True
    else:
        return False
    
    
    
if __name__ == "__main__":
    main()
    
    
