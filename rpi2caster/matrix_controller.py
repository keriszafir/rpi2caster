#!/usr/bin/env python3
"""Diecase manipulation functions"""

import csv
from contextlib import suppress
from collections import OrderedDict
from itertools import zip_longest
from sqlalchemy.orm import exc as orm_exc
from . import exceptions as e
from . import constants as c
from . import wedge_unit_values as wu
from . import unit_arrangements as ua
from .styles import Roman, Bold, Italic, SmallCaps, Inferior, Superior
from .models import Database, Diecase, Matrix, Wedge
from .ui import UIFactory, Abort
from .letter_frequencies import CharFreqs
from .defaults import USER_DATA_DIR

UI = UIFactory()
DB = Database()


def import_csv(diecase, filename=''):
    """Imports a layout from file"""
    def preview(num=5):
        """Preview the first five records in the file"""
        with layout_file:
            records = csv.reader(layout_file, line_num=num,
                                 delimiter=';', quotechar='"')
            text = '\n'.join(''.join(str(field).ljust(15) for field in rec)
                             for rec in records)
            UI.display('File preview: displaying first %s rows:\n' % num)
            UI.display(text)

    # Load the layout from file
    try:
        layout_file = UI.import_file(filename)
        preview()
        with layout_file:
            csv_reader = csv.reader(layout_file, delimiter=';', quotechar='"')
            layout_gen = (record for record in csv_reader)
        if UI.confirm('Is the 1st row a table header? ', default=True):
            next(layout_gen)
        if not UI.confirm('Proceed?', default=True):
            raise Abort
        # parse the layout
        diecase.load_layout(rec for rec in layout_gen)
    except Abort:
        UI.display('Aborted.')
    except (TypeError, ValueError):
        UI.pause('Incorrect layout. Check your file.')


def export_csv(diecase, filename=''):
    """Exports the matrix case layout to file."""
    name = diecase.diecase_id or 'NewDiecase'
    # Save the exported diecase layout in the default directory
    file_name = filename or '%s/%s.csv' % (USER_DATA_DIR, name)
    with suppress(Abort):
        output_file = UI.export_file(file_name)
        with output_file:
            csv_writer = csv.writer(output_file, delimiter=';',
                                    quotechar='"', quoting=csv.QUOTE_ALL)
            csv_writer.writerow(['Char', 'Styles', 'Position', 'Units'])
            # store mats with no position info as well
            csv_writer.writerows(diecase.layout.raw)
        UI.pause('File %s successfully saved.' % filename)


def clear_layout(diecase):
    """Generates a new layout for the diecase"""
    if UI.confirm('Are you sure?'):
        diecase.layout.reset()
        diecase.store_layout()


def test_characters(diecase, input_iter='', styles=None):
    """Enter the string and parse the diecase to see if any of the
    specified characters are missing."""
    styles = styles or diecase.styles
    input_collection = input_iter or UI.enter('Text to check?')
    test_char_set = set(input_collection)
    # Return True unless any characters are missing
    retval = True
    for style in styles:
        chars_found = {mat.char for mat in diecase for char in test_char_set
                       if char == mat.char and
                       (mat.is_space or style in mat.styles)}
        missing = sorted(test_char_set.difference(chars_found))
        if missing:
            UI.display('Missing mats for %s: %s'
                       % (style.name, ', '.join(missing)))
            retval = False
        else:
            UI.display('All characters for %s are present.' % style.name)
    return retval


def test_lang_completeness(diecase):
    """Choose a language and test whether the diecase contains all
    characters, and if not, list them"""
    char_backend = CharFreqs()
    UI.display('Building character set...')
    uppercase = [str(char).upper() for char in char_backend]
    lowercase = [str(char).lower() for char in char_backend]
    all_chars = sorted(set(uppercase + lowercase))
    UI.display('\nCharacters: %s\n' % ''.join(all_chars))
    styles = diecase.styles
    styles.choose()
    test_characters(diecase, all_chars, styles)
    UI.pause()


def change_parameters(diecase):
    """Change parameters: diecase ID, typeface"""
    prompt = 'Diecase ID? '
    diecase_id = UI.enter(prompt, default=diecase.diecase_id)
    prompt = 'Typeface? (e.g. series, size, name) '
    typeface = UI.enter(prompt, default=diecase.typeface)
    changed = diecase_id != diecase.diecase_id or typeface != diecase.typeface
    if changed and UI.confirm('Apply changes?'):
        diecase.typeface = typeface
        diecase.diecase_id = diecase_id


