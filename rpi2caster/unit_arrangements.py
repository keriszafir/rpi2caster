# -*- coding: utf-8 -*-
"""Font unit arrangements from Monotype information booklets
(found at Alembic Press)"""

from .exceptions import UnitArrangementNotFound, UnitValueNotFound
from .styles import Styles
from .global_config import UI

# Accented letters will use the same unit arrangement value as their
# non-accented counterparts. We need a collection for determining
# which letter's variation we have.
ACCENTS = {'a': ['ą', 'ä', 'á', 'ã', 'â', 'ạ', 'à'],
           'c': ['ć', 'ĉ', 'ç'],
           'e': ['ę', 'ë', 'ȩ', 'ẽ', 'é', 'ê', 'è', 'ẹ'],
           'g': ['ǵ', 'ĝ'],
           'h': ['ḧ', 'ḩ', 'ĥ', 'ḥ'],
           'i': ['ï', 'ĩ', 'í', 'î', 'ì', 'ị'],
           'j': ['j́', 'ĵ'],
           'k': ['ķ', 'ḱ', 'ḳ'],
           'l': ['ł', 'ļ', 'ĺ', 'ḷ'],
           'm': ['ḿ', 'ṃ'],
           'n': ['ń', 'ņ', 'ñ', 'ǹ', 'ṇ'],
           'o': ['ó', 'ö', 'õ', 'ô', 'ò', 'ọ'],
           'p': ['þ', 'ṕ'],
           'q': [],
           'r': ['ŗ', 'ŕ', 'ṛ'],
           's': ['ś', 'ş', 'ŝ', 'ṣ'],
           't': ['ţ', 'ẗ', 'ṭ'],
           'u': ['ü', 'ũ', 'ú', 'û', 'ù', 'ụ', 'ǘ', 'ǜ'],
           'v': ['ṽ', 'ṿ'],
           'w': ['ẅ', 'ẃ', 'ŵ', 'ẁ', 'ẉ'],
           'x': ['ẍ'],
           'y': ['ÿ', 'ỹ', 'ý', 'ŷ', 'ỳ', 'ỵ'],
           'z': ['ż', 'ź', 'ẑ', 'ẓ']}

