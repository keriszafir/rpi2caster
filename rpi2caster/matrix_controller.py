# coding: utf-8
"""Diecase manipulation functions"""

import csv
from collections import OrderedDict
from contextlib import suppress
from copy import copy
from functools import partial
from string import ascii_lowercase, ascii_uppercase, digits
from sqlalchemy.orm import exc as orm_exc
from . import basic_models as bm, basic_controllers as bc, definitions as d
from .config import USER_DATA_DIR, CFG
from .models import DB, Diecase
from .ui import UI, Abort, Finish, option

PREFS_CFG = CFG.preferences


def import_csv(diecase, filename=''):
    """Imports a layout from file"""
    def preview(num=5):
        """Preview the first five records in the file"""
        with layout_file:
            records = csv.reader(layout_file, line_num=num,
                                 delimiter=';', quotechar='"')
            text = '\n'.join(''.join(str(field).ljust(15) for field in rec)
                             for rec in records)
            UI.display('File preview: displaying first {} rows:\n'
                       .format(num))
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
        if not UI.confirm('Proceed?', default=True, abort_answer=False):
            return
        # parse the layout
        diecase.load_layout(rec for rec in layout_gen)
    except (TypeError, ValueError):
        UI.pause('Incorrect layout. Check your file.')


def export_csv(diecase, filename=''):
    """Exports the matrix case layout to file."""
    name = diecase.diecase_id or 'NewDiecase'
    # Save the exported diecase layout in the default directory
    file_name = filename or '{}/{}.csv'.format(USER_DATA_DIR, name)
    with suppress(Abort):
        output_file = UI.export_file(file_name)
        with output_file:
            csv_writer = csv.writer(output_file, delimiter=';',
                                    quotechar='"', quoting=csv.QUOTE_ALL)
            csv_writer.writerow(['Char', 'Styles', 'Position', 'Units'])
            # store mats with no position info as well
            csv_writer.writerows(diecase.layout.raw)
        UI.pause('File {} successfully saved.'.format(filename))


def clear_layout(diecase):
    """Generates a new layout for the diecase"""
    if UI.confirm('Are you sure?', default=False, abort_answer=False):
        diecase.layout.reset()
        diecase.store_layout()


def test_characters(diecase, input_iter='', styles=None):
    """Enter the string and parse the diecase to see if any of the
    specified characters are missing."""
    def find_missing_mats(style):
        """Look up characters of a given style in the diecase layout"""
        missing = []
        for char in test_char_set:
            try:
                diecase.layout.select_one(char=char, style=style)
            except bm.MatrixNotFound:
                missing.append(char)
        return missing

    styles = styles or diecase.styles
    input_collection = input_iter or UI.enter('Text to check?')
    test_char_set = sorted(set(input_collection))

    # which characters we don't have, grouped by style
    checks = {style: find_missing_mats(style) for style in styles}
    missing_by_style = {style: missing
                        for style, missing in checks.items() if missing}

    # if we have all needed characters, all missing char lists are empty
    # the diecase is complete, so return True
    if not missing_by_style:
        UI.display('All characters are present.')
        return True

    # info for user
    info = 'Missing matrices for {}: {}'

    # sort the missing mats by style, then by char
    for style in styles:
        missing_chars = missing_by_style.get(style)
        if not missing_chars:
            continue
        missing_chars_string = ', '.join(sorted(missing_chars))
        UI.display(info.format(style.name, missing_chars_string))

    # the diecase is incomplete
    return False


def test_lang_completeness(diecase):
    """Choose a language and test whether the diecase contains all
    characters, and if not, list them"""
    # choose a language and get its letter frequencies
    char_freqs = bc.get_letter_frequencies()
    UI.display('Building character set...\n')

    uppercase = [str(char).upper() for char in char_freqs]
    lowercase = [str(char).lower() for char in char_freqs]
    all_chars = sorted(set(uppercase + lowercase))
    UI.display('Characters:\n{}\n'.format(''.join(all_chars)))

    # choose styles (by default: all those supported by diecase)
    # for completeness checking
    styles = bc.choose_styles(diecase.styles)
    test_characters(diecase, all_chars, styles)
    UI.pause()


