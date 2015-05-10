# -*- coding: utf-8 -*-
"""Times New Roman 12D 327+334"""

diecaseID = '327-12-KS01'
typeface = 'Times New Roman'
series = 327
wedge = 'S5'
setWidth = 12

"""Matrix case layout: 

It's a dictionary containing sub-dictionaries, where:
{roman       : { char1 : (column, row, units),
                 char2 : (column, row, units),
                 etc. 
                },
 bold        : {character definitions},
 italic      : {character definitions},
 smallcaps   : {character definitions},
 subscript   : {character definitions},
 superscript : {character definitions}
}

  char - as found in input text (utf-8),
  column - column's 'number' (e.g. 'NL', 'A', 'O') - this will be addressed
        (any corrections based on caster's settings will be applied later,
         like changing D column to EF combination when using unit shift)
  row - row number (1...15 or 16 for HMN, KMN, unit-shift diecases),
  units - unit width of a character, optional.
  
If no unit value is given for char, use unit widths calculated 
from the row's unit width, based on the normal wedge's values.
If unit width is specified - compare it with row's unit width, calculate
the difference and then use D10/D11 wedges to add or subtract units.
We can also use unit-shift for casting a character from n-th row with
the (n-1)-th row's unit value; we must add D signal to the combination.

Exceptions to be caught:
-IndexError: tuple index out of range (no unit value given for char)
-KeyError: character is not found in style's layout (use roman instead)
-KeyError: style is not found in diecase (use roman instead, or stop
if roman is not found as well)
"""


def roman():
    pass
def bold():
    pass
def italic():
    pass
def smallcaps():
    pass
def subscript():
    pass
def superscript():
    pass


layout = {roman : {'a' : ('H', 9, 7),
                   'ą' : ('K', 9, 7),
                   'b' : ('E', 11, 7),
                   'c' : ('I', 5, 7),
                   'ć' : ('J', 5, 7),
                   'd' : ('H', 10, 7),
                   'e' : ('G', 6, 7),
                   'ę' : ('K', 5, 7),
                   'f' : ('F', 3, 6),
                   'g' : ('F', 9, 7),
                   'h' : ('K', 10, 8),
                   'i' : ('H', 2, 5),
                   'j' : ('I', 2, 5),
                   'k' : ('L', 10, 8),
                   'l' : ('J', 2, 5),
                   'ł' : ('K', 2, 5),
                   'm' : ('G', 14, 15),
                   'n' : (),
                   'ń' : (),
                   'o' : (),
                   'ó' : (),
                   'p' : (),
                   'q' : (),
                   'r' : (),
                   's' : (),
                   'ś' : (),
                   't' : (),
                   'u' : (),
                   'v' : (),
                   'w' : (),
                   'x' : (),
                   'y' : (),
                   'z' : (),
                   'ź' : (),
                   'ż' : (),
                   'A' : (),
                   'Ą' : (),
                   'B' : (),
                   'C' : (),
                   'Ć' : (),
                   'D' : (),
                   'E' : (),
                   'Ę' : (),
                   'F' : (),
                   'G' : (),
                   'H' : (),
                   'I' : (),
                   'J' : (),
                   'K' : (),
                   'L' : (),
                   'Ł' : (),
                   'M' : (),
                   'N' : (),
                   'Ń' : (),
                   'O' : (),
                   'Ó' : (),
                   'P' : (),
                   'Q' : (),
                   'R' : (),
                   'S' : (),
                   'Ś' : (),
                   'T' : (),
                   'U' : (),
                   'V' : (),
                   'W' : (),
                   'X' : (),
                   'Y' : (),
                   'Z' : (),
                   'Ź' : (),
                   'Ż' : (),
                   '1' : (),
                   '2' : (),
                   '3' : (),
                   '4' : (),
                   '5' : (),
                   '6' : (),
                   '7' : (),
                   '8' : (),
                   '9' : (),
                   '0' : (),
                   '+' : (),
                   '×' : (),
                   '[' : (),
                   ']' : (),
                   '(' : (),
                   ')' : (),
                   ':' : (),
                   ';' : (),
                   '?' : (),
                   '/' : (),
                   '°' : (),
                   '-' : (),
                   '–' : (),
                   '—' : (),
                   '=' : (),
                   '.' : (),
                   '"' : (),
                   '!' : (),
                   '%' : (),
                   '•' : (),
                   '*' : (),
                   '„' : (),
                   '”' : (),
                   ',' : (),
                   '’' : ()
                   }
}

diecase = (diecaseID, typeface, series, wedge, setWidth, layout)