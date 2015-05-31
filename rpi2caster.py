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
air bar down,
-help calibrating the space transfer wedge by casting a combination without
and with the S-needle with 0075 wedge at 3 and 0005 wedge at 8 (neutral)
-heat the mould up by casting some em-quads

During casting, the program automatically detects the machine movement,
so no additional actions on user's part are required.

In the future, the program will have an "emergency stop" feature.
When an interrupt on a certain Raspberry Pi's GPIO is detected, the program
stops sending codes to the caster and sends a 0005 combination instead.
The pump is immediately stopped.
"""

# IMPORTS, and warnings if package is not found in system:
unmetDependencies = []

# Typical libs, used by most routines:
import sys
import os
import time

# Config parser for reading the interface settings
import ConfigParser

# Used for serializing lists stored in database, and for communicating
# with the web application (in the future):
try:
    import json
except ImportError:
    import simplejson as json

# These libs are used by file name autocompletion:
import readline
import glob

# Essential for polling the sensor for state change:
import select

# Signals parsing methods for rpi2caster:
import parsing

# MCP23017 driver & hardware abstraction layer library:
try:
    import wiringpi2 as wiringpi
    #import wiringpi
except ImportError:
    unmetDependencies.append('wiringPi2 Python bindings: wiringpi2-python')

# rpi2caster uses sqlite3 database for storing caster, interface,
# wedge, diecase & matrix parameters:
try:
    import sqlite3
except ImportError:
    unmetDependencies.append('SQLite3: sqlite3')

# Warn about unmet dependencies:
if unmetDependencies:
    warning = 'Unmet dependencies - some functionality will not work:\n'
    for dep in unmetDependencies:
        warning += (dep + '\n')
    print warning
    time.sleep(2)


class Config(object):
    """Configuration class.

    A class for reading and parsing the config file with a specified path.

    Want to use a different conffile? Just instantiate this class with
    a custom "path" parameter, that's all.
    """

    def __init__(self, path='/etc/rpi2caster.conf'):
        """Check if config file is readable first"""
        self.UI = TextUI()
        self.is_caster = True
        try:
            with open(path, 'r'):
                self.confFilePath = path
            self.cfg = ConfigParser.SafeConfigParser()
            self.cfg.read(self.confFilePath)
        except IOError:
            self.UI.display('Cannot open config file:', path)

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
             norm15     - old 15x15,
             norm17     - 15x17 NI, NL,
             hmn        - 16x17 HMN (rare),
             kmn        - 16x17 KMN (rare),
             shift      - 16x17 unit-shift (most modern).
        unit_adding [0,1] - whether the machine has a unit-adding attachment,
        interface_id [0,1,2,3] - ID of the interface connected to the caster.
        """
        try:
            isPerforator = self.cfg.get(casterName, 'is_perforator')
        except (ConfigParser.NoSectionError,
                ConfigParser.NoOptionError,
                ValueError, TypeError):
                    isPerforator = False
        # We now know if it's a perforator
        try:
            interfaceID = self.cfg.get(casterName, 'interface_id')
            if isPerforator:
                return int(interfaceID)
            else:
            # Get caster parameters from conffile
                unitAdding = self.cfg.get(casterName, 'unit_adding')
                diecaseSystem = self.cfg.get(casterName, 'diecase_system')
            # Time to return the data:
                return [bool(unitAdding), diecaseSystem, int(interfaceID)]
        except (ConfigParser.NoSectionError,
                ConfigParser.NoOptionError,
                ValueError, TypeError):
        # Do nothing if config is wrong:
            self.UI.display('Incorrect caster parameters. '
                            'Using hardcoded defaults.')
            self.UI.exception_handler()
            return None

    def get_interface_settings(self, interfaceID):
        """get_interface_settings(interfaceID):

        Reads a configuration file and gets interface parameters.

        If the config file is correct, it returns a list:
        [emergencyGPIO, sensorGPIO, mcp0Address, mcp1Address, pinBase]

        emergencyGPIO - BCM number for emergency stop button GPIO
        sensorGPIO        - BCM number for sensor GPIO
        mcp0Address     - I2C address for 1st MCP23017
        mcp1Address     - I2C address for 2nd MCP23017
        pinBase             - pin numbering base for GPIO outputs on MCP23017

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

        interfaceID    mcp0 pin        mcp1 pin        mcp0         mcp1
                       A2,A1,A0        A2,A1,A0        addr         addr
        0              000             001             0x20         0x21
        1              010             011             0x22         0x23
        2              100             101             0x24         0x25
        3              110             111             0x26         0x27

        where 0 means the pin is pulled down, and 1 means pin pulled up.

        As for pinBase parameter, it's the wiringPi's way of identifying GPIOs
        on MCP23017 extenders. WiringPi is an abstraction layer which allows
        you to control (read/write) pins on MCP23017 just like you do it on
        typical Raspberry Pi's GPIO pins. Thus you don't have to send bytes
        to registers.
        The initial 64 GPIO numbers are reserved for Broadcom SoC,
        so the lowest pin base you can use is 65.
        Each interface (2xMCP23017) uses 32 pins.

        If you are using multiple interfaces per Raspberry, you SHOULD
        assign the following pin bases to each interface:

        interfaceID        pinBase
        0                  65
        1                  98                  (pinBase0 + 32)
        2                  131                 (pinBase1 + 32)
        3                  164                 (pinBase2 + 32)
        """
        interfaceName = 'Interface' + str(interfaceID)
        try:
        # Check if the interface is active, else return None
            trueAliases = ['true', '1', 'on', 'yes']
            if self.cfg.get(interfaceName, 'active').lower() in trueAliases:
                if self.is_caster:
                # Emergency stop and sensor are valid only for casters,
                # perforators do not have them
                    emergencyGPIO = self.cfg.get(interfaceName, 'stop_gpio')
                    sensorGPIO = self.cfg.get(interfaceName, 'sensor_gpio')
                mcp0Address = self.cfg.get(interfaceName, 'mcp0_address')
                mcp1Address = self.cfg.get(interfaceName, 'mcp1_address')
                pinBase = self.cfg.get(interfaceName, 'pin_base')

            # Check which signals arrangement the interface uses...
                signalsArrangement = self.cfg.get(interfaceName, 'signals_arr')
                """...and get the signals order for it:"""
                signalsArrangement = self.cfg.get('SignalsArrangements',
                                                  signalsArrangement)
                if self.is_caster:
                # Return parameters for a caster
                    return [int(emergencyGPIO), int(sensorGPIO),
                            int(mcp0Address, 16), int(mcp1Address, 16),
                            int(pinBase), signalsArrangement]
                else:
                # Return parameters for a perforator - no sensor or emerg. stop
                    return [int(mcp0Address, 16), int(mcp1Address, 16),
                            int(pinBase), signalsArrangement]
            else:
            # This happens if the interface is inactive in conffile:
                self.UI.display('Interface %i is marked as inactive!'
                                % interfaceID)
                return None
        except (ConfigParser.NoSectionError,
                ConfigParser.NoOptionError,
                ValueError, TypeError):
            self.UI.display('Incorrect interface parameters. '
                            'Using hardcoded defaults.')
            self.UI.exception_handler()
            return None

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
        self.UI = TextUI()
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
        # Look database path up in conffile:
            try:
                self.databasePath = config.get('Database', 'path')
            except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            # Revert to defaults if database not configured properly:
                self.databasePath = 'database/monotype.db'
                self.UI.debug_info('Database path not found in conffile. '
                                   'Using default:', self.databasePath)

    def add_wedge(self, wedgeName, setWidth, britPica, steps):
        """add_wedge(wedgeName, setWidth, britPica, steps):

        Registers a wedge in our database.
        Returns True if successful, False otherwise.

        Arguments:
        wedgeName - wedge's number, e.g. S5 or 1160. String, cannot be null.
        setWidth - set width of a wedge, e.g. 9.75. Float, cannot be null.
        britPica - 1 or True if it's a British pica system (1pica = 0.1667")
        0 or False if it's an American pica system (1pica = 0.1660")

        If the wedge has "E" at the end of its number (e.g. 5-12E),
        then it was made for European countries which used Didot points
        and ciceros (1cicero = 0.1776"), but the unit calculations were all
        based on the British pica.

        steps - a wedge's unit arrangement - list of unit values for each
        of the wedge's steps (i.e. diecase rows). Cannot be null.

        An additional column, id, will be created and auto-incremented.
        This will be an unique identifier of a wedge.
        """

        # data - a list with wedge parameters to be written,
        # a unit arrangement (list of wedge's steps) is JSON-encoded
        data = [wedgeName, setWidth, str(britPica), json.dumps(steps)]
        with self.db:
            try:
                cursor = self.db.cursor()
            # Create the table first:
                cursor.execute('CREATE TABLE IF NOT EXISTS wedges ('
                               'id INTEGER PRIMARY KEY ASC AUTOINCREMENT, '
                               'wedge_id TEXT NOT NULL, '
                               'set_width REAL NOT NULL, '
                               'brit_pica TEXT NOT NULL, '
                               'steps TEXT NOT NULL)')
            # Then add an entry:
                cursor.execute('''INSERT INTO wedges (
                                  wedge_id,set_width,old_pica,steps
                                  ) VALUES (?, ?, ?, ?)''', data)
                self.db.commit()
                return True
            except:
            # In debug mode, display exception code & stack trace.
                self.UI.display('Database error: cannot add wedge!')
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
        britPica - bool - whether this is an old-pica ("E") wedge or not,
        steps - list of unit values for all wedge's steps.

        Else, function returns False.
        """
        with self.db:
            try:
                cursor = self.db.cursor()
                cursor.execute('SELECT * FROM wedges '
                               'WHERE wedge_id = ? AND set_width = ?',
                               [wedgeName, setWidth])
                wedge = cursor.fetchone()
                if wedge is None:
                    self.UI.display('No wedge %s - %f found in database!'
                                    % (wedgeName, setWidth))
                    return False
                else:
                    wedge = list(wedge)
                    self.UI.display('Wedge %s-%fset found in database - OK'
                                    % (wedgeName, setWidth))
                # Change return value of britPica to boolean:
                    wedge[3] = bool(wedge[3])
                # Change return value of steps to list:
                    wedge[4] = json.loads(wedge[4])
                # Return [ID, wedgeName, setWidth, britPica, steps]:
                    return wedge
            except:
            # In debug mode, display exception code & stack trace.
                self.UI.display('Database error: cannot get wedge!')
                self.UI.exception_handler()

    def wedge_by_id(self, ID):
        """wedge_by_id(ID):

        Gets parameters for a wedge with given ID.

        If so, returns:
        ID - unique, int (e.g. 0),
        wedgeName - string (e.g. S5) - wedge name
        setWidth - float (e.g. 9.75) - set width,
        britPica - bool - whether this is a British pica wedge or not,
        steps - list of unit values for all wedge's steps.

        Else, returns False.
        """
        with self.db:
            try:
                cursor = self.db.cursor()
                cursor.execute('SELECT * FROM wedges WHERE id = ? ', [ID])
                wedge = cursor.fetchone()
                if wedge is None:
                    self.UI.display('Wedge not found!')
                    return False
                else:
                    wedge = list(wedge)
                # Change return value of britPica to boolean:
                    wedge[3] = bool(wedge[3])
                # Change return value of steps to list:
                    wedge[4] = json.loads(wedge[4])
                    """Return [ID, wedgeName, setWidth, britPica, steps]:"""
                    return wedge
            except:
            # In debug mode, display exception code & stack trace.
                self.UI.display('Database error: cannot get wedge!')
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
                    cursor.execute('DELETE FROM wedges WHERE id = ?', [ID])
                    return True
                except:
                # In debug mode, display exception code & stack trace.
                    self.UI.display('Database error: cannot delete wedge!')
                    self.UI.exception_handler()
                    return False
        else:
            self.UI.display('Nothing to delete.')
            return False

    def list_wedges(self):
        """list_wedges(self):

        Lists all wedges stored in database, with their step unit values.

        Prints the following to stdout:

        ID - unique, int (e.g. 0),
        wedgeName - string (e.g. S5) - wedge name
        setWidth - float (e.g. 9.75) - set width,
        britPica - bool - whether this is an old-pica ("E") wedge or not,
        steps - list of unit values for all wedge's steps.

        Returns True if successful, False otherwise.
        """
        with self.db:
            try:
                cursor = self.db.cursor()
                cursor.execute('SELECT * FROM wedges')
                header = ('\n' + 'ID'.center(10)
                          + 'wedge No'.center(10)
                          + 'Brit. pica'.center(10)
                          + 'unit arrangement'
                          + '\n')
                self.UI.display(header)
                while True:
                    wedge = cursor.fetchone()
                    if wedge is not None:
                        record = ''
                        for field in wedge:
                            record += str(field).ljust(10)
                        self.UI.display(record)
                    else:
                        break
                return True
            except:
            # In debug mode, display exception code & stack trace."""
                self.UI.display('Database error: cannot list wedges!')
                self.UI.exception_handler()
                return False

    def diecase_by_series_and_size(self, typeSeries, typeSize):
        """diecase_by_series_and_size(typeSeries, typeSize):

        Searches for diecase metadata, based on the desired type series
        and size. Allows to choose one of the diecases found.
        """
        with self.db:
            try:
                cursor = self.db.cursor()
                cursor.execute('SELECT * FROM diecases '
                               'WHERE type_series = "%s" AND size = %i',
                               (typeSeries, typeSize))
            # Initialize a list of matching diecases:
                matches = []
                while True:
                    diecase = cursor.fetchone()
                    if diecase is not None:
                        diecase = list(diecase)
                        matches.append(diecase)
                    else:
                        break
                if not matches:
                # List is empty. Notify the user:
                    self.UI.display('Sorry - no results found.')
                    time.sleep(1)
                    return False
                elif len(matches) == 1:
                    return matches[0]
                else:
                # More than one match - decide which one to use:
                    IDs = []
                    for diecase in matches:
                        IDs.append(diecase[0])
                # Display a menu with diecases from 1 to the last:
                    options = dict(zip(range(1, len(matches) + 1), IDs))
                    header = 'Choose a diecase:'
                    choice = self.UI.menu(options, header)
                # Return a list with chosen diecase's parameters:
                    return options[choice]
            except:
            # In debug mode, display exception code & stack trace.
                self.UI.display('Database error: cannot find diecase data!')
                self.UI.exception_handler()
                return False

    def diecase_by_id(self, diecaseID):
        """diecase_by_id(diecaseID):

        Searches for diecase metadata, based on the unique diecase ID.
        """
        with self.db:
            try:
                cursor = self.db.cursor()
                cursor.execute('SELECT * FROM diecases WHERE id = "%s"'
                               % diecaseID)
            # Return diecase if found:
                diecase = cursor.fetchone()
                if diecase is not None:
                    diecase = list(diecase)
                    return diecase
                else:
                # Otherwise, notify the user, return False:
                    self.UI.display('Sorry - no results found.')
                    time.sleep(1)
                    return False
            except:
            # In debug mode, display exception code & stack trace.
                self.UI.display('Database error: cannot find diecase data!')
                self.UI.exception_handler()
                return False

    def __exit__(self, *args):
        self.UI.debug_info('Exiting database context.')
        pass


