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
# Letter frequency for completeness testing
from . import letter_frequencies as lf
# Make or use existing database instance
DB = database.Database()


class Diecase(object):
    """Diecase: matrix case attributes and operations"""
    def __init__(self):
        self.diecase_id = ''
        self.typeface = ''
        self.wedge = wedge_data.Wedge()
        self.matrices = generate_empty_layout(15, 17)

    def __iter__(self):
        return iter(self.matrices)

    def __next__(self):
        yield from self.matrices

    def __repr__(self):
        return self.diecase_id

    def __bool__(self):
        return bool(self.diecase_id)

    def __getitem__(self, char_and_style):
        try:
            char, style = char_and_style
            return self.lookup_matrix(char, style)
        except ValueError:
            # Must work if we give it a character only
            return self.lookup_matrix(char_and_style)

    def show_layout(self):
        """Shows the diecase layout"""
        UI.display_diecase_layout(self)
        UI.pause()

    def edit_layout(self):
        """Edits a layout and asks if user wants to save changes"""
        # Edit the layout
        UI.edit_diecase_layout(self)

    def lookup_matrix(self, char='', style=''):
        """Enter coordinates and unit value"""
        if char:
            UI.display('Enter matrix data for character: %s' % char)
        codes = UI.enter_data_or_default('Combination?', 'G5').upper()
        codes = p.parse_signals(codes)
        # Got a list of signals
        row = p.get_row(codes)
        column = p.get_column(codes)
        matrix = Matrix(char or '', [style], (column, row))
        matrix.diecase = self
        matrix.units = self.wedge[matrix.row]
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
            self.matrices = generate_empty_layout()
            for matrix in self.matrices:
                for (char, styles, column, row, units) in submitted_layout:
                    if matrix.column == column and matrix.row == row:
                        matrix.char = char
                        matrix.styles = styles
                        matrix.units = units
        except (TypeError, ValueError):
            UI.pause('Cannot process the uploaded layout!')
            return False

    def export_layout(self):
        """Exports the matrix case layout to file."""
        filename = os.path.expanduser('~') + '/%s.csv' % self
        with io.open(filename, 'a') as output_file:
            csv_writer = csv.writer(output_file, delimiter=';', quotechar='"',
                                    quoting=csv.QUOTE_ALL)
            csv_writer.writerow(['Character', 'Style(s)', 'Column', 'Row',
                                 'Unit width'])
            for matrix in self.matrices:
                (char, styles, column, row, units) = matrix.record
                csv_writer.writerow([char, ', '.join(list(styles)),
                                     column, row, units])
        UI.pause('File %s successfully saved.' % filename)
        return True

    def check_missing_characters(self, input_string='', style='roman'):
        """Enter the string and parse the diecase to see if any of the
        specified characters are missing."""
        input_string = input_string or UI.enter_data('Text to check?')
        charset = {char for char in input_string}
        chars_found = {mat.char for mat in self for char in charset
                       if char == mat.char and
                       (char in ' _' or style in mat.styles)}
        missing = sorted(charset.difference(chars_found))
        if missing:
            UI.display('Missing mats for %s: %s' % (style, ', '.join(missing)))
        else:
            UI.display('All characters for %s are present.' % style)

    def test_completeness(self):
        """Choose a language and test whether the diecase contains all
        characters, and if not, list them"""
        charset = [x for x in lf.CharFreqs()]
        uppercase = [char.upper() for char in charset]
        lowercase = [char.lower() for char in charset]
        all_chars = ''.join(list(sorted(set(uppercase + lowercase))))
        UI.display('\nCharacters: %s\n' % all_chars)
        styles = UI.choose_styles()
        for style in styles:
            self.check_missing_characters(all_chars, style)
        UI.pause()

    def set_diecase_id(self, diecase_id=None):
        """Sets a diecase ID"""
        prompt = 'Diecase ID? (leave blank to exit)'
        diecase_id = (diecase_id or UI.enter_data_or_blank(prompt) or
                      self.diecase_id)
        # Ask if we are sure we want to update this
        # if self.diecase_id was set earlier
        if not self.diecase_id or UI.confirm('Apply changes?', default=False):
            self.diecase_id = diecase_id
            return True

    def set_typeface(self, typeface=None):
        """Sets the type series, size and typeface name"""
        prompt = 'Typeface (series, size, name)?'
        typeface = typeface or UI.enter_data_or_blank(prompt) or self.typeface
        if not self.typeface or UI.confirm('Apply changes?', default=False):
            self.typeface = typeface
            return True

    def assign_wedge(self, wedge_name=None):
        """Assigns a wedge (from database or newly-defined) to the diecase"""
        self.wedge = wedge_data.SelectWedge(wedge_name)

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
        ans = UI.confirm('Are you sure?', default=False)
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

    def manipulation_menu(self):
        """A menu with all operations on a diecase"""
        def clear_layout():
            """Generates a new layout for the diecase"""
            self.matrices = generate_empty_layout()
        try:
            while True:
                UI.clear()
                UI.display_parameters({'Diecase data': self.parameters,
                                       'Wedge data': self.wedge.parameters})
                options = {'M': e.return_to_menu,
                           'T': self.set_typeface,
                           'A': self.test_completeness,
                           'W': self.assign_wedge,
                           'ID': self.set_diecase_id,
                           'E': self.edit_layout,
                           'N': clear_layout,
                           'V': self.show_layout,
                           'I': self.import_layout,
                           'X': self.export_layout,
                           'C': e.menu_level_up}
                messages = ['\nMatrix case manipulation:\n\n'
                            '[V]iew, [N]ew, [E]dit, [I]mport '
                            'or e[X]port layout\nAssign [W]edge, '
                            'change [T]ypeface or diecase [ID]\n'
                            '[A] - check if all characters are in diecase\n\n']
                # Save to database needs a complete set of metadata
                required = {'Typeface': self.typeface,
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
                messages.append('\n[C] to choose/create another diecase, '
                                '[M] to exit to menu.')
                messages.append('\nYour choice: ')
                message = ''.join(messages)
                UI.simple_menu(message, options)()
        except e.MenuLevelUp:
            # Exit matrix case manipulation menu
            return True

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
            self.__dict__['_matrices'] = matrices

    @property
    def alternative_wedge(self):
        """Get values for temporary, alternative wedge assigned at
        typesetting or casting time, for re-calculating matrix unit widths."""
        return self.__dict__.get('_alt_wedge', self.wedge)

    @alternative_wedge.setter
    def alternative_wedge(self, alt_wedge):
        """Set the alternative wedge"""
        self.__dict__['_alt_wedge'] = alt_wedge

    @property
    def parameters(self):
        """Gets a list of parameters"""
        return [(self.diecase_id, 'Diecase ID'),
                (self.typeface, 'Typeface'),
                (self.wedge, 'Assigned wedge')]

    @property
    def styles(self):
        """Parses the diecase layout and gets available typeface styles.
        Returns a list of them."""
        return list({style for mat in self for style in mat.styles if style})


class SelectDiecase(Diecase):
    """Initialize a diecase object with or without given ID.
    If possible, choose automatically. If this fails, choose manually,
    and if user chooses no diecase, an empty one will be initialized."""
    def __init__(self, diecase_id=None):
        super().__init__()
        # Diecases created with diecase_id will be set up automatically
        try:
            mcd = diecase_id and DB.get_diecase(diecase_id) or choose_diecase()
            (self.diecase_id, self.typeface, wedge_name, self.layout) = mcd
            # Assign the correct wedge
            self.wedge = wedge_data.SelectWedge(wedge_name)
        except (KeyError, TypeError, e.NoMatchingData, e.DatabaseQueryError):
            UI.display('Diecase choice failed. Using empty one instead.')

    def lookup_matrix(self, char='', style=''):
        """Chooses a matrix automatically or manually (if multiple matches),
        allows to specify matrix data manually if no matches found"""
        spaces = {' ': 'low space', '_': 'high space'}
        if char in spaces:
            style = ''
        # Find as many matches as we can:
        # -all matrices for a given character for a given style
        # -all matrices for a given style if char not specified
        # -all matrices for a given character if style not specified
        # -all matrices for spaces
        # -enter manually if no character and no style is specified
        # Then choose from menu (if multiple match), automatically
        # (single match) or enter manually (no matches)
        if char and style:
            candidates = [mat for mat in self.matrices
                          if mat.char == char and style in mat.styles]
        elif char:
            candidates = [mat for mat in self.matrices if mat.char == char]
        elif style:
            candidates = [mat for mat in self.matrices
                          if style in mat.styles or not self.styles]
        else:
            candidates = []
        # Built the list of candidates...
        if not candidates:
            return super().lookup_matrix(char, style)
        elif len(candidates) == 1:
            return candidates[0]
        else:
            # Multiple matches found = let user choose
            pr_char = spaces.get(char, char)
            UI.display_header('Multiple matrices for %s %s' % (style, pr_char))
            # Show a menu with multiple candidates
            mats = {i: mat for i, mat in enumerate(candidates, start=1)}
            UI.display(''.join(['Index'.ljust(10), 'Char'.ljust(10),
                                'Styles'.ljust(30), 'Column'.ljust(10),
                                'Row'.ljust(10)]))
            for i, mat in mats.items():
                record = [str(i).ljust(10), mat.char.ljust(10),
                          ', '.join(mat.styles).ljust(30),
                          mat.column.ljust(10), str(mat.row).ljust(10)]
                UI.display(''.join(record))
            prompt = 'Choose matrix (leave blank to enter manually)'
            choice = UI.enter_data_or_blank(prompt, int)
            matrix = (mats.get(choice, None) or
                      super().lookup_matrix(char, style))
            matrix.diecase = self
            return matrix


class Matrix(object):
    """A class for single matrices - all matrix data"""
    def __init__(self, char='', styles=('roman',),
                 coordinates=('O', 15), units=None):
        self.char = char
        self.styles = styles
        # Spaces (low and high) have every style
        if char in ' _':
            styles = []
        (self.column, self.row) = coordinates
        self.diecase = None
        self.units = units

    def __repr__(self):
        return self.code

    @property
    def row_units(self):
        """Gets the row's unit width value for the wedge assigned
        to the diecase."""
        return self.diecase.wedge[self.row]

    @property
    def units(self):
        """Gets the specific or default number of units"""
        return self.__dict__.get('_units', self.row_units)

    @units.setter
    def units(self, units):
        """Sets the unit width value"""
        if units:
            self.__dict__['_units'] = units

    @property
    def points(self):
        """Gets a DTP point (=.1667"/12) width for the matrix"""
        wedge = self.diecase.wedge
        points = self.units * wedge.set_width * wedge.pica / 18 / 0.1667
        return round(points, 2)

    @points.setter
    def points(self, points):
        """Sets a DTP point value for the mat and updates the unit value"""
        wedge = self.diecase.wedge
        self.units = 18 * 0.1667 * points / wedge.set_width / wedge.pica

    @property
    def row_points(self):
        """Gets a number of points for characters in the diecase row"""
        return self.diecase.alternative_wedge.points[self.row]

    @property
    def min_points(self):
        """Gets the minimum unit value for a given wedge, based on the
        matrix row and wedge unit value, for wedges at 1/1"""
        # 3/8 - 1/1 = 2/7 so 2*15 + 7 = 37
        # 37 * 0.0005 = 0.0185 i.e. max inches we can take away
        return round(max(self.row_points - 0.0185 * 72, 0), 2)

    @property
    def max_points(self):
        """Gets the minimum unit value for a given wedge, based on the
        matrix row and wedge unit value, for wedges at 1/1"""
        # 15/15 - 3/8 = 12/7 so 12*15 + 7 = 187
        # 187 * 0.0005 = 0.0935 i.e. max inches we can add
        # Matrix is typically .2 x .2 - anything wider will lead to a splash!
        # Safe limit is .19" and we don't let the mould open further
        return round(min(self.row_points + 0.0935 * 72, 0.19 * 72), 2)

    @property
    def row(self):
        """Gets the row number"""
        return self.__dict__.get('_row', 5)

    @row.setter
    def row(self, value):
        """Sets the row number"""
        value = int(value)
        value = max(1, value)
        value = min(value, 16)
        self.__dict__['_row'] = value

    @property
    def parameters(self):
        """Gets all parameters for the matrix"""
        return [(self.char, 'Character'),
                (', '.join(list(self.styles)), 'Styles'),
                (self, 'Coordinates'), (self.units, 'Unit width')]

    @property
    def code(self):
        """Gets the matrix code"""
        return self.column + str(self.row)

    @property
    def record(self):
        """Returns a record suitable for JSON-dumping and storing in DB"""
        return [self.char, self.styles, self.column, self.row, self.units]

    @property
    def diecase(self):
        """Get a diecase the matrix belongs to, or an empty one"""
        return self.__dict__.get('_diecase', Diecase())

    @diecase.setter
    def diecase(self, diecase):
        """Assign a diecase to the matrix (done on instantiation of Matrix,
        required for accessing wedge for calculations)"""
        if diecase is not None:
            self.__dict__['_diecase'] = diecase

    def isspace(self):
        """Check whether the mat is space or not"""
        return self.islowspace() or self.ishighspace()

    def islowspace(self):
        """Check whether the mat is low space"""
        return self.char == ' '

    def ishighspace(self):
        """Check whether the mat is high space"""
        return self.char == '_'

    def isempty(self):
        """Check whether the mat is empty"""
        return not self.char

    def edit(self):
        """Edit the matrix data - this depends on the user interface"""
        UI.edit_matrix(self)

    def specify_units(self):
        """Give a user-defined unit value for the matrix;
        mostly used for matrices placed in a different row than the
        unit arrangement indicates; this will make the program set the
        justification wedges and cast the character with the S-needle"""
        prompt = 'Unit value for the matrix?'
        self.units = UI.enter_data_or_default(prompt, self.row_units, int)

    def wedge_positions(self, point_correction=0):
        """Calculate the 0075 and 0005 wedge positions for this matrix
        based on the current wedge used"""
        diff = self.points + point_correction - self.row_points
        # The following calculations are done in 0005 wedge steps
        # 1 step of 0075 wedge is 15 steps of 0005; neutral positions are 3/8
        # 3 * 15 + 8 = 53, so any increment/decrement is relative to this
        # Add or take away a number of inches; diff is in points i.e. 1/72"
        steps_0005 = int(diff * 2000 / 72) + 53
        # Upper limit: 15/15 => 15*15=225 + 15 = 240
        # Unsafe for casting from mats - .2x.2 size - larger leads to splash!
        # Adding a high space for overhanging character is the way to do it
        # Space casting is fine, we can open the mould as far as possible
        steps_0005 = min(steps_0005, 240)
        # Lower limit: 1/1 wedge positions => 15 + 1 = 16:
        steps_0005 = max(16, steps_0005)
        steps_0075 = 0
        while steps_0005 > 15:
            steps_0005 -= 15
            steps_0075 += 1
        # Got the wedge positions, return them
        return (steps_0075, steps_0005)


def diecase_operations():
    """Matrix case operations menu for inventory management"""
    try:
        UI.display_header('Matrix case manipulation')
        while True:
            # Choose a diecase or initialize a new one
            SelectDiecase().manipulation_menu()
    except e.ReturnToMenu:
        # Exit diecase operations
        return True


def list_diecases():
    """Lists all matrix cases we have."""
    data = DB.get_all_diecases()
    results = {}
    UI.display('\n' +
               'No.'.ljust(4) +
               'Diecase ID'.ljust(25) +
               'Wedge'.ljust(12) +
               'Typeface' +
               '\n\n0 - start a new empty diecase\n')
    for index, diecase in enumerate(data, start=1):
        # Start each row with index
        row = [str(index).ljust(4)]
        # Collect the ciecase parameters: ID, typeface, wedge
        # Leave the diecase layout out
        row.append(diecase[0].ljust(25))
        # Swap the wedge and typeface designations (more place for long names)
        row.append(diecase[2].ljust(12))
        row.append(diecase[1])
        # Add number and ID to the result that will be returned
        results[index] = diecase[0]
        UI.display(''.join(row))
    UI.display('\n\n')
    # Now we can return the number - diecase ID pairs
    return results


def choose_diecase():
    """Lists diecases and lets the user choose one;
    returns the Diecase class object with all parameters set up."""
    prompt = 'Number of a diecase (0 for a new one, leave blank to exit): '
    while True:
        try:
            UI.display('Choose a matrix case:', end='\n\n')
            data = list_diecases()
            choice = UI.enter_data_or_exception(prompt, e.ReturnToMenu, int)
            if not choice:
                return None
            else:
                return DB.get_diecase(data[choice])
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
    try:
        filename = UI.enter_input_filename()
    except e.ReturnToMenu:
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
        if UI.confirm('Is the 1st row a table header? ', default=True):
            all_records.pop(0)
    if not UI.confirm('Proceed?', default=True):
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


def generate_empty_layout(rows=None, columns=None):
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
    return [Matrix(coordinates=(column, row), units=0)
            for row in rows_list for column in columns_list]
