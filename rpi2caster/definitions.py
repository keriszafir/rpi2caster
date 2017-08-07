# -*- coding: utf-8 -*-
"""Constants and basic data structure definitions"""

from collections import namedtuple

# define some namedtuple objects so that returning data is easier
Coordinates = namedtuple('Coordinates', 'column row')
MatrixSize = namedtuple('MatrixSize', 'horizontal vertical')
MatrixRecord = namedtuple('MatrixRecord', 'char styles code units')
WedgePositions = namedtuple('WedgePositions', 'pos_0075 pos_0005')
WedgeLimits = namedtuple('WedgeLimits', 'shrink stretch')
QueueItem = namedtuple('QueueItem', 'matrix units qty')

# Style definitions
Style = namedtuple('Style', 'name alternatives short codes ansi')
SD = namedtuple('StyleDefinitions',
                ('roman bold semibold italic altitalic bolditalic '
                 'smallcaps fraktur inferior superior '
                 'size1 size2 size3 size4 size5'))
STYLES = SD(roman=Style(name='roman', short='r',
                        alternatives='regular, antiqua',
                        codes=('^rr', '^00'), ansi=0),
            italic=Style(name='italic', short='i', alternatives='',
                         codes=('^ii', '^01'), ansi='3;31'),
            altitalic=Style(name='alternative italic', short='a', ansi='3;31',
                            codes=('^ai', '^08'), alternatives=''),
            semibold=Style(name='semi-bold', short='h', ansi='1;33',
                           codes=('^sb', '^09'), alternatives=''),
            bold=Style(name='bold', short='b', alternatives='',
                       codes=('^bb', '^03'), ansi='1;33'),
            bolditalic=Style(name='bold italic', short='q', ansi='1;31',
                             alternatives='',
                             codes=('^bi', '^ib', '^07')),
            smallcaps=Style(name='small caps', short='s', alternatives='',
                            codes=('^sc', '^ss', '^02'),
                            ansi='4;32'),
            inferior=Style(name='inferior', short='l',
                           alternatives='lower index, subscript',
                           codes=('^ll', '^05'), ansi=34),
            superior=Style(name='superior', short='u',
                           alternatives='upper index, superscript',
                           codes=('^uu', '^04'), ansi=35),
            fraktur=Style(name='Fraktur', short='f',
                          alternatives='Schwabacher, German',
                          codes=('^ff', '^06'), ansi=36),
            size1=Style(name='size 1', short='1', ansi=0,
                        alternatives='', codes=('^s1',)),
            size2=Style(name='size 2', short='2', ansi=0,
                        alternatives='', codes=('^s2',)),
            size3=Style(name='size 3', short='3', ansi=0,
                        alternatives='', codes=('^s3',)),
            size4=Style(name='size 4', short='4', ansi=0,
                        alternatives='', codes=('^s4',)),
            size5=Style(name='size 5', short='5', ansi=0,
                        alternatives='', codes=('^s5',)))
# Style control commands for typesetting - generate automatically
STYLE_COMMANDS = {code: style for style in STYLES for code in style.codes}
# add uppercase as well
STYLE_COMMANDS.update({c.upper(): STYLE_COMMANDS[c] for c in STYLE_COMMANDS})

# Text alignments
Alignment = namedtuple('Alignment', 'name alternatives codes')
AD = namedtuple('AlignmentDefinitions', 'left center right both')
ALIGNMENTS = AD(left=Alignment(name='left', codes=('^cr',),
                               alternatives='flush left, rag right'),
                center=Alignment(name='center', codes=('^cc',),
                                 alternatives='rag left and right'),
                right=Alignment(name='right', codes=('^cl',),
                                alternatives='flush right, rag left'),
                both=Alignment(name='both', codes=('^cf', '^cb'),
                               alternatives='justified, flat, flush both'))
ALIGN_COMMANDS = {code: algmt for algmt in ALIGNMENTS for code in algmt.codes}
ALIGN_COMMANDS.update({c.upper(): ALIGN_COMMANDS[c] for c in ALIGN_COMMANDS})

# Default space positions
DEFAULT_LOW_SPACE_POSITIONS = (('G', 1), ('G', 2), ('G', 5), ('O', 15))
DEFAULT_HIGH_SPACE_POSITIONS = (('O', 16),)
# Names for low and high spaces, depending on their width
SPACE_NAMES = {'   ': 'low em quad', '  ': 'low en quad', ' ': 'low space',
               '___': 'high em quad', '__': 'high en quad', '_': 'high space'}
SPACE_SYMBOLS = {' ': '□', '_': '▣'}

# Measurement units for line length, character/space width etc.
TYPOGRAPHIC_UNITS = dict(pc=12.0, pt=1.0, Pp=12*0.166/0.1667, pp=0.166/0.1667,
                         cc=12*0.1776/0.1667, dd=0.1776/0.1667,
                         cf=12*0.1628/0.1667, ff=0.1628/0.1667,
                         cm=0.3937*72, mm=0.03937*72)
TYPOGRAPHIC_UNITS['in'] = TYPOGRAPHIC_UNITS['"'] = 72.0


# S5 wedge unit values; wedge name aliases
S5 = [5, 6, 7, 8, 9, 9, 9, 10, 10, 11, 12, 13, 14, 15, 18]


# Accented letters will use the same unit arrangement value as their
# non-accented counterparts.
ACCENTS = dict(a='ąäáãâạà', c='ćĉç', e='ęëȩẽéêèẹ', g='ǵĝ', h='ḧḩĥḥ',
               i='ïĩíîìị', j='j́ĵ', k='ķḱḳ', l='łļĺḷ', m='ḿṃ', n='ńņñǹṇ',
               o='óöõôòọ', p='þṕ', r='ŗŕṛ', s='śşŝṣ', t='ţẗṭ', u='üũúûùụǘǜ',
               v='ṽṿ', w='ẅẃŵẁẉ', x='ẍ', y='ÿỹýŷỳỵ', z='żźẑẓ')
ACCENTS.update({letter.upper(): ACCENTS[letter].upper() for letter in ACCENTS})
REVERSE_ACCENTS = {accented_char: unaccented_char
                   for unaccented_char, accents in ACCENTS.items()
                   for accented_char in accents}

# Typical ligatures:
LIGATURES = ['ae', 'oe', 'AE', 'OE', 'fi', 'fl', 'ff', 'fb', 'fh', 'fk',
             'fj', 'ffi', 'ffl', 'ij', 'IJ', 'st', 'ct']

# Language codes
LANGS = {'en': 'English', 'nl': 'Dutch', 'pl': 'Polish', 'de': 'German',
         'eo': 'Esperanto', 'tr': 'Turkish', 'it': 'Italian',
         'cz': 'Czech', 'fr': 'French', 'es': 'Spanish', 'pt': 'Portugese',
         'da': 'Danish', 'fi': 'Finnish', 'sv': 'Swedish', '#': 'numbers'}
