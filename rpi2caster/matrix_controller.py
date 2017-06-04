# coding: utf-8
"""Diecase manipulation functions and classes"""

import csv
from collections import OrderedDict
from contextlib import suppress
from functools import partial, wraps
from . import basic_models as bm, basic_controllers as bc, definitions as d
from .rpi2caster import USER_DATA_DIR, UI, Abort, Finish, option
from .data import TYPEFACES as TF, UNIT_ARRANGEMENTS as UA
from .main_models import DB, Diecase


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
        UI.pause('Incorrect layout. Check your file.', allow_abort=True)


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


def edit_typeface(diecase):
    """Change parameters: diecase ID, typeface"""
    def assign_unit_arrangement(ua_id, style):
        """Assign an unit arrangement and variant to a style"""
        prompt = 'Unit arrangement for {}?'.format(style.name)
        ua_number = UI.enter(prompt, default=ua_id or '', datatype=int)
        ua_definitions = UA.get(ua_number)
        if not ua_definitions:
            # no UA or no specified variant in the UA
            ex_prompt = 'No definition found for UA #{}'.format(ua_number)
            raise bm.UnitArrangementNotFound(ex_prompt)
        if len(ua_definitions) == 1:
            # get the first and only variant, if it was not specified
            variant = ua_definitions[0]
        else:
            # which variants are in the arrangements? choose
            variants = {v.short: v for v in d.VARIANTS}
            opts = [option(key=v, value=v, text=variants.get(v).name)
                    for v in ua_definitions]
            variant = UI.simple_menu('Choose the UA variant', opts)
        # assign and ask if user wants to see the unit values
        choice = (ua_number, variant)
        if UI.confirm('Display unit values?'):
            # make an UA object and display it
            arrangement = bm.UnitArrangement(*choice)
            bc.display_ua(arrangement)
        return choice

    def edit_style(style):
        """edit data for a given style"""
        # look for current settings in raw data
        raw_data = typeface.get(style.short, {})
        current_series = raw_data.get('typeface', 0)
        ua_id, _ = raw_data.get('ua', (0, ''))
        # select typeface name
        prompt = 'Typeface series for {}?'.format(style.name)
        series = UI.enter(prompt, current_series or type_series)
        # set the unit arrangement
        while True:
            try:
                unit_arr = assign_unit_arrangement(ua_id, style)
                break
            except bm.UnitArrangementNotFound as exc:
                UI.display('{}'.format(exc))
                if not UI.confirm('Cannot assign UA to style. Try again?'):
                    unit_arr = (0, '')
                    break

        new_data[style.short] = dict(typeface=series, size=size, ua=unit_arr)

    def generate_diecase_id():
        """generate the new diecase ID"""
        typeface_numbers = (s.get('typeface', 0) for s in new_data.values())
        numbers = sorted(n for n in typeface_numbers if n)
        series_string = '+'.join(str(n) for n in numbers)
        diecase_id = '{}-{}'.format(series_string, size)
        return diecase_id

    # enter the main (dominant) type series
    new_data = {}
    typeface = diecase.typeface
    while True:
        type_series = UI.enter('Typeface # for diecase?', datatype=int)
        typeface_name = TF.get(type_series, {}).get('typeface', 'unknown')
        if UI.confirm('Typeface name: {} - OK?'.format(typeface_name)):
            break
    # enter size
    size = UI.enter('Type size?', default=12.0)
    # choose styles
    styles = bc.choose_styles(typeface.styles or diecase.layout.styles)
    for style in styles:
        edit_style(style)
    # edit diecase ID
    default_diecase_id = diecase.diecase_id or generate_diecase_id()
    diecase_id = UI.enter('Diecase ID (unique)?', default_diecase_id)
    # ask for confirmation
    if new_data != typeface.raw and UI.confirm('Save changes'):
        diecase.typeface = new_data
        diecase.diecase_id = diecase_id


@DB
def get_all_diecases():
    """Lists all matrix cases we have."""
    try:
        rows = Diecase.select().order_by(Diecase.diecase_id)
        enumerated_diecases = enumerate(rows, start=1)
        return OrderedDict(enumerated_diecases)
    except Diecase.DoesNotExist:
        return {}


