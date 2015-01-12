#!/usr/bin/python

""" Monotype composition caster & keyboard paper tower control program.
The program reads a "ribbon" file, then waits for the user to start
casting or punching the paper tape. In the casting mode, during each
machine cycle, the photocell is lit (high state) or obscured (low).
When high, the program reads a line from ribbon and turns on
the solenoid valves respective to the Monotype control codes.
After the photocell is lit (low state on input), the valves are
turned off and the program moves on to the next line."""

import sys, os, time, string, readline, glob, select
try:
  import wiringpi2 as wiringpi
except ImportError:
  print('wiringPi2 not installed! It\'s OK for testing, but you MUST install it if you want to cast!')
  time.sleep(1)
finally:
  pass
try:
  import sqlite3
except ImportError:
    print('You must install sqlite3 database and python-sqlite2 package.')
    exit()
finally:
  pass

global DebugMode
DebugMode = False

class Hardware(object):
  """A class which stores all methods related to the interface and
  caster itself"""

  def __init__(self, photocellGPIO, mcp0Address, mcp1Address, pinBase):

    self.photocellGPIO = photocellGPIO
    self.mcp0Address = mcp0Address
    self.mcp1Address = mcp1Address
    self.pinBase = pinBase

    self.setup()


  def setup(self):
    """Input configuration:
    We need to set up the sysfs interface before (powerbuttond.py -
    a daemon running on boot with root privileges takes care of it).
    In the future,  we'll add configurable GPIO numbers. Why store the
    device config in the program source, if we can use a .conf file?"""
    gpioSysfsPath = '/sys/class/gpio/gpio%s/' % self.photocellGPIO
    self.valueFileName = gpioSysfsPath + 'value'
    self.edgeFileName = gpioSysfsPath + 'edge'

    """Check if the photocell GPIO has been configured:"""
    if not os.access(self.valueFileName, os.R_OK):
      print('%s: file does not exist or cannot be read. '
         'You must export the GPIO no %i as input first!'
              % (self.valueFileName, self.photocellGPIO))
      exit()

    """Check if the interrupts are generated for photocell GPIO
    for both rising and falling edge:"""
    with open(self.edgeFileName, 'r') as edgeFile:
      if (edgeFile.read()[:4] != 'both'):
        print('%s: file does not exist, cannot be read or the interrupt '
        'on GPIO no %i is not set to "both". Check the system config.'
        % (self.edgeFileName, self.photocellGPIO))
        exit()

    """Output configuration:
    Setup the wiringPi MCP23017 chips for valve outputs:"""
    wiringpi.mcp23017Setup(self.pinBase, self.mcp0Address)
    wiringpi.mcp23017Setup(self.pinBase + 16, self.mcp1Address)
    pins = range(self.pinBase, self.pinBase + 32)
    signals = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11',
             '12', '13', '14', '0005', '0075', 'A', 'B', 'C', 'D', 'E',
             'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'S', 'O15']

    """Set all I/O lines as outputs - mode 1"""
    for pin in pins:
      wiringpi.pinMode(pin,1)

    """Assign wiringPi pin numbers on MCP23017s to the Monotype control codes."""
    self.wiringPiPinNumber = dict(zip(signals, pins))

  def detect_rotation(self):
    """Detects if the machine is rotating"""
    """count machine cycles, initial 0, target 3"""
    cycles = 0
    cycles_max = 3
    """let's give it 30 seconds timeout"""
    time_start = time.time()
    time_max = 30
    """check for photocell signals until timeout or target is reached"""
    with open(self.valueFileName, 'r') as gpiostate:
      while time.time() <= time_start + time_max and cycles <= cycles_max:
        photocellSignals = select.epoll()
        photocellSignals.register(gpiostate, select.POLLPRI)
        events = photocellSignals.poll(0.5)
        if events:
          gpiostate.seek(0)
          photocellState = int(gpiostate.read())
          previousState = 0
          if photocellState == 1 and previousState == 0:
            previousState = 1
            cycles += 1
          elif photocellState == 0 and previousState == 1:
            previousState = 0
      else:
        if cycles > cycles_max:
          print('\nOkay, the machine is running...\n')
          return True
        else:
          self.machine_stopped()
          self.detect_rotation()
          return False

  def send_signals_to_caster(self, signals, machineTimeout):
    """Casting - the pace is dictated by the machine (via photocell)."""
    with open(self.valueFileName, 'r') as gpiostate:
      po = select.epoll()
      po.register(gpiostate, select.POLLPRI)
      previousState = 0

      """Detect events on a photocell input and cast all signals in a row.
      Ask the user what to do if the machine is stopped (no events)."""
      while True:
        """polling for interrupts"""
        events = po.poll(machineTimeout)
        if events:
          """be sure that the machine is working"""
          gpiostate.seek(0)
          photocellState = int(gpiostate.read())

          if photocellState == 1:
            """there's a signal from photocell - let the air in"""
            self.activate_valves(signals)
            previousState = 1

          elif photocellState == 0 and previousState == 1:
            """state changes from 1 to 0 - end of air in phase"""
            self.deactivate_valves()
            previousState = 0
            break

        else:
          """if machine isn't working, notify the user"""
          self.machine_stopped()


  def activate_valves(self, signals):
    """ Activates the valves corresponding to Monotype signals found
    in an array fed to the function. The input array "signals" can contain
    lowercase (a, b, g, s...) or uppercase (A, B, G, S...) descriptions.
    Do nothing if the function receives an empty sequence."""
    if len(signals) != 0:
      for monotypeSignal in signals:
        pin = self.wiringPiPinNumber[monotypeSignal]
        wiringpi.digitalWrite(pin,1)


  def deactivate_valves(self):
    """Turn all valves off to avoid erroneous operation,
    esp. in case of program termination."""
    for pin in range(self.pinBase, self.pinBase + 32):
      wiringpi.digitalWrite(pin,0)


  def machine_stopped(self):
    """This allows us to choose whether we want to continue, return to menu
    or exit if the machine stops during casting."""
    choice = ""
    while choice not in ['c', 'm', 'e']:
      choice = raw_input('Machine not running! Check what\'s going on.'
                   '\n(C)ontinue, return to (M)enu or (E)xit program.')
    else:
      if choice.lower() == 'c':
        return True
      elif choice.lower() == 'm':
        self.menu()
      elif choice.lower() == 'e':
        self.deactivate_valves()
        exit()



