# -*- coding: utf-8 -*-
"""
casting:

A module for everything related to working on a Monotype composition caster:
-casting composed type,
-punching paper tape (ribbon) for casters without interfaces,
-casting l lines of m sorts from matrix with x, y coordinates,
-composing and casting a line of text
-testing all valves, lines and pinblock,
-calibrating the space transfer wedge,
-heating the mould up,
-sending any codes/combinations to the caster and keeping them on.
"""

# IMPORTS:
# Signals parsing methods for rpi2caster
from . import parsing
# Custom exceptions
from . import exceptions
# Constants shared between modules
from . import constants
# Typesetting functions module
from . import typesetting_funcs
# Read ribbon files
from . import typesetting_data
# Caster backend
from . import monotype
# Modules imported in the typesetting_data - matrix_data - wedge_data
# No need to import them again - just point to them
matrix_data = typesetting_data.matrix_data
wedge_data = matrix_data.wedge_data
# User interface is the same as in typesetting_data
UI = typesetting_data.UI


def use_caster(func):
    """Method decorator for requiring the caster context"""
    def func_wrapper(self, *args, **kwargs):
        """Wrapper function"""
        with self.caster:
            return func(self, *args, **kwargs)
    return func_wrapper


def change_sensor(func):
    """Method decorator for using perforator sensor when punching ribbon"""
    def func_wrapper(self, *args, **kwargs):
        """Sets the perforator sensor"""
        if self.caster.is_perforator:
            sensor = monotype.PerforatorSensor()
        else:
            sensor = self.caster.sensor or monotype.Sensor()
        with sensor as self.caster.sensor:
            return func(self, *args, **kwargs)
    return func_wrapper


def set_output_driver(func):
    """Method decorator for using perforator sensor when punching ribbon"""
    def func_wrapper(self, *args, **kwargs):
        """Sets the perforator sensor"""
        if not self.caster.simulation_mode:
            driver = monotype.wiringpi_output_driver()
        else:
            driver = self.caster.output_driver or monotype.OutputDriver()
        with driver as self.caster.output_driver:
            return func(self, *args, **kwargs)
    return func_wrapper


def cast_result(func):
    """After finished, ask for confirmation and cast the resulting ribbon"""
    def func_wrapper(self, *args, **kwargs):
        """Wrapper function"""
        ribbon = func(self, *args, **kwargs)
        if UI.yes_or_no('Cast it?'):
            return self.cast_composition(ribbon)
        else:
            return False
    return func_wrapper


