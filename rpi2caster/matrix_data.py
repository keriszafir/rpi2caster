# -*- coding: utf-8 -*-
"""Module containing functions for diecase retrieval and parsing,
diecase storing, parameter searches.
"""
# File operations
import io
import csv
from copy import copy
# Some functions raise custom exceptions
from . import exceptions as e
# Constants module
from . import constants as c
# Parsing module
from . import parsing as p
# Styles manager
from .styles import Styles
# Wedge operations for several matrix-case management functions
from .wedge_data import Wedge
# User interface
from .global_settings import UI, APPDIR
# Letter frequency for completeness testing
from .letter_frequencies import CharFreqs
# Database backend
from .database import Database
# Make or use existing database instance
DB = Database()


class Diecase(object):
    """Diecase: matrix case attributes and operations"""
    def __init__(self, diecase_id='', manual_choice=False):
        if manual_choice:
            data = choose_diecase()
        elif diecase_id:
            try:
                data = DB.get_diecase(diecase_id)
            except (e.NoMatchingData, e.DatabaseQueryError):
                data = choose_diecase()
        else:
            data = None
        if not data:
            # Use default diecase
            UI.debug_info('Using empty 15x17 diecase with S5-12E wedge...')
            data = ['', '', 'S5-12E', []]
        UI.debug_info('Processing diecase data...')
        (self.diecase_id, self.typeface, wedge_name, layout) = data
        self.wedge = Wedge(wedge_name, manual_choice=not wedge_name)
        self.alt_wedge = self.wedge
        self.layout = layout

    def __iter__(self):
        return iter(self.matrices)

    def __repr__(self):
        return self.diecase_id

    def __bool__(self):
        return bool(self.diecase_id)

    def __getitem__(self, item):
        try:
            char, styles = item
        except ValueError:
            char = item
            styles = ''
        return self.lookup_matrix(char, styles)

    @property
    def matrices(self):
        """Gets an iterator of mats"""
        matrices = self.__dict__.get('_matrices')
        if not matrices:
            layout = (self.__dict__.get('_layout') or
                      generate_empty_layout(15, 17))
            mats = [Matrix(char=char, styles=styles, code=code,
                           units=units, diecase=self)
                    for (char, styles, code, units) in layout]
            self.__dict__['_matrices'] = mats
        return (x for x in self.__dict__.get('_matrices'))

    @matrices.setter
    def matrices(self, matrices):
        """Sets a list of matrices"""
        self.__dict__['_matrices'] = [mat for mat in matrices]

    @property
    def ligatures(self):
        """Matrix character may be any string, not just a single character.
        This is used for ligatures, like ct, fb, fh, fi, fl, ffi, ffl, ij etc.
        Return an iterator of matrices where char attribute is not a single
        character. En-dashes and em-dashes will end up here also."""
        return (x for x in self.matrices if len(x.char) > 1)

    @property
    def ligature_length(self):
        """Get the maximum ligature length in chars"""
        return max(len(matrix) for matrix in self.matrices)

    @property
    def low_spaces(self):
        """Return an iterator of low spaces"""
        return (x for x in self.matrices if x.islowspace())

    @property
    def high_spaces(self):
        """Return an iterator of high spaces"""
        return (x for x in self.matrices if x.ishighspace())

    @property
    def spaces(self):
        """Return an iterator of all spaces, low and high"""
        return (x for x in self.matrices if x.isspace())

    @property
    def layout(self):
        """Gets a diecase layout as a list of lists"""
        return [matrix.get_record() for matrix in self.matrices]

    @layout.setter
    def layout(self, layout):
        """Translates the layout to a list of matrix objects"""
        if layout:
            self.matrices = []
            self.__dict__['_layout'] = layout

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
        all_styles = set(''.join([mat.styles for mat in self]))
        return Styles(all_styles)()

    def show_layout(self):
        """Shows the diecase layout"""
        UI.display_diecase_layout(self)
        UI.pause()

    def edit_layout(self):
        """Edits a layout and asks if user wants to save changes"""
        # Edit the layout
        UI.edit_diecase_layout(self)

    def lookup_matrix(self, char='', style=''):
        """Chooses a matrix automatically or manually (if multiple matches),
        allows to specify matrix data manually if no matches found"""
        def enter_manually(char='', style=''):
            """Specify matrix by entering code"""
            if char:
                st_string = str(Styles(style))
                if 'all' in st_string:
                    st_string = ''
                else:
                    st_string = st_string + ' '
                what = spaces.get(char) or '%s%s' % (st_string, char)
                UI.display('Choose matrix for %s' % what)
            else:
                char = ''
            code = UI.enter_data_or_default('Mat position?', 'G5').upper()
            matrix = Matrix(char=char, style=style, code=code, diecase=self)
            return matrix

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
            return enter_manually(char, style)
        elif len(candidates) == 1:
            return candidates[0]
        else:
            # Multiple matches found = let user choose
            st_string = str(Styles(style))
            if 'all' in st_string:
                st_string = ''
            else:
                st_string = ' ' + st_string
            what = spaces.get(char) or '%s%s' % (st_string, char)
            UI.display_header('Multiple matrices for %s' % what)
            # Show a menu with multiple candidates
            mats = {i: mat for i, mat in enumerate(candidates, start=1)}
            UI.display(''.join(['Index'.ljust(10), 'Char'.ljust(10),
                                'Styles'.ljust(30), 'Coordinates']))
            for i, mat in mats.items():
                matrix_styles = str(Styles(mat.styles))
                record = [str(i).ljust(10), mat.char.ljust(10),
                          matrix_styles.ljust(30), mat.code]
                UI.display(''.join(record))
            prompt = 'Choose matrix (leave blank to enter manually)'
            choice = UI.enter_data_or_blank(prompt, int)
            matrix = mats.get(choice) or enter_manually(char, style)
            return matrix

    def decode_matrix(self, code):
        """Finds the matrix based on the column and row in layout"""
        matrices = (mat for mat in self.matrices if mat.code == code.upper())
        try:
            mat = next(matrices)
        except StopIteration:
            mat = Matrix(code=code, diecase=self)
        if not mat.char:
            # Assume it's a space
            mat.char = ' '
        return mat

    def import_layout(self):
        """Imports a layout from file"""
        # Load the layout from file
        submitted_layout = [x for x in import_layout_file()]
        if not submitted_layout:
            UI.pause('File does not contain a proper layout!')
            return False
        # Update the empty layout with characters read from file
        # record = (char, styles, coordinates, units)
        try:
            self.layout = generate_empty_layout()
            for matrix in self.matrices:
                for record in submitted_layout:
                    (char, styles, coordinates, units) = record
                    if matrix.code.upper() == coordinates.upper():
                        matrix.char = char
                        matrix.styles = styles
                        matrix.units = units
        except (TypeError, ValueError):
            UI.pause('Cannot process the uploaded layout!')
            return False

    def export_layout(self):
        """Exports the matrix case layout to file."""
        name = self.diecase_id or 'NewDiecase'
        # Save the exported diecase layout in the default directory
        filename = APPDIR + '/%s.csv' % name
        with io.open(filename, 'a') as output_file:
            csv_writer = csv.writer(output_file, delimiter=';', quotechar='"',
                                    quoting=csv.QUOTE_ALL)
            csv_writer.writerow(['Char', 'Styles', 'Coordinates', 'Units'])
            for matrix in self.matrices:
                csv_writer.writerow(matrix.get_record())
        UI.pause('File %s successfully saved.' % filename)
        return True

    def test_characters(self, input_string='', styles='r'):
        """Enter the string and parse the diecase to see if any of the
        specified characters are missing."""
        input_string = input_string or UI.enter_data('Text to check?')
        charset = {char for char in input_string}
        # Return True unless any characters are missing
        retval = True
        for style, description in Styles(styles).items():
            chars_found = {mat.char for mat in self for char in charset
                           if char == mat.char and
                           (mat.isspace() or style in mat.styles)}
            missing = sorted(charset.difference(chars_found))
            if missing:
                UI.display('Missing mats for %s: %s'
                           % (description, ', '.join(missing)))
                retval = False
            else:
                UI.display('All characters for %s are present.' % description)
        return retval

    def _test_lang_completeness(self):
        """Choose a language and test whether the diecase contains all
        characters, and if not, list them"""
        char_backend = CharFreqs()
        UI.display('Building character set...')
        uppercase = [char.upper() for char in char_backend]
        lowercase = [char.lower() for char in char_backend]
        all_chars = ''.join(list(sorted(set(uppercase + lowercase))))
        UI.display('\nCharacters: %s\n' % all_chars)
        styles = Styles(self.styles, manual_choice=True)()
        self.test_characters(all_chars, styles)
        UI.pause()

    def _set_diecase_id(self, diecase_id=None):
        """Sets a diecase ID"""
        prompt = 'Diecase ID? (leave blank to exit)'
        diecase_id = (diecase_id or UI.enter_data_or_blank(prompt) or
                      self.diecase_id)
        # Ask if we are sure we want to update this
        # if self.diecase_id was set earlier
        if not self.diecase_id or UI.confirm('Apply changes?', default=False):
            self.diecase_id = diecase_id
            return True

    def _set_typeface(self, typeface=None):
        """Sets the type series, size and typeface name"""
        prompt = 'Typeface (series, size, name)?'
        typeface = typeface or UI.enter_data_or_blank(prompt) or self.typeface
        if not self.typeface or UI.confirm('Apply changes?', default=False):
            self.typeface = typeface
            return True

    def _assign_wedge(self, wedge=''):
        """Assigns a wedge (from database or newly-defined) to the diecase"""
        self.wedge = Wedge(wedge, manual_choice=not wedge)

    def _save_to_db(self):
        """Stores the matrix case definition/layout in database"""
        try:
            DB.add_diecase(self)
            UI.pause('Data saved successfully.')
            return True
        except e.DatabaseQueryError:
            UI.pause('Cannot save the diecase!')

    def _delete_from_db(self):
        """Deletes a diecase from database"""
        ans = UI.confirm('Are you sure?', default=False)
        if ans and DB.delete_diecase(self):
            UI.display('Matrix case deleted successfully.')
            return True

    def _check_db(self):
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
            self.layout = generate_empty_layout()
        try:
            while True:
                UI.clear()
                UI.display_parameters({'Diecase data': self.parameters,
                                       'Wedge data': self.wedge.parameters})
                options = {'Q': e.return_to_menu,
                           'T': self._set_typeface,
                           'A': self._test_lang_completeness,
                           'W': self._assign_wedge,
                           'ID': self._set_diecase_id,
                           'E': self.edit_layout,
                           'N': clear_layout,
                           'V': self.show_layout,
                           'I': self.import_layout,
                           'X': self.export_layout,
                           'C': e.menu_level_up}
                messages = ['Matrix case manipulation:\n\n'
                            '[V]iew layout,\n'
                            '[E]dit layout,\n'
                            '[I]mport layout from file\n'
                            'e[X]port layout to file,\n'
                            'assign [W]edge,\n'
                            'change [T]ypeface\n'
                            'set diecase [ID]\n'
                            'check if [A]ll characters for chosen language '
                            'are in diecase,\n'
                            '[N]ew layout from scratch\n']
                # Save to database needs a complete set of metadata
                required = {'Typeface': self.typeface,
                            'Diecase ID': self.diecase_id}
                missing = [item for item in required if not required[item]]
                messages.extend(['Cannot save diecase with missing %s\n'
                                 % item.lower() for item in missing])
                if not missing:
                    options['S'] = self._save_to_db
                    messages.append('[S]ave diecase to database,\n')
                # Check if it's in the database
                if self._check_db():
                    options['D'] = self._delete_from_db
                    messages.append('[D]elete diecase from database,\n')
                # Options constructed
                messages.append('[C] to choose/create another diecase,\n'
                                '[Q] to quit.\n')
                messages.append('Your choice: ')
                message = ''.join(messages)
                UI.simple_menu(message, options)()
        except e.MenuLevelUp:
            # Exit matrix case manipulation menu
            return True