def assign_unit_arrangements(diecase):
    """Sets the unit arrangements for diecase's styles"""
    unit_arrangements = ua.ua_by_style(diecase.styles,
                                       diecase.unit_arrangements)
    if UI.confirm('Display character unit values?', False):
        ua.display_unit_values(diecase.unit_arrangements)
        UI.pause()
    prompt = 'Apply changes?'
    if unit_arrangements != diecase.unit_arrangements and UI.confirm(prompt):
        diecase.unit_arrangements = unit_arrangements


def assign_wedge(diecase):
    """Assigns a wedge (from database or newly-defined) to the diecase"""
    diecase.wedge = choose_wedge(diecase.wedge.name)


def save_to_db(diecase):
    """Stores the matrix case definition/layout in database"""
    DB.session.add(diecase)
    DB.session.commit()
    UI.pause('Data saved successfully.')


def delete_from_db(diecase):
    """Deletes a diecase from database"""
    ans = UI.confirm('Are you sure?', default=False)
    if ans:
        DB.session.delete(diecase)
        DB.session.commit()
        UI.display('Matrix case deleted successfully.')
        return True


def get_all_diecases():
    """Lists all matrix cases we have."""
    diecases = OrderedDict(enumerate(DB.query(Diecase).all(), start=1))
    return diecases


def list_diecases(data=get_all_diecases()):
    """Display all diecases in a dictionary, plus an empty new one"""
    UI.display('\nAvailable diecases:\n\n' +
               'No.'.ljust(4) +
               'Diecase ID'.ljust(25) +
               'Wedge name'.ljust(12) +
               'Typeface')
    for index, diecase in data.items():
        row = ''.join([str(index).ljust(4),
                       diecase.diecase_id.ljust(25),
                       diecase.wedge.name.ljust(12),
                       diecase.typeface])
        UI.display(row)


def choose_diecase(fallback=Diecase, fallback_description='new empty diecase'):
    """Select diecases from database and let the user choose one of them.
    If no diecases are found, return None and let the calling logic
    determine what fallback to use."""
    prompt = 'Number? (0: %s, leave blank to exit)' % fallback_description
    while True:
        try:
            data = get_all_diecases()
            if not data:
                return fallback()
            else:
                UI.display('Choose a matrix case:', end='\n\n')
                list_diecases(data)
                choice = UI.enter(prompt, exception=Abort, datatype=int)
                data[0] = None
                return data[choice] or fallback()
        except KeyError:
            UI.pause('Diecase number is incorrect!')


def get_diecase(diecase_id=None, fallback=choose_diecase):
    """Get a diecase with given parameters"""
    try:
        return DB.query(Diecase).filter(Diecase.diecase_id == diecase_id).one()
    except orm_exc.NoResultFound:
        # choose diecase manually if not found
        UI.display('Diecase %s not found in database!' % diecase_id)
        return fallback()


def get_wedge(wedge_name):
    """Get a Wedge object for a specified wedge name"""
    return Wedge(wedge_name)