def change_parameters(diecase):
    """Change parameters: diecase ID, typeface"""
    prompt = 'Diecase ID? '
    diecase_id = UI.enter(prompt, default=diecase.diecase_id)

    prompt = 'Typeface? (e.g. series, size, name) '
    typeface = UI.enter(prompt, default=diecase.typeface)

    changed = diecase_id != diecase.diecase_id or typeface != diecase.typeface
    if changed and UI.confirm('Apply changes?', abort_answer=False):
        diecase.typeface = typeface
        diecase.diecase_id = diecase_id


def ua_by_style(styles='*', current_mapping=None):
    """Ask for styles and assign them a unit arrangement.
    Return a list of tuples: [(style1, ua1), (style2, ua2)...]
    for each style in styles_string (if called without arguments,
    let user choose the styles manually)"""
    # ensure that the mapping is ordered by style
    styles_collection = bm.Styles(styles)
    mapping = OrderedDict()
    ua_numbers = ', '.join(x for x in sorted(ua.UA))
    UI.display('Known unit arrangements:\n{}'.format(ua_numbers))

    for style in styles_collection:
        prompt = 'UA number for {}?'.format(style.name)
        try:
            current = current_mapping[style]
            # preset the UA for this style
            mapping[style] = current
            ua_number = UI.enter(prompt, default=current, datatype=int)
        except (KeyError, TypeError):
            # no pre-existing mapping
            ua_number = UI.enter(prompt, default='', datatype=str)

        if ua_number:
            mapping[style] = ua_number

    return mapping


def display_unit_values(mapping=None):
    """Print a list on the screen with unit values for each character.
    Use a {style1: ua1, style2: ua2} OrderedDict mapping.
    If mapping is not provided, user will choose style manually."""
    mapping = mapping or ua_by_style()
    # ordered dict of unit values by style, then by char:
    # {roman: {'a': 9, 'b': 9...}, bold: {'a': 10, 'b': 10...}...}
    source = ua.char_unit_values(mapping)

    characters = [*ascii_lowercase, *ascii_uppercase, *digits, *d.LIGATURES]
    # Unit values by styles and chars
    # character     roman    bold     italic
    fields = ('Character', *(style.name for style in source))
    header = ''.join(name.ljust(15) for name in fields)
    # Display the data for characters
    UI.display('Unit values for characters:\n')
    UI.display(header)
    UI.display('-' * len(header))
    for char in characters:
        # get the unit values for each style (or empty string if undefined)
        values = (style_ua.get(char, '') for style_ua in source.values())
        # format to 15-character wide columns and display
        fields = (char.ljust(15), *(str(units).ljust(15) for units in values))
        UI.display(''.join(fields))

    UI.display('\n\nCharacters by unit value:\n')
    # By unit values, then character
    for units in range(4, 25):
        strings = []
        for style, style_ua in source.items():
            chars = [c for c in characters if style_ua.get(c, 0) == units]
            if not chars:
                continue
            strings.append('{} : {}'.format(style.name, ', '.join(chars)))
        if not strings:
            continue
        UI.display('\n\nCharacters {} units wide:'.format(units))
        UI.display('\n'.join(strings))


def assign_unit_arrangements(diecase):
    """Sets the unit arrangements for diecase's styles"""
    unit_arrangements = ua_by_style(diecase.styles, diecase.unit_arrangements)
    if UI.confirm('Display character unit values?', default=True):
        display_unit_values(diecase.unit_arrangements)
        UI.pause()
    prompt = 'Apply changes?'
    arrangements_changed = unit_arrangements != diecase.unit_arrangements
    if arrangements_changed and UI.confirm(prompt, abort_answer=False):
        diecase.unit_arrangements = unit_arrangements


def assign_wedge(diecase):
    """Assigns a wedge (from database or newly-defined) to the diecase"""
    diecase.wedge = bc.choose_wedge(diecase.wedge)


def save_to_db(diecase):
    """Stores the matrix case definition/layout in database"""
    diecase.store_layout()
    DB.session.add(diecase)
    DB.session.commit()
    UI.pause('Data saved successfully.')