def list_diecases(data=get_all_diecases()):
    """Display all diecases in a dictionary, plus an empty new one"""
    UI.display('\nAvailable diecases:\n')
    UI.display_header('|{:<5}  {:<25} {:<12} {:<50}|'
                      .format('Index', 'Diecase ID', 'Wedge', 'Typeface'),
                      trailing_newline=0)
    # show the rest of the table
    template = ('|{index:>5}  {d.diecase_id:<25} '
                '{d.wedge.name:<12} {d.typeface.text:<50}|')
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
    if not data:
        return fallback()
    UI.display('Choose a matrix case:', end='\n\n')
    list_diecases(data)
    qty = len(data)
    # let the user choose the diecase
    choice = UI.enter(prompt, default=0, datatype=int, minimum=0, maximum=qty)
    return data.get(choice) or fallback()


@DB
def get_diecase(diecase_id=None, fallback=choose_diecase):
    """Get a diecase with given parameters"""
    if diecase_id:
        with suppress(Diecase.DoesNotExist):
            return Diecase.get(Diecase.diecase_id == diecase_id)
        UI.display('Diecase {} not found in database!'.format(diecase_id))
    return fallback()


def temp_diecase(routine):
    """Use a temporary diecase"""
    @wraps(routine)
    def wrapper(self, *args, **kwargs):
        """Wrapper function"""
        if not self.diecase:
            # empty diecase? then let the user choose...
            old_diecase, self.diecase = self.wedge, choose_diecase()
            UI.display_parameters(self.diecase.parameters)
            UI.display('\n\n')
            retval = routine(self, *args, **kwargs)
            # cleanup: restore the previous diecase
            self.diecase = old_diecase
        else:
            # if diecase was chosen before, don't ask
            retval = routine(self, *args, **kwargs)
        return retval
    return wrapper


# Diecase layout controller routines

def display_layout(layout):
    """Display the diecase layout, unit values, styles."""
    def get_formatted_text(text, styles, length='^3'):
        """format a text with formatting string in styles definitions"""
        field = '{{:{}}}'.format(length) if length else '{}'
        if text in d.SPACE_NAMES:
            # got a space = display symbol instead
            return field.format(d.SPACE_SYMBOLS.get(text[0]))
        else:
            collection = bm.Styles(styles)
            ansi_codes = ';'.join(str(s.ansi) for s in collection if s.ansi)
            template = '\x1b[{codes}m{text}\x1b[0m'
            return template.format(codes=ansi_codes, text=field.format(text))

    def get_column_widths():
        """calculate column widths to adjust the content"""
        # 3 characters to start is reasonable enough
        columns = layout.size.column_numbers
        column_widths = OrderedDict((name, 3) for name in columns)

        # get the maximum width of characters in every column
        # if it's larger than header field width, update the column width
        for column, initial_width in column_widths.items():
            widths_gen = (len(mat) for mat in layout.select_column(column))
            column_widths[column] = max(initial_width, *widths_gen)
        return column_widths

    def build_row(row_number):
        """make a diecase layout table row - actually, 3 rows:
            empty row - separator; main row - characters,
            units row - unit values, if not matching the row units.
        """
        row = layout.select_row(row_number)
        units = layout.diecase.wedge.units[row_number]
        # initialize the row value dictionaries
        empty_row = dict(row='', units='')
        main_row = dict(row=row_number, units=units)
        units_row = dict(row='', units='')
        # fill all mat character fields
        for mat in row:
            column = mat.position.column
            empty_row[column] = ''
            # display unit width if it differs from row width
            m_units = '' if mat.units == units else mat.units
            units_row[column] = m_units
            # format character for display
            fmt = '^{}'.format(widths.get(column, 3))
            main_row[column] = get_formatted_text(mat.char, mat.styles, fmt)

        # format and concatenate two table rows
        empty_str = template.format(**empty_row)
        main_str = template.format(**main_row)
        units_str = template.format(**units_row)
        return '{}\n{}\n{}'.format(empty_str, main_str, units_str)

    def build_description():
        """diecase description: ID, typeface, wedge name and set width"""
        left = '{d.diecase_id} ({d.typeface.text})'.format(d=layout.diecase)
        right = layout.diecase.wedge.name
        center = ' ' * (len(header) - len(left) - len(right) - 4)
        description = '║ {}{}{} ║'.format(left, center, right)
        line = '═' * (len(description) - 2)
        upper_border = '╔{}╗'.format(line)
        lower_border = '╠{}╣'.format(line)
        return '\n'.join((upper_border, description, lower_border))

    # table row template
    widths = get_column_widths()
    fields = ' '.join(' {{{col}:^{width}}} '.format(col=col, width=width)
                      for col, width in widths.items())
    template = '║ {{row:>3}} │{fields}│ {{units:>5}} ║'.format(fields=fields)
    # header row template
    header = dict(units='Units', row='Row')
    header.update({col: col for col in widths})
    header = template.format(**header)
    # proper layout
    contents = (build_row(num) for num in layout.size.row_numbers)
    # info about styles
    legend = ', '.join(get_formatted_text(s.name, s) for s in layout.styles)
    # table description
    desc = build_description()
    # put the thing together
    table = (desc, header, '╟{}╢'.format('─' * (len(header) - 2)),
             *contents, '╚{}╝'.format('═' * (len(header) - 2)),
             legend)
    # finally display it
    UI.display('\n'.join(table))


