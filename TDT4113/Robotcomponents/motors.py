#!/usr/bin/env python
from time import sleep
import RPi.GPIO as GPIO
import wiringpi2 as wp 

class Motors():

	def __init__(self):
		self.setup()

	def setup(self):
		self.max = 1024
		self.high = 500
		self.normal = 300 
		self.low = 100

		wp.wiringPiSetupGpio()

		wp.pinMode(18, 2)
		wp.pinMode(19, 2)
		wp.pinMode(23, 1)
		wp.pinMode(24, 1)

		wp.digitalWrite(23, 0)
		wp.digitalWrite(24, 0)

		self.freq = 400	# PWM frequency
		self.dc = 0		# Duty cycle
		print("Completed setting up motors!")

	def forward(self):
		self.dc = self.normal
		wp.digitalWrite(23, 0)
		wp.digitalWrite(24, 0)
		wp.pwmWrite(18, self.dc)
		wp.pwmWrite(19, self.dc)

	def backward(self):
		self.dc = self.normal
		wp.digitalWrite(23, 1)
		wp.digitalWrite(24, 1)
		wp.pwmWrite(18, self.dc)
		wp.pwmWrite(19, self.dc)

	def left(self):
		if self.dc == 0:
			wp.digitalWrite(23, 1)
			wp.pwmWrite(18, self.low)
			wp.digitalWrite(24, 0)
			wp.pwmWrite(19, self.low)
		else:
			wp.pwmWrite(18, 150)
			wp.pwmWrite(19, 450)
		
	def right(self):
		if self.dc == 0:
			wp.digitalWrite(23, 0)
			wp.pwmWrite(18, self.normal)
			wp.digitalWrite(24, 1)
			wp.pwmWrite(19, self.normal)
		else:
			wp.pwmWrite(18, 450)
			wp.pwmWrite(19, 150)
			
	def stop(self):
		self.dc = 0
		wp.pwmWrite(18, self.dc)
		wp.pwmWrite(19, self.dc)

	# Val should be a 2 dimensional vector with values for the left and right motor speeds
	def set_value(self, val):
		left_val = val[0]
		right_val = val[1]

		# If we pass negative values to the motors, we need to reverse the direction of the motor
		self.set_left_dir(1) if (left_val < 0) else self.set_left_dir(0)
		self.set_right_dir(1) if (right_val < 0) else self.set_right_dir(0)

		# Set speed to the absolute value of the passed values
		self.set_left_speed(abs(left_val))
		self.set_right_speed(abs(right_val))

	def set_left_speed(self, dc):
		wp.pwmWrite(18, dc)

	def set_right_speed(self, dc):
		wp.pwmWrite(19, dc)

	def set_left_dir(self, is_forward):
		wp.digitalWrite(23, is_forward) # 0 is forward so if they pass 1 we 'not' it

	def set_right_dir(self, is_forward):
		wp.digitalWrite(24, is_forward) # 0 is forward so if they pass 1 we 'not' it

