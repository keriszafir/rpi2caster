# -*- coding: utf-8 -*-
"""Basic controller routines - elementary setters/getters.
Depend on models. Used by higher-order controllers."""

from functools import wraps
from itertools import zip_longest
from . import basic_models as bm, definitions as d
from .config import CFG
from .ui import UI, Abort
from .wedge_units import UNITS, ALIASES as wedge_name_aliases

PREFS_CFG = CFG.Preferences


# Letter frequency controller routines

def define_scale(freqs):
    """Define scale of production"""
    prompt = ('How much lowercase "a" characters do you want to cast?\n'
              'The quantities of other characters will be calculated\n'
              'based on the letter frequency of the language.\n'
              'Minimum of 10 characters each will be cast.')
    freqs.scale = UI.enter(prompt, default=100, datatype=int)


def define_case_ratio(freqs):
    """Define uppercase to lowercase ratio"""
    prm = 'Uppercase to lowercase ratio in %?'
    freqs.case_ratio = UI.enter(prm, default=20.0, datatype=float) / 100.0


def get_letter_frequencies():
    """Display available languages and let user choose one.
    Returns a string with language code (e.g. en, nl, de)."""
    lang_it = ('{} - {}'.format(lang, bm.CharFreqs.langs[lang])
               for lang in sorted(bm.CharFreqs.langs))

    # Group by three
    grouper = zip_longest(lang_it, lang_it, lang_it, fillvalue='')
    descriptions = '\n'.join('\t'.join(z) for z in grouper)

    UI.display('Choose language:\n\n{}\n'.format(descriptions))
    prompt = 'Language code (e.g. "en")'
    while True:
        lang = UI.enter(prompt, default=Abort, datatype=str, maximum=2)
        try:
            return bm.CharFreqs(lang)
        except KeyError:
            UI.display('Language {} not found. Choose again.'.format(lang))


# Measure controller routines

def enter_measure(input_value=PREFS_CFG.default_measure,
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
            '    em - 18 units, en - 9 units, u - 1 unit wedge\'s set,\n'
            '    ", in - inch;   mm - millimeter;   cm - centimeter\n\n')

    prompt = 'Enter the {} value and unit (or "?" for help)'.format(what)
    default_measure = bm.Measure(input_value, PREFS_CFG.measurement_unit)
    while True:
        # If 0, use default
        raw_string = UI.enter(prompt, default='{}'.format(default_measure))
        if '?' in raw_string:
            # Display help message and start again
            UI.display(info)
        try:
            return bm.Measure(raw_string, PREFS_CFG.measurement_unit,
                              set_width=set_width)
        except (TypeError, ValueError):
            UI.display('Incorrect value - enter again...')


def temp_measure(routine):
    """Decorator for casting and typesetting routines.
    Allow user to change measure i.e. line length"""
    @wraps(routine)
    def wrapper(self, *args, **kwargs):
        """Wrapper function"""
        prompt = 'Current measure is {}, change it?'.format(self.measure)
        description = 'line length / galley width'
        if UI.confirm(prompt, default=False):
            # Change measure before, restore after
            old_measure = self.measure
            self.measure = enter_measure(old_measure, description)
            retval = routine(self, *args, **kwargs)
            self.measure = old_measure
            return retval
        else:
            # Just do it
            return routine(self, *args, **kwargs)
    return wrapper


# Style controller routines

def choose_styles(styles='*', default=d.STYLES.roman, multiple=True):
    """Manual style choice"""
    styles_string = str(styles)
    if multiple:
        header = 'Choose one or more text styles.'
        all_styles = ',\na or * - all styles.\n'
    else:
        header = 'Choose a style.'
        all_styles = '.\n'
    prompt = ('{} Available options:\n'
              'r - roman, b - bold, i - italic, s - small caps,\n'
              'l - lower index (inferior), u - upper index (superior){}'
              'Your choice?'.format(header, all_styles))
    result = UI.enter(prompt, default=styles_string, datatype=str)
    if not multiple:
        result = result[:1]
    return bm.Styles(result, default)


# Wedge controller routines

def choose_wedge(wedge_name=None):
    """Choose a wedge manually"""
    def enter_name():
        """Enter the wedge's name"""
        # Ask for wedge name and set width as it is written on the wedge
        aliases = iter(wedge_name_aliases)
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
        current_units = UNITS.get(series, d.S5)
        prompt = ('Enter the wedge unit values for rows 1...15 '
                  'or 1...16, separated by commas.\n')
        units = UI.enter(prompt, default=current_units, minimum=15, maximum=16)
        # Now we have the data...
        return {'series': series, 'set_width': set_width,
                'is_brit_pica': is_brit_pica, 'units': units}

    default_wedge = str(wedge_name) if wedge_name else 'S5-12E'
    w_name = enter_name()
    try:
        return bm.Wedge(w_name)

    except ValueError:
        data = enter_parameters(w_name)
        wedge = bm.Wedge()
        wedge.load(data)
        return wedge


def temp_wedge(routine):
    """Decorator for typesetting and casting routines.
    Assign a temporary alternative wedge for casting/calibration"""
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
