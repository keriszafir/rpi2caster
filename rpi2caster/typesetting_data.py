# -*- coding: utf-8 -*-
"""typesetting_data

Database operations for text and ribbon storing, retrieving and deleting.
"""
# Operating system functions
import os
# File operations
import io
# Some functions raise custom exceptions
from rpi2caster import exceptions
# Ribbon metadata parsing needs this
from rpi2caster import parsing
# Constants for rpi2caster
from rpi2caster import constants
# Matrix data for diecases
from rpi2caster import matrix_data
# Use the same database backend and user interface that matrix_data uses
DB = matrix_data.DB
ui = matrix_data.ui


class Ribbon(object):
    """Ribbon objects - no matter whether files or database entries.

    A ribbon has the following attributes:
    author, title, customer - strings
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
    set_[author, title, customer, diecase_id, unit_shift] - set parameters
        manually

    """
    def __init__(self, diecase_id=None, filename=None, contents=()):
        self.author = None
        self.title = None
        self.customer = None
        self.diecase = matrix_data.Diecase(diecase_id)
        self.unit_shift = False
        self.filename = filename
        # Start with empty or contents or what was passed on instantiation
        self.contents = contents
        self.setup(filename=filename)

    def set_author(self, author=None):
        """Manually sets the author"""
        prompt = 'Enter the author name for this ribbon: '
        self.author = author or ui.enter_data_or_blank(prompt) or self.author

    def set_title(self, title=None):
        """Manually sets the title"""
        prompt = 'Enter the title: '
        self.title = title or ui.enter_data_or_blank(prompt) or self.title

    def set_customer(self, customer=None):
        """Manually sets the customer"""
        prompt = 'Enter the customer\'s name for this ribbon: '
        self.customer = (customer or ui.enter_data_or_blank(prompt) or
                         self.customer)

    def set_diecase(self, diecase_id=None):
        """Chooses the diecase for this ribbon"""
        self.diecase = matrix_data.Diecase(diecase_id)

    def set_unit_shift(self, unit_shift=False):
        """Chooses whether unit-shift is needed"""
        prompt = 'Is unit shift needed?'
        self.unit_shift = unit_shift or ui.yes_or_no(prompt) or self.unit_shift

    def setup(self, ribbon_id=None, filename=None):
        """Choose a ribbon from database or file.
        If supplied ribbon_id, try to choose automatically.
        If no ribbon_id or the above failed, choose the ribbon manually
        from database or file.
        """
        # If called with a filename - select from file
        # If called with ID - select automatically from database
        # If no or wrong ID given - will select manually
        # If this fails - will load from file
        if filename or not self.get_from_db(ribbon_id):
            self.read_from_file(filename)

    def display_data(self):
        """Displays all available data"""
        if self.author:
            ui.display('Author: %s' % self.author)
        if self.title:
            ui.display('Title: %s' % self.title)
        if self.customer:
            ui.display('Customer: %s' % self.customer)
        if self.diecase.diecase_id:
            ui.display('Matrix case ID: %s' % self.diecase.diecase_id)
        if self.unit_shift:
            ui.display('This ribbon was coded for casting WITH unit-shift.')
        elif self.unit_shift is None:
            ui.display('Unit shift status is not defined.')
        else:
            ui.display('This ribbon was coded for casting WITHOUT unit-shift.')

    def display_contents(self):
        """Displays the ribbon's contents, line after line"""
        ui.display('Ribbon contents preview:\n')
        try:
            for line in self.contents:
                ui.display(line)
        except KeyboardInterrupt:
            # Press ctrl-C to abort displaying long ribbons
            pass
        ui.confirm('', ui.MSG_MENU)

    def get_from_db(self, ribbon_id=None):
        """Gets the ribbon from database"""
        # Check if we have any ribbons in the database at all... if not, exit
        if not check_if_ribbons():
            ui.display('No ribbons found in database.')
            return False
        # If id not supplied, choose a ribbon
        question = 'Select ribbon from database?'
        ribbon_id = ribbon_id or ui.yes_or_no(question) and choose_ribbon()
        # Now get its parameters
        try:
            ribbon = DB.ribbon_by_id(ribbon_id)
            # Set ribbon attributes
            (self.author, self.title, diecase_id, self.customer,
             self.unit_shift, self.contents) = ribbon
            # Choose diecase automatically or manually
            self.set_diecase(diecase_id)
            return True
        except (exceptions.DatabaseQueryError,
                exceptions.NoMatchingData,
                exceptions.ReturnToMenu):
            return False

    def store_in_db(self):
        """Stores the ribbon in database"""
        self.display_data()
        # Ask for confirmation
        if ui.yes_or_no('Commit to the database?'):
            DB.add_ribbon(self.title, self.author, self.customer,
                          self.diecase.diecase_id,
                          self.unit_shift, self.contents)
            ui.display('Data added successfully.')

    def read_from_file(self, filename=None):
        """Reads a ribbon file, parses its contents, sets the ribbon attrs"""
        # Ask, and stop here if answered no
        ui.display('Loading the ribbon from file...')
        try:
            filename = filename or ui.enter_input_filename()
            if not filename:
                return False
        except exceptions.ReturnToMenu:
            return False
        # Initialize the contents
        with io.open(filename, mode='r') as ribbon_file:
            contents = [x.strip('\n') for x in ribbon_file]
        # Parse the file, get metadata
        metadata = parsing.get_metadata(contents)
        print(metadata)
        # Metadata parsing
        self.author, self.title, self.customer = None, None, None
        self.unit_shift, diecase_id, self.contents = False, 0, None
        if 'diecase' in metadata:
            diecase_id = metadata['diecase']
        elif 'diecase_id' in metadata:
            diecase_id = metadata['diecase_id']
        if 'author' in metadata:
            self.author = metadata['author']
        if 'title' in metadata:
            self.title = metadata['title']
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
        self.display_data()
        # Now enter filename for writing
        filename = ui.enter_output_filename()
        if not filename:
            return False
        # Write everything to the file
        with io.open(filename, mode='w') as ribbon_file:
            for line in self.contents:
                ribbon_file.write(line)