def choose_wedge(wedge_name='S5-12E'):
    """Choose a wedge manually"""
    def enter_name():
        """Enter the wedge's name"""
        # Ask for wedge name and set width as it is written on the wedge
        al_it = iter(wu.ALIASES)
        # Group by three
        grouper = zip_longest(al_it, al_it, al_it, fillvalue='')
        old_wedges = '\n'.join('\t'.join(z) for z in grouper)
        prompt = ('\nSome old-style wedge designations:\n\n%s'
                  '\n\nIf you have one of those, '
                  'enter the corresponding new-style number (like S5-xx.yE).'
                  '\n\nWedge designation?' % old_wedges)
        return UI.enter(prompt, default=wedge_name)

    def enter_parameters():
        """Parse the wedge's name and return a list:
        [series, set_width, is_brit_pica, units]"""
        # For countries that use comma as decimal delimiter, convert to point:
        w_name = wedge_name.replace(',', '.').upper().strip()
        # Check if this is an European wedge
        # (these were based on pica = .1667" )
        is_brit_pica = w_name.endswith('E')
        # Away with the initial S, final E and any spaces before and after
        # Make it work with space or dash as delimiter
        wedge = w_name.strip('SE ').replace('-', ' ').split(' ')
        try:
            (series, set_width) = wedge
        except ValueError:
            series = wedge[0]
            set_width = None
        # Now get the set width - ensure that it is float divisible by 0.25
        # no smaller than 5 (narrowest type), no wider than 20 (large comp)
        while True:
            try:
                set_width = float(set_width)
                if not set_width % 0.25 and 5 <= set_width <= 20:
                    break
                else:
                    raise ValueError
            except (TypeError, ValueError):
                prompt = ('Enter the set width as a decimal fraction '
                          'divisible by 0.25 - e.g. 12.25: ')
                set_width = UI.enter(prompt, datatype=float)
        # We have the wedge name, so we can look the wedge up in known wedges
        # (no need to enter the unit values manually)
        units = wu.UNITS.get(series, None)
        while not units:
            # Enter manually if not found:
            prompt = ('Enter the wedge unit values for rows 1...15 '
                      'or 1...16, separated by commas.\n')
            # Now we need to be sure that all whitespace is stripped,
            # and the value written to database is a list of integers
            try:
                units = [int(i.strip())
                         for i in UI.enter(prompt).split(',')]
                # Display warning if the number of steps is not
                # 15 or 16 (15 is most common, 16 was used for HMN and KMN).
                if not 15 <= len(units) <= 16:
                    UI.display('Wedge must have 15 or 16 steps - enter again.')
                    units = None
            except ValueError:
                UI.display('Incorrect value - enter the values again.')
                units = None
        # Now we have the data...
        return {'series': series, 'set_width': set_width,
                'is_brit_pica': is_brit_pica, 'units': units}

    wedge_name = enter_name()
    try:
        get_wedge(wedge_name)
    except ValueError:
        data = enter_parameters()
        wedge = Wedge()
        wedge.update(data)
        return wedge


class MatrixMixin(object):
    """Matrix editing operations"""
    def edit_matrix(self, matrix):
        """Edits the matrix data"""
        styles = matrix.styles
        char = (c.SPACE_NAMES.get(matrix.char) or
                'char: "%s"' % matrix.char if matrix.char
                else 'character unknown')
        styles = 'styles: %s ' % styles.names if not styles.use_all else ''
        UI.display('\n' + '*' * 80 + '\n')
        UI.display('%s %s %s, units: %s'
                   % (matrix.pos, styles, char, matrix.units))
        self.edit_mat_char(matrix)
        self.choose_styles(matrix)
        self.specify_units(matrix)
        return matrix

    @staticmethod
    def edit_mat_char(matrix):
        """Edit the matrix character"""
        prompt = ('Char? (" ": low / "_": high space, '
                  'blank = keep, ctrl-C to exit)?')
        matrix.char = UI.enter(prompt,
                               blank_ok=not matrix.char, default=matrix.char)

    @staticmethod
    def edit_code(matrix):
        """Edit the matrix code"""
        # display char only if matrix is not space and has specified char
        char = matrix.char
        if char and c.SPACE_NAMES.get(char) is None:
            ch_str = '"%s"' % char
            # for matrices with all/unspecified styles don't display these
            style_str = (matrix.styles.names if not matrix.styles.use_all
                         else '')
        else:
            ch_str = c.SPACE_NAMES.get(char) or ''
            style_str = ''
        f_str = ' for ' if ch_str or style_str else ''
        # display style string only if char is there
        prompt_list = ['Enter the matrix position', f_str, style_str, ch_str]
        matrix.pos = UI.enter(''.join(prompt_list), default=matrix.pos)

    @staticmethod
    def specify_units(matrix):
        """Give a user-defined unit value for the matrix;
        mostly used for matrices placed in a different row than the
        unit arrangement indicates; this will make the program set the
        justification wedges and cast the character with the S-needle"""
        desc = '"%s" at ' % matrix.char if matrix.char else ''
        ua_units = matrix.get_units_from_arrangement()
        row_units = matrix.get_row_units()
        if ua_units:
            UI.display('%s%s unit values: %s by UA, %s by row'
                       % (desc, matrix.pos, ua_units, row_units))
            prompt = 'New unit value? (0 = UA units, blank = current)'
        else:
            UI.display('%s%s row unit value: %s' % (desc, matrix.pos,
                                                    row_units))
            prompt = 'New unit value? (0 = row units, blank = current)'
        matrix.units = UI.enter(prompt, default=matrix.units, datatype=float)

    @staticmethod
    def choose_styles(matrix):
        """Choose styles for the matrix"""
        styles = matrix.styles
        styles.choose()
        matrix.styles = styles


