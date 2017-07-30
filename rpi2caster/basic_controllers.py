# -*- coding: utf-8 -*-
"""Basic controller routines - elementary setters/getters.
Depend on models. Used by higher-order controllers."""
from contextlib import suppress
from functools import partial, wraps
from itertools import zip_longest
from .rpi2caster import CFG, UI, Abort, Finish, option
from . import basic_models as bm, definitions as d, views
from .data import WEDGE_DEFINITIONS


# Letter frequency controller routines

def define_scale(freqs):
    """Define scale of production and upper.lowercase ratio"""
    prompt = ('How much lowercase "a" characters do you want to cast?\n'
              'The quantities of other characters will be calculated\n'
              'based on the letter frequency of the language.\n'
              'Minimum of 10 characters each will be cast.')
    freqs.scale = UI.enter(prompt, default=100, datatype=int)
    prompt = 'Uppercase to lowercase ratio in %?'
    freqs.case_ratio = UI.enter(prompt, default=20.0, datatype=float) / 100.0


def get_letter_frequencies():
    """Display available languages and let user choose one.
    Returns a string with language code (e.g. en, nl, de)."""
    langs = ('{} - {}'.format(c, lang) for c, lang in sorted(d.LANGS.items()))

    # Group by three
    grouper = zip_longest(langs, langs, langs, fillvalue='')
    descriptions = '\n'.join('\t'.join(z) for z in grouper)

    UI.display('Choose language:\n\n{}\n'.format(descriptions))
    prompt = 'Language code (e.g. "en")'
    while True:
        lang = UI.enter(prompt, default=Abort, datatype=str, maximum=2)
        try:
            return bm.CharFreqs(lang)
        except KeyError:
            UI.display('Language {} not found. Choose again.'.format(lang))


# Matrix control routines

def edit_matrix(matrix, single=True):
    """Edits the matrix data.

    matrix : a Matrix class object to edit,

    edit_char : whether or not to edit the character,
    edit_position : whether or not to edit the matrix coordinates,
    edit_styles : whether or not to change the styles for the matrix,
    edit_units : whether or not to change the matrix unit value
    single : if True, editing only one matrix, else: more
             (adds an option to escape editing the whole series)
    """
    def _edit_char():
        """Edit the matrix character"""
        prompt = 'Character? (blank = keep current)'
        matrix.char = UI.enter(prompt, default=matrix.char or '')
        # if this is a space, then done
        if matrix.isspace():
            return
        # change styles
        matrix.styles = choose_styles(matrix.styles,
                                      mask=matrix.diecase.styles)

    def _edit_dimensions():
        """Edit the matrix size"""
        current_size = matrix.size
        options = [option(key='n', value=(1, 1), seq=1, text='1x1 - normal'),
                   option(key='w', value=(2, 1), seq=2, text='2x1 - wide'),
                   option(key='h', value=(1, 2), seq=3, text='1x2 - high'),
                   option(key='l', value=(2, 2), seq=4, text='2x2 - large'),
                   option(key='Enter', value=current_size, seq=5,
                          text='keep current ({})'.format(current_size))]
        new_size = UI.simple_menu('New matrix size?', options,
                                  allow_abort=False)
        matrix.size = d.MatrixSize(new_size)

    def _edit_position():
        """Edit the matrix coordinates"""
        def move_outside(new, current):
            """Move the old mat to outside characters, and replace it with
            a new mat"""
            current.code = None
            diecase.outside_mats.append(current)
            new.code = code

        def swap(new, current):
            """Swap two matrices"""
            new.code, current.code = current.code, new.code

        code = UI.enter('New position for this matrix?',
                        default=matrix.code or '').upper()
        try:
            # look for a mat in the target position
            diecase = matrix.diecase
            if not code:
                diecase.outside_mats.append(matrix)
            current_mat = diecase.select_one(code=code)
            if current_mat:
                UI.display('There is already a mat in the target position.')
                question = 'What to do with {}?'.format(current_mat)
                options = [option('s', swap, text='Swap the matrices', seq=1),
                           option('o', move_outside, seq=1,
                                  text='Remove the current matrix'),
                           option('Esc', Abort, text='Cancel')]
                UI.simple_menu(question, options)(matrix, current_mat)
            else:
                matrix.code = code
        except bm.MatrixNotFound:
            # no mat in the target position = move the mat freely
            matrix.code = code
        except Abort:
            pass

    def _edit_units():
        """Change the matrix unit width value"""
        # skip this for spaces
        if not _edit_units:
            return

        # get unit width values
        row_units = matrix.get_units_from_row()
        ua_units = matrix.get_units_from_arrangement()
        curr_units = matrix.units

        # build a prompt with units info
        curr_chunk = '' if not curr_units else 'current: {}'.format(curr_units)
        row_chunk = '' if not row_units else 'row units: {}'.format(row_units)
        ua_chunk = '' if not ua_units else 'UA units: {}'.format(ua_units)
        chunks = [x for x in (curr_chunk, row_chunk, ua_chunk) if x]
        if chunks:
            prompt = 'Enter unit width ({})'.format(', '.join(chunks))
        else:
            prompt = 'Enter unit width'
        new_units = UI.enter(prompt, default=curr_units, datatype=int,
                             minimum=3, maximum=30)
        matrix.units = new_units or ua_units or row_units

    def options():
        """Generate menu options"""
        ret = [option(key='c', value=_edit_char, seq=1,
                      text='Set the character and assign styles'),
               option(key='l', value=matrix.set_lowspace, seq=10,
                      text='Set the matrix as low space'),
               option(key='h', value=matrix.set_highspace, seq=11,
                      text='Set the matrix as high space'),
               option(key='p', value=_edit_position, seq=20,
                      text='Move the matrix to a different position'),
               option(key='w', value=_edit_units, seq=40,
                      cond=not matrix.isspace(), text='Change the unit width'),
               option(key='d', value=_edit_dimensions, seq=50,
                      text=('Change the matrix size (current: {}x{} cells)'
                            .format(*matrix.size))),
               option(key='Enter', value=Abort, seq=90,
                      text='Finish editing the matrix', cond=single),
               option(key='Enter', value=Abort, seq=90,
                      text='Edit the next matrix in series', cond=not single),
               option(key='Esc', value=Finish, seq=99, cond=not single,
                      text='Return to the layout editor menu')]
        return ret

    with suppress(Abort):
        # keep displaying this menu until aborted
        while True:
            # display the menu for user to choose
            header = 'Edit the matrix for {}:'.format(matrix)
            choice = UI.simple_menu(header, options, allow_abort=False)
            # execute the subroutine
            choice()
    return matrix


