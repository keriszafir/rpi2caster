# -*- coding: utf-8 -*-
"""
Database:

Database-related classes for rpi2caster suite.
"""
# IMPORTS:
from __future__ import absolute_import
# Used for serializing lists stored in database, and for communicating
# with the web application (in the future):
try:
    import json
except ImportError:
    import simplejson as json
# this module uses sqlite3 database for storing caster, interface,
# wedge, diecase & matrix parameters:
try:
    import sqlite3
except ImportError:
    print 'Missing dependency: sqlite3'
    exit()
# Custom exceptions
from rpi2caster import exceptions
# Config parser for reading the interface settings
from rpi2caster import cfg_parser


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

    def __init__(self, database_path='', config_path=''):
        """init:

        Sets up config path (specified or default),
        sets up database path (specified, set up in config, then default),
        """
        # Update cfg_parser's CONFIG_PATH or keep it default
        cfg_parser.CONFIG_PATH = config_path or cfg_parser.CONFIG_PATH
        # Database path selection priority:
        # 1. explicitly stated on class instantiation
        # 2. found in conffile
        # 3. hardcoded default: database/monotype.db
        self.database_path = (database_path
                              or cfg_parser.get_config('Database', 'path')
                              or 'database/monotype.db')
        # Connect to the database
        try:
            self.db_connection = sqlite3.connect(self.database_path)
        except (sqlite3.OperationalError, sqlite3.DatabaseError):
            raise exceptions.WrongConfiguration('Database cannot be opened')

    def __enter__(self):
        return self


    def add_wedge(self, wedge_name, set_width, brit_pica, unit_arrangement):
        """add_wedge:

        Registers a wedge in our database.
        Returns True if successful, False otherwise.

        Arguments:
        wedge_name - wedge number, e.g. S5 or 1160, str or int, not null.
        set_width - set width of a wedge, e.g. 9.75. float, not null.
        brit_pica - True if it's a British pica system (1pica = 0.1667")
                    False if it's an American pica system (1pica = 0.1660")

        If the wedge has "E" at the end of its number (e.g. 5-12E),
        then it was made for European countries which used Didot points
        and ciceros (1cicero = 0.1776"), but the unit calculations were all
        based on the British pica.

        unit_arrangement - a wedge's unit arrangement - list of unit values
        for each of the wedge's steps (i.e. diecase rows). Not null.

        An additional column, id, will be created and auto-incremented.
        This will be an unique identifier of a wedge.
        """

        # data - a list with wedge parameters to be written,
        # boolean brit_pica must be converted to int,
        # a unit arrangement is a JSON-encoded list
        data = [wedge_name, set_width, int(brit_pica),
                json.dumps(unit_arrangement)]
        with self.db_connection:
            try:
                cursor = self.db_connection.cursor()
            # Create the table first:
                cursor.execute('CREATE TABLE IF NOT EXISTS wedges ('
                               'id INTEGER PRIMARY KEY ASC AUTOINCREMENT, '
                               'wedge_number TEXT NOT NULL, '
                               'set_width REAL NOT NULL, '
                               'brit_pica INTEGER NOT NULL, '
                               'unit_arrangement TEXT NOT NULL)')
            # Then add an entry:
                cursor.execute('INSERT INTO wedges ('
                               'wedge_number,set_width,'
                               'brit_pica,unit_arrangement'
                               ') VALUES (?, ?, ?, ?)''', data)
                self.db_connection.commit()
                return True
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                return False

    def wedge_by_name_and_width(self, wedge_name, set_width):
        """wedge_by_name_and_width(wedge_name, set_width):

        Looks up a wedge with given ID and set width in database.
        Useful when coding a ribbon - wedge is obtained from diecase data.

        If wedge is registered, function returns:
        ID - unique, int (e.g. 0),
        wedge_name - string (e.g. S5) - wedge name
        set_width - float (e.g. 9.75) - set width,
        brit_pica - bool - whether this is an old-pica ("E") wedge or not,
        steps - list of unit values for all wedge's steps.

        Else, function returns False.
        """
        with self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                cursor.execute('SELECT * FROM wedges '
                               'WHERE wedge_number = ? AND set_width = ?',
                               [wedge_name, set_width])
                wedge = cursor.fetchone()
                try:
                    wedge = list(wedge)
                # Change return value of brit_pica to boolean:
                    wedge[3] = bool(wedge[3])
                # Change return value of steps to list:
                    wedge[4] = json.loads(wedge[4])
                    return wedge
                except (TypeError, ValueError, IndexError):
                    # No data or corrupted data found
                    raise exceptions.NoMatchingData
            # Database error happened:
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                return False

    def wedge_by_id(self, w_id):
        """wedge_by_id:

        Gets parameters for a wedge with given ID.

        If so, returns:
        ID - unique, int (e.g. 0),
        wedge_name - string (e.g. S5) - wedge name
        set_width - float (e.g. 9.75) - set width,
        brit_pica - bool - whether this is a British pica wedge or not,
        steps - list of unit values for all wedge's steps.

        Else, returns False.
        """
        with self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                cursor.execute('SELECT * FROM wedges WHERE id = ? ', [w_id])
                wedge = cursor.fetchone()
                try:
                    wedge = list(wedge)
                    # Change return value of brit_pica to boolean:
                    wedge[3] = bool(wedge[3])
                    # Change return value of steps to list:
                    wedge[4] = json.loads(wedge[4])
                    # Return wedge
                    return wedge
                except (TypeError, ValueError, IndexError):
                    # No data or corrupted data found
                    raise exceptions.NoMatchingData
            # Database error happened:
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                return False

    def delete_wedge(self, w_id):
        """delete_wedge:

        Deletes a wedge with given unique ID from the database
        (useful in case we no longer have the wedge).

        Returns True if successful, False otherwise.

        First, the function checks if the wedge is in the database at all.
        """
        if self.wedge_by_id(w_id):
            with self.db_connection:
                try:
                    cursor = self.db_connection.cursor()
                    cursor.execute('DELETE FROM wedges WHERE id = ?', [w_id])
                    return True
                #Database error happened:
                except (sqlite3.OperationalError, sqlite3.DatabaseError):
                    return False
        else:
            return None

    def get_all_wedges(self):
        """get_all_wedges(self):

        Gets all wedges stored in database, with their step unit values.

        Returns a list of all wedges found.
        """
        with self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                cursor.execute('SELECT * FROM wedges')
                # Initialize a loop, end after last wedge is displayed
                return cursor.fetchall()
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                return False

    def diecase_by_series_and_size(self, type_series, type_size):
        """diecase_by_series_and_size(type_series, type_size):

        Searches for diecase metadata, based on the desired type series
        and size. Allows to choose one of the diecases found.
        """
        with self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                cursor.execute('SELECT * FROM diecases '
                               'WHERE type_series = "%s" AND size = %i',
                               (type_series, type_size))
            # Initialize a list of matching diecases:
                return cursor.fetchall()
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                return False

    def diecase_by_id(self, diecase_id):
        """diecase_by_id(diecase_id):

        Searches for diecase metadata, based on the unique diecase ID.
        """
        with self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                cursor.execute('SELECT * FROM diecases WHERE id = "%s"'
                               % diecase_id)
            # Return diecase if found:
                diecase = cursor.fetchone()
                try:
                    return list(diecase)
                except (ValueError, TypeError, IndexError):
                # No data or corrupted data found
                    raise exceptions.NoMatchingData
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                return False

    def __exit__(self, *args):
        pass
