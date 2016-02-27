# -*- coding: utf-8 -*-
"""Operations on ribbon and scheme objects: creating, editing and deleting. """
# File operations
import io
# CSV reader/writer
import csv
# Some functions raise custom exceptions
from . import exceptions as e
# Matrix data for diecases
from . import matrix_data
# Constants for rpi2caster
from .constants import ASSIGNMENT_SYMBOLS
# User interface
from .global_settings import UI
# Database
from . import database
DB = database.Database()


class Ribbon(object):
    """Ribbon objects - no matter whether files or database entries.

    A ribbon has the following attributes:
    description, customer - strings
    diecase_id (diecase is selected automatically on casting, so user can e.g.
                view the layout or know which wedge to use)
    contents - series of Monotype codes

    Methods:
    choose_ribbon - choose ribbon automatically or manually,
        first try to get a ribbon with ribbon_id, and if that fails
        ask and select ribbon manually from database, and if that fails
        ask and load ribbon from file
    read_from_file - select a file, parse the metadata, set the attributes
    get_from_db - get data from database
    export_to_file - store the metadata and contents in text file
    store_in_db - store the metadata and contents in db
    set_[description, customer, diecase_id] - set parameters manually"""
    def __init__(self):
        self.ribbon_id = None
        self.description = None
        self.customer = None
        self.filename = None
        self.contents = []
        self.diecase = matrix_data.Diecase()

    def set_ribbon_id(self, ribbon_id=None):
        """Sets the ribbon ID"""
        prompt = 'Ribbon ID? (leave blank to exit) : '
        ribbon_id = (ribbon_id or UI.enter_data_or_blank(prompt) or
                     self.ribbon_id)
        # Ask if we are sure we want to update this
        # if self.ribbon_id was set earlier
        condition = (not self.ribbon_id or ribbon_id != self.ribbon_id and
                     UI.confirm('Are you sure to change the ribbon ID?'))
        if condition:
            self.ribbon_id = ribbon_id
            return True

    def set_description(self, description=None):
        """Manually sets the ribbon's description"""
        prompt = 'Enter the title: '
        self.description = (description or
                            UI.enter_data_or_blank(prompt) or self.description)

    def set_customer(self, customer=None):
        """Manually sets the customer"""
        prompt = 'Enter the customer\'s name for this ribbon: '
        self.customer = (customer or
                         UI.enter_data_or_blank(prompt) or self.customer)

    def set_diecase(self, diecase_id=None):
        """Chooses the diecase for this ribbon"""
        self.diecase = matrix_data.SelectDiecase(diecase_id)

    @property
    def parameters(self):
        """Gets a list of parameters"""
        return [('\n', '\nRibbon data'),
                (self.filename, 'File name'),
                (self.ribbon_id, 'Ribbon ID'),
                (self.description, 'Description'),
                (self.customer, 'Customer'),
                (self.diecase.diecase_id, 'Matrix case ID')]

    def display_contents(self):
        """Displays the ribbon's contents, line after line"""
        UI.display('Ribbon contents preview:\n')
        contents_generator = (line for line in self.contents if line)
        try:
            while True:
                UI.display(contents_generator.__next__())
        except StopIteration:
            # End of generator
            UI.pause('Finished', UI.MSG_MENU)
        except (EOFError, KeyboardInterrupt):
            # Press ctrl-C to abort displaying long ribbons
            UI.pause('Aborted', UI.MSG_MENU)

    def get_from_db(self):
        """Gets the ribbon from database"""
        data = choose_ribbon_from_db()
        if data and UI.confirm('Override current data?'):
            (self.ribbon_id, self.description, diecase_id,
             self.customer, self.contents) = data
            self.diecase = (diecase_id and self.set_diecase(diecase_id) or
                            self.diecase)
            return True

    def store_in_db(self):
        """Stores the ribbon in database"""
        UI.display_parameters(self.parameters)
        # Ask for confirmation
        try:
            DB.add_ribbon(self)
            UI.pause('Ribbon added successfully.')
            return True
        except (e.DatabaseQueryError, e.NoMatchingData):
            UI.pause('Cannot store ribbon in database!')
            return False

    def delete_from_db(self):
        """Deletes a ribbon from database."""
        if UI.confirm('Are you sure?'):
            DB.delete_ribbon(self)
            UI.display('Ribbon deleted successfully.')

    def import_from_file(self, filename=None):
        """Reads a ribbon file, parses its contents, sets the ribbon attrs"""
        (self.ribbon_id, self.description, diecase_id,
         self.customer, self.contents) = import_ribbon_from_file()
        # Set filename as attribute
        self.filename = filename
        self.diecase = (diecase_id and self.set_diecase(diecase_id) or
                        self.diecase)

    def export_to_file(self, filename=None):
        """Exports the ribbon to a text file"""
        UI.display_parameters(self.parameters)
        # Choose file, write metadata, write contents
        filename = filename or UI.enter_output_filename()
        with io.open(filename, mode='w+') as ribbon_file:
            ribbon_file.write('diecase: ' + self.diecase.diecase_id)
            ribbon_file.write('description: ' + self.description)
            ribbon_file.write('customer: ' + self.customer)
            for line in self.contents:
                ribbon_file.write(line)