class Work(object):
    """Work objects = input files (and input from editor).

    A work object has the following attributes:
    author, title,
    customer - to know for whom we are composing (for commercial workshops),
    contents - the unprocessed text, utf8-encoded, to be read by the
                typesetting program."""
    def __init__(self, contents=None):
        self.work_id = None
        self.title = None
        self.author = None
        self.customer = None
        self.contents = contents

    def display_data(self):
        """Displays work's id, author and title"""
        ui.display('ID: %s' % self.work_id)
        ui.display('Title: %s' % self.title)
        ui.display('Author: %s' % self.author)
        ui.display('Customer: %s' % self.customer)

    def set_author(self):
        """Manually sets the work's author"""
        prompt = 'Enter the author name for this work: '
        self.author = ui.enter_data_or_blank(prompt) or self.author

    def set_title(self):
        """Manually sets the work's title"""
        prompt = 'Enter the title: '
        self.title = ui.enter_data_or_blank(prompt) or self.title

    def set_customer(self):
        """Manually sets the customer"""
        prompt = 'Enter the customer\'s name for this work: '
        self.customer = ui.enter_data_or_blank(prompt) or self.customer


def check_if_ribbons():
    """Checks if any ribbons are available in the database"""
    try:
        DB.get_all_ribbons()
        return True
    except exceptions.DatabaseQueryError:
        return False


