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
# Get global settings
from . import global_settings
# Package constants
from .constants import DEFAULT_DATABASE_PATHS


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
        database_paths = ([global_settings.DATABASE_PATH] +
                          DEFAULT_DATABASE_PATHS)
        # Connect to the database
        for path in database_paths:
            try:
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

    def __enter__(self):
        return self

    def add_wedge(self, wedge):
        """Registers a wedge in our database."""
        # data - a list with wedge parameters to be written,
        # boolean is_brit_pica must be converted to int,
        # a unit arrangement is a JSON-encoded list
        data = [wedge.series, wedge.set_width, int(wedge.is_brit_pica),
                json.dumps(wedge.unit_arrangement)]
        with self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                # Create the table first:
                sql = ('CREATE TABLE IF NOT EXISTS wedges ('
                       'wedge_series TEXT NOT NULL, '
                       'set_width REAL NOT NULL, '
                       'brit_pica INTEGER NOT NULL, '
                       'unit_arrangement TEXT NOT NULL, '
                       'PRIMARY KEY (wedge_series, set_width, brit_pica))')
                cursor.execute(sql)
                # Then add an entry:
                cursor.execute('INSERT OR REPLACE INTO wedges ('
                               'wedge_series, set_width, '
                               'brit_pica, unit_arrangement'
                               ') VALUES (?, ?, ?, ?)''', data)
                self.db_connection.commit()
                return True
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                # Database failed
                raise exceptions.DatabaseQueryError

    def check_wedge(self, wedge):
        """Checks if a wedge with given parameters is in database"""
        with self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                sql = ('SELECT * FROM wedges WHERE wedge_series = ?'
                       'AND set_width = ? AND brit_pica = ?')
                data = [wedge.series, wedge.set_width, int(wedge.is_brit_pica)]
                cursor.execute(sql, data)
                data = cursor.fetchall()
                # Empty list = False
                return bool(data)
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                return False

    def get_wedge(self, wedge_series, set_width):
        """get_wedge(wedge_series, set_width):

        Looks up a wedge with given ID and set width in database.
        If found, returns (series, set_width, brit_pica, unit_arrangement)

        series - string (e.g. S5) - wedge name
        set_width - float (e.g. 9.75) - set width,
        brit_pica - bool - whether this is an old-pica ("E") wedge or not,
        unit_arrangement - list of unit values for all wedge's steps.

        Else, function returns False.
        """
        with self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                cursor.execute('SELECT * FROM wedges '
                               'WHERE wedge_series = ? AND set_width = ?',
                               [str(wedge_series), float(set_width)])
                (wedge_series, set_width, is_brit_pica,
                 raw_unit_arrangement) = cursor.fetchone()
                # Change return value of steps to list:
                wedge = [wedge_series, set_width, bool(is_brit_pica),
                         [int(x) for x in json.loads(raw_unit_arrangement)]]
                return wedge
            except (TypeError, ValueError, IndexError):
                # No data or cannot process it
                raise exceptions.NoMatchingData
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                # Database failed
                raise exceptions.DatabaseQueryError

    def delete_wedge(self, wedge):
        """Deletes a wedge from the database."""
        with self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                sql = ('DELETE FROM wedges WHERE wedge_series = ? '
                       'AND set_width = ? AND brit_pica = ?')
                data = [wedge.series, wedge.set_width, wedge.is_brit_pica]
                cursor.execute(sql, data)
                return True
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                # Database failed
                raise exceptions.DatabaseQueryError

    def get_all_wedges(self):
        """Gets all wedges stored in database."""
        with self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                cursor.execute('SELECT * FROM wedges')
                # Check if we got any:
                all_wedges = cursor.fetchall()
                processed_wedges = []
                if not all_wedges:
                    raise exceptions.NoMatchingData
                for record in all_wedges:
                    (wedge_series, set_width,
                     is_brit_pica, unit_arrangement) = record
                    record = [wedge_series, set_width, bool(is_brit_pica),
                              [x for x in json.loads(unit_arrangement)]]
                    processed_wedges.append(record)
                return processed_wedges
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                # Database failed
                raise exceptions.DatabaseQueryError

    def get_all_diecases(self):
        """Gets all diecases stored in database."""
        with self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                cursor.execute('SELECT * FROM matrix_cases')
                # Check if we got any:
                results = cursor.fetchall()
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
        data = [diecase.diecase_id, diecase.type_series, diecase.type_size,
                diecase.wedge.series, diecase.wedge.set_width,
                diecase.typeface_name, json.dumps(diecase.layout)]
        with self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                # Create the table first:
                cursor.execute('CREATE TABLE IF NOT EXISTS matrix_cases ('
                               'diecase_id TEXT UNIQUE PRIMARY KEY, '
                               'type_series TEXT NOT NULL, '
                               'type_size TEXT NOT NULL, '
                               'wedge_series TEXT NOT NULL, '
                               'set_width REAL NOT NULL, '
                               'typeface_name TEXT NOT NULL, '
                               'layout TEXT NOT NULL)')
                # Then add an entry:
                cursor.execute('INSERT OR REPLACE INTO matrix_cases ('
                               'diecase_id, type_series, type_size,'
                               'wedge_series, set_width, typeface_name, layout'
                               ') VALUES (?, ?, ?, ?, ?, ?, ?)''', data)
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
                # Return diecase if found:
                diecase = list(cursor.fetchone())
                # De-serialize the diecase layout, convert it back to a list
                raw_layout = json.loads(diecase.pop())
                # Convert the layout
                # Record is now 'character style1,style2... column row units'
                # Make it a list
                layout = []
                for record in raw_layout:
                    # Make a tuple of styles
                    (char, styles, column, row, units) = record
                    # Last field - unit width - was not mandatory
                    # Try to convert it to int
                    # If no unit width is specified, use None instead
                    try:
                        units = int(units)
                    except (IndexError, ValueError):
                        record.append(0)
                    record = (char, tuple(styles), column, int(row), units)
                    layout.append(record)
                    # Record is now:
                    # [character, (style1, style2...), column, row, units]
                # Add the layout back to diecase and return the data
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
                cursor.execute('SELECT * FROM ribbons')
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
        data = [ribbon.description, ribbon.customer, ribbon.diecase.diecase_id,
                json.dumps(ribbon.contents)]
        with self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                # Create the table first:
                cursor.execute('CREATE TABLE IF NOT EXISTS ribbons ('
                               'ribbon_id INTEGER PRIMARY KEY AUTOINCREMENT, '
                               'description TEXT, '
                               'customer TEXT, '
                               'diecase_id TEXT NOT NULL, '
                               'contents TEXT NOT NULL)')
                # Then add an entry:
                cursor.execute('INSERT OR REPLACE INTO ribbons ('
                               'title, author, customer, diecase_id, contents'
                               ') VALUES (?, ?, ?, ?)''', data)
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

    def get_all_schemes(self):
        """Gets all font schemes stored in database."""
        with self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                cursor.execute('SELECT * FROM font_schemes')
                # Check if we got any:
                results = cursor.fetchall()
                if not results:
                    raise exceptions.NoMatchingData
                return results
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                # Database failed
                raise exceptions.DatabaseQueryError

    def add_scheme(self, scheme):
        """Registers a scheme (source text) in our database."""
        data = [scheme.scheme_id, scheme.description, scheme.language,
                json.dumps(scheme.layout)]
        with self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                # Create the table first:
                cursor.execute('CREATE TABLE IF NOT EXISTS font_schemes ('
                               'scheme_id TEXT UNIQUE PRIMARY KEY, '
                               'description TEXT NOT NULL, '
                               'language TEXT NOT NULL, '
                               'scheme_layout TEXT NOT NULL)')
                # Then add an entry:
                cursor.execute('INSERT OR REPLACE INTO font_schemes ('
                               'scheme_id, description, language, '
                               'scheme_layout) VALUES (?, ?, ?, ?)''', data)
                self.db_connection.commit()
                return True
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                # Database failed
                raise exceptions.DatabaseQueryError

    def get_scheme(self, scheme_id):
        """Searches for scheme based on the unique scheme ID."""
        with self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                cursor.execute('SELECT * FROM font_schemes '
                               'WHERE scheme_id = ?', [scheme_id])
                scheme = list(cursor.fetchone())
                layout = scheme.pop()
                scheme.append(json.loads(layout))
                return scheme
            except (TypeError, ValueError, IndexError):
                # No data or cannot process it
                raise exceptions.NoMatchingData
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                # Database failed
                raise exceptions.DatabaseQueryError

    def delete_scheme(self, scheme):
        """Deletes a scheme with given unique ID from the database."""
        with self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                cursor.execute('DELETE FROM font_schemes WHERE scheme_id = ?',
                               [scheme.scheme_id])
                return True
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                # Database failed
                raise exceptions.DatabaseQueryError

    def __exit__(self, *args):
        pass
