# -*- coding: utf-8 -*-
"""matrix_data

Module containing functions for diecase retrieval and parsing,
diecase storing, parameter searches.
"""
# File operations
import io
import csv
# We need user interface
from rpi2caster.global_settings import USER_INTERFACE as ui
# Some functions raise custom exceptions
from rpi2caster import exceptions
# We need to operate on a database
from rpi2caster import database
# Wedge operations for several matrix-case management functions
from rpi2caster import wedge_data
# Create an instance of Database class with default parameters
DB = database.Database()


def lookup_diecase(type_series, type_size):
    """lookup_diecase

    Searches for a diecase of given type series (e.g. 327) and size (e.g. 12),
    if several matches found - allows to choose one of them, returns data.
    """
    data = DB.diecase_by_series_and_size(type_series, type_size)
    if len(data) == 1:
        # One result found
        return data[0]
    else:
        # More than one record - let user decide which one to use:
        match = {record[0]: record for record in data}
        # Display a menu with diecases from 1 to the last:
        id_numbers = [(i, k) for i, k in enumerate(data, start=1)]
        header = 'Choose a diecase:'
        choice = ui.menu(id_numbers, header)
        # Choose a diecase and return a list of its parameters:
        return match[id_numbers[choice]]


def list_diecases():
    """Lists all matrix cases we have."""
    data = DB.get_all_diecases()
    results = {}
    ui.clear()
    ui.display('\n' +
               'Index'.ljust(7) +
               'Diecase ID'.ljust(20) +
               'Type series'.ljust(15) +
               'Type size'.ljust(15) +
               'Wedge series'.ljust(15) +
               'Set width'.ljust(15) +
               'Typeface name' + '\n')
    for index, diecase in enumerate(data, start=1):
        # Collect diecase parameters
        index = str(index)
        row = [index.ljust(7)]
        row.append(str(diecase[0]).ljust(20))
        row.extend([str(field).ljust(15) for field in diecase[1:-2]])
        # Add number and ID to the result that will be returned
        results[index] = diecase[0]
        # Add typeface name - no justification!
        row.append(diecase[-2])
        ui.display(''.join(row))
    ui.display('\n\n')
    # Now we can return the number - diecase ID pairs
    return results


def choose_diecase(diecase_id=None):
    """Lists diecases and lets the user choose one; returns the record."""
    # First try to get the diecase by ID:
    if diecase_id:
        try:
            return DB.diecase_by_id(diecase_id)
        except (exceptions.NoMatchingData, exceptions.DatabaseQueryError):
            pass
    # If this fails, choose manually
    while True:
        ui.display('Choose a matrix case:', end='\n\n')
        available_diecases = list_diecases()
        # Enter the diecase name
        prompt = 'Number of a diecase or [Enter] to exit: '
        choice = (ui.enter_data_or_blank(prompt) or
                  exceptions.return_to_menu())
        # Safeguards against entering a wrong number or non-numeric string
        try:
            diecase_id = available_diecases[choice]
            return DB.diecase_by_id(diecase_id)
        except (KeyError,
                exceptions.NoMatchingData,
                exceptions.DatabaseQueryError):
            ui.confirm('Diecase number is incorrect! [Enter] to continue...')
            continue


def show_diecase(diecase_id):
    """show_diecase:

    Wrapper function for menu: used for choosing and showing a diecase layout.
    """
    # First, get diecase data
    try:
        (_, _, _, wedge_series, set_width,
         _, layout) = DB.diecase_by_id(diecase_id)
        # Process metadata
        # Get wedge unit arrangement
        unit_arr = wedge_data.get_unit_arrangement(wedge_series, set_width)
        ui.display_diecase_layout(layout, unit_arr)
    except exceptions.NoMatchingData:
        ui.display('Diecase layout not defined or cannot be displayed.')