class Matrix(object):
    """A class for single matrices - all matrix data"""
    def __init__(self, **kwargs):
        self.diecase = kwargs.get('diecase', EMPTY_DIECASE)
        self.char = kwargs.get('char', '')
        self.styles = kwargs.get('styles', 'r')
        self.code = kwargs.get('code', 'O15')
        self.units = kwargs.get('units') or 0

    def __repr__(self):
        return self.code

    def __str__(self):
        if self.points != self.get_row_points():
            s_signal = 'S'
        else:
            s_signal = ''
        comment = (self.islowspace() and
                   ' // low space %.2f points wide' % self.points or
                   self.ishighspace() and
                   ' // high space %.2f points wide' % self.points or
                   self.char and
                   ' // %s %s' % (Styles(self.styles), self.char) or '')
        return '%s%s%s%s' % (self.column, s_signal, self.row, comment)

    def __call__(self, points):
        """Returns a copy of self with a corrected width"""
        new_mat = copy(self)
        new_mat.points += points
        return new_mat

    def __len__(self):
        return len(self.char)

    def __bool__(self):
        return True

    @property
    def styles(self):
        """Get the matrix's styles or an empty string if matrix has no char"""
        if not self.char or self.isspace():
            return ''
        else:
            return self.__dict__.get('_styles', 'r')

    @styles.setter
    def styles(self, styles):
        """Sets the matrix's style string"""
        self.__dict__['_styles'] = styles

    @property
    def units(self):
        """Gets the specific or default number of units"""
        # If units are assigned to the matrix, return the value
        # Otherwise, wedge default
        units = (self.__dict__.get('_units', 0) or
                 self.diecase.wedge.units[self.row])
        return units

    @units.setter
    def units(self, units):
        """Sets the unit width value"""
        if units:
            self.__dict__['_units'] = units

    @property
    def points(self):
        """Gets a DTP point (=.1667"/12) width for the matrix"""
        points = (self.__dict__.get('_points') or
                  self.diecase.wedge.units_to_points_factor * self.units)
        return round(points, 2)

    @points.setter
    def points(self, points):
        """Sets a DTP point value for the mat and updates the unit value"""
        # Set constraints on width
        lim_points = min(points, self.get_max_points())
        lim_points = max(lim_points, self.get_min_points())
        self.__dict__['_points'] = lim_points

    @property
    def row(self):
        """Gets the row number"""
        return self.__dict__.get('_row', 15)

    @row.setter
    def row(self, value):
        """Sets the row number"""
        value = int(value)
        if value in range(1, 17):
            self.__dict__['_row'] = value

    @property
    def column(self):
        """Gets the matrix column"""
        return self.__dict__.get('_column', 'O')

    @column.setter
    def column(self, value):
        """Sets the column"""
        column = value.upper()
        if column in c.COLUMNS_17:
            self.__dict__['_column'] = column
        else:
            self.__dict__['_column'] = 'O'

    @property
    def code(self):
        """Gets the matrix code"""
        return '%s%s' % (self.column, self.row)

    @code.setter
    def code(self, code_string):
        """Sets the coordinates for the matrix"""
        signals = p.parse_signals(code_string)
        self.row = p.get_row(signals)
        self.column = p.get_column(signals)

    def get_row_points(self):
        """Gets a number of points for characters in the diecase row"""
        # Try wedges in order:
        # diecase's temporary wedge, diecase's default wedge, standard S5-12E
        return self.diecase.alt_wedge.points[self.row]

    def get_min_points(self):
        """Gets the minimum unit value for a given wedge, based on the
        matrix row and wedge unit value, for wedges at 1/1"""
        # 3/8 - 1/1 = 2/7 so 2*15 + 7 = 37
        # 37 * 0.0005 = 0.0185 i.e. max inches we can take away
        return round(max(self.get_row_points() - 0.0185 * 72, 0), 2)

    def get_max_points(self):
        """Gets the minimum unit value for a given wedge, based on the
        matrix row and wedge unit value, for wedges at 1/1"""
        # 15/15 - 3/8 = 12/7 so 12*15 + 7 = 187
        # 187 * 0.0005 = 0.0935 i.e. max inches we can add
        # Matrix is typically .2 x .2 - anything wider will lead to a splash!
        # Safe limit is .19" = 13.680" and we don't let the mould open further
        full_width = round(self.get_row_points() + 0.0935 * 72, 2)
        width_cap = 13.680
        if self.islowspace():
            return full_width
        else:
            return min(full_width, width_cap)

    def wedge_positions(self, point_correction=0):
        """Calculate the 0075 and 0005 wedge positions for this matrix
        based on the current wedge used"""
        diff = self.points + point_correction - self.get_row_points()
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

    def get_record(self):
        """Returns a record suitable for JSON-dumping and storing in DB"""
        return [self.char, self.styles, self.code, self.units]

    def isspace(self):
        """Check whether the mat is space or not"""
        return self.islowspace() or self.ishighspace()

    def islowspace(self):
        """Check whether the mat is low space"""
        return self.char == ' '

    def ishighspace(self):
        """Check whether the mat is high space"""
        return self.char == '_'

    def edit(self):
        """Edits the matrix data"""
        char = self.char and 'char: "%s"' % self.char or 'character not set'
        styles = self.styles and 'styles: %s' % self.styles or ''
        UI.display('\n' + '*' * 80 + '\n')
        UI.display('%s %s %s, units: %s'
                   % (self.code, styles, char, self.units))
        self.edit_char()
        self.choose_styles()
        self.specify_units()
        return self

    def edit_char(self):
        """Edit the matrix character"""
        prompt = ('Char? (" ": low / "_": high space, '
                  'blank = keep, ctrl-C to exit)?')
        if self.char:
            self.char = UI.enter_data_or_default(prompt, self.char)
        else:
            self.char = UI.enter_data_or_blank(prompt)

    def specify_units(self):
        """Give a user-defined unit value for the matrix;
        mostly used for matrices placed in a different row than the
        unit arrangement indicates; this will make the program set the
        justification wedges and cast the character with the S-needle"""
        UI.display('Enter unit value for %s; 0 = row units, '
                   'blank = current' % self.code)
        prompt = 'Units?'
        self.units = UI.enter_data_or_default(prompt, self.units, int)

    def choose_styles(self):
        """Choose styles for the matrix"""
        style_manager = Styles(self.styles)
        style_manager.choose()
        self.styles = style_manager()


