#!/usr/bin/python
import RPi.GPIO as gpio
import os, signal, sys
from time import sleep
gpio.setmode(gpio.BCM)
gpio.setup(15, gpio.IN, pull_up_down = gpio.PUD_DOWN)
gpio.setup(4, gpio.OUT)

def signal_term_handler(signal, frame):
        print 'SIGTERM received. Exiting.'
        gpio.cleanup()
        sys.exit(0)
try:
	while True:
		signal.signal(signal.SIGTERM, signal_term_handler)
		gpio.output(4,1)
		if(gpio.input(15) == 1):
			os.system("sudo shutdown -h now")
			gpio.cleanup()
			break
		sleep(2)
except KeyboardInterrupt:
	print "Interrupted by user"
	gpio.cleanup()
