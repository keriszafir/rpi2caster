# -*- coding: utf-8 -*-
"""typesetting_data

Database operations for text and ribbon storing, retrieving and deleting.
"""
# File operations
import io
# Object copying
from copy import deepcopy
# Some functions raise custom exceptions
from . import exceptions as e
# Constants for rpi2caster
from .constants import TRUE_ALIASES, ASSIGNMENT_SYMBOLS
# Matrix data for diecases
from . import matrix_data
# Use the same database backend and user interface that matrix_data uses
DB = matrix_data.DB
UI = matrix_data.UI


class EmptyRibbon(object):
    """Ribbon objects - no matter whether files or database entries.

    A ribbon has the following attributes:
    description, customer - strings
    diecase_id (diecase is selected automatically on casting, so user can e.g.
                view the layout or know which wedge to use)
    unit_shift - bool - stores whether this was coded for unit-shift or not
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
    set_[description, customer, diecase_id, unit_shift] - set parameters
        manually

    """
    def __init__(self):
        self.ribbon_id = None
        self.description = None
        self.customer = None
        self.unit_shift = False
        self.filename = None
        self.contents = []
        self.diecase = matrix_data.EmptyDiecase()

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
        self.diecase = matrix_data.Diecase(diecase_id)

    def set_unit_shift(self, unit_shift=False):
        """Chooses whether unit-shift is needed"""
        prompt = 'Is unit shift needed?'
        self.unit_shift = (bool(unit_shift) or UI.confirm(prompt) or
                           self.unit_shift)

    def show_parameters(self):
        """Shows diecase's parameters"""
        data = self.get_parameters()
        info = ['%s: %s' % (desc, value) for (value, desc) in data if value]
        for item in info:
            UI.display(item)

    def get_parameters(self):
        """Gets a list of parameters"""
        data = [('\n', '\nRibbon data'),
                (self.filename, 'File name'),
                (self.ribbon_id, 'Ribbon ID'),
                (self.description, 'Description'),
                (self.customer, 'Customer'),
                (self.diecase.diecase_id, 'Matrix case ID'),
                (self.unit_shift, 'Casting with unit-shift')]
        return data

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

    def copy(self):
        """Copies itself and returns an independent object"""
        return deepcopy(self)

    def get_from_db(self):
        """Gets the ribbon from database"""
        data = choose_ribbon_from_db()
        if data and UI.confirm('Override current data?'):
            (self.ribbon_id, self.description, diecase_id, self.customer,
             self.unit_shift, self.contents) = data
            self.diecase = (diecase_id and self.set_diecase(diecase_id) or
                            self.diecase)
            return True

    def store_in_db(self):
        """Stores the ribbon in database"""
        self.show_parameters()
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
        (self.ribbon_id, self.description, diecase_id, self.customer,
         self.unit_shift, self.contents) = import_ribbon_from_file()
        # Set filename as attribute
        self.filename = filename
        self.diecase = (diecase_id and self.set_diecase(diecase_id) or
                        self.diecase)

    def export_to_file(self, filename=None):
        """Exports the ribbon to a text file"""
        self.show_parameters()
        # Now enter filename for writing
        filename = filename or UI.enter_output_filename()
        if filename:
            # Write everything to the file
            with io.open(filename, mode='w') as ribbon_file:
                for line in self.contents:
                    ribbon_file.write(line)


class Ribbon(EmptyRibbon):
    """A class for ribbons chosen from database or file"""
    def __init__(self, ribbon_id=None, filename=None):
        super().__init__()
        try:
            ribbon_data = (ribbon_id and DB.get_ribbon(ribbon_id) or
                           filename and import_ribbon_from_file(filename) or
                           choose_ribbon_from_db() or
                           import_ribbon_from_file())
            (self.ribbon_id, self.description, diecase_id, self.customer,
             self.unit_shift, self.contents) = ribbon_data
            # Update diecase if correct diecase_id found in ribbon
            self.diecase = (diecase_id and self.set_diecase(diecase_id) or
                            self.diecase)
        # Otherwise use empty ribbon
        except (e.NoMatchingData, e.DatabaseQueryError):
            UI.display('Ribbon choice failed. Starting a new one.')