class Inventory(object):
    """Inventory management class:

    Used for configuring the Monotype workshop inventory:
    -wedges
    -diecases
    -diecase layouts.
    """

    def __init__(self):
        self.UI = TextUI()

    def __enter__(self):
        self.UI.debug_info('Entering inventory management job context...')
        return self

    # Placeholders for functionality not implemented yet:
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

    def add_wedge(self, wedgeName='', setWidth='', britPica=None, steps=''):
        """add_wedge(wedgeName, setWidth, britPica, steps)

        Used for adding wedges.

        Can be called with or without arguments.

        wedgeName - string - series name for a wedge (e.g. S5, S111)
        setWidth  - float - set width of a particular wedge (e.g. 9.75)
        britPica - boolean - whether the wedge is based on British pica
        (0.1667") or not (American pica - 0.1660")
        True if the wedge is for European market ("E" after set width number)
        steps - string with unit values for steps - e.g. '5,6,7,8,9,9,9...,16'

        Start with defining the unit arrangements for some known wedges.
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

        In this program, all wedges have the "S" (for stopbar) letter
        at the beginning of their designation. However, the user can enter
        a designation with or without "S", so check if it's there, and
        append if needed (only for numeric designations - not the "monospace"
        or other text values!)

        If no name is given, assume that the user means the S5 wedge, which is
        very common and most casting workshops have a few of them.
        """
        wedgeData = {'S5'     : '5,6,7,8,9,9,9,10,10,11,12,13,14,15,18,18',
                     'S96'    : '5,6,7,8,9,9,10,10,11,12,13,14,15,16,18,18',
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
                     'MONOSPACE' : '9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9'}
        # Enter the wedge name:
        while not wedgeName:
            wedgeName = self.UI.enter_data('Enter the wedge name, e.g. S5 '
                                           '(very typical, default): ')
            if not wedgeName:
                wedgeName = 'S5'
            elif wedgeName[0].upper() is not 'S' and wedgeName.isdigit():
                wedgeName = 'S' + wedgeName
            wedgeName = wedgeName.upper()
        # Enter the set width:
        while not setWidth:
            prompt = 'Enter the wedge set width as decimal, e.g. 9.75E: '
            setWidth = self.UI.enter_data(prompt)
        # Determine if it's a British pica wedge automatically - E is present:
        if setWidth[-1].upper() == 'E':
            setWidth = setWidth[:-1]
            britPica = True
        elif britPica is None:
        # Otherwise, let user choose if it's American or British pica:
            options = {'A' : False, 'B' : True}
            message = '[A]merican (0.1660"), or [B]ritish (0.1667") pica? '
            choice = self.UI.simple_menu(message, options).upper()
            britPica = options[choice]
        try:
            setWidth = float(setWidth)
        except ValueError:
            setWidth = 12
        # Enter the wedge unit arrangement for steps 1...15 (optionally 16):
        while not steps:
        # Check if we have the values hardcoded already:
            try:
                rawSteps = wedgeData[wedgeName]
            except (KeyError, ValueError):
            # No wedge - enter data manually:
                prompt = ('Enter the wedge unit values for steps 1...16, '
                          'separated by commas. If empty, entering values '
                          'for wedge S5 (very common): ')
                rawSteps = self.UI.enter_data(prompt)
                if not rawSteps:
                    rawSteps = wedgeData['S5']
            rawSteps = rawSteps.split(',')
            steps = []
        # Now we need to be sure that all whitespace is stripped,
        # and the value written to database is a list of integers
            for step in rawSteps:
                step = int(step.strip())
                steps.append(step)
        # Display warning if the number of steps is anything other than
        # 15 or 16 (15 is most common, 16 was used for HMN and KMN systems).
        # If length is correct, tell user it's OK.
            warnMin = ('Warning: the wedge you entered has less than 15 steps!'
                       '\nThis is almost certainly a mistake.\n')
            warnMax = ('Warning: the wedge you entered has more than 16 steps!'
                       '\nThis is almost certainly a mistake.\n')
            stepsOK = ('The wedge has ', len(steps), 'steps. That is OK.')
            if len(steps) < 15:
                self.UI.display(warnMin)
            elif len(steps) > 16:
                self.UI.display(warnMax)
            else:
                self.UI.display(stepsOK)
        # Display a summary:
        summary = {'Wedge' : wedgeName,
                   'Set width' : setWidth,
                   'British pica wedge?' : britPica}
        for parameter in summary:
            self.UI.display(parameter, ':', summary[parameter])
        # Loop over all unit values in wedge's steps and display them:
        for i, step in zip(range(len(steps)), steps):
            self.UI.display('Step', i+1, 'unit value:', step, '\n')
        # Subroutines:
        def commit_wedge():
            if self.database.add_wedge(wedgeName, setWidth, britPica, steps):
                self.UI.display('Wedge added successfully.')
            else:
                self.UI.display('Failed to add wedge!')
        def reenter():
            self.UI.enter_data('Enter parameters again from scratch... ')
            self.add_wedge()
        # Confirmation menu:
        message = ('\nCommit wedge to database? \n'
                   '[Y]es / [N]o (enter values again) / return to [M]enu: ')
        options = {'Y' : commit_wedge, 'N' : reenter, 'M' : self.main_menu}
        ans = self.UI.simple_menu(message, options).upper()
        options[ans]()

    def delete_wedge(self):
        """Used for deleting a wedge from database.
        """
        self.list_wedges()
        ID = self.UI.enter_data('Enter the wedge ID to delete: ')
        if ID.isdigit():
            ID = int(ID)
            if self.database.delete_wedge(ID):
                self.UI.display('Wedge deleted successfully.')
        else:
            self.UI.display('Wedge ID must be a number!')

    def list_wedges(self):
        """lists all wedges we have
        """
        self.database.list_wedges()

    def main_menu(self):
        options = {1 : 'List matrix cases',
                   2 : 'Show matrix case layout',
                   3 : 'Add a new, empty matrix case',
                   4 : 'Edit matrix case layout',
                   5 : 'Clear matrix case layout',
                   6 : 'Delete matrix case',
                   7 : 'List wedges',
                   8 : 'Add wedge',
                   9 : 'Delete wedge',
                   0 : 'Exit program'}
        commands = {1 : self.list_diecases,
                    2 : self.show_diecase_layout,
                    3 : self.add_diecase,
                    4 : self.edit_diecase,
                    5 : self.clear_diecase,
                    6 : self.delete_diecase,
                    7 : self.list_wedges,
                    8 : self.add_wedge,
                    9 : self.delete_wedge,
                    0 : self.UI.exit_program}
        h = 'Setup utility for rpi2caster CAT.\nMain menu:'
        choice = self.UI.menu(options, header=h, footer='')
        # Execute it!
        with self.database:
            commands[choice]()
        self.UI.hold_on_exit()
        self.main_menu()

    def __exit__(self, *args):
        self.UI.debug_info('Exiting inventory management job context.')
        pass


