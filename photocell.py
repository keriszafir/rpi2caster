#!/usr/bin/python
import RPi.GPIO as gpio
gpio.setmode(gpio.BCM)
gpio.setup(14, gpio.IN, pull_up_down = gpio.PUD_UP)

while True:
	if(gpio.input(14) == 1):
		print "Photo cell activated."
		gpio.cleanup()
		break
