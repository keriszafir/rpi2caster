# coding: utf-8
"""Diecase manipulation functions and classes"""

import csv
from collections import OrderedDict
from contextlib import suppress
from copy import copy
from functools import wraps

from . import basic_models as bm, basic_controllers as bc, definitions as d
from . import views
from .rpi2caster import USER_DATA_DIR, UI, Abort, Finish, option
from .data import WEDGE_DEFINITIONS
from .main_models import DB, Diecase, Wedge, TypefaceSize, UnitArrangement


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
            csv_writer.writerows(diecase.get_raw_layout())
        UI.pause('File {} successfully saved.'.format(filename))


def edit_diecase_typeface_data(diecase):
    """Edit the typeface data for a diecase"""
    def set_typefaces():
        """Assign styles to typeface. Will also look for related typefaces."""
        ua_prompt = 'Unit arrangement variant? Possible options:\n{}'
        for style in styles:
            try:
                # what was set up previously?
                # (helpful when choosing the typeface/UA manually)
                old_typeface, old_unit_arrangement = typeface_data[style]
                old_typeface_series = old_typeface.series
                old_ua_number = old_unit_arrangement.number
            except (KeyError, ValueError, AttributeError):
                old_ua_number, old_typeface_series = '', ''

            try:
                # auto-assign typeface
                variant = main_typeface.get_variant(style)
                if not variant:
                    raise ValueError
            except ValueError:
                # assign manually
                _num = UI.enter('Typeface number for {}?'.format(style.name),
                                default=old_typeface_series)
                _typeface = TypefaceSize(_num, size)
                # choose only one style here
                _style = bc.choose_styles(_typeface.styles.first,
                                          multiple=False,
                                          mask=_typeface.styles).first
                variant = _typeface.get_variant(_style)

            # try to automatically select unit arrangement from typeface data
            # if this fails, choose the unit arrangement manually
            unit_arrangement = variant.unit_arrangement
            if not unit_arrangement:
                views.list_unit_arrangements()
                UI.display('Cannot automatically choose the unit arrangement.')
                ua_number = UI.enter('Unit arrangement number?',
                                     default=old_ua_number)
                uarr = UnitArrangement(ua_number)
                ua_variant = UI.enter(ua_prompt.format(uarr.variant_names),
                                      default='r')
                unit_arrangement = uarr.get_variant(ua_variant)
            typeface_data[style] = (variant, unit_arrangement)

    def assign_normal_wedge():
        """Assign a normal wedge for the diecase"""
        wedge = diecase.wedge
        series = wedge.series
        set_width = main_typeface.set_width
        suffix = 'E' if wedge.is_brit_pica else ''
        designation = 'S{}-{}{}'.format(series, set_width, suffix)
        diecase.wedge = choose_wedge(designation)

    def set_diecase_id():
        """Set the diecase ID (unique name) for this diecase."""
        faces = [item[0] for item in typeface_data.values()]
        size = main_typeface.size
        numbers = '+'.join(sorted({tf.series for tf in faces}))
        UI.display('Enter a name used for identifying your diecase.\n'
                   'It MUST be unique and can, but does not have to, '
                   'include the typeface series and size.\n'
                   'Customize the name to your preference.')
        suggested = '{}-{}-'.format(numbers, size)
        diecase.diecase_id = UI.enter('Diecase ID?', default=suggested)

    typeface_data = diecase.typeface_data
    # get the styles currently assigned to the diecase
    styles = bm.Styles(typeface_data)
    # get the main typeface, most often but not always roman
    # if this fails, get the variant for the Times New Roman 12D roman
    try:
        # changing the data already configured
        main_typeface = typeface_data.get(styles.first)[0]
        if not main_typeface:
            raise ValueError
    except (IndexError, ValueError):
        # no data entered yet
        main_typeface = TypefaceSize()
    UI.display('Diecase: {}'.format(diecase.description))
    UI.display('Editing the typeface information:\n'
               'First choose the typeface series and size.\n'
               'New diecases have 327-12D roman prefilled by default, '
               'change the number and size to your need.\n')
    while True:
        # edit series and size
        series = UI.enter('Type series?', main_typeface.series).upper()
        size = UI.enter('Type size?', main_typeface.size).upper()
        main_typeface = TypefaceSize(series, size)
        # edit or update styles
        styles = bc.choose_styles(styles, mask=main_typeface.combined_styles)
        # choose typeface per style, automatically or manually
        # choose unit arrangements for each style, and normal wedge for diecase
        set_typefaces()
        assign_normal_wedge()
        if UI.confirm('All OK? If not, start again.', allow_abort=True):
            break

    diecase.typeface_data = typeface_data
    if not diecase.diecase_id:
        set_diecase_id()


