#!/usr/bin/python
import os
import sys
import json
from rpi2caster import Database

try:
  import sqlite3
except ImportError:
    print('You must install sqlite3 database and python-sqlite2 package.')
    exit()
finally:
  pass


global DebugMode
DebugMode = False


def is_hex(s):
  try:
    int(s, 16)
    return True
  except (TypeError, ValueError):
    return False

def conv_hex(s):
  n = int(s, 16)
  return n

def choice(message, options):
  """A simple menu where user is asked what to do.
  Wrong choice points to the menu.

  Message: string displayed on screen;
  options: a list or tuple of strings - options.
  """
  ans = ''
  while ans not in options:
    ans = raw_input(message)
  return ans

def menu(self, **kwargs):
  """menu(header, footer, options, recursive):

  A menu which takes three arguments:
  header - string to be displayed above,
  footer - string to be displayed below.,
  options - a list of n lists of 3 options (n x 3 matrix), where:
            [key, displayed_option_name, command]
  recursive - determines whether the menu will call itself after
              a command called by choice is executed.

  After choice is made, executes the command.
  """

  """Declare an empty var for your choice (needed by "while" loop).
  Create an empty list of choices and commands;
  these will be filled later on.
  """
  header = kwargs['header']
  footer = kwargs['footer']
  options = kwargs['options']
  try:
    recursive = kwargs['recursive']
  except KeyError:
    recursive = False


  yourChoice = ''
  choices = []
  commands = []

  """Clear the screen, display header and add two empty lines:"""
  os.system('clear')
  print header
  print('')

  """Display all the options; construct the possible choices list:"""
  for option in options:
    if option:
      print('\t')

      """Convert the choice and displayed name to string,
      making it possible to use integers when calling the funtion:
      """
      choice = str(option[0])
      displayedName = str(option[1])
      command = str(option[2])

      print choice, ' :  ', displayedName
      choices.append(choice)

      if command is not None:
        commands.append(command)
      else:
        commands.append('')
    else:
      """Empty option - useful if we want to add an empty line"""
      print option
  if footer:
    print('')
    print footer
  print('\n')

  optionsMenu = dict(zip(choices, commands))

  while yourChoice not in choices:
    yourChoice = raw_input('Your choice: ')
  else:
    try:
      exec optionsMenu[yourChoice]
    except NameError:
      print('Something went wrong!')
      """Raise the exception in debug mode:"""
      if DebugMode:
        raise
  if recursive:
    """Go back to this menu after the command is done:"""
    raw_input('\nPress Enter to go back to menu...')
    menu(self, **kwargs)


