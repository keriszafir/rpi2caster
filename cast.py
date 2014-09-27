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
#wiringpi.wiringPiSetup()
#wiringpi.pinMode(14, 0)
#wiringpi.pullUpDnControl(14, 2)
#gpio.setup(14, gpio.IN, pull_up_down = gpio.PUD_UP)
#gpio.add_event_detect(14, gpio.RISING, bouncetime = 10)
wiringpi.mcp23017Setup(65,0x20)
wiringpi.mcp23017Setup(81,0x21)
for pin in range(65,97):
	wiringpi.pinMode(pin,1)

# Assign wiringPi pin numbers on MCP23017s to the Monotype control codes.

wiringPiPinNumber = dict([('1', 65), ('2', 66), ('3', 67), ('4', 68), ('5', 69), ('6', 70), ('7', 71), ('8', 72), ('9', 73), ('10', 74), ('11', 75), ('12', 76), ('13', 77), ('14', 78), ('0005', 79), ('0075', 80), ('A', 81), ('B', 82), ('C', 83), ('D', 84), ('E', 85), ('F', 86), ('G', 87), ('H', 88), ('I', 89), ('J', 90), ('K', 91), ('L', 92), ('M', 93), ('N', 94), ('S', 95), ('O15', 96)])

try:

	print("rpi2caster - Monotype Composition Caster control utility by Christophe Slychan.\n\nThis program reads a ribbon (input file) and casts the type on a Composition Caster.\n")

# Read the input file. Wait until user presses return. Parse a row, print a combination of signals and turn proper valves on.
# The input file can contain lowercase (a, b, g, s...) or uppercase (A, B, G, S...) signals. The program will translate them.
	with open(sys.argv[1], 'rb') as ribbon:
		reader = csv.reader(ribbon, delimiter=';')
		raw_input("Input file found. Press return to start casting.")
		print("\nThe combinations of Monotype signals will be displayed on screen while the machine casts the type.\n")
		for row in reader:
			print(str.upper(' '.join(row)))
			for cell in row:
				monotypeSignal = str.upper(cell)
				pin = wiringPiPinNumber[monotypeSignal]
				wiringpi.digitalWrite(pin,1)
# Wait 2 seconds. In the future, this will be replaced with waiting for photocell interrupt.
			time.sleep(2)
# Turn all valves off before starting next cycle.
			for pin in range(65,97):
				wiringpi.digitalWrite(pin,0)
	print("\nEnd of ribbon. Casting finished.")		
except RuntimeError:
	print("You must run this program as root!")
except IndexError:
	print("You must specify the input file - run as " + sys.argv[0] + " [FILENAME]")
except IOError:
	print("Wrong input file name!")
except KeyboardInterrupt:
	print("Terminated by user.")
finally:
	for pin in range(65,97):
		wiringpi.digitalWrite(pin, 0)
#	gpio.cleanup()
	exit()