@DB
def get_all_diecases():
    """Lists all matrix cases we have."""
    try:
        rows = Diecase.select().order_by(Diecase.diecase_id)
        enumerated_diecases = enumerate(rows, start=1)
        return OrderedDict(enumerated_diecases)
    except Diecase.DoesNotExist:
        return {}
    except DB.OperationalError:
        Diecase.create_table(fail_silently=True)
        return get_all_diecases()


@DB
def count_diecases():
    """Count the diecases in database"""
    try:
        return Diecase.select().count()
    except DB.OperationalError:
        # since we're creating a new table, we're sure no diecases are there
        Diecase.create_table(fail_silently=True)
        return 0


@DB
def check_persistence(diecase_id):
    """Check if the diecase is stored in the database"""
    try:
        query = Diecase.select().where(Diecase.diecase_id == diecase_id)
        return query.count()
    except DB.OperationalError:
        Diecase.create_table(fail_silently=True)
        return 0


def choose_diecase(fallback=Diecase, fallback_description='new empty diecase'):
    """Select diecases from database and let the user choose one of them.
    If no diecases are found, return None and let the calling logic
    determine what fallback to use."""
    prompt = 'Your choice? (0 = {})'.format(fallback_description)
    data = get_all_diecases()
    if not data:
        return fallback().load()
    UI.display('Choose a matrix case:', end='\n\n')
    views.list_diecases(data)
    qty = len(data)
    # let the user choose the diecase
    choice = UI.enter(prompt, default=0, datatype=int, minimum=0, maximum=qty)
    diecase = data.get(choice) or fallback()
    return diecase.load()


@DB
def get_diecase(diecase_id=None, fallback=choose_diecase):
    """Get a diecase with given parameters"""
    if diecase_id:
        try:
            return Diecase.get(Diecase.diecase_id == diecase_id).load()
        except Diecase.DoesNotExist:
            UI.display('Diecase {} not found in database!'.format(diecase_id))
        except DB.OperationalError:
            Diecase.create_table(fail_silently=True)
    return fallback().load()


def temp_diecase(routine):
    """Use a temporary diecase"""
    @wraps(routine)
    def wrapper(self, *args, **kwargs):
        """Wrapper function"""
        if not self.diecase:
            # empty diecase? then let the user choose...
            old_diecase, self.diecase = self.diecase, choose_diecase()
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


def resize_layout(diecase):
    """Change the diecase layout size"""
    # select one of 3 sizes used by Monotype
    sizes = [(15, 15), (15, 17), (16, 17)]
    options = [option(key=n, value=size, text='{} x {}'.format(*size))
               for n, size in enumerate(sizes, start=1)]
    selected_size = UI.simple_menu(message='Matrix case size:',
                                   options=options,
                                   default_key=2, allow_abort=True)
    diecase.resize(*selected_size)


