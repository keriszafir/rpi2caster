# -*- coding: utf-8 -*-
"""View functions for rpi2caster"""

from collections import OrderedDict
from contextlib import suppress
from itertools import zip_longest
from string import ascii_lowercase, ascii_uppercase, digits

from . import basic_models as bm, definitions as d
from .rpi2caster import UI
from .data import TYPEFACES, UNIT_ARRANGEMENTS
from .data import WEDGE_ALIASES, WEDGE_DEFINITIONS
from .main_models import Typeface, UnitArrangement


# Wedge views

def list_wedges():
    """List known wedges"""
    def sorting_key(ua_number):
        """Sorting key: integer part"""
        return int(''.join(char for char in ua_number if char.isdigit()))

    UI.display('Wedge definitions and their unit values:\n\n'
               'The first number is the wedge/stopbar series number.\n'
               'Unit values are listed for each row of the matrix case.\n'
               'Some wedges have an additional 16th unit value. This means '
               'that this wedge was used\nwith a "HMN" or "KMN" early row 16 '
               'addressing system. Those wedges and attachments are rare.\n\n')
    UI.display('The program currently knows {} wedge definitions.'
               .format(len(WEDGE_DEFINITIONS)))
    rows = ''.join(str(x).ljust(5) for x in range(1, 16))
    UI.display_header('{:^10}{}[16]'.format('Wedge', rows))
    # display all wedges
    for wedge_number in sorted(WEDGE_DEFINITIONS, key=sorting_key):
        wedge_units = WEDGE_DEFINITIONS[wedge_number]
        unit_values = ''.join(str(x).ljust(5) for x in wedge_units)
        UI.display('{:^10}{}'.format(wedge_number, unit_values))

    # display old-style wedge designations
    aliases = iter(WEDGE_ALIASES)
    # Group by three
    grouper = zip_longest(aliases, aliases, aliases, fillvalue='')
    old_wedges = '\n'.join('\t'.join(z) for z in grouper)
    desc = ('\n\nSome known OLD-STYLE British wedge designations:\n\n'
            'If you have one of those, then whenever the program asks you '
            'about the wedge designation,\nyou need to enter the NEW-STYLE '
            'number, for example "9 1/4 AK" will be "S5-9.25".\nIf the wedge '
            'is marked as "EU", then it was made for continental Europe,\n'
            'and based on old British pica value (.1667"). New-style wedge '
            'designations\nfor European wedges have the letter "E" '
            'appended to the set width - e.g. "S5-12E"\n')
    UI.display(desc)
    UI.display(old_wedges)
    UI.display('\n\nScroll your terminal up to see more.')


# Unit arrangement views


def list_unit_arrangements():
    """List all unit arrangements the program knows about."""
    number = 1
    # display UA list
    for ua_number in sorted(UNIT_ARRANGEMENTS, key=int):
        arr = UnitArrangement(ua_number)
        variant_names = ', '.join(var.name for var in arr.variants)
        UI.display('UA {} - {}'.format(arr.number, variant_names))
        with suppress(ValueError):
            number = int(ua_number)

    missing = [str(x) for x in range(1, number)
               if str(x) not in UNIT_ARRANGEMENTS]
    UI.display('The program currently knows {} unit arrangements.\nAt least '
               '{} seem to be missing - it is unclear if they ever existed.'
               '\n\nScroll your terminal up to see more.'
               .format(len(UNIT_ARRANGEMENTS), len(missing)))