def diecase_operations():
    """Matrix case operations menu for inventory management"""
    try:
        UI.display_header('Matrix case manipulation')
        while True:
            # Choose a diecase or initialize a new one
            Diecase(manual_choice=True).manipulation_menu()
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
    prompt = 'Number of a diecase (0 for a new one, leave blank to exit)'
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
    The format should be: "character";"styles";"coordinates";"unit_width"."""
    # Give us a file or end here
    try:
        filename = UI.enter_input_filename()
    except e.ReturnToMenu:
        return False
    # Initialize the records list
    raw_records = []
    # This will store the processed combinations - and whenever a duplicate
    # is detected, the function will raise an exception
    with io.open(filename, 'r') as layout_file:
        input_data = csv.reader(layout_file, delimiter=';', quotechar='"')
        raw_records = [record for record in input_data]
        displayed_lines = [' '.join(record) for record in raw_records[:5]]
        # Preview file
        UI.display('File preview: displaying first 5 rows:\n')
        UI.display('\n'.join(displayed_lines), end='\n\n')
        # Ask if the first row is a header - if so, away with it
        if UI.confirm('Is the 1st row a table header? ', default=True):
            raw_records.pop(0)
    if not UI.confirm('Proceed?', default=True):
        return False
    try:
        # Assume we have a 15x15 diecase (if it turns out larger - override)
        columns = c.COLUMNS_15
        rows = range(1, 16)
        records = []
        for record in raw_records:
            # Must work also if we don't specify the units
            try:
                (char, styles, coordinates, units) = record
                units = int(units.strip())
            except (ValueError, AttributeError):
                (char, styles, coordinates) = record[:3]
                units = 0
            # Strip unneeded whitespace from character
            if char.isspace():
                char = ' '
            else:
                char = char.strip()
            # Parse styles and order them
            styles = Styles(styles)()
            # Determine the diecase size, override previous size if larger
            if '16' in coordinates:
                columns = c.COLUMNS_17
                rows = range(1, 17)
            elif 'NI' in coordinates or 'NL' in coordinates:
                columns = c.COLUMNS_17
            records.append((char, styles, coordinates, units))
        # Arrange the uploaded list into a layout
        layout = (record for row in rows for col in columns
                  for record in records if record[2] == '%s%s' % (col, row))
        # Show the uploaded layout
        return layout
    except (KeyError, ValueError, IndexError):
        return []


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
    return (('', '', '%s%s' % (column, row), 0)
            for row in rows_list for column in columns_list)


# Make a single instance of empty diecase for getting fallback values
EMPTY_DIECASE = Diecase()