class DryRun(object):
  """A class which allows to test rpi2caster without an actual interface"""

  def __init__(self):
    print 'Testing rpi2caster without an actual caster or interface. Debug mode ON.'
    time.sleep(1)

  def send_signals_to_caster(self, signals, machineTimeout):
    """Just send signals, as we don't have a photocell"""
    raw_input('Sensor ON - press [ENTER]')
    self.activate_valves(signals)
    raw_input('Sensor OFF - press [ENTER]')
    self.deactivate_valves()


  def activate_valves(self, signals):
    """If there are any signals, print them out"""
    if len(signals) != 0:
      print 'The valves: ',' '.join(signals),' would be activated now.'

  def deactivate_valves(self):
    """No need to do anything"""
    print 'The valves would be deactivated now.'

  def detect_rotation(self):
    print 'Now, the program would check if the machine is rotating.\n'
    startTime = time.time()
    while time.time() < startTime + 5:
      answer = raw_input('Press return (to simulate rotation) '
                    'or wait 5sec (to simulate machine off)\n')
    else:
      if answer is None:
        self.machine_stopped()
        self.detect_rotation()

  def machine_stopped(self):
    """This allows us to choose whether we want to continue, return to menu
    or exit if the machine stops during casting. It's just a simulation here."""
    choice = ""
    while choice not in ['c', 'm', 'e']:
      choice = raw_input('Machine not running! Check what\'s going on.'
                   '\n(C)ontinue, return to (M)enu or (E)xit program.')
    else:
      if choice.lower() == 'c':
        return True
      elif choice.lower() == 'm':
        self.menu()
      elif choice.lower() == 'e':
        self.deactivate_valves()
        exit()