def list_ribbons():
    """Lists all ribbons in the database."""
    try:
        data = DB.get_all_ribbons()
    except exceptions.DatabaseQueryError:
        ui.display('Cannot access ribbon database!')
        return None
    results = {}
    ui.display('\n' +
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
        # Add ribbon name, author, title, diecase ID
        row.extend([str(field).ljust(30) for field in ribbon[1:4]])
        # Add unit-shift
        row.append(str(ribbon[5]).ljust(15))
        # Display it all
        ui.display(''.join(row))
        # Add number and ID to the result that will be returned
        results[index] = ribbon[0]
    ui.display('\n\n')
    # Now we can return the number - ribbon ID pairs
    return results


def delete_ribbon(ribbon_id=None):
    """Used for deleting a ribbon from database.

    Lists ribbons, then allows user to choose ID.
    """
    while True:
        ribbon_id = ribbon_id or choose_ribbon() or exceptions.return_to_menu()
        ans = ui.yes_or_no('Are you sure?')
        if ans and DB.delete_ribbon(ribbon_id):
            ui.display('Ribbon deleted successfully.')


def choose_ribbon():
    """Chooses a ribbon from database, returns ribbon id"""
    while True:
        ui.clear()
        ui.display('Choose a ribbon:', end='\n\n')
        available_ribbons = list_ribbons()
        if not available_ribbons:
            ui.confirm('No ribbons found.')
            return None
        # Enter the diecase name or raise an exception to break the loop
        prompt = 'Number of a ribbon? (leave blank to exit): '
        choice = (ui.enter_data_or_blank(prompt) or
                  exceptions.return_to_menu())
        # Safeguards against entering a wrong number
        # or non-numeric string
        try:
            ribbon_id = available_ribbons[choice]
            return ribbon_id
        except KeyError:
            ui.confirm('Ribbon number is incorrect!')
            continue


def list_works():
    """Lists all works in the database."""
    data = DB.get_all_works()
    results = {}
    ui.display('\n' +
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
        ui.display(''.join(row))
        # Add number and ID to the result that will be returned
        results[index] = work[0]
    ui.display('\n\n')
    # Now we can return the number - work ID pairs
    return results


def choose_work():
    """Lets user choose a text file for typesetting."""
    # Do it only if we have diecases (depends on list_diecases retval)
    while True:
        ui.clear()
        ui.display('Choose a text:', end='\n\n')
        available_works = list_works()
        # Enter the diecase name
        prompt = 'Number of a work? (leave blank to exit): '
        choice = (ui.enter_data_or_blank(prompt) or
                  exceptions.return_to_menu())
        # Safeguards against entering a wrong number or non-numeric string
        try:
            work_id = available_works[choice]
            return work_id
        except KeyError:
            ui.confirm('Index number is incorrect!')
            continue


def add_work(contents, title=None, author=None):
    """add_work:

    Adds a work to the database.
    """
    prompt = 'Work name: '
    work_id = ui.enter_data_or_blank(prompt) or exceptions.return_to_menu()
    title = title or ui.enter_data('Title: ')
    prompt = 'Author? (default: %s) : ' % os.getlogin()
    author = ui.enter_data_or_blank(prompt) or os.getlogin()
    # Some info for the user
    info = []
    info.append('Work ID: %s' % work_id)
    info.append('Title: %s' % title)
    info.append('Autor: %s' % author)
    for line in info:
        ui.display(line)
    # Ask for confirmation
    if ui.yes_or_no('Commit to the database?'):
        DB.add_work(work_id, title, author, contents)
        ui.display('Data added successfully.')


def delete_work(work_id=None):
    """Used for deleting a ribbon from database.

    Lists ribbons, then allows user to choose ID.
    """
    while True:
        work_id = work_id or choose_work() or exceptions.return_to_menu()
        ans = ui.yes_or_no('Are you sure?')
        if ans and DB.delete_work(work_id):
            ui.display('Ribbon deleted successfully.')


def submit_work_file():
    """submit_work_file:

    Reads a text file and commits it to the database.
    """
    # Ask, and stop here if answered no
    if not ui.yes_or_no('Add the work from file?'):
        return False
    filename = ui.enter_input_filename()
    if not filename:
        return False
    # Initialize the contents
    with io.open(filename, mode='r') as work_file:
        contents = [x for x in work_file]
    add_work(contents)
