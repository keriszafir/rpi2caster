# -*- coding: utf-8 -*-
"""matrix_data

Module containing functions for diecase retrieval and parsing,
diecase storing, parameter searches.
"""
# File operations
import io
import os
import csv
# Object copying
from copy import deepcopy
# Some functions raise custom exceptions
from rpi2caster import exceptions
# Wedge operations for several matrix-case management functions
from rpi2caster import wedge_data
# Constants module
from rpi2caster import constants
# Use the same database backend and user interface as wedge_data uses
DB = wedge_data.DB
UI = wedge_data.UI


class EmptyDiecase(object):
    """Diecase: matrix case attributes and operations"""
    def __init__(self):
        self.diecase_id = ''
        self.type_series = ''
        self.type_size = ''
        self.typeface_name = ''
        self.wedge = wedge_data.DefaultWedge()
        self.layout = generate_empty_layout(15, 17)

    def show_layout(self):
        """Shows the diecase layout"""
        UI.display_diecase_layout(self)
        UI.confirm()

    def edit_layout(self):
        """Edits a layout and asks if user wants to save changes"""
        # Edit the layout
        UI.edit_diecase_layout(self)

    def import_layout(self):
        """Imports a layout from file"""
        # Start with an empty layout
        new_layout = generate_empty_layout()
        # Load the layout from file
        submitted_layout = submit_layout_file()
        if not submitted_layout:
            UI.confirm('File does not contain a proper layout!')
            return False
        # Update the empty layout with characters read from file
        # record = (char, styles, column, row, units)
        try:
            for position in new_layout:
                for record in submitted_layout:
                    if record[2] == position[2] and record[3] == position[3]:
                        new_layout[new_layout.index(position)] = record
        except (TypeError, ValueError):
            UI.confirm('Cannot process the uploaded layout!')
            return False
        # Other positions will be empty but defined
        # Now display the layout - need to use a temporary diecase for that
        temp_diecase = EmptyDiecase()
        temp_diecase.layout = new_layout
        temp_diecase.wedge = self.wedge
        UI.display('\nSubmitted layout:\n')
        UI.display_diecase_layout(temp_diecase)
        # Ask for confirmation
        if UI.yes_or_no('Save the changes?'):
            self.layout = new_layout
            return True

    def export_layout(self):
        """Exports the matrix case layout to file."""
        filename = os.path.expanduser('~') + '/%s.csv' % self.diecase_id
        with io.open(filename, 'a') as output_file:
            csv_writer = csv.writer(output_file, delimiter=';', quotechar='"',
                                    quoting=csv.QUOTE_ALL)
            for record in self.layout:
                (char, styles, column, row, units) = record
                csv_writer.writerow([char, ', '.join(styles),
                                     column, row, units])
        UI.confirm('File %s successfully saved.' % filename)
        return True

    def clear_layout(self):
        """Clears a layout for the diecase"""
        layout = generate_empty_layout()
        if UI.yes_or_no('Are you sure?'):
            self.layout = layout

    def set_diecase_id(self, diecase_id=None):
        """Sets a diecase ID"""
        prompt = 'Diecase ID? (leave blank to exit) : '
        diecase_id = (diecase_id or UI.enter_data_or_blank(prompt) or
                      self.diecase_id)
        # Ask if we are sure we want to update this
        # if self.diecase_id was set earlier
        condition = (not self.diecase_id or diecase_id != self.diecase_id and
                     UI.yes_or_no('Are you sure to change diecase ID?'))
        if condition:
            self.diecase_id = diecase_id
            return True

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
        if current_data_not_set or UI.yes_or_no('Apply changes?'):
            self.type_series = type_series
            self.type_size = type_size
            self.typeface_name = typeface_name

    def assign_wedge(self, wedge_series=None, set_width=0):
        """Assigns a wedge (from database or newly-defined) to the diecase"""
        self.wedge = wedge_data.choose_wedge(wedge_series, set_width)

    def show_parameters(self):
        """Shows diecase's parameters"""
        data = self.get_parameters()
        info = ['%s: %s' % (desc, value) for (value, desc) in data if value]
        for item in info:
            UI.display(item)

    def get_parameters(self):
        """Gets a list of parameters"""
        data = [(self.diecase_id, 'Diecase ID'),
                (self.typeface_name, 'Typeface'),
                (self.type_series, 'Type series'),
                (self.type_size, 'Type size')]
        return data

    def save_to_db(self):
        """Stores the matrix case definition/layout in database"""
        try:
            DB.add_diecase(self)
            UI.confirm('Data saved successfully.')
            return True
        except exceptions.DatabaseQueryError:
            UI.confirm('Cannot save the diecase!')

    def delete_from_db(self):
        """Deletes a diecase from database"""
        ans = UI.yes_or_no('Are you sure?')
        if ans and DB.delete_diecase(self):
            UI.display('Matrix case deleted successfully.')
            return True

    def check_db(self):
        """Checks if the diecase is registered in database"""
        try:
            DB.get_diecase(self.diecase_id)
            return True
        except (exceptions.DatabaseQueryError, exceptions.NoMatchingData):
            return False

    def get_styles(self):
        """Parses the diecase layout and gets available typeface styles.
        Returns a list of them."""
        try:
            return list({style for mat in self.layout
                         for style in mat[1] if style})
        except TypeError:
            return []

    def copy(self):
        """Copies itself and returns an independent object"""
        return deepcopy(self)

    def manipulation_menu(self):
        """A menu with all operations on a diecase"""
        # Menu
        try:
            while True:
                messages = ['\nMatrix case manipulation:\n\n'
                            '[V]iew, [C]lear, [E]dit, [I]mport '
                            'or e[X]port layout\nAssign [W]edge, '
                            'change [T]ypeface or diecase [ID]\n']
                self.show_parameters()
                self.wedge.show_parameters()
                options = {'M': exceptions.return_to_menu,
                           'T': self.set_typeface,
                           'W': self.assign_wedge,
                           'ID': self.set_diecase_id,
                           'E': self.edit_layout,
                           'C': self.clear_layout,
                           'V': self.show_layout,
                           'I': self.import_layout,
                           'X': self.export_layout,
                           '': exceptions.menu_level_up}
                # Save to database needs a complete set of metadata
                missing = [x for x in (self.type_series, self.type_size,
                                       self.typeface_name, self.diecase_id)
                           if not x]
                if missing:
                    messages.append('Some data is missing - '
                                    'cannot save to database.\n')
                else:
                    options['S'] = self.save_to_db
                    messages.append('[S]ave diecase to database')
                # Check if it's in the database
                if self.check_db():
                    options['D'] = self.delete_from_db
                    messages.append(', [D]elete diecase from database')
                # Options constructed
                messages.append('\n[M] to exit to menu, or leave blank '
                                'to choose/create another diecase.')
                messages.append('\nYour choice: ')
                message = ''.join(messages)
                UI.simple_menu(message, options)()
        except exceptions.MenuLevelUp:
            # Exit matrix case manipulation menu
            return True


