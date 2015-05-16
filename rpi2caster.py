#!/usr/bin/python
# -*- coding: utf-8 -*-

"""rpi2caster - control a Monotype composition caster with Raspberry Pi.

Monotype composition caster & keyboard paper tower control program.

This program sends signals to the solenoid valves connected to the
composition caster's (or keyboard's) paper tower. When casting,
the program uses methods of the Monotype class and waits for the machine
to send feedback (i.e. an "air bar down" signal), then turns on
a group of valves. On the "air bar up" signal, valves are turned off and
the program reads another code sequence, just like the original paper
tower.

In "punching" mode, the program sends code sequences to the paper tower
(controlled by valves as well) in arbitrary time intervals, and there is
no machine feedback.

rpi2caster can also:
-cast a user-specified number of sorts from a matrix with given
coordinates (the "pump on", "pump off" and "line to the galley"
code sequences will be issued automatically),
-test all the valves, pneumatic connections and control mechanisms in a
caster (i.e. pinblocks, 0005/S/0075 mechs, unit-adding & unit-shift valves
and attachments), line by line,
-send a user-defined combination of signals for a time as long as the user
desires - just like piercing holes in a piece of ribbon and clamping the
air bar down.

During casting, the program automatically detects the machine movement,
so no additional actions on user's part are required.

In the future, the program will have an "emergency stop" feature.
When an interrupt on a certain Raspberry Pi's GPIO is detected, the program
stops sending codes to the caster and sends a 0005 combination instead.
The pump is immediately stopped.
"""


"""Typical libs, used by most routines:"""
import sys
import os
import time
#import string

"""Config parser for reading the interface settings"""
import ConfigParser

"""Used for serializing lists stored in database, and for communicating
with the web application (in the future):"""
try:
  import json
except ImportError:
  import simplejson as json

"""These libs are used by file name autocompletion:"""
import readline
import glob

"""Essential for polling the photocell for state change:"""
import select

"""MCP23017 driver & hardware abstraction layer library:"""
try:
  import wiringpi2 as wiringpi
  #import wiringpi
except ImportError:
  print('wiringPi2 not installed! It is OK for testing, '
        'but you MUST install it if you want to cast!')
  time.sleep(1)

"""rpi2caster uses sqlite3 database for storing caster, interface,
wedge, diecase & matrix parameters:"""
try:
  import sqlite3
except ImportError:
    print('You must install sqlite3 database and python-sqlite2 package.')
    exit()



class Config(object):
  """Configuration class.

  A class for reading and parsing the config file with a specified path.

  Want to use a different conffile? Just instantiate this class with
  a custom "path" parameter, that's all.
  """

  def __init__(self, path='/etc/rpi2caster.conf'):
    """Check if file is readable first:"""
    try:
      with open(path, 'r'):
        self.confFilePath = path
      self.cfg = ConfigParser.SafeConfigParser()
      self.cfg.read(self.confFilePath)
    except IOError:
      self.UI.notify_user('Cannot open config file:', path)


  def __enter__(self):
    self.UI.debug_info('Entering configuration context...')
    return self


  def get_caster_settings(self, casterName):
    """get_caster_settings(casterName):

    Reads the settings for a caster with self.casterName
    from the config file (where it is represented by a section, whose
    name is self.casterName).

    The parameters returned are:
    [diecase_system, unit_adding, interface_id]

    where:
    diecase_system - caster's diecase layout and a method of
                     accessing 16th row, if applicable:
                         norm15 - old 15x15,
                         norm17 - 15x17 NI, NL,
                         hmn    - 16x17 HMN (rare),
                         kmn    - 16x17 KMN (rare),
                         shift  - 16x17 unit-shift (most modern).
    unit_adding [0, 1] - whether the machine has a unit-adding attachment,
    interface_id [0, 1, 2, 3] - ID of the interface connected to the caster

    """

    try:
      """Get caster parameters from conffile."""

      unitAdding = self.cfg.get(casterName, 'unit_adding')
      diecaseSystem = self.cfg.get(casterName, 'diecase_system')
      interfaceID = self.cfg.get(casterName, 'interface_id')
      """Time to return the data:"""
      return [bool(unitAdding), diecaseSystem, int(interfaceID)]

    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError,
            ValueError, TypeError):
      """
      In case of shit happening, return None and fall back on defaults."""
      self.UI.notify_user(
          'Incorrect caster parameters. Using hardcoded defaults.'
          )
      self.UI.exception_handler()
      return None


  def get_interface_settings(self, interfaceID):
    """get_interface_settings(interfaceID):

    Reads a configuration file and gets interface parameters.

    If the config file is correct, it returns a list:
    [emergencyGPIO, photocellGPIO, mcp0Address, mcp1Address, pinBase]

    emergencyGPIO - BCM number for emergency stop button GPIO
    photocellGPIO - BCM number for photocell GPIO
    mcp0Address   - I2C address for 1st MCP23017
    mcp1Address   - I2C address for 2nd MCP23017
    pinBase       - pin numbering base for GPIO outputs on MCP23017

    Multiple interfaces attached to a single Raspberry Pi:

    It's possible to use up to four interfaces (i.e. 2xMCP23017, 4xULN2803)
    for a single Raspberry. It can be used for operating multiple casters,
    or a caster and a keyboard's paper tower, simultaneously (without
    detaching a valve block from the paper tower and moving it elsewhere).

    These interfaces should be identified by numbers: 0, 1, 2, 3.

    Each of the MCP23017 chips has to have unique I2C addresses. They are
    set by pulling the A0, A1, A2 pins up (to 3.3V) or down (to GND).
    There are 2^3 = 8 possible addresses, and an interface uses two chips,
    so you can use up to four interfaces.

    It's best to order the MCP23017 chips' addresses ascending, i.e.

    interfaceID    mcp0 pin    mcp1 pin    mcp0     mcp1
                   A2,A1,A0    A2,A1,A0    addr     addr

    0              000         001         0x20     0x21
    1              010         011         0x22     0x23
    2              100         101         0x24     0x25
    3              110         111         0x26     0x27

    where 0 means the pin is pulled down, and 1 means pin pulled up.

    As for pinBase parameter, it's the wiringPi's way of identifying GPIOs
    on MCP23017 extenders. WiringPi is an abstraction layer which allows
    you to control (read/write) pins on MCP23017 just like you do it on
    typical Raspberry Pi's GPIO pins. Thus you don't have to send bytes
    to registers.
    The initial 64 GPIO numbers are reserved for Broadcom SoC, so the lowest
    pin base you can use is 65. Each interface (2xMCP23017) uses 32 pins.

    If you are using multiple interfaces per Raspberry, you SHOULD
    assign the following pin bases to each interface:

    interfaceID    pinBase

    0              65
    1              98          (pinBase0 + 32)
    2              131         (pinBase1 + 32)
    3              164         (pinBase2 + 32)


    The interface ID is an attribute of an object.
    """
    interfaceName = 'Interface' + str(interfaceID)
    try:
      """Check if the interface is active, else return None"""
      trueAliases = ['true', '1', 'on', 'yes']
      if self.cfg.get(interfaceName, 'active').lower() in trueAliases:
        emergencyGPIO = self.cfg.get(interfaceName, 'emergency_gpio')
        photocellGPIO = self.cfg.get(interfaceName, 'photocell_gpio')
        mcp0Address = self.cfg.get(interfaceName, 'mcp0_address')
        mcp1Address = self.cfg.get(interfaceName, 'mcp1_address')
        pinBase = self.cfg.get(interfaceName, 'pin_base')

        """Check which signals arrangement the interface uses..."""
        signalsArrangement = self.cfg.get(interfaceName, 'signals_arr')
        """...and get the signals order for it:"""
        signalsArrangement = self.cfg.get('SignalsArrangements',
                                              signalsArrangement)

        """Return parameters:"""
        return [int(emergencyGPIO), int(photocellGPIO),
                int(mcp0Address, 16), int(mcp1Address, 16),
                int(pinBase), signalsArrangement]
      else:
        """This happens if the interface is inactive in conffile:"""
        self.UI.notify_user(
              'Interface ID=', interfaceID, 'is marked as inactive. '
              'We cannot use it - reverting to defaults'
              )
        return None

    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError,
            ValueError, TypeError):
      """
      In case of shit happening, return None and fall back on defaults.
      """
      self.UI.notify_user(
           'Incorrect interface parameters. Using hardcoded defaults.'
           )
      self.UI.exception_handler()
      return None


  def get_keyboard_settings(self, name):
    """get_keyboard_settings(name):

    Reads the settings for a keyboard with a given name
    from the config file (where it is represented by its section).
    """

    try:
      """Get caster parameters from conffile."""
      interfaceID = self.cfg.get(name, 'interface_id')

    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError,
            ValueError, TypeError):
      """
      In case of shit happening, fall back on defaults."""
      self.UI.notify_user(
          'Incorrect parameters. Using hardcoded defaults.'
          )
      interfaceID = 0
      self.UI.exception_handler()


    """Time to get interface parameters:"""
    interfaceName = 'Interface' + str(interfaceID)
    try:
      """Check if the interface is active, else return None"""
      trueAliases = ['true', '1', 'on', 'yes']
      if self.cfg.get(interfaceName, 'active').lower() in trueAliases:
        mcp0Address = self.cfg.get(interfaceName, 'mcp0_address')
        mcp1Address = self.cfg.get(interfaceName, 'mcp1_address')
        pinBase = self.cfg.get(interfaceName, 'pin_base')

        """Check which signals arrangement the interface uses
        and get the signals order for it:
        """
        signalsArrangement = self.cfg.get('SignalsArrangements',
                             self.cfg.get(interfaceName, 'signals_arr'))

        """Return a tuple of parameters for keyboard:"""
        return (int(interfaceID), int(mcp0Address, 16),
                int(mcp1Address, 16), int(pinBase),
                signalsArrangement)

      else:
        """This happens if the interface is inactive in conffile:"""
        self.UI.notify_user(
              'Interface ID=', interfaceID, 'is marked as inactive. '
              'We cannot use it - reverting to defaults.'
              )
        return False

    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError,
            ValueError, TypeError):
      """
      In case of shit happening, return False and fall back on defaults.
      """
      self.UI.notify_user(
           'Incorrect interface parameters. Using hardcoded defaults.'
           )
      self.UI.exception_handler()
      return False


  def __exit__(self, *args):
    self.UI.debug_info('Exiting configuration context.')
    pass



