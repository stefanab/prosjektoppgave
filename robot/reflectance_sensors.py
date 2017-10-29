#!/usr/bin/env python
from time import sleep
import datetime
import RPi.GPIO as GPIO
import Motors as motor


class ReflectanceSensors():
    # The constructor allows students to decide if they want to auto_calibrate
    # the robot, or if they want to hard code the min and max readings of the
    # reflectance sensors
    def __init__(self, auto_calibrate=False, min_reading=100, max_reading=1000):
        self.setup()
        if not (auto_calibrate):
            # Calibration loop should last ~5 seconds
            # Calibrates all sensors
            self.calibrate()
                
        else:
            for i in range(len(self.max_val)):
                self.max_val[i] = max_reading
                self.min_val[i] = min_reading

        print("Calibration results")
        print(self.max_val)
        print(self.min_val)


    def setup(self):
        # Initialize class variables
        self.max_val = [-1, -1, -1, -1, -1, -1]
        self.min_val = [-1, -1, -1, -1, -1, -1]
        self.start_time = -1
        # Initialize value array to all negative values, which should never appear
        # as an actual result
        self.value = [-1.0, -1.0, -1.0, -1.0, -1.0, -1.0]
        # A dictionary mapping each channel to the index it's value is located in
        # the value array
        self.sensor_indices = {29: 5, 36: 4, 37: 3, 31: 2, 32: 1, 33: 0}
        self.updated = False
        # For GPIO.BOARD
        self.sensor_inputs = [33, 32, 31, 37, 36, 29]  # Sensors from left to right

        # Set the mode to GPIO.BOARD
        GPIO.setmode(GPIO.BOARD)

    #Calibrates the motors. If the function is called from outside the motors are used to indicate that the 
    #robot should be moved for the next calibration.
    def calibrate(self, motob=None):
        print("calibrating...")
        self.recharge_capacitors()
        
        # GPIO.setup(sensor_inputs, GPIO.IN)
        print("Put robot on darkest spot...")
        
        for pin in self.sensor_inputs:
            time = self.get_sensor_reading(pin)

            # Get the index from the map
            index = self.sensor_indices[pin]
             
            self.min_val[index] = time.microseconds
                
            # Print the calculated time in microseconds
            print("Pin: " + str(pin))
            print(time.microseconds)
            
        if motob:
            motob.forward(.2)
        
        print("now put the robot on the lightest spot")
        sleep(5)
        
        for pin in self.sensor_inputs:
            time = self.get_sensor_reading(pin)

            # Get the index from the map
            index = self.sensor_indices[pin]
            
            self.max_val[index] = time.microseconds
                
            # Print the calculated time in microseconds
            print("Pin: " + str(pin))
            print(time.microseconds)
            
        
            
            

    def get_sensor_reading(self, pin):
        GPIO.setup(pin, GPIO.IN)
        # Measure the time
        start_time = datetime.datetime.now()

        while GPIO.input(pin):
            pass

        # Measure time again
        end_time = datetime.datetime.now()
        # Calculate the time passed
        time = end_time - start_time
        return time


    def recharge_capacitors(self):
        # Make all sensors an output, and set all to HIGH
        GPIO.setup(self.sensor_inputs, GPIO.OUT)
        GPIO.output(self.sensor_inputs, True)
        # Wait 5 milliseconds to ensure that the capacitor is fully charged
        sleep(0.005)


    def reset(self):
        self.updated = False
        self.value = [-1.0, -1.0, -1.0, -1.0, -1.0, -1.0]


    # Function should return a list of 6 reals between 0 and 1.0 indicating
    # the amount of reflectance picked up by each one.  A high reflectance (near 1) indicates a LIGHT surface, while
    # a value near 0 indicates a DARK surface.

    def get_value(self):
        return self.value


    def update(self):
        self.compute_value()
        return self.value


    def compute_value(self):
        self.recharge_capacitors()
        for pin in self.sensor_inputs:
            time = self.get_sensor_reading(pin)

            index = self.sensor_indices[pin]
            self.value[index] = 1 - self.normalize(index, time.microseconds)


    # Uses the calibrated min and maxs for each sensor to return a normalized
    # value for the @param sensor_time for the given @param index
    def normalize(self, index, sensor_time):
        print("normalize")
        normalized_value = float(sensor_time) / (self.max_val[index] - self.min_val[index])
        if (normalized_value > 1.0):
            return 1.0
        elif (normalized_value < 0.0):
            return 0.0
        return normalized_value
