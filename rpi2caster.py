#!/usr/bin/python

# Monotype composition caster & keyboard paper tower control program by Christophe Slychan
# The program reads a "ribbon" file, then waits for the user to start casting or punching the paper tape.
# In the casting mode, during each machine cycle, the photocell is obscured (high state) or lit (low state).
# When high, the program reads a line from ribbon and turns on the solenoid valves respective to the Monotype control codes.
# After the photocell is lit (low state on input), the valves are turned off and the program moves on to the next line.

import sys, os, time, string, csv, readline, glob, select
import wiringpi2 as wiringpi


def input_setup():
# We need to set up the sysfs interface before (powerbuttond.py - a daemon running on boot with root privileges takes care of it)
# In the future, we'll add configurable GPIO numbers. Why store the device config in the program source, if we can use a .conf file?
  photocellGPIO = 17
  gpioSysfsPath = '/sys/class/gpio/gpio%s/' % photocellGPIO
  global valueFileName
  valueFileName = gpioSysfsPath + 'value'
  edgeFileName = gpioSysfsPath + 'edge'

# Check if the photocell GPIO has been configured:
  if not os.access(valueFileName, os.R_OK):
    print('%s: file does not exist or cannot be read. You must export the GPIO no %i as input first!' % (valueFileName, photocellGPIO))
    exit()
# Check if the interrupts are generated for photocell GPIO rising AND falling edge:
  with open(edgeFileName, 'r') as edgeFile:
    if (edgeFile.read()[:4] != "both"):
      print('%s: file does not exist, cannot be read or the interrupt on GPIO no %i is not set to "both". Check the system config.' % (edgeFileName, photocellGPIO))
      exit()


def output_setup():
# Setup the wiringPi MCP23017 chips for valve outputs:
  wiringpi.mcp23017Setup(65,0x20)
  wiringpi.mcp23017Setup(81,0x21)
  for pin in range(65,97):
    wiringpi.pinMode(pin,1)
# Assign wiringPi pin numbers on MCP23017s to the Monotype control codes.
  global wiringPiPinNumber
  wiringPiPinNumber = dict([('1', 65), ('2', 66), ('3', 67), ('4', 68), ('5', 69), ('6', 70), ('7', 71), ('8', 72), ('9', 73), ('10', 74), ('11', 75), ('12', 76), ('13', 77), ('14', 78), ('0005', 79), ('0075', 80), ('A', 81), ('B', 82), ('C', 83), ('D', 84), ('E', 85), ('F', 86), ('G', 87), ('H', 88), ('I', 89), ('J', 90), ('K', 91), ('L', 92), ('M', 93), ('N', 94), ('S', 95), ('O15', 96)])


# Set up comment symbols for parsing the ribbon files:
global commentSymbols
commentSymbols = ['**', '* ', '//']


def complete(text, state):
# This function enables tab key auto-completion when you enter the filename. Will definitely come in handy.
  return (glob.glob(text+'*')+[None])[state]
readline.set_completer_delims(' \t\n;')
readline.parse_and_bind('tab: complete')
readline.set_completer(complete)


global inputFileName
inputFileName = ""


def enter_filename():
# Enter the ribbon filename
  global inputFileName
  inputFileName = raw_input('\n Enter the ribbon file name: ')

def menu():
# Main menu. On entering, clear the screen and turn any valves off.
  os.system('clear')
  deactivate_valves()
  print('rpi2caster - CAT (Computer-Aided Typecasting) for Monotype Composition or Type and Rule casters.\n\nThis program reads a ribbon (input file) and casts the type on a Composition Caster, \nor punches a paper tape with a Monotype keyboard\'s paper tower.\n')
  ans = ''
  while ans == '':
    print ("""
		Main menu:

		1. Load a ribbon file

		2. Cast type from ribbon file

		3. Punch a paper tape

		4. Cast sorts

		5. Test the valves and pinblocks

		6. Lock the caster on a specified diecase position



		0. Exit to shell

		""")

    if inputFileName != '':
      print('Input file name: %s\n' % os.path.realpath(inputFileName))

    ans = raw_input('Choose an option: ')
    if ans=='1':
      enter_filename()
      menu()
    elif ans=='2':
      cast_composition(inputFileName)
    elif ans=='3':
      punch_composition(inputFileName)
    elif ans=='4':
      sorts_menu()
    elif ans=='5':
      line_test()
    elif ans=='6':
      lock_on_position()

    elif ans=='0':
      print('\nGoodbye! :)\n')
      exit()
    else:
      print('\nNo such option. Choose again.')
      ans = ''