class Monotype(object):
    """Monotype(job, name, confFilePath):

    A class which stores all hardware-layer methods, related to caster control.
    This class requires a caster name, and a database object.
    """

    def __init__(self, name='Monotype'):
        """Creates a caster object for a given caster name
        """
        self.UI = TextUI()
        self.name = name
        # It's not configured yet - we'll do it when needed, and only once:
        self.configured = False

    def __enter__(self):
        """Run the setup when entering the context:
        """
        self.UI.debug_info('Entering caster/interface context...')
        # Configure the interface if it needs it:
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
        # Default caster parameters:
        self.interfaceID = 0
        self.unitAdding = 0
        self.diecaseSystem = 'norm17'
        # Default interface parameters:
        self.emergencyGPIO = 18
        self.sensorGPIO = 24
        self.mcp0Address = 0x20
        self.mcp1Address = 0x21
        self.pinBase = 65
        self.signalsArrangement = ('1,2,3,4,5,6,7,8,9,10,11,12,13,14,0005,'
                                   '0075,A,B,C,D,E,F,G,H,I,J,K,L,M,N,S,O15')
        # Next, this method reads caster data from database and fetches
        # a list of caster parameters: diecaseFormat, unitAdding, interfaceID.
        # In case there is no data, the function will run on default settings.
        settings = self.config.get_caster_settings(self.name)
        try:
            [self.unitAdding, self.diecaseSystem, self.interfaceID] = settings
        except:
            pass
        # When debugging, display all caster info:
        self.UI.debug_info('\nCaster parameters:\n')
        output = {'Using caster name: ' : self.name,
                  'Diecase system: ' : self.diecaseSystem,
                  'Has unit-adding attachement? ' : self.unitAdding,
                  'Interface ID: ' : self.interfaceID}
        for parameter in output:
            self.UI.debug_info(parameter, output[parameter])
        # Call a config method to get interface settings,
        # otherwise revert to defaults.
        interfaceSettings = self.config.get_interface_settings(self.interfaceID)
        try:
            [self.emergencyGPIO, self.sensorGPIO,
             self.mcp0Address, self.mcp1Address,
             self.pinBase, self.signalsArrangement] = interfaceSettings
        except:
            pass
        # Print the parameters for debugging:
        self.UI.debug_info('\nInterface parameters:\n')
        output = {'Emergency button GPIO: ' : self.emergencyGPIO,
                  'Sensor GPIO: ' : self.sensorGPIO,
                  '1st MCP23017 I2C address: ' : self.mcp0Address,
                  '2nd MCP23017 I2C address: ' : self.mcp1Address,
                  'MCP23017 pin base for GPIO numbering: ' : self.pinBase,
                  'Signals arrangement: ' : self.signalsArrangement}
        for parameter in output:
            self.UI.debug_info(parameter, output[parameter])
        # Set up an input for machine cycle sensor:
        gpioSysfsPath = '/sys/class/gpio/gpio%s/' % self.sensorGPIO
        self.sensorGPIOValueFile = gpioSysfsPath + 'value'
        self.sensorGPIOEdgeFile = gpioSysfsPath + 'edge'
        # Check if the sensor GPIO has been configured - file is readable:
        try:
            with open(self.sensorGPIOValueFile, 'r'):
                pass
        except IOError:
            message = ('%s : file does not exist or cannot be read. '
                       'You must export the GPIO no %s as input first!'
                       % (self.sensorGPIOValueFile, self.sensorGPIO))
            self.UI.display(message)
            self.UI.exit_program()
        # Ensure that the interrupts are generated for sensor GPIO
        # for both rising and falling edge:
        with open(self.sensorGPIOEdgeFile, 'r') as edgeFile:
            if 'both' not in edgeFile.read():
                message = ('%s: file does not exist, cannot be read, '
                           'or the interrupt on GPIO %i is not set to "both". '
                           'Check the system config.'
                           % (self.sensorGPIOEdgeFile, self.sensorGPIO))
                self.UI.display(message)
                self.UI.exit_program()
        # Setup the wiringPi MCP23017 chips for valve outputs
        wiringpi.mcp23017Setup(self.pinBase, self.mcp0Address)
        wiringpi.mcp23017Setup(self.pinBase + 16, self.mcp1Address)
        pins = range(self.pinBase, self.pinBase + 32)
        # Set all I/O lines on MCP23017s as outputs - mode=1
        for pin in pins:
            wiringpi.pinMode(pin, 1)
        # Make a nice list out of the signal arrangement string:
        signalsArrangement = self.signalsArrangement.split(',')
        # Assign wiringPi pin numbers on MCP23017s to the Monotype
        # control signals
        self.wiringPiPinNumber = dict(zip(signalsArrangement, pins))
        # Mark the caster as configured
        self.configured = True
        # Wait for user confirmation if in debug mode
        self.UI.debug_enter_data('Caster configured. [Enter] to continue... ')

    def perforator_setup(self):
        """Perforator setup routine:

        A simplified interface with no machine cycle sensor is used
        for controlling a perforator, i.e. a paper tower taken off a Monotype
        keyboard and used for punching the paper tape. This is useful if you
        want to make some tape with composed text for someone who has a caster
        but cannot make a ribbon because they have no keyboard
        or necessary parts (keybar, stopbar, justifying scale).

        The perforator interface has outputs only, and does not rely on
        any GPIOs, apart from the I2C interface and MCP23017 chips.
        """
        self.interfaceID = 0
        self.mcp0Address = 0x20
        self.mcp1Address = 0x21
        self.pinBase = 65
        self.signalsArrangement = ('1,2,3,4,5,6,7,8,9,10,11,12,13,14,0005,'
                                   '0075,A,B,C,D,E,F,G,H,I,J,K,L,M,N,S,O15')
        # Next, this method reads data from config file and overrides the
        # default interface parameters for an object
        settings = self.config.get_settings_from_conffile(self.name)
        # Check if we got anything - if so, set parameters for object
        try:
            (self.interfaceID, self.mcp0Address, self.mcp1Address,
             self.pinBase, self.signalsArrangement) = settings
        except (NameError, ValueError):
            return False
        # Print the parameters for debugging
        self.UI.debug_info('\nInterface parameters:\n')
        output = {'Interface ID: ' : self.interfaceID,
                  '1st MCP23017 I2C address: ' : self.mcp0Address,
                  '2nd MCP23017 I2C address: ' : self.mcp1Address,
                  'MCP23017 pin base for GPIO numbering: ' : self.pinBase,
                  'Signals arrangement: ' : self.signalsArrangement}
        for parameter in output:
            self.UI.debug_info(parameter, output[parameter])
        # Set up the wiringPi MCP23017 chips for valve outputs
        wiringpi.mcp23017Setup(self.pinBase, self.mcp0Address)
        wiringpi.mcp23017Setup(self.pinBase + 16, self.mcp1Address)
        pins = range(self.pinBase, self.pinBase + 32)
        # Set all I/O lines on MCP23017s as outputs - mode=1
        for pin in pins:
            wiringpi.pinMode(pin, 1)
        # Make a nice list out of signal arrangement string
        signalsArrangement = self.signalsArrangement.split(',')
        # Assign wiringPi pin numbers on MCP23017s to the Monotype signals
        self.wiringPiPinNumber = dict(zip(signalsArrangement, pins))
        # Mark the perforator interface as configured
        self.configured = True
        # Wait for user confirmation
        prompt = 'Interface configured. [Enter] to continue... '
        self.UI.debug_enter_data(prompt)
        return True

    def detect_rotation(self):
        """detect_rotation():

        Checks if the machine is running by counting pulses on a sensor
        input. One pass of a while loop is a single cycle. If cycles_max
        value is exceeded in a time <= time_max, the program assumes that
        the caster is rotating and it can start controlling the machine.
        """
        cycles = 0
        cycles_max = 3
        # Let's give it 30 seconds timeout
        time_start = time.time()
        time_max = 30
        # Check for sensor signals, keep checking until max time is exceeded
        # or target number of cycles is reached
        with open(self.sensorGPIOValueFile, 'r') as gpiostate:
            while time.time() <= time_start + time_max and cycles <= cycles_max:
                sensorSignals = select.epoll()
                sensorSignals.register(gpiostate, select.POLLPRI)
                events = sensorSignals.poll(0.5)
            # Check if the sensor changes state at all
                if events:
                    gpiostate.seek(0)
                    sensorState = int(gpiostate.read())
                    previousState = 0
                # Increment the number of passed machine cycles
                    if sensorState == 1 and previousState == 0:
                        previousState = 1
                        cycles += 1
                    elif sensorState == 0 and previousState == 1:
                        previousState = 0
            else:
            # Determine if the loop ended due to timeout (machine not running)
            # or exceeded number of cycles (machine running):
                if cycles > cycles_max:
                    self.UI.display('\nOkay, the machine is running...\n')
                    return True
                else:
                    self.machine_stopped()
                # Check again:
                    self.detect_rotation()

    def send_signals_to_caster(self, signals, machineTimeout=5):
        """send_signals_to_caster(signals, machineTimeout):

        Checks for the machine's rotation, sends the signals (activates
        solenoid valves) after the caster is in the "air bar down" position.

        If no machine rotation is detected (sensor input doesn't change
        its state) during machineTimeout, calls a function to ask user
        what to do (can be useful for resuming casting after manually
        stopping the machine for a short time - not recommended as the
        mould cools down and type quality can deteriorate).

        When casting, the pace is dictated by the caster and its RPM. Thus,
        we can't arbitrarily set the intervals between valve ON and OFF
        signals. We need to get feedback from the machine, and we can use
        contact switch (unreliable in the long run), magnet & reed switch
        (not precise enough) or a sensor + LED (very precise).
        We can use a paper tower's operating lever for obscuring the sensor
        (like John Cornelisse did), or we can use a partially obscured disc
        attached to the caster's shaft (like Bill Welliver did).
        Both ways are comparable; the former can be integrated with the
        valve block assembly, and the latter allows for very precise tweaking
        of duty cycle (bright/dark area ratio) and phase shift (disc's position
        relative to 0 degrees caster position).

        Detect events on a sensor input, and if a rising or falling edge
        is detected, determine the input's logical state (high or low).
        If high - check if it was previously low to be sure. Then send
        all signals passed as an argument (tuple or list).
        In the next cycle, turn all the valves off and exit the loop.
        Set the previous state each time the valves are turned on or off.
        """
        with open(self.sensorGPIOValueFile, 'r') as gpiostate:
            po = select.epoll()
            po.register(gpiostate, select.POLLPRI)
            previousState = 0
            while True:
            # Polling the interrupt file
                events = po.poll(machineTimeout)
                if events:
                # Be sure that the machine is working!
                    gpiostate.seek(0)
                    sensorState = int(gpiostate.read())
                    if sensorState == 1 and previousState == 0:
                    # Now, the air bar on paper tower would go down -
                    # we got signal from sensor to let the air in
                        self.activate_valves(signals)
                        previousState = 1
                    elif sensorState == 0 and previousState == 1:
                    # Air bar on paper tower goes back up -
                    # end of "air in" phase, turn off the valves
                        self.deactivate_valves()
                        previousState = 0
                        break
                else:
                # No events? That would mean that the machine has stopped,
                # usually because of emergency. Ask user what to do.
                    self.machine_stopped()

    def activate_valves(self, signals):
        """activate_valves(signals):

        Activates the solenoid valves connected with interface's outputs,
        as specified in the "signals" parameter (tuple or list).
        The input array "signals" contains strings, either
        lowercase (a, b, g, s...) or uppercase (A, B, G, S...).
        Do nothing if the function receives an empty sequence, which will
        occur if we cast with the matrix found at position O15.
        """
        if signals:
            for monotypeSignal in signals:
                pin = self.wiringPiPinNumber[monotypeSignal]
                wiringpi.digitalWrite(pin, 1)

    def deactivate_valves(self):
        """deactivate_valves():

        Turn all valves off after casting/punching any character.
        Call this function to avoid outputs staying turned on if something
        goes wrong, esp. in case of abnormal program termination.
        """
        for pin in range(self.pinBase, self.pinBase + 32):
            wiringpi.digitalWrite(pin, 0)

    def emergency_stop_kicked_in(self):
        """emergency_stop_kicked_in():

        If the machine is stopped, we need to turn the pump off and then turn
        all the lines off. Otherwise, the machine will keep pumping
        while it shouldnot (e.g. after a splash).

        The program will hold execution until the operator clears the situation,
        it needs turning the machine at least one full revolution.
        """
        self.UI.display('Stopping the pump...')
        self.send_signals_to_caster(['N', 'J', '0005'])
        self.UI.display('Pump stopped. All valves off...')
        self.deactivate_valves()
        time.sleep(1)

    def machine_stopped(self):
        """machine_stopped():

        This allows us to choose whether we want to continue, return to menu
        or exit if the machine is stopped during casting.
        """
        def continue_casting():
        # Helper function - continue casting.
            pass
        def return_to_menu():
        # Make sure pump is off and no valves are activated.
            self.emergency_stop_kicked_in()
            self.job.main_menu()
        def exit_program():
        # Make sure pump is off and no valves are activated.
            self.emergency_stop_kicked_in()
            self.UI.exit_program()
        # Display a menu for the user to decide what to do
        options = {'C' : continue_casting,
                   'M' : return_to_menu,
                   'E' : exit_program}
        message = ("Machine not running! Check what's going on.\n"
                   "[C]ontinue, return to [M]enu or [E]xit program? ")
        choice = self.UI.simple_menu(message, options).upper()
        options[choice]()

    def cleanup(self):
        """cleanup():

        Turn all valves off, then set all lines on MCP23017 as inputs.
        TODO: implement GPIO unsetting after wiringpi2-python gets it done.
        """
        self.UI.debug_info('Cleaning up: turning all pins off...')
        for pin in range(self.pinBase, self.pinBase + 32):
            wiringpi.digitalWrite(pin, 0)
        # Wait for user confirmation in debug mode
        self.UI.debug_enter_data('Press [Enter] to continue... ')

    def __exit__(self, *args):
        """On exit, do the cleanup:
        """
        self.UI.debug_info('Exiting caster/interface context.')
        self.cleanup()