class Database(object):
  """Database(databasePath, confFilePath):

  A class containing all methods related to storing, retrieving
  and deleting data from a SQLite3 database used for config.

  We're using database because it's easy to access and modify with
  third-party programs (like sqlite, sqlitebrowser or a Firefox plugin),
  and there will be lots of data to store: diecase (matrix case)
  properties, diecase layouts, wedge unit values, caster and interface
  settings (although we may move them to config files - they're "system"
  settings best left default, instead of "foundry" settings the user has
  to set up before being able to cast, based on their type foundry's
  inventory, which varies from one place to another).

  Methods here are for reading/writing data for diecases, matrices,
  wedges (and casters & interfaces) from/to designated sqlite3 database.

  Default database path is ./database/monotype.db - but you can
  override it by instantiating this class with a different name
  passed as an argument. It is necessary that the user who's running
  this program for setup has write access to the database file;
  read access is enough for normal operation.
  Usually you run setup with sudo.
  """

  def __init__(self, databasePath='', confFilePath='/etc/rpi2caster.conf'):
    self.databasePath = databasePath
    self.confFilePath = confFilePath

  def __enter__(self):
    self.UI.debug_info('Entering database context...')
    self.database_setup()
    self.UI.debug_info('Using database path:', self.databasePath)
    self.db = sqlite3.connect(self.databasePath)
    return self


  def database_setup(self):
    """Initialize database:

    Database path passed to class has priority over database path
    set in conffile. If none of them is found, the program will use
    hardcoded default.
    """
    if not self.databasePath:
      config = ConfigParser.SafeConfigParser()
      config.read(self.confFilePath)

      """Look database path up in conffile:"""
      try:
        self.databasePath = config.get('Database', 'path')
      except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        """Revert to default:"""
        self.databasePath = 'database/monotype.db'
        self.UI.debug_notice('Database path not found in conffile. '
                             'Using default:', self.databasePath)


  def add_wedge(self, wedgeName, setWidth, oldPica, steps):
    """add_wedge(wedgeName, setWidth, oldPica, steps):

    Registers a wedge in our database.
    Returns True if successful, False otherwise.

    Arguments:

    wedgeName - wedge's number, e.g. S5 or 1160. String, cannot be null.

    setWidth - set width of a wedge, e.g. 9.75. Float, cannot be null.

    oldPica - determines if it's an old pica system (i.e. 1pica = 0.1667")
        If the wedge has "E" at the end of its number (e.g. 5-12E), then
        it's an old-pica wedge.
        1, True, 0, False.

    steps - a list with unit values for each of the wedge's steps.
        Not null.

    An additional column, id, will be created and auto-incremented.
    This will be an unique identifier of a wedge.
    """

    """data - a list with wedge parameters to be written:"""
    data = [wedgeName, setWidth, str(oldPica), json.dumps(steps)]

    with self.db:
      try:
        cursor = self.db.cursor()
        """Create the table first:"""
        cursor.execute(
                      'CREATE TABLE IF NOT EXISTS wedges '
                      '(id INTEGER PRIMARY KEY ASC AUTOINCREMENT, '
                      'wedge_id TEXT NOT NULL, '
                      'set_width REAL NOT NULL, '
                      'old_pica TEXT NOT NULL, '
                      'steps TEXT NOT NULL)'
                      )

        """Then add an entry:"""
        cursor.execute(
                      'INSERT INTO wedges '
                      '(wedge_id,set_width,old_pica,steps) '
                      'VALUES (?, ?, ?, ?)', data
                      )
        self.db.commit()
        return True

      except:
        """In debug mode we get the exact exception code & stack trace."""
        self.UI.notify_user('Database error: cannot add wedge!')
        self.UI.exception_handler()
        return False



  def wedge_by_name_and_width(self, wedgeName, setWidth):
    """wedge_by_name_and_width(wedgeName, setWidth):

    Looks up a wedge with given ID and set width in database.
    Useful when coding a ribbon - wedge is obtained from diecase data.

    If wedge is registered, function returns:
    ID - unique, int (e.g. 0),
    wedgeName - string (e.g. S5) - wedge name
    setWidth - float (e.g. 9.75) - set width,
    oldPica - bool - whether this is an old-pica ("E") wedge or not,
    steps - list of unit values for all wedge's steps.

    Else, function returns False.
    """

    with self.db:
      try:
        cursor = self.db.cursor()
        cursor.execute(
                      'SELECT * FROM wedges WHERE wedge_id = ? '
                      'AND set_width = ?', [wedgeName, setWidth]
                      )
        wedge = cursor.fetchone()
        if wedge is None:
          self.UI.notify_user(
                                  'No wedge %s - %f found in database!'
                                   % (wedgeName, setWidth)
                                 )
          return False
        else:
          wedge = list(wedge)
          self.UI.notify_user(
                                  'Wedge', wedgeName, '-', setWidth,
                                  'set found in database - OK'
                                 )

          """Change return value of oldPica to boolean:"""
          wedge[3] = bool(wedge[3])

          """Change return value of steps to list:"""
          wedge[4] = json.loads(wedge[4])

          """Return [ID, wedgeName, setWidth, oldPica, steps]:"""
          return wedge

      except:
        """In debug mode we get the exact exception code & stack trace."""
        self.UI.notify_user('Database error: cannot get wedge!')
        self.UI.exception_handler()


  def wedge_by_id(self, ID):
    """wedge_by_id(ID):

    Gets parameters for a wedge with given ID.

    If so, returns:
    ID - unique, int (e.g. 0),
    wedgeName - string (e.g. S5) - wedge name
    setWidth - float (e.g. 9.75) - set width,
    oldPica - bool - whether this is an old-pica ("E") wedge or not,
    steps - list of unit values for all wedge's steps.

    Else, returns False.
    """

    with self.db:
      try:
        cursor = self.db.cursor()
        cursor.execute(
                      'SELECT * FROM wedges WHERE id = ? ', [ID]
                      )
        wedge = cursor.fetchone()
        if wedge is None:
          self.UI.notify_user('Wedge not found!')
          return False
        else:
          wedge = list(wedge)

          """Change return value of oldPica to boolean:"""
          wedge[3] = bool(wedge[3])

          """Change return value of steps to list:"""
          wedge[4] = json.loads(wedge[4])

          """Return [ID, wedgeName, setWidth, oldPica, steps]:"""
          return wedge

      except:
        """In debug mode we get the exact exception code & stack trace."""
        self.UI.notify_user('Database error: cannot get wedge!')
        self.UI.exception_handler()


  def delete_wedge(self, ID):
    """delete_wedge(self, ID):

    Deletes a wedge with given unique ID from the database
    (useful in case we no longer have the wedge).

    Returns True if successful, False otherwise.

    First, the function checks if the wedge is in the database at all.
    """
    if self.wedge_by_id(ID):
      with self.db:
        try:
          cursor = self.db.cursor()
          cursor.execute(
                         'DELETE FROM wedges WHERE id = ?', [ID]
                        )
          return True
        except:
          """In debug mode we get the exact exception code & stack trace."""
          self.UI.notify_user('Database error: cannot delete wedge!')
          self.UI.exception_handler()
          return False
    else:
      self.UI.notify_user('Nothing to delete.')
      return False


  def list_wedges(self):
    """list_wedges(self):

    Lists all wedges stored in database, with their step unit values.

    Prints the following to stdout:

    ID - unique, int (e.g. 0),
    wedgeName - string (e.g. S5) - wedge name
    setWidth - float (e.g. 9.75) - set width,
    oldPica - bool - whether this is an old-pica ("E") wedge or not,
    steps - list of unit values for all wedge's steps.

    Returns True if successful, False otherwise.
    """

    with self.db:
      try:
        cursor = self.db.cursor()
        cursor.execute('SELECT * FROM wedges')
        self.UI.notify_user(
                            '\nid, wedge name, set width, British pica, '
                            'unit values for all steps:\n'
                           )
        while True:
          wedge = cursor.fetchone()
          if wedge is not None:
            wedge = list(wedge)

            """Change return value of steps to list:"""
            wedge[4] = json.loads(wedge[4])

            """Print all the wedge parameters:"""
            self.UI.notify_user(' '.join([str(item)
                                    for item in list(wedge)]), '\n')
          else:
            break
        return True

      except:
        """In debug mode we get the exact exception code & stack trace."""
        self.UI.notify_user('Database error: cannot list wedges!')
        self.UI.exception_handler()
        return False


  def get_diecase(self, typeSeries, typeSize, diecaseSystem, styles):
    """
    Searches for diecase metadata, based on the desired type series,
    type size, diecase system (norm15, norm17, MNH, MNK, unit-shift),
    required styles (r - roman, b - bold, i - italic, sc - small caps,
    sup - superior, inf - inferior)
    """
    with self.db:
      try:
        cursor = self.db.cursor()
        cursor.execute(
                        'SELECT * FROM diecases WHERE type_series = "%s" '
                        'AND size = %i AND diecase_system = %s',
                        (typeSeries, typeSize, diecaseSystem)
                      )
        while True:
          diecase = cursor.fetchone()
          if diecase is not None:
            diecase = list(diecase)

            """Print all the parameters:"""
            self.UI.notify_user(' '.join([str(item)
                                    for item in diecase]), '\n')
          else:
            break

      except:
        """In debug mode we get the exact exception code & stack trace."""
        self.UI.notify_user('Database error: cannot find diecase data!')
        self.UI.exception_handler()
        return False


  def get_matrix_position(self, character, style, diecaseID):
    """
    Searches for matrix coordinates (column, row) where the character
    is stored in the diecase - based on diecase ID (which dictates layout,
    type series/typeface, size) and character's style 
    (r, b, i, sc, sup, inf). Returns character's unit width as well.
    """
    with self.db:
      try:
        cursor = self.db.cursor()
        cursor.execute(
                        'SELECT * FROM %s WHERE character = "%s" '
                        'AND style = %s',
                        ('layout_' + diecaseID, character, style)
                      )
        rawData = cursor.fetchone()
        row = rawData[1]
        column = rawData[2]
        unitWidth = rawData[3]
        return (row, column, unitWidth)

      except:
        """In debug mode we get the exact exception code & stack trace."""
        self.UI.notify_user('Database error: cannot get coordinates!')
        self.UI.exception_handler()
        return False


  def __exit__(self, *args):
    self.UI.debug_info('Exiting database context.')
    pass
  
  
  
