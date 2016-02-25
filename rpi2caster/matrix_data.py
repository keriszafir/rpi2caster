# -*- coding: utf-8 -*-
"""Module containing functions for diecase retrieval and parsing,
diecase storing, parameter searches.
"""
# File operations
import io
import os
import csv
# Object copying
from copy import deepcopy
# Some functions raise custom exceptions
from . import exceptions as e
# Wedge operations for several matrix-case management functions
from . import wedge_data
# Constants module
from . import constants as c
# Parsing module
from . import parsing as p
# Use the same database backend and user interface as wedge_data uses
DB = wedge_data.DB
UI = wedge_data.UI


class Diecase(object):
    """Diecase: matrix case attributes and operations"""
    def __init__(self):
        self.diecase_id = ''
        self.type_series = ''
        self.type_size = ''
        self.typeface_name = ''
        self.wedge = wedge_data.Wedge()
        self.layout = generate_empty_layout(15, 17)

    def show_layout(self):
        """Shows the diecase layout"""
        UI.display_diecase_layout(self)
        UI.pause()

    def edit_layout(self):
        """Edits a layout and asks if user wants to save changes"""
        # Edit the layout
        UI.edit_diecase_layout(self)

    def get_matrix(self, char='', *styles):
        """Chooses a matrix manually"""
        matrix = Matrix()
        matrix.diecase = self
        if char:
            UI.display('Enter matrix data for character: %s' % char)
        styles = styles
        prompt = 'Combination? (default: G5): '
        code_string = UI.enter_data_or_blank(prompt).upper() or 'G5'
        combination = p.parse_signals(code_string)
        # Got a list of signals
        row = p.get_row(combination)
        column = p.get_column(combination)
        # Default unit width value = determine based on wedge
        units = self.wedge.unit_arrangement[row]
        prompt = 'Unit width? (default: %s): ' % units
        units = abs(UI.enter_data_or_blank(prompt, int) or units)
        matrix.char = char
        matrix.styles = styles
        matrix.column = column
        matrix.row = row
        matrix.units = units
        return matrix

    def import_layout(self):
        """Imports a layout from file"""
        # Start with an empty layout
        new_layout = generate_empty_layout()
        # Load the layout from file
        submitted_layout = import_layout_file()
        if not submitted_layout:
            UI.pause('File does not contain a proper layout!')
            return False
        # Update the empty layout with characters read from file
        # record = (char, styles, column, row, units)
        try:
            for position in new_layout:
                for record in submitted_layout:
                    if record[2] == position[2] and record[3] == position[3]:
                        new_layout[new_layout.index(position)] = record
        except (TypeError, ValueError):
            UI.pause('Cannot process the uploaded layout!')
            return False
        # Other positions will be empty but defined
        # Now display the layout - need to use a temporary diecase for that
        temp_diecase = Diecase()
        temp_diecase.layout = new_layout
        temp_diecase.wedge = self.wedge
        UI.display('\nSubmitted layout:\n')
        UI.display_diecase_layout(temp_diecase)
        # Ask for confirmation
        if UI.confirm('Save the changes?'):
            self.layout = new_layout
            return True

    def export_layout(self):
        """Exports the matrix case layout to file."""
        filename = os.path.expanduser('~') + '/%s.csv' % self.diecase_id
        with io.open(filename, 'a') as output_file:
            csv_writer = csv.writer(output_file, delimiter=';', quotechar='"',
                                    quoting=csv.QUOTE_ALL)
            csv_writer.writerow(['Character', 'Style(s)', 'Column', 'Row',
                                 'Unit width'])
            for record in self.layout:
                (char, styles, column, row, units) = record
                csv_writer.writerow([char, ', '.join(styles),
                                     column, row, units])
        UI.pause('File %s successfully saved.' % filename)
        return True

    def clear_layout(self):
        """Clears a layout for the diecase"""
        layout = generate_empty_layout()
        if UI.confirm('Are you sure?'):
            self.layout = layout

    def set_diecase_id(self, diecase_id=None):
        """Sets a diecase ID"""
        prompt = 'Diecase ID? (leave blank to exit) : '
        diecase_id = (diecase_id or UI.enter_data_or_blank(prompt) or
                      self.diecase_id)
        # Ask if we are sure we want to update this
        # if self.diecase_id was set earlier
        condition = (not self.diecase_id or diecase_id != self.diecase_id and
                     UI.confirm('Are you sure to change diecase ID?'))
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
        if current_data_not_set or UI.confirm('Apply changes?'):
            self.type_series = type_series
            self.type_size = type_size
            self.typeface_name = typeface_name

    def assign_wedge(self, wedge_series=None, set_width=0):
        """Assigns a wedge (from database or newly-defined) to the diecase"""
        self.wedge = wedge_data.SelectWedge(wedge_series, set_width)

    @property
    def parameters(self):
        """Gets a list of parameters"""
        return [('\n', '\nMatrix case data'),
                (self.diecase_id, 'Diecase ID'),
                (self.typeface_name, 'Typeface'),
                (self.type_series, 'Type series'),
                (self.type_size, 'Type size')]

    def save_to_db(self):
        """Stores the matrix case definition/layout in database"""
        try:
            DB.add_diecase(self)
            UI.pause('Data saved successfully.')
            return True
        except e.DatabaseQueryError:
            UI.pause('Cannot save the diecase!')

    def delete_from_db(self):
        """Deletes a diecase from database"""
        ans = UI.confirm('Are you sure?')
        if ans and DB.delete_diecase(self):
            UI.display('Matrix case deleted successfully.')
            return True

    def check_db(self):
        """Checks if the diecase is registered in database"""
        try:
            DB.get_diecase(self.diecase_id)
            return True
        except (e.DatabaseQueryError, e.NoMatchingData):
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
                UI.clear()
                UI.display_parameters(self.parameters, self.wedge.parameters)
                options = {'M': e.return_to_menu,
                           'T': self.set_typeface,
                           'W': self.assign_wedge,
                           'ID': self.set_diecase_id,
                           'E': self.edit_layout,
                           'C': self.clear_layout,
                           'V': self.show_layout,
                           'I': self.import_layout,
                           'X': self.export_layout,
                           '': e.menu_level_up}
                messages = ['\nMatrix case manipulation:\n\n'
                            '[V]iew, [C]lear or resize, [E]dit, [I]mport '
                            'or e[X]port layout\nAssign [W]edge, '
                            'change [T]ypeface or diecase [ID]\n\n']
                # Save to database needs a complete set of metadata
                required = {'Type series': self.type_series,
                            'Type size': self.type_size,
                            'Typeface / font family name': self.typeface_name,
                            'Diecase ID': self.diecase_id}
                missing = [item for item in required if not required[item]]
                messages.extend([item + ' is not set\n' for item in missing])
                if not missing:
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
        except e.MenuLevelUp:
            # Exit matrix case manipulation menu
            return True