class Parsing(object):
  """This class contains file- and line-parsing methods"""


  def signals_parser(self, originalSignals):
    """Parses an input string, passes only A-N, 1-14, 0005, S, 0075.
    Prints any comments to screen."""

    """We need to work on strings. Convert any lists, integers etc."""
    signals = str(originalSignals)

    """This is a comment parser. It looks for any comment symbols defined
    here - e.g. **, *, ##, #, // etc. - and prints the comment to screen.
    If it's an inline comment (placed after combination), we cast this
    combination. If a line in file contains a comment only, we cast nothing.
    So, we need an empty line if we want to cast O15 (place the comment above)."""
    commentSymbols = ['**', '*', '//', '##', '#']
    comment = ''
    for symbol in commentSymbols:
      symbolPosition = signals.find(symbol)
      if symbolPosition != -1:
        comment = signals[symbolPosition + len(symbol):].strip()
        signals = signals[:symbolPosition].strip()

    """Filter out all non-alphanumeric characters and whitespace"""
    signals = filter(str.isalnum, signals).upper()

    """Codes for columns, rows and special signals will be stored
    separately and sorted on output"""
    columns = []
    rows = []
    special_signals = []

    """First, detect special signals: 0005, 0075, S"""
    for special in ['0005', '0075', 'S']:
      if signals.find(special) != -1:
        special_signals.append(special)
        signals = signals.replace(special, '')

    """Look for any numbers between 14 and 100, strip them"""
    for n in range(100, 14, -1):
      signals = signals.replace(str(n), '')

    """From remaining numbers, determine row numbers"""
    for n in range(15, 0, -1):
      pos = signals.find(str(n))
      if pos > -1:
        rows.append(str(n))
      signals = signals.replace(str(n), '')

    """Treat signals as a list and filter it, dump all letters beyond N
    (S was taken care of earlier). That will be the column signals."""
    columns = filter(lambda s: s in list('ABCDEFGHIJKLMN'), list(signals))

    """Make sure no signal appears more than once, and sort them"""
    columns = sorted(set(columns))

    """Return a list containing the signals, as well as a comment."""
    return [columns + rows + special_signals, comment]


class CasterConfig(object):
  """Read/write caster & interface configuration from/to sqlite3 database"""


  def add_caster(self, serialNumber, machineName, machineType,
                            justification, diecaseFormat, interfaceID):
    """Register a new caster"""
    with sqlite3.connect('database/monotype.db') as db:
      cursor = db.cursor()
      """Make sure that the table exists, if not - create it"""
      cursor.execute('CREATE TABLE IF NOT EXISTS machine_settings \
      (serial_number integer primary key, machine_name text, machine_type text, \
      justification text, diecase_format text, interface_id integer)')

      """Create an entry for the caster in the database"""
      cursor.execute('INSERT INTO machine_settings (serial_number,machine_name,\
      machine_type,justification,diecase_format) VALUES (%i, %s, %s, %s, %s)'
      % serialNumber, machineName, machineType, justification, diecaseFormat, interfaceID)
      db.commit()

  def list_casters(self):
    """List all casters stored in database"""
    print('\nSerial No, name, type, justification, diecase format, interface ID\n')
    with sqlite3.connect('database/monotype.db') as db:
      cursor = db.cursor()
      cursor.execute('SELECT * FROM machine_settings')
      while True:
        caster = cursor.fetchone()
        if caster is not None:
          print '   '.join(caster)
        else:
          break

  def caster_by_name(self, machineName):
    """Get caster parameters for a caster with a given name"""
    with sqlite3.connect('database/monotype.db') as db:
      cursor = db.cursor()
      cursor.execute('SELECT * FROM machine_settings WHERE caster_name = %s' % machineName)
      caster = cursor.fetchone()
      """returns a list: [machineSerial, machineName, machineType, justification, diecaseFormat]"""
      return caster

  def caster_by_serial(self, machineSerial):
    """Get caster parameters for a caster with a given serial No"""
    with sqlite3.connect('database/monotype.db') as db:
      cursor = db.cursor()
      cursor.execute('SELECT * FROM machine_settings WHERE caster_serial = %s' % machineSerial)
      caster = cursor.fetchone()
      """returns a list: [machineSerial, machineName, machineType, justification, diecaseFormat]"""
      return caster


  def add_interface(self, interfaceID, interfaceName, emergencyGPIO,
                            photocellGPIO, mcp0Address, mcp1Address, pinBase):
    """Register a new interface, i.e. I2C expander params + emergency stop GPIO + photocell GPIO"""
    with sqlite3.connect('database/monotype.db') as db:
      cursor = db.cursor()
      cursor.execute('CREATE TABLE IF NOT EXISTS interface_settings \
      (interface_id integer primary key, interface_name text, emergency_gpio integer, \
      photocell_gpio integer, mcp0_address blob, \
      mcp1_address blob, pin_base integer)')
      cursor.execute('INSERT INTO interface_settings \
      (interface_id,interface_name,emergency_gpio,photocell_gpio,mcp0_address,\
      mcp1_address,pin_base) VALUES (%i, %s, %i, %i, %i, %i, %i)' % interfaceID,
      interfaceName, emergencyGPIO, photocellGPIO, mcp0Address, mcp1Address, pinBase)
      db.commit()

  def get_interface(self, interfaceID=0):
    """Get interface parameters for a given ID, most typically 0 for a RPi with a single interface"""
    with sqlite3.connect('database/monotype.db') as db:
      cursor = db.cursor()
      cursor.execute('SELECT * FROM interface_settings WHERE interface_id = %i' % interfaceID)
      interface = cursor.fetchone()
      """returns a list: [interfaceID, interfaceName, emergencyGPIO, photocellGPIO,
      mcp0Address, mcp1Address, pinBase] """
      return interface

  def list_interfaces(self):
    """List all casters stored in database"""
    print('\nID, name, emergency GPIO, photocell GPIO, MCP0 addr, MCP1 addr, pin base:\n')
    with sqlite3.connect('database/monotype.db') as db:
      cursor = db.cursor()
      cursor.execute('SELECT * FROM interface_settings')
      while True:
        caster = cursor.fetchone()
        if interface is not None:
          print '   '.join(interface)
        else:
          break