class MonotypeSetup(object):

  def __init__(self, database):
    """Connect to a specified database:"""
    self.database = database

  def __enter__(self):
    return self


  def add_caster(
                 self, casterSerial='', casterName='', casterType='',
                 unitAdding='', diecaseSystem='', interfaceID=''
                ):
    """add_caster(casterSerial, casterName, casterType,
                  unitAdding, diecaseSystem, interfaceID):

    Adds a caster. The function will pass at least twice -
    until all data is entered correctly.

    It can be called with or without parameters:

    casterSerial - int - serial number of a caster,
    casterName - string - a user-friendly name to identify a caster,
    casterType - string - 'comp' (composition caster),
                          'large_comp' (large comp. / type&rule caster),
    unitAdding - boolean - whether the caster has an unit adding
                           attachment present and turned on, or off
    diecaseSystem - string - diecase (matrix case) system the caster uses:
                           'norm15' - 15x15 only,
                           'norm17' - 15x17 NI, NL
                           'hmn' - 16x17 HMN,
                           'kmn' - 16x17 KMN,
                           'shift' - 16x17 unit-shift.
    interfaceID - int - ID of a Raspberry-Monotype interface this caster
                           is connected to. Usually 0, but in certain cases
                           you may want to add another interface to your
                           Raspberry if you want to use multiple casters
                           without detaching and attaching the valveblock.
    """

    """Reset revalidation; if everything is OK, the data can be written
    to the database. Else, the add_caster function will recurse into itself
    with entered data as arguments. The user will have to re-enter
    any parameter which does not match the expected values or type."""
    revalidate = False

    """Check if the serial No is numeric - we must ensure
    that the value in db is integer"""
    if str(casterSerial).isdigit():
      casterSerial = int(casterSerial)
    else:
      casterSerial = raw_input(
                               'Enter the serial number of your caster: '
                              )
      revalidate = True

    """Enter a string for machine name"""
    if not casterName:
      casterName = raw_input(
                             'Enter the name you use for this machine: '
                            )
      revalidate = True

    """Choose the machine type - and validate the choice.
    Case insensitive; value stored in db as uppercase"""
    while casterType not in ['comp', 'large_comp']:
      casterType = raw_input(
                             'What type is the machine? '
                             '1 = composition caster, '
                             '2 = type & rule caster / '
                             'large composition caster: '
                            )
      if casterType == '1':
        casterType = 'comp'
      elif casterType == '2':
        casterType = 'large_comp'
      else:
        casterType = ''
      revalidate = True

    """Choose if the machine has unit adding or not"""
    while unitAdding not in (True, False):
      unitAdding = raw_input(
                             'Does the caster use unit adding attachment? '
                             '1 - yes, 0 - no: '
                            )
      if unitAdding == '0':
        unitAdding = False
      elif unitAdding == '1':
        unitAdding = True
      else:
        unitAdding = ''
      revalidate = True

    """Choose the diecase format the machine is using,
    and validate the choice"""
    dcsystems = ['norm15', 'norm17', 'hmn', 'kmn', 'shift']
    while diecaseSystem not in dcsystems:
      diecaseSystem = raw_input(
                      'Diecase format this machine works with: '
                      '0 for 15x15, 1 for 15x17, 2 for HMN, 3 for KMN, '
                      '4 for unit-shift: ')
      if diecaseSystem == '0':
        diecaseSystem = dcsystems[0]
      elif diecaseSystem == '1':
        diecaseSystem = dcsystems[1]
      elif diecaseSystem == '2':
        diecaseSystem = dcsystems[2]
      elif diecaseSystem == '3':
        diecaseSystem = dcsystems[3]
      elif diecaseSystem == '4':
        diecaseSystem = dcsystems[4]
      else:
        diecaseSystem = dcsystems[1]
      revalidate = True

    """Choose the interface ID"""
    if str(interfaceID).isdigit() and int(interfaceID) in range(4):
      interfaceID = int(interfaceID)
    else:
      interfaceID = raw_input(
                              'Raspberry interface number '
                              'for this machine. '
                              'Can be 0, 1, 2, 3. Default is 0: '
                             )
      if interfaceID == '':
        interfaceID = '0'
      revalidate = True

    """Now we can list entered data and ask for user's confirmation:"""
    if not revalidate:
      print('Caster serial number: %i \n' % casterSerial)
      print('Caster name: %s \n' % casterName)
      print('Caster type: %s \n' % casterType)
      print('Unit adding: %s \n' % str(unitAdding))
      print('Diecase system: %s \n' % diecaseSystem)
      print('Interface ID for this caster: %i \n' % interfaceID)

      ans = choice('\nCommit? '
                        '[y] - yes, save caster to database, '
                        '[n] - no, enter values again, '
                        'or [m] to return to main menu.',
                        ['y', 'n', 'm']
                       )
      if ans.lower() == 'y':
        if database.add_caster(casterSerial, casterName,
                             casterType, unitAdding,
                             diecaseSystem, interfaceID):
          print('Caster added successfully.')
        else:
          print('Failed to add caster!')
      elif ans.lower() == 'n':
        raw_input('Enter parameters again from scratch... ')
        self.add_caster()
      elif ans.lower() == 'm':
        pass

    else:
      """Recursively call this function to revalidate parameters:"""
      self.add_caster(
                      casterSerial, casterName, casterType,
                      unitAdding, diecaseSystem, interfaceID
                     )


  def add_interface(self, ID='', interfaceName='',
                    emergencyGPIO='',photocellGPIO='',
                    mcp0Address='', mcp1Address='', pinBase=''):
    """add_interface(ID, interfaceName, emergencyGPIO, photocellGPIO,
                     mcp0Address, mcp1Address, pinBase):

    Adds a Raspberry Pi I2C+GPIO interface parameters to the database.
    A single Raspberry can work with up to four interfaces -
    it's uncommon, but possible, and may come in handy if you have
    several casters that you want to control with several sets of valves.
    """


    """Reset revalidation; if everything is OK, the data can be written
    to the database. Else, the add_caster function will recurse into itself
    with entered data as arguments. The user will have to re-enter
    any parameter which does not match the expected values or type."""
    revalidate = False

    """Check if the serial No is numeric -
    we must ensure that the value in db is integer"""
    if str(ID).isdigit() and int(ID) in range(4):
      ID = int(ID)
    else:
      ID = raw_input(
                     'Enter the interface ID: 0, 1, 2, 3, 4; default 0: '
                    )
      if ID == '':
        ID = 0
      revalidate = True

    """Enter a string for interface name"""
    if not interfaceName:
      interfaceName = raw_input(
                                'Enter the name you want to use '
                                'for this interface: '
                               )
      revalidate = True

    """Emergency button GPIO for this interface"""
    if (
        str(emergencyGPIO).isdigit()
        and int(emergencyGPIO) > 3
       ):
      emergencyGPIO = int(emergencyGPIO)
    else:
      emergencyGPIO = raw_input(
                                'Enter the emergency button GPIO - '
                                'BCM number: '
                               )
      revalidate = True

    """Photocell GPIO for this interface"""
    if (
        str(photocellGPIO).isdigit()
        and int(photocellGPIO) > 3
        and photocellGPIO != emergencyGPIO
       ):
      photocellGPIO = int(photocellGPIO)
    else:
      photocellGPIO = raw_input(
                                'Enter the photocell GPIO - BCM number: '
                               )
      revalidate = True

    """First MCP23017 address for this interface, typically 0x20:"""
    if is_hex(mcp0Address):
      mcp0Address = conv_hex(mcp0Address)
    else:
      mcp0Address = raw_input(
                              'Enter the first MCP23017 I2C address - '
                              'hexadecimal. Default 0x20: '
                             )
      if mcp0Address == '':
        mcp0Address = '0x20'
      revalidate = True

    """Second MCP23017 address for this interface, typically 0x21:"""
    if is_hex(mcp1Address):
      mcp1Address = conv_hex(mcp1Address)
    else:
      mcp1Address = raw_input(
                              'Enter the second MCP23017 I2C address - '
                              'hexadecimal. Default 0x21: '
                             )
      if mcp1Address == '':
        mcp1Address = '0x21'
      revalidate = True

    """Pin base for GPIOs on MCP23017. Typically 65 for first interface,
    97 for second, 129 for third. 0 to 64 are RESERVED, we can't use them!"""
    if str(pinBase).isdigit() and int(pinBase) > 64:
      pinBase = int(pinBase)
    else:
      pinBase = raw_input(
                          'Enter the pin base for GPIOs on MCP23017 chips. '
                          'Default 65: '
                         )
      if pinBase == '':
        pinBase = 65
      revalidate = True


    if not revalidate:
      print('Interface ID: %i \n' % ID)
      print('Interface name: %s \n' % interfaceName)
      print('Emergency GPIO: %i \n' % emergencyGPIO)
      print('Photocell GPIO: %i \n' % photocellGPIO)
      print('MCP0 Address: %s \n' % mcp0Address)
      print('MCP1 Address: %s \n' % mcp1Address)
      print('Pin base: %i \n' % pinBase)


      ans = choice('\nCommit? '
                   '[y] - yes, save interface to database, '
                   '[n] - no, enter values again, '
                   'or [m] to return to main menu.',
                   ['y', 'n', 'm']
                  )
      if ans.lower() == 'y':
        if database.add_interface(ID, interfaceName, emergencyGPIO,
                                  photocellGPIO, mcp0Address,
                                  mcp1Address, pinBase
                                 ):
          print('Interface added successfully.')
        else:
          print('Failed to add interface!')
      elif ans.lower() == 'n':
        raw_input('Enter parameters again from scratch... ')
        self.add_interface()
      elif ans.lower() == 'm':
        """Back to menu..."""
        pass

    else:
      """If revalidate is True, function recurses into itself
      with obtained data and checks if that is correct:
      """
      self.add_interface(
                         ID, interfaceName, emergencyGPIO,
                         photocellGPIO, mcp0Address, mcp1Address,
                         pinBase
                        )


  def add_wedge(self, wedgeName='', setWidth='', oldPica='', steps=''):
    """add_wedge(wedgeName, setWidth, oldPica, steps)

    Used for adding wedges.

    Can be called with or without arguments.

    wedgeName - string - series name for a wedge (e.g. S5, S111)
    setWidth  - float - set width of a particular wedge (e.g. 9.75)
    oldPica - boolean - True if the wedge is European old pica
              ("E" after set width number), False otherwise
    steps - string with unit values for steps - e.g. '5,6,7,8,9,9,9...,16'

    If called without arguments, the function runs at least twice.
    The first time is for entering data, the second (and further) times
    are for validating and correcting the data entered earlier.
    When all data passes validation ("revalidate" flag remains False),
    user is asked if everything is correct and can commit values
    to the database."""


    """
    Reset revalidation: it's necessary to set the "revalidate" flag
    to False at the beginning.
    if everything is OK, the data can be written to the database.
    In case of empty/wrong values, the validation is failed and user
    has to enter or re-enter the value. The "revalidate" flag is set
    to True. After all values are collected, the add_caster function
    will recurse into itself with entered data as arguments.
    If everything is correct, the user will be able to commit the data
    to the database. If not, the user must re-enter
    any parameter which does not match the expected values or type.
    """
    revalidate = False


    """
    Let's define unit values for some known wedges.
    This is a dictionary, so you get values (string)
    by referring via key (string), feel free to add any unit values
    for the wedges not listed.

    This data will be useful when adding a wedge. The setup program
    will look up a wedge by its name, then get unit values.
    """
    wedgeData = { 'S5'   : '5,6,7,8,9,9,9,10,10,11,12,13,14,15,18,18',
                  'S96'  : '5,6,7,8,9,9,10,10,11,12,13,14,15,16,18,18',
                  'S111' : '5,6,7,8,8,8,9,9,9,9,10,12,12,13,15,15',
                  'S334' : '5,6,7,8,9,9,10,10,11,11,13,14,15,16,18,18',
                  'S344' : '5,6,7,9,9,9,10,11,11,12,12,13,14,15,16,16',
                  'S377' : '5,6,7,8,8,9,9,10,10,11,12,13,14,15,18,18',
                  'S409' : '5,6,7,8,8,9,9,10,10,11,12,13,14,15,16,16',
                  'S467' : '5,6,7,8,8,9,9,9,10,11,12,13,14,15,18,18',
                  'S486' : '5,7,6,8,9,11,10,10,13,12,14,15,15,18,16,16',
                  'S526' : '5,6,7,8,9,9,10,10,11,12,13,14,15,17,18,18',
                  'S536' : '5,6,7,8,9,9,10,10,11,12,13,14,15,17,18,18',
                  'S562' : '5,6,7,8,9,9,9,10,11,12,13,14,15,17,18,18',
                  'S607' : '5,6,7,8,9,9,9,9,10,11,12,13,14,15,18,18',
                  'S611' : '6,6,7,9,9,10,11,11,12,12,13,14,15,16,18,18',
                  'S674' : '5,6,7,8,8,9,9,9,10,10,11,12,13,14,15,18',
                  'S724' : '5,6,7,8,8,9,9,10,10,11,13,14,15,16,18,18',
                  'S990' : '5,5,6,7,8,9,9,9,9,10,10,11,13,14,18,18',
                  'S1063': '5,6,8,9,9,9,9,10,12,12,13,14,15,15,18,18',
                  'S1329': '4,5,7,8,9,9,9,9,10,10,11,12,12,13,15,15',
                  'S1331': '4,5,7,8,8,9,9,9,9,10,11,12,12,13,15,15',
                  'S1406': '4,5,6,7,8,8,9,9,9,9,10,10,11,12,13,15',
                  'MONOSPACE' : '9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9',
                }

    """In this program, all wedges have the "S" (for stopbar) letter
    at the beginning of their designation. However, the user can enter
    a designation with or without "S", so check if it's there, and
    append if needed (only for numeric designations - not the "monospace"
    or other text values!)

    If no name is given, assume that the user means the S5 wedge, which is
    very common and most casting workshops have a few of them.
    """
    if wedgeName == '':
      wedgeName = raw_input(
                            'Enter the wedge name, e.g. S5 '
                            '(very typical, default): '
                           )
      if wedgeName == '':
        wedgeName = 'S5'
      elif wedgeName[0].upper() != 'S' and wedgeName.isdigit():
        wedgeName = 'S' + wedgeName
      wedgeName = wedgeName.upper()
      revalidate = True

    """
    Enter a set width, float. If the width ends with "E", it's an
    old-pica (1pica = 0.1667") wedge for European foundries, thus E.
    Apparently, there were no cicero/Didot wedges, all was in picas.
    E will be stripped, and the program will determine whether it's
    an old pica wedge or not.
    """
    try:
      setWidth = float(setWidth)
    except ValueError:
      setWidth = raw_input(
                          'Enter the wedge set width as decimal, '
                          'e.g. 9.75E: '
                          )

      """Determine if it's an old pica wedge - E is present:"""
      if setWidth[-1].upper() == 'E':
        setWidth = setWidth[:-1]
        oldPica = True
      else:
        oldPica = False
      revalidate = True

    """Enter the wedge unit values for steps 1...15 (and optionally 16):"""
    if not steps:
      try:
        rawSteps = wedgeData[wedgeName]
      except (KeyError, ValueError):
        rawSteps = raw_input(
                            'Enter the wedge unit values for steps 1...16, '
                            'separated by commas. If empty, entering values '
                            'for wedge S5 (very common): '
                            )
      if rawSteps == '':
        rawSteps = '5,6,7,8,9,9,9,10,10,11,12,13,14,15,18,18'
      rawSteps = rawSteps.split(',')
      steps = []
      """
      Now we need to be sure that all whitespace is stripped,
      and the value written to database is a list of integers:
      """
      for step in rawSteps:
        step = int(step.strip())
        steps.append(step)
      """
      Display warning if the number of steps is anything other than
      15 or 16 (15 is most common, 16 was used for HMN and KMN systems):
      """
      if len(steps) < 15:
        print('Warning - the wedge you entered has less than 15 steps! \n'
              'This is almost certainly a mistake.\n'
             )
      elif len(steps) > 16:
        print('Warning - the wedge you entered has more than 16 steps! \n'
              'This is almost certainly a mistake.\n'
             )
      else:
        print 'The wedge has ', len(steps), 'steps. That is OK.'

    if not revalidate:
      print('Wedge: %s \n' % wedgeName)
      print('Set width: %f \n' % setWidth)
      print('Is it an old pica ("E") wedge?: %s \n' % str(oldPica))

      """Loop over all unit values in wedge's steps and display them:"""
      for i, step in zip(range(len(steps)), steps):
        print('Step %i unit value: %i \n' % (i+1, step))

      ans = choice('\nCommit? [y] - yes, save wedge to database, '
                   '[n] - no, enter values again, '
                   'or [m] to return to main menu.',
                   ['y', 'n', 'm']
                  )
      if ans.lower() == 'y':
        """If everything is OK and user confirms,
        add data to the database.
        """
        if database.add_wedge(wedgeName, setWidth, oldPica, steps):
          print('Wedge added successfully.')
        else:
          print('Failed to add wedge!')
      elif ans.lower() == 'n':
        raw_input('Enter parameters again from scratch... ')
        add_wedge()
      elif ans.lower() == 'm':
        """Back to menu..."""
        pass

    else:
      """Recurse into add_wedge with obtained data to re-check it"""
      self.add_wedge(wedgeName, setWidth, oldPica, steps)


  def delete_caster(self):
    """Ask for ID and delete the caster"""
    ID = raw_input('Enter the caster ID to delete: ')
    if ID.isdigit():
      ID = int(ID)
      if database.caster_by_id(ID):
        database.delete_caster(ID)
        print('Caster deleted successfully.')
    else:
      print('Caster ID must be a number!')


  def delete_interface(self):
    """Ask for ID and delete the interface"""
    ID = raw_input('Enter the interface ID to delete: ')
    if ID.isdigit():
      ID = int(ID)
      if database.get_interface(ID):
        database.delete_interface(ID)
        print('Interface deleted successfully.')
    else:
      print('Interface ID must be a number!')


  def delete_wedge(self):
    """Used for deleting a wedge from database"""
    ID = raw_input('Enter the wedge ID to delete: ')
    if ID.isdigit():
      ID = int(ID)
      if database.delete_wedge(ID):
        print('Wedge deleted successfully.')
    else:
      print('Wedge name must be a number!')


  def list_casters(self):
    """lists all casters we have in database"""
    database.list_casters()

  def list_interfaces(self):
    """lists all available interfaces"""
    database.list_interfaces()

  def list_wedges(self):
    """lists all wedges we have"""
    database.list_wedges()



  def menu(self):
    menu  (self,
    header = (
              'Setup program for rpi2caster computer-aided typecasting. '
              '\n\nMain menu:'
             ),
    footer = '',
    options = [
               [1, 'List casters', 'self.list_casters()'],
               [2, 'Add caster', 'self.add_caster()'],
               [3, 'Delete caster', 'self.delete_caster()'],
               [4, 'List interfaces', 'self.list_interfaces()'],
               [5, 'Add interface', 'self.add_interface()'],
               [6, 'Delete interface', 'self.delete_interface()'],
               [7, 'List wedges', 'self.list_wedges()'],
               [8, 'Add wedge', 'self.add_wedge()'],
               [9, 'Delete wedge', 'self.delete_wedge()'],
               [0, 'Exit program', 'exit()']
              ],
    recursive = True
          )

  def __exit__(self, *args):
    pass


database = Database()
setup = MonotypeSetup(database)
with setup:
  try:
    setup.menu()
  except KeyboardInterrupt:
    print('\nInterrupted by user.')
    exit()