def delete_from_db(diecase):
    """Deletes a diecase from database"""
    ans = UI.confirm('Are you sure?', default=False, abort_answer=False)
    if ans:
        DB.session.delete(diecase)
        DB.session.commit()
        UI.pause('Matrix case deleted successfully.')


def get_all_diecases():
    """Lists all matrix cases we have."""
    try:
        database_entries = DB.query(Diecase).order_by(Diecase.diecase_id).all()
        enumerated_diecases = enumerate(database_entries, start=1)
        return OrderedDict(enumerated_diecases)
    except orm_exc.NoResultFound:
        return {}


def list_diecases(data=get_all_diecases()):
    """Display all diecases in a dictionary, plus an empty new one"""
    UI.display('\nAvailable diecases:\n')
    UI.display_header('|{:<5}  {:<25} {:<12} {:<50}|'
                      .format('Index', 'Diecase ID', 'Wedge', 'Typeface'),
                      trailing_newline=0)
    # show the rest of the table
    template = ('|{index:>5}  {d.diecase_id:<25} '
                '{d.wedge.name:<12} {d.typeface:<50}|')
    entries = (template.format(d=diecase, index=index)
               for index, diecase in data.items())
    UI.display(*entries, sep='\n')
    return data


def choose_diecase(fallback=Diecase, fallback_description='new empty diecase'):
    """Select diecases from database and let the user choose one of them.
    If no diecases are found, return None and let the calling logic
    determine what fallback to use."""
    prompt = 'Your choice? (0 = {})'.format(fallback_description)
    data = get_all_diecases()
    # end right away
    if not data:
        return fallback()
    UI.display('Choose a matrix case:', end='\n\n')
    list_diecases(data)
    # empty option for fallback
    qty = len(data)
    # let the user choose the diecase
    choice = UI.enter(prompt, default=0, datatype=int, minimum=0, maximum=qty)
    return data.get(choice) or fallback()


def get_diecase(diecase_id=None, fallback=choose_diecase):
    """Get a diecase with given parameters"""
    try:
        return DB.query(Diecase).filter(Diecase.diecase_id == diecase_id).one()
    except orm_exc.NoResultFound:
        # choose diecase manually if not found
        UI.display('Diecase {} not found in database!'.format(diecase_id))
        return fallback()