def resize_layout(diecase):
    """Change the diecase layout size"""
    # select one of 3 sizes used by Monotype
    sizes = [(15, 15), (15, 17), (16, 17)]
    options = [option(key=n, value=size, text='{} x {}'.format(*size))
               for n, size in enumerate(sizes, start=1)]
    selected_size = UI.simple_menu(message='Matrix case size:',
                                   options=options,
                                   default_key=2, allow_abort=True)
    diecase.layout.resize(*selected_size)


def edit_layout(layout):
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
            mat1 = layout.select_one(code=code1)
            mat2 = layout.select_one(code=code2)
            # Swap their coordinates
            mat1.code, mat2.code = mat2.code, mat1.code

    def edit(mat):
        """Edit a matrix"""
        UI.clear()
        display_layout(layout)
        mat = bc.edit_matrix(mat)

    def all_rows():
        """Row-by-row editing - all cells in row 1, then 2 etc."""
        for mat in sum(layout.by_rows(), []):
            edit(mat)

    def all_columns():
        """Column-by-column editing - all cells in column NI, NL, A...O"""
        for mat in sum(layout.by_columns(), []):
            edit(mat)

    def single_row(row):
        """Edits matrices found in a single row"""
        for mat in layout.select_row(row):
            edit(mat)

    def single_column(column):
        """Edits matrices found in a single column"""
        for mat in layout.select_column(column):
            edit(mat)

    # Map unit values to rows
    # If the layout is empty, we need to initialize it
    diecase = layout.diecase
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
        display_layout(layout)
        UI.display()
        # ask what to do
        answer = UI.enter(prompt, default=Abort, datatype=str).upper()
        routine = routines.get(answer)
        # try to perform the chosen action
        with suppress(bm.MatrixNotFound, Abort, Finish):
            if routine:
                routine()
            elif answer.startswith('SWAP'):
                # swap two mats
                swap(answer)
            else:
                # user entered matrix coordinates
                mat = layout.select_one(code=answer)
                edit(mat)


