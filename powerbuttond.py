#!/usr/bin/python
import RPi.GPIO as gpio
import os, sys, time, signal

try:

	gpio.setmode(gpio.BCM)
	gpio.setwarnings(False)
	gpio.setup(15, gpio.IN, pull_up_down = gpio.PUD_DOWN)
	gpio.setup(4, gpio.OUT)
	gpio.output(4,1)

except RuntimeError:

	print("You must run this program as root!")
	sys.exit()

def blink(n,speed):
	for i in range(0,n):
		gpio.output(4,0)
		time.sleep(speed)
		gpio.output(4,1)
		time.sleep(speed)

def signal_handler(signal, frame):
	print("Terminated by OS")
	blink(10,0.5)
	gpio.output(4,0)
	gpio.cleanup()
	sys.exit()

def shutdown(channel):
	time.sleep(2)
	if (gpio.input(15) == 1):
		blink(5,0.1)
		os.system("sudo shutdown -h now")

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

gpio.add_event_detect(15, gpio.RISING, callback = shutdown, bouncetime = 2000)

while True:
	time.sleep(1)
