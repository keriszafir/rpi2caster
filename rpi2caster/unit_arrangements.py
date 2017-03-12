# -*- coding: utf-8 -*-
"""Font unit arrangements from Monotype information booklets
(found at Alembic Press)"""

from collections import OrderedDict
from .ui import UIFactory
from .exceptions import UnitArrangementNotFound, UnitValueNotFound
from .styles import (StylesCollection, Roman, Bold, Italic,
                     SmallCaps, Inferior, Superior)

UI = UIFactory()

# Accented letters will use the same unit arrangement value as their
# non-accented counterparts. We need a collection for determining
# which letter's variation we have.
ACCENTS = {'a': 'ąäáãâạà',
           'c': 'ćĉç',
           'e': 'ęëȩẽéêèẹ',
           'g': 'ǵĝ',
           'h': 'ḧḩĥḥ',
           'i': 'ïĩíîìị',
           'j': 'j́ĵ',
           'k': 'ķḱḳ',
           'l': 'łļĺḷ',
           'm': 'ḿṃ',
           'n': 'ńņñǹṇ',
           'o': 'óöõôòọ',
           'p': 'þṕ',
           'q': '',
           'r': 'ŗŕṛ',
           's': 'śşŝṣ',
           't': 'ţẗṭ',
           'u': 'üũúûùụǘǜ',
           'v': 'ṽṿ',
           'w': 'ẅẃŵẁẉ',
           'x': 'ẍ',
           'y': 'ÿỹýŷỳỵ',
           'z': 'żźẑẓ'}

# Add accents for upper-case characters
for unaccented_char in [char for char in ACCENTS]:
    ACCENTS[unaccented_char.upper()] = ACCENTS.get(unaccented_char).upper()

# Ligatures are multiple-character glyphs, using a single matrix,
# cast as a single sort of type. Typical ligatures listed below, with
# a possibility of adding more in the future. We never know everything.
# Not all ligatures are present in capitals or small caps (e.g. f-ligatures
# are lowercase only).
LIGATURES = ['ae', 'oe', 'AE', 'OE', 'fi', 'fl', 'ff', 'fb', 'fh', 'fk',
             'fj', 'ffi', 'ffl', 'ij', 'IJ', 'st', 'ct']