class Typesetting(object):
  """Typesetter:

  This class contains all methods related to typesetting, i.e. converting
  an input text to a sequence of Monotype codes to be read by the casting
  interface. This class is to be instantiated, so that all data
  and buffers are contained within an object and isolated from other
  typesetting sessions.
  """

  def __init__(self):
    self.diecase = ''
    self.setWidth = ''
    self.typeface = ''
    self.typeSeries = ''
    self.diecaseID = ''
    self.typeSize = ''
    self.wedge = ''
    self.diecaseSystem = ''
    self.layout = []
    self.lineLength = ''
    self.singleSetUnitLineLength = ''
    self.multiSetUnitLineLength = ''
    self.measurement = ''
    self.inputFile = ''
    self.outputFile = ''

  def __enter__(self):
    self.UI.debug_info('Entering typesetting job context...')
    return self

  def main_menu(self):
    """Calls self.UI.menu() with options,
    a header and a footer.

    Options: {option_name : description}
    """
    options = {
               1 : 'Load a text file',
               2 : 'Specify an output file name',
               3 : 'Choose diecase',
               4 : 'Display diecase layout',
               5 : 'Enter line length',
               6 : 'Calculate units',
               7 : 'Choose machine settings',
               8 : 'Translate text to Monotype code',
               0 : 'Exit program'
              }


    """Declare local functions for menu options:"""
    def choose_input_filename():
      self.inputFile = self.UI.enter_input_filename()
      self.main_menu()
      
    def choose_output_filename():
      self.outputFile = self.UI.enter_output_filename()
      self.main_menu()

    def debug_notice():
      """Prints a notice if the program is in debug mode:"""
      if self.UI.debugMode:
        return('\n\nThe program is now in debugging mode!')
      else:
        return ''

    def additional_info():
      """Displays additional info as a main menu footer.

      Start with empty list:"""
      info = []
      
      """Add ribbon filename, if any:"""
      if self.inputFile:
        info.append('Input file name: ' + self.inputFile)

      """Add ribbon filename, if any:"""
      if self.outputFile:
        info.append('Output file name: ' + self.outputFile)

      """Add a diecase info:"""
      if self.diecase:
        info.append('\nDiecase info:\n')
        info.append('Using diecase ID: ' + str(self.diecaseID))
        info.append('Typeface: '         + str(self.typeface))
        info.append('Series: '           + str(self.typeSeries))
        info.append('Size: '             + str(self.typeSize))
        info.append('Stopbar/wedge: '    + str(self.wedge))
        info.append('Set width: '        + str(self.setWidth))
        info.append('Diecase system: '   + str(self.diecaseSystem))
        
        variants = []
        for variant in self.layout:
          variants.append(variant)
        if variants:
          info.append('Variants: ' + ', '.join(variants) + '\n')
          
          
      """Add a line length:"""
      if self.lineLength:
        info.append('Line length: %i %s' % (self.lineLength, self.measurement))
        
      """Unit line length in 1-set units:"""
      if self.singleSetUnitLineLength:
        info.append('Line length in 1-set units: %i' 
                      % self.singleSetUnitLineLength)
      
      """Unit line length in multiset units:"""
      if self.multiSetUnitLineLength:
        info.append('Line length in n-set units: %i' 
                       % self.multiSetUnitLineLength)
        

      """Convert it all to a multiline string:"""
      return '\n'.join(info)


    """Commands: {option_name : function}"""
    commands = {
                1 : choose_input_filename,
                2 : choose_output_filename,
                3 : self.choose_diecase,
                4 : self.display_diecase_layout,
                5 : self.enter_line_length,
                6 : self.calculate_units,
                7 : self.choose_machine_settings,
                8 : self.translate,
                0 : self.UI.exit_program
               }

    choice = self.UI.menu( options,
              header = (
                        'rpi2caster - CAT (Computer-Aided Typecasting) '
                        'for Monotype Composition or Type and Rule casters.'
                        '\n\n'
                        'This program reads a ribbon (input file) '
                        'and casts the type on a Composition Caster, \n'
                        'or punches a paper tape with a paper tower '
                        'taken off a Monotype keyboard.'
                       ) + debug_notice() + '\n\nMain Menu:',

              footer = additional_info()
              )


    """Call the function and return to menu.
    Use caster context for everything that needs it:"""
    commands[choice]()
    self.main_menu()
    
  
  def enter_line_length(self):
    """enter_line_length():
    
    Sets the line length and allows to specify measurement units.
    """
    
    if self.lineLength:
      self.lineLength = ''
    while not self.lineLength.isdigit():
      self.lineLength = raw_input('Enter the desired line length: ')
    else:
      self.lineLength = int(self.lineLength)
    
    """The line length is set. Now choose the measurement units."""    
    
    options = {
               'c'  : 'cicero',
               'b'  : 'britPica',
               'a'  : 'amerPica',
               'cm' : 'cm',
               'mm' : 'mm',
               'in' : 'in'
              }
    message = (
               'Select measurement units:\n'
               'a - American pica (0.1660"),\n'
               'b - British pica (0.1667"),\n'
               'c - Didot cicero (0.1776"),\n'
               'cm - centimeters,\n'
               'mm - millimeters,\n'
               'in - inches\n'
              )
    choice = self.UI.simple_menu(message, options)
    
    self.measurement = options[choice]
    
                                     
  def choose_diecase(self):
    """Choose diecase:
    
    Placeholder: we'll import hardcoded 327-12 TNR for now...
    TODO: implement a proper diecase choice!"""
    
    diecaseID = '327-12-KS01'
    typeface = 'Times New Roman'
    series = 327
    size = '12D'
    setWidth = 12
    wedge = 'S5'
    diecaseSystem = 'shift'
    layout = {
          'roman' : {
                   'a' : ('H', 9, 7),
                   'ą' : ('K', 9, 7),
                   'b' : ('E', 11, 7),
                   'c' : ('I', 5, 7),
                   'ć' : ('J', 5, 7),
                   'd' : ('H', 10, 7),
                   'e' : ('G', 6, 7),
                   'ę' : ('K', 5, 7),
                   'f' : ('F', 3, 6),
                   'g' : ('F', 9, 7),
                   'h' : ('K', 10, 8),
                   'i' : ('H', 2, 5),
                   'j' : ('I', 2, 5),
                   'k' : ('L', 10, 8),
                   'l' : ('J', 2, 5),
                   'ł' : ('K', 2, 5),
                   'm' : ('G', 14, 15),
                   'n' : ('F', 10),
                   'ń' : ('N', 9),
                   'o' : ('B', 9),
                   'ó' : ('L', 9),
                   'p' : ('J', 10),
                   'q' : ('C', 10),
                   'r' : ('E', 4),
                   's' : ('F', 4),
                   'ś' : ('H', 4),
                   't' : ('L', 2),
                   'u' : ('G', 9),
                   'v' : ('E', 9),
                   'w' : ('N', 12),
                   'x' : ('J', 9),
                   'y' : ('I', 9),
                   'z' : ('H', 5),
                   'ź' : ('L', 5),
                   'ż' : ('M', 5),
                   'A' : ('G', 13),
                   'Ą' : ('L', 13),
                   'B' : ('H', 11),
                   'C' : ('K', 12),
                   'Ć' : ('NL', 12),
                   'D' : ('B', 14),
                   'E' : ('K', 11),
                   'Ę' : ('C', 12),
                   'F' : ('J', 12),
                   'G' : ('C', 14),
                   'H' : ('I', 14),
                   'I' : ('E', 3),
                   'J' : ('F', 5),
                   'K' : ('J', 14),
                   'L' : ('I', 12),
                   'Ł' : ('B', 10),
                   'M' : ('G', 15),
                   'N' : ('F', 14),
                   'Ń' : ('K', 14),
                   'O' : ('F', 13),
                   #'Ó' : (),
                   'P' : ('D', 10),
                   'Q' : ('J', 13),
                   'R' : ('E', 13),
                   'S' : ('B', 10),
                   'Ś' : ('NI', 9),
                   'T' : ('J', 11),
                   'U' : ('H', 14),
                   'V' : ('D', 12),
                   'W' : ('D', 15),
                   'X' : ('I', 13),
                   'Y' : ('H', 13),
                   'Z' : ('H', 12),
                   'Ź' : ('A', 12),
                   #'Ż' : (),
                   '1' : ('D', 6),
                   '2' : ('E', 6),
                   '3' : ('F', 6),
                   '4' : ('D', 7),
                   '5' : ('E', 7),
                   '6' : ('F', 7),
                   '7' : ('G', 7),
                   '8' : ('D', 8),
                   '9' : ('E', 8),
                   '0' : ('F', 8),
                   '+' : ('A', 16),
                   '×' : ('NL', 16),
                   '[' : ('NI', 1),
                   ']' : ('NL', 1),
                   '(' : ('A', 2),
                   ')' : ('B', 2),
                   ':' : ('C', 3),
                   ';' : ('D', 3),
                   '?' : ('N', 5),
                   '/' : ('NL', 4),
                   '°' : ('NI', 5),
                   '-' : ('E', 2),
                   #'–' : (),
                   #'—' : (),
                   '=' : ('H', 16),
                   '.' : ('M', 1),
                   '!' : ('B', 3),
                   '%' : ('E', 16),
                   '•' : ('O', 1),
                   '*' : ('G', 10),
                   #'„' : (),
                   #'”' : (),
                   ',' : ('L', 1),
                   "'" : ('F', 1),
                   '’' : ('E', 1)
                   },
           'bold' : {
                   'a' : ('G', 8),
                   'ą' : ('K', 6),
                   'b' : ('I', 6),
                   'c' : ('J', 4),
                   'ć' : ('L', 4),
                   'd' : ('H', 7),
                   'e' : ('I', 4),
                   'ę' : ('M', 4),
                   'f' : ('F', 2),
                   'g' : ('I', 7),
                   'h' : ('J', 8),
                   'i' : ('H', 1),
                   'j' : ('I', 1),
                   'k' : ('M', 9),
                   'l' : ('J', 1),
                   'ł' : ('K', 1),
                   'm' : ('D', 14),
                   'n' : ('C', 6),
                   'ń' : ('K', 7),
                   'o' : ('H', 8),
                   'ó' : ('K', 8),
                   'p' : ('J', 6),
                   'q' : ('L', 8),
                   'r' : ('I', 3),
                   's' : ('J', 3),
                   'ś' : ('K', 3),
                   't' : ('L', 3),
                   'u' : ('J', 7),
                   'v' : ('O', 5),
                   'w' : ('N', 11),
                   #'x' : (),
                   'y' : ('I', 8),
                   'z' : ('K', 4),
                   'ź' : ('N', 4),
                   'ż' : ('O', 4),
                   'A' : ('I', 16),
                   'Ą' : ('O', 13),
                   'B' : ('NL', 15),
                   'C' : ('NI', 12),
                   #'Ć' : (),
                   'D' : ('O', 14),
                   'E' : ('M', 11),
                   'Ę' : ('I', 10),
                   'F' : ('O', 10),
                   'G' : ('B', 16),
                   'H' : ('M', 14),
                   'I' : ('G', 3),
                   'J' : ('O', 9),
                   'K' : ('J', 15),
                   'L' : ('F', 12),
                   'Ł' : ('O', 11),
                   'M' : ('I', 15),
                   'N' : ('C', 16),
                   'Ń' : ('NL', 14),
                   'O' : ('L', 14),
                   'Ó' : ('NI', 14),
                   'P' : ('G', 12),
                   'Q' : ('N', 16),
                   'R' : ('H', 15),
                   'S' : ('M', 10),
                   'Ś' : ('NL', 9),
                   'T' : ('L', 11),
                   'U' : ('A', 15),
                   'V' : ('J', 16),
                   'W' : ('M', 15),
                   'X' : ('L', 15),
                   'Y' : ('M', 16),
                   'Z' : ('E', 15),
                   'Ź' : ('N', 15),
                   #'Ż' : (),
                   '1' : ('M', 6),
                   '2' : ('N', 6),
                   '3' : ('O', 6),
                   '4' : ('L', 7),
                   '5' : ('M', 7),
                   '6' : ('N', 7),
                   '7' : ('O', 7),
                   '8' : ('M', 8),
                   '9' : ('N', 8),
                   '0' : ('O', 8),
                   #'+' : (),
                   #'×' : (),
                   #'[' : (),
                   #']' : (),
                   '(' : ('N', 2),
                   ')' : ('O', 2),
                   ':' : ('M', 3),
                   ';' : ('D', 5),
                   '?' : ('L', 6),
                   #'/' : (),
                   #'°' : (),
                   '-' : ('M', 2),
                   #'–' : (),
                   #'—' : (),
                   #'=' : (),
                   '.' : ('NI', 2),
                   '!' : ('O', 3),
                   '%' : ('F', 16),
                   #'•' : (),
                   #'*' : (),
                   #'„' : (),
                   #'”' : (),
                   ',' : ('NL', 2),
                   "'" : ('N', 1),
                   '’' : ('NL', 2)
                   },
         'italic' : {
                   'a' : ('B', 8),
                   'ą' : ('NI', 7),
                   'b' : ('NL', 6),
                   'c' : ('C', 5),
                   'ć' : ('A', 5),
                   'd' : ('A', 6),
                   'e' : ('E', 5),
                   'ę' : ('A', 4),
                   'f' : ('C', 2),
                   'g' : ('B', 6),
                   'h' : ('A', 9),
                   'i' : ('D', 1),
                   'j' : ('C', 1),
                   'k' : ('N', 9),
                   'l' : ('B', 1),
                   'ł' : ('A', 1),
                   'm' : ('M', 13),
                   'n' : ('C', 5),
                   'ń' : ('N', 10),
                   'o' : ('NL', 5),
                   'ó' : ('NL', 7),
                   'p' : ('A', 7),
                   'q' : ('C', 8),
                   'r' : ('A', 3),
                   's' : ('C', 4),
                   'ś' : ('H', 3),
                   't' : ('D', 2),
                   'u' : ('A', 8),
                   'v' : ('B', 5),
                   'w' : ('G', 11),
                   'x' : ('C', 9),
                   'y' : ('B', 7),
                   'z' : ('B', 4),
                   'ź' : ('G', 4),
                   'ż' : ('D', 4),
                   'A' : ('E', 12),
                   #'Ą' : (),
                   'B' : ('B', 11),
                   'C' : ('L', 12),
                   #'Ć' : (),
                   'D' : ('D', 13),
                   'E' : ('F', 11),
                   'Ę' : ('K', 15),
                   'F' : ('NL', 10),
                   'G' : ('M', 12),
                   'H' : ('A', 14),
                   'I' : ('NL', 3),
                   'J' : ('C', 7),
                   'K' : ('B', 15),
                   'L' : ('D', 11),
                   'Ł' : ('I', 11),
                   'M' : ('F', 15),
                   'N' : ('B', 13),
                   #'Ń' : (),
                   'O' : ('C', 13),
                   #'Ó' : (),
                   'P' : ('C', 11),
                   'Q' : ('K', 16),
                   'R' : ('C', 15),
                   'S' : ('A', 10),
                   #'Ś' : (),
                   'T' : ('E', 11),
                   'U' : ('A', 13),
                   'V' : ('G', 16),
                   'W' : ('E', 14),
                   'X' : ('N', 13),
                   'Y' : ('O', 12),
                   'Z' : ('NI', 11),
                   #'Ź' : (),
                   'Ż' : ('NI', 16),
                   #'1' : (),
                   #'2' : (),
                   #'3' : (),
                   #'4' : (),
                   #'5' : (),
                   #'6' : (),
                   #'7' : (),
                   #'8' : (),
                   #'9' : (),
                   #'0' : (),
                   #'+' : (),
                   #'×' : (),
                   #'[' : (),
                   #']' : (),
                   #'(' : (),
                   #')' : (),
                   ':' : ('NI', 4),
                   ';' : ('N', 3),
                   '?' : ('NI', 6),
                   #'/' : (),
                   #'°' : (),
                   #'-' : (),
                   #'–' : (),
                   #'—' : (),
                   #'=' : (),
                   #'.' : (),
                   '!' : ('NI', 3),
                   #'%' : (),
                   #'•' : (),
                   #'*' : (),
                   #'„' : (),
                   #'”' : (),
                   #',' : (),
                   #"'" : (),
                   #'’' : ()
                   }
    }

    self.diecase = (diecaseID, typeface, series, 
                    size, wedge, setWidth, diecaseSystem, layout)
                    
    """End of placeholder code."""                    
    [self.diecaseID, self.typeface, self.typeSeries,
     self.typeSize, self.wedge, self.setWidth,
     self.diecaseSystem, self.layout ] = self.diecase
    
    """Try to construct character maps for all variants:"""
    try:
      self.romanCharset         = self.layout['roman']
    except:
      pass
    try:
      self.boldCharset          = self.layout['bold']
    except:
      pass
    try:
      self.italicCharset        = self.layout['italic']
    except:
      pass
    try:
      self.smallcapsCharset     = self.layout['smallcaps']
    except:
      pass
    try:
      self.subscriptCharset     = self.layout['subscript']
    except:
      pass
    try:
      self.superscriptCharset   = self.layout['superscript']
    except:
      pass
    
    """Choose a wedge based on wedge number and set size:"""
    with self.database:
      wedgeSteps = self.database.wedge_by_name_and_width(
                               self.wedge, self.setWidth)[4]
    self.wedgeUnits = dict(zip(range(1, 17), wedgeSteps))
  
  
  def display_diecase_layout(self):
    """display_diecase_layout:
    
    Displays all characters, grouped by variant (roman, bold, italic,
    small caps, subscript, superscript) with their coordinates and unit
    values.
    
    Sanity check: we must have chosen a diecase first...
    TODO: make an option accessible in menu only if diecase is chosen.
    """
    if not self.layout:
      self.UI.notify_user('Diecase not chosen, no layout to check!')
      time.sleep(1)
      self.main_menu()
    
    for variant in self.layout:
      self.UI.notify_user('\nMatrices for variant: ' + variant + '\n\n'+
                          'Char:   Column: Row: Units: ')
      variantCharset = self.layout[variant]
      for character in variantCharset:
        parameters = variantCharset[character]
        column   = parameters[0]
        row      = parameters[1]
        try:
          units  = parameters[2]
        except IndexError:
          units = self.wedgeUnits[row]
        """Now display the data:"""
        self.UI.notify_user(
                            character.strip().rjust(6) + 
                            column.rjust(8) + str(row).rjust(5) + 
                            str(units).rjust(7)
                            )
                            
    """Wait until user presses return:"""
    self.UI.enter_data('Press return to go back to menu....')
        

  
  def choose_machine_settings(self):
    """choose_machine_settings:
    
    Chooses the machine settings - diecase format (15x15, 15x17,
    16x17 HMN, KMN or unit-shift), justification mode (0005, 0075 or NJ, NK)
    and whether there's a unit-shift attachment.
    """
    
    
    
    
  def translate(self):
    """translate:
    
    A proper translation routine. It calculates unit widths of characters,
    and adds them, then warns the operator if the line is near filling.
    
    TODO: add description,
    TODO: work on this routine and make justified type
    """
    
    if (not self.inputFile or not self.outputFile):
      self.UI.notify_user('You must specify the input '
                          'and output filenames first!')
      time.sleep(1)
      


  @staticmethod
  def calculate_wedges(setWidth, units):
    """calculate_wedges(setWidth, units):

    Calculate the 0005 and 0075 wedge positions based on the unit width
    difference (positive or negative) for the given set width.

    Since one step of 0075 wedge is 15 steps of 0005, we'll get a total
    would-be number of 0005 steps, then floor-divide it by 15 to get the
    0075 steps, and modulo-divide by 15 to get 0005 steps.

    If number of 0075 steps or 0005 steps is 0, we'll set 1 instead,
    because the wedge cannot have a "0" position.

    The function returns a list: [pos0075, pos0005].

    Maths involved may be a bit daunting, but it's not rocket science...
    First, we need to derive the width in inches of 1 unit 1 set:

    1p [pica] = 1/6" = 0.1667" (old pica), or alternatively:
    1p = 0.1660" (new pica - closer to the Fournier system).
    1p = 12pp [pica-points]. So, 1pp = 1/12p * 1/6["/p] = 1/72".

    In continental Europe, they used ciceros and Didot points:
    1c = 0.1776"
    1c = 12D - so, 1D = 0.0148"

    A set number of the type is the width of an em (i.e., widest char).
    It can, but doesn't have to, be the same as the type size in pp.
    Set numbers were multiples of 1/4, so we can have 9.75, 10, 11.25 etc.

    For example, 327-12D Times New Roman is 12set (so, it's very close),
    but condensed type will have a lower set number.

    And 1 Monotype fundamental unit is defined as 1/18em. Thus, the width
    of 1 unit 1 set = 1/18 pp; 1 unit multi-set = setWidth/18 pp.

    All things considered, let's convert the unit to inches:

    Old pica:
    W(1u 1set) = 1/18 * 1/72" = 1/1296"

    The width in inches  of a given no of units at a given set size is:
    W = s * u / 1296
    (s - set width, u - no of units)

    Now, we go on to explaining what the S-needle does.
    It's used for modifying (adding/subtracting) the width of a character
    to make it wider or narrower, if it's needed (for example, looser or
    tighter spaces when justifying a line).

    When S is disengaged (e.g. G5), the lower transfer wedge (62D)
    is in action. The justification wedges (10D, 11D) have nothing to do,
    and the character width depends solely on the matrix's row and its
    corresponding unit value.

    Suppose we're using a S5 wedge, and the unit values are as follows:
    row   1 2 3 4 5 6 7 8  9  10 11 12 13 14 15 16
    units 5 6 7 8 9 9 9 10 10 11 12 13 14 15 18 18
    (unless unit-shift is engaged)

    The S5 wedge moves with a matrix case, and for row 1, the characters
    will be 5 units wide. So, the width will be:
    W(5u) = setWidth * 5/1296 = 0.003858" * setWidth.

    Now, we want to cast the character with the S-needle.
    Instead of the lower transfer wedge 62D, the upper transfer wedge 52D
    together with justification wedges 10D & 11D affect the character's
    width. The 10D is a coarse justification wedge and adds/subtracts
    0.0075" per step; the 11D is a fine justification wedge and changes
    width by 0.0005" peru step. The wedges can have one of 15 positions.

    Notice that 0.0075 = 15 x 0.0005 (so, 0.0005 at 15 equals 0.0075 at 1).
    Position 0 or >15 is not possible.S

    Also notice that 0.0005" precision would mean a resolution of 2000dpi -
    beat that, Hewlett-Packard! :).

    Now, we can divide the character's width in inches by by 0.0005
    (or multiply by 2000) and we get a number of 0005 wedge steps
    to cast the character with the S needle. It'll probably be more than
    15, so we need to floor-divide the number to get 0075 wedge steps,
    and modulo-divide it to get 0005 steps:

    steps = W * 2000          (round that to integer)
    steps0075 = steps // 15   (floor-divide)
    steps0005 = steps % 15    (modulo-divide)

    The equivalent 0005 and 0075 wedge positions for a 5-unit character
    in the 1st row (if we decide to cast it with the S-needle) will be:

    steps = 5/1296 * 2000 * setWidth

    (so it is proportional to set width).
    For example, consider the 5 unit 12 set type, and we have:

    steps = 5 * 12 * 2000 / 1296 = 92.6
    so, steps = 92
    steps // 15 = 6
    steps % 15 = 2

    So, the 0075 wedge will be at pos. 6 and 0005 will be at 3.

    If any of the wedge step numbers is 0, set 1 instead (a wedge must
    be in position 1...15).
    """

    steps = 2000/1296 * setWidth * units
    steps = int(steps)
    steps0075 = steps // 15
    steps0005 = steps % 15
    if not steps0075:
      steps0075 = 1
    if not steps0005:
      steps0005 = 1
    return [steps0075, steps0005]

  
  def calculate_line_length(self):
    """calculate_line_length():

    Calculates the line length in Monotype fundamental (1-set) units.
    The "length" parameter is in British pica (0.1667") by default,
    but this can be changed with the "measurement" parameter.
    """

    """Check if the measurement is one of the following:
    britPica, amerPica, cicero
    If not, throw an error.
    """

    inchWidth = {
               'britPica' : 0.1667,
               'amerPica' : 0.1660,
               'cicero'   : 0.1776,
               'mm'       : 0.03937,
               'cm'       : 0.3937,
               'in'       : 1
              }
    if self.measurement not in inchWidth:
      """Nothing to do - return False:"""
      return False

    """Base em width is a width (in inches) of a single em -
    which, by the Monotype convention, is defined as 18 units 12 set.

    Use American pica (0.166") value if specified; other systems
    use British pica (0.1667").
    """
    
    if self.measurement == 'amerPica':
      baseEmWidth = inchWidth['amerPica']
    else:
      baseEmWidth = inchWidth['britPica']

    """To calculate the inch width of a fundamental unit (1-unit 1-set),
    we need to divide the (old or new) pica length in inches by 12*18 = 216:
    """
    fundamentalUnitWidth = baseEmWidth / 216

    """Convert the line length in picas/ciceros to inches:"""
    inchLineLength = self.lineLength * inchWidth[self.measurement]

    """Now, we need to calculate how many units of a given set
    the row will contain. Round that to an integer and return the result.
    """
    self.singleSetUnitLineLength = round(
                                   inchLineLength / fundamentalUnitWidth
                                   )
    
    
  def calculate_units(self):
    """calculate_units:
    
    Calculates line length in 1-set units, and if the set number is given,
    calculates in multi-set units as well.
    """
    
    if self.measurement and self.lineLength:
      self.calculate_line_length()
    else:
      self.UI.notify_user('Line length and meas. units not specified!')
      time.sleep(1)      
      self.main_menu()
    
    """Calculate the multi-set unit value:"""
    if self.setWidth:
      self.multiSetUnitLineLength = round( self.singleSetUnitLineLength 
                                                        / self.setWidth 
                                          )


  @staticmethod
  def calculate_space_width(spaces, unitsLeft):
    """
    Divides the remaining length of line by the number of spaces in line.
    Rounds the result down.
    The min space width is 4 units wide; if the result is smaller,
    the function returns 4 units.
    """
    spaceWidth = unitsLeft % spaces
    if spaceWidth < 4:
      spaceWidth = 4
    return spaceWidth


  def __exit__(self, *args):
    self.UI.debug_info('Exiting typesetting job context.')
    pass



