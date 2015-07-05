"""
typesetter - program for generating the code sequence fed to
a Monotype composition caster or type&rule caster.

This program reads an input file (UTF-8 text file) or allows to enter
a string, then parses it, auto-hyphenates (with TeX hyphenation algorithm),
calculates justification figures and outputs the combinations of Monotype
signals, one by one, to the file or database. These sequences are to be read
and parsed by the casting program, which sends the signals to the machine.
"""
# Typical libs, used by most routines:
import time
# User interface
from rpi2caster.global_settings import USER_INTERFACE as ui
# Exceptions module
from rpi2caster import exceptions
# Wedge and database operations
from rpi2caster import matrix_data, wedge_data
# HTML/XML parser:
try:
    from bs4 import BeautifulSoup
except ImportError:
    raise exceptions.MissingDependency('BeautifulSoup 4 not installed!')


class Typesetter(object):
    """Typesetter:

    This class contains all methods related to typesetting, i.e. converting
    an input text to a sequence of Monotype codes to be read by the casting
    interface. This class is to be instantiated, so that all data
    and buffers are contained within an object and isolated from other
    typesetting sessions.
    """

    def __init__(self):
        self.diecase = ''
        self.set_width = 0
        self.typeface = ''
        self.type_series = ''
        self.diecase_id = ''
        self.type_size = ''
        self.wedge = ''
        self.diecase_system = ''
        self.diecase_layout = []
        self.line_length = ''
        self.fu_line_length = ''
        self.unit_line_length = ''
        self.measurement = ''
        self.input_file = ''
        self.output_file = ''

    def __enter__(self):
        """Do nothing"""
        return self

    def main_menu(self):
        """main_menu

        Calls ui.menu() with options, a header and a footer.
        Also defines some subroutines for appending information.
        """

        # Declare local functions for menu options:
        def choose_input_filename():
            self.input_file = ui.enter_input_filename()
            self.main_menu()

        def choose_output_filename():
            self.output_file = ui.enter_output_filename()
            self.main_menu()

        def debug_notice():
            # Prints a notice if the program is in debug mode:
            info = '\n\nThe program is now in debugging mode!'
            return ui.DEBUG_MODE and info or ''

        def additional_info():
            # Displays additional info as a main menu footer.
            # Start with empty list:
            info = []
            # Add ribbon filename, if any:
            if self.input_file:
                info.append('Input file name: ' + self.input_file)
            # Add ribbon filename, if any:
            if self.output_file:
                info.append('Output file name: ' + self.output_file)
            # Add a diecase info:
            if self.diecase:
                info.append('\nDiecase info:\n')
                info.append('Using diecase ID: ' + str(self.diecase_id))
                info.append('Typeface: ' + str(self.typeface))
                info.append('Series: ' + str(self.type_series))
                info.append('Size: ' + str(self.type_size))
                info.append('Stopbar/wedge: ' + str(self.wedge))
                info.append('Set width: ' + str(self.set_width))
                info.append('Diecase system: ' + str(self.diecase_system))
            # Get type variants from retrieved data:"""
                variants = []
                for variant in self.diecase_layout:
                    variants.append(variant)
                if variants:
                    info.append('Variants: ' + ', '.join(variants) + '\n')
        # Add a desired measure (line length):"""
            if self.line_length:
                info.append('Line length: %i %s'
                            % (self.line_length, self.measurement))
        # Unit line length in 1-set (fundamental) units:"""
            if self.fu_line_length:
                info.append('Line length in 1-set units: %i'
                            % self.fu_line_length)
        # Unit line length in multiset units:"""
            if self.unit_line_length:
                info.append('Line length in %i-set units: %i'
                            % (self.set_width, self.unit_line_length))
        # Convert it all to a multiline string:"""
            return '\n'.join(info)
        # End of subroutines.
        # Now construct a menu.
        # Commands: {option_name : function}
        hdr = ('rpi2caster - CAT (Computer-Aided Typecasting) '
               'for Monotype Composition or Type and Rule casters. \n\n'
               'This program reads a ribbon (input file) and casts the type '
               'on a Composition Caster, \n'
               'or punches a paper tape with a pneumatic perforator.' +
               debug_notice() + '\n\nMain Menu:')
        # Option list for menu:
        options = [('Exit program', exceptions.exit_program),
                   ('Load a text file', choose_input_filename),
                   ('Specify an output file name', choose_output_filename),
                   ('Choose diecase', self.choose_diecase),
                   ('Display diecase layout', self.display_diecase_layout),
                   ('Enter line length', self.enter_line_length),
                   ('Calculate units', self.calculate_units),
                   ('Choose machine settings', self.choose_machine_settings),
                   ('Translate text to Monotype code', self.translate)]

        while True:
            # Call the function and return to menu.
            try:
                ui.menu(options, header=hdr, footer=additional_info())()
            except exceptions.ReturnToMenu:
                pass
            except (KeyboardInterrupt, exceptions.ExitProgram):
                ui.exit_program()

    def enter_line_length(self):
        """enter_line_length():

        Sets the line length and allows to specify measurement units.
        """
        prompt = 'Enter the desired line length: '
        self.line_length = ui.enter_data_spec_type(prompt, float)
        # The line length is set.
        # Now choose the measurement units from a menu.
        options = {'c': 'cicero',
                   'b': 'britPica',
                   'a': 'amerPica',
                   'cm': 'cm',
                   'mm': 'mm',
                   'in': 'in'}
        message = ('Select measurement units:\n'
                   'a - American pica (0.1660"),\n'
                   'b - British pica (0.1667"),\n'
                   'c - Didot cicero (0.1776"),\n'
                   'cm - centimeters,\n'
                   'mm - millimeters,\n'
                   'in - inches\n')
        choice = ui.simple_menu(message, options)
        self.measurement = options[choice]

    def choose_diecase(self):
        """Choose diecase:

        Placeholder: we'll import hardcoded 327-12 TNR for now...
        """
        self.diecase = matrix_data.diecase_by_id('327-12-KS01')
        (self.diecase_id, self.type_series, self.type_size, self.set_width,
         self.typeface,  wedge_series, self.diecase_layout) = self.diecase
        # Choose a wedge based on wedge number and set size:
        wedge_ua = wedge_data.wedge_by_name_and_width(wedge_series,
                                                      self.set_width)[4]
        # Get unit values for that wedge:
        self.wedge_units = {i : k for i, k in enumerate(wedge_ua, 1)}
        self.shifted_wedge_units = {i : k for i, k in enumerate(wedge_ua, 2)}

    def display_diecase_layout(self):
        """display_diecase_layout:

        Displays all characters, grouped by variant (roman, bold, italic,
        small caps, subscript, superscript) with their coordinates and unit
        values.

        Sanity check: we must have chosen a diecase first...
        TODO: make an option accessible in menu only if diecase is chosen.
        """
        if not self.diecase_layout:
            ui.display('Diecase not chosen, no layout to check!')
            time.sleep(1)
            self.main_menu()
        for variant in self.diecase_layout:
            ui.display('\nMatrices for variant: ' + variant + '\n\n' +
                       'Char:'.ljust(8) +
                       'Column:'.ljust(8) +
                       'Row:'.ljust(8) +
                       'Units:'.ljust(8))
            variantCharset = self.diecase_layout[variant]
            for character in variantCharset:
                parameters = variantCharset[character]
                column = parameters[0]
                row = parameters[1]
                try:
                    units = parameters[2]
                except IndexError:
                    units = self.wedgeUnits[row]
                # Now display the data:"""
                ui.display(character.strip().ljust(8) +
                           column.ljust(8) + str(row).ljust(8) +
                           str(units).ljust(8))
        # Keep displaying the data until user presses return:"""
        ui.confirm('Press return to go back to menu....')

    def choose_machine_settings(self):
        """choose_machine_settings:

        Chooses the machine settings - diecase format (15x15, 15x17,
        16x17 HMN, KMN or unit-shift), justification mode
        (0005, 0075 or NJ, NK) and whether there's a unit-shift attachment.

        TODO: implement the function
        """
        pass

    def translate(self):
        """translate:

        A proper translation routine. It calculates unit widths of characters,
        and adds them, then warns the operator if the line is near filling.

        TODO: add description,
        TODO: work on this routine and make justified type,
        TODO: implement TeX hyphenation algorithm
        """
        if not self.input_file or not self.output_file:
            ui.display('You must specify the input '
                       'and output filenames first!')
            time.sleep(1)

    @staticmethod
    def calculate_wedges(set_width, units):
        """calculate_wedges(set_width, units):

        Calculate the 0005 and 0075 wedge positions based on the unit width
        difference (positive or negative) for the given set width.

        Since one step of 0075 wedge is 15 steps of 0005, we'll get a total
        would-be number of 0005 steps, then floor-divide it by 15 to get the
        0075 steps, and modulo-divide by 15 to get 0005 steps.

        If number of 0075 steps or 0005 steps is 0, we'll set 1 instead,
        because the wedge cannot have a "0" position.

        The function returns a list: [pos0075, pos0005].

        Maths involved may be a bit daunting, but it's not rocket science...
        First, we need to derive the width in inches of 1 unit 1 set:

        1p [pica] = 1/6" = 0.1667" (old pica), or alternatively:
        1p = 0.1660" (new pica - closer to the Fournier system).
        1p = 12pp [pica-points]. So, 1pp = 1/12p * 1/6["/p] = 1/72".

        In continental Europe, they used ciceros and Didot points:
        1c = 0.1776"
        1c = 12D - so, 1D = 0.0148"

        A set number of the type is the width of an em (i.e., widest char).
        It can, but doesn't have to, be the same as the type size in pp.
        Set numbers were multiples of 1/4, so we can have 9.75, 10, 11.25 etc.

        For example, 327-12D Times New Roman is 12set (so, it's very close),
        but condensed type will have a lower set number.

        And 1 Monotype fundamental unit is defined as 1/18em. Thus, the width
        of 1 unit 1 set = 1/18 pp; 1 unit multi-set = set_width/18 pp.

        All things considered, let's convert the unit to inches:

        Old pica:
        W(1u 1set) = 1/18 * 1/72" = 1/1296"

        The width in inches    of a given no of units at a given set size is:
        W = s * u / 1296
        (s - set width, u - no of units)

        Now, we go on to explaining what the S-needle does.
        It's used for modifying (adding/subtracting) the width of a character
        to make it wider or narrower, if it's needed (for example, looser or
        tighter spaces when justifying a line).

        When S is disengaged (e.g. G5), the lower transfer wedge (62D)
        is in action. The justification wedges (10D, 11D) have nothing to do,
        and the character width depends solely on the matrix's row and its
        corresponding unit value.

        Suppose we're using a S5 wedge, and the unit values are as follows:
        row     1 2 3 4 5 6 7 8  9  10 11 12 13 14 15
        units   5 6 7 8 9 9 9 10 10 11 12 13 14 15 18
        (unless unit-shift is engaged)

        The S5 wedge moves with a matrix case, and for row 1, the characters
        will be 5 units wide. So, the width will be:
        W(5u) = set_width * 5/1296 = 0.003858" * set_width.

        Now, we want to cast the character with the S-needle.
        Instead of the lower transfer wedge 62D, the upper transfer wedge 52D
        together with justification wedges 10D & 11D affect the character's
        width. The 10D is a coarse justification wedge and adds/subtracts
        0.0075" per step; the 11D is a fine justification wedge and changes
        width by 0.0005" peru step. The wedges can have one of 15 positions.

        Notice that 0.0075 = 15 x 0.0005 (so, 0.0005 at 15 equals 0.0075 at 1).
        Position 0 or >15 is not possible.S

        Also notice that 0.0005" precision would mean a resolution of 2000dpi -
        beat that, Hewlett-Packard! :).

        Now, we can divide the character's width in inches by by 0.0005
        (or multiply by 2000) and we get a number of 0005 wedge steps
        to cast the character with the S needle. It'll probably be more than
        15, so we need to floor-divide the number to get 0075 wedge steps,
        and modulo-divide it to get 0005 steps:

        steps = W * 2000                    (round that to integer)
        steps0075 = steps // 15     (floor-divide)
        steps0005 = steps % 15        (modulo-divide)

        The equivalent 0005 and 0075 wedge positions for a 5-unit character
        in the 1st row (if we decide to cast it with the S-needle) will be:

        steps = 5/1296 * 2000 * set_width

        (so it is proportional to set width).
        For example, consider the 5 unit 12 set type, and we have:

        steps = 5 * 12 * 2000 / 1296 = 92.6
        so, steps = 92
        steps // 15 = 6
        steps % 15 = 2

        So, the 0075 wedge will be at pos. 6 and 0005 will be at 3.

        If any of the wedge step numbers is 0, set 1 instead (a wedge must
        be in position 1...15).
        """
        steps = 2000/1296 * set_width * units
        steps = int(steps)
        steps0075 = steps // 15
        steps0005 = steps % 15
        if not steps0075:
            steps0075 = 1
        if not steps0005:
            steps0005 = 1
        return [steps0075, steps0005]

    def calculate_line_length(self):
        """calculate_line_length():

        Calculates the line length in Monotype fundamental (1-set) units.

        We must know the line length and measurement unit first.
        If not, throw an error.
        """
        inchWidth = {'britPica': 0.1667,
                     'amerPica': 0.1660,
                     'cicero': 0.1776,
                     'mm': 0.03937,
                     'cm': 0.3937,
                     'in': 1}
        if self.measurement not in inchWidth:
            return False
        # Base em width is a width (in inches) of a single em -
        # which, by the Monotype convention, is defined as 18 units 12 set.
        # Use American pica (0.166") value only if specified; other systems
        # use British pica (0.1667").
        if self.measurement == 'amerPica':
            baseEmWidth = inchWidth['amerPica']
        else:
            baseEmWidth = inchWidth['britPica']
        # To calculate the inch width of a fundamental unit (1-unit 1-set),
        # we need to divide the British or American pica length in inches
        # by 12*18 = 216:
        fundamentalUnitWidth = baseEmWidth / 216
        # Convert the line length in picas/ciceros to inches:
        inch_line_length = self.line_length * inchWidth[self.measurement]
        # Now, we need to calculate how many units of a given set
        # the row will contain. Round that to an integer and return the result.
        self.fu_line_length = round(inch_line_length / fundamentalUnitWidth)

    def calculate_units(self):
        """calculate_units:

        Calculates line length in 1-set units, and if the set number is given,
        calculates in multi-set units as well.
        """
        if self.measurement and self.line_length:
            self.calculate_line_length()
        else:
            ui.display('Line length and meas. units not specified!')
            time.sleep(1)
            self.main_menu()
        # Calculate the multi-set unit value:
        try:
            self.unit_line_length = round(self.fu_line_length / self.set_width)
        except ZeroDivisionError:
            pass

    @staticmethod
    def calculate_space_width(spaces, unitsLeft):
        """Space width calculation for justification.

        Divides the remaining length of line by the number of spaces in line.
        Rounds the result down.
        The min space width is 3 units wide; if the result is smaller,
        the function returns 3 units.
        """
        spaceWidth = unitsLeft % spaces
        if spaceWidth < 3:
            spaceWidth = 3
        return spaceWidth

    def __exit__(self, *args):
        ui.debug_info('Exiting typesetting job context.')
