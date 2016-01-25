# -*- coding: utf-8 -*-
"""typesetting_data

Database operations for text and ribbon storing, retrieving and deleting.
"""
# Operating system functions
import os
# File operations
import io
# We need user interface
from rpi2caster.global_settings import USER_INTERFACE as ui
# Some functions raise custom exceptions
from rpi2caster import exceptions
# Ribbon metadata parsing needs this
from rpi2caster import parsing
# We need to operate on a database
from rpi2caster import database
# Create an instance of Database class with default parameters
DB = database.Database()


class Ribbon(object):
    """Ribbon objects - no matter whether files or database entries.

    A ribbon has the following attributes:
    author, title
    customer
    diecase_id (diecase is selected automatically on casting, so user can e.g.
                view the layout or know which wedge to use)
    unit_shift - bool - stores whether this was coded for unit-shift or not
    contents - series of Monotype codes

    Methods:
    read_from_file - select a file, parse the metadata, set the attributes
    read_from_db - get data from database
    write_to_file - store the metadata and contents in text file
    write_to_db - store the metadata and contents in db
    """
    def __init__(self, ribbon_id=None, diecase_id=None, contents=None):
        self.author = None
        self.title = None
        self.customer = None
        self.diecase_id = diecase_id
        self.unit_shift = False
        self.contents = contents
        # Choose the ribbon automatically or manually
        self.choose_ribbon(ribbon_id)

    def set_author(self):
        """Manually sets the author"""
        prompt = 'Enter the author name for this ribbon: '
        self.author = ui.enter_data_or_blank(prompt) or self.author

    def set_title(self):
        """Manually sets the title"""
        prompt = 'Enter the title: '
        self.title = ui.enter_data_or_blank(prompt) or self.title

    def set_customer(self):
        """Manually sets the customer"""
        prompt = 'Enter the customer\'s name for this ribbon: '
        self.customer = ui.enter_data_or_blank(prompt) or self.customer

    def set_diecase_id(self):
        """Manually sets the diecase ID"""
        prompt = 'Enter the diecase ID for this ribbon: '
        self.diecase_id = ui.enter_data_or_blank(prompt) or self.diecase_id

    def set_unit_shift(self):
        """Chooses whether unit-shift is needed"""
        prompt = 'Is unit shift needed?'
        self.unit_shift = ui.yes_or_no(prompt)

    def choose_ribbon(self, ribbon_id=None):
        """Choose a ribbon from database or file.
        If supplied ribbon_id, try to choose automatically.
        If no ribbon_id or the above failed, choose the ribbon manually
        from database or file.
        """
        # If given an ID on instantiation - look it up in database
        # If no ID given - will select manually
        # If this fails - will load from file
        self.get_from_db(ribbon_id) or self.read_from_file()

    def display_data(self):
        """Displays all available data"""
        if self.author:
            ui.display('Author: %s' % self.author)
        if self.title:
            ui.display('Title: %s' % self.title)
        if self.customer:
            ui.display('Customer: %s' % self.customer)
        if self.diecase_id:
            ui.display('Matrix case ID: %s' % self.diecase_id)
        if self.unit_shift:
            ui.display('This ribbon was coded for casting WITH unit-shift')
        elif self.unit_shift is None:
            ui.display('Unit shift status is not defined')
        else:
            ui.display('This ribbon was coded for casting WITHOUT unit-shift')

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

    def get_from_db(self, ribbon_id):
        """Gets the ribbon from database"""
        try:
            ribbon = DB.ribbon_by_id(ribbon_id)
        except (exceptions.DatabaseQueryError, exceptions.NoMatchingData):
            while True:
                ui.clear()
                ui.display('Choose a ribbon:', end='\n\n')
                available_ribbons = list_ribbons()
                if not available_ribbons:
                    ui.confirm('No ribbons found.')
                    return False
                # Enter the diecase name
                prompt = 'Number of a ribbon? (leave blank to exit): '
                choice = (ui.enter_data_or_blank(prompt) or
                          exceptions.return_to_menu())
                # Safeguards against entering a wrong number
                # or non-numeric string
                try:
                    ribbon_id = available_ribbons[choice]
                    break
                except KeyError:
                    ui.confirm('Ribbon number is incorrect!')
                    continue
        except exceptions.ReturnToMenu:
            return False
        ribbon = DB.ribbon_by_id(ribbon_id)
        (_, self.author, self.title, self.diecase_id, self.customer,
         self.unit_shift, self.contents) = ribbon
        return True

    def store_in_db(self):
        """Stores the ribbon in database"""
        self.display_data()
        # Ask for confirmation
        if ui.yes_or_no('Commit to the database?'):
            DB.add_ribbon(self.title, self.author, self.customer,
                          self.diecase_id, self.unit_shift, self.contents)
            ui.display('Data added successfully.')

    def read_from_file(self):
        """Reads a ribbon file, parses its contents, sets the ribbon attrs"""
        # Ask, and stop here if answered no
        if not ui.yes_or_no('Add the ribbon from file?'):
            return False
        filename = ui.enter_input_filename()
        if not filename:
            return False
        # Initialize the contents
        with io.open(filename, mode='r') as ribbon_file:
            content = [x for x in ribbon_file]
        # Parse the file, get metadata
        metadata = parsing.get_metadata(content)
        # Metadata parsing
        author, title, unit_shift, diecase = None, None, None, None
        if 'diecase' in metadata:
            diecase = metadata['diecase']
        if 'author' in metadata:
            author = metadata['author']
        if ('unit-shift' in metadata and
                metadata['unit-shift'].lower() in ['true', 'on']):
            unit_shift = True
        if ('unit-shift' in metadata and
                metadata['unit-shift'].lower() in ['false', 'off']):
            unit_shift = False
        if 'title' in metadata:
            title = metadata['title']
        add_ribbon(content, title, author, diecase, unit_shift)

    def export_to_file(self):
        """Exports the ribbon to a text file"""
        self.display_data()
        pass


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