class Inventory(object):
  """A "job" class for configuring the Monotype workshop inventory:

  -wedges
  -diecases
  -diecase layouts.
  """

  def __init__(self):
    pass

  def __enter__(self):
    self.UI.debug_info('Entering inventory management job context...')
    return self

  """Placeholders for functionality not implemented yet:"""
  def list_diecases(self):
    pass
  def show_diecase_layout(self):
    pass
  def add_diecase(self):
    pass
  def edit_diecase(self):
    pass
  def clear_diecase(self):
    pass
  def delete_diecase(self):
    pass


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
    Let's define unit values for some known wedges.
    This is a dictionary, so you get values (string)
    by referring via key (string), feel free to add any unit values
    for the wedges not listed.

    This data will be useful when adding a wedge. The setup program
    will look up a wedge by its name, then get unit values.

    The MONOSPACE wedge is a special wedge, where all steps have
    the same unit value of 9. It is used for casting constant-width
    (monospace) type, like the typewriters have. You could even cast
    from regular matrices, provided that you use 0005 and 0075 wedges
    to add so many units that you can cast wide characters
    like "M", "W" etc. without overhang. You'll get lots of spacing
    between narrower characters, because they'll be cast on a body
    wider than necessary.
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
    while not wedgeName:
      wedgeName = self.UI.enter_data(
                                     'Enter the wedge name, e.g. S5 '
                                     '(very typical, default): '
                                    )
      if wedgeName == '':
        wedgeName = 'S5'
      elif wedgeName[0].upper() != 'S' and wedgeName.isdigit():
        wedgeName = 'S' + wedgeName
      wedgeName = wedgeName.upper()

    """
    Enter a set width, float. If the width ends with "E", then
    it's a wedge for European foundries with 1.667" (British) pica.
    E will be stripped, and the program will set the wedge as British
    pica.

    Otherwise, user can choose if it's American (0.166") or British pica.
    """
    while not setWidth:
      setWidth = self.UI.enter_data(
                                    'Enter the wedge set width as decimal, '
                                    'e.g. 9.75E: '
                                   )

      """Determine if it's a British pica wedge - E is present:"""
      if setWidth[-1].upper() == 'E':
        setWidth = setWidth[:-1]
        britPica = True
      else:
        """Let user choose if it's American or British pica:"""
        options = { 'A' : False, 'B' : True }
        message = '[A]merican (0.1660"), or [B]ritish (0.1667") pica? '
        choice = self.UI.simple_menu(message, options).upper()
        britPica = options[choice]
      try:
        setWidth = float(setWidth)
      except ValueError:
        setWidth = ''
        """Try again."""

    """Enter the wedge unit values for steps 1...15 (and optionally 16):"""
    while not steps:
      """First, check if we've got this wedge in our program:"""
      try:
        rawSteps = wedgeData[wedgeName]
      except (KeyError, ValueError):
        """No wedge - enter data:"""
        rawSteps = self.UI.enter_data(
                        'Enter the wedge unit values for steps 1...16, '
                        'separated by commas. If empty, entering values '
                        'for wedge S5 (very common): '
                        )
        if not rawSteps:
          rawSteps = wedgeData['S5']
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
        self.UI.notify_user(
             'Warning - the wedge you entered has less than 15 steps! \n'
             'This is almost certainly a mistake.\n'
             )
      elif len(steps) > 16:
        self.UI.notify_user(
              'Warning - the wedge you entered has more than 16 steps! \n'
              'This is almost certainly a mistake.\n'
             )
      else:
        self.UI.notify_user('The wedge has ', len(steps), 'steps. That is OK.')


    """Display a summary:"""
    summary = {
               'Wedge' : wedgeName,
               'Set width' : setWidth,
               'British pica wedge?' : britPica
              }
    for parameter in summary:
      self.UI.notify_user(parameter, ':', summary[parameter])

    """Loop over all unit values in wedge's steps and display them:"""
    for i, step in zip(range(len(steps)), steps):
      self.UI.notify_user('Step', i+1, 'unit value:', step, '\n')

    def commit_wedge():
      if self.database.add_wedge(wedgeName, setWidth, britPica, steps):
        self.UI.notify_user('Wedge added successfully.')
      else:
        self.UI.notify_user('Failed to add wedge!')

    def reenter():
      self.UI.enter_data('Enter parameters again from scratch... ')
      self.add_wedge()


    message = (
               '\nCommit wedge to database? \n'
               '[Y]es / [N]o (enter values again) / return to [M]enu: '
              )
    options = { 'Y' : commit_wedge, 'N' : reenter, 'M' : self.main_menu }
    ans = self.UI.simple_menu(message, options).upper()
    options[ans]()


  def delete_wedge(self):
    """Used for deleting a wedge from database."""
    self.list_wedges()
    ID = self.UI.enter_data('Enter the wedge ID to delete: ')
    if ID.isdigit():
      ID = int(ID)
      if self.database.delete_wedge(ID):
        self.UI.notify_user('Wedge deleted successfully.')
    else:
      self.UI.notify_user('Wedge name must be a number!')


  def list_wedges(self):
    """lists all wedges we have"""
    self.database.list_wedges()


  def main_menu(self):

    options = {
               1 : 'List matrix cases',
               2 : 'Show matrix case layout',
               3 : 'Add a new, empty matrix case',
               4 : 'Edit matrix case layout',
               5 : 'Clear matrix case layout',
               6 : 'Delete matrix case',
               7 : 'List wedges',
               8 : 'Add wedge',
               9 : 'Delete wedge',
               0 : 'Exit program'
              }

    commands = {
                1 : self.list_diecases,
                2 : self.show_diecase_layout,
                3 : self.add_diecase,
                4 : self.edit_diecase,
                5 : self.clear_diecase,
                6 : self.delete_diecase,
                7 : self.list_wedges,
                8 : self.add_wedge,
                9 : self.delete_wedge,
                0 : self.UI.exit_program
               }

    choice = self.UI.menu (options,
          header = ('Setup utility for rpi2caster CAT.\nMain menu:'),
          footer = '')

    """Execute it!"""
    with self.database:
      commands[choice]()
    self.UI.hold_on_exit()
    self.main_menu()


  def __exit__(self, *args):
    self.UI.debug_info('Exiting inventory management job context.')
    pass