class DiecaseMixin(MatrixMixin):
    """Mixin for diecase-related operations"""
    @property
    def wedge(self):
        """Get the temporary wedge, or the diecase's assigned wedge"""
        return self.__dict__.get('_wedge') or self.diecase.wedge

    @wedge.setter
    def wedge(self, wedge):
        """Set the temporary wedge"""
        self.__dict__['_wedge'] = wedge

    @wedge.setter
    def wedge_name(self, wedge_name):
        """Set the wedge with a given name"""
        try:
            self.wedge = (get_wedge(wedge_name) if wedge_name
                          else self.diecase.wedge)
        except ValueError:
            # parsing failed
            self.wedge = choose_wedge(wedge_name)

    @property
    def diecase(self):
        """Get a diecase or empty diecase, lazily instantiating a new one
        if none was chosen before"""
        diecase = self.__dict__.get('_diecase')
        if not diecase:
            # instantiate a new one and cache it
            diecase = Diecase()
            self.__dict__['_diecase'] = diecase
        return diecase

    @diecase.setter
    def diecase(self, diecase):
        """Set a diecase; keep the wedge"""
        self.__dict__['_diecase'] = diecase

    @diecase.setter
    def diecase_id(self, diecase_id):
        """Set a diecase with a given diecase ID, or a current/default one"""
        with suppress(Abort):
            self.diecase = get_diecase(diecase_id, fallback=self.diecase)

    @property
    def charset(self):
        """Get a {style: {char: Matrix object}} charset from the diecase"""
        return self.diecase.layout.charset

    @property
    def space(self):
        """Get a space from diecase; most typically G2, 6-units wide"""
        return self.get_space(units=6, is_low_space=True)

    @property
    def half_quad(self):
        """Get a 9-unit quad (half-square) from diecase"""
        return self.get_space(units=9, is_low_space=True)

    @property
    def quad(self):
        """Get a full em quad"""
        return self.get_space(units=18, is_low_space=True)

    def choose_diecase(self):
        """Chooses a diecase from database"""
        with suppress(Abort):
            self.diecase = choose_diecase(fallback=self.diecase,
                                          fallback_description='keep current')

    def choose_wedge(self):
        """Chooses a wedge from registered ones"""
        self.wedge = choose_wedge()

    def find_matrix(self, char=None, styles=None, position=None, units=None,
                    manual_choice=True):
        """Search the diecase layout and get a matching mat"""
        def define_new_mat():
            """Create a new Matrix object"""
            mat = Matrix(diecase=self.diecase, styles=styles, char=char,
                         units=units, position=position)
            self.edit_code(mat)
            return mat

        def choose_from_menu():
            """Display a menu to choose mats"""
            menu_data = {i: mat for i, mat in enumerate(mats, start=1)}
            menu_data[0] = None
            # build header depending on char and styles
            ch_string = '%s ' % char
            st_string = ('' if styles.use_all or not ch_string
                         else '%s ' % styles.names)
            title = ['Multiple matrices', ' for ' if ch_string else '',
                     st_string, ch_string, 'found. Please choose a matrix:\n']
            UI.display(''.join(title))
            header = ''.join(['Index'.ljust(7), 'Char'.ljust(7),
                              'Code'.ljust(7), 'Styles'.ljust(50)])
            UI.display(header)
            UI.display('-' * len(header))
            for i, mat in menu_data.items():
                UI.display(''.join([str(i).ljust(7),
                                    mat.char.ljust(7),
                                    mat.pos.ljust(7),
                                    mat.styles.names.ljust(50)]))
            UI.display()
            prompt = 'Choose matrix (0 or blank to enter manually)'
            choice = None
            # make sure we get a number corresponding to a diecase
            while choice not in menu_data:
                choice = UI.enter(prompt, blank_ok=True, datatype=int)
            mat = menu_data[choice]
            # if mat is None, define a new one
            return mat or define_new_mat()

        mats = self.diecase.layout.select_many(char, styles, position, units)
        if manual_choice:
            if not mats:
                return define_new_mat()
            elif len(mats) == 1:
                # skip manual choice and select the only matching mat
                return mats[0]
            else:
                return choose_from_menu()
        elif mats:
            # choose the first or only mat found
            return mats[0]
        else:
            # no mats found in automatic choice? raise an exception
            raise e.MatrixNotFound

    def get_space(self, units=5, is_low_space=True):
        """Get a most suitable space for a given number of units"""
        return self.diecase.layout.get_space(units=units, low=is_low_space)

    def get_supporting_space(self, units):
        """Support for overhanging characters with type body narrower than
        the character; used for adding many units"""
        return self.diecase.layout.get_space(units=units, low=False)

    def specify_space_width(self, matrix, width=None):
        """Specify the space's width"""
        # TODO: use Measure as an engine?
        def parse_value(raw_string):
            """Parse the entered value with units"""
            # By default, use wedge set units
            factor = 1
            string = raw_string.strip()
            for symbol in symbols:
                # End after first match
                if string.endswith(symbol):
                    string = string.replace(symbol, '')
                    factor = meas.get(symbol, 1)
                    break
            # Filter the string
            string.replace(',', '.')
            num_string = ''.join(x for x in string if x.isdigit() or x is '.')
            # Convert the value with known unit to units
            units = float(num_string) * factor
            return round(units, 2)

        try:
            # Point to unit conversion factor
            ptu = 1 / self.wedge.unit_point_width
        except AttributeError:
            # Assume set width = 12; 18 units is 12 points, 1 point = 1.33 unit
            # This applies both to pt for .1667 and pp for .166 pica wedges
            ptu = 1.33
        help_text = ('\n\nAvailable units:\n'
                     '    dd - European Didot point,\n'
                     '    cc - cicero (=12dd, .1776"),\n'
                     '    ff - Fournier point,\n'
                     '    cf - Fournier cicero (=12ff, .1628"),\n'
                     '    pp - TeX / US printer\'s pica point,\n'
                     '    Pp - TeX / US printer\'s pica (=12pp, .1660"),\n'
                     '    pt - DTP / PostScript point = 1/72",\n'
                     '    pc - DTP / PostScript pica (=12pt, .1667"),\n'
                     '    u - unit of wedge\'s set\n'
                     '    en - 9 units of wedge\'s set\n'
                     '    em - 18 units of wedge\'s set\n\n')

        meas = {'pc': 12.0 * ptu, 'pt': 1.0 * ptu,
                'Pp': 12 * 0.166 / 0.1667 * ptu, 'pp': 0.166 / 0.1667 * ptu,
                'cc': 12 * 0.1776 / 0.1667 * ptu, 'dd': 0.1776 / 0.1667 * ptu,
                'cf': 12 * 0.1628 / 0.1667 * ptu, 'ff': 0.1628 / 0.1667 * ptu,
                'u': 1, 'en': 9, 'em': 18}
        symbols = ['pc', 'pt', 'Pp', 'pp', 'cc', 'dd', 'cf', 'ff',
                   'en', 'em', 'u']
        prompt = 'Enter the space width value and unit (or "?" for help)'
        while True:
            if not width:
                raw_string = UI.enter(prompt, default='1en')
            else:
                raw_string = str(width)
            if '?' in raw_string:
                # Display help message and start again
                UI.display(help_text)
            try:
                matrix.units = parse_value(raw_string)
                return
            except (TypeError, ValueError):
                UI.display('Incorrect value - enter again...')
                raw_string = None

    def display_diecase_layout(self, diecase=None, pause_after_exit=True):
        """Display the diecase layout, unit values, styles.

        diecase - Diecase object or None (in this case, self.diecase is used)
        pause_after_exit - if True (default), ask user to continue after
                           the layout is displayed.
                           Otherwise continue the program execution
                           (e.g. in diecase edit menus).
        """
        diecase = diecase or self.diecase


    def _display_diecase_layout(self, diecase=None, pause_after_exit=True):
        """Shows a layout for a given diecase ID, unit values for its
        assigned wedge, or the typical S5 if not specified."""
        # TODO: reimplement using layout iterators and style formatting
        def get_char(matrix):
            """New style formatting for diecase layouts"""
            style_modifiers = {Roman: dict(fg=None),
                               Bold: dict(bold=True),
                               Italic: dict(fg='cyan'),
                               SmallCaps: dict(underline=True),
                               Superior: dict(fg='blue'),
                               Inferior: dict(fg='magenta')}
            spaces_symbols = {'_': UI.FormattedText('▣', fg='red'),
                              ' ': UI.FormattedText('□', fg='red'),
                              '': UI.FormattedText(' ')}
            style_options = {'fg': None}
            for style in matrix.styles:
                style_options.update(style_modifiers.get(style))
            return (spaces_symbols.get(matrix.char) or
                    UI.FormattedText(matrix.char, **style_options))

        def get_width(column):
            """Get the column width"""
            return column_widths.get(column, 4)

        def get_mat_unit_value(mat):
            """Get the unit value string for a character, if the width
            overrides the wedge default"""
            show_units = (mat.units != wedge_row_units and
                          mat.char and not mat.is_space)
            if show_units:
                return str(mat.units)
            else:
                return ''

        diecase = diecase or self.diecase
        col_numbers = c.COLUMNS_15
        row_numbers = [x for x in range(1, 16)]
        # Set the initial column width value to 4
        column_widths = {}
        # Now loop over the matrices and adjust the displayed table
        for mat in diecase:
            if '16' in mat.pos:
                col_numbers = c.COLUMNS_17
                row_numbers = [x for x in range(1, 17)]
                break
            elif mat.column in ('NI', 'NL'):
                col_numbers = c.COLUMNS_17
            # Update column width if displayed character turns out too long
            if len(get_char(mat)) + 2 > column_widths.get(mat.column, 4):
                column_widths[mat.column] = len(get_char(mat)) + 2
        # Generate a header with column numbers
        # Widths are variable and depend on text field width
        fields = [col.center(get_width(col)) for col in col_numbers]
        header = ' Row %s Units ' % ''.join(fields)
        # "-----" line in the table
        separator = '—' * len(header)
        # Initialize the displayed layout
        table = [header, separator]
        # Process each row
        for row in row_numbers:
            items = []
            units_row = []
            wedge_row_units = diecase.wedge[row]
            for col in col_numbers:
                width = get_width(col)
                for mat in diecase:
                    if mat.pos == '%s%s' % (col, row):
                        items.append(get_char(mat).center(width))
                        units_row.append(get_mat_unit_value(mat).center(width))
                        # No need to iterate further
                        break
            items = ['|', str(row).center(3), '|', ''.join(items),
                     '|%s|' % str(wedge_row_units).center(5)]
            units_row = ['|', ' ' * 3, '|',
                         ''.join(units_row),
                         '|', ' ' * 5, '|']
            table.append(''.join(items))
            table.append(''.join(units_row))
            # table.append(empty_row)
        # Add the header at the bottom
        table.extend([separator, header])
        # We can display it now
        UI.display('\nDiecase ID: %s  -   assigned stopbar/wedge: %s\n'
                   % (diecase, diecase.wedge))
        for row in table:
            print(row)
        # Explanation of symbols
        UI.display('\nExplanation:', '□ = low space, ▣ = high space',
                   '*a = bold, /a = italic, ·a = small caps',
                   '_a = subscript (inferior), ^a = superscript (superior)',
                   '# - matrix assigned to more than two styles', sep='\n')
        if pause_after_exit:
            UI.pause()

    def edit_diecase_layout(self, diecase=None):
        """Edits a matrix case layout, row by row, matrix by matrix.
        Allows to enter a position to be edited. """
        def swap(command):
            """Swap two matrices based on command"""
            # Process the command string (uppercase)
            command = command.replace('SWAP', '').strip()
            code1, code2 = command.split(',', 1)
            code1, code2 = code1.strip(), code2.strip()
            # Look for matrices
            matches1 = [mat for mat in diecase.matrices
                        if mat.pos == code1]
            matches2 = [mat for mat in diecase.matrices
                        if mat.pos == code2]
            if matches1 and matches2:
                mat1, mat2 = matches1[0], matches2[0]
                mat1.pos, mat2.pos = mat2.pos, mat1.pos

        def edit(mat):
            """Edit a matrix"""
            UI.clear()
            self.display_diecase_layout(diecase, pause_after_exit=False)
            self.edit_matrix(mat)

        def all_rows_mode():
            """Row-by-row editing - all cells in row 1, then 2 etc."""
            for mat in diecase:
                edit(mat)

        def all_columns_mode():
            """Column-by-column editing - all cells in column NI, NL, A...O"""
            # Rearrange the layout so that it's read column by column
            iter_mats = (mat for col in c.COLUMNS_17
                         for mat in diecase if mat.column == col)
            for mat in iter_mats:
                edit(mat)

        def single_row_mode(row):
            """Edits matrices found in a single row"""
            iter_mats = (mat for mat in diecase if mat.row == row)
            for mat in iter_mats:
                edit(mat)

        def single_column_mode(column):
            """Edits matrices found in a single column"""
            iter_mats = (mat for mat in diecase if mat.column == column)
            for mat in iter_mats:
                edit(mat)

        # Map unit values to rows
        # If the layout is empty, we need to initialize it
        diecase = diecase or self.diecase
        can_save = diecase.typeface and diecase.diecase_id
        prompt = ('Enter row number to edit all mats in a row,\n'
                  'column number to edit all mats in a column,\n'
                  'matrix coordinates to edit a single matrix,\n'
                  'or choose edit mode: AR - all matrices row by row, '
                  'AC - all matrices column by column.'
                  '\nYou can swap two mats by entering: "swap pos1, pos2".'
                  '%s'
                  '\nYour choice (or leave blank to exit) : '
                  % (can_save and '\nS to save diecase to database.' or ''))
        while True:
            UI.display('\nCurrent diecase layout:\n')
            self.display_diecase_layout(diecase, pause_after_exit=False)
            UI.display()
            with suppress(IndexError, KeyboardInterrupt,
                          TypeError, AttributeError):
                ans = input(prompt).upper()
                if ans == 'S' and can_save:
                    diecase.save_to_db()
                elif ans == 'AR':
                    all_rows_mode()
                elif ans == 'AC':
                    all_columns_mode()
                elif ans in c.COLUMNS_17:
                    single_column_mode(ans)
                elif ans in [str(x) for x in range(1, 17)]:
                    single_row_mode(int(ans))
                elif ans.startswith('SWAP'):
                    swap(ans)
                elif ans:
                    with suppress(IndexError, TypeError, AttributeError):
                        mats = [mat for mat in diecase
                                if mat.pos == ans.upper()]
                        edit(mats[0])
                else:
                    return diecase.matrices

    def diecase_manipulation(self, diecase=None):
        """A menu with all operations on a diecase"""
        diecase = diecase or self.diecase
        while True:
            UI.clear()
            UI.display_parameters({'Diecase data': diecase.parameters,
                                   'Wedge data': diecase.wedge.parameters})
            options = {'Q': UI.finish,
                       'C': UI.abort,
                       'P': change_parameters,
                       'A': test_lang_completeness,
                       'W': assign_wedge,
                       'E': self.edit_diecase_layout,
                       'N': clear_layout,
                       'U': assign_unit_arrangements,
                       'V': self.display_diecase_layout,
                       'I': import_csv,
                       'X': export_csv}
            messages = ['Matrix case manipulation:\n\n'
                        '[V]iew layout,\n'
                        '[E]dit layout,\n'
                        '[I]mport layout from CSV file,\n'
                        'e[X]port layout to CSV file,\n'
                        'change [P]arameters (diecase ID, typeface),\n'
                        'change [W]edge,\n'
                        'choose [U]nit arrangements,\n'
                        'check if [A]ll characters for chosen language '
                        'are in diecase,\n'
                        '[N]ew layout from scratch\n']
            # Save to database needs a complete set of metadata
            required = {'Typeface': diecase.typeface,
                        'Diecase ID': diecase.diecase_id}
            missing = [item for item in required if not required[item]]
            messages.extend(['Cannot save diecase with missing %s\n'
                             % item.lower() for item in missing])
            if not missing:
                options['S'] = save_to_db
                messages.append('[S]ave diecase to database,\n')
            # Check if it's in the database
            options['D'] = delete_from_db
            messages.append('[D]elete diecase from database,\n')
            # Options constructed
            messages.append('[C] to choose/create another diecase,\n'
                            '[Q] to quit.\n')
            messages.append('Your choice: ')
            message = ''.join(messages)
            UI.simple_menu(message, options)(diecase)
