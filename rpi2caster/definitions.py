# -*- coding: utf-8 -*-
"""Constant and basic data structure definitions"""

from collections import namedtuple

# define some namedtuple objects so that returning data is easier
# namedtuple for matrix coordinates
Coordinates = namedtuple('Coordinates', 'column row')
# some parameter namedtuples for records
Settings = namedtuple('Settings',
                      'row_16_mode explicit_o15 add_missing_o15')
Content = namedtuple('Content',
                     ('original_entry raw_signals comment '
                      'justification columns rows use_s_needle'))
Report = namedtuple('Report',
                    ('has_signals uses_row_16 has_0005 has_0075 '
                     'is_pump_start is_pump_stop is_pump_hold '
                     'is_newline is_char'))
# menu item namedtuple
MenuItem = namedtuple('MenuItem',
                      'key value condition lazy text description seq')
# Standard keyboard combinations
Key = namedtuple('Key', 'getchar name')
# template for style definitions
Style = namedtuple('Style', 'name alternatives short codes ansi')
SD = namedtuple('StyleDefinitions',
                ('roman bold italic smallcaps inferior superior '
                 'size1 size2 size3 size4 size5'))

# Configuration namedtuple definitions
Preferences = namedtuple('Preferences', 'default_measure measurement_unit')
Interface = namedtuple('Interface',
                       ('sensor output choose_backend sensor_gpio '
                        'emergency_stop_gpio signals_arrangement '
                        'mcp0 mcp1 pin_base i2c_bus bounce_time'))

# Style definitions
STYLES = SD(roman=Style(name='roman', short='r',
                        alternatives='regular, antiqua',
                        codes=('^rr', '^RR', '^00'), ansi=0),
            italic=Style(name='italic', short='i', alternatives=0,
                         codes=('^ii', '^II', '^01'), ansi=3),
            bold=Style(name='bold', short='b', alternatives='',
                       codes=('^bb', '^BB', '^03'), ansi=1),
            smallcaps=Style(name='small caps', short='s', alternatives='',
                            codes=('^sc', '^ss', '^SC', '^SS', '^02'), ansi=4),
            inferior=Style(name='inferior', short='l',
                           alternatives='lower index, subscript',
                           codes=('^ll', '^LL', '^05'), ansi=33),
            superior=Style(name='superior', short='u',
                           alternatives='upper index, superscript',
                           codes=('^uu', '^UU', '^04'), ansi=35),
            size1=Style(name='size 1', short='1', ansi=0,
                        alternatives='', codes=('^s1')),
            size2=Style(name='size 2', short='2', ansi=0,
                        alternatives='', codes=('^s2')),
            size3=Style(name='size 3', short='3', ansi=0,
                        alternatives='', codes=('^s3')),
            size4=Style(name='size 4', short='4', ansi=0,
                        alternatives='', codes=('^s4')),
            size5=Style(name='size 5', short='5', ansi=0,
                        alternatives='', codes=('^s5')))

# Constants for control codes
STYLE_COMMANDS = {'^00': 'r', '^rr': 'r', '^01': 'i', '^ii': 'i',
                  '^02': 'b', '^bb': 'b', '^03': 's', '^ss': 's',
                  '^04': 'l', '^ll': 'l', '^05': 'u', '^uu': 'u'}
ALIGNMENTS = {'^CR': 'left', '^CC': 'center', '^CL': 'right', '^CF': 'both'}

# Default space positions
DEFAULT_LOW_SPACE_POSITIONS = (('G', 1), ('G', 2), ('G', 5), ('O', 15))
DEFAULT_HIGH_SPACE_POSITIONS = (('O', 16))
# Names for low and high spaces, depending on their width
SPACE_NAMES = {'   ': 'low em quad', '  ': 'low en quad', ' ': 'low space',
               '___': 'high em quad', '__': 'high en quad', '_': 'high space'}

# Measurement units for line length
TYPOGRAPHIC_UNITS = dict(pc=12.0, pt=1.0, Pp=12*0.166/0.1667, pp=0.166/0.1667,
                         cc=12*0.1776/0.1667, dd=0.1776/0.1667,
                         cf=12*0.1628/0.1667, ff=0.1628/0.1667,
                         cm=0.3937*72, mm=0.03937*72)