class Monotype(object):
  """Monotype(job, name, confFilePath):

  A class which stores all methods related to the interface and
  caster itself.

  This class MUST be instantiated with a caster name, and a
  database object.

  No static methods or class methods here.
  """

  def __init__(self, name='Monotype'):
    """Creates a caster object for a given caster name:"""
    self.name = name

    """Initialize the interface as non-configured..."""
    self.configured = False


  def __enter__(self):
    """Run the setup when entering the context:"""
    self.UI.debug_info('Entering caster/interface context...')

    """Configure the interface if it needs it:"""
    if not self.configured:
      self.caster_setup()
    return self


  def caster_setup(self):
    """Setup routine:

    Sets up initial default parameters for caster & interface:
    caster - "Monotype" (if no name is given),
    interface ID 0,
    unit-adding disabled,
    diecase format 15x17.
    """

    """Default caster parameters:"""
    self.interfaceID = 0
    self.unitAdding = 0
    self.diecaseSystem = 'norm17'

    """Default interface parameters:"""
    self.emergencyGPIO = 18
    self.photocellGPIO = 24
    self.mcp0Address = 0x20
    self.mcp1Address = 0x21
    self.pinBase = 65
    self.signalsArrangement = ('1,2,3,4,5,6,7,8,9,10,11,12,13,14,0005,'
                               '0075,A,B,C,D,E,F,G,H,I,J,K,L,M,N,S,O15')

    """
    Next, this method reads caster data from database and fetches
    a list of caster parameters:
    [diecaseFormat, unitAdding, interfaceID].

    In case there is no data, the function will run on default settings.
    """
    settings = self.config.get_caster_settings(self.name)
    if settings:
      [self.unitAdding, self.diecaseSystem, self.interfaceID] = settings

    """When debugging, display all caster info:"""

    self.UI.debug_info('\nCaster parameters:\n')
    output = {
              'Using caster name: '           : self.name,
              'Diecase system: '              : self.diecaseSystem,
              'Has unit-adding attachement? ' : self.unitAdding,
              'Interface ID: '                : self.interfaceID
             }
    for parameter in output:
      self.UI.debug_info(parameter, output[parameter])

    """
    Then, the interface ID is looked up in the database, and interface
    parameters are obtained. The program tries to override defaults
    with the parameters from conffile.
    The parameters will affect the whole object created with this class.
    """
    interfaceSettings = self.config.get_interface_settings(self.interfaceID)
    if interfaceSettings:
      [self.emergencyGPIO, self.photocellGPIO,
      self.mcp0Address, self.mcp1Address,
      self.pinBase, self.signalsArrangement] = interfaceSettings

    """Print the parameters for debugging:"""
    self.UI.debug_info('\nInterface parameters:\n')
    output = {
              'Emergency button GPIO: ' : self.emergencyGPIO,
              'Photocell GPIO: ' : self.photocellGPIO,
              '1st MCP23017 I2C address: ' : self.mcp0Address,
              '2nd MCP23017 I2C address: ' : self.mcp1Address,
              'MCP23017 pin base for GPIO numbering: ' : self.pinBase,
              'Signals arrangement: ' : self.signalsArrangement
             }
    for parameter in output:
      self.UI.debug_info(parameter, output[parameter])

    """Now do the input configuration:

    We need to set up the sysfs interface before (powerbuttond.py -
    a daemon running on boot with root privileges takes care of it).
    """
    gpioSysfsPath = '/sys/class/gpio/gpio%s/' % self.photocellGPIO
    self.gpioValueFileName = gpioSysfsPath + 'value'
    self.gpioEdgeFileName  = gpioSysfsPath + 'edge'

    """Check if the photocell GPIO has been configured - file can be read:"""
    if not os.access(self.gpioValueFileName, os.R_OK):
      self.UI.notify_user(
           self.gpioValueFileName, ': file does not exist or cannot be read.',
          'You must export the GPIO no', self.photocellGPIO, 'as input first!'
          )
      self.UI.exit_program()


    """Ensure that the interrupts are generated for photocell GPIO
    for both rising and falling edge:"""
    with open(self.gpioEdgeFileName, 'r') as edgeFile:
      if (edgeFile.read()[:4] != 'both'):
        self.UI.notify_user(
            '%s: file does not exist, cannot be read, '
            'or the interrupt on GPIO no %i is not set to "both". '
            'Check the system config.'
             % (self.gpioEdgeFileName, self.photocellGPIO)
            )
        self.UI.exit_program()

    """Output configuration:

    Setup the wiringPi MCP23017 chips for valve outputs:
    """
    wiringpi.mcp23017Setup(self.pinBase,      self.mcp0Address)
    wiringpi.mcp23017Setup(self.pinBase + 16, self.mcp1Address)

    pins = range(self.pinBase, self.pinBase + 32)

    """Set all I/O lines on MCP23017s as outputs - mode = 1"""
    for pin in pins:
      wiringpi.pinMode(pin,1)

    """Make a nice list out of signal arrangement string:"""
    signalsArrangement = self.signalsArrangement.split(',')

    """Assign wiringPi pin numbers on MCP23017s to the Monotype
    control signals:
    """
    self.wiringPiPinNumber = dict(zip(signalsArrangement, pins))

    """Mark the caster as configured:"""
    self.configured = True

    """Wait for user confirmation:"""
    self.UI.debug_enter_data('Caster configured. Press [Enter] to continue... ')



  def detect_rotation(self):
    """
    detect_rotation():

    Checks if the machine is running by counting pulses on a photocell
    input. One pass of a while loop is a single cycle. If cycles_max
    value is exceeded in a time <= time_max, the program assumes that
    the caster is rotating and it can start controlling the machine.
    """
    cycles = 0
    cycles_max = 3
    """Let's give it 30 seconds timeout."""
    time_start = time.time()
    time_max = 30

    """
    Check for photocell signals, keep checking until max time is exceeded
    or target number of cycles is reached:
    """
    with open(self.gpioValueFileName, 'r') as gpiostate:
      while time.time() <= time_start + time_max and cycles <= cycles_max:
        photocellSignals = select.epoll()
        photocellSignals.register(gpiostate, select.POLLPRI)
        events = photocellSignals.poll(0.5)
        """Check if the photocell changes state at all:"""
        if events:
          gpiostate.seek(0)
          photocellState = int(gpiostate.read())
          previousState = 0
          """Cycle between 0 and 1, increment the number
          of passed cycles:
          """
          if photocellState == 1 and previousState == 0:
            previousState = 1
            cycles += 1
          elif photocellState == 0 and previousState == 1:
            previousState = 0
      else:
        """In case of cycles exceeded (machine running),
        or timeout (machine stopped):
        """
        if cycles > cycles_max:
          self.UI.notify_user('\nOkay, the machine is running...\n')
          return True
        else:
          self.machine_stopped()
          """Recurse:"""
          self.detect_rotation()


  def send_signals_to_caster(self, signals, machineTimeout=5):
    """
    send_signals_to_caster(signals, machineTimeout):

    Checks for the machine's rotation, sends the signals (activates
    solenoid valves) after the caster is in the "air bar down" position.

    If no machine rotation is detected (photocell input doesn't change
    its state) during machineTimeout, calls a function to ask user
    what to do (can be useful for resuming casting after manually
    stopping the machine for a short time - not recommended as the
    mould cools down and type quality can deteriorate).

    When casting, the pace is dictated by the caster and its RPM. Thus,
    we can't arbitrarily set the intervals between valve ON and OFF
    signals. We need to get feedback from the machine, and we can use
    contact switch (unreliable in the long run), magnet & reed switch
    (not precise enough) or a photocell + LED (very precise).
    We can use a paper tower's operating lever for obscuring the sensor
    (like John Cornelisse did), or we can use a partially obscured disc
    attached to the caster's shaft (like Bill Welliver did).
    Both ways are comparable; the former can be integrated with the
    valve block assembly, and the latter allows for very precise tweaking
    of duty cycle (bright/dark area ratio) and phase shift (disc's position
    relative to 0 degrees caster position).
    """
    with open(self.gpioValueFileName, 'r') as gpiostate:
      po = select.epoll()
      po.register(gpiostate, select.POLLPRI)
      previousState = 0

      """
      Detect events on a photocell input, and if a rising or falling edge
      is detected, determine the input's logical state (high or low).
      If high - check if it was previously low to be sure. Then send
      all signals passed as an argument (tuple or list).
      In the next cycle, turn all the valves off and exit the loop.
      Set the previous state each time the valves are turned on or off.
      """
      while True:
        """polling for interrupts"""
        events = po.poll(machineTimeout)
        if events:
          """be sure that the machine is working"""
          gpiostate.seek(0)
          photocellState = int(gpiostate.read())

          if photocellState == 1 and previousState == 0:
            """Now, the air bar on paper tower would go down -
            we got signal from photocell to let the air in:
            """
            self.activate_valves(signals)
            previousState = 1

          elif photocellState == 0 and previousState == 1:
            """Air bar on paper tower goes back up -
            end of "air in" phase, turn off the valves:
            """
            self.deactivate_valves()
            previousState = 0
            break

        else:
          """Ask the user what to do if the machine is stopped
          (no events from the photocell)."""
          self.machine_stopped()


  def activate_valves(self, signals):
    """activate_valves(signals):

    Activates the solenoid valves connected with interface's outputs,
    as specified in the "signals" argument (tuple or list).
    The input array "signals" contains strings, either
    lowercase (a, b, g, s...) or uppercase (A, B, G, S...).
    Do nothing if the function receives an empty sequence, which will
    occur if we cast with the matrix found at position O15.
    """
    if signals:
      for monotypeSignal in signals:
        pin = self.wiringPiPinNumber[monotypeSignal]
        wiringpi.digitalWrite(pin,1)


  def deactivate_valves(self):
    """deactivate_valves():

    Turn all valves off after casting/punching any character.
    Call this function to avoid outputs staying turned on if something
    goes wrong, esp. in case of abnormal program termination.
    """
    for pin in range(self.pinBase, self.pinBase + 32):
      wiringpi.digitalWrite(pin,0)


  def machine_stopped(self):
    """machine_stopped():

    This allows us to choose whether we want to continue, return to menu
    or exit if the machine is stopped during casting.
    """
    def continue_casting():
      """Helper function - continue casting."""
      return True

    options = {
               'C' : continue_casting,
               'M' : self.job.main_menu,
               'E' : self.UI.exit_program
              }
    message = (
               "Machine not running! Check what's going on.\n"
               "[C]ontinue, return to [M]enu or [E]xit program? "
              )
    choice = self.UI.simple_menu(message, options).upper()
    options[choice]()


  def cleanup(self):
    """cleanup():

    Turn all valves off, then set all lines on MCP23017 as inputs.
    """
    self.UI.debug_info('Cleaning up: turning all pins off...')
    for pin in range(self.pinBase, self.pinBase + 32):
      wiringpi.digitalWrite(pin,0)
    """Wait for user confirmation:"""
    self.UI.debug_enter_data('Press [Enter] to continue... ')


  def __exit__(self, *args):
    """On exit, do the cleanup:"""
    self.UI.debug_info('Exiting caster/interface context.')
    self.cleanup()