class Actions(Parsing):
  """Actions the user can do in this software"""


  def cast_composition(self, filename):
    """ Composition casting routine. The input file is read backwards -
    last characters are cast first, after setting the justification."""

    """Open a file with signals"""
    with open(filename, 'rb') as ribbon:
      contents = ribbon.readlines()


    """For casting, we need to read the file backwards"""
    contents = reversed(contents)

    """Wait until the operator confirms"""
    print('\nThe combinations of Monotype signals will be displayed '
    'on screen while the machine casts the type.\nTurn on the machine '
    'and the program will start automatically.\n')
    #raw_input('\nInput file found. Press return to start casting.\n')
    self.detect_rotation()
    for line in contents:

      """Parse the row, return a list of signals and a comment.
      Both can have zero or positive length."""
      signals, comment = self.signals_parser(line)

      """Print a comment if there is one (positive length)"""
      if len(comment) > 0:
        print comment

      """Cast an empty line, signals with comment, signals with no comment.
      Don't cast a line with comment alone."""
      if len(comment) == 0 or len(signals) > 0:
        if len(signals) > 0:
          print ' '.join(signals)
        else:
          print('O+15 - no signals')
        self.send_signals_to_caster(signals, 5)

    """After punching is finished, notify the user:"""
    raw_input('\nCasting finished. Press return to go to main menu. ')
    self.menu()


  def punch_composition(self, filename):
    """Punching routine.
    When punching, the input file is read forwards. An additional line
    (O+15) is switched on for operating the paper tower, if less than two
    signals are found in a sequence."""

    """Open a file with signals"""
    with open(filename, 'rb') as ribbon:

      """Wait until the operator confirms"""
      print('\nThe combinations of Monotype signals will be displayed '
                'on screen while the paper tower punches the ribbon.\n')
      raw_input('\nInput file found. Turn on the air, fit the tape '
             'on your paper tower and press return to start punching.\n')
      for line in ribbon:

        """Parse the row, return a list of signals and a comment.
        Both can have zero or positive length."""
        signals, comment = self.signals_parser(line)

        """Print a comment if there is one - positive length"""
        if len(comment) > 0:
          print comment

        """Punch an empty line, signals with comment, signals with no comment.
        Don't punch a line with comment alone (prevents erroneous O+15's)."""
        if len(comment) == 0 or len(signals) > 0:

          """Determine if we need to turn O+15 on"""
          if len(signals) < 2:
            signals += ('O15',)
          print ' '.join(signals)
          self.activate_valves(signals)

          """The pace is arbitrary, let's set it to 200ms/200ms"""
          time.sleep(0.2)
          self.deactivate_valves()
          time.sleep(0.2)

    """After punching is finished, notify the user:"""
    raw_input('\nPunching finished. Press return to go to main menu. ')
    self.menu()


  def line_test(self):
    """Test all valves and composition caster's inputs to check
    if everything works and is properly connected. Signals will be tested
    in order: 0005 - S - 0075, 1 towards 14, A towards N, O+15, NI, NL,
    MNH, MNK (feel free to add other important combinations!)"""
    raw_input('This will check if the valves, pin blocks and 0005, S, '
             '0075 mechanisms are working. Press return to continue... ')
    for combination in [['0005'], ['S'], ['0075'], ['1'], ['2'], ['3'], ['4'],
                ['5'], ['6'], ['7'], ['8'], ['9'], ['10'], ['11'], ['12'],
                ['13'], ['14'], ['A'], ['B'], ['C'], ['D'], ['E'], ['F'],
                ['G'], ['H'], ['I'], ['J'], ['K'], ['L'], ['M'], ['N'], ['O15'],
                ['N', 'I'], ['N', 'L'], ['M', 'N', 'H'], ['M', 'N', 'K']]:
      print ' '.join(combination)
      self.send_signals_to_caster(combination, 60)
    raw_input('\nTesting done. Press return to go to main menu. ')
    self.menu()


  def cast_sorts(self):
    """Sorts casting routine, based on the position in diecase.
    Ask user about the diecase row & column, as well as number of sorts."""
    os.system('clear')
    print('Calibration and Sort Casting:\n\n')
    signals = raw_input('Enter column and row symbols (default: G 5, spacebar if O-15) ')
    print('\n')
    if signals == '':
      signals = 'G5'

    parsedSignals, comment = self.signals_parser(signals)

    """O15 yields no signals, but we may want to cast it - check if we
    entered spacebar"""
    if len(parsedSignals) == 0 and signals != ' ':
      print('\nRe-enter the sequence')
      time.sleep(1)
      self.cast_sorts()
    n = raw_input('\nHow many sorts do you want to cast? (default: 10) ')
    print('\n')

    """Default to 10 if user enters non-positive number or letters"""
    if not n.isdigit() or int(n) < 0:
      n = '10'
    n = int(n)

    """Warn if we want to cast too many sorts from a single matrix"""
    print ('\nWe\'ll cast it %i times.\n' % (n))
    if n > 30:
      print('\nWarning: you want to cast a single character more than '
                    '30 times. This may lead to matrix overheating!\n')

    """Ask user if the entered parameters are correct"""
    choice = ''
    while choice not in ['c', 'r', 'm', 'e']:
      choice = raw_input('(C)ontinue, (R)epeat, go back to (M)enu or (E)xit program? ')
    else:
      if choice.lower() == 'c':
        """Check if the machine is running"""
        print('Start the machine...')
        self.detect_rotation()
        """Cast the sorts: turn on the pump first."""
        print('Starting the pump...')
        self.send_signals_to_caster(['N', 'K', '0075'], 5)
        print('Casting characters...')
        """Cast n combinations of row & column, one by one"""
        for i in range(n):
          if len(parsedSignals) > 0:
            print ' '.join(parsedSignals)
          else:
            print('O+15 - no signals')
          self.send_signals_to_caster(parsedSignals, 5)
        """After casting sorts we need to stop the pump"""
        print('Stopping the pump and putting line to the galley...')
        self.send_signals_to_caster(['0005', '0075'], 5)
      elif choice.lower() == 'r':
        self.cast_sorts()
      elif choice.lower() == 'm':
        self.menu()
      elif choice.lower() == 'e':
        self.deactivate_valves()
        exit()

    """Ask what to do after casting"""
    print('\nFinished!')
    finishedChoice = ''
    while finishedChoice not in ['r', 'm', 'e']:
      finishedChoice = raw_input('(R)epeat, go back to (M)enu or (E)xit program? ')
      if finishedChoice.lower() == 'r':
        self.cast_sorts()
      elif finishedChoice.lower() == 'm':
        self.menu()
      elif finishedChoice.lower() == 'e':
        self.deactivate_valves()
        exit()
      else:
        print('\nNo such option. Choose again.')
        finishedChoice = ''


  def lock_on_position(self):
    """This function allows us to give the program a specific combination
    of Monotype codes, and will keep the valves on until we press return
    (useful for calibration). It also checks the signals' validity"""

    """Let the user enter a combo:"""
    signals = ''
    while signals == '':
      signals = raw_input('Enter the signals to send to the machine: ')
    combination = self.signals_parser(signals)[0]
    if len(combination) > 0:
      print ' '.join(combination)
    self.activate_valves(combination)

    """Wait until user decides to stop sending those signals to valves:"""
    raw_input('Press return to stop and go back to main menu. ')
    self.deactivate_valves()
    self.menu()