def delete_ribbon():
    """Used for deleting a ribbon from database.

    Lists ribbons, then allows user to choose ID.
    """
    while True:
        ribbon_id = choose_ribbon()
        ans = ui.yes_or_no('Are you sure?')
        if ans and DB.delete_ribbon(ribbon_id):
            ui.display('Ribbon deleted successfully.')


def get_ribbon_contents(ribbon_id):
    """get_ribbon_contents:

    Returns the contents of a ribbon.
    """
    ribbon_contents = DB.ribbon_by_id(ribbon_id)[-1]
    return ribbon_contents


def get_ribbon_metadata(ribbon_id):
    """get_ribbon_metadata:

    Returns the ribbon metadata: title, author, diecase ID, unit shift
    requirement.
    """
    ribbon_metadata = DB.ribbon_by_id(ribbon_id)[1:5]
    return ribbon_metadata


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


def show_work():
    """show_work:

    Shows a text file.
    """
    while True:
        # Choose the work
        work_id = choose_work()
        # First, get the work data
        (work_id, title, author, contents) = DB.work_by_id(work_id)
        info = []
        info.append('Title: %s' % title)
        info.append('Autor: %s' % author)
        for line in info:
            ui.display(line)
        ui.display('\n\n')
        # Print it to the screen
        for line in contents:
            ui.display(line)
        ui.confirm('\n')


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


def delete_work():
    """Used for deleting a ribbon from database.

    Lists ribbons, then allows user to choose ID.
    """
    while True:
        work_id = choose_work()
        ans = ui.yes_or_no('Are you sure?')
        if ans and DB.delete_work(work_id):
            ui.display('Ribbon deleted successfully.')


def get_text(work_id):
    """get_text:

    Returns the contents of a text.
    """
    contents = DB.work_by_id(work_id)[-1]
    return contents


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