def edit_layout(diecase):
    """Edits a matrix case layout, row by row, matrix by matrix.
    Allows to enter a position to be edited. """
    def swap():
        """Swap two matrices based on command"""
        mat1_code = UI.enter('Matrix position to replace?')
        mat1 = diecase.select_one(code=mat1_code)
        mat2_code = UI.enter('Other matrix position?')
        mat2 = diecase.select_one(code=mat2_code)
        # no exceptions? then swap
        mat1.code, mat2.code = mat2.code, mat1.code

    def edit(mat, single=False):
        """Edit a matrix"""
        views.display_layout(diecase)
        mat = bc.edit_matrix(mat, single=single)

    def all_rows():
        """Row-by-row editing - all cells in row 1, then 2 etc."""
        sequence = [mat for column_number in diecase.column_numbers
                    for mat in diecase.select_column(column_number)]
        for mat in sequence:
            edit(mat)

    def all_columns():
        """Column-by-column editing - all cells in column NI, NL, A...O"""
        sequence = [mat for row_number in diecase.row_numbers
                    for mat in diecase.select_row(row_number)]
        for mat in sequence:
            edit(mat)

    def single_row():
        """Edits matrices found in a single row"""
        row = UI.enter('Row?', datatype=int, default='',
                       minimum=1, maximum=diecase.rows)
        for mat in diecase.select_row(row):
            edit(mat)

    def single_column():
        """Edits matrices found in a single column"""
        def condition(col_num):
            """Validation condition for column number"""
            return col_num.upper() in diecase.column_numbers

        prompt = 'Column? [{}]'.format(', '.join(diecase.column_numbers))
        column = UI.enter(prompt, default='', condition=condition).upper()
        for mat in diecase.select_column(column):
            edit(mat)

    def single_matrix():
        """Edits a single matrix with specified coordinates"""
        position = UI.enter('Coordinates?', default='')
        mat = diecase.select_one(code=position.upper())
        edit(mat, single=True)

    def show_layout():
        """Shows diecase layout and pauses"""
        UI.display('\nCurrent diecase layout:\n')
        views.display_layout(diecase)
        UI.pause()

    def options():
        """Menu options"""
        ret = [option(key='r', value=single_row, text='Single row', seq=10),
               option(key='R', value=all_rows,
                      text='All mats, row by row', seq=20),
               option(key='c', value=single_column,
                      text='Single column', seq=30),
               option(key='C', value=all_columns,
                      text='All mats, column by column', seq=40),
               option(key='m', value=single_matrix,
                      text='Single matrix', seq=5),
               option(key='s', value=swap, text='Swap two matrices', seq=60),
               option(key='l', value=show_layout,
                      text='View current layout', seq=70),
               option(key='Ins', value=diecase.store_layout,
                      text='Save the changes in diecase layout', seq=80),
               option(key='Esc', value=Finish, text='Finish editing', seq=99)]
        return ret

    while True:
        opt = UI.simple_menu('Diecase layout edition menu:', options=options)
        with suppress(TypeError):
            raise opt
        with suppress(Abort, Finish, bm.MatrixNotFound):
            opt()


def test_layout_charset(diecase):
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

    lookup_table = diecase.get_lookup_table()
    styles = bc.choose_styles(diecase.styles)
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


def find_matrix(diecase, choose=True, **kwargs):
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
                        diecase=diecase)
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
    mats = diecase.select_many(**kwargs)
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


# Wedge controller routines

def choose_wedge(wedge_name=None):
    """Choose a wedge manually"""
    def enter_name():
        """Enter the wedge's name"""
        # List known wedges
        views.list_wedges()
        return UI.enter('Wedge designation?', default=default_wedge)

    def enter_parameters(name):
        """Parse the wedge's name and return a list:
        [series, set_width, is_brit_pica, units]"""
        def divisible_by_quarter(value):
            """Check if a value is divisible by 0.25:
            1, 3.0, 1.25, 2.5, 5.75 etc. -> True
            2.2, 6.4 etc. -> False"""
            return not value % 0.25

        # For countries that use comma as decimal delimiter, convert to point:
        w_name = name.replace(',', '.').upper().strip()
        # Check if this is an European wedge
        # (these were based on pica = .1667" )
        is_brit_pica = w_name.endswith('E')
        # Away with the initial S, final E and any spaces before and after
        # Make it work with space or dash as delimiter
        # ("S5-12" and "S5 12" should work the same)
        wedge = w_name.strip('SE ').replace('-', ' ').split(' ')
        try:
            series, set_width = wedge
        except ValueError:
            series, set_width = wedge, 0
        # Now get the set width - ensure that it is float divisible by 0.25
        # no smaller than 5 (narrowest type), no wider than 20 (large comp)
        prompt = ('Enter the set width as a decimal fraction '
                  'divisible by 0.25 - e.g. 12.25: ')
        set_width = UI.enter(prompt, datatype=float)

        set_width = UI.enter(prompt, default=set_width, datatype=float,
                             minimum=5, maximum=20,
                             condition=divisible_by_quarter)
        # We have the wedge name, so we can look the wedge up in known wedges
        # (no need to enter the unit values manually)
        current_units = WEDGE_DEFINITIONS.get(series, d.S5)
        prompt = ('Enter the wedge unit values for rows 1...15 '
                  'or 1...16, separated by commas.\n')
        units = UI.enter(prompt, default=current_units, minimum=15, maximum=16)
        # Now we have the data...
        return {'series': series, 'set_width': set_width,
                'is_brit_pica': is_brit_pica, 'units': units}

    default_wedge = str(wedge_name) if wedge_name else 'S5-12E'
    w_name = enter_name()
    try:
        return Wedge(wedge_name=w_name)
    except ValueError:
        data = enter_parameters(w_name)
        return Wedge(wedge_data=data)