class MonotypeSimulation(object):
    """MonotypeSimulation:

    A class which allows to test rpi2caster without an actual interface
    or caster. Most functionality will be developped without an access
    to the machine.
    """

    def __init__(self, name='Monotype Simulator'):
        self.UI = TextUI()
        self.name = name

    def __enter__(self):
        self.UI.debug_info('Entering caster/keyboard simulation context...')
        # Display some info
        self.UI.display('Using caster name:', self.name)
        self.UI.display('This is not an actual caster or interface. ')
        self.UI.enter_data('Press [ENTER] to continue...')
        # Debugging is ON by default
        self.UI.debugMode = True
        return self

    def send_signals_to_caster(self, signals, machineTimeout=5):
        """Simulates sending signals to the caster.

        Just wait for feedback from user, as we don't have a sensor.
        """
        self.UI.enter_data('Press [ENTER] to simulate sensor going ON')
        self.activate_valves(signals)
        self.UI.enter_data('Press [ENTER] to simulate sensor going OFF')
        self.deactivate_valves()

    def activate_valves(self, signals):
        """If there are any signals, print them out"""
        if len(signals) != 0:
            message = ('The valves: %s would be activated now.'
                       % ' '.join(signals))
            self.UI.display(message)

    def deactivate_valves(self):
        """No need to do anything"""
        self.UI.display('The valves would be deactivated now.')

    def detect_rotation(self):
        """Detect rotation:

        FIXME: implement raw input breaking on timeout"""
        '''TODO: make this function work...
        self.UI.debug_info('Now, the program would check if the machine '
                           'is rotating.\n')
        startTime = time.time()
        answer = None
        while answer is None and time.time() < (startTime + 5):
            prompt = ('Press [ENTER] (to simulate rotation) '
                      'or wait 5sec (to simulate machine off)\n')
            answer = self.UI.enter_data(prompt)
        else:
            self.machine_stopped()
            """Recurse:"""
            self.detect_rotation()
        '''
        pass

    def machine_stopped(self):
        """Machine stopped:

        This allows us to choose whether we want to continue, return to menu
        or exit if the machine is stopped during casting.
        """
        def continue_casting():
        # Helper function - continue casting.
            return True
        options = {'C' : continue_casting,
                   'M' : self.job.main_menu,
                   'E' : self.UI.exit_program}
        message = ('Machine not running! Check what happened.\n'
                   '[C]ontinue, return to [M]enu or [E]xit program? ')
        choice = self.UI.simple_menu(message, options).upper()
        options[choice]()

    def __exit__(self, *args):
        self.deactivate_valves()
        self.UI.debug_info('Exiting caster/keyboard simulation context.')
        pass


