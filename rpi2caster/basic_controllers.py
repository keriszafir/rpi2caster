# -*- coding: utf-8 -*-
"""Basic controller routines - elementary setters/getters.
Depend on models. Used by higher-order controllers."""

from contextlib import suppress
from functools import wraps
from itertools import zip_longest
from string import ascii_lowercase, ascii_uppercase, digits
from .rpi2caster import CFG, UI, Abort, Finish, option
from . import basic_models as bm, definitions as d
from .data import TYPEFACES, WEDGE_DEFINITIONS


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

def edit_matrix(matrix,
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
        matrix.char = UI.enter(prompt, default=matrix.char or '')

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
        if not edit_position:
            return
        matrix.code = UI.enter('Enter the matrix position',
                               default=matrix.code or '')
        # reset the unit width
        if not matrix.char or matrix.isspace():
            matrix.units = 0

    def _edit_styles():
        """Change the matrix styles"""
        # skip this for spaces
        if not edit_styles or matrix.isspace():
            return
        matrix.styles = choose_styles(matrix.styles)

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
        new_units = UI.enter(prompt, default=curr_units, datatype=int)
        matrix.units = new_units or ua_units or row_units

    with suppress(Abort):
        # keep displaying this menu until aborted
        while True:
            # generate menu options dynamically
            options = [option(key='c', value=_edit_char, seq=1,
                              lazy=_get_char, cond=edit_char,
                              text='change character (current: {})'),
                       option(key='p', value=_edit_position, seq=2,
                              lazy=matrix.code, cond=edit_position,
                              text='change position (current: {})'),
                       option(key='s', value=_edit_styles, seq=3,
                              lazy=matrix.styles.names,
                              cond=(edit_styles and matrix.char and not
                                    matrix.isspace()),
                              text='assign styles (current: {})'),
                       option(key='w', value=_edit_units, seq=4,
                              lazy=matrix.units,
                              cond=edit_units and not matrix.isspace(),
                              text='change width (current: {} units)'),
                       option(key='d', value=_edit_dimensions, seq=5,
                              text='change matrix size (current: {})',
                              lazy='{}x{}'.format(*matrix.size)),
                       option(key='Enter', value=Abort, seq=90,
                              text='done editing'),
                       option(key='Esc', value=Finish, seq=99,
                              text='finish')]
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
                                        .format(_get_char(), matrix.code),
                                        options, allow_abort=False)
            # execute the subroutine
            choice()
    return matrix


# Typeface controller routines

def list_typefaces(*_):
    """Show all available typefaces"""
    template = '{num:>6}\t{name:<30}\t{styles}'
    UI.display_header('List of known typefaces by series number:')
    UI.display('Series\t{:<30}\tStyles'.format('Name'))
    for number, record in sorted(TYPEFACES.items()):
        name = record.get('typeface')
        if not name:
            continue
        styles = bm.Styles(record.get('styles', 'r')).names
        entry = template.format(num=number, name=name, styles=styles)
        UI.display(entry)
    UI.pause()


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

def choose_styles(styles='*', default=d.STYLES.roman, multiple=True):
    """Manual style choice"""
    styles_string = str(styles) if styles else ''
    if multiple:
        header = 'Choose one or more text styles.'
        all_styles = ',\na or * - all styles.\n'
    else:
        header = 'Choose a style.'
        all_styles = '.\n'
    prompt = ('{} Available options:\n'
              'r - roman/regular, b - bold, i - italic, s - small caps,\n'
              'l - lower index (inferior), u - upper index (superior),\n'
              's1...s5 - size 1...size 5 (titling){}'
              'Your choice?'.format(header, all_styles))
    result = UI.enter(prompt, default=styles_string, datatype=str)
    if not multiple:
        result = result[:1]
    return bm.Styles(result, default)


# Unit arrangement controller routines

def display_ua(unit_arrangement):
    """Show an unit arrangement by char and by units"""
    def display_by_units():
        """display chars grouped by unit value"""
        UI.display('Ordered by unit value:')
        for unit_value, chars in sorted(unit_arrangement.by_units.items()):
            char_string = ', '.join(sorted(chars))
            UI.display('\t{}:\t{}'.format(unit_value, char_string))
        UI.display()

    def display_letters():
        """display unit values for all letters and ligatures"""
        # define templates for lower+uppercase, lowercase only, uppercase only
        template = '\t{:<4}: {:>3} units, \t\t{:<4}: {:>3} units'
        lc_template = '\t{:<4}: {:>3} units'
        uc_template = '\t\t\t{:<4}: {:>3} units'

        UI.display('Ordered by character:')
        for lowercase in [*ascii_lowercase, *d.LIGATURES]:
            uppercase = lowercase.upper()
            with suppress(bm.UnitValueNotFound):
                # display both lower and upper
                lower_units = unit_arrangement[lowercase]
                upper_units = unit_arrangement[uppercase]
                UI.display(template.format(lowercase, lower_units,
                                           uppercase, upper_units))
                continue
            with suppress(bm.UnitValueNotFound):
                # display lowercase only
                lower_units = unit_arrangement[lowercase]
                UI.display(lc_template.format(lowercase, lower_units))
                continue
            with suppress(bm.UnitValueNotFound):
                # display uppercase only
                lower_units = unit_arrangement[uppercase]
                UI.display(uc_template.format(uppercase, upper_units))
                continue
        UI.display()

    def display_numbers():
        """display 0...9 unit values"""
        grouped = {units: [n for n in digits if unit_arrangement[n] == units]
                   for units in range(5, 22)}
        numbers = [(', '.join(chars), units)
                   for units, chars in grouped.items() if chars]
        if numbers:
            chunks = ('{}: {} units'.format(c, u) for c, u in numbers)
            row = 'Digits: {}'.format(', '.join(chunks))
            UI.display(row)

    def display_others():
        """display other characters - not letters"""
        done = [*ascii_lowercase, *ascii_uppercase, *digits, *d.LIGATURES]
        other_chars = {u: [c for c in sorted(set(chars).difference(done))]
                       for u, chars in unit_arrangement.by_units.items()}
        others = [(', '.join(chars), units)
                  for units, chars in sorted(other_chars.items()) if chars]
        if others:
            chunks = ('{}: {} units'.format(c, u) for c, u in others)
            row = 'Other: {}'.format(', '.join(chunks))
            UI.display(row)

    header = ('Unit arrangement for {ua.style.name}: '
              '#{ua.number} {ua.variant.name}')
    UI.display_header(header.format(ua=unit_arrangement))
    display_by_units()
    display_letters()
    display_numbers()
    display_others()


# Wedge controller routines

def choose_wedge(wedge_name=None):
    """Choose a wedge manually"""
    def enter_name():
        """Enter the wedge's name"""
        # Ask for wedge name and set width as it is written on the wedge
        aliases = iter(d.WEDGE_ALIASES)
        # Group by three
        grouper = zip_longest(aliases, aliases, aliases, fillvalue='')
        old_wedges = '\n'.join('\t'.join(z) for z in grouper)
        prompt = ('\nSome old-style wedge designations:\n\n{}'
                  '\n\nIf you have one of those, '
                  'enter the corresponding new-style number (like S5-xx.yE).'
                  '\n\nWedge designation?'.format(old_wedges))
        return UI.enter(prompt, default=default_wedge)

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
