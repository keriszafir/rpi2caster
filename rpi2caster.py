#!/usr/bin/python

# Monotype composition caster & keyboard paper tower control program by Christophe Slychan
# The program reads a "ribbon" file, then waits for the user to start casting or punching the paper tape. 
# In the casting mode, during each machine cycle, the photocell is obscured (high state) or lit (low state). 
# When high, the program reads a line from ribbon and turns on the solenoid valves respective to the Monotype control codes.
# After the photocell is lit, the valves are turned off and the program moves on to the next line.

import sys, os, time, string, csv, readline, glob
import wiringpi2 as wiringpi

#import RPi.GPIO as gpio

# Commment out lines referring to RPi.GPIO or WiringPi, depending on which module you use for reading the photocell input.
# RPi.GPIO requires you to run the program as root. WiringPi has some problems with input interrupt handling.

# I think we'll stick with WiringPi. Less dependencies, can be configured to run as normal user. We still need it for MCP23017. 
# WiringPi seems to have an interrupt handling if you use sysfs interface.
# We need to set up the sysfs interface before (powerbuttond.py - a daemon running on boot with root privileges takes care of it)

# Might need to change powerbuttond.py to set envvar or touch a file in /run to indicate that the photocell GPIO is initialized properly.
# Or just check if the intput is exported... 

# In the future, we'll add configurable GPIO numbers. Why store the device config in the program source, if we can use a .conf file?

wiringpi.wiringPiSetupSys()
#wiringpi.pinMode(14, 0) # already taken care of in powerbuttond.py
#gpio.setmode(gpio.BCM)
#gpio.setup(14, gpio.IN, pull_up_down = gpio.PUD_UP)
#gpio.add_event_detect(14, gpio.RISING, bouncetime = 10)
wiringpi.mcp23017Setup(65,0x20)
wiringpi.mcp23017Setup(81,0x21)
for pin in range(65,97):
  wiringpi.pinMode(pin,1)

# Assign wiringPi pin numbers on MCP23017s to the Monotype control codes.
wiringPiPinNumber = dict([('1', 65), ('2', 66), ('3', 67), ('4', 68), ('5', 69), ('6', 70), ('7', 71), ('8', 72), ('9', 73), ('10', 74), ('11', 75), ('12', 76), ('13', 77), ('14', 78), ('0005', 79), ('0075', 80), ('A', 81), ('B', 82), ('C', 83), ('D', 84), ('E', 85), ('F', 86), ('G', 87), ('H', 88), ('I', 89), ('J', 90), ('K', 91), ('L', 92), ('M', 93), ('N', 94), ('S', 95), ('O15', 96)])

# Set up comment symbols for parsing the ribbon files:
commentSymbol = '//'

# This function enables tab key auto-completion when you enter the filename. Will definitely come in handy.
def complete(text, state):
  return (glob.glob(text+'*')+[None])[state]
readline.set_completer_delims(' \t\n;')
readline.parse_and_bind("tab: complete")
readline.set_completer(complete)

global inputFileName
inputFileName = ""
def enter_filename():
  global inputFileName
  inputFileName = raw_input("\n Enter the ribbon file name: ")

def menu():
  os.system("clear")
  print("rpi2caster - Monotype Composition Caster control utility by Christophe Slychan.\n\nThis program reads a ribbon (input file) and casts the type on a Composition Caster, or punches a paper tape.\n")
  ans = True
  while ans:
    print ("""
		Main menu:

		1. Load a ribbon file

		2. Cast type from ribbon file

		3. Punch a paper tape

		4. Calibrate the caster



		0. Exit to shell

		""")

    if inputFileName != "":
      print("Input file name: " + inputFileName + "\n")

    ans = raw_input("Choose an option: ") 
    if ans=="1": 
      enter_filename()
      menu()
    elif ans=="2":
      cast(inputFileName, "cast")
    elif ans=="3":
      cast(inputFileName, "punch")
    elif ans=="4":
      print("\n Testing the machine...")


    elif ans=="0":
      print("\nGoodbye! :)\n")
      exit()
    elif ans !="":
      print("\nNo such option. Choose again.")

def activate_valves(mode, row):
  if ( wiringpi.digitalRead(14) == 1):
    for monotypeSignal in row:
      pin = wiringPiPinNumber[str.upper(monotypeSignal)]
      wiringpi.digitalWrite(pin,1)
      if mode == "punch":
        wiringpi.digitalWrite(wiringPiPinNumber["O15"],1)
  else:
    for pin in range(65,97):
      wiringpi.digitalWrite(pin,0)

# Main casting/punching routine.
# When punching, the input file is read in reversed order and an additional line (O15) is switched on for operating the paper tower.
# The input file can contain lowercase (a, b, g, s...) or uppercase (A, B, G, S...) signals. The program will translate them.
def cast(filename, mode):
  with open(filename, 'rb') as ribbon:
    if mode == "punch":
      reader = csv.reader(ribbon, delimiter=';')
      print("\nThe combinations of Monotype signals will be displayed on screen while the paper tower punches the ribbon.\n")
      raw_input("\nInput file found. Turn on the air, fit the tape on your paper tower and press return to start punching.\n")
    else:
      reader = reversed(list(csv.reader(ribbon, delimiter=';')))
      print("\nThe combinations of Monotype signals will be displayed on screen while the machine casts the type.\n")
      raw_input("\nInput file found. Press return to start casting.\n")
    for row in reader:
      if ((' '.join(row)).startswith(commentSymbol)):
        print(' '.join(row)[2:])
      else:
        print(str.upper(' '.join(row)))

# Activate valves as specified in row, then wait and deactivate them. 
# For punching, activate additional O15 the keyboard paper tower needs.:
#      activate_valves(mode, row)
#      time.sleep(2)
#      deactivate_valves()
			
# Wait for interrupt from photocell and activate the valves
        wiringpi.wiringPiISR(14, 3, activate_valves(mode, row))  # rising: activate, falling: deactivater

# After casting/punching is finished:

  raw_input("\nEnd of ribbon. All done. Press return to go to main menu.")
  main()

# Main loop definition. All exceptions should be caught here.
def main():
  try:
    menu()
  except RuntimeError:
    print("\nYou must run this program as root!")
#  except (IOError, NameError):
#    raw_input("\nInput file not chosen or wrong input file name. Press return to go to main menu.\n")
#    main()
  except KeyboardInterrupt:
    print("Terminated by user.")
    for pin in range(65,97):
      wiringpi.digitalWrite(pin, 0)
    exit()
  finally:
    for pin in range(65,97):
      wiringpi.digitalWrite(pin, 0)
#    gpio.cleanup()

# Do the main loop.
main()
