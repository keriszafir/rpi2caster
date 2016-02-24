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
from collections import deque
# Signals parsing methods for rpi2caster
from . import parsing as p
# Custom exceptions
from . import exceptions as e
# Constants shared between modules
from . import constants as c
# Typesetting functions module
from . import typesetting_funcs
# Read ribbon files
from . import typesetting_data
# Caster backend
from . import monotype
# Casting stats
from .casting_stats import Stats
# Modules imported in the typesetting_data - matrix_data - wedge_data
# No need to import them again - just point to them
matrix_data = typesetting_data.matrix_data
wedge_data = matrix_data.wedge_data
# User interface is the same as in typesetting_data
UI = typesetting_data.UI
# Constants for control sequences
GALLEY_TRIP = 'NKJS 0005 0075'
PUMP_OFF = 'NJS 0005'
PUMP_ON = 'NKS 0075'


def choose_sensor_and_driver(cast_or_punch):
    """Checks current modes (simulation, perforation, testing)"""
    def wrapper(self, *args, **kwargs):
        """Wrapper function"""
        UI.debug_pause('About to %s' %
                       (self.mode.casting and 'cast composition...' or
                        self.mode.testing and 'test outputs...' or
                        self.mode.punching and 'punch ribbon...'))
        # Instantiate and enter context
        with self.mode.sensor() as self.caster.sensor:
            with self.mode.output() as self.caster.output:
                with self.caster:
                    return cast_or_punch(self, *args, **kwargs)
    return wrapper


def repeat(routine):
    """Decorator for repeating with user confirmation"""
    def wrapper(self, *args, **kwargs):
        """Inner wrapper"""
        while True:
            routine(self, *args, **kwargs)
            if not UI.confirm('Start again?'):
                break
    return wrapper


def cast_or_punch_result(ribbon_source):
    """Ask for confirmation and cast the resulting ribbon;
    uses temporary stats object"""
    def wrapper(self, *args, **kwargs):
        """Wrapper function"""
        new_ribbon = ribbon_source(self, *args, **kwargs)
        if self.mode.diagnostics or UI.confirm('Cast / punch it?'):
            self.stats, old_stats = Stats(self), self.stats
            try:
                self.cast_or_punch(new_ribbon, *args, **kwargs)
            except e.CastingAborted:
                pass
            self.mode.diagnostics, self.stats = False, old_stats
    return wrapper


