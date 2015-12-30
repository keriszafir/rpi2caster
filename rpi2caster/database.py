# -*- coding: utf-8 -*-
"""
Database:

Database-related classes for rpi2caster suite.
"""
# IMPORTS:
# Used for serializing lists stored in database, and for communicating
# with the web application (in the future):
try:
    import json
except ImportError:
    import simplejson as json
# Custom exceptions
from rpi2caster import exceptions
# Get global settings
from rpi2caster import global_settings
# this module uses sqlite3 database for storing caster, interface,
# wedge, diecase & matrix parameters:
try:
    import sqlite3
except ImportError:
    raise exceptions.MissingDependency('Missing dependency: sqlite3')


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

    def __init__(self):
        """init:

        Sets up config path (specified or default),
        sets up database path (specified, set up in config, then default),
        """
        database_paths = (global_settings.DATABASE_PATH,
                          '/var/rpi2caster/monotype.db',
                          '/var/rpi2caster/rpi2caster.db',
                          'data/rpi2caster.db')
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
        Unit arrangements are stored in database as 15- or 16-element array
        (json-encoded), in simmilar format to those stored in
        wedge_arrangements.

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
                # Database failed
                raise exceptions.DatabaseQueryError

    def wedge_by_name_and_width(self, wedge_series, set_width):
        """wedge_by_name_and_width(wedge_series, set_width):

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
                               [str(wedge_series), float(set_width)])
                (wedge_id, wedge_name, set_width, brit_pica,
                 raw_unit_arrangement) = cursor.fetchone()
                # Change return value of steps to list:
                unit_arrangement = json.loads(raw_unit_arrangement)
                unit_arrangement = [0] + unit_arrangement
                # Fill the wedge arrangement so that it has 16 steps
                while True:
                    try:
                        # Check if 16th position is there (no exception)
                        # If so - end here
                        0 == unit_arrangement[16]
                        break
                    except IndexError:
                        # No 16th position - add one more
                        unit_arrangement.append(unit_arrangement[-1])
                wedge = (wedge_id, wedge_name, set_width, bool(brit_pica),
                         tuple(unit_arrangement))
                return wedge
            except (TypeError, ValueError, IndexError):
                # No data or cannot process it
                raise exceptions.NoMatchingData
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                # Database failed
                raise exceptions.DatabaseQueryError

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
                ([w_id, wedge_series, set_width, brit_pica,
                 raw_unit_arrangement]) = cursor.fetchone()
                # Transform the data on the fly
                unit_arrangement = json.loads(raw_unit_arrangement)
                unit_arrangement = [0] + unit_arrangement
                # Fill the wedge arrangement so that it has 16 steps
                while True:
                    try:
                        # Check if 16th position is there (no exception)
                        # If so - end here
                        0 == unit_arrangement[16]
                        break
                    except IndexError:
                        # No 16th position - add one more
                        unit_arrangement.append(unit_arrangement[-1])
                wedge = (w_id, wedge_series, set_width, bool(brit_pica),
                         tuple(unit_arrangement))
                return wedge
            except (TypeError, ValueError, IndexError):
                # No data or cannot process it
                raise exceptions.NoMatchingData
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                # Database failed
                raise exceptions.DatabaseQueryError

    def delete_wedge(self, w_id):
        """delete_wedge:

        Deletes a wedge with given unique ID from the database
        (useful in case we no longer have the wedge).

        Returns True if successful, False otherwise.

        First, the function checks if the wedge is in the database at all.
        """
        # Check if wedge is there (will raise an exception if not)
        # We don't care about the retval which is a list.
        self.wedge_by_id(w_id)
        # Okay, proceed:
        with self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                cursor.execute('DELETE FROM wedges WHERE id = ?', [w_id])
                return True
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                # Database failed
                raise exceptions.DatabaseQueryError

    def get_all_wedges(self):
        """get_all_wedges:

        Gets all wedges stored in database, with their step unit values.

        Returns a list of all wedges found or raises an exception.
        """
        with self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                cursor.execute('SELECT * FROM wedges')
                # Check if we got any:
                results = cursor.fetchall()
                processed_results = []
                if not results:
                    raise exceptions.NoMatchingData
                for result in results:
                    result = list(result)
                    result[-1] = json.loads(result[-1])
                    result[-2] = bool(result[-2])
                    processed_results.append(result)
                return processed_results
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                # Database failed
                raise exceptions.DatabaseQueryError

    def get_all_diecases(self):
        """get_all_diecadses(self):

        Gets all diecases stored in database, with their metadata.

        Returns a list of all diecases found or raises an exception.
        """
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

    def add_diecase(self, diecase_id, type_series, type_size,
                    wedge_series, set_width, typeface_name, layout):
        """add_diecase:

        Registers a diecase in our database.
        Returns True if successful, False otherwise.

        Arguments:
        diecase_id - user-defined inventory diecase number
        type_series - fount No (e.g. 327 for Times New Roman)
        type_size - size with an optional sizing system indication
                    (D for Didot, F for Fournier)
        set_width - set width of a type
        typeface_name - typeface's name
        wedge_series - wedge series number, e.g. 5 (for stopbar S5 / wedge 5)
        layout - a list, constructed as following:

        layout = ((character, (style1, style2...), column, row, units), (...))
        character = single character, double/triple character (for ligatures),
        ' ' for low space and '_' for high space
        style1, style2... - one or more styles a matrix belongs to,
        this will enable a matrix to be used with specified text styles only
        column - string (NI, NL, A...O)
        row_number - int (1...15 or 16)
        unit_width - int (unit width of a character) or 0 if not specified
        """

        # data - a list with diecase parameters to be written,
        # layout is a JSON-encoded dictionary
        layout = json.dumps(layout)
        data = [diecase_id, type_series, type_size, wedge_series, set_width,
                typeface_name, layout]
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
                cursor.execute('INSERT INTO matrix_cases ('
                               'diecase_id,type_series,type_size,'
                               'wedge_series,set_width,typeface_name,layout'
                               ') VALUES (?, ?, ?, ?, ?, ?, ?)''', data)
                self.db_connection.commit()
                return True
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                # Database failed
                raise exceptions.DatabaseQueryError

    def diecase_by_id(self, diecase_id):
        """diecase_by_id:

        Searches for diecase metadata, based on the unique diecase ID.
        """
        with self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                cursor.execute('SELECT * FROM matrix_cases '
                               'WHERE diecase_id = ?', [diecase_id])
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

    def diecase_by_series_and_size(self, type_series, type_size):
        """diecase_by_series_and_size:

        Looks up a diecase of a given type series (string e.g. 327) and size
        (string e.g. 12D).
        """
        with self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                cursor.execute('SELECT * FROM matrix_cases '
                               'WHERE type_series = ? AND type_size = ?',
                               [str(type_series), str(type_size)])
                diecase = list(cursor.fetchone())
                # De-serialize the diecase layout, convert it back to a list
                raw_layout = json.loads(diecase.pop())
                # Convert the layout
                # Record is now 'character style1,style2... column row units'
                # Make it a list
                layout = []
                for record in raw_layout:
                    # Make a tuple of styles
                    record[1] = tuple(record[1].split(','))
                    # Convert the row number to int
                    record[3] = int(record[3])
                    # Last field - unit width - was not mandatory
                    # Try to convert it to int
                    # If no unit width is specified, use None instead
                    try:
                        record[4] = int(record[4])
                    except (IndexError, ValueError):
                        record.append(None)
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

    def update_diecase_layout(self, diecase_id, layout={}):
        """update_diecase_layout:

        Changes the matrix case layout on an existing diecase.
        If called with the diecase_id only - then clears the whole layout.
        """
        with self.db_connection:
            try:
                layout = json.dumps(layout)
                cursor = self.db_connection.cursor()
                cursor.execute('UPDATE matrix_cases '
                               'SET layout = ? WHERE diecase_id = ?',
                               [layout, diecase_id])
                return True
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                # Database failed
                raise exceptions.DatabaseQueryError

    def delete_diecase(self, diecase_id):
        """delete_diecase:

        Deletes a diecase with given unique ID from the database
        (useful in case we no longer have the diecase).

        Returns True if successful, False otherwise.

        First, the function checks if the diecase is in the database at all.
        """
        # Check if wedge is there (will raise an exception if not)
        # We don't care about the retval which is a list.
        self.diecase_by_id(diecase_id)
        # Okay, proceed:
        with self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                cursor.execute('DELETE FROM matrix_cases '
                               'WHERE diecase_id = ?', [diecase_id])
                return True
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                # Database failed
                raise exceptions.DatabaseQueryError

    def get_all_ribbons(self):
        """get_all_ribbons:

        Gets all ribbons stored in database, with their metadata.

        Returns a list of all ribbons found or raises an exception.
        """
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

    def add_ribbon(self, ribbon_id, title, author, diecase_id, unit_shift,
                   contents):
        """add_ribbon:

        Registers a ribbon in our database.
        Returns True if successful, raises an exception otherwise.

        Arguments:
        ribbon_id - user-defined unique ribbon ID
        title - title of a work,
        author - author's name (or system login),
        diecase_id - diecase used for casting the ribbon,
        contents - codes to send to the caster
        """
        # contents is a JSON-encoded list
        contents = json.dumps(contents)
        unit_shift = int(unit_shift)
        data = [ribbon_id, title, author, diecase_id, unit_shiftcontents]
        with self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                # Create the table first:
                cursor.execute('CREATE TABLE IF NOT EXISTS ribbons ('
                               'ribbon_id TEXT UNIQUE PRIMARY KEY, '
                               'title TEXT NOT NULL, '
                               'author TEXT NOT NULL, '
                               'diecase_id TEXT NOT NULL, '
                               'unit_shift INTEGER NOT NULL, '
                               'contents TEXT NOT NULL)')
                # Then add an entry:
                cursor.execute('INSERT INTO ribbons ('
                               'ribbon_id,title,author,diecase_id,contents'
                               ') VALUES (?, ?, ?, ?, ?, ?)''', data)
                self.db_connection.commit()
                return True
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                # Database failed
                raise exceptions.DatabaseQueryError

    def ribbon_by_id(self, ribbon_id):
        """ribbon_by_id:

        Searches for ribbon metadata, based on the unique ribbon ID.
        """
        with self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                cursor.execute('SELECT * FROM ribbons '
                               'WHERE ribbon_id = ?', [ribbon_id])
                ribbon = list(cursor.fetchone())
                # De-serialize the contents, convert it back to a list
                raw_contents = json.loads(ribbon.pop())
                unit_shift = bool(ribbon.pop())
                ribbon.append(unit_shift)
                ribbon.append(raw_contents)
                return ribbon
            except (TypeError, ValueError, IndexError):
                # No data or cannot process it
                raise exceptions.NoMatchingData
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                # Database failed
                raise exceptions.DatabaseQueryError

    def delete_ribbon(self, ribbon_id):
        """delete_ribbon:

        Deletes a ribbon with given unique ID from the database
        (in case it is no longer needed).

        Returns True if successful, raises an exception otherwise.

        First, the function checks if the ribbon is in the database at all.
        """
        # Check if wedge is there (will raise an exception if not)
        # We don't care about the retval which is a list.
        self.ribbon_by_id(ribbon_id)
        # Okay, proceed:
        with self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                cursor.execute('DELETE FROM ribbons '
                               'WHERE ribbon_id = ?', [ribbon_id])
                return True
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                # Database failed
                raise exceptions.DatabaseQueryError

    def get_all_works(self):
        """get_all_works:

        Gets all works (source texts) stored in database, with their metadata.

        Returns a list of all works found or raises an exception.
        """
        with self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                cursor.execute('SELECT * FROM works')
                # Check if we got any:
                results = cursor.fetchall()
                if not results:
                    raise exceptions.NoMatchingData
                return results
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                # Database failed
                raise exceptions.DatabaseQueryError

    def add_work(self, work_id, title, author, contents):
        """add_work:

        Registers a work (unprocessed text) in our database.
        Returns True if successful, raises an exception otherwise.

        Arguments:
        work_id - user-defined unique work ID
        title - title of a work,
        author - author's name (or system login),
        contents - the text.
        """
        # contents is a JSON-encoded list
        contents = json.dumps(contents)
        data = [work_id, title, author, contents]
        with self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                # Create the table first:
                cursor.execute('CREATE TABLE IF NOT EXISTS works ('
                               'work_id TEXT UNIQUE PRIMARY KEY, '
                               'title TEXT NOT NULL, '
                               'author TEXT NOT NULL, '
                               'contents TEXT NOT NULL)')
                # Then add an entry:
                cursor.execute('INSERT INTO works ('
                               'work_id,title,author,contents'
                               ') VALUES (?, ?, ?, ?)''', data)
                self.db_connection.commit()
                return True
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                # Database failed
                raise exceptions.DatabaseQueryError

    def work_by_id(self, work_id):
        """Searches for work metadata, based on the unique work ID."""
        with self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                cursor.execute('SELECT * FROM works '
                               'WHERE work_id = ?', [work_id])
                work = list(cursor.fetchone())
                # De-serialize the contents
                raw_contents = json.loads(work.pop())
                work.append(raw_contents)
                return work
            except (TypeError, ValueError, IndexError):
                # No data or cannot process it
                raise exceptions.NoMatchingData
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                # Database failed
                raise exceptions.DatabaseQueryError

    def delete_work(self, work_id):
        """delete_work:

        Deletes a work with given unique ID from the database
        (in case it is no longer needed).

        Returns True if successful, raises an exception otherwise.

        First, the function checks if the work is in the database at all.
        """
        # Check if wedge is there (will raise an exception if not)
        # We don't care about the retval which is a list.
        self.work_by_id(work_id)
        # Okay, proceed:
        with self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                cursor.execute('DELETE FROM works '
                               'WHERE work_id = ?', [work_id])
                return True
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                # Database failed
                raise exceptions.DatabaseQueryError

    def __exit__(self, *args):
        pass