TYPOGRAPHIC_UNITS['in'] = TYPOGRAPHIC_UNITS['"'] = 72.0

# S5 wedge unit values
S5 = [5, 6, 7, 8, 9, 9, 9, 10, 10, 11, 12, 13, 14, 15, 18]

# Accented letters will use the same unit arrangement value as their
# non-accented counterparts.
ACCENTS = dict(a='ąäáãâạà', c='ćĉç', e='ęëȩẽéêèẹ', g='ǵĝ', h='ḧḩĥḥ',
               i='ïĩíîìị', j='j́ĵ', k='ķḱḳ', l='łļĺḷ', m='ḿṃ', n='ńņñǹṇ',
               o='óöõôòọ', p='þṕ', r='ŗŕṛ', s='śşŝṣ', t='ţẗṭ', u='üũúûùụǘǜ',
               v='ṽṿ', w='ẅẃŵẁẉ', x='ẍ', y='ÿỹýŷỳỵ', z='żźẑẓ')
ACCENTS.update({letter.upper(): ACCENTS[letter].upper() for letter in ACCENTS})

# Typical ligatures:
LIGATURES = ['ae', 'oe', 'AE', 'OE', 'fi', 'fl', 'ff', 'fb', 'fh', 'fk',
             'fj', 'ffi', 'ffl', 'ij', 'IJ', 'st', 'ct']

# Language codes
LANGS = {'en': 'English', 'nl': 'Dutch', 'pl': 'Polish', 'de': 'German',
         'eo': 'Esperanto', 'tr': 'Turkish', 'it': 'Italian',
         'cz': 'Czech', 'fr': 'French', 'es': 'Spanish', 'pt': 'Portugese',
         'da': 'Danish', 'fi': 'Finnish', 'sv': 'Swedish', '#': 'numbers'}

KEYS = dict(
    # main keys
    esc=Key('\x1b', 'Esc'), enter=Key('\r', 'Enter'), space=Key(' ', 'Space'),
    tab=Key('\t', 'Tab'), backspace=Key('\x7f', 'Backspace'),
    # arrow keys
    up=Key('\x1b[A', 'Up'), down=Key('\x1b[B', 'Down'),
    left=Key('\x1b[D', 'Left'), right=Key('\x1b[C', 'Right'),
    # editor keys
    ins=Key('\x1b[2~', 'Ins'), delete=Key('\x1b[3~', 'Del'),
    home=Key('\x1b[H', 'Home'), end=Key('\x1b[F', 'End'),
    pgup=Key('\x1b[5~', 'PgUp'), pgdn=Key('\x1b[6~', 'PgDn'),
    # ctrl combinations
    ctrl_c=Key('\x03', 'Ctrl-C'), ctrl_z=Key('\x1a', 'Ctrl-Z'),
    # function keys
    f1=Key('\x1bOP', 'F1'), f2=Key('\x1bOQ', 'F2'),
    f3=Key('\x1bOR', 'F3'), f4=Key('\x1bOS', 'F4'),
    f5=Key('\x1b[15~', 'F5'), f6=Key('\x1b[17~', 'F6'),
    f7=Key('\x1b[18~', 'F7'), f8=Key('\x1b[19~', 'F8'),
    f9=Key('\x1b[20~', 'F9'), f10=Key('\x1b[21~', 'F10'),
    f11=Key('\x1b[23~', 'F11'), f12=Key('\x1b[24~', 'F12')
    )
DEFAULT_ABORT_KEYS = [KEYS[key] for key in ('esc', 'ctrl_c', 'ctrl_z', 'f10')]

# parsing delimiters
COMMENT_SYMBOLS = ['**', '*', '//', '##', '#']
ASSIGNMENT_SYMBOLS = ['=', ':', ' ']

# Row 16 addressing modes
OFF, HMN, KMN, UNIT_SHIFT = 0, 1, 2, 3

# Column numbers in 15x17 diecase
COLUMNS_15 = [*'ABCDEFGHIJKLMNO']
COLUMNS_17 = ['NI', 'NL', *'ABCDEFGHIJKLMNO']
# Build a sequence of Monotype signals as they appear on the paper tower
SIGNALS = [*'NMLKJIHGFSED', '0075', *'CBA',
           *(str(x) for x in range(1, 15)), '0005', 'O15']