class Casting(object):
    """Casting:

    Methods related to operating the composition caster.
    Requires configured:
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
    -casting spaces to heat up the mould."""

    def __init__(self, ribbonFile=''):
        self.UI = TextUI()
        self.ribbonFile = ribbonFile

    def __enter__(self):
        self.UI.debug_info('Entering casting job context...')
        return self

    def cast_composition(self):
        """cast_composition()

        Composition casting routine. The input file is read backwards -
        last characters are cast first, after setting the justification.
        """
        # First, read the file contents
        contents = parsing.read_file(self.ribbonFile)
        # If file read failed, end here
        if not contents:
            self.UI.display('Error reading file!')
            time.sleep(1)
            return False
        # Count all characters and lines in the ribbon
        [linesAll, charsAll] = parsing.count_lines_and_characters(contents)
        # Characters already cast - start with zero
        currentChar = 0
        charsLeft = charsAll
        # Line currently cast: since the caster casts backwards
        # (from the last to the first line), this will decrease.
        currentLine = linesAll
        # The program counts galley trip sequences and determines line count.
        # The first code to send to machine is galley trip (which also sets the
        # justification wedges and turns the pump on). So, subtract this one
        # to have the correct number of lines.
        linesAll -= 1
        # Show the numbers to the operator
        self.UI.display('Lines found in ribbon: %i' % linesAll)
        self.UI.display('Characters: %i' % charsAll)
        # For casting, we need to read the contents in reversed order
        contents = reversed(contents)
        # Display a little explanation
        intro = ('\nThe combinations of Monotype signals will be displayed '
                 'on screen while the machine casts the type.\n'
                 'Turn on the machine and the program will start.\n')
        self.UI.display(intro)
        # Start only after the machine is running
        self.caster.detect_rotation()
        # Read the reversed file contents, line by line, then parse
        # the lines, display comments & code combinations, and feed the
        # combinations to the caster
        for line in contents:
        # Parse the row, return a list of signals and a comment.
        # Both can have zero or positive length.
            [rawSignals, comment] = parsing.comments_parser(line)
        # Parse the signals
            signals = parsing.signals_parser(rawSignals)
            if parsing.check_newline(signals):
                currentLine -= 1
            # % of all lines done:
                linePercentDone = 100 * (linesAll - currentLine) / linesAll
            elif parsing.check_character(signals):
                currentChar += 1
                charsLeft -= 1
            # % of chars to cast in the line
                charPercentDone = 100 * currentChar / charsAll
            # A string with information for user: signals, comments, etc.
            userInfo = ''
            if parsing.check_newline(signals):
            # If starting a new line - display number of the working line,
            # number of all remaining lines, % done
                userInfo += ('Starting line: %i of %i, %i%% done...\n'
                             % (currentLine, linesAll, linePercentDone))
            elif parsing.check_character(signals):
            # If casting a character - display number of chars done,
            # number of all and remaining chars, % done
                userInfo += ('Casting character: %i / %i, '
                             '%i remaining, %i%% done...\n'
                             % (currentChar, charsAll,
                                charsLeft, charPercentDone))
        # Append signals to be cast
            if signals:
                userInfo += ' '.join(signals).ljust(15)
        # Add comment
            userInfo += comment
        # Display the info
            self.UI.display(userInfo)
        # If we have signals - cast them
            if signals:
        # Now check if we had O, 15 and strip them, then cast the combination
                signals = parsing.strip_O_and_15(signals)
                self.caster.send_signals_to_caster(signals)
        # After casting is finished, notify the user
        self.UI.display('\nCasting finished!')
        return True

    def punch_composition(self):
        """punch_composition():

        When punching, the input file is read forwards. An additional line
        (O+15) is switched on for operating the paper tower, if less than
        two signals are found in a sequence.

        We can't use automatic machine cycle detection like we do in
        cast_composition, because keyboard's paper tower doesn't run
        by itself - it must get air into tubes to operate, punches
        the perforations, and doesn't give any feedback.

        For punching, O+15 are needed if <2 lines are active.
        That's because of how the keyboard's paper tower is built -
        it has a balance mechanism that advances paper tape only if two
        signals can outweigh constant air pressure on the other side.
        Basically: less than two signals - no ribbon advance...
        """
        # First, read the file contents
        contents = parsing.read_file(self.ribbonFile)
        # If file read failed, end here
        if not contents:
            self.UI.display('Error reading file!')
            time.sleep(1)
            return False
        # Count a number of combinations punched in ribbon
        combinationsAll = parsing.count_combinations(contents)
        self.UI.display('Combinations in ribbon: %i', combinationsAll)
        # Wait until the operator confirms.
        intro = ('\nThe combinations of Monotype signals will be displayed '
                 'on screen while the paper tower punches the ribbon.\n')
        self.UI.display(intro)
        prompt = ('\nInput file found. Turn on the air, fit the tape '
                  'on your paper tower and press return to start punching.')
        self.UI.enter_data(prompt)
        for line in contents:
        # Parse the row, return a list of signals and a comment.
        # Both can have zero or positive length.
            [rawSignals, comment] = parsing.comments_parser(line)
        # Parse the signals
            signals = parsing.signals_parser(rawSignals)
        # A string with information for user: signals, comments, etc.
            userInfo = ''
        # Add signals to be cast
            if signals:
                userInfo += ' '.join(signals).ljust(20)
        # Add comment
            if comment:
                userInfo += comment
        # Display the info
            self.UI.display(userInfo)
        # Send the signals, adding O+15 whenever needed
            if signals:
            # Convert O or 15 to a combined O+15 signal:"""
                signals = parsing.convert_O15(signals)
                if len(signals) < 2:
                    signals.append('O15')
            # Punch it!"""
                self.caster.activate_valves(signals)
            # The pace is arbitrary, let's set it to 200ms/200ms
                time.sleep(0.2)
                self.caster.deactivate_valves()
                time.sleep(0.2)
        # After punching is finished, notify the user:"""
        self.UI.display('\nPunching finished!')
        return True

    def line_test(self):
        """line_test():

        Tests all valves and composition caster's inputs to check
        if everything works and is properly connected. Signals will be tested
        in order: 0075 - S - 0005, 1 towards 14, A towards N, O+15.
        """
        intro = ('This will check if the valves, pin blocks and 0075, S, '
                 '0005 mechanisms are working. Press return to continue... ')
        self.UI.enter_data(intro)
        combinations = [['0075'], ['S'], ['0005'], ['1'], ['2'], ['3'],
                        ['4'], ['5'], ['6'], ['7'], ['8'], ['9'], ['10'],
                        ['11'], ['12'], ['13'], ['14'], ['A'], ['B'],
                        ['C'], ['D'], ['E'], ['F'], ['G'], ['H'], ['I'],
                        ['J'], ['K'], ['L'], ['M'], ['N'], ['O15']]
        # Send all the combinations to the caster, one by one.
        # Set machine_stopped timeout at 120s.
        for combination in combinations:
            self.UI.display(' '.join(combination))
            self.caster.send_signals_to_caster(combination, 120)
        self.UI.display('\nTesting finished!')

    def cast_sorts(self):
        """cast_sorts():

        Sorts casting routine, based on the position in diecase.
        Ask user about the diecase row & column, as well as number of sorts.
        """
        self.UI.clear()
        self.UI.display('Calibration and Sort Casting:\n\n')
        prompt = 'Enter column and row symbols (default: G 5): '
        signals = self.UI.enter_data(prompt)
        if not signals:
            signals = 'G 5'
        # Ask for number of sorts and lines
        prompt = '\nHow many sorts? (default: 10): '
        n = self.UI.enter_data(prompt)
        # Default to 10 if user enters non-positive number or letters
        if not n.isdigit() or int(n) < 0:
            n = 10
        else:
            n = int(n)
        prompt = '\nHow many lines? (default: 1): '
        lines = self.UI.enter_data(prompt)
        # Default to 10 if user enters non-positive number or letters
        if not lines.isdigit() or int(lines) < 0:
            lines = 1
        else:
            lines = int(lines)
        # Warn if we want to cast too many sorts from a single matrix
        warning = ('Warning: you want to cast a single character more than '
                   '10 times. This may lead to matrix overheating!\n')
        if n > 10:
            self.UI.display(warning)
        # Use a simple menu to ask if the entered parameters are correct
        def cast_it():
        # Subroutine to cast chosen signals and/or repeat.
            self.cast_from_matrix(signals, n, lines)
            options = {'R' : cast_it,
                       'C' : self.cast_sorts,
                       'M' : self.main_menu,
                       'E' : self.UI.exit_program}
            message = ('\nCasting finished!\n '
                       '[R]epeat sequence, [C]hange code, [M]enu or [E]xit? ')
            choice = self.UI.simple_menu(message, options).upper()
            # Execute choice
            options[choice]()
            # End of casting subroutine.
        # After entering parameters, ask the operator if they're OK
        options = {'O' : cast_it,
                   'C' : self.cast_sorts,
                   'M' : self.main_menu,
                   'E' : self.UI.exit_program}
        message = ('Casting %s, %i lines of %i sorts.\n'
                   '[O]K, [C]hange code/quantity, [M]enu or [E]xit? '
                   % (signals, lines, n))
        choice = self.UI.simple_menu(message, options).upper()
        # Execute choice
        options[choice]()

    def cast_from_matrix(self, signals, n=5, lines=1, pos0075=3, pos0005=8):
        """cast_from_matrix(combination, n, pos0075, pos0005):

        Casts n sorts from combination of signals (list),
        with correction wedges if S needle is in action.

        By default, it sets 0075 wedge to 3 and 0005 wedge to 8 (neutral).
        Determines if single justification (0075 only) or double
        justification (0005 + 0075) is used.

        N, K and J signals are for alternate justification scheme,
        used with unit-adding attachment and turned on/off with a large
        IN/OUT valve at the backside of the caster:
        NJ = 0005
        NK = 0075
        NKJ = 0005 + 0075
        """
        combination = parsing.signals_parser(signals)
        combination = parsing.strip_O_and_15(combination)
        pos0005 = str(pos0005)
        pos0075 = str(pos0075)
        # Check if the machine is running first
        self.UI.display('Start the machine...')
        self.caster.detect_rotation()
        # Cast the sorts: set wedges, turn pump on, cast, line out
        for currentLine in range(lines):
            self.UI.display('Castling line %i of %i' % (currentLine + 1, lines))
            self.UI.display('0005 wedge at ' + pos0005)
            self.caster.send_signals_to_caster(['N', 'J', '0005', pos0005])
            self.UI.display('0075 wedge at ' + pos0075)
            self.UI.display('Starting the pump...')
            self.caster.send_signals_to_caster(['N', 'K', '0075', pos0075])
        # Start casting characters
            self.UI.display('Casting characters...')
        # Cast n combinations of row & column, one by one
            for i in range(1, n+1):
                info = ('%s - casting character %i of %i, %i%% done.'
                        % (' '.join(combination).ljust(20), i, n, 100 * i / n))
                self.UI.display(info)
                parsing.strip_O_and_15(combination)
                self.caster.send_signals_to_caster(combination)
        # Put the line out to the galley
            self.UI.display('Putting line to the galley...')
            self.caster.send_signals_to_caster(['N', 'K', 'J', '0005', '0075'])
        # After casting sorts we need to stop the pump
        self.UI.display('Stopping the pump...')
        self.caster.send_signals_to_caster(['N', 'J', '0005'])

    def send_combination(self):
        """send_combination():

        This function allows us to give the program a specific combination
        of Monotype codes, and will keep the valves on until we press return
        (useful for calibration). It also checks the signals' validity.
        """
        signals = ''
        while not signals:
            prompt = 'Enter the signals to send to the caster: '
            signals = self.UI.enter_data(prompt)
        # Parse the combination, get the signals (first item returned
        # by the parsing function)
            signals = parsing.signals_parser(signals)
        # Add O+15 signal if it was desired
            signals = parsing.convert_O15(signals)
        # Turn the valves on
        self.UI.display(' '.join(signals))
        self.caster.activate_valves(signals)
        # Wait until user decides to stop sending those signals to valves
        self.UI.enter_data('Press [Enter] to stop. ')
        self.caster.deactivate_valves()
        return True

    def align_wedges(self, spaceAt='G5'):
        """align_wedges(spaceAt='G5'):

        Allows to align the justification wedges so that when you're
        casting a 9-unit character with the S-needle at 0075:3 and 0005:8
        (neutral position), the    width is the same.

        It works like this:
        1. 0075 - turn the pump on,
        2. cast 10 spaces from the specified matrix (default: G9),
        3. put the line to the galley & set 0005 to 8, 0075 to 3, pump on,
        4. cast 10 spaces with the S-needle from the same matrix,
        5. put the line to the galley, then 0005 to turn the pump off.
        """
        intro = ('Transfer wedge calibration:\n\n'
                 'This function will cast 10 spaces, then set the correction '
                 'wedges to 0075:3 and 0005:8, \nand cast 10 spaces with the '
                 'S-needle. You then have to compare the length of these two '
                 'sets. \nIf they are identical, all is OK. '
                 'If not, you have to adjust the 52D space transfer wedge.\n\n'
                 'Turn on the machine...')
        self.UI.display(intro)
        # Parse the space combination:"""
        spaceAt = parsing.signals_parser(spaceAt)
        # Cast 10 spaces without correction
        self.UI.display('Now casting with a normal wedge only.')
        self.cast_from_matrix(spaceAt, 10)
        # Cast 10 spaces with the S-needle
        self.UI.display('Now casting with justification wedges...')
        self.cast_from_matrix(spaceAt + ['S'], 10)
        # Finished. Return to menu.
        options = {'R' : self.align_wedges,
                   'M' : self.main_menu,
                   'E' : self.UI.exit_program}
        message = ('Done. Compare the lengths and adjust if needed.'
                   '\n[R]epeat, [M]enu or [E]xit? ')
        choice = self.UI.simple_menu(message, options).upper()
        # Execute choice
        options[choice]()

    def main_menu(self):
        """Calls self.UI.menu() with options,
        a header and a footer.

        Options: {option_name : description}
        """
        options = {1 : 'Load a ribbon file',
                   2 : 'Cast composition',
                   3 : 'Cast sorts',
                   4 : 'Test the valves and pinblocks',
                   5 : 'Lock the caster on a specified diecase position',
                   6 : 'Calibrate the 0005 and 0075 wedges',
                   7 : 'Cast two lines of 20 quads to heat up the mould',
                   0 : 'Exit program'}
        # Declare subroutines for menu options
        def choose_ribbon_filename():
            self.ribbonFile = self.UI.enter_input_filename()
            self.main_menu()
        def debug_notice():
        # Prints a notice if the program is in debug mode
            if self.UI.debugMode:
                return '\n\nThe program is now in debugging mode!'
            else:
                return ''
        def additional_info():
        # Displays additional info as a menu footer. Start with empty list
            info = []
        # Add ribbon filename, if any
            if self.ribbonFile:
                info.append('Input file name: ' + self.ribbonFile)
        # Add a caster name
            info.append('Using caster: ' + self.caster.name)
        # Convert it all to a multiline string
            return '\n'.join(info)
        def heatup():
            self.UI.clear()
            self.cast_from_matrix('O15', n=20, lines=2)
        # End of subroutines.
        # Commands: {option_name : function}
        commands = {1 : choose_ribbon_filename,
                    2 : self.cast_composition,
                    3 : self.cast_sorts,
                    4 : self.line_test,
                    5 : self.send_combination,
                    6 : self.align_wedges,
                    7 : heatup,
                    0 : self.UI.exit_program}
        h = ('rpi2caster - CAT (Computer-Aided Typecasting) '
             'for Monotype Composition or Type and Rule casters.'
             '\n\n'
             'This program reads a ribbon (input file) '
             'and casts the type on a composition caster.'
             + debug_notice() + '\n\nMain Menu:')
        choice = self.UI.menu(options, header=h, footer=additional_info())
        # Call the function and return to menu.
        # Use the caster context for everything that needs it.
        if choice in [0, 1]:
            commands[choice]()
        # FIXME: get rid of this ugly ifology
        elif choice in [5]:
            with self.caster:
                commands[choice]()
        else:
            with self.caster:
                commands[choice]()
                self.UI.hold_on_exit()
        self.main_menu()

    def __exit__(self, *args):
        self.UI.debug_info('Exiting casting job context.')
        pass