def prepare_job(cast_or_punch):
    """Prepares the job for casting"""
    line_of_quads = ['O15'] * 20 + ['NKJS 0005 0075']
    # Alias to make it shorter
    enter = UI.enter_data_or_blank

    def wrapper(self, ribbon=()):
        """Wrapper function"""
        # Mode aliases
        punching, diagnostics = self.mode.punching, self.mode.diagnostics
        # Get ribbon, derive stats for it
        ribbon = ribbon or self.ribbon.contents
        # Rewind the ribbon if 0005 is found before 0005+0075
        if not diagnostics and not punching and p.stop_comes_first(ribbon):
            ribbon = [x for x in reversed(ribbon)]
        UI.display_header('Ribbon info:')
        self.stats.ribbon = ribbon
        UI.display_parameters(self.stats.parameters)
        UI.display('\n')
        # Ask how many times to repeat this (always 1 run for calibrating)
        prompt = 'How many times do you want to cast it? (default: 1) : '
        self.stats.runs = ((diagnostics or punching) * 1 or
                           abs(enter(prompt, int) or 1))
        # Line skipping - ask user if they want to skip any initial line(s)
        prompt = 'How many lines do you want to skip?  (default: 0): '
        l_skipped = (not diagnostics and not punching and
                     abs(enter(prompt, int) or 0))
        # Feed info to statistics; get session info from statistics
        self.stats.ribbon = ribbon
        self.stats.runs_left = self.stats.runs
        UI.display_header('Session info:')
        UI.display_parameters(self.stats.session_parameters)
        while self.stats.runs_left:
            queue = deque(ribbon)
            UI.display_header('Starting run %s of %s, %s left'
                              % (self.stats.current_run_number,
                                 self.stats.runs, self.stats.runs_left))
            quad_lines = 0
            if not (punching or diagnostics) and UI.confirm('Heat the mould?'):
                l_skipped -= 2
                # When skipping less than 2 lines, we'll cast quads instead
                quad_lines = max(-l_skipped, 0)
            # Apply constraints: 0 <= lines_skipped < lines in ribbon
            l_skipped = min(l_skipped, self.stats.ribbon_lines - 1)
            l_skipped = max(0, l_skipped)
            if l_skipped:
                UI.display('Skipping %s initial lines...' % l_skipped)
            if quad_lines:
                UI.display('Casting %s line(s) of 20 quads' % quad_lines)
            # Make sure we take off lines from the beginning of the
            # casting job - i.e. last lines of text; count the lines
            code = ''
            # Add one more line to skip - because ribbon starts with 0075-0005
            l_skipped += 1
            while l_skipped:
                code = queue.popleft()
                l_skipped -= 1 * p.check_newline(code)
            # Add it back, then add those quads
            queue.appendleft(code)
            queue.extendleft(quad_lines * line_of_quads)
            # The ribbon is ready for casting / punching
            try:
                cast_or_punch(self, queue or [])
                if not self.stats.runs_left and UI.confirm('Repeat?'):
                    self.stats.add_run()
            except e.CastingAborted:
                l_skipped = self.stats.current_line_number
                if not UI.confirm('Retry this job?'):
                    return
    return wrapper


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
        self.mode = monotype.Mode()
        self.ribbon = (ribbon_file and
                       typesetting_data.SelectRibbon(filename=ribbon_file) or
                       typesetting_data.Ribbon())

    @choose_sensor_and_driver
    @prepare_job
    def cast_or_punch(self, casting_queue=()):
        """Casts the sequence of codes in ribbon or self.ribbon.contents,
        displaying the statistics (depending on context:
        casting, punching or testing)"""

        def add_or_remove_o15(signals):
            """Checks if we need to activate O15, based on mode"""
            return ([x for x in signals if x != 'O15' or self.mode.testing] +
                    ['O15'] * (self.mode.punching and not self.mode.testing))

        casting_queue = casting_queue or self.ribbon
        self.stats.next_run()
        self.stats.queue = casting_queue
        UI.display_header('Current run info:')
        UI.display_parameters(self.stats.run_parameters)
        UI.display('\n')
        # Now process the queue
        generator = (p.parse_record(record) for record in casting_queue)
        if not self.mode.testing:
            self.caster.sensor.check_if_machine_is_working()
        for (signals, comment) in generator:
            comment = comment and UI.display(comment)
            if not signals:
                # No signals (comment only)- go to the next combination
                continue
            self.stats.signals = signals
            UI.display_parameters(self.stats.code_parameters)
            # Let the caster do the job
            self.caster.process(add_or_remove_o15(signals))
        return True

    @repeat
    @cast_or_punch_result
    def test_front_pinblock(self):
        """Sends signals 1...14, one by one"""
        UI.pause('Testing the front pinblock - signals 1 towards 14.')
        self.mode.testing = True
        return [str(n) for n in range(1, 15)]

    @repeat
    @cast_or_punch_result
    def test_rear_pinblock(self):
        """Sends NI, NL, A...N"""
        UI.pause('This will test the front pinblock - signals NI, NL, A...N. ')
        self.mode.testing = True
        return [x for x in c.COLUMNS_17]

    @repeat
    @cast_or_punch_result
    def test_all(self):
        """Tests all valves and composition caster's inputs in original
        Monotype order: NMLKJIHGFSED 0075 CBA 123456789 10 11 12 13 14 0005.
        """
        UI.pause('This will test all the air lines in the same order '
                 'as the holes on the paper tower: \n%s\n'
                 'MAKE SURE THE PUMP IS DISENGAGED.' % ' '.join(c.SIGNALS))
        self.mode.testing = True
        return [x for x in c.SIGNALS]

    @repeat
    @cast_or_punch_result
    def test_justification(self):
        """Tests the 0075-S-0005"""
        UI.pause('This will test the justification pin block (0075, S, 0005).')
        self.mode.testing = True
        return ['0075', 'S', '0005']

    @choose_sensor_and_driver
    def test_any_code(self):
        """Tests a user-specified combination of signals"""
        self.mode.testing = False
        while True:
            UI.display('Enter the signals to send to the caster, '
                       'or leave empty to return to menu: ')
            string = UI.enter_data_or_blank('Signals? (leave blank to exit): ')
            signals = p.parse_signals(string)
            if signals:
                UI.display('Activating ' + ' '.join(signals))
                self.caster.output.valves_on(signals)
            else:
                break
        self.caster.output.valves_off()
        self.mode.testing = False

    @repeat
    @cast_or_punch_result
    # TODO: Selection from diecase by character
    def cast_sorts(self):
        """Sorts casting routine, based on the position in diecase.
        Ask user about the diecase row & column, as well as number of sorts.
        """
        queue = []
        # Outer loop
        while True:
            UI.clear()
            UI.display('Sorts casting by matrix coordinates\n\n')
            prompt = 'Combination? (default: G5): '
            user_code = UI.enter_data_or_blank(prompt).upper() or 'G5'
            combination = p.parse_signals(user_code)
            row = p.get_row(combination)
            column = p.get_column(combination)
            units = 0
            # If we want to cast from row 16, we need unit-shift
            # HMN or KMN systems are not supported yet
            question = 'Trying to access 16th row. Use unit shift?'

            unit_shift = row == 16 and UI.confirm(question)
            if row == 16 and not unit_shift:
                UI.pause('Aborting.')
                continue
            elif unit_shift:
                row -= 1
                # Turn on D. Replace D with EF.
                column_code = (column is 'D' and 'EF' or column) + 'D'
            # Determine the unit width for a row
            row_units = self.wedge.unit_arrangement[row]
            # Enter custom unit value (no points-based calculation yet)
            prompt = 'Unit width value? (decimal, default: %s) : ' % row_units
            while not 4 < units < 25:
                units = UI.enter_data_or_blank(prompt, float) or row_units
            # Calculate the unit width difference and apply justification
            diff = units - row_units
            calc = typesetting_funcs.calculate_wedges
            (pos_0075, pos_0005) = calc(diff, self.wedge.set_width,
                                        self.wedge.brit_pica)
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
            # Add 'S' if there is width difference
            signals = column_code + (diff and 'S' or '') + str(row)
            # Ask for confirmation
            prompt = 'Casting %s lines of %s%s. OK?' % (lines, column, row)
            if UI.confirm(prompt):
                line_codes = [GALLEY_TRIP + str(pos_0005),
                              PUMP_ON + str(pos_0075)]
                line_codes.extend([signals] * sorts)
                queue.extend(line_codes * lines)
            if not UI.confirm('Another combination?'):
                # Finished gathering data
                break
        return queue + [GALLEY_TRIP, PUMP_OFF]

    @repeat
    @cast_or_punch_result
    def cast_spaces(self):
        """Spaces casting routine, based on the position in diecase.
        Ask user about the space width and measurement unit.
        """
        queue = []
        # Measurement system
        options = {'A': 0.1660,
                   'B': 0.1667,
                   'D': 0.1776,
                   'F': 0.1629}
        message = ('Measurement unit to use? [A]merican Johnson pica = 0.166",'
                   '[B]ritish pica = 0.1667",\n [D]idot cicero = 0.1776", '
                   '[F]ournier cicero = 0.1629": ')
        pica_def = UI.simple_menu(message, options)
        # Ask about line length
        prompt = 'Galley line length in above units? (default: 25) : '
        line_length = abs(UI.enter_data_or_blank(prompt, int) or 25)
        # Unit line length:
        unit_line_length = int(18 * pica_def / 0.1667 * line_length *
                               self.wedge.set_width / 12)
        prompt = 'Combination? (default: G5): '
        code_string = UI.enter_data_or_blank(prompt).upper() or 'G5'
        combination = p.parse_signals(code_string)
        row = p.get_row(combination)
        column = p.get_column(combination)
        width = 0.0
        # Not using unit shift by default, ask for row 16
        question = 'Trying to access 16th row. Use unit shift?'
        unit_shift = row == 16 and UI.confirm(question)
        if row == 16 and not unit_shift:
            UI.pause('Aborting.')
            e.return_to_menu()
        elif unit_shift:
            row -= 1
            column = (column is 'D' and 'EF' or column) + 'D'
        # Determine the unit width for a row
        row_units = self.wedge.unit_arrangement[row]
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
        width = UI.simple_menu(message, options) * 12.0
        # Ask about custom value, then specify units
        while not 2 <= width <= 20:
            prompt = 'Custom width in points (decimal, 2...20) ? : '
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
        space_units = round(width * factor * self.wedge.set_width / 8, 2)
        # How many spaces will fit in a line? Calculate it...
        # We add 2 em-quads at O15 before and after the proper spaces
        # We need 64 additional units for that - need to subtract
        allowance = unit_line_length - 64
        sorts = int(allowance // space_units)
        # Check if the corrections are needed at all
        diff = space_units - row_units
        calc = typesetting_funcs.calculate_wedges
        (pos_0075, pos_0005) = calc(diff, self.wedge.set_width,
                                    self.wedge.brit_pica)
        # Add 'S' if there is width difference
        signals = column + (diff and 'S' or '') + str(row)
        # Ask for confirmation
        prompt = ('Casting %s lines of %s-point spaces from %s%s. OK?' %
                  (lines, width, column, row))
        if UI.confirm(prompt):
            line_codes = [GALLEY_TRIP + str(pos_0005),
                          PUMP_ON + str(pos_0075)]
            line_codes.extend([signals] * sorts)
            queue.extend(line_codes * lines)
        return queue + [GALLEY_TRIP, PUMP_OFF]

    @cast_or_punch_result
    def adhoc_typesetting(self):
        """Allows us to use caster for casting single lines.
        This means that the user enters a text to be cast,
        gives the line length, chooses alignment and diecase.
        Then, the program composes the line, justifies it, translates it
        to Monotype code combinations.

        This allows for quick typesetting of short texts, like names etc.
        """
        # Initialize the typesetter for a chosen diecase
        typesetter = typesetting_funcs.Typesetter()
        # Supply the diecase id
        typesetter.session_setup(self.diecase)
        # Enter text
        text = UI.enter_data("Enter text to compose: ")
        typesetter.text_source = typesetter.parse_and_generate(text)
        # Translate the text to Monotype signals
        typesetter.compose()
        queue = typesetter.justify()
        self.ribbon.contents, old_ribbon = queue, self.ribbon.contents
        if UI.confirm('Show the codes?'):
            self.ribbon.display_contents()
        self.ribbon.contents = old_ribbon
        return queue

    @repeat
    @cast_or_punch_result
    def calibrate_wedges(self):
        """Allows to calibrate the justification wedges so that when you're
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
                 'This function will cast two lines of 5 spaces: '
                 'first: G5, second: GS5 with wedges at 3/8. \n'
                 'Adjust the 52D space transfer wedge '
                 'until the lengths are the same.')
        UI.display(intro)
        signals = 'G5'
        queue = [GALLEY_TRIP] + [signals] * 7
        queue.extend([GALLEY_TRIP + '8', PUMP_ON + '3'] + [signals + 'S'] * 7)
        queue.extend([GALLEY_TRIP, PUMP_OFF])
        self.mode.calibration = True
        return queue

    @repeat
    @cast_or_punch_result
    def calibrate_mould(self):
        """Calculates the width, displays it and casts some 9-unit characters.
        Then, the user measures the width and adjusts the mould opening width.
        """
        intro = ('Mould blade opening calibration:\n'
                 'Cast G5 (9-units wide on S5 wedge), then measure the width. '
                 'Adjust if needed.')
        UI.display(intro)
        pica = self.wedge.brit_pica and 0.1667 or 0.166
        # We calculate the width of double 9 units = 18 units, i.e. 1 pica em
        em_width = pica * self.wedge.set_width / 12.0
        UI.display('9 units (1en) is %s" wide' % round(0.5 * em_width, 4))
        UI.display('18 units (1em) is %s" wide' % round(em_width, 4))
        signals = 'G5'
        self.mode.calibration = True
        return [GALLEY_TRIP] + [signals] * 7 + [GALLEY_TRIP, PUMP_OFF]

    @repeat
    @cast_or_punch_result
    def calibrate_diecase(self):
        # TODO: REFACTOR
        """Casts the "en dash" characters for calibrating the character X-Y
        relative to type body."""
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
        except (e.MatrixNotFound, TypeError, IndexError):
            # Choose it manually
            dash_position = UI.enter_data_or_blank('En dash (–) at: ').upper()
        try:
            # Find the "n" letter automatically
            lowercase_n_position = [mat[2] + str(mat[3])
                                    for mat in self.diecase.layout
                                    if mat[0] == 'n'][0]
        except (e.MatrixNotFound, TypeError, IndexError):
            # Choose itmanually
            lowercase_n_position = UI.enter_data_or_blank('"n" at: ').upper()
        while True:
            # Subroutines for menu options
            def continue_aligning():
                """Do nothing"""
                pass
            # Finished. Return to menu.
            options = {'C': continue_aligning,
                       'M': e.menu_level_up,
                       'E': e.exit_program}
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

    def diagnostics_submenu(self):
        """Settings and alignment menu for servicing the caster"""
        def menu_options():
            """Build a list of options, adding an option if condition is met"""
            caster = not self.mode.punching
            opts = [(e.menu_level_up, 'Back',
                     'Returns to main menu', True),
                    (self.test_all, 'Test outputs',
                     'Tests all the air outputs one by one', True),
                    (self.test_front_pinblock, 'Test the front pinblock',
                     'Tests the pins 1...14', caster),
                    (self.test_rear_pinblock, 'Test the rear pinblock',
                     'Tests the pins NI, NL, A...N one by one', caster),
                    (self.test_justification, 'Test the 0075-S-0005 pinblock',
                     'Tests the pins for justification wedges', caster),
                    (self.test_any_code, 'Send specified signals',
                     'Sends the specified signal combination', True),
                    (self.calibrate_wedges, 'Calibrate the 52D wedge',
                     'Calibrate the space transfer wedge for correct width',
                     caster),
                    (self.calibrate_mould, 'Calibrate mould opening',
                     'Casts 9-unit characters to adjust the type width',
                     caster),
                    (self.calibrate_diecase, 'Calibrate matrix X-Y',
                     'Calibrate the character-to-body positioning', caster)]
            return [(function, description, long_description) for
                    (function, description, long_description, condition)
                    in opts if condition]

        header = ('Diagnostics and machine calibration menu:\n\n')
        # Keep displaying the menu and go back here after any method ends
        while True:
            try:
                # Catch "return to menu" and "exit program" exceptions here
                UI.menu(menu_options(), header=header)()
            except e.ReturnToMenu:
                # Stay in the menu
                pass

    @property
    def stats(self):
        """Ribbon/job statistics"""
        return self.__dict__.get('stats', Stats(self))

    @stats.setter
    def stats(self, stats):
        """Parse the stats to get the ribbon data"""
        self.__dict__['stats'] = (isinstance(stats, Stats) and stats or
                                  Stats(self))

    @property
    def ribbon(self):
        """Ribbon for the casting session"""
        return self.__dict__.get('ribbon', typesetting_data.Ribbon())

    @ribbon.setter
    def ribbon(self, ribbon):
        """Ribbon setter"""
        rib = (isinstance(ribbon, typesetting_data.Ribbon) and ribbon or
               typesetting_data.SelectRibbon())
        self.__dict__['ribbon'] = rib
        self.diecase = self.ribbon.diecase
        # New stats after choosing a different ribbon
        self.stats = Stats(self)

    @property
    def diecase(self):
        """Ribbon for the casting session"""
        return self.__dict__.get('diecase', matrix_data.Diecase())

    @diecase.setter
    def diecase(self, diecase):
        """Ribbon setter"""
        case = (isinstance(diecase, matrix_data.Diecase) and diecase or
                matrix_data.SelectDiecase())
        self.__dict__['diecase'] = case
        self.wedge = self.diecase.wedge

    @property
    def wedge(self):
        """Ribbon for the casting session"""
        return self.__dict__.get('wedge', wedge_data.Wedge())

    @wedge.setter
    def wedge(self, wedge):
        """Ribbon setter"""
        self.__dict__['wedge'] = (isinstance(wedge, wedge_data.Wedge) and
                                  wedge or wedge_data.SelectWedge())

    def _choose_ribbon(self):
        """Chooses a ribbon from database or file"""
        self.ribbon = typesetting_data.SelectRibbon()

    def _choose_diecase(self):
        """Chooses a diecase from database"""
        self.diecase = matrix_data.SelectDiecase()

    def _choose_wedge(self):
        """Chooses a wedge from registered ones"""
        self.wedge = wedge_data.SelectWedge()

    def _display_details(self):
        """Collect ribbon, diecase and wedge data here"""
        UI.display_parameters(self.caster.parameters, self.ribbon.parameters,
                              self.stats.parameters, self.diecase.parameters,
                              self.wedge.parameters)
        UI.pause()

    def _main_menu_options(self):
        """Build a list of options, adding an option if condition is met"""
        # Options are described with tuples: (function, description, condition)
        caster = not self.mode.punching
        ribbon = self.ribbon.contents
        diecase_selected = self.diecase.diecase_id
        opts = [(e.exit_program, 'Exit', 'Exits the program', True),
                (self.cast_or_punch, 'Cast or punch composition',
                 'Casts type or punch a ribbon', ribbon),
                (self._choose_ribbon, 'Select ribbon',
                 'Selects a ribbon from database or file', True),
                (self._choose_diecase, 'Select diecase',
                 'Selects a matrix case from database', True),
                (self._choose_wedge, 'Select wedge',
                 'Selects a wedge from database', True),
                (self.ribbon.display_contents, 'View codes',
                 'Displays all sequences in a ribbon', ribbon),
                (self.diecase.show_layout, 'Show diecase layout',
                 'Views the matrix case layout', diecase_selected),
                (self.adhoc_typesetting, 'Ad-hoc typesetting',
                 'Compose and cast a line of text', diecase_selected),
                (self.cast_sorts, 'Cast sorts',
                 'Cast from matrix with given coordinates', caster),
                (self.cast_spaces, 'Cast spaces or quads',
                 'Casts spaces or quads of a specified width', caster),
                (self._display_details, 'Show detailed info...',
                 'Displays caster, ribbon, diecase and wedge details', True),
                (self.diagnostics_submenu, 'Service...',
                 'Interface and machine diagnostic functions', True)]
        # Built a list of menu options conditionally
        return [(function, description, long_description)
                for (function, description, long_description, condition)
                in opts if condition]

    def main_menu(self):
        """Main menu for the type casting utility."""
        header = ('rpi2caster - CAT (Computer-Aided Typecasting) '
                  'for Monotype Composition or Type and Rule casters.\n\n'
                  'This program reads a ribbon (from file or database) '
                  'and casts the type on a composition caster.'
                  '\n\nCasting / Punching Menu:')
        # Keep displaying the menu and go back here after any method ends
        while True:
            # Catch any known exceptions here
            try:
                UI.menu(self._main_menu_options(), header=header, footer='')()
            except (e.ReturnToMenu, e.MenuLevelUp):
                # Will skip to the end of the loop, and start all over
                pass
