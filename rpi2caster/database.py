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
        database_path = global_settings.DATABASE_PATH or '/var/rpi2caster/db'
        # Connect to the database
        try:
            self.db_connection = sqlite3.connect(database_path)
        except (sqlite3.OperationalError, sqlite3.DatabaseError):
            raise exceptions.WrongConfiguration('Cannot connect to database!')

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
                # Database failed
                raise exceptions.DatabaseQueryError

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
                wedge = list(wedge)
                # wedge[0] - ID
                # wedge[1] - name
                # wedge[2] - set width
                # Change return value of brit_pica to boolean:
                wedge[3] = bool(wedge[3])
                # Change return value of steps to list:
                wedge[4] = json.loads(wedge[4])
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
                wedge = cursor.fetchone()
                wedge = list(wedge)
                # Change return value of brit_pica to boolean:
                wedge[3] = bool(wedge[3])
                # Change return value of steps to list:
                wedge[4] = json.loads(wedge[4])
                # Return wedge
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
        """get_all_wedges(self):

        Gets all wedges stored in database, with their step unit values.

        Returns a list of all wedges found or raises an exception.
        """
        with self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                cursor.execute('SELECT * FROM wedges')
                # Check if we got any:
                results = cursor.fetchall()
                if not results:
                    raise exceptions.NoMatchingData
                return results
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

        layout = [[character, [style1, style2...], column, row, units], [...]]
        character = single character, double/triple character (for ligatures),
        ' ' for low space and '_' for high space
        style1, style2... - one or more styles a matrix belongs to,
        this will enable a matrix to be used with specified text styles only
        column - string (NI, NL, A...O)
        row_number - int (1...15 or 16)
        unit_width - int (unit width of a character) or None if not specified
        """

        # data - a list with wedge parameters to be written,
        # layout is a JSON-encoded dictionary
        layout = json.dumps(layout)
        data = [diecase_id, type_series, type_size, wedge_series, set_width,
                typeface_name, layout]
        with self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                # Create the table first:
                cursor.execute('CREATE TABLE IF NOT EXISTS matrix_cases ('
                               'diecase_id TEXT PRIMARY KEY, '
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
        """diecase_by_id(diecase_id):

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

    def __exit__(self, *args):
        pass
