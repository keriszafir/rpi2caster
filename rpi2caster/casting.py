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
# Built-in time library
import time
# Signals parsing methods for rpi2caster
from rpi2caster import parsing
# User interfaces module for rpi2caster:
from rpi2caster.global_settings import USER_INTERFACE as ui
# Custom exceptions
from rpi2caster import exceptions
# Typesetting functions module
from rpi2caster import typesetting
# Diecase manipulation functions
from rpi2caster import matrix_data
# Wedge manipulation functions
from rpi2caster import wedge_data
# Read ribbon files
from rpi2caster import typesetting_data
# Constants shared between modules
from rpi2caster import constants


def use_caster(func):
    """Method decorator for requiring the caster context"""
    def func_wrapper(self, *args, **kwargs):
        """Wrapper function"""
        with self.caster:
            return func(self, *args, **kwargs)
    return func_wrapper


class Casting(object):
    """Casting:

    Methods related to operating the composition caster.
    Requires configured:
    -caster
    -database
    -UI.

    These attributes need to be set up before casting anything.
    Normally, you instantiate the Session class and it takes care of all
    setup work.

    Ribbon filename is also an object's attribute, but it's usually
    set up via user interaction. You can also feed the filename
    to class on init.

    All methods related to operating a composition caster are here:
    -casting composition and sorts,
    -calibrating the caster,
    -testing the interface,
    -sending an arbitrary combination of signals,
    -casting spaces to heat up the mould."""

    def __init__(self, ribbon_file=''):
        # Caster - this will be set up later
        self.caster = None
        # Ribbon object, start with a default empty ribbon
        self.ribbon = typesetting_data.Ribbon()
        # Diecase object, empty now
        self.diecase = matrix_data.Diecase()
        # Wedge object, create a default one first
        self.wedge = wedge_data.Wedge()
        # Automatically set up a ribbon, diecase and wedge if loaded with file
        self.setup_ribbon_file(ribbon_file)
        # Indicates which line the last casting was aborted on
        self.line_aborted = 0

    def __enter__(self):
        ui.debug_info('Entering casting job context...')
        main_menu()

    def setup_ribbon_file(self, ribbon_file=None):
        """Sets up the ribbon if filename was given as a cmdline argument"""
        if ribbon_file:
            self.ribbon.setup(filename=ribbon_file)
            self.diecase = matrix_data.Diecase(self.ribbon.diecase_id)
            self.wedge = self.diecase.wedge

    @use_caster
    def cast_composition(self):
        """cast_composition()

        Composition casting routine. The input file is read backwards -
        last characters are cast first, after setting the justification.
        """
        # Count all characters and lines in the ribbon
        (all_lines, all_chars) = parsing.count_lines_and_chars(
            self.ribbon.contents)
        # Show the numbers to the operator
        ui.display('Lines found in ribbon: %i' % all_lines)
        ui.display('Characters: %i' % all_chars)
        # Check the line previous job has been aborted on
        # Ask how many lines to skip; add two previous lines if possible
        # so that the mould temperature has a chance to stabilize
        lines_skipped = self.line_aborted - 2
        # This must be non-negative
        lines_skipped = max(lines_skipped, 0)
        ui.display('You can skip a number of lines so that you can e.g. start '
                   'a casting job aborted earlier.')
        prompt = 'How many lines to skip? (default: %s) : ' % lines_skipped
        lines_skipped = (ui.enter_data_spec_type_or_blank(prompt, int) or
                         lines_skipped)
        prompt = 'How many times do you want to cast this? (default: 1) : '
        repetitions = ui.enter_data_spec_type_or_blank(prompt, int) or 1
        # For casting, we need to check the direction of ribbon
        if parsing.rewind_ribbon(self.ribbon.contents):
            ui.display('Ribbon starts with pump stop sequence - rewinding...')
            queue = [line for line in reversed(self.ribbon.contents)]
        else:
            ui.display('Ribbon starts with galley trip - not rewinding...')
            queue = [line for line in self.ribbon.contents]
        # Display a little explanation
        intro = ('\nThe combinations of Monotype signals will be displayed '
                 'on screen while the machine casts the type.\n'
                 'Turn on the machine and the program will start.\n')
        ui.display(intro)
        # Start only after the machine is running
        self.caster.detect_rotation()
        # Dict for telling the user whether sth is on or off
        status = {True: 'ON', False: 'OFF'}
        # Current run number
        current_run = 1
        # Repeat casting the whole sequence as many times as we would like
        while current_run <= repetitions:
            ui.display('\n\nCASTING RUN %d / %d (%d left)...\n\n'
                       % (current_run, repetitions, repetitions - current_run))
            current_run += 1
            # Characters already cast - start with zero
            current_char = 0
            chars_left = all_chars
            # Line currently cast: since the caster casts backwards
            # (from the last to the first line), this will decrease.
            current_line = all_lines
            # Lines done: this will increase
            # We start with a galley trip
            lines_done = 0
            # Wedges are initially unset - 15/15
            pos_0075, pos_0005 = '15', '15'
            # Read the reversed file contents, line by line, then parse
            # the lines, display comments & code combinations, and feed the
            # combinations to the caster
            for line in queue:
                # Parse the row, return a list of signals and a comment.
                # Both can have zero or positive length.
                [signals, comment] = parsing.comments_parser(line)
                # A list with information for user: signals, comments, etc.
                info_for_user = []
                if parsing.check_newline(signals):
                    # Decrease the counter for each started new line
                    current_line -= 1
                    # Percent of all lines done:
                    line_percent_done = 100 * lines_done / (all_lines - 1)
                    # Up the completed lines counter
                    lines_done += 1
                    # Display number of the working line,
                    # number of all remaining lines, percent done
                    if not current_line:
                        info_for_user.append('All lines successfully cast.\n')
                    else:
                        msg = ('Starting line no. %i (%i of %i), %i remaining '
                               '[%i%% done]...\n' %
                               (current_line, lines_done, all_lines - 1,
                                all_lines - lines_done, line_percent_done))
                        info_for_user.append(msg)
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
                           % (current_line, lines_done, all_lines - 1,
                              current_char, all_chars,
                              chars_left, char_percent_done))
                    info_for_user.append(msg)
                # Skipping the unneeded lines:
                # Just don't cast anything until we get to the correct line
                if lines_done <= lines_skipped:
                    continue
                # Determine if wedge positions change
                (new_0075, new_0005) = parsing.check_wedge_positions(signals)
                pos_0075 = new_0075 or pos_0075
                pos_0005 = new_0005 or pos_0005
                # Display wedge positions and pump status
                wedges_info = ('0075 wedge at %s, 0005 wedge at %s\n'
                               % (pos_0075, pos_0005))
                info_for_user.append(wedges_info)
                info_for_user.append('Pump is %s\n'
                                     % status[self.caster.pump.working])
                # Append signals to be cast
                info_for_user.append(' '.join(signals).ljust(15))
                # Add comment
                info_for_user.append(comment + '\n')
                # Display the info
                ui.display(''.join(info_for_user))
                # Proceed with casting only if code is explicitly stated
                # (i.e. O15 = cast, empty list = don't cast)
                if signals:
                    # First strip the unneeded O15
                    signals = parsing.strip_o15(signals)
                    # Cast the sequence (even if empty)
                    try:
                        self.caster.process_signals(signals)
                    except exceptions.CastingAborted:
                        # On failure - abort the whole job.
                        # Check the aborted line so we can get back to it.
                        self.line_aborted = current_line
                        ui.confirm('\nCasting aborted on line %i.'
                                   % self.line_aborted, ui.MSG_MENU)
                        return False
        # After casting is finished, notify the user
        ui.confirm('Casting finished successfully!', ui.MSG_MENU)
        return True

    @use_caster
    def punch_composition(self):
        """punch_composition():

        When punching, the input file is read forwards. An additional line
        (O+15) is switched on for operating the paper tower to exert enough
        force to drive the punches and advance the ribbon.
        This mode uses arbitrary timings for air on / off phases.
        """
        # Count a number of combinations punched in ribbon
        all_combinations = parsing.count_combinations(self.ribbon.contents)
        ui.display('Combinations in ribbon: %i', all_combinations)
        # Wait until the operator confirms.
        ui.display('\nThe combinations of Monotype signals will be displayed '
                   'on screen while the paper tower punches the ribbon.\n'
                   'Turn on the air and fit the tape on your paper tower.')
        ui.confirm()
        for line in self.ribbon.contents:
            # Parse the row, return a list of signals and a comment.
            # Both can have zero or positive length.
            [signals, comment] = parsing.comments_parser(line)
            # A string with information for user: signals, comments, etc.
            ui.display(' '.join(signals).ljust(20) + comment)
            # Send the signals
            if signals:
                # In any case add O+15 (to put enough force on punches)
                if 'O15' not in signals:
                    signals.append('O15')
                # Punch it!
                self.caster.activate_valves(signals)
                # The pace is arbitrary, let's set it to 200ms/200ms
                time.sleep(0.2)
                self.caster.deactivate_valves()
                time.sleep(0.2)
        # After punching is finished, notify the user:"""
        ui.confirm('\nPunching finished!', ui.MSG_MENU)
        return True

    @use_caster
    def test_air_signals(self, combinations):
        """Tests a sequence of signals specified on input"""
        try:
            for code in combinations:
                ui.display(code)
                code = parsing.signals_parser(code)
                self.caster.process_signals(code, 120)
        except exceptions.CastingAborted:
            return False
        else:
            ui.confirm('\nTesting finished!', ui.MSG_MENU)
            return True

    def test_front_pinblock(self):
        """test_front_pinblock():

        Tests all valves and composition caster's inputs on the front pinblock
        to check if everything works and is properly connected.
        Signals will be tested in order: 1 towards 14.
        """
        intro = ('This will test the front pinblock - signals 1 towards 14. '
                 'At the end O+15 will be activated.')
        ui.confirm(intro)
        self.test_air_signals([str(n) for n in range(1, 15)])

    def test_rear_pinblock(self):
        """test_rear_pinblock():

        Tests all valves and composition caster's inputs on the rear pinblock
        to check if everything works and is properly connected.
        Signals will be tested in order: NI, NL, A...N, O+15.
        """
        intro = ('This will test the front pinblock - signals NI, NL, A...N. '
                 'At the end O+15 will be activated.')
        ui.confirm(intro)
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
        ui.confirm(intro)
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
            ui.clear()
            ui.display('Sorts casting by matrix coordinates\n\n')
            prompt = 'Column: NI, NL, A...O? (default: G): '
            # Got no signals? Use G5.
            column = ''
            column_symbols = ['NI', 'NL'] + [ltr for ltr in 'ABCDEFGHIJKLMNO']
            while column not in column_symbols:
                column = ui.enter_data_or_blank(prompt).upper() or 'G'
            prompt = 'Row: 1...16? (default: 5): '
            # Initially set this to zero to enable the while loop
            row = 0
            units = 0
            # Not using unit shift by default
            unit_shift = False
            # Ask for row number
            while row not in range(1, 17):
                try:
                    row = ui.enter_data_spec_type_or_blank(prompt, int) or 5
                    row = abs(row)
                except TypeError:
                    row = 0
            if row == 16:
                question = 'Trying to access 16th row. Use unit shift?'
                unit_shift = ui.yes_or_no(question)
                row = 15
                if not unit_shift:
                    ui.display('Cannot access the 16th row; using 15 instead')
                    ui.yes_or_no('Is it okay?') or exceptions.return_to_menu()
            # Correct the column number if using unit shift
            if unit_shift:
                column = column.replace('D', 'E F')
                column += ' D'
            # Determine the unit width for a row
            try:
                row_units = wedge.unit_arrangement[row]
            except (IndexError, KeyError):
                row_units = 5
            prompt = 'Unit width value? (decimal, default: %s) : ' % row_units
            while not 2 < units < 25:
                units = (ui.enter_data_spec_type_or_blank(prompt, float) or
                         row_units)
            # Calculate the unit width difference and apply justification
            difference = units - row_units
            wedge_positions = typesetting.calculate_wedges(difference,
                                                           wedge.set_width,
                                                           wedge.brit_pica)
            if difference:
                # If we need to correct the width -
                # we must cast with the S needle
                signals = column + ' S ' + str(row)
            else:
                signals = column + ' ' + str(row)
            # Ask for number of sorts and lines, no negative numbers here
            prompt = '\nHow many sorts per line? (default: 10): '
            sorts = abs(ui.enter_data_spec_type_or_blank(prompt, int) or 10)
            prompt = '\nHow many lines? (default: 1): '
            lines = abs(ui.enter_data_spec_type_or_blank(prompt, int) or 1)
            # Warn if we want to cast too many sorts from a single matrix
            warning = ('Warning: you want to cast a single character more than'
                       ' 10 times. This may lead to matrix overheating!\n')
            if sorts > 10:
                ui.display(warning)
            # After entering parameters, ask the operator if they're OK
            try:
                while True:
                    # Inner loop
                    # Menu subroutines
                    def cast_it():
                        """Cast the combination or go back to menu"""
                        if self.cast_from_matrix(signals, sorts, lines,
                                                 wedge_positions):
                            ui.display('Casting finished successfully.')
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
                    ui.simple_menu(message, options)()
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
        line_length = ui.enter_data_spec_type_or_blank(prompt, int) or 25
        line_length = abs(line_length)
        # Measurement system
        options = {'A': 0.1660,
                   'B': 0.1667,
                   'D': 0.1776,
                   'F': 0.1629}
        message = ('Measurement? [A]merican Johnson pica = 0.166", '
                   '[B]ritish pica = 0.1667",\n [D]idot cicero = 0.1776", '
                   '[F]ournier cicero = 0.1629": ')
        pica_def = ui.simple_menu(message, options)
        # We need to choose a wedge unless we did it earlier
        wedge = self.wedge or wedge_data.Wedge()
        # Unit line length:
        unit_line_length = int(18 * pica_def / 0.1667 * line_length *
                               wedge.set_width / 12)
        # Now we can cast multiple different spaces
        while True:
            ui.clear()
            ui.display('Spaces / quads casting\n\n')
            prompt = 'Column: NI, NL, A...O? (default: G): '
            # Got no signals? Use G5.
            column = ''
            column_symbols = ['NI', 'NL'] + [ltr for ltr in 'ABCDEFGHIJKLMNO']
            while column not in column_symbols:
                column = ui.enter_data_or_blank(prompt).upper() or 'G'
            prompt = 'Row: 1...16? (default: 2): '
            # Initially set this to zero to enable the while loop
            row = 0
            width = 0
            # Not using unit shift by default
            unit_shift = False
            # Ask for row number
            while row not in range(1, 17):
                row = abs(ui.enter_data_spec_type_or_blank(prompt, int) or 2)
            if row == 16:
                question = 'Trying to access 16th row. Use unit shift?'
                unit_shift = ui.yes_or_no(question)
                row = 15
                if not unit_shift:
                    ui.display('Cannot access the 16th row; using 15 instead')
                    ui.yes_or_no('Is it okay?') or exceptions.return_to_menu()
            # Correct the column number if using unit shift
            if unit_shift:
                column = column.replace('D', 'E F')
                column += ' D'
            # Determine the unit width for a row
            try:
                row_units = wedge.unit_arrangement[row]
            except (IndexError, KeyError):
                row_units = 6
            prompt = '\nHow many lines? (default: 1): '
            lines = abs(ui.enter_data_spec_type_or_blank(prompt, int) or 1)
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
            width = ui.simple_menu(message, options) * 12
            # Ask about custom value, then specify units
            if not width:
                while width < 1 or width > 20:
                    prompt = 'Custom width in points (decimal, 1...20) ? : '
                    width = ui.enter_data_spec_type_or_blank(prompt, float)
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
            difference = sort_units - row_units
            # Calculate the wedge positions
            wedge_positions = typesetting.calculate_wedges(difference,
                                                           wedge.set_width,
                                                           wedge.brit_pica)
            if difference:
                # If we need to correct the width -
                # we must cast with the S needle
                signals = column + ' S ' + str(row)
            else:
                signals = column + ' ' + str(row)
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
                        ui.display(message)
                        self.cast_from_matrix('O15', quads_number)
                        for num in range(lines):
                            ui.display('Now casting line %s' % str(num + 1))
                            ui.display('\nFive quads before - discard them.\n')
                            self.cast_from_matrix('O15', end_galley_trip=False,
                                                  machine_check=False)
                            ui.display('\nSpaces of desired width...\n')
                            self.cast_from_matrix(signals, sorts_number, 1,
                                                  wedge_positions,
                                                  end_galley_trip=False,
                                                  machine_check=False)
                            ui.display('\nFive quads after - discard them.\n')
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
                        ui.display(message)
                    message = ('[C]ast it, [D]ifferent parameters, '
                               '[M]enu or [E]xit? ')
                    ui.simple_menu(message, options)()
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
            ui.display('Start the machine...')
            self.caster.detect_rotation()
        # We're here because the machine is rotating. Start casting the job...
        for current_line in range(1, lines + 1):
            # Cast each line and if the CastingAborted exception is caught,
            # remember the last line and stop casting.
            try:
                # Cast the sorts: set wedges, turn pump on, cast, line out
                # Set up the justification, turn the pump on
                ui.display('Casting line %i of %i' % (current_line, lines))
                ui.display('0005 wedge at ' + pos_0005)
                ui.display('0075 wedge at ' + pos_0075)
                if start_galley_trip:
                    # Double justification
                    ui.display('Putting the line out...')
                    self.caster.process_signals(galley_trip)
                else:
                    # Starting a job
                    self.caster.process_signals(set_0005)
                ui.display('Starting the pump...')
                self.caster.process_signals(set_0075)
                # Start casting characters
                ui.display('Casting characters...')
                # Cast n combinations of row & column, one by one
                for i in range(1, num + 1):
                    info = ('%s - casting character %i of %i, %i%% done.'
                            % (' '.join(combination).ljust(20),
                               i, num, 100 * i / num))
                    ui.display(info)
                    combination = parsing.strip_o15(combination)
                    self.caster.process_signals(combination)
                if end_galley_trip:
                    # If everything went normally, put the line to the galley
                    ui.display('Putting line to the galley...')
                    self.caster.process_signals(galley_trip)
                    # After casting sorts we need to stop the pump
                ui.display('Stopping the pump...')
                self.caster.process_signals(set_0005)
            except exceptions.CastingAborted:
                self.line_aborted = current_line
                ui.display('Casting aborted on line %i' % self.line_aborted)
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
            signals = ui.enter_data_or_blank(prompt)
            # Turn off any valves that were on (from previous combination)
            self.caster.deactivate_valves()
            if not signals:
                # Escape the infinite loop here
                raise exceptions.ReturnToMenu
            # Parse the combination, get the signals (first item returned
            # by the parsing function)
            signals = parsing.signals_parser(signals)
            # Turn the valves on
            ui.display(' '.join(signals))
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
        ui.display(intro)
        while True:
            # Subroutines for menu options
            def continue_aligning():
                """Cast spaces with and without S-needle"""
                pass
            # Finished. Return to menu.
            options = {'C': continue_aligning,
                       'M': exceptions.return_to_menu,
                       'E': exceptions.exit_program}
            ui.simple_menu('\n[C]ontinue, [M]enu or [E]xit? ', options)()
            # Cast 10 spaces without correction.
            # End here if casting unsuccessful.
            ui.display('Now casting with a normal wedge only.')
            if not self.cast_from_matrix(space_position, 5):
                continue
            # Cast 10 spaces with the S-needle.
            # End here if casting unsuccessful.
            ui.display('Now casting with justification wedges...')
            if not self.cast_from_matrix(space_position + 'S', 5):
                continue
            # At the end of successful sequence, some info for the user:
            ui.display('Done. Compare the lengths and adjust if needed.')

    def align_mould(self):
        """align_mould:

        Calculates the width, displays it and casts some 9-unit characters.
        Then, the user measures the width and adjusts the mould opening width.
        """
        intro = ('Mould blade opening calibration:\n'
                 'Cast some 9-unit characters, then measure the width.\n'
                 'Adjust if needed.')
        ui.display(intro)
        # Use current wedge or select one
        wedge = self.wedge or wedge_data.Wedge()
        # Selected
        if wedge.brit_pica:
            pica = 0.1667
        else:
            pica = 0.166
        # We calculate the width of double 9 units = 18 units, i.e. 1 pica em
        em_width = pica * wedge.set_width / 12
        ui.display('Type 9 units (1en) width: %s' % round(em_width / 2, 4))
        ui.display('Type 18 units (1em) width: %s' % round(em_width, 4))
        while True:
            # Subroutines for menu options
            def continue_aligning():
                """Do nothing"""
                pass
            # Finished. Return to menu.
            options = {'C': continue_aligning,
                       'M': exceptions.return_to_menu,
                       'E': exceptions.exit_program}
            ui.simple_menu('\n[C]ontinue, [M]enu or [E]xit? ', options)()
            # Cast 5 nine-unit quads
            # End here if casting unsuccessful.
            ui.display('Now casting 9-units spaces')
            if not self.cast_from_matrix('G5', 7):
                continue
            # At the end of successful sequence, some info for the user:
            ui.display('Done. Compare the lengths and adjust if needed.')

    def align_diecase(self):
        """align_diecase:

        Casts the "en dash" characters for calibrating the character X-Y
        relative to type body.
        """
        intro = ('X-Y character calibration:\n'
                 'Cast some en-dashes and/or lowercase "n" letters, '
                 'then check the position of the character relative to the '
                 'type body.\nAdjust if needed.')
        ui.display(intro)
        try:
            # Find the en-dash automatically
            dash_position = [mat[2] + str(mat[3])
                             for mat in self.diecase.layout
                             if mat[0] == '–'][0]
        except (exceptions.MatrixNotFound, TypeError, IndexError):
            # Choose it manually
            dash_position = ui.enter_data_or_blank('En dash (–) at: ').upper()
        try:
            # Find the "n" letter automatically
            lowercase_n_position = [mat[2] + str(mat[3])
                                    for mat in self.diecase.layout
                                    if mat[0] == 'n'][0]
        except (exceptions.MatrixNotFound, TypeError, IndexError):
            # Choose itmanually
            lowercase_n_position = ui.enter_data_or_blank('"n" at: ').upper()
        while True:
            # Subroutines for menu options
            def continue_aligning():
                """Do nothing"""
                pass
            # Finished. Return to menu.
            options = {'C': continue_aligning,
                       'M': exceptions.return_to_menu,
                       'E': exceptions.exit_program}
            ui.simple_menu('\n[C]ontinue, [M]enu or [E]xit? ', options)()
            # Cast 5 nine-unit quads
            # End here if casting unsuccessful.
            if dash_position:
                ui.display('Now casting en dash')
                if not self.cast_from_matrix(dash_position, 7):
                    continue
            if lowercase_n_position:
                ui.display('Now casting lowercase "n"')
                if not self.cast_from_matrix(lowercase_n_position, 7):
                    continue
            # At the end of successful sequence, some info for the user:
            ui.display('Done. Compare the lengths and adjust if needed.')

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
        typesetter = typesetting.Typesetter()
        # Supply the diecase id
        # TODO: refactor it to use the new diecase and wedge data model!
        typesetter.session_setup(self.diecase.diecase_id)
        # Enter text
        text = ui.enter_data("Enter text to compose: ")
        typesetter.text_source = typesetter.parse_and_generate(text)
        # Translate the text to Monotype signals
        # Compose the text
        typesetter.compose()
        self.ribbon.contents = typesetter.justify()
        # Ask whether to display buffer contents
        if ui.yes_or_no('Show the codes?'):
            self.ribbon.display_contents()
        # We're casting
        if ui.yes_or_no('Cast it?'):
            try:
                self.cast_composition()
            except exceptions.ReturnToMenu:
                # If casting aborted - don't go back to menu
                pass

    def heatup(self):
        """Casts 2 lines x 20 quads from the O15 matrix to heat up the mould"""
        ui.clear()
        self.cast_from_matrix('O15', num=20, lines=2)

    def diagnostics_submenu(self):
        """Settings and alignment menu for servicing the caster"""
        def menu_options():
            """Build a list of options, adding an option if condition is met"""
            opts = [(exceptions.menu_level_up, 'Return to main menu', True),
                    (self.test_all, 'Test the air outputs one by one', True),
                    (self.test_front_pinblock, 'Test the pins 1...14',
                     not self.caster.is_perforator),
                    (self.test_rear_pinblock, 'Test the pins NI, NL, A...N',
                     not self.caster.is_perforator),
                    (self.send_combination, 'Send specified signals', True),
                    (self.align_wedges, 'Calibrate the space transfer wedge',
                     not self.caster.is_perforator),
                    (self.align_mould, 'Calibrate mould opening',
                     not self.caster.is_perforator),
                    (self.align_diecase, 'Calibrate diecase X-Y',
                     not self.caster.is_perforator)]
            return [(desc, func) for (func, desc, cond) in opts if cond]

        header = ('Diagnostics and machine calibration menu:\n\n')
        # Keep displaying the menu and go back here after any method ends
        while True:
            try:
                # Catch "return to menu" and "exit program" exceptions here
                ui.menu(menu_options(), header=header)()
            except exceptions.ReturnToMenu:
                # Stay in the menu
                pass

    def display_additional_info(self):
        """Collect ribbon, diecase and wedge data here"""
        data = [(self.caster.name, 'Caster name'),
                (self.ribbon.filename, 'Ribbon filename'),
                (self.ribbon.title, 'Ribbon title'),
                (self.ribbon.author, 'Author'),
                (self.ribbon.customer, 'Customer'),
                (self.ribbon.unit_shift, 'Casting with unit-shift on?'),
                (self.diecase.diecase_id, 'Diecase ID'),
                (self.diecase.typeface_name, 'Typeface'),
                (self.diecase.type_series, 'Type series'),
                (self.diecase.type_size, 'Type size'),
                (self.wedge.series, 'Wedge series'),
                (self.wedge.set_width, 'Set width of a wedge'),
                (self.wedge.brit_pica, 'British pica (.1667") based wedge?'),
                (' '.join([str(x) for x in self.wedge.unit_arrangement if x]),
                 'Unit arrangement for this wedge'),
                (self.line_aborted, 'Last casting was aborted on line no')]
        info = ['%s: %s' % (desc, value) for (value, desc) in data if value]
        return '\n'.join(info)

    def __exit__(self, *args):
        ui.debug_info('Exiting casting job context.')


