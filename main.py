from motors import Motors
import RPi.GPIO as GPIO
from time import sleep
import signal
import sys
from reflectance_sensors import ReflectanceSensors

def cleanUp():
    motors.stop()
    GPIO.cleanup()
    sys.exit(0)

main():
	motor    = motors.Motors()
	infrared = reflectance_sensors.ReflectanceSensors()
	
	
	# To exit the program properly on keyboardinterrupt
    def signal_handler(signal, frame):
        motors.stop()
        GPIO.cleanup()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
	
	