# -*- coding: utf-8 -*-
"""Module containing functions for diecase retrieval and parsing,
diecase storing, parameter searches.
"""
# File operations
import io
import os
import csv

# Some functions raise custom exceptions
from . import exceptions as e
# Wedge operations for several matrix-case management functions
from . import wedge_data
# Constants module
from . import constants as c
# Parsing module
from . import parsing as p
# Database backend
from . import database
# User interface
from .global_settings import UI
DB = database.Database()


class Diecase(object):
    """Diecase: matrix case attributes and operations"""
    def __init__(self):
        self.diecase_id = ''
        self.type_series = ''
        self.type_size = ''
        self.typeface_name = ''
        self.wedge = wedge_data.Wedge()
        self.matrices = None
        self.generate_empty_layout(15, 17)

    def __iter__(self):
        return iter(self.matrices)

    def __next__(self):
        yield from self.matrices

    def show_layout(self):
        """Shows the diecase layout"""
        UI.display_diecase_layout(self)
        UI.pause()

    def edit_layout(self):
        """Edits a layout and asks if user wants to save changes"""
        # Edit the layout
        UI.edit_diecase_layout(self)

    def get_matrix(self, char='', style='roman'):
        """Chooses a matrix manually"""
        matrix = Matrix(char, [style])
        matrix.diecase = self
        if char:
            UI.display('Enter matrix data for character: %s' % char)
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
        matrix.column = column
        matrix.row = row
        matrix.units = units
        return matrix

    def decode_matrix(self, code):
        """Finds the matrix based on the column and row in layout"""
        return [mat for mat in self.matrices if mat.code == code.upper()][0]

    def import_layout(self):
        """Imports a layout from file"""
        # Load the layout from file
        submitted_layout = import_layout_file()
        if not submitted_layout:
            UI.pause('File does not contain a proper layout!')
            return False
        # Update the empty layout with characters read from file
        # record = (char, styles, column, row, units)
        try:
            self.generate_empty_layout()
            for matrix in self.matrices:
                for record in submitted_layout:
                    (char, styles, column, row, units) = record
                    if matrix.column == column and matrix.row == row:
                        matrix.char = char
                        matrix.styles = styles
                        matrix.units = units
        except (TypeError, ValueError):
            UI.pause('Cannot process the uploaded layout!')
            return False

    def export_layout(self):
        """Exports the matrix case layout to file."""
        filename = os.path.expanduser('~') + '/%s.csv' % self.diecase_id
        with io.open(filename, 'a') as output_file:
            csv_writer = csv.writer(output_file, delimiter=';', quotechar='"',
                                    quoting=csv.QUOTE_ALL)
            csv_writer.writerow(['Character', 'Style(s)', 'Column', 'Row',
                                 'Unit width'])
            for matrix in self.matrices:
                (char, styles, column, row, units) = matrix.record
                csv_writer.writerow([char, ', '.join(styles),
                                     column, row, units])
        UI.pause('File %s successfully saved.' % filename)
        return True

    def generate_empty_layout(self, rows=None, columns=None):
        """Makes a list of empty matrices, row for row, column for column"""
        prompt = ('Matrix case size: 1 for 15x15, 2 for 15x17, 3 for 16x17? '
                  '(leave blank to cancel) : ')
        options = {'1': (15, 15), '2': (15, 17), '3': (16, 17), '': ()}
        if (rows, columns) not in options.values():
            choice = UI.simple_menu(prompt, options)
            if not choice:
                return
            (rows, columns) = choice
        # Generate column numbers
        columns_list = columns == 17 and c.COLUMNS_17 or c.COLUMNS_15
        # Generate row numbers: 1...15 or 1...16
        rows_list = [num + 1 for num in range(rows)]
        self.matrices = [Matrix(coordinates=(column, row),
                                units=self.wedge.unit_arrangement[row])
                         for row in rows_list for column in columns_list]

    @property
    def layout(self):
        """Gets a diecase layout as a list of lists"""
        return [matrix.record for matrix in self.matrices]

    @layout.setter
    def layout(self, layout):
        """Translates the layout to a list of matrix objects"""
        self.matrices = [Matrix(char, styles, (column, row), units)
                         for (char, styles, column, row, units) in layout]

    @property
    def matrices(self):
        """Gets a list of Matrix objects"""
        return self.__dict__.get('_matrices')

    @matrices.setter
    def matrices(self, matrices):
        """Sets a list of Matrix objects, used for storing the layout"""
        if matrices:
            for matrix in matrices:
                matrix.diecase = self
                # Set the unit width for chars with 0 value; correct for
                # the wedge currently assigned to the diecase
                matrix.units = matrix.units or matrix.row_units(self.wedge)
            self.__dict__['_matrices'] = matrices

    def set_diecase_id(self, diecase_id=None):
        """Sets a diecase ID"""
        prompt = 'Diecase ID? (leave blank to exit) : '
        diecase_id = (diecase_id or UI.enter_data_or_blank(prompt) or
                      self.diecase_id)
        # Ask if we are sure we want to update this
        # if self.diecase_id was set earlier
        if not self.diecase_id or diecase_id != self.diecase_id:
            if UI.confirm('Are you sure to change diecase ID?'):
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
        return [(self.diecase_id, 'Diecase ID'),
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

    def manipulation_menu(self):
        """A menu with all operations on a diecase"""
        try:
            while True:
                UI.clear()
                UI.display_parameters({'Diecase data': self.parameters,
                                       'Wedge data': self.wedge.parameters})
                options = {'M': e.return_to_menu,
                           'T': self.set_typeface,
                           'W': self.assign_wedge,
                           'ID': self.set_diecase_id,
                           'E': self.edit_layout,
                           'N': self.generate_empty_layout,
                           'V': self.show_layout,
                           'I': self.import_layout,
                           'X': self.export_layout,
                           '': e.menu_level_up}
                messages = ['\nMatrix case manipulation:\n\n'
                            '[V]iew, [N]ew, [E]dit, [I]mport '
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

    def get_matrix(self, char='', style='roman'):
        """Chooses a matrix automatically"""
        candidates = [mat for mat in self.matrices
                      if char == mat.char and style in mat.styles]
        if not candidates:
            return super().get_matrix(char, style)
        elif len(candidates) == 1:
            return candidates[0]
        else:
            # Show a menu with multiple candidates
            hdr = (['Index'.ljust(10), 'Char'.ljust(10), 'Styles'.ljust(30),
                    'Column'.ljust(10), 'Row'.ljust(10), 'Units'.ljust(10)])
            mats = {i: mat for i, mat in enumerate(candidates, start=1)}
            prompt = 'Choose matrix (leave blank to enter manually): '
            choice = 0
            UI.display(''.join(hdr))
            for i, mat in mats.items():
                record = [str(i).ljust(10), mat.char.ljust(10),
                          ', '.join(mat.styles).ljust(30),
                          mat.column.ljust(10), str(mat.row).ljust(10),
                          str(mat.units).ljust(10)]
                UI.display(''.join(record))
            choice = UI.enter_data_or_blank(prompt, int)
            matrix = mats.get(choice, Matrix(char, (style)))
            matrix.diecase = self
            return matrix


class Matrix(object):
    """A class for single matrices - all matrix data"""
    def __init__(self, char='', styles=('roman'),
                 coordinates=('O', 15), units=None):
        self.char = char
        self.styles = styles
        (self.column, self.row) = coordinates
        self.diecase = None
        self.units = units

    def row_units(self, alt_wedge=None):
        """Gets the row's unit width value for the diecase's wedge"""
        wedge = alt_wedge or self.diecase.wedge
        return wedge.unit_arrangement[self.row]

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
    def parameters(self):
        """Gets all parameters for the matrix"""
        return [(self.char, 'Character'),
                (', '.join(list(self.styles)), 'Styles'),
                (self.code, 'Coordinates'), (self.units, 'Unit width')]

    @property
    def code(self):
        """Gets the matrix code"""
        return self.column + str(self.row)

    @property
    def units(self):
        """Gets the specific or default number of units"""
        units = self.__dict__.get('_units', None)
        return units or self.row_units()

    @units.setter
    def units(self, units):
        """Sets the unit width value"""
        self.__dict__['_units'] = units

    @property
    def record(self):
        """Returns a record suitable for JSON-dumping and storing in DB"""
        return [self.char, self.styles, self.column, self.row, self.units]

    @property
    def diecase(self):
        """Get a diecase or an empty one"""
        return self.__dict__.get('_diecase', Diecase())

    @diecase.setter
    def diecase(self, diecase):
        """Set a diecase"""
        if diecase is not None:
            self.__dict__['_diecase'] = diecase

    def wedge_positions(self, unit_correction=0, alt_wedge=None):
        """Calculates the 0075 and 0005 wedge positions for this matrix
        based on the diecase's default wedge or specified one."""
        wedge = alt_wedge or self.diecase.wedge
        diff = self.units + unit_correction - self.row_units(wedge)
        # 53 = neutral position where no corrections applied, i.e. 3/8
        # diff in units of given set; wedge pica = 0.166 or 0.1667
        steps_0005 = int(diff / wedge.pica * wedge.set_width * 0.25617) + 53
        # Upper limit: 15/15 => 15*15=225 + 15 = 240
        # (unsafe for casting from mats!)
        steps_0005 = min(steps_0005, 240)
        # Lower limit: 1/1 wedge positions => 15 + 1 = 16:
        steps_0005 = max(16, steps_0005)
        steps_0075 = 0
        while steps_0005 > 15:
            steps_0005 -= 15
            steps_0075 += 1
        # Got the wedge positions, return them
        return {'0075': steps_0075, '0005': steps_0005}

    def edit(self):
        """Edits the matrix data"""
        UI.edit_matrix(self)


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