class EmptyWork(object):
    """Work objects = input files (and input from editor).

    A work object has the following attributes:
    description - e.g. author and title,
    customer - to know for whom we are composing (for commercial workshops),
    type_series, type_size, typeface_name - font data,
    contents - the unprocessed text, utf8-encoded, to be read by the
    typesetting program.
    """
    def __init__(self):
        self.work_id = None
        self.description = None
        self.customer = None
        self.type_size = None
        self.type_series = None
        self.typeface_name = None
        self.text = ''

    def show_parameters(self):
        """Shows diecase's parameters"""
        data = self.get_parameters()
        info = ['%s: %s' % (desc, value) for (value, desc) in data if value]
        for item in info:
            UI.display(item)

    def get_parameters(self):
        """Gets a list of parameters"""
        data = [('\n', '\nWork data'),
                (self.work_id, 'Work ID'),
                (self.description, 'Description'),
                (self.customer, 'Customer'),
                (self.type_series, 'Monotype type series'),
                (self.type_size, 'Type size'),
                (self.typeface_name, 'Typeface name')]
        return data

    def set_work_id(self, work_id=None):
        """Sets the work ID"""
        prompt = 'Work ID? (leave blank to exit) : '
        work_id = work_id or UI.enter_data_or_blank(prompt) or self.work_id
        # Ask if we are sure we want to update this
        # if self.work_id was set earlier
        condition = (not self.work_id or work_id != self.work_id and
                     UI.confirm('Are you sure to change the work ID?'))
        if condition:
            self.work_id = work_id
            return True

    def set_description(self, description=None):
        """Manually sets the work's description"""
        prompt = 'Enter the title: '
        self.description = (description or UI.enter_data_or_blank(prompt) or
                            self.description)

    def set_customer(self, customer=None):
        """Manually sets the customer"""
        prompt = 'Enter the customer\'s name for this work: '
        self.customer = (customer or UI.enter_data_or_blank(prompt) or
                         self.customer)

    def set_typeface(self, type_series=None, type_size=None,
                     typeface_name=None):
        """Sets the type series, size and typeface name"""
        prompt = 'Type series: '
        type_series = (type_series or UI.enter_data_or_blank(prompt) or
                       self.type_series)
        type_size = (type_size or UI.enter_data('Type size in points: ') or
                     self.type_size)
        typeface_name = (typeface_name or UI.enter_data('Typeface name: ') or
                         self.typeface_name)
        # Validate data
        current_data_not_set = not self.type_series and not self.type_size
        if current_data_not_set or UI.confirm('Apply changes?'):
            self.type_series = type_series
            self.type_size = type_size
            self.typeface_name = typeface_name

    def display_text(self):
        """Displays the contents"""
        UI.display(self.text)

    def copy(self):
        """Copies itself and returns an independent object"""
        return deepcopy(self)

    def import_from_file(self, filename=None):
        """Reads a text file and sets contents."""
        self.text = import_work_from_file(filename)

    def delete_from_db(self):
        """Deletes a work from database."""
        if UI.confirm('Are you sure?'):
            try:
                DB.delete_work(self)
                UI.display('Ribbon deleted successfully.')
            except (e.NoMatchingData, e.DatabaseQueryError):
                UI.display('Cannot delete work from database!')

    def store_in_db(self):
        """Stores the work in database"""
        try:
            DB.add_work(self)
            UI.pause('Data added successfully.')
            return True
        except (e.DatabaseQueryError, e.NoMatchingData):
            UI.pause('Cannot store work in database!')