def temp_wedge(routine):
    """Decorator for typesetting and casting routines.
    Assign a temporary alternative wedge for casting"""
    @wraps(routine)
    def wrapper(self, *args, **kwargs):
        """Wrapper function"""
        # Assign a temporary wedge
        old_wedge, self.wedge = self.wedge, choose_wedge(self.wedge.name)
        UI.display_parameters(self.wedge.parameters)
        UI.display('\n\n')
        retval = routine(self, *args, **kwargs)
        # Restore the former wedge and exit
        self.wedge = old_wedge
        return retval
    return wrapper


def get_wedge_positions(matrix, normal_wedge, units, correction=0):
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
        limits = normal_wedge.get_adjustment_limits(matrix.islowspace())
        minimum = row_units - limits.shrink
        maximum = row_units + limits.stretch
        message = ('{}: desired width of {} units exceeds '
                   'adjustment limits (min: {} / max: {})')
        width = units + delta
        error_msg = message.format(matrix, width, minimum, maximum)
        raise bm.TypesettingError(error_msg)

    # absolute width: how many .0005" steps is it?
    char_width = steps(normal_wedge, units)
    # how many do we need to add or take away? (for kerning etc.)
    delta = steps(normal_wedge, correction)
    # how wide would a character from the given row normally be?
    # (using self.wedge, not self.diecase.wedge!)
    row_units = normal_wedge[matrix.position.row]
    row_width = steps(normal_wedge, row_units)
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


