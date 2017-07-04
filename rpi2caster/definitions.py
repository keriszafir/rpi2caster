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
Typeface = namedtuple('Typeface', 'raw ids uas styles text')

# Style definitions
Style = namedtuple('Style', 'name alternatives short codes ansi')
SD = namedtuple('StyleDefinitions',
                ('roman bold italic smallcaps inferior superior fraktur '
                 'size1 size2 size3 size4 size5'))
STYLES = SD(roman=Style(name='roman', short='r',
                        alternatives='regular, antiqua',
                        codes=('^rr', '^RR', '^00'), ansi=0),
            italic=Style(name='italic', short='i', alternatives='',
                         codes=('^ii', '^II', '^01'), ansi='3;31'),
            bold=Style(name='bold', short='b', alternatives='',
                       codes=('^bb', '^BB', '^03'), ansi='1;33'),
            smallcaps=Style(name='small caps', short='s', alternatives='',
                            codes=('^sc', '^ss', '^SC', '^SS', '^02'),
                            ansi='4;32'),
            inferior=Style(name='inferior', short='l',
                           alternatives='lower index, subscript',
                           codes=('^ll', '^LL', '^05'), ansi=34),
            superior=Style(name='superior', short='u',
                           alternatives='upper index, superscript',
                           codes=('^uu', '^UU', '^04'), ansi=35),
            fraktur=Style(name='Fraktur', short='f',
                          alternatives='Schwabacher, German',
                          codes=('^ff', '^FF', '^06'), ansi=36),
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

# Unit arrangement variants
Variant = namedtuple('UAVariant', 'name short alternatives')
VD = namedtuple('VariantDefinition',
                'regular italic smallcaps accented '
                'size1 size2 size3 size4 size5 '
                'a_regular a_italic a_smallcaps b_regular')
VARIANTS = VD(regular=Variant('regular', 'r', 'roman or bold'),
              italic=Variant('italic', 'i', ''),
              smallcaps=Variant('small caps', 's', ''),
              accented=Variant('accents', 'a', 'Gaelic'),
              size1=Variant('size 1', 's1', 'titling'),
              size2=Variant('size 2', 's2', 'titling'),
              size3=Variant('size 3', 's3', 'titling'),
              size4=Variant('size 4', 's4', 'titling'),
              size5=Variant('size 5', 's5', 'titling'),
              a_regular=Variant('regular A', 'ar', 'special variant'),
              a_italic=Variant('italic A', 'ai', 'special variant'),
              a_smallcaps=Variant('small caps A', 'as', 'special variant'),
              b_regular=Variant('regular B', 'br', 'special variant'))

# Text alignments
Alignments = namedtuple('Alignments', ('left', 'center', 'right', 'both'))
ALIGNMENTS = Alignments('left', 'center', 'right', 'both')
# Control codes for typesetting
ALIGN_COMMANDS = {'^CR': ALIGNMENTS.left, '^CC': ALIGNMENTS.center,
                  '^CL': ALIGNMENTS.right, '^CF': ALIGNMENTS.both}
STYLE_COMMANDS = {'^00': STYLES.roman, '^rr': STYLES.roman,
                  '^01': STYLES.italic, '^ii': STYLES.italic,
                  '^02': STYLES.bold, '^bb': STYLES.bold,
                  '^03': STYLES.smallcaps, '^ss': STYLES.smallcaps,
                  '^04': STYLES.inferior, '^ll': STYLES.inferior,
                  '^05': STYLES.superior, '^uu': STYLES.superior,
                  '^s1': STYLES.size1, '^s2': STYLES.size2,
                  '^s3': STYLES.size3, '^s4': STYLES.size4,
                  '^s5': STYLES.size5}

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
WEDGE_ALIASES = ('10E: UK S527', '10L: UK S536', '11Q: UK S574',
                 '14E: UK S1406', '1A: UK S207', '1B: UK S209',
                 '1C: UK S210', '1O: UK S221', '1R: UK S223',
                 '1Q: UK S224', '2A: UK S233', '2Z: UK S261',
                 '3O: UK S275', '3Q: UK S277', '3Y: UK S286',
                 '4A: UK S295', '4G: UK S300', '5P: UK S327',
                 '5V: UK S371', '7J: UK S422', '7Z: UK S449',
                 '8A: UK S450', '8U: UK S409', 'TW: S535 typewriter',
                 'AK: EU S5', 'BO: EU S221', 'CZ: EU S336',
                 'A: UK S5', 'D: UK S46', 'E: UK S92',
                 'F: UK S94', 'G: UK S93', 'J: UK S101',
                 'K: UK S87', 'L: UK S96', 'M: UK S45',
                 'N: UK S88', 'O: UK S111', 'Q: UK S50',
                 'S: UK S197', 'V: UK S202', 'W: UK S205', 'X: UK S47')


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