def activate_valves(mode, signals):
# Activates the valves corresponding to Monotype signals found in an array fed to the function.
# The input array "signals" can contain lowercase (a, b, g, s...) or uppercase (A, B, G, S...) descriptions.
# In "punch" mode, an additional line (O+15) will be activated if less than two signals are to be sent.
  for monotypeSignal in signals:
    pin = wiringPiPinNumber[str.upper(monotypeSignal)]
    wiringpi.digitalWrite(pin,1)
    if mode == 'punch' and len(signals) < 2:
      wiringpi.digitalWrite(wiringPiPinNumber['O15'],1)

def deactivate_valves():
# Turn all valves off to avoid erroneous operation, esp. in case of program termination
  for pin in range(65,97):
    wiringpi.digitalWrite(pin,0)


def machine_stopped():
# This allows us to choose whether we want to continue, return to menu or exit if the machine stops during casting.
  choice = ""
  while choice is not 'c' and choice is not 'm' and choice is not 'e':
    choice = raw_input("Machine not running! Check what's going on.'\n(C)ontinue, return to (M)enu or (E)xit program.")
  else:
    if choice.lower() == 'c':
      return True
    elif choice.lower() == 'm':
      menu()
    elif choice.lower() == 'e':
      deactivate_valves()
      exit()


def cast_composition(filename):
# Composition casting routine.
# The input file is read backwards - last characters are cast first, after setting the justification
  with open(filename, 'rb') as ribbon:
    mode = 'cast'
    fileContents = reversed(list(csv.reader(ribbon, delimiter=';')))
    print('\nThe combinations of Monotype signals will be displayed on screen while the machine casts the type.\n')
    raw_input('\nInput file found. Press return to start casting.\n')
    code_reader(fileContents, mode)
  raw_input('\nCasting finished. Press return to go to main menu.')
  main()


def punch_composition(filename):
# Punching routine.
# When punching, the input file is read forwards.
# The "punch" mode means that an additional line (O15) is switched on for operating the paper tower.
  with open(filename, 'rb') as ribbon:
    mode = 'punch'
    fileContents = csv.reader(ribbon, delimiter=';')
    print('\nThe combinations of Monotype signals will be displayed on screen while the paper tower punches the ribbon.\n')
    raw_input('\nInput file found. Turn on the air, fit the tape on your paper tower and press return to start punching.\n')
    code_reader(fileContents, mode)
# After casting/punching is finished:
  raw_input('\nPunching finished. Press return to go to main menu.')
  main()


def code_reader(fileContents, mode):
# A function that works on ribbon file's contents (2-dimensional array) and casts/punches signals, row by row
  for row in fileContents:
# check if the row begins with a defined comment symbols - if so, print it but don't turn on the valves
    if ((''.join(row))[:2] in commentSymbols):
      print(' '.join(row)[2:])
    else:
        cast_row(row, mode, 5)


def line_test():
# Test all valves and composition caster's inputs to check if everything works and is properly connected
# Signals will be tested in order: 0005 - S - 0075, 1 towards 14, A towards N, O+15, NI, NL, MNH, MNK
  raw_input('This will check if the valves, pin blocks and 0005, S, 0075 mechanisms are working. Press return to continue...')
  for signal in [['0005'], ['S'], ['0075'], ['1'], ['2'], ['3'], ['4'], ['5'], ['6'], ['7'],
              ['8'], ['9'], ['10'], ['11'], ['12'], ['13'], ['14'], ['A'], ['B'], ['C'], ['D'],
              ['E'], ['F'], ['G'], ['H'], ['I'], ['J'], ['K'], ['L'], ['M'], ['N'], ['O15'],
              ['N', 'I'], ['N', 'L'], ['M', 'N', 'H'], ['M', 'N', 'K']]:
    cast_row(signal, 'cast', 60)
  raw_input('\nTesting done. Press return to go to main menu.')
  main()


def sorts_menu():
# Sorts casting routine, based on the position in diecase.
# Ask user about the diecase row & column, as well as number of sorts
  os.system('clear')
  print('Calibration and Sort Casting:\n\n')
  column = raw_input('Enter column symbol (default: G) ').upper()
  row = raw_input('Enter row number (default: 5) ')
  n = raw_input('How many sorts do you want to cast? (default: 10) ')
  if not row.isdigit() or int(row) > 16 or int(row) < 1:
    print('Wrong row number. Defaulting to 5.')
    row = '5'
  if not column.isalpha():
    print('Wrong column symbol. Defaulting to G.')
    column = 'G'
  if not n.isdigit() or int(n) <= 0:
    print('Incorrect number of sorts. Defaulting to 10.')
    n = '10'
  n = int(n)
  choice = ''
  os.system('clear')
  while choice is not 'c' and choice is not 'r' and choice is not 'm' and choice is not 'e':
    choice = raw_input('\nWe\'ll cast %s%s, %s times.\n(C)ontinue, (R)epeat, go back to (M)enu or (E)xit program?' % (column, row, n))
  else:
    if choice.lower() == 'c':
      cast_sorts(column, row, n)
    elif choice.lower() == 'r':
      sorts_menu()
    elif choice.lower() == 'm':
      menu()
    elif choice.lower() == 'e':
      deactivate_valves()
      exit()