class Casting(object):
    """Casting:

    Methods related to operating the composition caster.
    Requires configured caster.

    All methods related to operating a composition caster are here:
    -casting composition and sorts, punching composition,
    -calibrating the caster,
    -testing the interface,
    -sending an arbitrary combination of signals,
    -casting spaces to heat up the mould."""

    def __init__(self, ribbon_file=''):
        # Caster for this job
        self.caster = monotype.MonotypeCaster()
        # Ribbon object, start with a default empty ribbon
        if ribbon_file:
            self.ribbon = typesetting_data.choose_ribbon(filename=ribbon_file)
        else:
            # Start with empty ribbon
            self.ribbon = typesetting_data.EmptyRibbon()
        self.diecase = self.ribbon.diecase
        self.wedge = self.diecase.wedge
        # Indicates which line the last casting was aborted on
        self.line_aborted = 0

    @change_sensor
    @set_output_driver
    @use_caster
    def cast_composition(self, casting_queue=None):
        """cast_composition()

        Composition casting routine. The input file is read backwards -
        last characters are cast first, after setting the justification.
        """
        # Casting queue - if not defined, use self.ribbon.contents
        casting_queue = casting_queue or self.ribbon.contents
        # Count all characters and lines in the ribbon
        (all_lines, all_chars) = parsing.count_lines_and_chars(
            casting_queue)
        # Show the numbers to the operator
        UI.display('Lines found in ribbon: %i' % all_lines)
        UI.display('Characters: %i' % all_chars)
        # Check the line previous job has been aborted on
        # Ask how many lines to skip; add two previous lines if possible
        # so that the mould temperature has a chance to stabilize
        lines_skipped = self.line_aborted - 2
        # This must be non-negative
        lines_skipped = max(lines_skipped, 0)
        UI.display('You can skip a number of lines so that you can e.g. start '
                   'a casting job aborted earlier.')
        prompt = 'How many lines to skip? (default: %s) : ' % lines_skipped
        lines_skipped = (UI.enter_data_or_blank(prompt, int) or
                         lines_skipped)
        prompt = 'How many times do you want to cast this? (default: 1) : '
        repetitions = UI.enter_data_or_blank(prompt, int) or 1
        # For casting, we need to check the direction of ribbon
        if parsing.rewind_ribbon(casting_queue):
            UI.display('Ribbon starts with pump stop sequence - rewinding...')
            queue = [line for line in reversed(casting_queue)]
        else:
            UI.display('Ribbon starts with galley trip - not rewinding...')
            queue = [line for line in casting_queue]
        # Display a little explanation
        UI.display('\nThe combinations of Monotype signals will be displayed '
                   'on screen while the machine casts the type.\n'
                   'Turn on the machine and the program will start.\n')
        # Start only after the machine is running
        self.caster.detect_rotation()
        # Current run number - (start with 1 and increase)
        current_run = 1
        # Repeat casting the whole sequence as many times as we would like
        while current_run <= repetitions:
            UI.display('\n\nSTARTING THE CASTING RUN %d / %d (%d left)...\n\n'
                       % (current_run, repetitions, repetitions - current_run))
            current_run += 1
            # Characters already cast, lines done - start with zero
            current_char = 0
            lines_done = 0
            chars_left = all_chars
            # Line currently cast: since the caster casts backwards
            # (from the last to the first line), this will decrease.
            current_line = all_lines
            # Read the reversed file contents, line by line, then parse
            # the lines, display comments & code combinations, and feed the
            # combinations to the caster
            for record in queue:
                # Parse the row, return a list of signals and a comment.
                # Both can have zero or positive length.
                [signals, comment] = parsing.comments_parser(record)
                # A list with information for user: signals, comments, etc.
                info_for_user = []
                if parsing.check_newline(signals):
                    # Percent of all lines done:
                    line_percent_done = 100 * lines_done / all_lines
                    # Up the completed lines counter
                    lines_done += 1
                    # Display number of the working line,
                    # number of all remaining lines, percent done
                    if not current_line:
                        info = ('All lines successfully cast. '
                                'Putting the last line to the galley...\n')
                        info_for_user.append(info)
                    else:
                        # Decrease the counter for each started new line
                        msg = ('Starting line no. %i (%i of %i), %i remaining '
                               '[%i%% done]...\n' %
                               (current_line, lines_done, all_lines,
                                all_lines - lines_done, line_percent_done))
                        info_for_user.append(msg)
                        # Decrease the line counter
                        current_line -= 1
                elif parsing.check_character(signals):
                    # Increase the current character and decrease characters
                    # left, then do some calculations
                    current_char += 1
                    chars_left -= 1
                    # % of chars to cast in the line
                    char_percent_done = 100 * (current_char - 1) / all_chars
                    # Display number of chars done,
                    # number of all and remaining chars, % done
                    msg = ('Casting line no. %i (%i of %i), character: '
                           '%i of %i, %i remaining [%i%% done]...\n'
                           % (current_line, lines_done, all_lines,
                              current_char, all_chars,
                              chars_left, char_percent_done))
                    info_for_user.append(msg)
                # Skipping the unneeded lines:
                # Just don't cast anything until we get to the correct line
                if lines_done <= lines_skipped:
                    continue
                # Display wedge positions and pump status
                wedges_info = ('0075 wedge at %s, 0005 wedge at %s\n'
                               % (self.caster.current_0005,
                                  self.caster.current_0075))
                info_for_user.append(wedges_info)
                # Got to check before we display info
                self.caster.pump.check_working(signals)
                info_for_user.append(self.caster.pump.status() + '\n')
                # Add comment
                info_for_user.append(comment + '\n')
                # Display the info
                UI.display(''.join(info_for_user))
                # Proceed with casting only if code is explicitly stated
                # (i.e. O15 = cast, empty list = don't cast)
                if signals:
                    try:
                        self.caster.process_signals(signals)
                    except exceptions.CastingAborted:
                        # On failure - abort the whole job.
                        # Check the aborted line so we can get back to it.
                        self.line_aborted = current_line
                        UI.confirm('\nCasting aborted on line %i.'
                                   % self.line_aborted, UI.MSG_MENU)
                        return False
        # After casting is finished, notify the user
        UI.confirm('Casting finished successfully!', UI.MSG_MENU)
        return True

    @use_caster
    @set_output_driver
    @change_sensor
    def punch_composition(self, punching_queue=None):
        """punch_composition():

        When punching, the input file is read forwards. An additional line
        (O+15) is switched on for operating the paper tower to exert enough
        force to drive the punches and advance the ribbon.
        This mode uses arbitrary timings for air on / off phases.
        """
        # Punching queue - if not defined, use self.ribbon.contents
        punching_queue = punching_queue or self.ribbon.contents
        # Count a number of combinations punched in ribbon
        all_combinations = parsing.count_combinations(punching_queue)
        UI.display('Combinations in ribbon: %i' % all_combinations)
        # Wait until the operator confirms.
        UI.confirm('\nThe combinations of Monotype signals will be displayed '
                   'on screen while the paper tower punches the ribbon.\n'
                   'Turn on the air and fit the tape on your paper tower.')
        for line in punching_queue:
            # Parse the row, return a list of signals and a comment.
            # Both can have zero or positive length.
            [signals, comment] = parsing.comments_parser(line)
            # A string with information for user: signals, comments, etc.
            UI.display(' '.join(signals).ljust(20) + comment)
            # Send the signals
            if signals:
                self.caster.process_signals(signals)
        # After punching is finished, notify the user:"""
        UI.confirm('\nPunching finished!', UI.MSG_MENU)
        return True

    @use_caster
    def test_air_signals(self, combinations):
        """Tests a sequence of signals specified on input"""
        for code in combinations:
            UI.display(code)
            code = parsing.signals_parser(code)
            self.caster.process_signals(code, timeout=120)
        UI.confirm('\nTesting finished!', UI.MSG_MENU)

    def test_front_pinblock(self):
        """test_front_pinblock():

        Tests all valves and composition caster's inputs on the front pinblock
        to check if everything works and is properly connected.
        Signals will be tested in order: 1 towards 14.
        """
        intro = ('This will test the front pinblock - signals 1 towards 14. '
                 'At the end O+15 will be activated.')
        UI.confirm(intro)
        self.test_air_signals([str(n) for n in range(1, 15)])

    def test_rear_pinblock(self):
        """test_rear_pinblock():

        Tests all valves and composition caster's inputs on the rear pinblock
        to check if everything works and is properly connected.
        Signals will be tested in order: NI, NL, A...N, O+15.
        """
        intro = ('This will test the front pinblock - signals NI, NL, A...N. '
                 'At the end O+15 will be activated.')
        UI.confirm(intro)
        self.test_air_signals(constants.COLUMNS_17)

    def test_all(self):
        """test_all():

        Tests all valves and composition caster's inputs in original
        Monotype order: NMLKJIHGFSED 0075 CBA 123456789 10 11 12 13 14 0005.
        At the end O+15 signal is tested also.
        """
        intro = ('This will test all the air lines in the same order '
                 'as the holes on the paper tower: \n%s\n'
                 'At the end O+15 signal is tested.\n'
                 'MAKE SURE THE PUMP IS DISENGAGED.'
                 % ' '.join(constants.SIGNALS))
        UI.confirm(intro)
        self.test_air_signals(constants.SIGNALS)

    def cast_sorts(self):
        """cast_sorts():

        Sorts casting routine, based on the position in diecase.
        Ask user about the diecase row & column, as well as number of sorts.
        """
        # We need to choose a wedge unless we did it earlier
        wedge = self.wedge or wedge_data.Wedge()
        while True:
            # Outer loop
            UI.clear()
            UI.display('Sorts casting by matrix coordinates\n\n')
            prompt = 'Column: NI, NL, A...O? (default: G): '
            # Got no signals? Use G5.
            column = ''
            column_symbols = ['NI', 'NL'] + [ltr for ltr in 'ABCDEFGHIJKLMNO']
            while column not in column_symbols:
                column = UI.enter_data_or_blank(prompt).upper() or 'G'
            prompt = 'Row: 1...16? (default: 5): '
            # Initially set this to zero to enable the while loop
            row = 0
            units = 0
            # Ask for row number
            while row not in range(1, 17):
                try:
                    row = UI.enter_data_or_blank(prompt, int) or 5
                    row = abs(row)
                except (TypeError, ValueError):
                    # Repeat loop and enter new one
                    row = 0
            # If we want to cast from row 16, we need unit-shift
            # HMN or KMN systems are not supported yet
            question = 'Trying to access 16th row. Use unit shift?'
            unit_shift = row == 16 and UI.yes_or_no(question)
            if row == 16 and not unit_shift:
                UI.confirm('Aborting.')
                continue
            # Correct the column number if using unit shift
            if unit_shift:
                row = 15
                column = column.replace('D', 'E F')
                column += ' D'
            # Determine the unit width for a row
            row_units = wedge.unit_arrangement[row]
            # Enter custom unit value (no points-based calculation yet)
            prompt = 'Unit width value? (decimal, default: %s) : ' % row_units
            while not 2 < units < 25:
                units = (UI.enter_data_or_blank(prompt, float) or
                         row_units)
            # Calculate the unit width difference and apply justification
            diff = units - row_units
            calc = typesetting_funcs.calculate_wedges
            wedge_positions = calc(diff, wedge.set_width, wedge.brit_pica)
            signals = column
            if diff:
                # If we need to correct the width - cast with the S needle
                signals += ' S '
            signals += str(row)
            # Ask for number of sorts and lines, no negative numbers here
            prompt = '\nHow many sorts per line? (default: 10): '
            sorts = abs(UI.enter_data_or_blank(prompt, int) or 10)
            prompt = '\nHow many lines? (default: 1): '
            lines = abs(UI.enter_data_or_blank(prompt, int) or 1)
            # Warn if we want to cast too many sorts from a single matrix
            warning = ('Warning: you want to cast a single character more than'
                       ' 10 times. This may lead to matrix overheating!\n')
            if sorts > 10:
                UI.display(warning)
            # After entering parameters, ask the operator if they're OK
            try:
                while True:
                    # Inner loop
                    # Menu subroutines
                    def cast_it():
                        """Cast the combination or go back to menu"""
                        if self.cast_from_matrix(signals, sorts, lines,
                                                 wedge_positions):
                            UI.display('Casting finished successfully.')
                        else:
                            raise exceptions.ReturnToMenu
                    # End of menu subroutines.
                    options = {'C': cast_it,
                               'D': exceptions.change_parameters,
                               'M': exceptions.return_to_menu,
                               'E': exceptions.exit_program}
                    message = ('Casting %s, %i lines of %i sorts.\n'
                               '[C]ast it, [D]ifferent code/quantity, '
                               '[M]enu or [E]xit? '
                               % (signals, lines, sorts))
                    UI.simple_menu(message, options)()
            except exceptions.ChangeParameters:
                # Skip the menu and casting altogether, repeat the outer loop
                pass

    def cast_spaces(self):
        """cast_spaces():

        Spaces casting routine, based on the position in diecase.
        Ask user about the space width and measurement unit.
        """
        # Ask about line length
        prompt = 'Galley line length? [pica or cicero] (default: 25) : '
        line_length = UI.enter_data_or_blank(prompt, int) or 25
        line_length = abs(line_length)
        # Measurement system
        options = {'A': 0.1660,
                   'B': 0.1667,
                   'D': 0.1776,
                   'F': 0.1629}
        message = ('Measurement? [A]merican Johnson pica = 0.166", '
                   '[B]ritish pica = 0.1667",\n [D]idot cicero = 0.1776", '
                   '[F]ournier cicero = 0.1629": ')
        pica_def = UI.simple_menu(message, options)
        # We need to choose a wedge unless we did it earlier
        wedge = self.wedge or wedge_data.Wedge()
        # Unit line length:
        unit_line_length = int(18 * pica_def / 0.1667 * line_length *
                               wedge.set_width / 12)
        # Now we can cast multiple different spaces
        while True:
            UI.clear()
            UI.display('Spaces / quads casting\n\n')
            prompt = 'Column: NI, NL, A...O? (default: G): '
            # Got no signals? Use G5.
            column = ''
            column_symbols = ['NI', 'NL'] + [ltr for ltr in 'ABCDEFGHIJKLMNO']
            while column not in column_symbols:
                column = UI.enter_data_or_blank(prompt).upper() or 'G'
            prompt = 'Row: 1...16? (default: 2): '
            # Initially set this to zero to enable the while loop
            row = 0
            width = 0
            # Not using unit shift by default
            unit_shift = False
            # Ask for row number
            while row not in range(1, 17):
                try:
                    row = UI.enter_data_or_blank(prompt, int) or 2
                    row = abs(row)
                except (TypeError, ValueError):
                    # Repeat loop and enter new one
                    row = 0
            # If we want to cast from row 16, we need unit-shift
            # HMN or KMN systems are not supported yet
            question = 'Trying to access 16th row. Use unit shift?'
            unit_shift = row == 16 and UI.yes_or_no(question)
            if row == 16 and not unit_shift:
                UI.confirm('Aborting.')
                continue
            if unit_shift:
                row = 15
                column = column.replace('D', 'E F')
                column += ' D'
            # Determine the unit width for a row
            row_units = wedge.unit_arrangement[row]
            prompt = '\nHow many lines? (default: 1): '
            lines = abs(UI.enter_data_or_blank(prompt, int) or 1)
            # Space width in points
            options = {'6': 1/6,
                       '4': 1/4,
                       '3': 1/3,
                       '2': 1/2,
                       '1': 1,
                       'C': 0}
            message = ('Space width? [6] = 1/6em, [4] = 1/4em, [3] = 1/3em, '
                       '[2] = 1/2em, [1] = 1em, [C] for custom width: ')
            # Width in points
            width = UI.simple_menu(message, options) * 12
            # Ask about custom value, then specify units
            while not 1 <= width <= 20:
                prompt = 'Custom width in points (decimal, 1...20) ? : '
                width = UI.enter_data_or_blank(prompt, float)
            # We now have width in pica points
            # If we don't use an old British pica wedge, we must take
            # the pica difference into account
            # Calculate unit width of said number of points
            # We do it this way:
            # units = picas * set_width/12 * 18
            # a pica is 12 points, so:
            # units = points * set_width/12 * 1 / 12 * 18
            # 18 / (12*12) = 0.125, hence division by 8
            factor = pica_def / 0.1667
            sort_units = round(width * factor * wedge.set_width / 8, 2)
            # How many spaces will fit in a line? Calculate it...
            # We add 5 em-quads at O15 before and after the proper spaces
            # We need 180 additional units for that - need to subtract
            allowance = unit_line_length - 180
            sorts_number = int(allowance // sort_units)
            # The first line will be filled to the brim with em-quads
            # i.e. 18-unit spaces
            # Put as many as we can
            quads_number = int(unit_line_length // 18)
            # Check if the corrections are needed at all
            diff = sort_units - row_units
            calc = typesetting_funcs.calculate_wedges
            wedge_positions = calc(diff, wedge.set_width, wedge.brit_pica)
            signals = column
            if diff:
                # If we need to correct the width - cast with the S needle
                signals += ' S '
            signals += str(row)
            # Determine the number of quads per line to cast
            # After entering parameters, ask the operator if they're OK
            try:
                while True:
                    # Inner loop
                    # Menu subroutines
                    def cast_it():
                        """Cast the combination or go back to menu"""
                        message = ('\nFirst, we cast a line of em-quads '
                                   'to heat up the mould. Discard them.\n')
                        UI.display(message)
                        self.cast_from_matrix('O15', quads_number)
                        for num in range(lines):
                            UI.display('Now casting line %s' % str(num + 1))
                            UI.display('\nFive quads before - discard them.\n')
                            self.cast_from_matrix('O15', end_galley_trip=False,
                                                  machine_check=False)
                            UI.display('\nSpaces of desired width...\n')
                            self.cast_from_matrix(signals, sorts_number, 1,
                                                  wedge_positions,
                                                  end_galley_trip=False,
                                                  machine_check=False)
                            UI.display('\nFive quads after - discard them.\n')
                            self.cast_from_matrix('O15', machine_check=False)
                    # End of menu subroutines.
                    options = {'C': cast_it,
                               'D': exceptions.change_parameters,
                               'M': exceptions.return_to_menu,
                               'E': exceptions.exit_program}
                    info = ['Row: %s' % row,
                            'Column: %s' % column,
                            'Width in points: %s' % width,
                            'Width in %s-set units: %s' % (wedge.set_width,
                                                           sort_units),
                            '0075 wedge at: %s' % wedge_positions[0],
                            '0005 wedge at: %s' % wedge_positions[1],
                            'Line length in picas/ciceros: %s' % line_length,
                            'Number of sorts per line: %s' % sorts_number,
                            'Number of lines: %s' % lines]
                    for message in info:
                        UI.display(message)
                    message = ('[C]ast it, [D]ifferent parameters, '
                               '[M]enu or [E]xit? ')
                    UI.simple_menu(message, options)()
            except exceptions.ChangeParameters:
                # Skip the menu and casting altogether, repeat the outer loop
                pass

    @use_caster
    def cast_from_matrix(self, signals, num=5, lines=1,
                         wedge_positions=(3, 8),
                         start_galley_trip=False,
                         end_galley_trip=True,
                         machine_check=True):
        """cast_from_matrix(combination, n, lines, (pos0075, pos0005)):

        Casts n sorts from combination of signals (list),
        with correction wedges if S needle is in action.

        By default, it sets 0075 wedge to 3 and 0005 wedge to 8 (neutral).
        Determines if single justification (0075 only) or double
        justification (0005 + 0075) is used.

        N, K and J signals are for alternate justification scheme,
        used with unit-adding attachment and turned on/off with a large
        IN/OUT valve at the backside of the caster:
        NJ = 0005
        NK = 0075
        NKJ = 0005 + 0075
        """
        # Reset the aborted line counter
        self.line_aborted = 0
        (pos_0075, pos_0005) = (str(x) for x in wedge_positions)
        # Signals for setting 0005 and 0075 justification wedges
        # Strip O and 15
        set_0005 = parsing.signals_parser('N J S 0005 %s' % pos_0005)
        set_0075 = parsing.signals_parser('N K S 0075 %s' % pos_0075)
        # Galley trip signal
        galley_trip = parsing.signals_parser('N K J S 0005 0075 %s' % pos_0005)
        # Parse the combination
        combination = parsing.signals_parser(signals)
        # Check if the machine is running first, end here if not
        if machine_check:
            UI.display('Start the machine...')
            self.caster.detect_rotation()
        # We're here because the machine is rotating. Start casting the job...
        for current_line in range(1, lines + 1):
            # Cast each line and if the CastingAborted exception is caught,
            # remember the last line and stop casting.
            try:
                # Cast the sorts: set wedges, turn pump on, cast, line out
                # Set up the justification, turn the pump on
                UI.display('Casting line %i of %i' % (current_line, lines))
                UI.display('0005 wedge at ' + pos_0005)
                UI.display('0075 wedge at ' + pos_0075)
                if start_galley_trip:
                    # Double justification
                    UI.display('Putting the line out...')
                    self.caster.process_signals(galley_trip)
                else:
                    # Starting a job
                    self.caster.process_signals(set_0005)
                UI.display('Starting the pump...')
                self.caster.process_signals(set_0075)
                # Start casting characters
                UI.display('Casting characters...')
                # Cast n combinations of row & column, one by one
                for i in range(1, num + 1):
                    info = ('%s - casting character %i of %i, %i%% done.'
                            % (' '.join(combination).ljust(20),
                               i, num, 100 * i / num))
                    UI.display(info)
                    combination = parsing.strip_o15(combination)
                    self.caster.process_signals(combination)
                if end_galley_trip:
                    # If everything went normally, put the line to the galley
                    UI.display('Putting line to the galley...')
                    self.caster.process_signals(galley_trip)
                    # After casting sorts we need to stop the pump
                UI.display('Stopping the pump...')
                self.caster.process_signals(set_0005)
            except exceptions.CastingAborted:
                self.line_aborted = current_line
                UI.display('Casting aborted on line %i' % self.line_aborted)
                return False
        # We'll be here if casting ends successfully
        return True

    @use_caster
    def send_combination(self):
        """send_combination():

        This function allows us to give the program a specific combination
        of Monotype codes, and will keep the valves on until we press return
        (useful for calibration). It also checks the signals' validity.
        """
        while True:
            # You can enter new signals or exit
            prompt = ('Enter the signals to send to the caster, '
                      'or leave empty to return to menu: ')
            signals = UI.enter_data_or_blank(prompt)
            # Turn off any valves that were on (from previous combination)
            self.caster.deactivate_valves()
            if not signals:
                # Escape the infinite loop here
                raise exceptions.ReturnToMenu
            # Parse the combination, get the signals (first item returned
            # by the parsing function)
            signals = parsing.signals_parser(signals)
            # Turn the valves on
            UI.display(' '.join(signals))
            self.caster.activate_valves(signals)
            # Start over.

    def align_wedges(self, space_position='G5'):
        """align_wedges(space_position='G5'):

        Allows to align the justification wedges so that when you're
        casting a 9-unit character with the S-needle at 0075:3 and 0005:8
        (neutral position), the    width is the same.

        It works like this:
        1. 0075 - turn the pump on,
        2. cast 10 spaces from the specified matrix (default: G9),
        3. put the line to the galley & set 0005 to 8, 0075 to 3, pump on,
        4. cast 10 spaces with the S-needle from the same matrix,
        5. put the line to the galley, then 0005 to turn the pump off.
        """
        intro = ('Transfer wedge calibration:\n\n'
                 'This function will cast 10 spaces, then set the correction '
                 'wedges to 0075:3 and 0005:8, \nand cast 10 spaces with the '
                 'S-needle. You then have to compare the length of these two '
                 'sets. \nIf they are identical, all is OK. '
                 'If not, you have to adjust the 52D space transfer wedge.')
        UI.display(intro)
        while True:
            # Subroutines for menu options
            def continue_aligning():
                """Cast spaces with and without S-needle"""
                pass
            # Finished. Return to menu.
            options = {'C': continue_aligning,
                       'M': exceptions.return_to_menu,
                       'E': exceptions.exit_program}
            UI.simple_menu('\n[C]ontinue, [M]enu or [E]xit? ', options)()
            # Cast 10 spaces without correction.
            # End here if casting unsuccessful.
            UI.display('Now casting with a normal wedge only.')
            if not self.cast_from_matrix(space_position, 5):
                continue
            # Cast 10 spaces with the S-needle.
            # End here if casting unsuccessful.
            UI.display('Now casting with justification wedges...')
            if not self.cast_from_matrix(space_position + 'S', 5):
                continue
            # At the end of successful sequence, some info for the user:
            UI.display('Done. Compare the lengths and adjust if needed.')

    def align_mould(self):
        """align_mould:

        Calculates the width, displays it and casts some 9-unit characters.
        Then, the user measures the width and adjusts the mould opening width.
        """
        intro = ('Mould blade opening calibration:\n'
                 'Cast some 9-unit characters, then measure the width.\n'
                 'Adjust if needed.')
        UI.display(intro)
        # Use current wedge or select one
        wedge = self.wedge or wedge_data.Wedge()
        # Selected
        if wedge.brit_pica:
            pica = 0.1667
        else:
            pica = 0.166
        # We calculate the width of double 9 units = 18 units, i.e. 1 pica em
        em_width = pica * wedge.set_width / 12
        UI.display('Type 9 units (1en) width: %s' % round(em_width / 2, 4))
        UI.display('Type 18 units (1em) width: %s' % round(em_width, 4))
        while True:
            # Subroutines for menu options
            def continue_aligning():
                """Do nothing"""
                pass
            # Finished. Return to menu.
            options = {'C': continue_aligning,
                       'M': exceptions.return_to_menu,
                       'E': exceptions.exit_program}
            UI.simple_menu('\n[C]ontinue, [M]enu or [E]xit? ', options)()
            # Cast 5 nine-unit quads
            # End here if casting unsuccessful.
            UI.display('Now casting 9-units spaces')
            if not self.cast_from_matrix('G5', 7):
                continue
            # At the end of successful sequence, some info for the user:
            UI.display('Done. Compare the lengths and adjust if needed.')

    def align_diecase(self):
        """align_diecase:

        Casts the "en dash" characters for calibrating the character X-Y
        relative to type body.
        """
        intro = ('X-Y character calibration:\n'
                 'Cast some en-dashes and/or lowercase "n" letters, '
                 'then check the position of the character relative to the '
                 'type body.\nAdjust if needed.')
        UI.display(intro)
        try:
            # Find the en-dash automatically
            dash_position = [mat[2] + str(mat[3])
                             for mat in self.diecase.layout
                             if mat[0] == '–'][0]
        except (exceptions.MatrixNotFound, TypeError, IndexError):
            # Choose it manually
            dash_position = UI.enter_data_or_blank('En dash (–) at: ').upper()
        try:
            # Find the "n" letter automatically
            lowercase_n_position = [mat[2] + str(mat[3])
                                    for mat in self.diecase.layout
                                    if mat[0] == 'n'][0]
        except (exceptions.MatrixNotFound, TypeError, IndexError):
            # Choose itmanually
            lowercase_n_position = UI.enter_data_or_blank('"n" at: ').upper()
        while True:
            # Subroutines for menu options
            def continue_aligning():
                """Do nothing"""
                pass
            # Finished. Return to menu.
            options = {'C': continue_aligning,
                       'M': exceptions.return_to_menu,
                       'E': exceptions.exit_program}
            UI.simple_menu('\n[C]ontinue, [M]enu or [E]xit? ', options)()
            # Cast 5 nine-unit quads
            # End here if casting unsuccessful.
            if dash_position:
                UI.display('Now casting en dash')
                if not self.cast_from_matrix(dash_position, 7):
                    continue
            if lowercase_n_position:
                UI.display('Now casting lowercase "n"')
                if not self.cast_from_matrix(lowercase_n_position, 7):
                    continue
            # At the end of successful sequence, some info for the user:
            UI.display('Done. Compare the lengths and adjust if needed.')

    def line_casting(self):
        """line_casting:

        Allows us to use caster for casting single lines.
        This means that the user enters a text to be cast,
        gives the line length, chooses alignment and diecase.
        Then, the program composes the line, justifies it, translates it
        to Monotype code combinations.

        This allows for quick typesetting of short texts, like names etc.
        """
        # Initialize the typesetter for a chosen diecase
        typesetter = typesetting_funcs.Typesetter()
        # Supply the diecase id
        # TODO: refactor it to use the new diecase and wedge data model!
        typesetter.session_setup(self.diecase.diecase_id)
        # Enter text
        text = UI.enter_data("Enter text to compose: ")
        typesetter.text_source = typesetter.parse_and_generate(text)
        # Translate the text to Monotype signals
        typesetter.compose()
        self.ribbon.contents = typesetter.justify()
        # Ask whether to display buffer contents
        if UI.yes_or_no('Show the codes?'):
            self.ribbon.display_contents()
        # We're casting
        if UI.yes_or_no('Cast it?'):
            try:
                self.cast_composition()
            except exceptions.ReturnToMenu:
                # If casting aborted - don't go back to menu
                pass

    def heatup(self):
        """Casts 2 lines x 20 quads from the O15 matrix to heat up the mould"""
        UI.clear()
        self.cast_from_matrix('O15', num=20, lines=2)

    def diagnostics_submenu(self):
        """Settings and alignment menu for servicing the caster"""
        def menu_options():
            """Build a list of options, adding an option if condition is met"""
            perforator = self.caster.is_perforator
            opts = [(exceptions.menu_level_up, 'Back',
                     'Returns to main menu', True),
                    (self.test_all, 'Test outputs',
                     'Tests all the air outputs one by one', True),
                    (self.test_front_pinblock, 'Test the front pinblock',
                     'Tests the pins 1...14', not perforator),
                    (self.test_rear_pinblock, 'Test the rear pinblock',
                     'Tests the pins NI, NL, A...N one by one',
                     not perforator),
                    (self.send_combination, 'Send specified signals',
                     'Sends the specified signal combination', True),
                    (self.align_wedges, 'Adjust the 52D wedge',
                     'Calibrate the space transfer wedge for correct width',
                     not perforator),
                    (self.align_mould, 'Calibrate mould opening',
                     'Casts 9-unit characters to adjust the type width',
                     not perforator),
                    (self.align_diecase, 'Calibrate matrix X-Y',
                     'Calibrate the character-to-body positioning',
                     not perforator)]
            return [(function, description, long_description) for
                    (function, description, long_description, condition)
                    in opts if condition]

        header = ('Diagnostics and machine calibration menu:\n\n')
        # Keep displaying the menu and go back here after any method ends
        while True:
            try:
                # Catch "return to menu" and "exit program" exceptions here
                UI.menu(menu_options(), header=header)()
            except exceptions.ReturnToMenu:
                # Stay in the menu
                pass

    def _choose_ribbon(self):
        """Chooses a ribbon from database or file"""
        self.ribbon = typesetting_data.choose_ribbon()
        self.diecase = self.ribbon.diecase
        self.wedge = self.diecase.wedge

    def _choose_diecase(self):
        """Chooses a diecase from database"""
        self.diecase = matrix_data.choose_diecase()
        self.wedge = self.diecase.wedge

    def _choose_wedge(self):
        """Chooses a wedge from registered ones"""
        self.wedge = wedge_data.choose_wedge()

    def _display_additional_info(self):
        """Collect ribbon, diecase and wedge data here"""
        data = [(self.caster.name, 'Caster name'),
                (self.line_aborted, 'Last casting was aborted on line no')]
        data.extend(self.ribbon.get_parameters())
        data.extend(self.diecase.get_parameters())
        data.extend(self.wedge.get_parameters())
        info = ['%s: %s' % (desc, value) for (value, desc) in data if value]
        return '\n'.join(info)

    def _main_menu_options(self):
        """Build a list of options, adding an option if condition is met"""
        # Options are described with tuples: (function, description, condition)
        perforator = self.caster.is_perforator
        ribbon = self.ribbon.contents
        diecase_selected = self.diecase.diecase_id
        opts = [(exceptions.exit_program, 'Exit', 'Exits the program', True),
                (self._choose_ribbon, 'Select ribbon',
                 'Selects a ribbon from database or file', True),
                (self._choose_diecase, 'Select diecase',
                 'Selects a matrix case from database', True),
                (self._choose_wedge, 'Select wedge',
                 'Selects a wedge from database', True),
                (self.ribbon.display_contents, 'View codes',
                 'Displays all sequences in a ribbon', ribbon),
                (self.heatup, 'Heat the mould up',
                 'Casts some quads to heat up the mould', not perforator),
                (self.punch_composition, 'Punch composition',
                 'Punches a ribbon using a perforator', ribbon and perforator),
                (self.cast_composition, 'Cast composition',
                 'Casts type with a caster', ribbon and not perforator),
                (self.diecase.show_layout, 'Show diecase layout',
                 'Views the matrix case layout', diecase_selected),
                (self.line_casting, 'Ad-hoc typesetting',
                 'Compose and cast a line of text', diecase_selected),
                (self.cast_sorts, 'Cast sorts',
                 'Cast from matrix with given coordinates', not perforator),
                (self.cast_spaces, 'Cast spaces or quads',
                 'Casts spaces or quads of a specified width', not perforator),
                (self.diagnostics_submenu, 'Service...',
                 'Interface and machine diagnostic functions', True)]
        # Built a list of menu options conditionally
        return [(function, description, long_description)
                for (function, description, long_description, condition)
                in opts if condition]

    def main_menu(self):
        """main_menu:

        Calls UI.menu() with options, a header and a footer.
        Options: {option_name : description}
        Header: string displayed over menu
        Footer: string displayed under menu (all info will be added here).
        """
        header = ('rpi2caster - CAT (Computer-Aided Typecasting) '
                  'for Monotype Composition or Type and Rule casters.\n\n'
                  'This program reads a ribbon (from file or database) '
                  'and casts the type on a composition caster. \n\nMain Menu:')
        # Keep displaying the menu and go back here after any method ends
        while True:
            # Catch any known exceptions here
            try:
                UI.menu(self._main_menu_options(), header=header,
                        footer=self._display_additional_info())()
            except (exceptions.ReturnToMenu, exceptions.MenuLevelUp):
                # Will skip to the end of the loop, and start all over
                pass
