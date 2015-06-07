# -*- coding: utf-8 -*-
"""
Database:

Database-related classes for rpi2caster suite.
"""
# IMPORTS:
import sys
import time

# User interface
import text_ui as ui

# Config parser for reading the interface settings
import ConfigParser

# Used for serializing lists stored in database, and for communicating
# with the web application (in the future):
try:
    import json
except ImportError:
    import simplejson as json

# rpi2caster uses sqlite3 database for storing caster, interface,
# wedge, diecase & matrix parameters:
try:
    import sqlite3
except ImportError:
    print 'Missing dependency: sqlite3'
    sys.exit()


class Database(object):
    """Database(database_path, confFilePath):

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

    def __init__(self, database_path='database/monotype.db',
                 config_path='/etc/rpi2caster.conf'):
        self.database_path = database_path
        self.config_path = config_path
        # Connect to the database when entering the object's context
        self.db = None

    def __enter__(self):
        ui.debug_info('Entering database context...')
        self.database_setup()
        ui.debug_info('Using database path:', self.database_path)
        self.db = sqlite3.connect(self.database_path)
        return self

    def database_setup(self):
        """Initialize database:

        Database path passed to class has priority over database path
        set in conffile. If none of them is found, the program will use
        hardcoded default.
        """
        if not self.database_path:
            config = ConfigParser.SafeConfigParser()
            config.read(self.config_path)
        # Look database path up in conffile:
            try:
                self.database_path = config.get('Database', 'path')
            except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            # Revert to defaults if database not configured properly:
                self.database_path = 'database/monotype.db'
                ui.debug_info('Database path not found in conffile. '
                              'Using default:', self.database_path)

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
                               'wedge_number TEXT NOT NULL, '
                               'set_width REAL NOT NULL, '
                               'brit_pica TEXT NOT NULL, '
                               'steps TEXT NOT NULL)')
            # Then add an entry:
                cursor.execute('INSERT INTO wedges ( '
                               'wedge_number,set_width,old_pica,steps'
                               ') VALUES (?, ?, ?, ?)''', data)
                self.db.commit()
                return True
            except:
            # In debug mode, display exception code & stack trace.
                ui.display('Database error: cannot add wedge!')
                ui.exception_handler()
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
                               'WHERE wedge_number = ? AND set_width = ?',
                               [wedgeName, setWidth])
                wedge = cursor.fetchone()
                if wedge is None:
                    ui.display('No wedge %s - %f found in database!'
                               % (wedgeName, setWidth))
                    return False
                else:
                    wedge = list(wedge)
                    ui.display('Wedge %s-%fset found in database - OK'
                               % (wedgeName, setWidth))
                # Change return value of britPica to boolean:
                    wedge[3] = bool(wedge[3])
                # Change return value of steps to list:
                    wedge[4] = json.loads(wedge[4])
                # Return [ID, wedgeName, setWidth, britPica, steps]:
                    return wedge
            except:
            # In debug mode, display exception code & stack trace.
                ui.display('Database error: cannot get wedge!')
                ui.exception_handler()

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
                    ui.display('Wedge not found!')
                    return False
                else:
                    wedge = list(wedge)
                # Change return value of britPica to boolean:
                    wedge[3] = bool(wedge[3])
                # Change return value of steps to list:
                    wedge[4] = json.loads(wedge[4])
                # Return [ID, wedgeName, setWidth, britPica, steps]:
                    return wedge
            except:
            # In debug mode, display exception code & stack trace.
                ui.display('Database error: cannot get wedge!')
                ui.exception_handler()

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
                    ui.display('Database error: cannot delete wedge!')
                    ui.exception_handler()
                    return False
        else:
            ui.display('Nothing to delete.')
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
                ui.display(header)
                while True:
                    wedge = cursor.fetchone()
                    if wedge is not None:
                        record = ''
                        for field in wedge:
                            record += str(field).ljust(10)
                        ui.display(record)
                    else:
                        break
                return True
            except:
            # In debug mode, display exception code & stack trace."""
                ui.display('Database error: cannot list wedges!')
                ui.exception_handler()
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
                    ui.display('Sorry - no results found.')
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
                    choice = ui.menu(options, header)
                # Return a list with chosen diecase's parameters:
                    return options[choice]
            except:
            # In debug mode, display exception code & stack trace.
                ui.display('Database error: cannot find diecase data!')
                ui.exception_handler()
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
                    ui.display('Sorry - no results found.')
                    time.sleep(1)
                    return False
            except:
            # In debug mode, display exception code & stack trace.
                ui.display('Database error: cannot find diecase data!')
                ui.exception_handler()
                return False

    def __exit__(self, *args):
        ui.debug_info('Exiting database context.')
        