def add_diecase():
    """add_diecase:

    Adds a matrix case to the database.
    Can be called with arguments from another function, or the user can enter
    the data manually.
    Displays info and asks for confirmation.
    """
    prompt = 'Diecase ID? (leave blank to exit) : '
    diecase_id = ui.enter_data_or_blank(prompt) or exceptions.menu_level_up()
    type_series = ui.enter_data('Fount series: ')
    type_size = ui.enter_data('Type size (end with D for Didot): ')
    wedge_series = ui.enter_data('Wedge/stopbar series for this typeface: ')
    # If we enter S5 etc. - save it as 5
    wedge_series = wedge_series.strip('sS')
    set_width = ui.enter_data_spec_type('Set width (decimal): ', float)
    typeface_name = ui.enter_data('Typeface name: ')
    # Ask if we want to enter a layout file from file
    if ui.yes_or_no('Add layout from file?'):
        layout = submit_layout_file()
    else:
        # otherwise ask for diecase format and generate an empty layout
        layout = generate_empty_layout()
    # Edit the layout
    if ui.yes_or_no('Do you want to edit the layout now?'):
        # Get unit arrangement for editing the wedge
        unit_arr = wedge_data.get_unit_arrangement(wedge_series, set_width)
        layout = ui.edit_diecase_layout(layout, unit_arr)
    # Display parameters before asking to commit
    info = []
    info.append('Diecase ID: %s' % diecase_id)
    info.append('Type series: %s' % type_series)
    info.append('Type size: %s' % type_size)
    info.append('Wedge series: %s' % wedge_series)
    info.append('Set width: %s' % set_width)
    info.append('Typeface name: %s' % typeface_name)
    info.append('Styles present: %s' % ', '.join(get_styles(layout)))
    for line in info:
        ui.display(line)
    # Ask for confirmation
    if ui.yes_or_no('Commit to the database?'):
        DB.add_diecase(diecase_id, type_series, type_size, wedge_series,
                       float(set_width), typeface_name, layout)
        ui.display('Data added successfully.')


def edit_diecase(diecase_id):
    """edit_diecase:

    Chooses and edits a diecase layout.

    If layout is blank, user needs to enter the column and row numbers.
    Displays characters that were previously in position,
    allows to change them.
    A matrix can be used or not (for example, multiple-cell mats
    should be addressed only at one of these cells, where the centering pin
    can descend - and not where no hole is made, because trying to
    address such a cell can damage the caster!).
    If user wants to enter a space - decide if it is low or high.
    At the end, confirm and commit.
    """
    layout = get_layout(diecase_id)
    # Edit the layout?
    old_layout = layout[:]
    new_layout = ui.edit_diecase_layout(layout)
    # Check if any changes were made - if not, skip the rest
    if new_layout != old_layout:
        # Ask for confirmation
        ans = ui.yes_or_no('Commit to the database?')
        if ans and DB.update_diecase_layout(diecase_id, new_layout):
            ui.display('Matrix case layout updated successfully.')


def load_layout(diecase_id):
    """load_layout:

    Allows user to upload a matrix case layout from a CSV file.
    At the end, confirm and commit.
    """
    # Start with an empty layout
    layout = generate_empty_layout()
    # Load the layout from file
    try:
        submitted_layout = submit_layout_file()
    except (TypeError, ValueError):
        ui.confirm('File does not contain a proper layout!')
        exceptions.menu_level_up()
    # Update the empty layout with characters read from file
    # record = (char, styles, column, row, units)
    try:
        for position in layout:
            for record in submitted_layout:
                if record[2] == position[2] and record[3] == position[3]:
                    layout[layout.index(position)] = record
    except (TypeError, ValueError):
        ui.confirm('Cannot process the uploaded layout!')
        exceptions.menu_level_up()
    # Other positions will be empty - like in a freshly generated null layout
    # Ask for confirmation
    ui.display('\nSubmitted layout:\n')
    ui.display_diecase_layout(layout)
    ans = ui.yes_or_no('Commit to the database?')
    if ans and DB.update_diecase_layout(diecase_id, layout):
        ui.display('Matrix case layout uploaded successfully.')


def clear_diecase(diecase_id):
    """clear_diecase:

    Clears the diecase layout, so it can be entered from scratch.
    You usually want to use this if you seriously mess something up.
    """
    layout = generate_empty_layout()
    ans = ui.yes_or_no('Are you sure?')
    if ans and DB.update_diecase_layout(diecase_id, layout):
        ui.display('Matrix case purged successfully - now empty.')


def delete_diecase(diecase_id):
    """Used for deleting a diecase from database.

    Lists diecases, then allows user to choose ID.
    """
    ans = ui.yes_or_no('Are you sure?')
    if ans and DB.delete_diecase(diecase_id):
        ui.display('Matrix case deleted successfully.')