class Diecase(EmptyDiecase):
    """Initialize a diecase object with or without given ID.
    If possible, choose automatically. If this fails, choose manually,
    and if user chooses no diecase, an empty one will be initialized."""
    def __init__(self, diecase_id=None):
        EmptyDiecase.__init__(self)
        # Diecases created with diecase_id will be set up automatically
        temp_diecase = choose_diecase(diecase_id)
        # Assign attributes to diecase we're initializing
        self.diecase_id = temp_diecase.diecase_id
        self.type_series = temp_diecase.type_series
        self.type_size = temp_diecase.type_size
        self.typeface_name = temp_diecase.typeface_name
        self.layout = temp_diecase.layout
        self.wedge = temp_diecase.wedge


def diecase_operations():
    """Matrix case operations menu for inventory management"""
    try:
        UI.display('Matrix case manipulation: '
                   'choose a diecase or define a new one')
        while True:
            # Choose a wedge or initialize a new one
            diecase = choose_diecase()
            diecase.manipulation_menu()
    except exceptions.ReturnToMenu:
        # Exit wedge operations
        return True


def list_diecases():
    """Lists all matrix cases we have."""
    data = DB.get_all_diecases()
    results = {}
    UI.display('\n' +
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
        UI.display(''.join(row))
    UI.display('\n\n')
    # Now we can return the number - diecase ID pairs
    return results


def choose_diecase(diecase_id=None):
    """Lists diecases and lets the user choose one;
    returns the Diecase class object with all parameters set up."""
    # First try to get the diecase by ID:
    try:
        diecase_data = DB.get_diecase(diecase_id)
    except (exceptions.NoMatchingData, exceptions.DatabaseQueryError):
        # If this fails, choose manually
        while True:
            UI.display('Choose a matrix case:', end='\n\n')
            available_diecases = list_diecases()
            # Enter the diecase name
            prompt = 'Number of a diecase or leave blank for an empty one: '
            choice = UI.enter_data_or_blank(prompt)
            if not choice:
                return EmptyDiecase()
            # Safeguards against entering a wrong number or non-numeric string
            try:
                diecase_id = available_diecases[choice]
                diecase_data = DB.get_diecase(diecase_id)
                break
            except (KeyError,
                    exceptions.NoMatchingData,
                    exceptions.DatabaseQueryError):
                UI.confirm('Diecase number is incorrect!')
    (diecase_id, type_series, type_size, wedge_series, set_width,
     typeface_name, layout) = diecase_data
    diecase = EmptyDiecase()
    diecase.diecase_id = diecase_id
    diecase.type_series = type_series
    diecase.type_size = type_size
    diecase.typeface_name = typeface_name
    diecase.layout = layout
    diecase.wedge = wedge_data.Wedge(wedge_series, set_width)
    return diecase


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
    filename = UI.enter_input_filename()
    if not filename:
        return False
    # Initialize the records list
    all_records = []
    # This will store the processed combinations - and whenever a duplicate
    # is detected, the function will raise an exception
    with io.open(filename, 'r') as layout_file:
        input_data = csv.reader(layout_file, delimiter=';', quotechar='"')
        all_records = [record for record in input_data]
        displayed_lines = [' '.join(record) for record in all_records[:5]]
        # Preview file
        UI.display('File preview: displaying first 5 rows:\n')
        UI.display('\n'.join(displayed_lines), end='\n\n')
        # Ask if the first row is a header - if so, away with it
        if UI.yes_or_no('Is the 1st row a table header? '):
            all_records.pop(0)
    if not UI.yes_or_no('Proceed?'):
        return False
    try:
        # Process the records
        processed_records = [process_record(record) for record in all_records]
        # Determine the diecase size based on row and column
        # Get columns and rows lists
        columns = {record[2] for record in processed_records}
        rows = sorted({record[3] for record in processed_records})
        # Check if 17 columns (15x17, 16x17), else 15 columns (old 15x15)
        if 'NI' in columns or 'NL' in columns or 16 in rows:
            columns = constants.COLUMNS_17
        else:
            columns = constants.COLUMNS_15
        # We now have completed uploading a layout and making a list out of it
        layout = [record for row in rows for col in columns
                  for record in processed_records
                  if record[2] == col and record[3] == row]
        # Show the uploaded layout
        return layout
    except (KeyError, ValueError, IndexError):
        return False


def generate_empty_layout(rows=0, columns=0):
    """Generates a table of empty values for matrix case layout"""
    options = {'1': (15, 15), '2': (15, 17), '3': (16, 17)}
    if (rows, columns) not in options.values():
        prompt = "Matrix case size: 1 for 15x15, 2 for 15x17, 3 for 16x17? "
        (rows, columns) = UI.simple_menu(prompt, options)
    # Generate column numbers
    if columns == 17:
        columns_list = constants.COLUMNS_17
    else:
        columns_list = constants.COLUMNS_15
    # Generate row numbers: 1...15 or 1...16
    rows_list = [num + 1 for num in range(rows)]
    # Generate an empty layout with default row unit values
    layout = [['', ['roman'], column, row, 0]
              for row in rows_list for column in columns_list]
    return layout
