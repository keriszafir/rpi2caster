"""
typesetting_functions:

Contains functions used for calculating line length, justification,
setting wedge positions, breaking the line etc.
"""
from rpi2caster import exceptions
from rpi2caster.global_settings import USER_INTERFACE as ui
from rpi2caster import wedge_data
from rpi2caster import matrix_data


# Define control commands for the typesetting routines
COMMANDS = {'^00': 'style=roman',
            '^01': 'style=bold',
            '^02': 'style=ititalic',
            '^03': 'style=smallcaps',
            '^04': 'style=subscript',
            '^05': 'style=superscript',
            '^CR': 'align_center()'}


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


def choose_style(diecase_layout):
    """Parses the diecase for available styles and lets user choose one."""
    available_styles = matrix_data.get_styles(diecase_layout)
    options = {i: style for i, style in enumerate(available_styles, start=1)}
    return ui.menu(options, header='Choose a style')


def get_space_codes(space_style, unit_width, diecase_layout):
    """Gets coordinates for the space closest to the desired unit width"""
    available_spaces = [sp for sp in diecase_layout if sp[0] = space_style]
    # Search for a best match, starting with some arbitrary difference
    for space in available_spaces:
        if space[-1]


def compose_line(buffer, text_fragments, unit_line_length, space_settings,
                 diecase_layout, wedge_series, set_width, alignment,
                 unit_shift, manual_control=False, ligatures=False):
    """compose_line:

    Reads text fragments from input, then composes them, and justifies to a
    specified line length. Adds codes to the buffer.
    Text fragments is a list of tuples: ((text1, style1), (text2, style2)...)
    """
    # Read the space settings
    ((var_style, var_min_units), (fixed_style, fixed_units),
     (nb_sp_style, nb_sp_units)) = space_settings
    # Get the Monotype signals for the spaces
    fix_space_code = get_space_codes(fixed_style, fixed_units, diecase_layout)
    nb_space_code = get_space_codes(nb_sp_style, nb_sp_units, diecase_layout)
    # Inintialize with no chars and spaces count at 0
    chars_length = 0
    spaces_count = 0
    for (text, style) in text_fragments:
        if manual_control:
            while (chars_length + spaces_count * var_min_units <
                   unit_line_length - 100):
                for i, char in enumerate(text):
                    # Determine if it's a control command
                    try:
                        if char == '^':
                            # ^ denotes control commands
                            try:
                                command_code = text[i:i+2]
                                eval(COMMANDS[command_code])
                            except (IndexError, KeyError):
                                pass
                        elif char == ' ':
                            # This is a typical variable space
                            spaces_count += 1
                            buffer.append('var_space')
                        elif char == '~':
                            # This is a fixed space
                            buffer.extend(fix_space_code)
                            chars_length += fixed_units
                        elif char == '_':
                            # This is a non-breaking space
                            buffer.extend(nb_space_code)
                            chars_length += nb_sp_units
                        elif ligatures:
                            # Not a control sequence or space? Then character
                            # Try a ligature first...
                            translate(text[i:i+ligatures-1])
                    except IndexError:
                        pass


def translate(char):
    """Translates a character"""


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


def space_settings():
    """Chooses the spaces that will be used in typesetting."""
    # List available spaces
    # Matrix in layout is defined as follows:
    # (character, (style1, style2...)) : (column, row, unit_width)
    var_prompt = 'Variable space: [L]ow or [H]igh?'
    var_units_prompt = 'How many units min. (default: 4)? '
    fixed_prompt = 'Fixed space: [L]ow or [H]igh?'
    fix_units_prompt = 'How many units (default: 9)? '
    nbsp_prompt = 'Non-breaking space: [L]ow or [H]igh?'
    nbsp_units_prompt = 'How many units (default: 9)? '
    # Choose spaces
    # Variable space (justified) - minimum units
    variable_space = ui.simple_menu(var_prompt, {'L': ' ', 'H': '_'})
    min_units = ui.enter_data_spec_type_or_blank(var_units_prompt, int) or 4
    # Fixed space (allows line-breaking)
    fixed_space = ui.simple_menu(fixed_prompt, {'L': ' ', 'H': '_'})
    fixed_units = ui.enter_data_spec_type_or_blank(fix_units_prompt, int) or 9
    # Non-breaking space
    nb_space = ui.simple_menu(nbsp_prompt, {'L': ' ', 'H': '_'})
    nb_units = ui.enter_data_spec_type_or_blank(nbsp_units_prompt, int) or 9
    # Return decision
    return (variable_space, min_units,
            fixed_space, fixed_units,
            nb_space, nb_units)


def translate_character(char, style, layout, unit_shift, unit_arrangement):
    """translate_character:

    Gets character's coordinates in the diecase, determines and applies
    unit width correction (with unit shift or single justification).
    Returns coordinates (as a string) and unit width of a character.
    """
    try:
        column = layout[char][0]
        row = layout[char][1]
        units = int(layout[char][2]) or unit_arrangement[row]
    except KeyError:
        # Matrix not found in diecase
        raise exceptions.MatrixNotFound('%s %s not in diecase layout'
                                        % (char, style))
    except IndexError:
        # This happens if the "units" field is left blank
        column = layout[char][0]
        row = layout[char][1]
        units = unit_arrangement[row]
    if unit_shift:
        # Try to use unit-shift if previous row uses correct units
        # "EF" signals are used for addressing the column D:
        if unit_arrangement[row - 1] == units:
            row = row - 1
            if 'D' in column:
                column.replace('D', 'EF')
            column = 'D' + column


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
