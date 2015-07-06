#!/usr/bin/python3
"""add_334_14_enkidu01:

This program is a test/demonstration script, which adds a hardcoded
matrix case layout to the database. It is written because the matrix
manipulation utility is not ready yet, and we need to develop
the typesetting program.
"""
# matrix manipulation functions:
from rpi2caster import matrix_data

# Diecase metadata: diecase ID, typeface name, font series,
# type size (+ "D" for Didot or "F" for Fournier),
# set width of a wedge, and wedge series.

diecase_id = '334-14-enkidu01'
typeface_name = 'Times Bold'
type_series = '334'
type_size = '14D'
set_width = 12.75
wedge_series = '5'

# Layout consists of separate dictionaries, for each style
# (roman, bold, italic, small caps, subscript, superscript).
#
# Within the style dictionaries, all characters are listed.
# A character is described by a tuple consisting of:
#    column number (e.g. 'NI') - string,
#    row number (e.g. 5) - int,
#    unit width of a character (e.g. 12) - int.
# The unit widths can be found in the unit arrangement tables
# issued by the Monotype corporation.
#
# There is also a dictionary for storing the space position.
# Spaces can be low or high, and the last parameter
# indicates whether it is a low (True) or high space (False).
layout = {'bold': {'a': ('NI', 7, 9),
                   'ä': ('O', 7, 9),
		   'à': ('A', 8, 9),
		   'á': ('B', 7, 9),
		   'â': ('O', 6, 9),
		   'ã': ('C', 7, 9),
                   'b': ('E', 7, 9),
                   'c': ('NL', 4, 8),
                   'ç': ('N', 4, 8),
                   'd': ('NI', 6, 9),
                   'e': ('NI', 4, 8),
                   'ë': ('O', 4, 8),
                   'é': ('B', 4, 8),
                   'è': ('L', 4, 8),
                   'ê': ('M', 4, 8),
                   'f': ('NI', 2, 6),
                   'g': ('E', 5, 9),
                   'h': ('F', 5, 9),
                   'i': ('NI', 1, 5),
                   'ì': ('N', 1, 5),
                   'í': ('L', 1, 5),
                   'ï': ('N', 1, 5),
                   'î': ('O', 1, 5),
                   'j': ('NI', 1, 5),
                   'k': ('M', 8, 10),
                   'l': ('A', 1, 5),
                   'm': ('NI', 13, 14),
                   'n': ('A', 7, 9),
                   'ñ': ('H', 7, 9),
                   'o': ('NI', 5, 9),
                   'ó': ('I', 7, 9),
                   'ò': ('J', 7, 9),
                   'ö': ('K', 7, 9),
                   'ô': ('L', 7, 9),
                   'p': ('A', 6, 9),
                   'q': ('NL', 5, 9),
                   'r': ('NI', 3, 7),
                   's': ('NL', 3, 7),
                   't': ('NL', 2, 6),
                   'u': ('NL', 7, 9),
                   'ü': ('F', 7, 9),
                   'ù': ('NL', 6, 9),
                   'ú': ('D', 7, 9),
                   'û': ('F', 6, 9),
                   'v': ('A', 4, 8),
                   'w': ('NL', 11, 12),
                   'x': ('N', 8, 10),
                   'y': ('A', 5, 9),
                   'z': ('K', 4, 8),
                   'A': ('NI', 12, 13),
                   'Ä': ('E', 12, 13),
                   'Ã': ('C', 12, 13),
                   'Á': ('F', 12, 13),
                   'B': ('L', 11, 12),
                   'C': ('NL', 12, 13),
                   'Ç': ('L', 12, 13),
                   'D': ('B', 13, 14),
                   'E': ('NI', 11, 12),
                   'É': ('M', 11, 12),
                   'È': ('K', 11, 12),
                   'Ê': ('D', 11, 12),
                   'Ë': ('H', 11, 12),
                   'F': ('A', 10, 11),
                   'G': ('O', 13, 14),
                   'H': ('NL', 14, 15),
                   'I': ('A', 3, 7),
                   'Ï': ('B', 3, 7),
                   'Í': ('C', 3, 7),
                   'J': ('L', 8, 10),
                   'K': ('B', 12, 13),
                   'L': ('N', 11, 12),
                   'M': ('NL', 15, 18),
                   'N': ('A', 13, 14),
                   'Ñ': ('N', 13, 14),
                   'O': ('NI', 14, 15),
                   'Ó': ('I', 14, 15),
                   'Ö': ('G', 14, 15),
                   'Ô': ('H', 14, 15),
                   'Õ': ('J', 14, 15),
                   'P': ('A', 11, 12),
                   'Q': ('A', 14, 15),
                   'R': ('A', 12, 13),
                   'S': ('NL', 10, 11),
                   'T': ('O', 11, 12),
                   'U': ('NL', 13, 14),
                   'Ü': ('D', 13, 14),
                   'Ú': ('M', 13, 14),
                   'V': ('H', 12, 13),
                   'W': ('B', 15, 18),
                   'X': ('J', 12, 13),
                   'Y': ('K', 12, 13),
                   'Z': ('I', 12, 13),
                   '1': ('H', 5, 9),
                   '2': ('G', 6, 9),
                   '3': ('G', 7, 9),
                   '4': ('K', 5, 9),
                   '5': ('L', 5, 9),
                   '6': ('M', 5, 9),
                   '7': ('L', 6, 9),
                   '8': ('M', 6, 9),
                   '9': ('M', 7, 9),
                   '0': ('N', 7, 9),
                   '[': ('I', 2, 6),
                   ']': ('J', 2, 6),
                   '(': ('K', 2, 6),
                   ')': ('L', 2, 6),
                   ':': ('M', 3, 7),
                   ';': ('N', 5, 7),
                   '!': ('O', 3, 6),
                   '&': ('C', 15, 18),  # UA 324 lists this as 12 units
                   '?': ('B', 8, 9),
                   '-': ('M', 2, 7),
                   '—': ('M', 15, 18),
                   '.': ('B', 1, 6),
                   ',': ('C', 1, 6),
                   "'": ('N', 2, 5),
                   '«': ('A', 9, 6),
		   '»': ('K', 9, 6),
		   '£': ('O', 8, 10), # unit value unknown
		   'ae': ('C', 10, 11),
		   'oe': ('B', 10, 11),
		   'ff': ('NI', 10, 11),
		   'fi': ('L', 9, 10),
		   'fl': ('M', 9, 10),
		   'ffi': ('B', 14, 15),
		   'ffl': ('C', 14, 15),
		   'AE': ('J', 15, 18),
		   'OE': ('G', 15, 18)},
          'spaces': [('G', 1, True),
                     ('G', 2, True),
                     ('G', 3, True),
                     ('G', 5, True),
                     ('O', 15, True),
                     ('H', 1, False),
                     ('H', 2, False),
                     ('H', 3, False),
                     ('H', 4, False),
                     ('I', 5, False),
                     ('H', 8, False),
                     ('G', 10, False),
                     ('G', 11, False),
                     ('G', 12, False),
                     ('F', 13, False),
                     ('F', 14, False),
                     ('F', 15, False)]}

# Now add the metadata and layout to the database, using the matrix
# manipulation functions module:
matrix_data.add_diecase(diecase_id, type_series, type_size, wedge_series, set_width,
                        typeface_name, layout)