class DiecaseMixin:
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
    def wedge_name(self, w_name):
        """Set the wedge with a given name"""
        try:
            self.wedge = bm.Wedge(w_name) if w_name else self.diecase.wedge
        except ValueError:
            # parsing failed
            self.wedge = bc.choose_wedge(w_name)

    def choose_wedge(self):
        """Chooses a new wedge"""
        self.wedge = bc.choose_wedge(self.wedge)

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
        self.diecase = get_diecase(diecase_id, fallback=self.diecase)

    def choose_diecase(self):
        """Chooses a diecase from database"""
        self.diecase = choose_diecase(fallback=self.diecase,
                                      fallback_description='keep current')

    @property
    def charset(self):
        """Get a {style: {char: Matrix object}} charset from the diecase"""
        return self.diecase.layout.charset

    def get_space(self, units=5, low=True, temporary=False):
        """Get a most suitable space for a given number of units"""
        mat = self.diecase.layout.get_space(units=units, low=low)
        return copy(mat) if temporary else mat

    @property
    def space(self):
        """Get a space from diecase; most typically G2, 6-units wide"""
        return self.get_space(units=6, low=True)

    @property
    def half_quad(self):
        """Get a 9-unit quad (half-square) from diecase"""
        return self.get_space(units=9, low=True)

    @property
    def quad(self):
        """Get a full em quad"""
        return self.get_space(units=18, low=True)

    def edit_matrix(self, matrix,
                    edit_char=True, edit_position=True,
                    edit_styles=True, edit_units=True):
        """Edits the matrix data.

        matrix : a Matrix class object to edit,

        edit_char : whether or not to edit the character,
        edit_position : whether or not to edit the matrix coordinates,
        edit_styles : whether or not to change the styles for the matrix,
        edit_units : whether or not to change the matrix unit value
        """
        def _get_char():
            """Get a character or space information"""
            # either a space description or mat character
            char = d.SPACE_NAMES.get(matrix.char, matrix.char)
            return char or 'undefined'

        def _edit_char():
            """Edit the matrix character"""
            if not edit_char:
                return
            prompt = 'Char? (" ": low / "_": high space, blank = keep)'
            matrix.char = UI.enter(prompt, default=matrix.char)

        def _edit_position():
            """Edit the matrix coordinates"""
            if not edit_position:
                return
            matrix.pos = UI.enter('Enter the matrix position',
                                  default=matrix.pos)

        def _edit_styles():
            """Change the matrix styles"""
            # skip this for spaces
            if not edit_styles or matrix.isspace():
                return
            matrix.styles = bc.choose_styles(matrix.styles)

        def _edit_units():
            """Change the matrix unit width value"""
            # skip this for spaces
            if not _edit_units:
                return

            # get unit width values
            row_units = matrix.get_row_units()
            ua_units = matrix.get_units_from_arrangement()
            curr_units = matrix.units

            # build a prompt with units info
            curr_chunk = ('' if not curr_units
                          else 'current: {}'.format(curr_units))
            row_chunk = ('' if not row_units
                         else 'row units: {}'.format(row_units))
            ua_chunk = ('' if not ua_units
                        else 'UA units: {}'.format(ua_units))
            chunks = [x for x in (curr_chunk, row_chunk, ua_chunk) if x]
            if chunks:
                prompt = 'Enter unit width ({})'.format(', '.join(chunks))
            else:
                prompt = 'Enter unit width'
            matrix.units = UI.enter(prompt, default=curr_units, datatype=int,
                                    minimum=4, maximum=25)

        def _edit_space_width():
            """Edits the space width"""
            width = bc.enter_measure('1em', what='space width',
                                     set_width=self.wedge.set_width)
            matrix.units = width.units

        with suppress(Abort):
            # keep displaying this menu until aborted
            while True:
                # generate menu options dynamically
                options = [option(key='c', value=_edit_char, seq=1,
                                  lazy=_get_char, cond=edit_char,
                                  text='change character (current: {})'),
                           option(key='p', value=_edit_position, seq=2,
                                  lazy=matrix.pos, cond=edit_position,
                                  text='change position (current: {})'),
                           option(key='s', value=_edit_styles, seq=3,
                                  lazy=matrix.styles.names,
                                  cond=edit_styles and not matrix.isspace(),
                                  text='assign styles (current: {})'),
                           option(key='u', value=_edit_units, seq=4,
                                  lazy=matrix.units,
                                  cond=edit_units and not matrix.isspace(),
                                  text='change width (current: {} units)'),
                           option(key='w', value=_edit_space_width, seq=4,
                                  lazy=matrix.units,
                                  cond=edit_units and matrix.isspace(),
                                  text='change width (current: {} units)')]
                valid_options = [opt for opt in options if opt.condition]
                if not valid_options:
                    # nothing to do
                    break
                elif len(valid_options) == 1:
                    # only one thing - no need for the menu
                    choice = valid_options[0].value
                else:
                    # display the menu for user to choose
                    choice = UI.simple_menu('Edit the matrix for {} at {}:'
                                            .format(_get_char(), matrix.pos),
                                            options, default_key='Esc')
                # execute the subroutine
                choice()
        return matrix

    def find_matrix(self, char='', styles='*', position='', units=None,
                    choose=True, temporary=False):
        """Search the diecase layout and get a matching mat.

        char, styles, position, units: search criteria,
        choose: manual choice menu or new mat definition,
        temporary: if True, copies the matrix (if it is edited temporarily)."""
        def define_new_mat():
            """Create a new Matrix object"""
            mat = bm.Matrix(diecase=self.diecase, styles=styles_collection,
                            char=char, units=units, pos=position)
            return self.edit_matrix(mat)

        def choose_from_menu():
            """Display a menu to choose mats"""
            menu_data = {i: mat for i, mat in enumerate(mats, start=1)}
            # no matches? make a new one!
            if not menu_data:
                return None

            # build title depending on char and styles
            st_string = ('' if styles_collection.use_all or not char
                         else '{}'.format(styles_collection.names))
            title = ['Multiple matrices', 'for' if char else '',
                     st_string, char, 'found. Please choose a matrix:\n']
            UI.display(' '.join(s for s in title if s))

            # table header
            row = '{:<7}{:<7}{:<7}{:<50}'
            UI.display_header(row.format('Index', 'Char', 'Code', 'Styles'))

            # show available matrices
            for i, mat in menu_data.items():
                UI.display(row.format(i, mat.char, mat.pos, mat.styles.names))
            UI.display()

            # let user choose
            choice = UI.enter('Choose matrix (0 or blank to enter manually)',
                              default=0, minimum=0, maximum=len(menu_data))
            # if mat is None, define a new one
            return menu_data.get(choice)

        styles_collection = bm.Styles(styles)
        mats = self.diecase.layout.select_many(char, styles_collection,
                                               position, units)
        if len(mats) == 1:
            # only one match: return it
            retval = mats[0]
        elif choose:
            # manual mat choice
            retval = choose_from_menu() or define_new_mat()
        elif mats:
            # automatic choice, multiple matches found: get first available
            retval = mats[0]
        else:
            raise bm.MatrixNotFound

        # decide whether a new mat should be returned or copied
        # (e.g. to prevent from modification)
        return copy(retval) if temporary else retval

    def display_diecase_layout(self, diecase=None, pause_after_exit=True):
        """Display the diecase layout, unit values, styles.

        diecase - Diecase object or None (in this case, self.diecase is used)
        pause_after_exit - if True (default), ask user to continue after
                           the layout is displayed.
                           Otherwise continue the program execution
                           (e.g. in diecase edit menus).
        """
        def build_template():
            """Each layout column depends on its content.
            Calculate the widths."""
            # 3 characters to start is reasonable enough
            columns = layout.size.column_numbers
            widths = OrderedDict((name, 3) for name in columns)

            # get the maximum width of characters in every column
            # if it's larger than header field width, update the column width
            for column, initial_width in widths.items():
                widths_gen = (len(mat) for mat in layout.select_column(column))
                widths[column] = max(initial_width, *widths_gen)

            # column widths are now determined... make a field template
            fields = (' {{{col}:^{width}}} '.format(col=col, width=width)
                      for col, width in widths.items())
            template = '| {{row:>3}} |{fields}| {{units:>5}} |'
            return template.format(fields=''.join(fields))

        def build_row(row_number):
            """Build a layout table row.
            A row takes exactly two actual lines (top and bottom),
            top line displays row number, characters and row unit value,
            bottom line displays unit values if different from row units."""
            row = layout.select_row(row_number)
            units = diecase.wedge.units[row_number]
            # initialize the row value dictionaries
            empty = dict(row='', units='')
            top = dict(row=row_number, units=units)
            bottom = dict(row='', units='')
            # fill all mat character fields
            for mat in row:
                # empty row (separator)
                empty[mat.column] = ''
                # character row
                top[mat.column] = mat.char
                # show matrix unit width if it differs from row unit width
                bottom[mat.column] = '' if mat.units == units else mat.units

            # format and concatenate two table rows
            empty_str = template.format(**empty)
            top_str = template.format(**top)
            bottom_str = template.format(**bottom)
            return '{}\n{}\n{}'.format(empty_str, top_str, bottom_str)

        def build_legend():
            """Get the information about styles in diecase."""
            return layout.styles.names

        diecase = diecase or self.diecase
        layout = diecase.layout
        # table row template
        template = build_template()
        # header row template
        header_dict = dict(units='Units', row='Row')
        header_dict.update({col: col for col in layout.size.column_numbers})
        header = template.format(**header_dict)
        # a line of dases to separate the rows
        separator_line = '-' * len(header)
        # proper layout
        contents = (build_row(num) for num in layout.size.row_numbers)
        # info about styles
        legend = build_legend()
        # put the thing together
        table = (header, separator_line, *contents, separator_line, legend)
        # finally display it
        UI.display('Diecase: {d.diecase_id} ({d.typeface}) '
                   '- wedge: {d.wedge.name}'.format(d=diecase))
        UI.display('\n'.join(table))
        if pause_after_exit:
            UI.pause()

    def edit_diecase_layout(self, diecase=None):
        """Edits a matrix case layout, row by row, matrix by matrix.
        Allows to enter a position to be edited. """
        def swap(answer):
            """Swap two matrices based on command"""
            command = answer.upper().strip()
            if command.startswith('SWAP'):
                # Process the command string (uppercase)
                command = command.replace('SWAP', '').strip()
                code1, code2 = command.split(',', 1)
                code1, code2 = code1.strip(), code2.strip()
                # Look for matrices
                mat1 = layout.select_one(position=code1)
                mat2 = layout.select_one(position=code2)
                # Swap their coordinates
                mat1.pos, mat2.pos = mat2.pos, mat1.pos

        def edit(mat):
            """Edit a matrix"""
            UI.clear()
            self.display_diecase_layout(diecase, pause_after_exit=False)
            self.edit_matrix(mat)

        def all_rows():
            """Row-by-row editing - all cells in row 1, then 2 etc."""
            for mat in layout.by_rows():
                edit(mat)

        def all_columns():
            """Column-by-column editing - all cells in column NI, NL, A...O"""
            for mat in layout.by_columns():
                edit(mat)

        def single_row(row):
            """Edits matrices found in a single row"""
            for mat in layout.get_row(row):
                edit(mat)

        def single_column(column):
            """Edits matrices found in a single column"""
            for mat in layout.get_column(column):
                edit(mat)

        # Map unit values to rows
        # If the layout is empty, we need to initialize it
        diecase = diecase or self.diecase
        layout = diecase.layout
        prompt = ('Enter row number to edit all mats in a row,\n'
                  'column number to edit all mats in a column,\n'
                  'matrix coordinates to edit a single matrix,\n'
                  'or choose edit mode: AR - all matrices row by row, '
                  'AC - all matrices column by column.'
                  '\nS - save the layout after editing.'
                  '\nYou can swap two mats by entering: "swap pos1, pos2".')
        # define functions to execute after choosing the answer
        routines = dict(AR=all_rows, AC=all_columns, S=diecase.store_layout)
        # add options for column editing
        routines.update({x: partial(single_column, x)
                         for x in ('NI', 'NL', *'ABCDEFGHIJKLMNO')})
        # add options for row editing
        routines.update({str(x): partial(single_row, x) for x in range(1, 17)})

        while True:
            UI.display('\nCurrent diecase layout:\n')
            self.display_diecase_layout(diecase, pause_after_exit=False)
            UI.display()
            # ask what to do
            answer = UI.enter(prompt, default=Abort, datatype=str).upper()
            routine = routines.get(answer)
            # try to perform the chosen action
            with suppress(bm.MatrixNotFound):
                if routine:
                    routine()
                elif answer.startswith('SWAP'):
                    # swap two mats
                    swap(answer)
                else:
                    # user entered matrix coordinates
                    mat = layout.select_one(position=answer)
                    edit(mat)

    def diecase_manipulation(self, diecase=None):
        """A menu with all operations on a diecase"""
        diecase = diecase or self.diecase
        while True:
            UI.clear()
            UI.display_parameters(diecase.parameters, diecase.wedge.parameters)
            options = [option(key='q', value=Finish, text='Finish', seq=99),
                       option(key='Esc', value=Abort,
                              text='Another diecase', seq=90),
                       option(key='p', )]
            options = {'Q': Finish,
                       'C': Abort,
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
            UI.simple_menu(message, options, allow_abort=True)(diecase)


class MatrixEditor(DiecaseMixin):
    """Entry point for editing matrices and matrix cases."""
    def __init__(self, diecase_id=None):
        with suppress(Abort, Finish):
            while True:
                diecase = get_diecase(diecase_id)
                with suppress(Abort):
                    self.diecase_manipulation(diecase)