def get_diecase_parameters(diecase_id):
    """get_diecase_parameters:

    Displays parameters for a chosen matrix case and returns them.
    """
    (diecase_id, type_series, type_size, wedge_series, set_width,
     typeface_name, layout) = DB.diecase_by_id(diecase_id)
    # Display parameters before editing
    info = []
    info.append('Diecase ID: %s' % diecase_id)
    info.append('Type series: %s' % type_series)
    info.append('Type size: %s' % type_size)
    info.append('Wedge series: %s' % wedge_series)
    info.append('Set width: %s' % set_width)
    info.append('Typeface name: %s' % typeface_name)
    info.append('Styles present: %s' % ', '.join(get_styles(layout)))
    for line in info:
        ui.display(line)
    ui.display('\n\n')
    # Return data for further processing
    return (type_series, type_size, wedge_series, set_width,
            typeface_name, layout)


def get_layout(diecase_id):
    """get_layout:

    Displays parameters for a chosen matrix case and returns them.
    """
    layout = DB.diecase_by_id(diecase_id)[-1]
    return layout


def get_styles(layout):
    """Parses the diecase layout and gets available typeface styles.
    Returns a list of them."""
    try:
        return list({style for mat in layout for style in mat[1] if style})
    except TypeError:
        return []


def submit_layout_file():
    """submit_layout_file:

    Reads a matrix case arrangement from a text or csv file.
    The format should be:
    "character";"style1,style2...";"column";"row";"unit_width"
    """
    def process_record(record):
        """Prepares the record found in file for adding to the layout"""
        # A record is a list with all diecase data:
        # [character, (style1, style2...), column, row, units]
        # Add a character - first item; if it's a space, don't change it
        try:
            # 5 fields in a record = unit value given
            # Unit value must be converted to int
            (char, styles, column, row, units) = record
            units = int(units.strip())
        except (ValueError, AttributeError):
            # 4 fields = unit value not given
            # (or unit value cannot be converted to int)
            (char, styles, column, row) = record
            units = 0
        if char != ' ':
            char = char.strip()
        styles = [style.strip() for style in styles.split(',')]
        row = int(row.strip())
        column = column.strip()
        # Pack it again
        return (char, styles, column, row, units)

    # Give us a file or end here
    try:
        filename = ui.enter_input_filename()
    except exceptions.ReturnToMenu:
        exceptions.menu_level_up()
    if not filename:
        exceptions.menu_level_up()
    # Initialize the records list
    all_records = []
    # This will store the processed combinations - and whenever a duplicate
    # is detected, the function will raise an exception
    with io.open(filename, 'r') as layout_file:
        input_data = csv.reader(layout_file, delimiter=';', quotechar='"')
        all_records = [record for record in input_data]
        displayed_lines = [' '.join(record) for record in all_records[:5]]
        # Preview file
        ui.display('File preview: displaying first 5 rows:\n')
        ui.display('\n'.join(displayed_lines), end='\n\n')
        # Ask if the first row is a header - if so, away with it
        if ui.yes_or_no('Is the 1st row a table header? '):
            all_records.pop(0)
    if not ui.yes_or_no('Proceed?'):
        exceptions.menu_level_up()
    # Process the records
    processed_records = [process_record(record) for record in all_records]
    # Determine the diecase size based on row and column
    # Get columns and rows lists
    columns = {record[2] for record in processed_records}
    rows = sorted({record[3] for record in processed_records})
    # Check if 17 columns (15x17, 16x17), else 15 columns (old 15x15)
    if 'NI' in columns or 'NL' in columns or max(rows) == 16:
        columns = ['NI', 'NL']
    else:
        columns = []
    columns.extend([x for x in 'ABCDEFGHIJKLMNO'])
    # We now have completed uploading a layout and making a list out of it
    layout = [record for row in rows for col in columns
              for record in processed_records
              if record[2] == col and record[3] == row]
    # Show the uploaded layout
    return layout


def generate_empty_layout():
    """Generates a table of empty values for matrix case layout"""
    prompt = "Matrix case size: 1 for 15x15, 2 for 15x17, 3 for 16x17? "
    options = {'1': (15, 15), '2': (15, 17), '3': (16, 17)}
    (rows_number, columns_number) = ui.simple_menu(prompt, options)
    # Generate column numbers
    if columns_number == 17:
        columns = ['NI', 'NL']
    else:
        columns = []
    columns.extend([letter for letter in 'ABCDEFGHIJKLMNO'])
    # Generate row numbers: 1...15 or 1...16
    rows = [num + 1 for num in range(rows_number)]
    # Generate an empty layout with default row unit values
    layout = [['', ['roman'], column, row, 0]
              for row in rows for column in columns]
    return layout