def test_layout_charset(layout):
    """Tests completeness for a chosen language or text."""
    def get_lang_chars(lang):
        """Get an ordered set of characters in a language"""
        characters = bm.CharFreqs(lang)
        lowercase = (char for char in characters)
        uppercase = (char.upper() for char in characters)
        return lambda: (*uppercase, *lowercase)

    def enter_text():
        """Get an ordered set of all characters found in a text"""
        text = UI.edit()
        return sorted(set(char for char in text if not char.isspace()))

    def make_charset():
        """Use a menu to choose language or enter custom text,
        then return a set of all characters found"""
        lang_options = [option(value=get_lang_chars(lang),
                               text='{} - {}'.format(lang, lang_name))
                        for lang, lang_name in sorted(d.LANGS.items())]
        options = [*lang_options,
                   option(key='Esc', value=Abort, seq=99, text='Exit'),
                   option(key='e', value=enter_text, seq=98,
                          text='Custom text')]
        charset = UI.simple_menu('Choose language or enter text',
                                 options, default_key='e', allow_abort=False)()
        return sorted(set(charset))

    def find_missing_mats(style):
        """Look up characters of a given style in the diecase layout"""
        missing = []
        for char in charset:
            mat = lookup_table.get((char, style))
            if not mat:
                missing.append(char)
        return missing

    lookup_table = layout.get_lookup_table()
    styles = bc.choose_styles(layout.styles)
    charset = make_charset()
    # which characters we don't have, grouped by style
    checks = {style: find_missing_mats(style) for style in styles}
    missing_by_style = {style: missing
                        for style, missing in checks.items() if missing}

    # if we have all needed characters, all missing char lists are empty
    # the diecase is complete, so return True
    if not missing_by_style:
        UI.pause('All characters are present.')
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
    UI.pause()
    return False


def find_matrix(layout, choose=True, **kwargs):
    """Search the diecase layout and get a matching mat.

    char, styles, position, units: search criteria,
    choose: manual choice menu or new mat definition."""
    def define_new_mat():
        """Create a new Matrix object"""
        position = (kwargs.get('position', '') or kwargs.get('pos', '') or
                    UI.enter('Matrix coordinates?', default=''))
        if not position:
            raise bm.MatrixNotFound('No coordinates entered')
        mat = bm.Matrix(char=char, styles=styles, code=position,
                        diecase=layout.diecase)
        return mat

    def choose_from_menu():
        """Display a menu to choose mats"""
        matrices = sorted(mats, key=lambda mat: (mat.char, mat.position))
        menu_data = {i: mat for i, mat in enumerate(matrices, start=1)}
        # no matches? make a new one!
        if not menu_data:
            return None

        # build title depending on char and styles
        st_string = ('' if styles.use_all or not char
                     else '{}'.format(styles.names))
        title = ['Multiple matrices', 'for' if char else '',
                 st_string, char, 'found. Please choose a matrix:\n']
        UI.display(' '.join(s for s in title if s))

        # table header
        row = '{:<7}{}'
        UI.display_header(row.format('Index', 'Matrix'))

        # show available matrices
        for i, mat in menu_data.items():
            UI.display(row.format(i, mat))
        UI.display()

        # let user choose
        choice = UI.enter('Choose matrix (0 or blank to enter manually)',
                          default=0, minimum=0, maximum=len(menu_data))
        # if mat is None, define a new one
        return menu_data.get(choice)

    char = kwargs.get('char', '')
    styles = bm.Styles(kwargs.get('styles', '*'))
    mats = layout.select_many(**kwargs)
    if len(mats) == 1:
        # only one match: return it
        return mats[0]
    elif choose:
        # manual mat choice
        return choose_from_menu() or define_new_mat()
    elif mats:
        # automatic choice, multiple matches found: get first available
        return mats[0]
    else:
        raise bm.MatrixNotFound('Automatic matrix lookup failed')


