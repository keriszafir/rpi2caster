#!/usr/bin/python

"""rpi2caster - control a Monotype composition caster with Raspberry Pi.

Monotype composition caster & keyboard paper tower control program.
The program reads a "ribbon" file, then waits for the user to start
casting or punching the paper tape. In the casting mode, during each
machine cycle, the photocell is lit (high state) or obscured (low).
When high, the program reads a line from ribbon and turns on
the solenoid valves respective to the Monotype control codes.
After the photocell is lit (low state on input), the valves are
turned off and the program moves on to the next line."""

"""Typical libs, used by most routines:"""
import sys
import os
import time
import string

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
except ImportError:
  print('wiringPi2 not installed! It is OK for testing, \
  but you MUST install it if you want to cast!')
  time.sleep(1)

"""rpi2caster uses sqlite3 database for storing caster, interface,
wedge, diecase & matrix parameters:"""
try:
  import sqlite3
except ImportError:
    print('You must install sqlite3 database and python-sqlite2 package.')
    exit()

"""This determines whether some exceptions will be caught
or thrown to stderr, off by default:"""
global DebugMode
DebugMode = False



class Database(object):
  """Database(databasePath):

  Read/write data for casters, interfaces, diecases, matrices and wedges
  from/to designated sqlite3 database.

  Default database path is ./database/monotype.db - but you can
  override it by instantiating this class with a different name
  as parameter.
  """

  def __init__(self, databasePath='database/monotype.db'):
    self.databasePath = databasePath


  def __enter__(self):
    return self


  def add_caster(self, casterSerial, casterName, casterType,
                 unitAdding, diecaseSystem, interfaceID=0):

    """add_caster(self, casterSerial, casterName, casterType,
                  unitAdding, diecaseSystem, interfaceID=0)

    Register a new caster in the database.
    Returns True if successful, False otherwise.

    The function uses a SQL query to create a new entry for a caster
    with parameters passed as arguments.

    Explanation of input parameters:

    casterSerial: caster's serial number (on nameplate on paper tower),

    casterName: a string for a caster's name,

    casterType: the type of composition caster:
        comp (composition caster),
        large_comp (large comp. caster, a.k.a. type & rule caster)

    unitAdding: determines if the unit adding attachment is on,
        or turned off / not present; if on - justification mode is changed,
        so 0005 is replaced by NJ, 0075 by NK, double justification is NJK;

        possible options: True (UA on), False (UA off / not present)

    diecaseSystem: what diecases the machine supports, possible options:
        norm15 (15x15),
        norm17 (15x17 NI, NL),
        hmn (16x17 HMN),
        kmn (16x17 KMN),
        shift (16x17 unit-shift - D signal activates unit shift,
               EF is used for accessing column D of a diecase)

    interfaceID: the interface ID, i.e. a set of MCP23017 chips and
        photocell & emergency stop GPIO lines the caster uses.

        Must be integer - default: 0

    If we want to use a single Raspberry Pi with several valvesets
    connected at the same time, we have to configure more interfaces.
    Each interface consists of 32 solenoid valves, two MCP23017 I/O,
    expanders, four ULN2803 drivers, a photocell (with its GPIO pin)
    and an emergency stop button (with its GPIO pin as well).

    Each MCP23017 MUST have its unique I2C address, which is set by
    tying pins A0, A1 and A2 to 3V3 or GND. Typically, you tie all
    pins to GND on the first chip (a.k.a. mcp0), and tie A0 to 3V3,
    A1 and A2 to GND on the second chip (a.k.a. mcp1) for interface id=0.
    The hex addresses of the chips mcp0 and mcp1 will be 0x20 and 0x21
    respectively. See the table below.

    If you configure additional interfaces, it's best to order the
    MCP23017 chips' addresses ascending, i.e.

    interfaceID    mcp0 pin    mcp1 pin    mcp0     mcp1
                   A2,A1,A0    A2,A1,A0    addr     addr

    0              000         001         0x20     0x21
    1              010         011         0x22     0x23
    2              100         101         0x24     0x25
    3              110         111         0x26     0x27

    0 means pin tied to GND and 1 means pin tied to 3V3.

    We can define up to 4 interfaces per Raspberry, because maximum
    of 8 MCP23017 chips can work on a single I2C bus, and there are
    two MCP23017s per interface.
    """

    """data - a list consisting of data to be written:"""
    data = [
            int(casterSerial), casterName, casterType,
            int(unitAdding), diecaseSystem, int(interfaceID)
           ]

    with sqlite3.connect(self.databasePath) as db:
      try:
        cursor = db.cursor()

        """Make sure that the table exists, if not - create it"""
        cursor.execute(
                      'CREATE TABLE IF NOT EXISTS caster_settings ('
                      'id INTEGER PRIMARY KEY ASC AUTOINCREMENT, '
                      'caster_serial INTEGER NOT NULL, '
                      'caster_name TEXT UNIQUE NOT NULL, '
                      'caster_type TEXT NOT NULL, '
                      'unit_adding INTEGER NOT NULL, '
                      'diecase_system TEXT NOT NULL, '
                      'interface_id INTEGER NOT NULL)'
                      )

        """Create an entry for the caster in the database"""
        cursor.execute(
                      'INSERT INTO caster_settings '
                      '(caster_serial, caster_name, '
                      'caster_type, unit_adding, '
                      'diecase_system, interface_id) '
                      'VALUES (?, ?, ?, ?, ?, ?)', data
                      )
        db.commit()
        return True
      except:
        """In debug mode we get the exact exception code & stack trace."""
        print('Database error! Cannot add caster!')
        if DebugMode:
          raise
        return False


  def list_casters(self):
    """list_casters(self):

    List all casters stored in database, or display a message
    if the table does not exist.

    Returns True if successful and False otherwise.

    Explanation of columns:

    ID: unique caster entry's ID

    casterSerial: caster's serial number (on nameplate on paper tower),

    casterName: a string for a caster's name,

    casterType: the type of composition caster:
        comp (composition caster),
        large_comp (large comp. caster, a.k.a. type & rule caster)

    unitAdding: determines if the unit adding attachment is on,
        or turned off / not present; if on - justification mode is changed,
        so 0005 is replaced by NJ, 0075 by NK, double justification is NJK;

        possible options: True (UA on), False (UA off / not present)

    diecaseSystem: what diecases the machine supports, possible options:
        norm15 (15x15),
        norm17 (15x17 NI, NL),
        hmn (16x17 HMN),
        kmn (16x17 KMN),
        shift (16x17 unit-shift - D signal activates unit shift,
               EF is used for accessing column D of a diecase)

    interfaceID: the interface ID, i.e. a set of MCP23017 chips and
        photocell & emergency stop GPIO lines the caster uses.
    """

    with sqlite3.connect(self.databasePath) as db:
      try:
        cursor = db.cursor()
        cursor.execute('SELECT * FROM caster_settings')
        print(
              '\nID, serial No, name, type, unit adding, '
              'diecase system, interface ID\n'
             )

        """Loop over rows unless an empty row is found, then stop"""
        while True:
          caster = cursor.fetchone()
          if caster is not None:
            caster = list(caster)
            for item in caster:
              print item, '   ',
            print ''
          else:
            break
        return True

      except sqlite3.OperationalError:
        """In debug mode we get the exact exception code & stack trace."""
        print(
              'Error: caster_settings table does not exist in database '
              '- not configured yet?\n'
             )
        if DebugMode:
          raise
        return False


  def caster_by_name(self, casterName):
    """caster_by_name(self, casterName):

    Get caster parameters for a caster with a given name.

    The function returns a list: [ID, casterSerial, casterName,
    casterType, unitAdding, diecaseSystem, interfaceID]
    for the first caster with a specified name.

    Explanation of parameters:

    ID: unique caster entry's ID

    casterSerial: caster's serial number (on nameplate on paper tower),

    casterName: a string for a caster's name,

    casterType: the type of composition caster:
        comp (composition caster),
        large_comp (large comp. caster, a.k.a. type & rule caster)

    unitAdding: determines if the unit adding attachment is on,
        or turned off / not present; if on - justification mode is changed,
        so 0005 is replaced by NJ, 0075 by NK, double justification is NJK;

        possible options: True (UA on), False (UA off / not present)

    diecaseSystem: what diecases the machine supports, possible options:
        norm15 (15x15),
        norm17 (15x17 NI, NL),
        hmn (16x17 HMN),
        kmn (16x17 KMN),
        shift (16x17 unit-shift - D signal activates unit shift,
               EF is used for accessing column D of a diecase)

    interfaceID: the interface ID, i.e. a set of MCP23017 chips and
        photocell & emergency stop GPIO lines the caster uses.

    If no caster matches, the function returns False.
    """

    with sqlite3.connect(self.databasePath) as db:
      try:
        cursor = db.cursor()
        cursor.execute(
        'SELECT * FROM caster_settings WHERE caster_name=?', [casterName]
        )
        caster = cursor.fetchone()

        """Check if the function found anything:"""
        if caster is not None:
          return caster
        else:
          print('No casters found!\n')
          return False
      except sqlite3.OperationalError:
        """In debug mode we get the exact exception code & stack trace."""
        print('Error: cannot retrieve caster settings!\n')
        if DebugMode:
          raise
        return False


  def caster_by_id(self, ID=0):
    """caster_by_id(self, ID=0)

    Caster by ID number:

    Get caster parameters for a caster with a given ID number (unique).

    If the ID number is not supplied, the function assumes 0 -
    which is OK, if we have a single caster without configuration changes.

    We can add more caster entries with add_caster, and get configuration
    for any them by its ID. That is useful in case we have several casters,
    or multiple configurations for a single caster in our database
    (that happens if we frequently turn unit shift or unit adding
    on or off - these attachments change the way caster interprets some
    signals, i.e. 0005 and 0075 are no longer used for justification).

    The function returns a list: [ID, casterSerial, casterName,
    casterType, unitAdding, diecaseSystem, interfaceID]
    for the caster with a specified ID.

    Explanation of parameters:

    ID: unique caster entry's ID

    casterSerial: caster's serial number (on nameplate on paper tower),

    casterName: a string for a caster's name,

    casterType: the type of composition caster:
        comp (composition caster),
        large_comp (large comp. caster, a.k.a. type & rule caster)

    unitAdding: determines if the unit adding attachment is on,
        or turned off / not present; if on - justification mode is changed,
        so 0005 is replaced by NJ, 0075 by NK, double justification is NJK;

        possible options: True (UA on), False (UA off / not present)

    diecaseSystem: what diecases the machine supports, possible options:
        norm15 (15x15),
        norm17 (15x17 NI, NL),
        hmn (16x17 HMN),
        kmn (16x17 KMN),
        shift (16x17 unit-shift - D signal activates unit shift,
               EF is used for accessing column D of a diecase)

    interfaceID: the interface ID, i.e. a set of MCP23017 chips and
        photocell & emergency stop GPIO lines the caster uses.

    If no caster is found, the function returns False.
    """

    with sqlite3.connect(self.databasePath) as db:
      try:
        cursor = db.cursor()
        cursor.execute('SELECT * FROM caster_settings WHERE id = %i' % ID)
        caster = cursor.fetchone()
        if caster is not None:
          return caster
        else:
          print('No casters found!\n')
          return False
      except sqlite3.OperationalError:
        """In debug mode we get the exact exception code & stack trace."""
        print('Error: cannot retrieve caster settings!\n')
        if DebugMode:
          raise
        return False


  def delete_caster(self, ID):
    """delete_caster(self, ID):

    Deletes a caster with a given ID from database.
    """
    with sqlite3.connect(self.databasePath) as db:
      try:
        cursor = db.cursor()
        cursor.execute('DELETE FROM caster_settings WHERE id=?', [ID])
        db.commit()
        return True
      except sqlite3.OperationalError:
        """In debug mode we get the exact exception code & stack trace."""
        print('Error: cannot delete caster!\n')
        if DebugMode:
          raise
        return False


  def add_interface(self, interfaceID, interfaceName,
                    emergencyGPIO, photocellGPIO,
                    mcp0Address, mcp1Address, pinBase):

    """add_interface(self, interfaceID, interfaceName,
                     emergencyGPIO, photocellGPIO,
                     mcp0Address, mcp1Address, pinBase):

    Registers a Raspberry Pi to Monotype caster interface.
    Returns True if successful, False otherwise.

    Use arguments to register a new interface, i.e. I2C expander params,
    emergency stop GPIO and photocell GPIO. The function uses a SQL query
    to add an entry to the database.

    Arguments:

    interfaceID - integer (0...3), auto-incremented, unique

    interfaceName - string, name for an interface (e.g. "caster1")

    emergencyGPIO - emergency button GPIO (Broadcom number), integer,
        must be unique, can be null

    photocellGPIO - photocell GPIO (Broadcom number), integer, must be
        unique, cannot be null

    mcp0Address - mcp0 (first MCP23017) I2C address, hex number
        (e.g. 0x20), must be unique, cannot be null

    mcp1Address - mcp1 (second MCP23017) I2C address, hex number
        (e.g. 0x21), must be unique, cannot be null

    pinBase - integer, base number for pins supplied by the first
        MCP23017 chip (i.e. mcp0). Must be unique, cannot be null.
        Minimum: 65 (0...64 are used by system, so they are reserved).

        Each interface uses 32 pins.

        If you are using multiple interfaces per Raspberry, you SHOULD
        assign the following pin bases to each interface:

        interfaceID    pinBase

        0              65
        1              97          (pinBase0 + 32)
        2              129         (pinBase1 + 32)
        3              161         (pinBase2 + 32)
    """

    """Data we want to write to the database:"""
    data = [interfaceID, interfaceName,
            emergencyGPIO, photocellGPIO,
            int(mcp0Address), int(mcp1Address), pinBase
           ]

    with sqlite3.connect(self.databasePath) as db:
      try:
        cursor = db.cursor()
        """Create the table first:"""
        cursor.execute(
                      'CREATE TABLE IF NOT EXISTS interface_settings '
                      '(id INTEGER PRIMARY KEY ASC AUTOINCREMENT, '
                      'interface_name TEXT UNIQUE, '
                      'emergency_gpio INTEGER UNIQUE, '
                      'photocell_gpio INTEGER UNIQUE NOT NULL, '
                      'mcp0_address INTEGER UNIQUE NOT NULL, '
                      'mcp1_address INTEGER UNIQUE NOT NULL, '
                      'pin_base INTEGER UNIQUE NOT NULL)'
                       )
        """Then add an entry:"""
        cursor.execute(
                      'INSERT INTO interface_settings (id,'
                      'interface_name,emergency_gpio,photocell_gpio,'
                      'mcp0_address,mcp1_address,pin_base) '
                      'VALUES (?, ?, ?, ?, ?, ?, ?)', data
                       )
        db.commit()
        return True
      except:
        """In debug mode we get the exact exception code & stack trace."""
        print('Database error! Cannot add interface!')
        if DebugMode:
          raise
        return False


  def get_interface(self, interfaceID=0):
    """get_interface(interfaceID):

    Return parameters for an interface with a given ID, most typically 0
    for a Raspberry Pi with a single interface (2xMCP23017 & 4xULN2803).

    If no arguments are supplied, get parameters for interface_id == 0.

    This function returns a list: [interfaceID, interfaceName,
    emergencyGPIO, photocellGPIO, mcp0Address, mcp1Address, pinBase].

    Interface parameters:

    interfaceID - interface ID (0...3)

    interfaceName - name for an interface (e.g. "caster1")

    emergencyGPIO - emergency button GPIO (Broadcom number)

    photocellGPIO - photocell GPIO (Broadcom number)

    mcp0Address - mcp0 (first MCP23017) I2C address, hex number
        (e.g. 0x20)

    mcp1Address - mcp1 (second MCP23017) I2C address, hex number
        (e.g. 0x21)

    pinBase - integer, base number for pins supplied by the first
        MCP23017 chip (i.e. mcp0).
    """
    with sqlite3.connect(self.databasePath) as db:
      try:
        cursor = db.cursor()
        cursor.execute(
                       'SELECT * FROM interface_settings WHERE id = ?',
                       [interfaceID]
                      )
        interface = cursor.fetchone()
        if interface is not None:
          interface = list(interface)
          return interface
        else:
          print('No interface with a given ID found!\n')
          return False

      except:
        """In debug mode we get the exact exception code & stack trace."""
        print('Error: cannot retrieve interface settings!\n')
        if DebugMode:
          raise
        return False


  def list_interfaces(self):
    """list_interfaces:

    List all interfaces stored in database with their parameters.


    Interface parameters:

    ID - interface ID (0...3)

    name - name for an interface (e.g. "caster1")

    emergency GPIO - emergency button GPIO (Broadcom number)

    photocell GPIO - photocell GPIO (Broadcom number)

    mcp0 addr - mcp0 (first MCP23017) I2C address, hex number
        (e.g. 0x20)

    mcp1 addr - mcp1 (second MCP23017) I2C address, hex number
        (e.g. 0x21)

    pin base - integer, base number for pins supplied by the first
        MCP23017 chip (i.e. mcp0).
    """

    with sqlite3.connect(self.databasePath) as db:
      try:
        cursor = db.cursor()
        cursor.execute('SELECT * FROM interface_settings')
        print(
              '\nID, name, emergency GPIO, photocell GPIO, '
              'MCP0 addr, MCP1 addr, pin base:\n'
             )
        while True:
          interface = cursor.fetchone()
          if interface is not None:
            interface = list(interface)
            """Correction to print proper hex values for I2C addresses:"""
            interface[4] = hex(interface[4])
            interface[5] = hex(interface[5])
            for item in interface:
              print item, '   ',
            print ''
          else:
            break

      except:
        """In debug mode we get the exact exception code & stack trace."""
        print('Database error: cannot retrieve interface data!')
        if DebugMode:
          raise


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

    with sqlite3.connect(self.databasePath) as db:
      try:
        cursor = db.cursor()
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
        db.commit()
        return True

      except:
        """In debug mode we get the exact exception code & stack trace."""
        print('Database error: cannot add wedge!')
        if DebugMode:
          raise
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

    with sqlite3.connect(self.databasePath) as db:
      try:
        cursor = db.cursor()
        cursor.execute(
                      'SELECT * FROM wedges WHERE wedge_id = ? '
                      'AND set_width = ?', [wedgeName, setWidth]
                      )
        wedge = cursor.fetchone()
        if wedge is None:
          print(
                'No wedge %s - %f found in database!'
                 % (wedgeName, setWidth)
               )
          return False
        else:
          wedge = list(wedge)
          print(
                'Wedge %s - %f found in database - OK'
                 % (wedgeName, setWidth)
               )

          """Change return value of oldPica to boolean:"""
          wedge[3] = bool(wedge[3])

          """Change return value of steps to list:"""
          wedge[4] = json.loads(wedge[4])

          """Return [ID, wedgeName, setWidth, oldPica, steps]:"""
          return wedge

      except:
        """In debug mode we get the exact exception code & stack trace."""
        print('Database error: cannot get wedge!')
        if DebugMode:
          raise


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

    with sqlite3.connect(self.databasePath) as db:
      try:
        cursor = db.cursor()
        cursor.execute(
                      'SELECT * FROM wedges WHERE id = ? ', [ID]
                      )
        wedge = cursor.fetchone()
        if wedge is None:
          print('Wedge not found!')
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
        print('Database error: cannot get wedge!')
        if DebugMode:
          raise


  def delete_wedge(self, ID):
    """delete_wedge(self, ID):

    Deletes a wedge with given unique ID from the database
    (useful in case we no longer have the wedge).

    Returns True if successful, False otherwise.

    First, the function checks if the wedge is in the database at all.
    """
    if self.wedge_by_id(ID):
      with sqlite3.connect(self.databasePath) as db:
        try:
          cursor = db.cursor()
          cursor.execute(
                         'DELETE FROM wedges WHERE id = ?', [ID]
                        )
          return True
        except:
          """In debug mode we get the exact exception code & stack trace."""
          print('Database error: cannot delete wedge!')
          if DebugMode:
            raise
          return False
    else:
      print('Nothing to delete.')
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

    with sqlite3.connect(self.databasePath) as db:
      try:
        cursor = db.cursor()
        cursor.execute('SELECT * FROM wedges')
        print(
              '\nid, wedge name, set width, old pica, '
              'unit values for all steps:\n'
             )
        while True:
          wedge = cursor.fetchone()
          if wedge is not None:
            wedge = list(wedge)

            """Change return value of steps to list:"""
            wedge[4] = json.loads(wedge[4])

            """Print all the wedge parameters:"""
            for item in wedge:
              print item, '   ',
            print ''
          else:
            break
        return True

      except:
        """In debug mode we get the exact exception code & stack trace."""
        print('Database error: cannot list wedges!')
        if DebugMode:
          raise
        return False


  def __exit__(self, *args):
    pass