class Keyboard(object):
  """
  Keyboard is technically a paper tower taken off a keyboard,
  it does not have machine cycle sensor nor emergency stop button,
  but it has 32 valves and an interface to control them.
  """

  def __init__(self, name='Keyboard'):
    """Creates a caster object for a given caster name."""
    self.name = name

    """Initialize the interface as non-configured..."""
    self.configured = False


  def __enter__(self):
    """Run the setup when entering the context:"""
    self.UI.debug_info('Entering keyboard/interface context...')

    """Configure the interface if it needs it:"""
    if not self.configured:
      self.interface_setup()
    return self


  def interface_setup(self):
    """Setup routine:

    Sets up initial default parameters for interface:"""
    self.interfaceID = 0
    self.mcp0Address = 0x20
    self.mcp1Address = 0x21
    self.pinBase = 65
    self.signalsArrangement = ('1,2,3,4,5,6,7,8,9,10,11,12,13,14,0005,'
                               '0075,A,B,C,D,E,F,G,H,I,J,K,L,M,N,S,O15')

    """
    Next, this method reads data from config file and overrides the
    default interface parameters for an object:"""
    settings = self.config.get_settings_from_conffile(self.name)

    """Check if we got anything - if so, set parameters for object:"""
    if settings:
     (self.interfaceID, self.mcp0Address, self.mcp1Address,
      self.pinBase, self.signalsArrangement) = settings

    """Print the parameters for debugging:"""
    self.UI.debug_info('\nInterface parameters:\n')
    output = {
              'Interface ID: ' : self.interfaceID,
              '1st MCP23017 I2C address: ' : self.mcp0Address,
              '2nd MCP23017 I2C address: ' : self.mcp1Address,
              'MCP23017 pin base for GPIO numbering: ' : self.pinBase,
              'Signals arrangement: ' : self.signalsArrangement
             }
    for parameter in output:
      self.UI.debug_info(parameter, output[parameter])

    """Set up the wiringPi MCP23017 chips for valve outputs:"""
    wiringpi.mcp23017Setup(self.pinBase,      self.mcp0Address)
    wiringpi.mcp23017Setup(self.pinBase + 16, self.mcp1Address)

    pins = range(self.pinBase, self.pinBase + 32)

    """Set all I/O lines on MCP23017s as outputs - mode = 1"""
    for pin in pins:
      wiringpi.pinMode(pin,1)

    """Make a nice list out of signal arrangement string:"""
    signalsArrangement = self.signalsArrangement.split(',')

    """Assign wiringPi pin numbers on MCP23017s to the Monotype
    control signals:
    """
    self.wiringPiPinNumber = dict(zip(signalsArrangement, pins))

    """Mark the caster as configured:"""
    self.configured = True

    """Wait for user confirmation:"""
    self.UI.debug_enter_data('Interface configured. Press [Enter] to continue... ')



  def activate_valves(self, signals):
    """activate_valves(signals):

    Activates the solenoid valves connected with interface's outputs,
    as specified in the "signals" argument (tuple or list).
    The input array "signals" contains strings, either
    lowercase (a, b, g, s...) or uppercase (A, B, G, S...).
    Do nothing if the function receives an empty sequence, which will
    occur if we cast with the matrix found at position O15.
    """
    if signals:
      for monotypeSignal in signals:
        pin = self.wiringPiPinNumber[monotypeSignal]
        wiringpi.digitalWrite(pin,1)


  def deactivate_valves(self):
    """deactivate_valves():

    Turn all valves off after casting/punching any character.
    Call this function to avoid outputs staying turned on if something
    goes wrong, esp. in case of abnormal program termination.
    """
    for pin in range(self.pinBase, self.pinBase + 32):
      wiringpi.digitalWrite(pin,0)



  def cleanup(self):
    """cleanup():

    Turn all valves off, then set all lines on MCP23017 as inputs.
    """
    self.UI.debug_info('Cleaning up: turning all pins off...')
    for pin in range(self.pinBase, self.pinBase + 32):
      wiringpi.digitalWrite(pin,0)
    """Wait for user confirmation:"""
    self.UI.debug_enter_data('Press [Enter] to continue... ')


  def __exit__(self, *args):
    """On exit, do the cleanup:"""
    self.UI.debug_info('Exiting keyboard/interface context.')
    self.cleanup()



class MonotypeSimulation(object):
  """MonotypeSimulation:

  A class which allows to test rpi2caster without an actual interface
  or caster. Most functionality will be developped without an access
  to the machine.
  """

  def __init__(self, name='Monotype Simulator'):
    self.name = name

  def __enter__(self):
    self.UI.debug_info('Entering caster/keyboard simulation context...')
    """Display some info"""
    self.UI.notify_user('Using caster name:', self.name)
    self.UI.notify_user('This is not an actual caster or interface. ')
    self.UI.enter_data('Press [ENTER] to continue...')
    self.UI.debugMode = True
    return self


  def send_signals_to_caster(self, signals, machineTimeout=5):
    """
    Just send signals, and wait for feedback from user,
    as we don't have a photocell.
    """
    self.UI.enter_data('Press [ENTER] to simulate sensor going ON')
    self.activate_valves(signals)
    self.UI.enter_data('Press [ENTER] to simulate sensor going OFF')
    self.deactivate_valves()


  def activate_valves(self, signals):
    """If there are any signals, print them out"""
    if len(signals) != 0:
      self.UI.notify_user('The valves:', ' '.join(signals),
                          'would be activated now.')


  def deactivate_valves(self):
    """No need to do anything"""
    self.UI.notify_user('The valves would be deactivated now.')


  def detect_rotation(self):
    """FIXME: implement raw input breaking on timeout"""
    print('Now, the program would check if the machine is rotating.\n')
    #startTime = time.time()
    answer = None
    while answer is None:# and time.time() < (startTime + 5):
      answer = self.UI.enter_data(
                     'Press [ENTER] (to simulate rotation) '
                     'or wait 5sec (to simulate machine off)\n'
                    )
    else:
      self.machine_stopped()
      """Recurse:"""
      self.detect_rotation()


  def machine_stopped(self):
    """machine_stopped():

    This allows us to choose whether we want to continue, return to menu
    or exit if the machine is stopped during casting.
    """
    def continue_casting():
      """Helper function - continue casting."""
      return True

    options = {
               'C' : continue_casting,
               'M' : self.job.main_menu,
               'E' : self.UI.exit_program
              }
    message = (
               "Machine not running! Check what's going on.\n"
               "[C]ontinue, return to [M]enu or [E]xit program? "
              )
    choice = self.UI.simple_menu(message, options).upper()
    options[choice]()


  def __exit__(self, *args):
    self.deactivate_valves()
    self.UI.debug_info('Exiting caster/keyboard simulation context.')
    pass