def main_menu(work=Casting()):
    """main_menu:

    Calls ui.menu() with options, a header and a footer.
    Options: {option_name : description}
    Header: string displayed over menu
    Footer: string displayed under menu (all info will be added here).
    """
    def choose_ribbon():
        """Chooses a ribbon from database or file"""
        work.ribbon = typesetting_data.Ribbon()
        work.ribbon.setup()
        choose_diecase()

    def choose_diecase():
        """Chooses a diecase from database"""
        work.diecase = matrix_data.Diecase(work.ribbon.diecase_id)
        if not work.ribbon.diecase_id:
            work.diecase.setup()
        work.wedge = work.diecase.wedge

    def choose_wedge():
        """Chooses a wedge from registered ones"""
        work.wedge = wedge_data.Wedge()

    def menu_options():
        """Build a list of options, adding an option if condition is met"""
        # Options are described with tuples: (function, description, condition)
        opts = [(exceptions.exit_program, 'Exit program', True),
                (choose_ribbon, 'Select ribbon from database or file', True),
                (choose_diecase, 'Select a matrix case', True),
                (choose_wedge, 'Select a normal wedge', True),
                (work.ribbon.display_contents, 'Preview ribbon',
                 work.ribbon.contents),
                (work.heatup, 'Cast some quads to heat up the mould',
                 not work.caster.is_perforator),
                (work.punch_composition, 'Punch composition',
                 work.ribbon.contents and work.caster.is_perforator),
                (work.cast_composition, 'Cast composition',
                 work.ribbon.contents and not work.caster.is_perforator),
                (work.diecase.show_layout, 'View the matrix case layout',
                 work.diecase.diecase_id),
                (work.line_casting, 'Compose and cast a line of text',
                 work.diecase.diecase_id),
                (work.cast_sorts, 'Cast sorts from matrix coordinates',
                 not work.caster.is_perforator),
                (work.cast_spaces, 'Cast spaces or quads',
                 not work.caster.is_perforator),
                (work.diagnostics_submenu, 'Diagnostics and calibration', True)
                ]
        # Built a list of menu options conditionally
        return [(desc, func) for (func, desc, cond) in opts if cond]

    # Header is static, menu content is dynamic
    header = ('rpi2caster - CAT (Computer-Aided Typecasting) '
              'for Monotype Composition or Type and Rule casters.\n\n'
              'This program reads a ribbon (from file or database) '
              'and casts the type on a composition caster. \n\nMain Menu:')
    # Keep displaying the menu and go back here after any method ends
    while True:
        # Catch any known exceptions here
        try:
            ui.menu(menu_options(), header=header,
                    footer=work.display_additional_info())()
        except (exceptions.ReturnToMenu, exceptions.MenuLevelUp):
            # Will skip to the end of the loop, and start all over
            pass
        except (KeyboardInterrupt, EOFError, exceptions.ExitProgram):
            # Will exit program
            ui.exit_program()