class DiecaseMixin:
    """Mixin for diecase-related operations"""
    _wedge, _diecase = None, None

    @property
    def wedge(self):
        """Get the temporary wedge, or the diecase's assigned wedge"""
        selected, fallback = self._wedge, self.diecase.wedge
        return selected if selected else fallback if fallback else bm.Wedge()

    @wedge.setter
    def wedge(self, wedge):
        """Set the temporary wedge"""
        self._wedge = wedge

    @wedge.setter
    def wedge_name(self, wedge_name):
        """Set the wedge with a given name"""
        if not wedge_name:
            return
        try:
            self.wedge = bm.Wedge(wedge_name=wedge_name)
        except ValueError:
            # parsing failed
            self.wedge = bc.choose_wedge(wedge_name)

    def choose_wedge(self):
        """Chooses a new wedge"""
        self.wedge = bc.choose_wedge(self.wedge)
        return self.wedge

    def get_units(self, matrix):
        """Get the number of units translated to currently used wedge.
        Use this for calculating unit width in typesetting routines."""
        dc_wedge = self.diecase.wedge
        width = matrix.units * dc_wedge.set_width * dc_wedge.pica
        # self.wedge units
        return width / self.wedge.set_width / self.wedge.pica

    def get_wedge_positions(self, matrix, units=0, correction=0):
        """Calculate the 0075 and 0005 wedge positions for this matrix
        based on the current wedge used.

        matrix - a Matrix object
        correction - units of self.wedge's set to add/subtract,
        units - arbitrary character width in units of self.wedge's set"""
        def steps(wedge, unit_width=0):
            """get a width (in .0005" steps) of a character
            for a given number of units or diecase row"""
            inches = unit_width / 18 * wedge.set_width / 12 * wedge.pica
            # return a number of 0.0005" steps
            return int(2000 * inches)

        def limits_exceeded():
            """raise an error if width can't be adjusted with wedges"""
            limits = self.wedge.get_adjustment_limits(matrix.islowspace())
            minimum = row_units - limits.shrink
            maximum = row_units + limits.stretch
            message = ('{}: desired width of {} units exceeds '
                       'adjustment limits (min: {} / max: {})')
            width = char_units + delta
            error_msg = message.format(matrix, width, minimum, maximum)
            raise bm.TypesettingError(error_msg)

        # first we need to know how many units self.wedge's set the char has
        char_units = units or self.get_units(matrix)
        # absolute width: how many .0005" steps is it?
        char_width = steps(self.wedge, char_units)
        # how many do we need to add or take away? (for kerning etc.)
        delta = steps(self.wedge, correction)
        # how wide would a character from the given row normally be?
        # (using self.wedge, not self.diecase.wedge!)
        row_units = matrix.get_units_from_row(wedge_used=self.wedge)
        row_width = steps(self.wedge, row_units)
        # calculate the difference and wedge positions
        # 1 step of 0075 wedge is 15 steps of 0005; neutral positions are 3/8
        # 3 * 15 + 8 = 53, so any increment/decrement is relative to this
        increments = char_width + delta - row_width + 53
        # Upper limit: 15/15 => 15*15=225 + 15 = 240;
        # lower limit:  1/ 1 => 1 * 15 + 1 = 16
        if increments < 16 or increments > 240:
            limits_exceeded()
        # calculate wedge positions from the increments
        pos_0005, pos_0075 = increments % 15, increments // 15
        if not pos_0005:
            # wedge positions cannot be zero
            pos_0005, pos_0075 = 15, pos_0075 - 1
        return d.WedgePositions(pos_0075, pos_0005)

    @property
    def diecase(self):
        """Get a diecase or empty diecase, lazily instantiating a new one
        if none was chosen before"""
        diecase = self._diecase
        if not diecase:
            # instantiate a new one and cache it
            diecase = Diecase()
            self._diecase = diecase
        return diecase

    @diecase.setter
    def diecase(self, diecase):
        """Set a diecase; keep the wedge"""
        self._diecase = diecase

    @diecase.setter
    def diecase_id(self, diecase_id):
        """Set a diecase with a given diecase ID, or a current/default one"""
        self.diecase = get_diecase(diecase_id, fallback=self.diecase)

    def choose_diecase(self):
        """Chooses a diecase from database"""
        self.diecase = choose_diecase(fallback=self.diecase,
                                      fallback_description='keep current')
        return self.diecase

    @property
    def charset(self):
        """Get a {style: {char: Matrix object}} charset from the diecase"""
        return self.diecase.layout.get_charset()

    @property
    def space(self):
        """Get a space from diecase; most typically G2, 6-units wide"""
        return self.find_space(units=6, low=True)

    @property
    def half_quad(self):
        """Get a 9-unit quad (half-square) from diecase"""
        return self.find_space(units=9, low=True)

    @property
    def quad(self):
        """Get a full em quad"""
        return self.find_space(units=18, low=True)

    def find_space(self, units, low=True):
        """Find a matching space. If unit width is specified, try to
        look automatically, otherwise let user decide how wide it should be."""
        if not units:
            width = bc.set_measure(input_value='9u', unit='u',
                                   what='space width',
                                   set_width=self.wedge.set_width)
            units = width.units

        return self.diecase.layout.get_space(units, low, wedge=self.wedge)

    def find_matrix(self, choose=True, **kwargs):
        """Search the diecase layout and get a matching mat.

        choose: manual choice menu or new mat definition,
        temporary: if True, copies the matrix (if it is edited temporarily),

        kwargs: char, styles, position, units: search criteria."""
        return find_matrix(self.diecase.layout, choose, **kwargs)

    def resize_layout(self):
        """Resize the layout of currently used diecase"""
        resize_layout(self.diecase)

    def display_diecase_layout(self, layout=None):
        """Display the diecase layout, unit values, styles."""
        display_layout(layout or self.diecase.layout)
        UI.pause()

    def test_diecase_charset(self):
        """Test whether the diecase layout has all required characters,
        either for a text or language's character set."""
        test_layout_charset(self.diecase.layout)

    def diecase_manipulation(self):
        """A menu with all operations on a diecase"""
        @DB
        def _save():
            """Stores the matrix case definition/layout in database"""
            self.diecase.store_layout()
            self.diecase.save()
            UI.pause('Data saved.')

        @DB
        def _delete():
            """Deletes a diecase from database"""
            prompt = 'Are you sure?'
            ans = UI.confirm(prompt, default=False, abort_answer=False)
            if ans:
                self.diecase.delete_instance()
                UI.pause('Matrix case deleted.')

        def _change_diecase():
            """Chooses another diecase"""
            self.diecase = choose_diecase()

        def _edit_typeface():
            """Edit diecase's typeface info"""
            edit_typeface(self.diecase)

        def _display_arrangements():
            """Display all unit arrangements for this diecase"""
            for unit_arrangement in self.diecase.unit_arrangements.values():
                bc.display_ua(unit_arrangement)
                UI.pause()

        def _edit_layout():
            """Edits a matrix case layout, row by row, matrix by matrix.
            Allows to enter a position to be edited. """
            edit_layout(self.diecase.layout)

        def _clear_layout():
            """Generates a new layout for the diecase"""
            if UI.confirm('Are you sure?', default=False, abort_answer=False):
                self.diecase.layout.reset()
                self.diecase.store_layout()

        def _import():
            """Import diecase layout from CSV"""
            return import_csv(self.diecase)

        def _export():
            """Export diecase layout to CSV"""
            return export_csv(self.diecase)

        header = 'Diecase manipulation menu'
        options = [option(key='l', value=self.display_diecase_layout,
                          text='Display diecase layout', seq=1),
                   option(key='e', value=_edit_layout,
                          text='Edit diecase layout', seq=2),
                   option(key='u', value=_display_arrangements,
                          text='Display unit arrangements', seq=4),
                   option(key='p', value=_edit_typeface, seq=11,
                          text='Edit typeface information'),
                   option(key='t', value=self.test_diecase_charset, seq=15,
                          text='Test if diecase contains required characters'),
                   option(key='i', value=_import, seq=30,
                          text='Import layout from file'),
                   option(key='x', value=_export, seq=31,
                          text='Export layout to file'),
                   option(key='r', value=self.resize_layout, seq=89,
                          text='Change the diecase layout size'),
                   option(key='n', value=_clear_layout,
                          text='Clear the diecase layout', seq=90),
                   option(key='ins', value=_save, seq=91,
                          text='Save diecase to database',
                          cond=lambda: (self.diecase.diecase_id and
                                        self.diecase.typeface)),
                   option(key='delete', value=_delete, seq=92,
                          text='Delete diecase from database'),
                   option(key='F2', value=bc.list_typefaces, seq=95,
                          text='List typefaces'),
                   option(key='F3', value=_change_diecase, seq=96,
                          text='Change diecase'),
                   option(key='Esc', value=Abort, seq=98, text='Back'),
                   option(key='f10', value=Finish, seq=99,
                          text='Exit the diecase manipulation utility')]
        UI.dynamic_menu(options, header=header, allow_abort=False)


class MatrixEngine(DiecaseMixin):
    """Allows to look up characters in diecases"""
    def __init__(self, diecase_id=None):
        self.diecase = get_diecase(diecase_id)
        self.wedge = self.diecase.wedge