class SelectRibbon(Ribbon):
    """A class for ribbons chosen from database or file"""
    def __init__(self, ribbon_id=None, filename=None):
        super().__init__()
        try:
            ribbon_data = (ribbon_id and DB.get_ribbon(ribbon_id) or
                           filename and import_ribbon_from_file(filename) or
                           choose_ribbon_from_db() or
                           import_ribbon_from_file())
            (self.ribbon_id, self.description, diecase_id,
             self.customer, self.contents) = ribbon_data
            # Update diecase if correct diecase_id found in ribbon
            self.diecase = (diecase_id and self.set_diecase(diecase_id) or
                            self.diecase)
        # Otherwise use empty ribbon
        except (e.NoMatchingData, e.DatabaseQueryError):
            UI.display('Ribbon choice failed. Starting a new one.')


class FontScheme(object):
    """Font schemes store information about how many of each character is to be
    cast when casting typecases. Each language has its own."""
    def __init__(self):
        self.scheme_id = None
        self.description = None
        self.language = None
        self.layout = {}

    @property
    def parameters(self):
        """Gets a list of parameters"""
        return [('\n', '\nScheme data'),
                (self.scheme_id, 'Font scheme ID'),
                (self.description, 'Description'),
                (self.language, 'Language')]

    def set_scheme_id(self, scheme_id=None):
        """Sets the scheme ID"""
        prompt = 'Scheme ID? (leave blank to exit) : '
        scheme_id = (scheme_id or UI.enter_data_or_blank(prompt) or
                     self.scheme_id)
        # Ask if we are sure we want to update this
        # if self.scheme_id was set earlier
        condition = (not self.scheme_id or scheme_id != self.scheme_id and
                     UI.confirm('Are you sure to change the scheme ID?'))
        if condition:
            self.scheme_id = scheme_id
            return True

    def set_description(self, description=None):
        """Manually sets the scheme's description"""
        prompt = 'Enter the title: '
        self.description = (description or UI.enter_data_or_blank(prompt) or
                            self.description)

    def set_language(self, language=None):
        """Manually sets the language"""
        prompt = 'Enter the language for this font scheme: '
        self.language = (language or UI.enter_data_or_blank(prompt) or
                         self.language)

    def import_from_file(self, filename=None):
        """Reads a text file and sets contents."""
        self.layout = import_scheme_from_file(filename)

    def delete_from_db(self):
        """Deletes a scheme from database."""
        if UI.confirm('Are you sure?'):
            try:
                DB.delete_scheme(self)
                UI.display('Font scheme definition deleted successfully.')
            except (e.NoMatchingData, e.DatabaseQueryError):
                UI.display('Cannot delete scheme from database!')

    def store_in_db(self):
        """Stores the scheme in database"""
        try:
            DB.add_scheme(self)
            UI.pause('Data added successfully.')
            return True
        except (e.DatabaseQueryError, e.NoMatchingData):
            UI.pause('Cannot store scheme in database!')


class SelectFontScheme(FontScheme):
    """A class for font schemes selected from database or file"""
    def __init__(self, scheme_id=None, filename=None):
        super().__init__()
        try:
            scheme_data = (scheme_id and DB.get_scheme(scheme_id) or
                           choose_scheme_from_db())
            (self.scheme_id, self.description, self.language,
             self.layout) = scheme_data
        except (TypeError, e.NoMatchingData, e.DatabaseQueryError):
            UI.display('Scheme choice failed. Starting a new one.')
            self.layout = import_scheme_from_file(filename)


def list_ribbons():
    """Lists all ribbons in the database."""
    data = DB.get_all_ribbons()
    results = {}
    UI.display('\n' +
               'Index'.ljust(7) +
               'Ribbon name'.ljust(30) +
               'Title'.ljust(30) +
               'Author'.ljust(30) +
               'Diecase'.ljust(30) + '\n')
    for index, ribbon in enumerate(data, start=1):
        # Collect ribbon parameters
        index = str(index)
        row = [index.ljust(7)]
        # Add ribbon name, description, diecase ID
        row.extend([str(field).ljust(30) for field in ribbon])
        # Display it all
        UI.display(''.join(row))
        # Add number and ID to the result that will be returned
        results[index] = ribbon[0]
    UI.display('\n\n')
    # Now we can return the number - ribbon ID pairs
    return results