class TextUI(object):
    """TextUI(job):

    Use this class for creating a text-based console user interface.
    A caster object must be created before instantiating this class.
    Suitable for controlling a caster from the local terminal or via SSH,
    supports UTF-8 too.
    """

    def __init__(self, debugMode=False):
    # Get the debug-mode from input parameters
        self.debugMode = debugMode

    def __enter__(self):
        """Try to call main menu for a job.

        Display a message when user presses ctrl-C.
        """
    # Print some debug info
        self.debug_info('Entering text UI context...')
        try:
            self.job.main_menu()
        except KeyboardInterrupt:
            print '\nUser pressed ctrl-C. Exiting.'
        finally:
            print '\nGoodbye!\n'

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
        """menu(options={'foo':'bar','baz':'qux'}
                        header=foo,
                        footer=bar):

        A menu which takes three arguments:
        header - string to be displayed above,
        footer - string to be displayed below,

        After choice is made, return the command.

        Set up vars for conditional statements,
        and lists for appending new items.

        choices - options to be entered by user
        """
        yourChoice = ''
        choices = []
        # Clear the screen, display header and add two empty lines
        self.clear()
        if header:
            print header
            print
        # Display all the options; we'll take care of 0 later
        for choice in options:
            if choice != 0:
            # Print the option choice and displayed text
                print '\t', choice, ' : ', options[choice], '\n'
            # Add this option to possible choices.
            # We need to convert it to string first.
                choices.append(str(choice))
        try:
        # If an option "0." is available, print it at the end
            optionNumberZero = options[0]
            print '\n\t', 0, ' : ', optionNumberZero
            choices.append('0')
        except KeyError:
            pass
        # Print footer, if defined
        if footer:
            print '\n' + footer
        # Add an empty line to separate prompt
        print '\n'
        # Ask for user input
        while yourChoice not in choices:
            yourChoice = raw_input('Your choice: ')
        else:
        # Valid option is chosen, return integer if options were numbers,
        # else return string
            try:
                return int(yourChoice)
            except ValueError:
                return yourChoice

    def clear(self):
        # Clear screen
        os.system('clear')

    def display(self, *args):
        # Display info for the user - print all in one line
        for arg in args:
            print arg,
        print '\n'

    def debug_info(self, *args):
        # Print debug message to screen if in debug mode
        if self.debugMode:
            for arg in args:
                print arg,
            print '\n'

    def debug_enter_data(self, message):
        # For debug-specific data or confirmations
        if self.debugMode:
            return raw_input(message)


    def exception_handler(self):
        # Raise caught exceptions in debug mode
        if self.debugMode:
            print sys.exc_info()

    def enter_data(self, message):
        # Let user enter the data
        return raw_input(message)

    def enter_input_filename(self):
        # Enter the input filename; check if the file is readable
        fn = raw_input('\n Enter the input file name: ')
        fn = os.path.realpath(fn)
        try:
            with open(fn, 'r'):
                return fn
        except IOError:
            raw_input('Wrong filename or file not readable!')
            return ''

    def enter_output_filename(self):
        # Enter the output filename; no check here
        fn = raw_input('\n Enter the output file name: ')
        fn = os.path.realpath(fn)
        return fn

    def hold_on_exit(self):
        raw_input('Press [Enter] to return to main menu...')

    def simple_menu(self, message, options):
        """Simple menu:

        A simple menu where user is asked what to do.
        Wrong choice points back to the menu.

        Message: string displayed on screen;
        options: a list or tuple of strings - options.
        """
        ans = ''
        while ans.upper() not in options and ans.lower() not in options:
            ans = raw_input(message)
        return ans

    def exit_program(self):
        """Exit program:

        All objects call this method whenever they want to exit program.
        This is because we may do something specific in different UIs,
        so an abstraction layer may come in handy.
        """
        exit()

    def __exit__(self, *args):
        self.debug_info('Exiting text UI context.')
        pass