# Define unit arrangements for the fonts
# This may in future be stored in data files (JSON-encoded?)
UA = {'82': {'r': {5: ['f', 'i', 'I', 'j', 'J', 'l'],
                   6: [],
                   7: ['s', 't'],
                   8: ['a', 'c', 'r', 'z'],
                   9: ['e', 'F', 'g', 'S', 'v', 'y',
                       '1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
                   10: ['b', 'd', 'E', 'h', 'k', 'L', 'n', 'o', 'P', 'p', 'q',
                        'u', 'x', 'ff', 'fi', 'fl'],
                   11: ['B', 'T'],
                   12: ['R', 'V', 'Y', 'ae'],
                   13: ['A', 'C', 'K', 'Z', '&'],
                   14: ['D', 'G', 'H', 'U', 'w', 'X'],
                   15: ['M', 'm', 'N', 'O', 'Q', 'oe', 'ffi', 'ffl'],
                   17: ['AE', 'OE'],
                   20: ['W']}},
      '93': {'r': {5: [],
                   6: ['f', 'i', 'j', 'l'],
                   7: ['I', 'J'],
                   8: ['s', 't'],
                   9: ['c', 'r',
                       '1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
                   10: ['a', 'e', 'g', 'v', 'y', 'z', 'fl'],
                   11: ['b', 'd', 'F', 'h', 'k', 'n', 'o', 'p', 'q', 'S', 'u',
                        'x', 'fi'],
                   12: ['E', 'L', 'P', 'ff'],
                   13: ['B', 'R', 'T'],
                   14: ['C', 'K', 'V', 'Y', 'Z', '&', 'ae'],
                   15: ['A', 'D', 'G', 'w'],
                   16: ['H', 'N', 'O', 'Q', 'U', 'X', 'oe'],
                   17: ['M', 'ffi', 'ffl'],
                   18: ['m', 'W', 'OE'],
                   20: ['AE', 'OE'],
                   22: ['W']}},
      '311': {'i': {5: ['I', 'i', 'J', 'j', 'l'],
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
      '324': {'r': {5: ['i', 'j', 'l'],
                    6: ['f', 't'],
                    7: ['I', 'r', 's'],
                    8: ['c', 'e', 'v', 'z'],
                    9: ['a', 'b', 'd', 'g', 'h', 'n', 'o', 'p', 'q', 'u', 'y',
                        '1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
                    10: ['J', 'k', 'x', 'fi', 'fl'],
                    11: ['F', 'S', 'ae', 'oe', 'ff'],
                    12: ['B', 'E', 'L', 'P', 'T', 'w', '&'],
                    13: ['A', 'C', 'K', 'R', 'V', 'X', 'Y', 'Z'],
                    14: ['D', 'G', 'm', 'N', 'U'],
                    15: ['H', 'O', 'Q', 'ffi', 'ffl'],
                    18: ['M', 'W', 'AE', 'OE']}},
      '325': {'r': {5: ['i', 'j', 'l'],
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
              'i': {5: ['i', 'j', 'l'],
                    6: ['f', 't'],
                    7: ['I', 'r', 's'],
                    8: ['c', 'e', 'v', 'z'],
                    9: ['a', 'b', 'd', 'g', 'h', 'n', 'o', 'p', 'q', 'u', 'y',
                        '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'J'],
                    10: ['k', 'x', 'fi', 'fl'],
                    11: ['F', 'S', 'ae', 'oe', 'ff'],
                    12: ['B', 'E', 'L', 'P', 'T', 'w'],
                    13: ['A', 'C', 'G', 'K', 'R', 'V', 'X', 'Y', 'Z', '&'],
                    14: ['D', 'm', 'N', 'O', 'Q', 'U'],
                    15: ['H', 'ffi', 'ffl'],
                    18: ['M', 'W', 'AE', 'OE']},
              's': {5: ['i'],
                    6: ['j'],
                    7: ['s'],
                    8: ['e', 'f'],
                    9: ['b', 'l', 'p', 't'],
                    10: ['a', 'c', 'o', 'q', 'r', 'v', 'x', 'y', 'z'],
                    11: ['d', 'g', 'h', 'k', 'n', 'u'],
                    12: ['m'],
                    13: ['AE'],
                    14: ['OE'],
                    15: ['W']}}}


def get_unit_value(ua_id, char, style):
    """Get an unit value for a given character and style."""
    arrangement = UA.get(str(ua_id)).get(style)
    if not arrangement:
        raise UnitArrangementNotFound
    # Look up the character in accents
    if char in ACCENTS:
        lookup_character = char
    else:
        for letter in ACCENTS:
            if char in ACCENTS[letter]:
                lookup_character = letter
                break
    # Now look up the unit value for the character
    for unit_value in arrangement:
        if lookup_character in arrangement[unit_value]:
            retval = unit_value
            break
    else:
        raise UnitValueNotFound
    return retval


def ua_by_style(styles_string=''):
    """Ask for styles and assign them a unit arrangement"""
    styles = Styles(styles_string, allow_multiple=True)
    mapping = []
    ua_numbers = ', '.join([x for x in sorted(UA)])
    UI.display('Known unit arrangements:\n%s' % ua_numbers)
    for style in styles:
        while True:
            prompt = 'UA number for %s?' % Styles.style_dict.get(style)
            ua_number = UI.enter_data_or_blank(prompt)
            if not ua_number:
                break
            elif ua_number in UA:
                mapping.append((style, ua_number))
                break
    return mapping


def char_unit_values(mapping):
    """Get a dictionary of unit values based on style-to-UA assignment"""
    data = {}
    for style, ua_number in mapping:
        # Look for the style in UA; if not found, fall back to roman
        unit_arrangement = UA.get(ua_number)
        if not unit_arrangement:
            continue
        # Lookup the style or default roman
        units_dict = unit_arrangement.get(style) or unit_arrangement.get('r')
        # Found no unit values (e.g. looked for roman in italic-only UA)?
        # End here.
        if not units_dict:
            continue
        style_dict = {}
        for unit_value in units_dict:
            for character in units_dict[unit_value]:
                style_dict[character] = unit_value
        # Add the style character unit values to the collected data dict
        if style_dict:
            data[style] = style_dict
    # {r: {'a': 9, 'M': 18...}}
    return data


def display_unit_values(mapping=None):
    """Print a list on the screen with unit values for each character"""
    mapping = mapping or ua_by_style()
    styles = [x for (x, y) in mapping]
    source = char_unit_values(mapping)
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    digits = '0123456789'
    ligatures = ['ae', 'oe', 'AE', 'OE', 'fi', 'fl', 'ff', 'fb', 'fh', 'fk',
                 'fj', 'ffi', 'ffl', 'ij', 'IJ', 'st', 'ct']
    charset = alphabet + alphabet.upper() + digits
    charset = [x for x in charset]
    charset.extend(ligatures)
    # Unit values by styles and chars
    header = ('Character'.ljust(15) +
              ''.join([Styles.style_dict.get(style).ljust(15)
                       for style in styles]))
    # Display the data for characters
    UI.display('Unit values for characters:\n')
    UI.display(header)
    UI.display('-' * len(header))
    for char in charset:
        row = ''.join([char.ljust(15)] +
                      [str(source.get(style, {}).get(char)).ljust(15)
                       for style in styles])
        UI.display(row)
    UI.display('\n\nCharacters by unit value:\n')
    # By unit values, then character
    for units in range(4, 25):
        strings = []
        for style in 'rbislu':
            chars = ', '.join([char for char in charset
                               if source.get(style, {}).get(char) == units])
            if chars:
                style_name = Styles.style_dict.get(style)
                strings.append('%s : %s' % (style_name, chars))
        if strings:
            UI.display('\n\nCharacters %s units wide:' % units)
            UI.display('\n'.join(strings))
