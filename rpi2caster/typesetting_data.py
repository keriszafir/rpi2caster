# -*- coding: utf-8 -*-
"""typesetting_data

Database operations for text and ribbon storing, retrieving and deleting.
"""
# File operations
import io
# Object copying
from copy import deepcopy
# Some functions raise custom exceptions
from rpi2caster import exceptions
# Constants for rpi2caster
from rpi2caster import constants
# Matrix data for diecases
from rpi2caster import matrix_data
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
        self.unit_shift = unit_shift or UI.yes_or_no(prompt) or self.unit_shift

    def show_parameters(self):
        """Shows diecase's parameters"""
        data = self.get_parameters()
        info = ['%s: %s' % (desc, value) for (value, desc) in data if value]
        for item in info:
            UI.display(item)

    def get_parameters(self):
        """Gets a list of parameters"""
        data = [(self.filename, 'File name'),
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
            UI.confirm('Finished', UI.MSG_MENU)
        except (EOFError, KeyboardInterrupt):
            # Press ctrl-C to abort displaying long ribbons
            UI.confirm('Aborted', UI.MSG_MENU)

    def copy(self):
        """Copies itself and returns an independent object"""
        return deepcopy(self)

    def get_from_db(self, ribbon_id=None):
        """Gets the ribbon from database"""
        ribbon = choose_ribbon(ribbon_id or self.ribbon_id)
        if UI.yes_or_no('Override current data?'):
            self = ribbon

    def store_in_db(self):
        """Stores the ribbon in database"""
        self.show_parameters()
        # Ask for confirmation
        if UI.yes_or_no('Commit to the database?'):
            DB.add_ribbon(self)
            UI.display('Data added successfully.')

    def delete_from_db(self):
        """Deletes a ribbon from database."""
        if UI.yes_or_no('Are you sure?'):
            DB.delete_ribbon(self)
            UI.display('Ribbon deleted successfully.')

    def read_from_file(self, filename=None):
        """Reads a ribbon file, parses its contents, sets the ribbon attrs"""
        # Ask, and stop here if answered no
        UI.display('Loading the ribbon from file...')
        try:
            filename = filename or UI.enter_input_filename()
            if not filename:
                return False
        except exceptions.ReturnToMenu:
            return False
        # Initialize the contents
        with io.open(filename, mode='r') as ribbon_file:
            contents = [x.strip() for x in ribbon_file if x.strip()]
        # Parse the file, get metadata
        metadata = get_ribbon_metadata(contents)
        # Metadata parsing
        self.description, self.customer = None, None
        self.unit_shift, diecase_id, self.contents = False, 0, []
        if 'diecase' in metadata:
            diecase_id = metadata['diecase']
        elif 'diecase_id' in metadata:
            diecase_id = metadata['diecase_id']
        if 'description' in metadata:
            self.description = metadata['description']
        if 'customer' in metadata:
            self.customer = metadata['customer']
        if ('unit-shift' in metadata and
                metadata['unit-shift'].lower() in constants.TRUE_ALIASES):
            self.unit_shift = True
        elif ('unit-shift' in metadata and
              metadata['unit-shift'].lower() in constants.FALSE_ALIASES):
            self.unit_shift = False
        # Add the whole contents as the attribute
        self.contents = contents
        # Info about the filename
        self.filename = filename
        # Choose diecase automatically
        self.set_diecase(diecase_id)

    def export_to_file(self):
        """Exports the ribbon to a text file"""
        self.show_parameters()
        # Now enter filename for writing
        filename = UI.enter_output_filename()
        if not filename:
            return False
        # Write everything to the file
        with io.open(filename, mode='w') as ribbon_file:
            for line in self.contents:
                ribbon_file.write(line)


class Ribbon(EmptyRibbon):
    """A class for new/empty ribbons"""
    def __init__(self, ribbon_id=None, filename=None):
        EmptyRibbon.__init__(self)
        self.filename = filename
        self.ribbon_id = ribbon_id
        if filename or not self.get_from_db(ribbon_id):
            self.read_from_file(filename)


class EmptyWork(object):
    """Work objects = input files (and input from editor).

    A work object has the following attributes:
    author, title,
    customer - to know for whom we are composing (for commercial workshops),
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
        data = [(self.work_id, 'Work ID'),
                (self.description, 'Description'),
                (self.customer, 'Customer'),
                (self.type_series, 'Monotype type series'),
                (self.type_size, 'Type size'),
                (self.typeface_name, 'Typeface name')]
        return data

    def set_work_id(self):
        """Adds a work to the database."""
        prompt = 'Work name: '
        self.work_id = UI.enter_data_or_blank(prompt) or self.work_id

    def set_description(self):
        """Manually sets the work's description"""
        prompt = 'Enter the title: '
        self.description = UI.enter_data_or_blank(prompt) or self.description

    def set_customer(self):
        """Manually sets the customer"""
        prompt = 'Enter the customer\'s name for this work: '
        self.customer = UI.enter_data_or_blank(prompt) or self.customer

    def set_typeface(self):
        """Sets the type series, size and typeface name"""
        prompt = 'Fount series (leave blank to abort): '
        type_series = UI.enter_data_or_blank(prompt)
        if not type_series:
            return
        type_size = UI.enter_data('Type size in points: ')
        typeface_name = UI.enter_data('Typeface name: ')
        # Validate data
        current_data_not_set = not self.type_series and not self.type_size
        if current_data_not_set or UI.yes_or_no('Apply changes?'):
            self.type_series = type_series
            self.type_size = type_size
            self.typeface_name = typeface_name

    def display_text(self):
        """Displays the contents"""
        UI.display(self.text)

    def copy(self):
        """Copies itself and returns an independent object"""
        return deepcopy(self)

    def read_from_file(self):
        """Reads a text file and sets contents."""
        if not self.text or UI.yes_or_no('Overwrite current content?'):
            filename = UI.enter_input_filename()
            if filename:
                # Initialize the contents
                with io.open(filename, mode='r') as work_file:
                    self.text = [x for x in work_file]

    def delete_from_db(self):
        """Deletes a work from database."""
        if UI.yes_or_no('Are you sure?'):
            try:
                DB.delete_work(self)
                UI.display('Ribbon deleted successfully.')
            except (exceptions.NoMatchingData, exceptions.DatabaseQueryError):
                UI.display('Cannot delete work from database!')

    def store_in_db(self):
        """Stores the work in database"""
        if UI.confirm('Store the work in database?'):
            DB.add_work(self)
            UI.display('Data added successfully.')


class Work(EmptyWork):
    """A class for new/empty works (sources) for typesetting"""
    def __init__(self, work_id=None, text=None):
        EmptyWork.__init__(self)
        self.work_id = work_id
        self.text = text


def check_if_ribbons():
    """Checks if any ribbons are available in the database"""
    try:
        return bool(DB.get_all_ribbons())
    except exceptions.DatabaseQueryError:
        return False


def list_ribbons():
    """Lists all ribbons in the database."""
    try:
        data = DB.get_all_ribbons()
    except exceptions.DatabaseQueryError:
        UI.display('Cannot access ribbon database!')
        return None
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


def choose_ribbon(ribbon_id=None):
    """Chooses a ribbon from database, returns ribbon id"""
    try:
        # Automatic choice
        ribbon_data = DB.get_ribbon(ribbon_id)
    except (exceptions.NoMatchingData, exceptions.DatabaseQueryError):
        while True:
            UI.clear()
            UI.display('Choose a ribbon or leave blank to start a new one: ',
                       end='\n\n')
            available_ribbons = list_ribbons()
            if not available_ribbons:
                return EmptyRibbon()
            # Enter the diecase name or raise an exception to break the loop
            prompt = 'Number of a ribbon? (leave blank to exit): '
            choice = (UI.enter_data_or_blank(prompt) or
                      exceptions.return_to_menu())
            # Safeguards against entering a wrong number
            # or non-numeric string
            try:
                ribbon_id = available_ribbons[choice]
                ribbon_data = DB.get_ribbon(ribbon_id)
                break
            except (KeyError,
                    exceptions.DatabaseQueryError, exceptions.NoMatchingData):
                UI.confirm('Ribbon number is incorrect!')
    # Construct a new ribbon object
    ribbon = EmptyRibbon()
    (ribbon.description, diecase_id, ribbon.customer,
     ribbon.unit_shift, ribbon.contents) = ribbon_data
    # Assign diecase to ribbon
    ribbon.set_diecase(diecase_id)
    return ribbon


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


def choose_work(work_id=None):
    """Lets user choose a text file for typesetting."""
    # Do it only if we have diecases (depends on list_diecases retval)
    try:
        work_data = DB.get_ribbon(work_id)
    except (exceptions.NoMatchingData, exceptions.DatabaseQueryError):
        while True:
            UI.clear()
            UI.display('Choose a text:', end='\n\n')
            available_works = list_works()
            # Enter the diecase name
            prompt = 'Number of a work? (leave blank to exit): '
            choice = UI.enter_data_or_blank(prompt, int)
            if not choice:
                return EmptyWork()
            # Safeguards against entering a wrong number or non-numeric string
            try:
                work_data = DB.get_work(available_works[choice])
                break
            except KeyError:
                UI.confirm('Index number is incorrect!')
    # Construct a new work object
    work = EmptyWork()
    (work.work_id, work.description, work.customer, work.type_series,
     work.type_size, work.typeface_name, work.text) = work_data
    return work


def get_ribbon_metadata(content):
    """get_metadata:

    Catches the parameters included at the beginning of the ribbon.
    These parameters are used for storing diecase ID, set width, title etc.
    and serve mostly informational purposes, but can also be used for
    controlling some aspects of the program (e.g. displaying characters
    being cast).

    The row is parsed if it starts with a parameter, then the assignment
    operator is used for splitting the string in two (parameter and value),
    and a dictionary with parsed parameters is returned.
    """
    parameters = ['diecase', 'description', 'unit-shift', 'justification',
                  'diecase_id', 'customer']
    symbols = ['=', ':', ' ']
    result = {}
    # Work on an unmodified copy and delete lines from the sequence
    for line in content[:]:
        for parameter in parameters:
            if line.startswith(parameter):
                for symbol in symbols:
                    members = line.split(symbol, 1)
                    try:
                        value = members[1].strip()
                        result[parameter] = value
                        break
                    except (IndexError, ValueError):
                        pass
                content.remove(line)
    return result