class SelectDiecase(Diecase):
    """Initialize a diecase object with or without given ID.
    If possible, choose automatically. If this fails, choose manually,
    and if user chooses no diecase, an empty one will be initialized."""
    def __init__(self, diecase_id=None):
        super().__init__()
        # Diecases created with diecase_id will be set up automatically
        try:
            diecase_data = (diecase_id and DB.get_diecase(diecase_id) or
                            choose_diecase())
            (self.diecase_id, self.type_series, self.type_size, wedge_series,
             set_width, self.typeface_name, self.layout) = diecase_data
            self.wedge = wedge_data.SelectWedge(wedge_series, set_width)
        except (KeyError, TypeError, e.NoMatchingData, e.DatabaseQueryError):
            UI.display('Diecase choice failed. Using empty one instead.')


class Matrix(object):
    """A class for single matrices - all matrix data"""
    def __init__(self):
        self.char = ''
        self.styles = []
        self.column = 'O'
        self.row = 15
        self.units = 18
        self.diecase = Diecase()

    @property
    def row_units(self):
        """Gets the row's unit width value for the diecase's wedge"""
        return self.diecase.wedge.unit_arrangement[self.row]

    @property
    def row(self):
        """Gets the row number"""
        return self.__dict__.get('_row', 5)

    @row.setter
    def row(self, value):
        """Gets the row number"""
        value = int(value)
        value = max(1, value)
        value = min(value, 16)
        self.__dict__['_row'] = value

    @property
    def code(self):
        """Gets the matrix code"""
        return self.column + str(self.row)


def diecase_operations():
    """Matrix case operations menu for inventory management"""
    try:
        UI.display('Matrix case manipulation: '
                   'choose a diecase or define a new one')
        while True:
            # Choose a wedge or initialize a new one
            SelectDiecase().manipulation_menu()
    except e.ReturnToMenu:
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


def choose_diecase():
    """Lists diecases and lets the user choose one;
    returns the Diecase class object with all parameters set up."""
    prompt = 'Number of a diecase or leave blank for an empty one: '
    while True:
        try:
            UI.display('Choose a matrix case:', end='\n\n')
            data = list_diecases()
            choice = UI.enter_data_or_blank(prompt)
            return choice and DB.get_diecase(data[choice]) or None
        except KeyError:
            UI.pause('Diecase number is incorrect!')
        except (e.NoMatchingData, e.DatabaseQueryError):
            UI.display('No diecases found in database')
            return None


def import_layout_file():
    """Reads a matrix case arrangement from a text or csv file.
    The format should be:
    "character";"style1,style2...";"column";"row";"unit_width"
    """
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
        if UI.confirm('Is the 1st row a table header? '):
            all_records.pop(0)
    if not UI.confirm('Proceed?'):
        return False
    try:
        # Process the records
        processed_records = [process_record(record) for record in all_records]
        # Determine the diecase size based on row and column
        # Get columns and rows lists
        columns = {record[2] for record in processed_records}
        rows = sorted({record[3] for record in processed_records})
        # Check if 17 columns (15x17, 16x17), else 15 columns (old 15x15)
        big_layout = 'NI' in columns or 'NL' in columns or 16 in rows
        columns_list = big_layout and c.COLUMNS_17 or c.COLUMNS_15
        # We now have completed uploading a layout and making a list out of it
        layout = [record for row in rows for col in columns_list
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
    columns_list = columns == 17 and c.COLUMNS_17 or c.COLUMNS_15
    # Generate row numbers: 1...15 or 1...16
    rows_list = [num + 1 for num in range(rows)]
    # Generate an empty layout with default row unit values
    layout = [['', ['roman'], column, row, 0]
              for row in rows_list for column in columns_list]
    return layout


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