class WebInterface(object):
    """WebInterface:

    TODO: not implemented yet!
    Use this class for instantiating text-based console user interface
    """

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
    """Session:

    Class for injecting dependencies for objects.
    """
    def __init__(self, job=Casting(), caster=Monotype(), config=Config(),
                 UI=TextUI(), database=Database()):
        # Set dependencies as object attributes.
        # Make sure we've got an UI first.
        try:
            assert (isinstance(UI, TextUI)
                    or isinstance(UI, WebInterface))
        except NameError:
            print 'Error: User interface not specified!'
            exit()
        except AssertionError:
            print 'Error: User interface of incorrect type!'
            exit()
        # Make sure database and config are of the correct type
        try:
            assert isinstance(database, Database)
            assert isinstance(config, Config)
        except NameError:
        # Not set up? Move on
            pass
        except AssertionError:
        # We can be sure that UI can handle this now
            UI.display('Invalid config and/or database!')
            UI.exit_program()
        # We need a job: casting, setup, typesetting...
        try:
        # Any job needs UI and database
            job.UI = UI
            job.database = database
        # UI needs job context
            UI.job = job
        except NameError:
            UI.display('Job not specified!')
        # Database needs UI to communicate messages to user
        database.UI = UI
        # Database needs config to get the connection parameters
        database.config = config
        # Config needs UI to communicate debug/error messages to user
        config.UI = UI
        # Assure that we're using a caster or simulator for casting
        try:
            if isinstance(job, Casting):
                assert (isinstance(caster, Monotype)
                        or isinstance(caster, MonotypeSimulation))
        # Set up mutual dependencies
                job.caster = caster
                caster.UI = UI
                caster.job = job
                caster.config = config
        except (AssertionError, NameError, AttributeError):
            UI.display('You cannot do any casting without a proper caster!')
            UI.exit_program()
        # An __enter__ method of UI will call main_menu method in job
        with UI:
            pass


# End of class definitions.
# And now, for something completely different...
# Initialize the console interface when running the program directly.
if __name__ == '__main__':
    session = Session(caster=Monotype('mkart-cc'))