class DiecaseMixin:
    """Mixin for diecase-related operations"""
    _wedge, _diecase = None, None

    @property
    def wedge(self):
        """Get the temporary wedge, or the diecase's assigned wedge"""
        selected, fallback = self._wedge, self.diecase.wedge
        return selected if selected else fallback if fallback else Wedge()

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
            self.wedge = Wedge(wedge_name=wedge_name)
        except ValueError:
            # parsing failed
            self.wedge = choose_wedge(wedge_name)

    def choose_wedge(self):
        """Chooses a new wedge"""
        self.wedge = choose_wedge(self.wedge)
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
        char_units = units or self.get_units(matrix)
        return get_wedge_positions(matrix, self.wedge, char_units, correction)

    @property
    def diecase(self):
        """Get a diecase or empty diecase, lazily instantiating a new one
        if none was chosen before"""
        diecase = self._diecase
        if diecase is None:
            # instantiate a new one and cache it
            diecase = Diecase().load()
            self._diecase = diecase
        return diecase

    @diecase.setter
    def diecase(self, diecase):
        """Set a diecase; keep the wedge"""
        self._diecase = diecase

    @property
    def diecase_id(self):
        """Get the diecase ID"""
        return self.diecase.diecase_id

    @diecase_id.setter
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
        return self.diecase.get_charset()

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

        return self.diecase.get_space(units, low, wedge=self.wedge)

    def find_matrix(self, choose=True, **kwargs):
        """Search the diecase layout and get a matching mat.

        choose: manual choice menu or new mat definition,
        temporary: if True, copies the matrix (if it is edited temporarily),

        kwargs: char, styles, position, units: search criteria."""
        return find_matrix(self.diecase, choose, **kwargs)

    def resize_layout(self):
        """Resize the layout of currently used diecase"""
        resize_layout(self.diecase)
        self.diecase.store_layout()

    @UI.paused
    def display_diecase_layout(self):
        """Display the diecase layout, unit values, styles."""
        views.display_layout(self.diecase)

    def test_diecase_charset(self):
        """Test whether the diecase layout has all required characters,
        either for a text or language's character set."""
        test_layout_charset(self.diecase)

    def diecase_manipulation(self):
        """A menu with all operations on a diecase"""
        @DB
        def _save():
            """Stores the matrix case definition/layout in database"""
            is_stored = check_persistence(self.diecase.diecase_id)
            self.diecase.store()
            self.diecase.save(force_insert=not is_stored)
            UI.pause('Data saved.')

        @DB
        def _save_as():
            """Stores the diecase in database with a different diecase ID"""
            diecase = copy(self.diecase)
            while check_persistence(diecase.diecase_id):
                prompt = 'New diecase ID (must be unique)?'
                diecase.diecase_id = UI.enter(prompt, default=diecase)
            diecase.save(force_insert=True)

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
            edit_diecase_typeface_data(self.diecase)
            if UI.confirm('Save the diecase in database?'):
                _save()

        def _display_arrangements():
            """Display all unit arrangements for this diecase"""
            for unit_arrangement in self.diecase.unit_arrangements.values():
                views.display_ua_variant(unit_arrangement)
                UI.pause()

        def _edit_layout():
            """Edits a matrix case layout, row by row, matrix by matrix.
            Allows to enter a position to be edited. """
            edit_layout(self.diecase)

        def _clear_layout():
            """Generates a new layout for the diecase"""
            if UI.confirm('Are you sure?', default=False, abort_answer=False):
                self.diecase.purge()

        def _import():
            """Import diecase layout from CSV"""
            return import_csv(self.diecase)

        def _export():
            """Export diecase layout to CSV"""
            return export_csv(self.diecase)

        def header():
            """Menu header"""
            if not self.diecase.diecase_id:
                return ('Diecase manipulation menu:\n'
                        'To start, you must name your diecase.\n'
                        'The name must be unique, for example "327-12-01".')
            elif not check_persistence(self.diecase.diecase_id):
                return ('Diecase manipulation menu:\n'
                        'Diecase ID: {}\n'
                        'The diecase is not yet stored in the database.\n'
                        'You have to save it first before you can edit it.'
                        .format(self.diecase.diecase_id))
            return ('Diecase manipulation menu:\n\nWorking on {} ({})'
                    .format(self.diecase.diecase_id, self.diecase.description))

        def options():
            """Generate menu options"""
            is_stored = check_persistence(self.diecase.diecase_id)
            diecases_present = count_diecases()
            ret = [option(key='l', value=self.display_diecase_layout, seq=1,
                          text='Display diecase layout'),
                   option(key='e', value=_edit_layout,
                          text='Edit diecase layout', seq=2),
                   option(key='u', value=_display_arrangements, seq=4,
                          text='Display unit arrangements for this diecase'),
                   option(key='i', value=_edit_typeface, seq=11,
                          text='Edit the diecase information'),
                   option(key='t', value=self.test_diecase_charset, seq=15,
                          text='Test if diecase contains required characters'),
                   option(key='f', value=_import, seq=30,
                          text='Import layout from file'),
                   option(key='x', value=_export, seq=31,
                          text='Export layout to file'),
                   option(key='r', value=self.resize_layout, seq=89,
                          text='Change the diecase layout size',
                          desc=('Current: {} x {}'
                                .format(self.diecase.rows,
                                        self.diecase.columns))),
                   option(key='n', value=_clear_layout,
                          text='Clear the diecase layout', seq=90),
                   option(key='ctrl_s', value=_save, seq=91,
                          text='Store the diecase in database',
                          cond=self.diecase.diecase_id),
                   option(key='ctrl_n', value=_save_as, seq=92,
                          text='Store the diecase under a different name',
                          cond=is_stored),
                   option(key='delete', value=_delete, seq=93, cond=is_stored,
                          text='Delete diecase from database'),
                   option(key='F2', value=_change_diecase, seq=94,
                          text='Change diecase', cond=diecases_present),
                   option(key='F3', seq=95, text='List typefaces',
                          value=UI.paused(views.list_typefaces)),
                   option(key='F4', seq=96, text='List unit arrangements',
                          value=UI.paused(views.list_unit_arrangements)),
                   option(key='F5', seq=97, text='List normal wedges',
                          value=UI.paused(views.list_wedges))]
            return ret

        UI.dynamic_menu(options, header=header)
