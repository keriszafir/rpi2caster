# -*- coding: utf-8 -*-
"""
Database:

Database-related classes for rpi2caster suite.
"""
# IMPORTS:
# Used for serializing lists stored in database, and for communicating
# with the web application (in the future):
import json
# this module uses sqlite3 database for storing caster, interface,
# wedge, diecase & matrix parameters:
import sqlite3
# Custom exceptions
from . import exceptions
# Get database paths from configuration
from .global_config import DATABASE_PATHS


class Singleton(type):
    """Make only one object"""
    instance = None

    def __call__(cls, *args, **kw):
        if not cls.instance:
            cls.instance = super(Singleton, cls).__call__(*args, **kw)
        return cls.instance


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

    Default database path is /var/lib/rpi2caster - but you can
    override it by instantiating this class with a different name
    passed as an argument. It is necessary that the user who's running
    this program for setup has write access to the database file.
    """
    __metaclass__ = Singleton

    def __init__(self):
        # Connect to the database
        for path in DATABASE_PATHS:
            try:
                self.path = path
                self.db_connection = sqlite3.connect(path)
                # End on first successful find
                break
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                # Continue looping
                pass
        else:
            # Fell off the end of the loop
            raise exceptions.WrongConfiguration('Cannot connect to '
                                                'database file %s' % path)

    def __repr__(self):
        return self.path

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def get_all_diecases(self):
        """Gets all diecases stored in database."""
        with self.db_connection:
            try:
                sql_query = 'SELECT * FROM matrix_cases ORDER BY diecase_id'
                cursor = self.db_connection.cursor()
                cursor.execute(sql_query)
                results = cursor.fetchall()
                # Check if we got any:
                if not results:
                    raise exceptions.NoMatchingData
                return results
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                # Database failed
                raise exceptions.DatabaseQueryError

    def add_diecase(self, diecase):
        """Registers a diecase in our database."""
        # data - a list with diecase parameters to be written,
        # layout is a JSON-dumped dictionary
        data = [diecase.diecase_id, diecase.typeface, diecase.wedge.name,
                json.dumps(diecase.layout)]
        with self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                # Create the table first:
                cursor.execute('CREATE TABLE IF NOT EXISTS matrix_cases ('
                               'diecase_id TEXT UNIQUE PRIMARY KEY, '
                               'typeface TEXT NOT NULL, '
                               'wedge TEXT NOT NULL, '
                               'layout TEXT NOT NULL)')
                # Then add an entry:
                cursor.execute('INSERT OR REPLACE INTO matrix_cases ('
                               'diecase_id, typeface, wedge, layout'
                               ') VALUES (?, ?, ?, ?)''', data)
                self.db_connection.commit()
                return True
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                # Database failed
                raise exceptions.DatabaseQueryError

    def get_diecase(self, diecase_id):
        """Searches for diecase metadata, based on the unique diecase ID."""
        with self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                sql = 'SELECT * FROM matrix_cases WHERE diecase_id = ?'
                cursor.execute(sql, [diecase_id])
                row = cursor.fetchone()
                if not row:
                    raise exceptions.NoMatchingData
                diecase = list(row)
                # De-serialize the diecase layout, convert it back to a list
                raw_layout = json.loads(diecase.pop())
                # Make sure the layout has specified units
                layout = []
                for record in raw_layout:
                    (char, styles, coordinates, units) = record
                    try:
                        units = int(units)
                    except (IndexError, ValueError):
                        units = 0
                    record = (char, styles, coordinates, units)
                    layout.append(record)
                diecase.append(layout)
                return diecase
            except (TypeError, ValueError, IndexError):
                # No data or cannot process it
                raise exceptions.NoMatchingData
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                # Database failed
                raise exceptions.DatabaseQueryError

    def delete_diecase(self, diecase):
        """Deletes a diecase with given unique ID from the database."""
        with self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                cursor.execute('DELETE FROM matrix_cases WHERE diecase_id = ?',
                               [diecase.diecase_id])
                return True
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                # Database failed
                raise exceptions.DatabaseQueryError

    def get_all_ribbons(self):
        """Gets all ribbons stored in database"""
        with self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                cursor.execute('SELECT * FROM ribbons ORDER BY ribbon_id')
                # Check if we got any:
                results = cursor.fetchall()
                if not results:
                    raise exceptions.NoMatchingData
                return results
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                # Database failed
                raise exceptions.DatabaseQueryError

    def add_ribbon(self, ribbon):
        """Registers a ribbon in our database."""
        data = [ribbon.description, ribbon.customer, ribbon.diecase_id,
                ribbon.wedge_name, json.dumps(ribbon.contents)]
        with self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                # Create the table first:
                cursor.execute('CREATE TABLE IF NOT EXISTS ribbons ('
                               'ribbon_id INTEGER PRIMARY KEY AUTOINCREMENT, '
                               'description TEXT, '
                               'customer TEXT, '
                               'diecase_id TEXT NOT NULL, '
                               'wedge TEXT, '
                               'contents TEXT NOT NULL)')
                # Then add an entry:
                cursor.execute('INSERT OR REPLACE INTO ribbons ('
                               'title, author, customer, diecase_id, contents'
                               ') VALUES (?, ?, ?, ?, ?)''', data)
                self.db_connection.commit()
                return True
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                # Database failed
                raise exceptions.DatabaseQueryError

    def get_ribbon(self, ribbon_id):
        """Searches for ribbon, based on the unique ribbon ID."""
        with self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                cursor.execute('SELECT * FROM ribbons WHERE ribbon_id = ?',
                               [ribbon_id])
                ribbon = list(cursor.fetchone())
                # Take the last item which is contents
                # De-serialize it, convert it back to a list
                raw_contents = json.loads(ribbon.pop())
                # Add the contents
                ribbon.append(raw_contents)
                # Return the list
                return ribbon
            except (TypeError, ValueError, IndexError):
                # No data or cannot process it
                raise exceptions.NoMatchingData
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                # Database failed
                raise exceptions.DatabaseQueryError

    def delete_ribbon(self, ribbon):
        """Deletes a ribbon entry from database."""
        # Okay, proceed:
        with self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                cursor.execute('DELETE FROM ribbons WHERE ribbon_id = ?',
                               [ribbon.ribbon_id])
                return True
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                # Database failed
                raise exceptions.DatabaseQueryError