class MonotypeConfiguration(object):

  def __init__(self, database, userInterface):
    """Connect to a specified database:"""
    self.database = database
    self.userInterface = userInterface

  def __enter__(self):
    return self


  def convert_to_hex(s):
    """A simple hexstring to int converter.
    Returns int if arg is a hexstring, False otherwise.
    """
    try:
      result = int(s, 16)
      return result
    except (TypeError, ValueError):
      return False


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

    revalidate = False # deprecated!

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

    # To be deprecated and replaced with new menu

    while diecaseSystem not in dcsystems:
      diecaseSystem = raw_input(
                                'Diecase format this machine works with: '
                                '0 for 15x15, 1 for 15x17, '
                                '2 for HMN, 3 for KMN, 4 for unit-shift: '
                                )
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

      # To be deprecated and replaced with a new small menu:

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

      # Find a more elegant way to do it:

      print('Caster serial number: %i \n' % casterSerial)
      print('Caster name: %s \n' % casterName)
      print('Caster type: %s \n' % casterType)
      print('Unit adding: %s \n' % str(unitAdding))
      print('Diecase system: %s \n' % diecaseSystem)
      print('Interface ID for this caster: %i \n' % interfaceID)

      # To be deprecated and replaced with a new small menu:

      ans = userInterface.choice(
                                 '\nCommit? '
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

    """Enter the interface ID number; up to 4 interfaces are supported:"""
    while not str(ID).isdigit() or int(ID) in range(4):
      ID = raw_input(
                     'Enter the interface ID: 0, 1, 2, 3, 4; default 0: '
                    )
      if ID == '':
        ID = 0
    else:
      ID = int(ID)

    """Enter a string for interface name"""
    while not interfaceName:
      interfaceName = raw_input(
                                'Enter the name you want to use '
                                'for this interface: '
                               )

    """Emergency button GPIO for this interface"""
    while not str(emergencyGPIO).isdigit() or int(emergencyGPIO) < 4:
      emergencyGPIO = raw_input(
                                'Enter the emergency button GPIO - '
                                'BCM number: '
                               )
    else:
      emergencyGPIO = int(emergencyGPIO)

    """Photocell GPIO for this interface"""
    while not (
               str(photocellGPIO).isdigit()
               and int(photocellGPIO) > 3
               and photocellGPIO != emergencyGPIO
              ):
      photocellGPIO = raw_input(
                                'Enter the photocell GPIO - BCM number: '
                               )
    else:
      photocellGPIO = int(photocellGPIO)

    """First MCP23017 address for this interface, typically 0x20.
    First check if we have a hexstring. If not, enter value."""

    while not convert_to_hex(mcp0Address):
      mcp0Address = raw_input(
                              'Enter the first MCP23017 I2C address - '
                              'hexadecimal. Default 0x20: '
                             )
      if mcp0Address == '':
        mcp0Address = '0x20'
    mcp0Address = convert_to_hex(mcp0Address)

    """Second MCP23017 address for this interface, typically 0x21:"""
    while not convert_to_hex(mcp1Address):
      mcp1Address = raw_input(
                              'Enter the second MCP23017 I2C address - '
                              'hexadecimal. Default 0x21: '
                             )
      if mcp1Address == '':
        mcp1Address = '0x21'
    mcp1Address = convert_to_hex(mcp1Address)

    """Pin base for GPIOs on MCP23017. Typically 65 for first interface,
    97 for second, 129 for third. 0 to 64 are RESERVED, we can't use them!"""
    while not str(pinBase).isdigit() or int(pinBase) < 65:
      pinBase = raw_input(
                          'Enter the pin base for GPIOs on MCP23017 chips. '
                          'Default 65: '
                         )
      if pinBase == '':
        pinBase = 65
    else:
      pinBase = int(pinBase)

    """That's it! All interface parameters are entered, now let's
    display them and ask user what to do."""

    enteredParameters = { 'Interface ID' : ID,
                          'Interface name' : interfaceName,
                          'Emergency button GPIO' : emergencyGPIO,
                          'Photocell GPIO' : photocellGPIO,
                          '1st MCP23017 I2C address' : mcp0Address,
                          '2nd MCP23017 I2C address' : mcp1Address,
                          'Pin base for GPIOs on MCP23017s' : pinBase
                        }

    for key, value in enteredParameters:
      print key, ' : ', value

    """old code
    print('Interface ID: %i \n' % ID)
    print('Interface name: %s \n' % interfaceName)
    print('Emergency GPIO: %i \n' % emergencyGPIO)
    print('Photocell GPIO: %i \n' % photocellGPIO)
    print('MCP0 Address: %s \n' % mcp0Address)
    print('MCP1 Address: %s \n' % mcp1Address)
    print('Pin base: %i \n' % pinBase)
    """

      # To be deprecated and replaced with a new small menu:

    ans = userInterface.simple_menu('\nCommit? '
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

      # Find a more elegant way to do this:

      print('Wedge: %s \n' % wedgeName)
      print('Set width: %f \n' % setWidth)
      print('Is it an old pica ("E") wedge?: %s \n' % str(oldPica))

      """Loop over all unit values in wedge's steps and display them:"""
      for i, step in zip(range(len(steps)), steps):
        print('Step %i unit value: %i \n' % (i+1, step))

      # To be deprecated and replaced with a new small menu:

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



  def main_menu(self):
    self.userInterface.menu  (
          header = (
                    'Setup utility for rpi2caster CAT. '
                    '\nMain menu:'
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


class Monotype(object):
  """Monotype(casterName, database):

  A class which stores all methods related to the interface and
  caster itself."""

  def __init__(self, casterName, database):
    """__init__(casterName, database):

    Creates a caster object for a given caster name.
    Uses a database object obtained from upstream.
    Looks the caster up in a database and gets its parameters,
    as well as interface parameters.
    """
    self.casterName = casterName
    self.database = database


  def __enter__(self):

    if DebugMode:
      print 'Using caster: ', self.casterName
    self.caster_setup()
    return self


  def caster_setup(self):

    """Setup routine:

    After the class is instantiated, this method reads caster data
    from database and fetches a list of caster parameters: [serialNumber,
    casterName, casterType, justification, diecaseFormat, interfaceID].
    """
    casterParameters = self.database.caster_by_name(self.casterName)

    """
    Get casting interface ID from the parameters;
    we need the last item returned, hence [-1]
    """
    interfaceID = casterParameters[-1]

    """When debugging, display all caster info:"""
    if DebugMode:
      print 'Caster parameters: ', casterParameters
      print 'Interface ID: ', interfaceID

    """
    Unpack (assign to list items) the obtained parameters.
    The parameters will affect the whole object
    created with this class.
    """
    [self.casterID, self.casterSerial, self.casterName,
    self.casterType, self.unitAdding, self.diecaseSystem,
    self.interfaceID] = casterParameters

    """
    Then, the interface ID is looked up in the database, and interface
    parameters are known: [interfaceID, interfaceName, emergencyGPIO,
    photocellGPIO, mcp0Address, mcp1Address, pinBase]
    """
    interfaceParameters = self.database.get_interface(interfaceID)

    """Print the parameters for debugging:"""
    if DebugMode:
      print 'Interface parameters: ', interfaceParameters

    """
    Unpack (assign to list items) the obtained parameters.
    The parameters will affect the whole object
    created with this class.
    """
    [self.interfaceID, self.interfaceName,
    self.emergencyGPIO, self.photocellGPIO,
    self.mcp0Address, self.mcp1Address,
    self.pinBase] = interfaceParameters


    """On init, do the input configuration:

    We need to set up the sysfs interface before (powerbuttond.py -
    a daemon running on boot with root privileges takes care of it).
    """
    gpioSysfsPath = '/sys/class/gpio/gpio%s/' % self.photocellGPIO
    self.gpioValueFileName = gpioSysfsPath + 'value'
    self.gpioEdgeFileName  = gpioSysfsPath + 'edge'


    """Check if the photocell GPIO has been configured - file can be read:"""
    if not os.access(self.gpioValueFileName, os.R_OK):
      print(
            '%s: file does not exist or cannot be read. '
            'You must export the GPIO no %i as input first!'
              % (self.gpioValueFileName, self.photocellGPIO)
           )
      exit()


    """Ensure that the interrupts are generated for photocell GPIO
    for both rising and falling edge:"""
    with open(self.gpioEdgeFileName, 'r') as edgeFile:
      if (edgeFile.read()[:4] != 'both'):
        print(
              '%s: file does not exist, cannot be read, '
              'or the interrupt on GPIO no %i is not set to "both". '
              'Check the system config.'
               % (self.gpioEdgeFileName, self.photocellGPIO)
              )
        exit()


    """Output configuration:

    Setup the wiringPi MCP23017 chips for valve outputs:
    """
    wiringpi.mcp23017Setup(self.pinBase,      self.mcp0Address)
    wiringpi.mcp23017Setup(self.pinBase + 16, self.mcp1Address)

    pins = range(self.pinBase, self.pinBase + 32)

    """Set all I/O lines on MCP23017s as outputs - mode = 1"""
    for pin in pins:
      wiringpi.pinMode(pin,1)


    """This list defines the names and order of Monotype control signals
    that will be assigned to 32 MCP23017 outputs and solenoid valves.
    You may want to change it, depending on how you wired the valves
    in hardware (e.g. you can fix interchanged lines by swapping signals).

    Monotype ribbon perforations are arranged as follows:

    NMLKJIHGF S ED  0075    CBA 123456789 10 11 12 13 14  0005
                   (large)                               (large)

    O15 is absent in ribbon, and is only used by the keyboard's paper tower.
    It's recommended to assign it to the first or last output line.

    You'll probably want to assign your outputs in one of these orders:

    a) alphanumerically:

    mcp0 bank A | mcp0 bank B                | mcp1 bank A | mcp1 bank B
    ---------------------------------------------------------------------
    12345678    | 9 10 11 12 13 14 0005 0075 | ABCDEFGH    | IJKLMN S O15
    """
    signalsA = [
                '1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
                '11', '12', '13', '14', '0005', '0075', 'A', 'B',
                'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
                'M', 'N', 'S', 'O15'
               ]

    """
    b) according to Monotype codes:

    mcp0 bank A | mcp0 bank B     | mcp1 bank A | mcp1 bank B
    -----------------------------------------------------------------------
    NMLKJIHG    | F S ED 0075 CBA | 12345678    | 9 10 11 12 13 14 0005 O15
    """
    signalsB = [
                'N', 'M', 'L', 'K', 'J', 'I', 'H', 'G', 'F', 'S', 'E',
                'D', '0075', 'C', 'B', 'A', '1', '2', '3', '4', '5',
                '6', '7', '8', '9', '10', '11', '12', '13', '14',
                '0005', 'O15'
               ]

    """
    c) grouping odd and even Monotype signals in valve units,
    where first MCP controls odd signals (upper/lower paper tower inputs
    if you use V air connection block) and second MCP controls even signals:

    mcp0 bank A   | mcp0 bank B      | mcp1 bank A | mcp1 bank B
    --------------------------------------------------------------------
    NLJHFE 0075 B | 13579 11 13 0005 | MKIGSDCA    | 2468 10 12 14 O15
    """
    signalsC = [
                'N', 'L', 'J', 'H', 'F', 'E', '0075', 'B', '1', '3',
                '5', '7', '9', '11', '13', '0005', 'M', 'K', 'I', 'G',
                'S', 'D', 'C', 'A', '2', '4', '6', '8', '10', '12',
                '14', 'O15'
               ]

    """
    d) grouping odd and even Monotype signals in valve units,
    where first MCP controls left half of signals - N...A,
    and second MCP controls right half - 1...0005:

    mcp0 bank A   | mcp0 bank B | mcp1 bank A      | mcp1 bank B
    --------------------------------------------------------------------
    NLJGFE 0075 B | MKIHSDCA    | 13579 11 13 0005 | 2468 10 12 14 O15
    """
    signalsD = [
                'N', 'L', 'J', 'H', 'F', 'E', '0075', 'B', 'M', 'K',
                'I', 'G', 'S', 'D', 'C', 'A','1', '3', '5', '7', '9',
                '11', '13', '0005',  '2', '4', '6', '8', '10', '12',
                '14', 'O15'
               ]


    """mcp0 is the MCP23017 with lower address (e.g. 0x20), mcp1 - the chip
    with higher address (e.g. 0x21). If you're using DIP or SOIC chips,
    I/O bank A uses physical pin numbers 21...18, bank B is 1...8.
    See datasheet for further info."""


    """Choose one of predefined orders or define a brand new one:"""
    signals = signalsA

    """Assign wiringPi pin numbers on MCP23017s to the Monotype
    control signals defined earlier.
    """
    self.wiringPiPinNumber = dict(zip(signals, pins))

    """Print signals order for debugging:"""
    if DebugMode:
      print 'Signals arrangement: ',
      for sig in signals:
        print sig,
      print '\n'
      """The program has displayed caster-related debug info,
      now it is time for the user to read it and press Enter to proceed.

      Normally, user goes directly to the main menu."""
      raw_input('Press Enter to continue... ')


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
          print('\nOkay, the machine is running...\n')
          return True
        else:
          self.machine_stopped()
          self.detect_rotation()
          return False


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
    choice = ""
    while choice not in ['c', 'm', 'e']:
      choice = raw_input(
                         "Machine not running! Check what\'s going on."
                         "\n(C)ontinue, return to (M)enu "
                         "or (E)xit program."
                        )
    else:
      if choice.lower() == 'c':
        return True
      elif choice.lower() == 'm':
        pass
      elif choice.lower() == 'e':
        self.deactivate_valves()
        exit()


  def __exit__(self, *args):
    """On exit, turn all the valves off"""
    self.deactivate_valves()



class MonotypeSimulation(object):
  """MonotypeSimulation:

  A class which allows to test rpi2caster without an actual interface
  or caster. Most functionality will be developped without an access
  to the machine.
  """

  def __init__(self):
    pass

  def __enter__(self):
    """Instantiation:

    A lot simpler than "real" operation; we don't set up the GPIO lines
    nor interrupt polling files We'll use substitute routines that
    emulate caster-related actions.
    """
    raw_input(
              'Testing rpi2caster without an actual caster or interface. '
               'Debug mode ON.'
               )
    global DebugMode
    DebugMode = True
    return self


  def send_signals_to_caster(self, signals, machineTimeout):
    """Just send signals, as we don't have a photocell"""
    raw_input('Sensor ON - press [ENTER]')
    self.activate_valves(signals)
    raw_input('Sensor OFF - press [ENTER]')
    self.deactivate_valves()


  def activate_valves(self, signals):
    """If there are any signals, print them out"""
    if len(signals) != 0:
      print('The valves: ',' '.join(signals),' would be activated now.')


  def deactivate_valves(self):
    """No need to do anything"""
    print('The valves would be deactivated now.')


  def detect_rotation(self):
    """FIXME: implement raw input breaking on timeout"""
    print('Now, the program would check if the machine is rotating.\n')
    startTime = time.time()
    while time.time() < startTime + 5:
      answer = raw_input('Press return (to simulate rotation) '
                         'or wait 5sec (to simulate machine off)\n')
    else:
      if answer is None:
        self.machine_stopped()
        self.detect_rotation()


  def machine_stopped(self):
    """Machine stopped menu - the same as in actual casting.

    This allows us to choose whether we want to continue, return to menu
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


  def __exit__(self, *args):
    self.deactivate_valves()



class Parsing(object):
  def __init__(self):
    pass

  def __enter__(self):
    return self

  """This class contains file- and line-parsing methods"""


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


  def __exit__(self, *args):
    pass



class Actions(object):
  """Actions the user can do in this software"""


  def __init__(self, caster):
    """Pass a caster object to use:
    """
    self.caster = caster

  def __enter__(self):
    return self


  def cast_composition(self, filename):
    """ Composition casting routine. The input file is read backwards -
    last characters are cast first, after setting the justification."""

    """Open a file with signals"""
    with open(filename, 'rb') as ribbon:
      contents = ribbon.readlines()


    """For casting, we need to read the file backwards"""
    contents = reversed(contents)

    """Display a little explanation:"""
    print(
          '\nThe combinations of Monotype signals will be displayed '
          'on screen while the machine casts the type.\n'
          'Turn on the machine and the program will '
          'start automatically.\n'
          )

    """Check if the machine is running - don't do anything when
    it's not rotating yet!"""
    caster.detect_rotation()

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
        print comment

      """Cast an empty line, signals with comment, signals with no comment.
      Don't cast a line with comment alone."""
      if len(comment) == 0 or len(signals) > 0:
        if len(signals) > 0:
          print ' '.join(signals)
        else:
          print('O+15 - no signals')
        caster.send_signals_to_caster(signals)

    """After casting is finished, notify the user:"""
    print('\nCasting finished!')

    """End of function."""


  def punch_composition(self, filename):
    """punch_composition(filename):

    When punching, the input file is read forwards. An additional line
    (O+15) is switched on for operating the paper tower, if less than
    two signals are found in a sequence.
    """

    """Open a file with signals"""
    with open(filename, 'rb') as ribbon:

      """
      Wait until the operator confirms.

      We can't use automatic rotation detection like we do in
      cast_composition, because keyboard's paper tower doesn't run
      by itself - it must get air into tubes to operate, punches
      the perforations, and doesn't give any feedback.
      """
      print('\nThe combinations of Monotype signals will be displayed '
                'on screen while the paper tower punches the ribbon.\n')
      raw_input('\nInput file found. Turn on the air, fit the tape '
             'on your paper tower and press return to start punching.\n')
      for line in ribbon:

        """
        Parse the row, return a list of signals and a comment.
        Both can have zero or positive length.
        """
        signals, comment = Parsing.signals_parser(line)

        """Print a comment if there is one - positive length"""
        if len(comment) > 0:
          print comment

        """
        Punch an empty line, signals with comment, signals with
        no comment.

        Don't punch a line with nothing but comments
        (prevents erroneous O+15's).
        """
        if len(comment) == 0 or len(signals) > 0:

          """Determine if we need to turn O+15 on"""
          if len(signals) < 2:
            signals += ('O15',)
          print ' '.join(signals)
          caster.activate_valves(signals)

          """The pace is arbitrary, let's set it to 200ms/200ms"""
          time.sleep(0.2)
          caster.deactivate_valves()
          time.sleep(0.2)

    """After punching is finished, notify the user:"""
    print('\nPunching finished!')

    """End of function."""


  def line_test(self):
    """line_test():

    Tests all valves and composition caster's inputs to check
    if everything works and is properly connected. Signals will be tested
    in order: 0005 - S - 0075, 1 towards 14, A towards N, O+15, NI, NL,
    EF, NJ, NK, NKJ, MNH, MNK (feel free to add other combinations!)
    """
    raw_input('This will check if the valves, pin blocks and 0005, S, '
             '0075 mechanisms are working. Press return to continue... ')

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
      print ' '.join(combination)
      caster.send_signals_to_caster(combination, 120)

    print('\nTesting finished!')

    """End of function."""


  def cast_sorts(self):
    """cast_sorts():

    Sorts casting routine, based on the position in diecase.
    Ask user about the diecase row & column, as well as number of sorts.
    """
    os.system('clear')
    print('Calibration and Sort Casting:\n\n')
    signals = raw_input(
                        'Enter column and row symbols '
                        '(default: G 5, spacebar if O-15) '
                       )
    print('\n')
    if signals == '':
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
    if len(parsedSignals) == 0 and signals != ' ':
      print('\nRe-enter the sequence')
      time.sleep(1)
      self.cast_sorts()
    n = raw_input(
                  '\nHow many sorts do you want to cast? (default: 10) '
                 )
    print('\n')

    """Default to 10 if user enters non-positive number or letters"""
    if not n.isdigit() or int(n) < 0:
      n = '10'
    n = int(n)

    """Warn if we want to cast too many sorts from a single matrix"""
    print ("\nWe'll cast it %i times.\n" % n)
    if n > 10:
      print(
            'Warning: you want to cast a single character more than '
            '10 times. This may lead to matrix overheating!\n'
           )

    """Ask user if the entered parameters are correct"""
    choice = ''
    while choice not in ['c', 'r', 'm', 'e']:
      choice = raw_input(
                         '(C)ontinue, (R)epeat, go back to (M)enu '
                         'or (E)xit program? '
                        )
    else:
      if choice.lower() == 'c':
        """Check if the machine is running"""
        print('Start the machine...')
        caster.detect_rotation()

        """Cast the sorts: turn on the pump first."""
        print('Starting the pump...')
        caster.send_signals_to_caster(['0075'])

        """Start casting characters"""
        print('Casting characters...')

        """Cast n combinations of row & column, one by one"""
        for i in range(n):
          if len(parsedSignals) > 0:
            print ' '.join(parsedSignals)
          else:
            print('O+15 - no signals')
          caster.send_signals_to_caster(parsedSignals)

        """Put the line to the galley:"""
        print('Putting line to the galley...')
        caster.send_signals_to_caster(['0005', '0075'])
        """After casting sorts we need to stop the pump"""
        print('Putting line to the galley...')
        caster.send_signals_to_caster(['0005'])

      elif choice.lower() == 'r':
        self.cast_sorts()
      elif choice.lower() == 'm':
        pass
      elif choice.lower() == 'e':
        self.cleanup()
        exit()

    """Ask what to do after casting"""
    print('\nFinished!')

    finishedChoice = ''
    while finishedChoice.lower() not in ['r', 'm', 'e']:
      finishedChoice = raw_input(
                                 '(R)epeat, go back to (M)enu '
                                 'or (E)xit program? '
                                )
      if finishedChoice.lower() == 'r':
        self.cast_sorts()
      elif finishedChoice.lower() == 'm':
        pass
      elif finishedChoice.lower() == 'e':
        self.cleanup()
        exit()

      else:
        print('\nNo such option. Choose again.')
        finishedChoice = ''


  def send_combination(self):
    """This function allows us to give the program a specific combination
    of Monotype codes, and will keep the valves on until we press return
    (useful for calibration). It also checks the signals' validity"""

    """Let the user enter a combo:"""
    signals = ''
    while signals == '':
      signals = raw_input(
                          'Enter the signals to send to the machine: '
                         )

    """Parse the combination, get the signals (first item returned
    by the parsing function):"""
    combination = Parsing.signals_parser(signals)[0]

    """Check if we get any signals at all, if so, turn the valves on:"""
    if combination:
      print ' '.join(combination)
      caster.activate_valves(combination)

    """Wait until user decides to stop sending those signals to valves:"""
    raw_input('Press return to stop. ')
    caster.deactivate_valves()

    """End of function"""


  def cleanup(self):
    """Call deactivate_valves to make sure no lines stay turned on:
    """
    caster.deactivate_valves()


  def __exit__(self, *args):
    pass



class TextUserInterface(object):
  """TextUserInterface(database, caster, actions):

  Use this class for text-based console user interface.

  Database, caster and actions objects need to be created earlier
  before instantiating this class.

  Suitable for controlling a caster from the local terminal or via SSH,
  supports UTF-8 too.
  """

  def __init__(self, actions):
    pass


  def __enter__(self):

    """Set up an empty ribbon file name first"""
    self.inputFileName = ''
    return self


  def tab_complete(text, state):
    """tab_complete(text, state):

    This function enables tab key auto-completion when you
    enter the filename.
    """
    return (glob.glob(text+'*')+[None])[state]
  readline.set_completer_delims(' \t\n;')
  readline.parse_and_bind('tab: complete')
  readline.set_completer(tab_complete)


  def consoleUI(self):
    """consoleUI():

    Main loop definition. All exceptions should be caught here.
    Also, ensure cleaning up after exit.
    """
    try:
      self.main_menu()
    except (IOError, NameError):
      raw_input(
                '\nInput file not chosen or wrong input file name. '
                'Press return to go to main menu.\n'
                )
      if DebugMode == True:
        print('Debug mode: see what happened.')
        raise
      self.main_menu()

    except KeyboardInterrupt:
      print('\nTerminated by user.')
      exit()
    finally:
      print('Goodbye!')
      actions.cleanup()


  @staticmethod
  def menu(options, **kwargs):
    """menu(
            options={'foo':'bar','baz':'qux'}
            header=foo,
            footer=bar,
            recursive=False):

    A menu which takes three arguments:
    header - string to be displayed above,
    footer - string to be displayed below.,
    recursive - determines whether the menu will call itself after
                a command called by choice is executed entirely.

    After choice is made, executes the command.
    """

    """Parse the keyword arguments. If argument is unset, assign
    an empty string.
    """
    try:
      header = kwargs['header']
    except KeyError:
      header = ''

    try:
      footer = kwargs['footer']
    except KeyError:
      footer = ''

    try:
      recursive = kwargs['recursive']
    except KeyError:
      recursive = False

    """Set up vars for conditional statements,
     and lists for appending new items.

     choices - options to be entered by user,
     commands - commands to be executed after option is chosen,
     pauses - flags indicating whether the program will be paused
              on return to menu (waiting for user to press return):
     """
    yourChoice = ''
    choices = []


    """Clear the screen, display header and add two empty lines:"""
    os.system('clear')
    if header:
      print header
      print('')

    """Display all the options; construct the possible choices list:"""

    for choice in options:
       if choice != 0:
        """Print the option choice and displayed text:
        """
        print '\t', choice, ' : ', options[choice], '\n'
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

    if recursive:
      """Go back to this menu after the command is done:"""
      TextUserInterface.menu(options, kwargs)


  def main_menu_additional_info(self):
    """Displays additional info as a main menu footer:"""
    if self.inputFileName != '':
      return(
             'Input file name: ' + self.inputFileName
            )


  def enter_filename(self):
    """Enter the ribbon filename; check if the file is readable"""
    fn = raw_input('\n Enter the ribbon file name: ')
    fn = os.path.realpath(fn)
    try:
      with open(fn, 'r'):
        return fn
    except IOError:
      raw_input('Wrong filename or file not readable!')
      return ''


  @staticmethod
  def debug_notice():
    """Prints a notice if the program is in debug mode:"""
    if DebugMode:
      return('\n\nThe program is now in debugging mode!')
    else:
      return ''


  def main_menu(self):
    """Calls menu() with options, a header and a footer.
    Does not use the recursive feature of menu(), because the
    additional information would not be displayed.
    Instead, recursion is implemented in this function.
    """
    options = {
               1 : 'Load a ribbon file',
               2 : 'Cast composition',
               3 : 'Punch a paper tape',
               4 : 'Cast sorts',
               5 : 'Test the valves and pinblocks',
               6 : 'Lock the caster on a specified diecase position',
               0 : 'Exit program'
              }

    commands = {
                1 : 'self.inputFileName = self.enter_filename()',
                2 : 'actions.cast_composition(self.inputFileName)',
                3 : 'actions.punch_composition(self.inputFileName)',
                4 : 'actions.cast_sorts()',
                5 : 'actions.line_test()',
                6 : 'actions.send_combination()',
                0 : 'exit()'
               }

    choice = TextUserInterface.menu(
              options,
              header = (
                        'rpi2caster - CAT (Computer-Aided Typecasting) '
                        'for Monotype Composition or Type and Rule casters.'
                        '\n\n'
                        'This program reads a ribbon (input file) '
                        'and casts the type on a Composition Caster, \n'
                        'or punches a paper tape with a paper tower '
                        'taken off a Monotype keyboard.'
                       ) + self.debug_notice() + '\n\nMain Menu:',

              footer = self.main_menu_additional_info()
              )

    exec commands[choice]

    #raw_input('Press Enter to return to main menu...')
    self.main_menu()

  @staticmethod
  def simple_menu(message, options):
    """A simple menu where user is asked what to do.
    Wrong choice points back to the menu.

    Message: string displayed on screen;
    options: a list or tuple of strings - options.
    """
    ans = ''
    while ans not in options:
      ans = raw_input(message)
    return ans


  def __exit__(self, *args):
    """On exiting, turn all the valves off."""
    actions.cleanup()



class Testing(object):
  """Testing:

  A class for testing the program without an actual caster/interface.
  Certain functions referring to the caster will be replaced with
  placeholder methods from the MonotypeSimulation class.
  """
  def __init__(self, database, caster, actions, userInterface):
    """Instantiate a caster simulator object instead of a real caster;
    other functionality should remain unchanged"""
    self.database = database
    self.caster = caster
    self.actions = actions
    self.userInterface = userInterface


  def __enter__(self):
    pass


  def __exit__(self, *args):
    pass



class WebInterface(object):
  """WebInterface:

  Use this class for instantiating text-based console user interface"""

  def __init__(self, database, caster, actions):
    """instantiate config for the caster"""

    self.database = database
    self.caster = caster
    self.actions = actions


  def __enter__(self):
    self.webUI()


  def webUI(self):
    """This is a placeholder for web interface method. Nothing yet..."""
    pass

  def __exit__(self, *args):
    pass



"""And now, for something completely different...
Initialize the console interface when running the program directly."""
if __name__ == '__main__':


  DebugMode = True

  database = Database('database/monotype.db')
  caster = Monotype('mkart-cc', database)
  actions = Actions(caster)
  userInterface = TextUserInterface(actions)


  with database, caster, actions, userInterface:
    userInterface.consoleUI()