def list_schemes():
    """Lists all font schemes in the database."""
    data = DB.get_all_schemes()
    results = {}
    UI.display('\n' +
               'Index'.ljust(7) +
               'Scheme ID'.ljust(20) +
               'Description'.ljust(20) +
               'Language'.ljust(20))
    for index, scheme in enumerate(data, start=1):
        # Collect scheme parameters
        index = str(index)
        row = [index.ljust(7)]
        row.extend([str(field).ljust(20) for field in scheme[:-1]])
        UI.display(''.join(row))
        # Add number and ID to the result that will be returned
        results[index] = scheme[0]
    UI.display('\n\n')
    # Now we can return the number - scheme ID pairs
    return results


def import_ribbon_from_file(filename=None):
    """Imports ribbon from file, parses parameters, returns a list of them"""
    def get_value(line, symbol):
        """Helper function - strips whitespace and symbols"""
        # Split the line on an assignment symbol, get the second part,
        # strip any whitespace or multipled symbols
        return line.split(symbol, 1)[-1].strip(symbol).strip()

    UI.display('Loading the ribbon from file...')
    try:
        filename = filename or UI.enter_input_filename()
        with io.open(filename, mode='r') as ribbon_file:
            ribbon = [line.strip() for line in ribbon_file if line.strip()]
    except (FileNotFoundError, IOError):
        UI.pause('Cannot open ribbon file %s' % filename)
        return False
    # What to look for
    keywords = ['diecase', 'description', 'desc', 'diecase_id', 'customer']
    # Metadata (anything found), contents (the rest)
    metadata = {}
    contents = []
    # Look for parameters line per line, get parameter value
    # If parameters exhausted, append the line to contents
    for line in ribbon:
        for keyword in keywords:
            if line.startswith(keyword):
                for sym in ASSIGNMENT_SYMBOLS:
                    if sym in line:
                        # Data found
                        metadata[keyword] = get_value(line, sym)
                        break
                break
        else:
            contents.append(line)
    # Metadata parsing
    diecase_id = metadata.get('diecase', '') or metadata.get('diecase_id', '')
    description = metadata.get('description', '') or metadata.get('desc', '')
    customer = metadata.get('customer', '')
    ribbon_id = None
    # Add the whole contents as the attribute
    return (ribbon_id, description, diecase_id, customer, contents)


def import_scheme_from_file(filename=None):
    """Imports scheme text from file"""
    filename = filename or UI.enter_input_filename()
    # Initialize the contents
    with io.open(filename, mode='r') as scheme_file:
        input_data = csv.reader(scheme_file, delimiter=';', quotechar='"')
        all_records = [record for record in input_data]
    displayed_lines = [' '.join(record) for record in all_records[:5]]
    # Preview file
    UI.display('File preview: displaying first 5 rows:\n')
    UI.display('\n'.join(displayed_lines), end='\n\n')
    # Ask if the first row is a header - if so, away with it
    if UI.confirm('Is the 1st row a table header? '):
        all_records.pop(0)
        if not UI.confirm('Proceed?'):
            return False
    try:
        return [(char, style, int(qty)) for char, style, qty in all_records]
    except (KeyError, ValueError, IndexError):
        return []


def choose_ribbon_from_db():
    """Chooses ribbon data from database"""
    prompt = 'Number of a ribbon? (leave blank to exit): '
    while True:
        try:
            data = list_ribbons()
            choice = UI.enter_data_or_blank(prompt, int)
            return choice and DB.get_ribbon(data[choice]) or None
        except KeyError:
            UI.pause('Ribbon number is incorrect!')
        except (e.DatabaseQueryError, e.NoMatchingData):
            UI.display('No ribbons found in database')
            return None


def choose_scheme_from_db():
    """Chooses scheme data from database"""
    prompt = 'Number of a scheme? (leave blank to exit): '
    while True:
        try:
            data = list_schemes()
            choice = UI.enter_data_or_blank(prompt, int)
            return choice and DB.get_scheme(data[choice]) or None
        except KeyError:
            UI.pause('Font scheme number is incorrect!')
        except (e.DatabaseQueryError, e.NoMatchingData):
            UI.display('No font schemes found in database')
            return None
