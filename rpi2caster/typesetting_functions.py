"""
typesetting_functions:

Contains functions used for calculating line length, justification,
setting wedge positions, breaking the line etc.
"""
from rpi2caster import exceptions
from rpi2caster.global_settings import USER_INTERFACE as ui


def align_left(buffer, line_length, characters_unit_length):
    """Aligns the text to the left."""
    pass


def align_center(text, line_length):
    """Centers the text."""
    pass


def align_right(text, line_length):
    """Aligns the text to the right."""
    pass


def align_both(text, line_length):
    """Aligns the text to both margins."""
    pass


def choose_alignment():
    """Lets the user choose the text alignment in line or column."""
    options = {'L': align_left,
               'C': align_center,
               'R': align_right,
               'B': align_both}
    message = ('Alignment? [L]eft, [C]enter, [R]ight, [B]oth: ')
    return ui.simple_menu(message, options)


def translate(text, unit_line_length, diecase_layout, alignment,
              wedge_series, set_width, unit_shift=False, min_space=4):
    """translate:

    Translates the characters to matrix coordinates.
    Calculates the length in units. Returns the unit length and number
    of spaces found between the words (their width will be variable).
    """
    spaces = 0
    chars_unit_length = 0
    buffer = []
    # Determine the text variant
    # (roman, bold, italic, small caps, subscript, superscript):
    variant = type(text)
    # What alphabet to use:
    variant_layout = diecase_layout[variant]
    # Which diecase positions are actually spaces?
    spaces_available = diecase_layout['spaces']
    # Allow to choose space if more than one blank matrix is in the diecase
    if len(spaces_available) > 1:
        pass
    line_length = calculate_unit_line_length(inch_line_length, set_width)
    while chars_unit_length + spaces * min_space < line_length - 100:
        # Loop over all characters and find their coords, calculate values
        for character in text:
            if character == ' ':
                spaces += 1
                char_code = variable_space_code
            elif character == '_':
                spaces += 1
                char_code = fixed_space_code
            else:
                # Get matrix coordinates and unit value
                char_data = get_matrix_position(character, variant_layout)
                (column, row, char_units) = char_data
                # Be sure we're working with uppercase column ids
                column = column.upper()
                # Generate a string with Monotype code for the character
                char_code = ' '.join([column, str(row)])

            # In case of unit-shift: use EF for addressing column D
            if unit_shift and 'D' in char_code:
                char_code = char_code.replace('D', 'EF')
            buffer.append(coordinates)
            chars_unit_length += ch_units
        # Align to the left/center/right/both
        alignment(buffer, line_length, chars_unit_length)
    # The code sequence is ready
    return buffer


def enter_line_length():
    """enter_line_length:

    Asks user to enter line length and specify measurement units.
    Returns line length in inches for further calculations.
    """
    line_length = ui.enter_data_spec_type('Line length? : ', float)
    # Choose the measurement unit - and its equivalent in inches
    options = {'A': 0.1660,
               'B': 0.1667,
               'C': 0.3937,
               'D': 0.1776,
               'F': 0.1629}
    message = ('Measurement? [A]merican pica = Johnson, '
               '[B]ritish pica = DTP, '
               '[C]entimeter, [D]idot cicero, [F]ournier cicero: ')
    # Return line length in inches
    return ui.simple_menu(message, options) * line_length


def calculate_unit_line_length(inch_length, set_width, brit_pica):
    """Calculates the line length in units of a given set."""
    # How many picas?
    if brit_pica:
        pica_length = inch_length / 0.1667
    else:
        pica_length = inch_length / 0.166
    # 1 pica em is equal to 18 units 12-set
    # Units of a given set = pica_length * set_width * (12*18 = 1296)
    # Return the result
    return pica_length * set_width / 1296


def enter_min_variable_space():
    """Allows to enter minimum space length or leave blank for default."""
    prompt = 'Minimum space length? [default: 4 units]: '
    return abs(ui.enter_data_spec_type_or_blank(prompt, float)) or 4


def chose_spaces(layout):
    """Chooses the spaces that will be used in typesetting."""
    fixed_space = ui.enter


def get_matrix_position(character, layout):
    """get_matrix_position:

    Gets character's coordinates in the diecase, returns them.
    Returns coordinates (as a string) and unit width of a character.
    """
    try:
        column = str(layout[character][0])
        row = str(layout[character][1])
        units = int(layout[character][2]) or 0
        return (column + row, units)
    except KeyError:
        raise exceptions.MatrixNotFound('%s not in diecase layout' % character)


def single_justification(wedge_positions, buffer):
    """single_justification:

    Single justification: the caster sets 0005, then 0075 + pump resumes.
    Function adds a 0075-b, then 0005-a combination to buffer.
    Supports both normal (0075, 0005, 0005+0075) and alternate (NK, NJ, NKJ)
    justification modes.
    """
    (pos0075, pos0005) = wedge_positions
    # Add 0075-N-K-pos0075 first:
    buffer.append(str(pos0075) + 'NK 0075')
    # Add 0005-N-J-pos0005 next:
    buffer.append(str(pos0005) + 'NJ 0005')
    return True


def double_justification(wedge_positions, buffer):
    """double_justification:

    Double justification: the caster sets 0005+0075 and puts the line
    to the galley, then sets 0075 and pump resumes.
    Function adds a 0075-b, then 0005-a combination to buffer.
    Supports both normal (0075, 0005, 0005+0075) and alternate (NK, NJ, NKJ)
    justification modes.
    """
    (pos0075, pos0005) = wedge_positions
    # Add 0075-N-K-pos0075 first:
    buffer.append(str(pos0075) + 'NK 0075')
    # Add 0005-N-J-pos0005 next:
    buffer.append(str(pos0005) + 'NKJ 0005 0075')
    return True