def display_ua(ua_variant):
    """Show an unit arrangement by char and by units"""
    def display_by_units():
        """display chars grouped by unit value"""
        UI.display('Ordered by unit value:')
        for unit_value, chars in sorted(ua_variant.by_units.items()):
            char_string = ', '.join(sorted(chars))
            UI.display('\t{}:\t{}'.format(unit_value or 'Absent', char_string))
        UI.display()

    def display_letters():
        """display unit values for all letters and ligatures"""
        # define templates for lower+uppercase, lowercase only, uppercase only
        template = '\t{:<4}: {:>3} units, \t\t{:<4}: {:>3} units'
        lc_tmpl = '\t{:<4}: {:>3} units'
        uc_tmpl = '\t\t\t{:<4}: {:>3} units'

        UI.display('Ordered by character:')
        for lowercase in [*ascii_lowercase, *d.LIGATURES]:
            uppercase = lowercase.upper()
            with suppress(ValueError, IndexError):
                # display both lower and upper
                lower_units = ua_variant[lowercase]
                upper_units = ua_variant[uppercase]
                UI.display(template.format(lowercase, lower_units or 'absent',
                                           uppercase, upper_units or 'absent'))
                continue
            with suppress(ValueError, IndexError):
                # display lowercase only
                lower_units = ua_variant[lowercase]
                UI.display(lc_tmpl.format(lowercase, lower_units or 'absent'))
                continue
            with suppress(ValueError, IndexError):
                # display uppercase only
                lower_units = ua_variant[uppercase]
                UI.display(uc_tmpl.format(uppercase, upper_units or 'absent'))
                continue
        UI.display()

    def display_numbers():
        """display 0...9 unit values"""
        grouped_by_units = OrderedDict()
        for units in range(7, 15):
            chars = []
            for number in digits:
                with suppress(ValueError):
                    if ua_variant[number] == units:
                        chars.append(number)
            if chars:
                grouped_by_units[units] = ', '.join(chars)
        if not grouped_by_units:
            return
        UI.display('Digits / numerals:')
        for units, characters in grouped_by_units.items():
            UI.display('{}: {} units'.format(characters, units))

    def display_others():
        """display other characters - not letters"""
        done = [*ascii_lowercase, *ascii_uppercase, *digits, *d.LIGATURES]
        other_chars = {u: [c for c in sorted(set(chars).difference(done))]
                       for u, chars in ua_variant.by_units.items()}
        others = [(', '.join(chars), units)
                  for units, chars in sorted(other_chars.items()) if chars]
        if others:
            chunks = ('{}: {} units'.format(c, u) if u
                      else '{}: absent'.format(c) for c, u in others)
            row = 'Other: {}'.format(', '.join(chunks))
            UI.display(row)

    if not ua_variant:
        UI.display('No unit arrangement to display...')
        return

    UI.display_header('{}'.format(ua_variant))
    display_by_units()
    display_letters()
    display_numbers()
    display_others()


# Diecase views


def list_diecases(data):
    """Display all diecases in a dictionary, plus an empty new one"""
    UI.display('\nAvailable diecases:\n')
    UI.display_header('|{:<5}  {:<25} {:<12} {:<60}|'
                      .format('Index', 'Diecase ID', 'Wedge', 'Typeface(s)'),
                      trailing_newline=0)
    # show the rest of the table
    template = ('|{index:>5}  {d.diecase_id:<25} '
                '{d.wedge.name:<12} {d.description:<60}|')
    entries = (template.format(d=diecase, index=index)
               for index, diecase in data.items())
    UI.display(*entries, sep='\n')
    return data