class Parsing(object):
  """This class contains file- and line-parsing methods.
  It contains static methods to be called by other functions only.
  You cannot instantiate it.
  """


  @staticmethod
  def read_file(filename):
    """Open a file with signals, test if it's readable
    and return its contents:
    """
    try:
      contents = []
      with open(filename, 'r') as inputFile:
        contentsGenerator = inputFile.readlines()
        for line in contentsGenerator:
          contents.append(line)
        return contents
    except IOError:
      print('Error: File cannot be read!')    # rework it to fit a new UI model
      return False


  @staticmethod
  def signals_parser(originalSignals):
    """signals_parser(originalSignals):

    Parses an input string, and returns a list with two elements:

    -the Monotype signals found in a line: A-N, 1-14, 0005, S, 0075.
    -any comments delimited by symbols from commentSymbols list.
    """

    """We need to work on strings. Convert any lists, integers etc."""
    signals = str(originalSignals)

    """This is a comment parser. It looks for any comment symbols
    defined here - e.g. **, *, ##, #, // etc. - and saves the comment
    to return it later on.

    If it's an inline comment (placed after Monotype code combination),
    this combination will be returned for casting.

    If a line in file contains a comment only, returns no combination.

    If we want to cast O15, we have to feed an empty line
    (place the comment above).

    Example:

    ********
    O15 //comment         <-- casts from O+15 matrix, displays comment
                          <-- casts from O+15 matrix
    //comment             <-- displays comment
    0005 5 //comment      <-- sets 0005 justification wedge to 5,
                              turns pump off, displays comment
    """
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



class Casting(object):
  """
  Casting:

  A "job" class. Objects of this class have attributes as follows:
  -caster
  -database
  -UI.

  These attributes need to be set up before casting anything.
  Normally, you instantiate the Session class and it takes care of all
  setup work.

  Ribbon filename is also an object's attribute, but it's usually
  set up via user interaction. You can also feed the filename
  to class on init.

  All methods related to operating a composition caster are here:
  -casting composition and sorts,
  -calibrating the caster,
  -testing the interface,
  -sending an arbitrary combination of signals,
  -casting spaces to heat up the mould.
  """

  def __init__(self, ribbonFile=''):
    self.ribbonFile = ribbonFile


  def __enter__(self):
    self.UI.debug_info('Entering casting job context...')
    return self


  def cast_composition(self):
    """cast_composition()

    Composition casting routine. The input file is read backwards -
    last characters are cast first, after setting the justification.
    """

    """Read the file contents:"""
    contents = Parsing.read_file(self.ribbonFile)

    """If file read failed, end here:"""
    if not contents:
      return False

    """For casting, we need to read the contents in reversed order:"""
    contents = reversed(contents)

    """Display a little explanation:"""
    self.UI.notify_user(
          '\nThe combinations of Monotype signals will be displayed '
          'on screen while the machine casts the type.\n'
          'Turn on the machine and the program will '
          'start automatically.\n'
          )

    """Check if the machine is running - don't do anything when
    it's not rotating yet!"""
    self.caster.detect_rotation()

    """Read the reversed file contents, line by line, then parse
    the lines, display comments & code combinations, and feed the
    combinations to the caster:
    """
    for line in contents:

      """Parse the row, return a list of signals and a comment.
      Both can have zero or positive length."""
      signals, comment = Parsing.signals_parser(line)

      """Print a comment if there is one (positive length)"""
      if len(comment) > 0:
        self.UI.notify_user(comment)

      """Cast an empty line, signals with comment, signals with no comment.
      Don't cast a line with comment alone."""
      if len(comment) == 0 or len(signals) > 0:
        if len(signals) > 0:
          self.UI.notify_user(' '.join(signals))
        else:
          self.UI.notify_user('O+15 - no signals')
        self.caster.send_signals_to_caster(signals)

    """After casting is finished, notify the user:"""
    print('\nCasting finished!')

    """End of function."""


  def line_test(self):
    """line_test():

    Tests all valves and composition caster's inputs to check
    if everything works and is properly connected. Signals will be tested
    in order: 0005 - S - 0075, 1 towards 14, A towards N, O+15, NI, NL,
    EF, NJ, NK, NKJ, MNH, MNK (feel free to add other combinations!)
    """
    self.UI.enter_data(
          'This will check if the valves, pin blocks and 0005, S, '
          '0075 mechanisms are working. Press return to continue... '
         )

    combinations = [
                    ['0005'], ['S'], ['0075'], ['1'], ['2'], ['3'],
                    ['4'], ['5'], ['6'], ['7'], ['8'], ['9'], ['10'],
                    ['11'], ['12'], ['13'], ['14'], ['A'], ['B'],
                    ['C'], ['D'], ['E'], ['F'], ['G'], ['H'], ['I'],
                    ['J'], ['K'], ['L'], ['M'], ['N'], ['O15'],
                    ['N', 'I'], ['N', 'L'], ['N', 'J'], ['N', 'K'], ['E', 'F'],
                    ['N', 'K', 'J'], ['M', 'N', 'H'], ['M', 'N', 'K']
                   ]

    """Send all the combinations to the caster, one by one:"""
    for combination in combinations:
      self.UI.notify_user(' '.join(combination))
      self.caster.send_signals_to_caster(combination, 120)

    self.UI.notify_user('\nTesting finished!')

    """End of function."""


  def cast_sorts(self):
    """cast_sorts():

    Sorts casting routine, based on the position in diecase.
    Ask user about the diecase row & column, as well as number of sorts.
    """
    self.UI.clear()
    self.UI.notify_user('Calibration and Sort Casting:\n\n')
    signals = self.UI.enter_data(
                    'Enter column and row symbols '
                    '(default: G 5, spacebar if O-15)\n '
                   )
    if not signals:
      signals = 'G5'

    """
    Parse the signals and return a list containing the parsed
    signals and the comments:
    """
    [parsedSignals, comment] = Parsing.signals_parser(signals)

    """
    O15 yields no signals, but we may want to cast it - check if we
    entered spacebar. If parsing yields no signals (for example,
    user entered a string with row > 16 or column > O), check
    if user entered spacebar. If it's not the case, user has to
    enter the combination again.
    """
    if not parsedSignals and signals != ' ':
      self.UI.notify_user('\nRe-enter the sequence')
      time.sleep(1)
      self.cast_sorts()
    """Ask for number:"""
    n = self.UI.enter_data(
              '\nHow many sorts do you want to cast? (default: 10) \n'
             )

    """Default to 10 if user enters non-positive number or letters:"""
    if not n.isdigit() or int(n) < 0:
      n = '10'
    n = int(n)
    self.UI.notify_user("\nWe'll cast it %i times.\n" % n)

    """Warn if we want to cast too many sorts from a single matrix"""
    if n > 10:
      self.UI.notify_user(
            'Warning: you want to cast a single character more than '
            '10 times. This may lead to matrix overheating!\n'
           )

    """Use a simple menu to ask user if the entered parameters are correct"""

    def cast_it():
      """Subroutine to cast chosen signals and/or repeat."""
      self.cast_code(parsedSignals, n)
      options = {
                 'R' : cast_it,
                 'C' : self.cast_sorts,
                 'M' : self.main_menu,
                 'E' : self.UI.exit_program
                }
      message = ('\nCasting finished!\n '
                 '[R]epeat sequence, [C]hange code, [M]enu or [E]xit? ')
      choice = self.UI.simple_menu(message, options).upper()
  
      """Execute choice:"""
      options[choice]()

    """Prmeters chosen. Ask what to do:"""
    options = {
               'O' : cast_it,
               'R' : self.cast_sorts,
               'M' : self.main_menu,
               'E' : self.UI.exit_program
              }
    message = '[O]K, [R]e-enter, [M]enu or [E]xit program? '
    choice = self.UI.simple_menu(message, options).upper()

    """Execute choice:"""
    options[choice]()


  def cast_code(self, combination, n=5, pos0075=3, pos0005=8):
    """
    Casts n sorts from combination of signals (list),
    with correction wedges if S needle is in action.

    By default, it sets 0075 wedge to 3 and 0005 wedge to 8 (neutral).
    Determines if single justification (0075 only) or double
    justification (0005 + 0075) is used.

    Turns the pump on and off and casts the characters.
    """
    pos0005 = str(pos0005)
    pos0075 = str(pos0075)

    """Check if the machine is running first:"""
    self.UI.notify_user('Start the machine...')
    self.caster.detect_rotation()

    """Cast the sorts: turn on the pump first (and line to the galley)."""
    self.UI.notify_user('Starting the pump...')
    self.caster.send_signals_to_caster(['0075', '0005', pos0005])

    """If pos0005 != pos0075, we need double justification:"""
    if pos0005 != pos0075:
      self.caster.send_signals_to_caster(['0075', pos0075])

    """Start casting characters"""
    self.UI.notify_user('Casting characters...')

    """Cast n combinations of row & column, one by one"""
    for i in range(n):
      if len(combination) > 0:
        self.UI.notify_user(' '.join(combination))
      else:
        self.UI.notify_user('O+15 - no signals')
      self.caster.send_signals_to_caster(combination)

    """Put the line to the galley:"""
    self.UI.notify_user('Putting line to the galley...')
    self.caster.send_signals_to_caster(['0005', '0075'])

    """After casting sorts we need to stop the pump"""
    self.UI.notify_user('Stopping the pump...')
    self.caster.send_signals_to_caster(['0005'])


  def send_combination(self):
    """send_combination():

    This function allows us to give the program a specific combination
    of Monotype codes, and will keep the valves on until we press return
    (useful for calibration). It also checks the signals' validity.
    """

    """Let the user enter a combo:"""
    signals = ''
    while signals == '':
      signals = self.UI.enter_data(
                      'Enter the signals to send to the machine: '
                      )

    """Parse the combination, get the signals (first item returned
    by the parsing function):"""
    combination = Parsing.signals_parser(signals)[0]

    """Check if we get any signals at all, if so, turn the valves on:"""
    if combination:
      self.UI.notify_user(' '.join(combination))
      self.caster.activate_valves(combination)

    """Wait until user decides to stop sending those signals to valves:"""
    self.UI.enter_data('Press [Enter] to stop. ')
    self.caster.deactivate_valves()
    """End of function"""


  def align_wedges(self, space='G5'):
    """align_wedges(space='G5'):

    Allows to align the justification wedges so that when you're
    casting a 9-unit character with the S-needle at 0075:3 and 0005:8
    (neutral position), the  width is the same.

    It works like this:
    1. 0075 - turn the pump on,
    2. cast 10 spaces from the specified matrix (default: G9),
    3. put the line to the galley & set 0005 to 8, 0075 to 3, pump on,
    4. cast 10 spaces with the S-needle from the same matrix,
    5. put the line to the galley, then 0005 to turn the pump off.
    """

    """Print some info for the user:"""
    self.UI.notify_user(
          'Transfer wedge calibration:\n\n'
          'This function will cast 10 spaces, then set the correction '
          'wedges to 0075:3 and 0005:8, \nand cast 10 spaces with the '
          'S-needle. You then have to compare the length of these two '
          'sets. \nIf they are identical, all is OK. '
          'If not, you have to adjust the 52D wedge.\n\n'
          'Turn on the machine...'
          )

    """Parse the space combination:"""
    space = Parsing.signals_parser(space)[0]

    """Cast 10 spaces without S:"""
    self.UI.notify_user('Now casting with a normal wedge only.')
    self.cast_code(space, 10)

    """Cast 10 spaces with the S-needle:"""
    self.UI.notify_user('Now casting with justification wedges...')
    self.cast_code(space + ['S'], 10)

    """Finished. Return to menu."""
    self.UI.notify_user(
         'Procedure finished. Compare the lengths and adjust if needed.'
         )


  def main_menu(self):
    """Calls self.UI.menu() with options,
    a header and a footer.

    Options: {option_name : description}
    """
    options = {
               1 : 'Load a ribbon file',
               2 : 'Cast composition',
               3 : 'Cast sorts',
               4 : 'Test the valves and pinblocks',
               5 : 'Lock the caster on a specified diecase position',
               6 : 'Calibrate the 0005 and 0075 wedges',
               0 : 'Exit program'
              }


    """Declare local functions for menu options:"""
    def choose_ribbon_filename():
      self.ribbonFile = self.UI.enter_input_filename()
      self.main_menu()

    def debug_notice():
      """Prints a notice if the program is in debug mode:"""
      if self.UI.debugMode:
        return('\n\nThe program is now in debugging mode!')
      else:
        return ''

    def additional_info():
      """Displays additional info as a main menu footer.

      Start with empty list:"""
      info = []

      """Add ribbon filename, if any:"""
      if self.ribbonFile:
        info.append('Input file name: ' + self.ribbonFile)

      """Add a caster name:"""
      info.append('Using caster: ' + self.caster.name)

      """Convert it all to a multiline string:"""
      return '\n'.join(info)


    """Commands: {option_name : function}"""
    commands = {
                1 : choose_ribbon_filename,
                2 : self.cast_composition,
                3 : self.cast_sorts,
                4 : self.line_test,
                5 : self.send_combination,
                6 : self.align_wedges,
                0 : self.UI.exit_program
               }

    choice = self.UI.menu( options,
              header = (
                        'rpi2caster - CAT (Computer-Aided Typecasting) '
                        'for Monotype Composition or Type and Rule casters.'
                        '\n\n'
                        'This program reads a ribbon (input file) '
                        'and casts the type on a Composition Caster, \n'
                        'or punches a paper tape with a paper tower '
                        'taken off a Monotype keyboard.'
                       ) + debug_notice() + '\n\nMain Menu:',

              footer = additional_info()
              )


    """Call the function and return to menu.
    Use caster context for everything that needs it:"""
    if choice in [0, 1]:
      commands[choice]()
    else:
      with self.caster:
        commands[choice]()
        self.UI.hold_on_exit()
    self.main_menu()


  def __exit__(self, *args):
    self.UI.debug_info('Exiting casting job context.')
    pass