class Work(EmptyWork):
    """A class for works (sources) for typesetting from database or file"""
    def __init__(self, work_id=None, filename=None):
        super().__init__()
        try:
            work_data = (work_id and DB.get_work(work_id) or
                         choose_work_from_db())
            (self.work_id, self.description, self.customer, self.type_series,
             self.type_size, self.typeface_name, self.text) = work_data
        except (e.NoMatchingData, e.DatabaseQueryError):
            UI.display('Work choice failed. Starting a new one.')


def list_ribbons():
    """Lists all ribbons in the database."""
    data = DB.get_all_ribbons()
    results = {}
    UI.display('\n' +
               'Index'.ljust(7) +
               'Ribbon name'.ljust(30) +
               'Title'.ljust(30) +
               'Author'.ljust(30) +
               'Diecase'.ljust(30) +
               'Unit-shift on?'.ljust(15) + '\n')
    for index, ribbon in enumerate(data, start=1):
        # Collect ribbon parameters
        index = str(index)
        row = [index.ljust(7)]
        # Add ribbon name, description, diecase ID
        row.extend([str(field).ljust(30) for field in ribbon])
        # Add unit-shift
        row.append(str(ribbon[5]).ljust(15))
        # Display it all
        UI.display(''.join(row))
        # Add number and ID to the result that will be returned
        results[index] = ribbon[0]
    UI.display('\n\n')
    # Now we can return the number - ribbon ID pairs
    return results


def list_works():
    """Lists all works in the database."""
    data = DB.get_all_works()
    results = {}
    UI.display('\n' +
               'Index'.ljust(7) +
               'Work ID'.ljust(20) +
               'Title'.ljust(20) +
               'Author')
    for index, work in enumerate(data, start=1):
        # Collect work parameters
        index = str(index)
        row = [index.ljust(7)]
        row.extend([str(field).ljust(20) for field in work[:-2]])
        row.append(work[-2])
        UI.display(''.join(row))
        # Add number and ID to the result that will be returned
        results[index] = work[0]
    UI.display('\n\n')
    # Now we can return the number - work ID pairs
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
    parameters = ['diecase', 'description', 'desc', 'unit-shift',
                  'diecase_id', 'customer']
    # Metadata (anything found), contents (the rest)
    metadata = {}
    contents = []
    # Look for parameters line per line, get parameter value
    # If parameters exhausted, append the line to contents
    for line in ribbon:
        for parameter in parameters:
            if line.startswith(parameter):
                for sym in ASSIGNMENT_SYMBOLS:
                    if sym in line:
                        # Data found
                        metadata[parameter] = get_value(line, sym)
                        break
                break
        else:
            contents.append(line)
    # Metadata parsing
    diecase_id = ('diecase' in metadata and metadata['diecase'] or
                  'diecase_id' in metadata and metadata['diecase_id'] or 0)
    description = ('description' in metadata and metadata['description'] or
                   'desc' in metadata and metadata['desc'] or None)
    customer = 'customer' in metadata and metadata['customer'] or None
    unit_shift = ('unit-shift' in metadata and
                  metadata['unit-shift'].lower() in TRUE_ALIASES) or False
    ribbon_id = None
    # Add the whole contents as the attribute
    return (ribbon_id, description, diecase_id, customer, unit_shift, contents)


def import_work_from_file(filename=None):
    """Imports work text from file"""
    filename = filename or UI.enter_input_filename()
    if filename:
        # Initialize the contents
        with io.open(filename, mode='r') as work_file:
            return [x for x in work_file]


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


def choose_work_from_db():
    """Chooses work data from database"""
    prompt = 'Number of a work? (leave blank to exit): '
    while True:
        try:
            data = list_works()
            choice = UI.enter_data_or_blank(prompt, int)
            return choice and DB.get_ribbon(data[choice]) or None
        except KeyError:
            UI.pause('Work number is incorrect!')
        except (e.DatabaseQueryError, e.NoMatchingData):
            UI.display('No works found in database')
            return None