def display_layout(diecase):
    """Display the diecase layout, unit values, styles."""
    def get_formatted_text(text, styles, length='^3'):
        """format a text with formatting string in styles definitions"""
        field = '{{:{}}}'.format(length) if length else '{}'
        collection = bm.Styles(styles)
        if text in d.SPACE_NAMES:
            # got a space = display symbol instead
            return field.format(d.SPACE_SYMBOLS.get(text[0]))
        elif collection.use_all:
            return field.format(text)
        else:
            ansi_codes = ';'.join(str(s.ansi) for s in collection if s.ansi)
            template = '\x1b[{codes}m{text}\x1b[0m'
            return template.format(codes=ansi_codes, text=field.format(text))

    def get_column_widths():
        """calculate column widths to adjust the content"""
        # 3 characters to start is reasonable enough
        columns = diecase.column_numbers
        column_widths = OrderedDict((name, 3) for name in columns)

        # get the maximum width of characters in every column
        # if it's larger than header field width, update the column width
        for column, initial_width in column_widths.items():
            widths_gen = (len(mat) for mat in diecase.select_column(column))
            column_widths[column] = max(initial_width, *widths_gen)
        return column_widths

    def build_row(row_number):
        """make a diecase layout table row - actually, 3 rows:
            empty row - separator; main row - characters,
            units row - unit values, if not matching the row units.
        """
        row = diecase.select_row(row_number)
        units = wedge.units[row_number]
        # initialize the row value dictionaries
        empty_row = dict(row='', units='')
        main_row = dict(row=row_number, units=units)
        units_row = dict(row='', units='')
        # fill all mat character fields
        for mat in row:
            column = mat.position.column
            empty_row[column] = ''
            # display unit width if it differs from row width
            m_units = '' if mat.units == units else mat.units
            units_row[column] = m_units
            # format character for display
            fmt = '^{}'.format(widths.get(column, 3))
            main_row[column] = get_formatted_text(mat.char, mat.styles, fmt)

        # format and concatenate two table rows
        empty_str = template.format(**empty_row)
        main_str = template.format(**main_row)
        units_str = template.format(**units_row)
        return '{}\n{}\n{}'.format(empty_str, main_str, units_str)

    def build_description():
        """diecase description: ID, typeface, wedge name and set width"""
        table_width = len(header)
        try:
            # diecase ID, typeface, wedge used
            row1_left = '{d.diecase_id} ({d.description})'.format(d=diecase)
            row1_right = 'wedge: {}'.format(wedge.name)
        except AttributeError:
            row1_left = 'Unknown diecase ID.'
            row1_right = 'Unknown wedge. Assuming S5.'
        row1_filled_width = len(row1_left) + len(row1_right) + 4
        row1_center = ' ' * (table_width - row1_filled_width)
        # available styles
        row2_left = ', '.join(get_formatted_text(s.name, s)
                              for s in diecase.styles)
        # warning: ANSI-formatting the strings affects their length!
        # calculate the correct length of formatted style names
        styles_length = len(', '.join(s.name for s in diecase.styles))
        # space symbols
        spaces = [(d.SPACE_NAMES.get(space), symbol)
                  for space, symbol in d.SPACE_SYMBOLS.items()]
        row2_right = ', '.join('{} = {}'.format(*item)
                               for item in sorted(spaces))
        # calculate the length of occupied space
        row2_filled_width = styles_length + len(row2_right) + 4
        row2_center = ' ' * (table_width - row2_filled_width)
        # table border template
        line = '═' * (table_width - 2)
        upper_border = '╔{}╗'.format(line)
        lower_border = '╠{}╣'.format(line)
        row_tmpl = '║ {}{}{} ║'
        return '\n'.join((upper_border,
                          row_tmpl.format(row1_left, row1_center, row1_right),
                          row_tmpl.format(row2_left, row2_center, row2_right),
                          lower_border))

    # what wedge does the diecase use?
    try:
        wedge = diecase.wedge
    except AttributeError:
        wedge = bm.Wedge()
    # table row template
    widths = get_column_widths()
    fields = ' '.join(' {{{col}:^{width}}} '.format(col=col, width=width)
                      for col, width in widths.items())
    template = '║ {{row:>3}} │{fields}│ {{units:>5}} ║'.format(fields=fields)
    # header row template
    header = dict(units='Units', row='Row')
    header.update({col: col for col in widths})
    header = template.format(**header)
    # proper layout
    contents = (build_row(num) for num in diecase.row_numbers)
    # table description
    desc = build_description()
    # put the thing together
    table = (desc, header, '╟{}╢'.format('─' * (len(header) - 2)),
             *contents, '╚{}╝'.format('═' * (len(header) - 2)))
    # finally display it
    UI.display('\n'.join(table))
    UI.display('\n\nScroll your terminal up to see more.')


# Typeface views


def list_typefaces(*_):
    """Show all available typefaces"""
    template = '{series:>6}\t{name:<35}\t{script:<20} {styles:<25}\t{rel:<30}'
    typefaces = (Typeface(series) for series in sorted(TYPEFACES, key=int))
    fields = dict(series='Series', name='Name', script='Script',
                  styles='Styles in typeface', rel='Related typefaces')
    UI.display_header(template.format(**fields))
    # store the last number...
    number = 0
    # list of typefaces
    for typeface in typefaces:
        related = ', '.join('{}-> {} {}'
                            .format(style.name, face.series, face_style.name)
                            for style, (face, face_style)
                            in typeface.related.items())
        row = dict(series=typeface.series, name=typeface.name, rel=related,
                   script=typeface.script, styles=typeface.styles.names)
        UI.display(template.format(**row))
        with suppress(ValueError):
            number = int(typeface.series)

    # list missing typefaces
    missing = [str(x) for x in range(1, number) if str(x) not in TYPEFACES]
    UI.display('The program currently knows {} typefaces.\nAt least '
               '{} seem to be missing - it is unclear if they ever existed.'
               '\n\nScroll your terminal up to see more.'
               .format(len(TYPEFACES), len(missing)))