class TextUI(object):
  """This class defines a text user interface, i.e. what you can do
  when operating the program from console."""


  def consoleUI(self):
    """Main loop definition. All exceptions should be caught here.
    Also, ensure cleaning up after exit."""
    try:
      self.menu()
    except (IOError, NameError):
      if DebugMode == True:
        print('Debug mode: see what happened.')
        raise
      else:
        raw_input('\nInput file not chosen or wrong input file name. '
                              'Press return to go to main menu.\n')
        self.menu()
    except KeyboardInterrupt:
      print('\nTerminated by user.')
      exit()
    finally:
      print('Goodbye!')
      self.deactivate_valves()


  def tab_complete(text, state):
    """This function enables tab key auto-completion when you
    enter the filename. Will definitely come in handy."""
    return (glob.glob(text+'*')+[None])[state]

  readline.set_completer_delims(' \t\n;')
  readline.parse_and_bind('tab: complete')
  readline.set_completer(tab_complete)

  """Set up an empty ribbon file name first"""
  inputFileName = ''


  def enter_filename(self):
    """Enter the ribbon filename"""
    self.inputFileName = raw_input('\n Enter the ribbon file name: ')


  def menu(self):
    """Main menu. On entering, clear the screen and turn any valves off."""
    os.system('clear')
    self.deactivate_valves()
    print('rpi2caster - CAT (Computer-Aided Typecasting) for Monotype '
    'Composition or Type and Rule casters.\n\nThis program reads '
    'a ribbon (input file) and casts the type on a Composition Caster, '
    '\nor punches a paper tape with a Monotype keyboard\'s paper tower.\n')
    if DebugMode:
      print('\nThe program is now in debugging mode!\n')
    ans = ''
    while ans == '':
      print ("""
  \t Main menu:

  \t 1. Load a ribbon file

  \t 2. Cast type from ribbon file

  \t 3. Punch a paper tape

  \t 4. Cast sorts

  \t 5. Test the valves and pinblocks

  \t 6. Lock the caster on a specified diecase position



  \t 0. Exit to shell

  """)

      if self.inputFileName != '':
        print('Input file name: %s\n' % os.path.realpath(self.inputFileName))

      ans = raw_input('Choose an option: ')
      if ans=='1':
        self.enter_filename()
        self.menu()
      elif ans=='2':
        self.cast_composition(self.inputFileName)
      elif ans=='3':
        self.punch_composition(self.inputFileName)
      elif ans=='4':
        self.cast_sorts()
      elif ans=='5':
        self.line_test()
      elif ans=='6':
        self.lock_on_position()

      elif ans=='0':
        exit()
      else:
        print('\nNo such option. Choose again.')
        ans = ''


class Console(Hardware, Actions, TextUI):
  """Use this class for instantiating text-based console user interface"""

  def __init__(self, photocellGPIO=17, mcp0Address=0x20, mcp1Address=0x21, pinBase=65):
    Hardware.__init__(self, photocellGPIO, mcp0Address, mcp1Address, pinBase)

    self.consoleUI()

class Testing(DryRun, Actions, TextUI):
  """A class for testing the program without an actual caster/interface"""
  def __init__(self):
    global DebugMode
    DebugMode = True
    DryRun.__init__(self)
    self.consoleUI()

class WebInterface(Hardware, Actions):
  """Use this class for instantiating text-based console user interface"""

  def __init__(self, photocellGPIO=17, mcp0Address=0x20, mcp1Address=0x21, pinBase=65):
    Hardware.__init__(self, photocellGPIO, mcp0Address, mcp1Address, pinBase)

    self.webUI()

  def webUI(self):
    """This is a placeholder for web interface method. Nothing yet..."""