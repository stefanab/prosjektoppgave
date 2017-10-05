import RPi.GPIO as gpio
from time import sleep


gpio.setmode(gpio.BOARD)

motorA = 12
motorB = 35
motorE = 22

gpio.setup(motorA, gpio.OUT)
gpio.setup(motorB, gpio.OUT)
gpio.setup(motorE, gpio.OUT)

gpio.output(motorA, gpio.HIGH)
gpio.output(motorB, gpio.HIGH)
gpio.output(motorE, gpio.HIGH)

sleep(1)

gpio.output(motorA, gpio.LOW)
gpio.output(motorB, gpio.LOW)

gpio.cleanup()