def lock_on_position():
# This function allows us to give the program a specific combination of Monotype codes,
# and will keep the valves on until we press return (useful for calibration).
  signals = ''
  columns = []
  rows = []
  special_signals = []
# Let the user enter a combo:
  while signals == '':
    signals = raw_input('Enter the signals to send to the machine: ').upper()
# Strip non-alphanumeric characters, like !, +, ; or spacebar
  for char in signals:
    if not char.isalnum():
      signals = signals.replace(char, '')
# Detect special signals: 0005, 0075, S
  for special in ['0005', '0075', 'S']:
    if signals.find(special) != -1:
      special_signals.append(special)
    signals = signals.replace(special, '')
# Look for any numbers between 14 and 100, strip them
  for n in range(100, 14, -1):
    signals = signals.replace(str(n), '')
# Determine row numbers
  for n in range(15, 0, -1):
    pos = signals.find(str(n))
    if pos > -1:
      rows.append(str(n))
    signals = signals.replace(str(n), '')
# Determine columns A...N, strip any other letters (S was taken care of earlier)
# List comprehensions return generator objects, so we must convert that to list.
  columns = list(char for char in signals if char in list('ABCDEFGHIJKLMN'))
# Now we can splice all the signal lists into one, then feed them to activate_valves
  signals = columns + rows + special_signals
# Display columns, rows and special signals
  print ' '.join(signals)
  activate_valves('cast', signals)
# Wait until user decides to stop sending those signals to valves:
  raw_input('Press return to stop and go back to main menu')
  deactivate_valves()
  main()

def cast_sorts(column, row, n):
# Cast the sorts; turn on the pump first
  print('Starting the pump...')
  cast_row(['0075'], 'cast', 5)
  print('Casting characters...')
# Generate n combinations of row & column, then cast them one by one
  codes = [[column, row]] * n
  code_reader(codes, 'cast')
# After casting sorts we need to stop the pump
  print('Stopping pump and putting line to the galley...')
  cast_row(['0005', '0075'], 'cast', 5)

# Ask what to do after casting
  finishedChoice = ''
  while finishedChoice == '':
    finishedChoice = raw_input('Finished!\n(R)epeat, go back to (M)enu or (E)xit program?')
    if finishedChoice.lower() == 'r':
      sorts_menu()
    elif finishedChoice.lower() == 'm':
      menu()
    elif finishedChoice.lower() == 'e':
      deactivate_valves()
      exit()
    else:
      print('\nNo such option. Choose again.')
      finishedChoice = ''

def cast_row(signals, mode, machineTimeout):
# Detect events on a photocell input and cast all signals in a row.
# Ask the user what to do if the machine is stopped (no events).
  if mode == 'punch':
# Punching - the pace is arbitrary, let's set it to 200ms/200ms
# print signals to console, so that we know what we cast or test
    print(str.upper(' '.join(signals)))
    activate_valves(mode, signals)
    time.sleep(0.2)
    deactivate_valves()
    time.sleep(0.2)
  else:
# Casting - the pace is dictated by the machine (via photocell)
    with open(valueFileName, 'r') as gpiostate:
      po = select.epoll()
      po.register(gpiostate, select.POLLPRI)
      previousState = 0
      while 1:
        events = po.poll(machineTimeout)
        if events:
# machine is working
          gpiostate.seek(0)
          photocellState = int(gpiostate.read())
          if photocellState == 1:
# print signals to console, so that we know what we cast or test
            print(str.upper(' '.join(signals)))
            activate_valves(mode, signals)
            previousState = 1
          elif photocellState == 0 and previousState == 1:
            deactivate_valves()
            previousState = 0
            break
        else:
# if machine isn't working, the photocell status is not changing
          machine_stopped()



def main():
# Main loop definition. All exceptions should be caught here. Also, ensure cleaning up after exit.
  try:
    menu()
  except (IOError, NameError):
    raw_input("\nInput file not chosen or wrong input file name. Press return to go to main menu.\n")
    main()
  except KeyboardInterrupt:
    print("Terminated by user.")
    exit()
  finally:
    deactivate_valves()

# Do the main loop.
input_setup()
output_setup()
main()