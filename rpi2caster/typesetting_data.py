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


def choose_ribbon():
    """Lets user choose a ribbon for casting."""
    # Do it only if we have ribbons (depends on list_ribbons retval)
    while True:
        ui.clear()
        ui.display('Choose a ribbon:', end='\n\n')
        available_ribbons = list_ribbons()
        if not available_ribbons:
            ui.confirm('[Enter] to exit...')
            return False
        # Enter the diecase name
        prompt = 'Number of a ribbon? (leave blank to exit): '
        choice = (ui.enter_data_or_blank(prompt) or
                  exceptions.return_to_menu())
        # Safeguards against entering a wrong number or non-numeric string
        try:
            ribbon_id = available_ribbons[choice]
            return ribbon_id
        except KeyError:
            ui.confirm('Ribbon number is incorrect! [Enter] to continue...')
            continue


def show_ribbon():
    """Shows the ribbon contents."""
    while True:
        # Choose the ribbon
        ribbon_id = choose_ribbon()
        # If we cannot retrieve it, then abort
        if not ribbon_id:
            return False
        # First, get the ribbon data
        (ribbon_id, title, author,
         diecase, unit_shift, contents) = DB.ribbon_by_id(ribbon_id)
        # Print it to the screen
        info = []
        info.append('Ribbon name: %s' % ribbon_id)
        info.append('Work title: %s' % title)
        info.append('Author: %s' % author)
        info.append('Diecase ID: %s' % diecase)
        info.append('Unit-shift on?: %s' % unit_shift)
        for line in info:
            ui.display(line)
        ui.display('\n\n')
        for line in contents:
            ui.display(line)
        ui.confirm('\n[Enter] to continue...')


def add_ribbon(contents, title=None, author=None,
               diecase=None, unit_shift=None):
    """Adds a ribbon to the database."""
    prompt = 'Ribbon name: '
    ribbon_id = ui.enter_data_or_blank(prompt) or exceptions.return_to_menu()
    title = title or ui.enter_data('Title: ')
    prompt = 'Author? (default: %s) : ' % os.getlogin()
    author = ui.enter_data_or_blank(prompt) or os.getlogin()
    diecase_id = diecase or ui.enter_data('Diecase name: ')
    unit_shift = unit_shift or ui.yes_or_no('Casting with unit-shift?')
    # Some info for the user
    info = []
    info.append('Title: %s' % title)
    info.append('Autor: %s' % author)
    info.append('Matrix case: %s' % diecase_id)
    info.append('Unit-shift needed: %s' % unit_shift)
    for line in info:
        ui.display(line)
    # Ask for confirmation
    if ui.yes_or_no('Commit to the database?'):
        DB.add_ribbon(ribbon_id, title, author,
                      diecase_id, unit_shift, contents)
        ui.display('Data added successfully.')


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


def submit_ribbon_file():
    """submit_ribbon_file:

    Reads a ribbon file and commits it to the database.
    """
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


def export_ribbon_file():
    """Exports a ribbon from database to the file."""
    # TODO: not implemented yet


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
            ui.confirm('Index number is incorrect! [Enter] to continue...')
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
        ui.confirm('\n[Enter] to continue...')


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