# Measure controller routines

def set_measure(input_value=CFG['Typesetting'].get('default_measure'),
                unit=CFG['Typesetting'].get('measurement_unit'),
                what='measure', set_width=12.0):
    """Enter the line length, choose measurement units
    (for e.g. British or European measurement system).
    Return length in DTP points."""
    info = ('\n\nAvailable units:\n'
            '    dd - European Didot point,\n'
            '    cc - cicero (=12dd, .1776"),\n'
            '    ff - Fournier point,\n'
            '    cf - Fournier cicero (=12ff, .1628"),\n'
            '    pp - TeX / US printer\'s pica point,\n'
            '    Pp - TeX / US printer\'s pica (=12pp, .1660"),\n'
            '    pt - DTP / PostScript point = 1/72",\n'
            '    pc - DTP / PostScript pica (=12pt, .1667"),\n'
            '    em - 18 units, en - 9 units, u - 1 unit {} set,\n'
            '    ", in - inch;   mm - millimeter;   cm - centimeter\n\n')

    prompt = 'Enter the {} value and unit (or "?" for help)'.format(what)
    while True:
        # If 0, use default
        raw_string = UI.enter(prompt, default='{}'.format(input_value))
        if '?' in raw_string:
            # Display help message and start again
            UI.display(info.format(set_width))
            continue
        try:
            return bm.Measure(raw_string, unit, set_width)
        except (TypeError, ValueError):
            UI.display('Incorrect value - enter again...')


def temp_measure(routine):
    """Decorator for casting and typesetting routines.
    Allow user to change measure i.e. line length"""
    @wraps(routine)
    def wrapper(self, *args, **kwargs):
        """Wrapper function"""
        description = 'galley width (line length)'
        # Change measure before, restore after
        old_measure = self.measure
        self.measure = set_measure(old_measure, what=description,
                                   set_width=self.wedge.set_width)
        retval = routine(self, *args, **kwargs)
        self.measure = old_measure
        return retval
    return wrapper


# Style controller routines

def choose_styles(styles='', default=None, multiple=True, mask=None):
    """Manual style choice"""
    def select(sty):
        """Selects a style - either one or multiple"""
        if not multiple:
            current.clear()
        current.add(sty)

    def deselect(sty):
        """Remove the style from currently selected"""
        current.discard(sty)

    def header():
        """Build a header"""
        text = ', '.join(s.name for s in bm.Styles.definitions if s in current)
        names = text or '{} (default)'.format(default_style.name)
        what = 'one or more text styles' if multiple else 'a text style'
        return 'Select {}.\nCurrently selected: {}'.format(what, names)

    def options():
        """Make menu entries for style selection menu"""
        items = []
        number = 1
        for sty in bm.Styles.definitions:
            text_on = 'Select {}'.format(sty.name)
            st_on = option(key=sty.short, text=text_on, seq=number,
                           value=partial(select, sty),
                           cond=sty in _mask and sty not in current)
            text_off = 'Deselect {}'.format(sty.name)
            st_off = option(key=sty.short, text=text_off, seq=number,
                            value=partial(deselect, sty),
                            cond=multiple and sty in current)
            items.extend([st_on, st_off])
            number += 1
        items.append(option(key='enter', text='Finish', value=Finish))
        return items

    # make a mask limiting the choice of styles
    _mask = bm.Styles(mask or '*')
    # what styles are currently chosen?
    default_style = bm.STYLES.get(default, d.STYLES.roman)
    current = {s for s in bm.Styles(styles, default=default_style)}
    try:
        while True:
            UI.simple_menu(header, options, allow_abort=True)()
    except Finish:
        return bm.Styles(current, default_style, _mask)


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
        return bm.Wedge(wedge_name=w_name)
    except ValueError:
        data = enter_parameters(w_name)
        return bm.Wedge(wedge_data=data)


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