class RibbonPunching(object):
  """Job class for punching the paper tape (ribbon)."""

  def __init__(self):
    pass

  def __enter__(self):
    self.UI.debug_info('Entering ribbon punching job context...')
    return self


  def punch_composition(self):
    """punch_composition():

    When punching, the input file is read forwards. An additional line
    (O+15) is switched on for operating the paper tower, if less than
    two signals are found in a sequence.
    """

    """Read the file contents:"""
    contents = Parsing.read_file(self.ribbonFile)

    """If file read failed, end here:"""
    if not contents:
      return False

    """Wait until the operator confirms.

    We can't use automatic rotation detection like we do in
    cast_composition, because keyboard's paper tower doesn't run
    by itself - it must get air into tubes to operate, punches
    the perforations, and doesn't give any feedback.
    """
    self.UI.notify_user(
              '\nThe combinations of Monotype signals will be displayed '
              'on screen while the paper tower punches the ribbon.\n'
              )
    self.UI.enter_data(
           '\nInput file found. Turn on the air, fit the tape '
           'on your paper tower and press return to start punching.\n'
           )
    for line in contents:

      """
      Parse the row, return a list of signals and a comment.
      Both can have zero or positive length.
      """
      signals, comment = Parsing.signals_parser(line)

      """Print a comment if there is one - positive length"""
      if comment:
        self.UI.notify_user(comment)

      """
      Punch an empty line, signals with comment, signals with
      no comment.

      Don't punch a line with nothing but comments
      (prevents erroneous O+15's).
      """
      if not comment or signals:

        """Determine if we need to turn O+15 on"""
        if len(signals) < 2:
          signals += ('O15',)
        self.UI.notify_user(' '.join(signals))
        self.caster.activate_valves(signals)         # keyboard?

        """The pace is arbitrary, let's set it to 200ms/200ms"""
        time.sleep(0.2)
        self.caster.deactivate_valves()              # keyboard?
        time.sleep(0.2)

    """After punching is finished, notify the user:"""
    self.UI.notify_user('\nPunching finished!')

    """End of function."""


  def __exit__(self, *args):
    self.UI.debug_info('Exiting ribbon punching job context.')
    pass



class TextUI(object):
  """TextUI(job):

  Use this class for creating a text-based console user interface.

  A caster object must be created before instantiating this class.

  Suitable for controlling a caster from the local terminal or via SSH,
  supports UTF-8 too.
  """

  def __init__(self, debugMode=False):
    """Get the debug-mode from input parameters:"""
    self.debugMode = debugMode


  def __enter__(self):
    """Print some debug info:"""
    self.debug_info('Entering text UI context...')

    """Try to call main menu for a job.
    Display a message when user presses ctrl-C.
    """
    try:
      self.job.main_menu()
    except KeyboardInterrupt:
      print('\nUser pressed ctrl-C. Exiting.')
    finally:
      print('\nGoodbye!\n')


  def tab_complete(text, state):
    """tab_complete(text, state):

    This function enables tab key auto-completion when you
    enter the filename.
    """
    return (glob.glob(text+'*')+[None])[state]
  readline.set_completer_delims(' \t\n;')
  readline.parse_and_bind('tab: complete')
  readline.set_completer(tab_complete)


  def menu(self, options, header='', footer=''):
    """menu(
            options={'foo':'bar','baz':'qux'}
            header=foo,
            footer=bar):

    A menu which takes three arguments:
    header - string to be displayed above,
    footer - string to be displayed below.,

    After choice is made, executes the command.


    Set up vars for conditional statements,
    and lists for appending new items.

    choices - options to be entered by user,
    commands - commands to be executed after option is chosen,
    pauses - flags indicating whether the program will be paused
            on return to menu (waiting for user to press return):
    """
    yourChoice = ''
    choices = []

    """Clear the screen, display header and add two empty lines:"""
    self.clear()
    if header:
      print header
      print

    """Display all the options; we'll take care of 0 later:"""
    for choice in options:
       if choice != 0:
        """Print the option choice and displayed text:"""
        print '\t', choice, ' : ', options[choice], '\n'

        """Add this option to possible choices.
        We need to convert it to string first:"""
        choices.append(str(choice))

    try:
      """If an option "0." is available, print it as a last one:"""
      optionNumberZero = options[0]
      print '\n'
      print '\t', 0, ' : ', optionNumberZero
      choices.append('0')
    except KeyError:
      pass

    """Print footer, if defined:"""
    if footer:
      print('')
      print footer
    print('\n')

    """Ask for user input:"""
    while yourChoice not in choices:
      yourChoice = raw_input('Your choice: ')
    else:
      """Valid option is chosen, return integer if options were numbers,
      else return string:
      """
      try:
        return int(yourChoice)
      except ValueError:
        return yourChoice


  def clear(self):
    """Clear screen"""
    os.system('clear')


  def notify_user(self, *args):
    """Display info for the user - print all in one line:"""
    for arg in args:
      print arg,
    """Newline:"""
    print


  def debug_info(self, *args):
    """Print debug message to screen if in debug mode:"""
    if self.debugMode:
      for arg in args:
        print arg,
      """Newline:"""
      print


  def debug_enter_data(self, message):
    if self.debugMode:
      return raw_input(message)


  def exception_handler(self):
    """Raise caught exceptions in debug mode:"""
    if self.debugMode:
      print sys.exc_info()


  def enter_data(self, message):
    """Let user enter the data:"""
    return raw_input(message)


  def enter_input_filename(self):
    """Enter the input filename; check if the file is readable"""
    fn = raw_input('\n Enter the input file name: ')
    fn = os.path.realpath(fn)
    try:
      with open(fn, 'r'):
        return fn
    except IOError:
      raw_input('Wrong filename or file not readable!')
      return ''
  
  def enter_output_filename(self):
    """Enter the output filename; no check here:"""
    fn = raw_input('\n Enter the output file name: ')
    fn = os.path.realpath(fn)
    return fn


  def hold_on_exit(self):
      raw_input('Press [Enter] to return to main menu...')


  def simple_menu(self, message, options):
    """A simple menu where user is asked what to do.
    Wrong choice points back to the menu.

    Message: string displayed on screen;
    options: a list or tuple of strings - options.
    """
    ans = ''
    while ans.upper() not in options and ans.lower() not in options:
      ans = raw_input(message)
    return ans


  def exit_program(self):
    """
    All objects will call this method whenever they want to exit program.
    This is because we may do something specific in a different UI.
    """
    exit()


  def __exit__(self, *args):
    self.debug_info('Exiting text UI context.')
    pass



class WebInterface(object):
  """WebInterface:

  Use this class for instantiating text-based console user interface"""

  def __init__(self):
    pass

  def __enter__(self):
    return self

  def webUI(self):
    """This is a placeholder for web interface method. Nothing yet..."""
    pass

  def __exit__(self, *args):
    pass



class Session(object):
  """Class for injecting dependencies for objects."""
  def __init__(self, job=Casting(), caster=Monotype(), config=Config(),
                     UI=TextUI(), database=Database()):


    """Set dependencies as object attributes.
    Make sure we've got an UI first:"""
    try:
      assert (
              isinstance(UI, TextUI)
              or
              isinstance(UI, WebInterface)
             )
    except NameError:
      print('Error: User interface not specified!')
      exit()
    except AssertionError:
      print('Error: User interface of incorrect type!')
      exit()


    """Make sure database and config are of the correct type:"""
    try:
      assert isinstance(database, Database)
      assert isinstance(config, Config)
    except NameError:
      """Not set up? Move on."""
      pass
    except AssertionError:
      """We can be sure that UI can handle this now..."""
      UI.notify_user('Invalid config and/or database!')
      UI.exit_program()


    """We need a job: casting, punching, setup, typesetting..."""
    try:
      """Any job (casting, punching, setup) needs UI and database:"""
      job.UI = UI
      job.database = database
      """UI needs job context:"""
      UI.job = job
    except NameError:
      UI.notify_user('Job not specified!')


    """Database needs UI to communicate messages to user:"""
    database.UI = UI
    """Database needs config to get the connection parameters:"""
    database.config = config
    """Config needs UI to communicate debug/error messages to user:"""
    config.UI = UI


    """Assure that ribbon punching is done with keyboard
    (or that we're using a simulator - for testing etc.):"""
    try:
      if isinstance(job, RibbonPunching):
        assert (
                isinstance(keyboard, Keyboard)
                or
                isinstance(keyboard, MonotypeSimulation)
               )
        """Set up mutual dependencies:"""
        job.keyboard = keyboard
        keyboard.UI = UI
        keyboard.job = job
        keyboard.config = config
    except (AssertionError, NameError, AttributeError):
      UI.notify_user('You need a proper keyboard to punch a ribbon.')
      UI.exit_program()


    """Assure that we're using a caster or simulator for casting:"""
    try:
      if isinstance(job, Casting):
        assert (
                isinstance(caster, Monotype)
                or
                isinstance(caster, MonotypeSimulation)
               )
        """Set up mutual dependencies:"""
        job.caster = caster
        caster.UI = UI
        caster.job = job
        caster.config = config
    except (AssertionError, NameError, AttributeError):
      UI.notify_user('You cannot do any casting without a proper caster!')
      UI.exit_program()


    """An __enter__ method of UI will call main_menu method in job:"""
    with UI:
      pass


"""And now, for something completely different...
Initialize the console interface when running the program directly."""
if __name__ == '__main__':
  session = Session(caster=Monotype('mkart-cc'))