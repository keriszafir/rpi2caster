# -*- coding: utf-8 -*-
"""Operations on ribbon and scheme objects: creating, editing and deleting. """
# File operations
import io
# Some functions raise custom exceptions
from . import exceptions as e
# Constants for rpi2caster
from .constants import ASSIGNMENT_SYMBOLS
# User interface
from .global_config import UI
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
    def __init__(self, ribbon_id='', filename='', manual_choice=False):
        data = None
        self.filename = ''
        if ribbon_id:
            try:
                data = DB.get_ribbon(ribbon_id)
            except (e.NoMatchingData, e.DatabaseQueryError):
                UI.display('Ribbon choice failed. Starting a new one.')
        elif filename:
            self.filename = filename
            data = import_ribbon_from_file(filename)
        elif manual_choice:
            data = choose_ribbon_from_db() or import_ribbon_from_file()
        # Got data - unpack them, set the attributes
        if not data:
            data = ['', 'New ribbon', 'No customer', '', 'S5-12E', []]
        (self.ribbon_id, self.description, self.customer, self.diecase_id,
         self.wedge_name, self.contents) = data

    def __iter__(self):
        return iter(self.contents)

    def __next__(self):
        yield from self.contents

    def __repr__(self):
        return self.ribbon_id or ''

    def __bool__(self):
        return bool(self.contents)

    def set_ribbon_id(self, ribbon_id=None):
        """Sets the ribbon ID"""
        prompt = 'Ribbon ID? (leave blank to exit) : '
        ribbon_id = (ribbon_id or UI.enter_data_or_blank(prompt) or
                     self.ribbon_id)
        # Ask if we are sure we want to update this
        # if self.ribbon_id was set earlier
        prompt = 'Are you sure to change the ribbon ID?'
        condition = not self.ribbon_id or UI.confirm(prompt, default=False)
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

    def set_diecase(self, diecase_id=''):
        """Chooses the diecase for this ribbon"""
        self.diecase_id = diecase_id

    def set_wedge(self, wedge_name=None):
        """Sets a wedge for the ribbon"""
        self.wedge_name = wedge_name

    @property
    def parameters(self):
        """Gets a list of parameters"""
        return [(self.filename, 'File name'),
                (self.ribbon_id, 'Ribbon ID'),
                (self.description, 'Description'),
                (self.customer, 'Customer'),
                (self.diecase_id, 'Matrix case ID'),
                (self.wedge_name, 'Wedge')]

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
        if data and UI.confirm('Override current data?', default=False):
            (self.ribbon_id, self.description, self.customer, self.diecase_id,
             self.wedge_name, self.contents) = data

    def store_in_db(self):
        """Stores the ribbon in database"""
        UI.display_parameters({'Ribbon data': self.parameters})
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
        if UI.confirm('Are you sure?', default=False):
            DB.delete_ribbon(self)
            UI.display('Ribbon deleted successfully.')

    def import_from_file(self, filename=None):
        """Reads a ribbon file, parses its contents, sets the ribbon attrs"""
        self.filename = filename
        (self.ribbon_id, self.description, self.customer, self.diecase_id,
         self.wedge_name, self.contents) = import_ribbon_from_file()

    def export_to_file(self, filename=None):
        """Exports the ribbon to a text file"""
        UI.display_parameters({'Ribbon data': self.parameters})
        try:
            # Choose file, write metadata, write contents
            filename = filename or UI.enter_output_filename()
        except e.ReturnToMenu:
            return
        with io.open(filename, mode='w+') as ribbon_file:
            ribbon_file.write('description: ' + self.description)
            ribbon_file.write('customer: ' + self.customer)
            ribbon_file.write('diecase: ' + self.diecase_id)
            ribbon_file.write('wedge: ' + self.wedge_name)
            for line in self.contents:
                ribbon_file.write(line)


def list_ribbons():
    """Lists all ribbons in the database."""
    data = DB.get_all_ribbons()
    results = {}
    UI.display('\n' +
               'No.'.ljust(5) +
               'Ribbon name'.ljust(30) +
               'Description'.ljust(30) +
               'Customer'.ljust(30) +
               'Diecase'.ljust(30) +
               'Wedge'.ljust(30) +
               '\n\n0 - start a new empty ribbon\n')
    for index, ribbon in enumerate(data, start=1):
        # Collect ribbon parameters
        row = [str(index).ljust(5)]
        # Add ribbon name, description, diecase ID
        row.extend([field.ljust(30) for field in ribbon[:-1]])
        # Display it all
        UI.display(''.join(row))
        # Add number and ID to the result that will be returned
        results[index] = ribbon[0]
    UI.display('\n\n')
    # Now we can return the number - ribbon ID pairs
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
    except e.ReturnToMenu:
        return False
    # What to look for
    keywords = ['diecase', 'description', 'desc', 'diecase_id', 'customer',
                'wedge', 'stopbar']
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
    ribbon_id = None
    description = metadata.get('description', '') or metadata.get('desc', '')
    customer = metadata.get('customer', '')
    diecase_id = metadata.get('diecase', '') or metadata.get('diecase_id', '')
    wedge = metadata.get('wedge', '') or metadata.get('stopbar', '')
    # Add the whole contents as the attribute
    return (ribbon_id, description, customer, diecase_id, wedge, contents)


def choose_ribbon_from_db():
    """Chooses ribbon data from database"""
    prompt = 'Number of a ribbon? (0 for a new one, leave blank to exit): '
    while True:
        try:
            data = list_ribbons()
            choice = UI.enter_data_or_exception(prompt, e.ReturnToMenu, int)
            if not choice:
                return None
            else:
                return DB.get_ribbon(data[choice])
        except KeyError:
            UI.pause('Ribbon number is incorrect!')
        except (e.DatabaseQueryError, e.NoMatchingData):
            UI.display('No ribbons found in database')
            return None
