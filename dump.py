#!/usr/bin/python

# Monotype composition caster dump program by Christophe Slychan
# The program reads a "ribbon" file, then waits for the user to start casting. During each machine cycle, the photocell is obscured (high state)
# or lit (low state). When high, the program reads a line from ribbon and turns on the solenoid valves respective to the Monotype control codes.
# After the photocell is lit, the valves are turned off and the program moves on to the next line.

import sys, os, time, string, csv
import wiringpi2 as wiringpi
import RPi.GPIO as gpio

# Commment out lines referring to RPi.GPIO or WiringPi, depending on which module you use for reading the photocell input.
# RPi.GPIO requires you to run the program as root. WiringPi has some problems with input interrupt handling.

#gpio.setmode(gpio.BCM)
wiringpi.wiringPiSetup()
wiringpi.pinMode(14, 0)
wiringpi.pullUpDnControl(14, 2)
#gpio.setup(14, gpio.IN, pull_up_down = gpio.PUD_UP)
#gpio.add_event_detect(14, gpio.RISING, bouncetime = 10)
wiringpi.mcp23017Setup(65,0x20)
wiringpi.mcp23017Setup(81,0x21)
for pin in range(65,97):
	wiringpi.pinMode(pin,1)

# Assign wiringPi pin numbers on MCP23017s to the Monotype control codes.

monotypeSignal = dict([('1', 65), ('2', 66), ('3', 67), ('4', 68), ('5', 69), ('6', 70), ('7', 71), ('8', 72), ('9', 73), ('10', 74), ('11', 75), ('12', 76), ('13', 77), ('14', 78), ('0005', 79), ('0075', 80), ('A', 81), ('B', 82), ('C', 83), ('D', 84), ('E', 85), ('F', 86), ('G', 87), ('H', 88), ('I', 89), ('J', 90), ('K', 91), ('L', 92), ('M', 93), ('N', 94), ('S', 95), ('O15', 96)])

# Read the input file.

with open(sys.argv[1], 'rb') as ribbon:
	reader = csv.reader(ribbon)
	for row in reader:
		print(row)
try:
	print("It works!")		
except RuntimeError:
	print("You must run this program as root!")
except KeyboardInterrupt:
	print("Terminated by user.")
finally:
	for pin in range(65,97):
		wiringpi.digitalWrite(pin, 0)
#	gpio.cleanup()
	exit()