# Define unit arrangements for the fonts
# This may in future be stored in data files (JSON-encoded?)
UA = {'0': {Roman: {}, Bold: {}, Italic: {}, SmallCaps: {},
            Inferior: {}, Superior: {}},
      '82': {Roman: {5: ['f', 'i', 'I', 'j', 'J', 'l'],
                     6: [],
                     7: ['s', 't'],
                     8: ['a', 'c', 'r', 'z'],
                     9: ['e', 'F', 'g', 'S', 'v', 'y',
                         '1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
                     10: ['b', 'd', 'E', 'h', 'k', 'L', 'n', 'o', 'P', 'p',
                          'q', 'u', 'x', 'ff', 'fi', 'fl'],
                     11: ['B', 'T'],
                     12: ['R', 'V', 'Y', 'ae'],
                     13: ['A', 'C', 'K', 'Z', '&'],
                     14: ['D', 'G', 'H', 'U', 'w', 'X'],
                     15: ['M', 'm', 'N', 'O', 'Q', 'oe', 'ffi', 'ffl'],
                     17: ['AE', 'OE'],
                     20: ['W']}},
      '93': {Roman: {5: [],
                     6: ['f', 'i', 'j', 'l'],
                     7: ['I', 'J'],
                     8: ['s', 't'],
                     9: ['c', 'r',
                         '1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
                     10: ['a', 'e', 'g', 'v', 'y', 'z', 'fl'],
                     11: ['b', 'd', 'F', 'h', 'k', 'n', 'o', 'p', 'q', 'S',
                          'u', 'x', 'fi'],
                     12: ['E', 'L', 'P', 'ff'],
                     13: ['B', 'R', 'T'],
                     14: ['C', 'K', 'V', 'Y', 'Z', '&', 'ae'],
                     15: ['A', 'D', 'G', 'w'],
                     16: ['H', 'N', 'O', 'Q', 'U', 'X', 'oe'],
                     17: ['M', 'ffi', 'ffl'],
                     18: ['m', 'W', 'OE'],
                     20: ['AE', 'OE'],
                     22: ['W']}},
      '311': {Italic: {5: ['I', 'i', 'J', 'j', 'l'],
                       6: ['f', 't'],
                       7: ['r', 's'],
                       8: ['c', 'e', 'F', 'L', 'o', 'S', 'v', 'y'],
                       9: ['a', 'b', 'd', 'g', 'h', 'k', 'n', 'P', 'p', 'q',
                           'u', 'x', 'z', 'fi', 'fl',
                           '1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
                       10: ['A', 'B', 'E', 'R', 'T', 'V', 'Y'],
                       11: ['C', 'K', 'ff'],
                       12: ['D', 'G', 'O', 'Q', 'U', 'w', 'Z', 'ae', '&'],
                       13: ['H', 'N', 'X', 'oe'],
                       14: ['m', 'ffi', 'ffl'],
                       15: ['M'],
                       16: ['AE'],
                       18: ['W', 'OE']}},
      '324': {Roman: {5: ['i', 'j', 'l'],
                      6: ['f', 't'],
                      7: ['I', 'r', 's'],
                      8: ['c', 'e', 'v', 'z'],
                      9: ['a', 'b', 'd', 'g', 'h', 'n', 'o', 'p', 'q', 'u',
                          'y',
                          '1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
                      10: ['J', 'k', 'x', 'fi', 'fl'],
                      11: ['F', 'S', 'ae', 'oe', 'ff'],
                      12: ['B', 'E', 'L', 'P', 'T', 'w', '&'],
                      13: ['A', 'C', 'K', 'R', 'V', 'X', 'Y', 'Z'],
                      14: ['D', 'G', 'm', 'N', 'U'],
                      15: ['H', 'O', 'Q', 'ffi', 'ffl'],
                      18: ['M', 'W', 'AE', 'OE']}},
      '325': {Roman: {5: ['i', 'j', 'l'],
                      6: ['f', 't'],
                      7: ['I', 'r', 's'],
                      8: ['c', 'e', 'J', 'z'],
                      9: ['a', 'g', 'v', 'x', 'y',
                          '1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
                      10: ['b', 'd', 'h', 'k', 'n', 'o', 'p', 'q', 'S', 'u',
                           'fi', 'fl'],
                      11: ['P', 'ff'],
                      12: ['B', 'E', 'F', 'L', 'T', 'Z', 'ae'],
                      13: ['C', 'V', 'w', 'oe'],
                      14: ['A', 'O', 'Q', 'R', 'X', 'Y', '&'],
                      15: ['D', 'G', 'H', 'K', 'm', 'N', 'U', 'ffi', 'ffl'],
                      18: ['M', 'W', 'AE', 'OE']},
              Italic: {5: ['i', 'j', 'l'],
                       6: ['f', 't'],
                       7: ['I', 'r', 's'],
                       8: ['c', 'e', 'v', 'z'],
                       9: ['a', 'b', 'd', 'g', 'h', 'n', 'o', 'p', 'q', 'u',
                           'y', 'J'
                           '1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
                       10: ['k', 'x', 'fi', 'fl'],
                       11: ['F', 'S', 'ae', 'oe', 'ff'],
                       12: ['B', 'E', 'L', 'P', 'T', 'w'],
                       13: ['A', 'C', 'G', 'K', 'R', 'V', 'X', 'Y', 'Z', '&'],
                       14: ['D', 'm', 'N', 'O', 'Q', 'U'],
                       15: ['H', 'ffi', 'ffl'],
                       18: ['M', 'W', 'AE', 'OE']},
              SmallCaps: {5: ['i'],
                          6: ['j'],
                          7: ['s'],
                          8: ['e', 'f'],
                          9: ['b', 'l', 'p', 't'],
                          10: ['a', 'c', 'o', 'q', 'r', 'v', 'x', 'y', 'z'],
                          11: ['d', 'g', 'h', 'k', 'n', 'u'],
                          12: ['m'],
                          13: ['ae'],
                          14: ['oe'],
                          15: ['w']}}}


def get_unit_value(ua_id, char, styles):
    """Get an unit value for a given character and style."""
    # Get the unit arrangement for a given style
    # Caveat: some arrangements are used for bold etc. (non-regular) styles,
    # but are defined only for roman. If no arrangement for a given style
    # is found, try using roman instead.
    unit_arrangement = OrderedDict()
    for number, uas in UA.items():
        if str(number) == str(ua_id):
            unit_arrangement = OrderedDict(uas)
            break
    else:
        raise UnitArrangementNotFound
    # Get the unit arrangement for the particular style
    style_ua = {}
    for style in styles:
        style_ua = unit_arrangement.get(style)
        if style_ua:
            break
    else:
        try:
            # styles is a StylesCollection object
            default_style = styles.default
        except AttributeError:
            default_style = Roman
        style_ua = unit_arrangement.get(default_style)
        if not style_ua:
            raise UnitArrangementNotFound
    # Look up the character in accents
    for letter, accents_string in ACCENTS.items():
        if char in accents_string:
            # Get a non-accented letter and use its unit value
            char = letter
            break
    # Otherwise, char is not a known accent
    # Now look up the unit value for the character
    for unit_value, character_list in style_ua.items():
        if char in character_list:
            return unit_value
    # Falling off the loop means nothing is found - raise exception
    raise UnitValueNotFound


def ua_by_style(styles='', current_mapping=None):
    """Ask for styles and assign them a unit arrangement.
    Return a list of tuples: [(style1, ua1), (style2, ua2)...]
    for each style in styles_string (if called without arguments,
    let user choose the styles manually)"""
    current_mapping = current_mapping or {}
    style_mgr = StylesCollection(styles)
    mapping = {}
    ua_numbers = ', '.join([x for x in sorted(UA)])
    UI.display('Known unit arrangements:\n%s' % ua_numbers)
    for style in style_mgr:
        prompt = 'UA number for %s?' % style.name
        current = current_mapping.get(style)
        if current:
            # change a UA to something new
            ua_number = UI.enter(prompt, default=current, datatype=int)
        else:
            # no pre-existing mapping
            ua_number = UI.enter(prompt, blank_ok=True, datatype=int)
        if ua_number:
            mapping[style] = ua_number
    current_mapping.update(mapping)
    return current_mapping


def char_unit_values(mapping):
    """Get a dictionary of unit values based on style-to-UA assignment.
    mapping - a dictionary {Style: UA_number}."""
    data = OrderedDict({})
    for style, ua_number in mapping.items():
        # Look for the style in UA; if not found, fall back to roman
        unit_arrangement = UA.get(ua_number)
        if not unit_arrangement:
            continue
        # Lookup the style
        units_dict = unit_arrangement.get(style)
        # Found no unit values (e.g. looked for roman in italic-only UA)?
        # End here.
        if not units_dict:
            continue
        style_dict = {character: unit_value for unit_value in units_dict
                      for character in units_dict.get(unit_value, {})}
        # Add the style character unit values to the collected data dict
        if style_dict:
            data[style] = style_dict
    # {Roman: {'a': 9, 'M': 18...}, Italic: {'a': 7,...}}
    return data


def display_unit_values(mapping=None):
    """Print a list on the screen with unit values for each character.
    Use a [(style1, ua1), (style2, ua2)] mapping.
    If mapping is not provided, user will choose style manually."""
    mapping = mapping or ua_by_style()
    source = char_unit_values(mapping)
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    digits = '0123456789'
    characters = [x for x in alphabet + alphabet.upper() + digits] + LIGATURES
    # Unit values by styles and chars
    # character     roman    bold     italic
    fields = ['Character']
    fields.extend(style.name for style in source)
    header = ''.join(name.ljust(15) for name in fields)
    # Display the data for characters
    UI.display('Unit values for characters:\n')
    UI.display(header)
    UI.display('-' * len(header))
    for char in characters:
        row = ''.join([char.ljust(15)] +
                      [str(ua.get(char, '')).ljust(15)
                       for style, ua in source.items()])
        UI.display(row)
    UI.display('\n\nCharacters by unit value:\n')
    # By unit values, then character
    for units in range(4, 25):
        strings = []
        for style in source:
            chars = ', '.join([char for char in characters
                               if source[style].get(char) == units])
            if chars:
                strings.append('%s : %s' % (style.name, chars))
        if strings:
            UI.display('\n\nCharacters %s units wide:' % units)
            UI.display('\n'.join(strings))
