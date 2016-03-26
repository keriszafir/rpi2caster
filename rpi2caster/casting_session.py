# -*- coding: utf-8 -*-
"""
casting_session:

A module for everything related to working on a Monotype composition caster:
-casting composed type,
-punching paper tape (ribbon) for casters without interfaces,
-casting typecases based on character frequencies,
-casting a desired number of characters from matrix with x, y coordinates,
-composing and casting a line of text (not there yet)
-testing all valves, lines and pinblocks,
-calibrating the space transfer wedge, mould opening, diecase draw rods,
 position of character on type body
-sending any codes/combinations to the caster.
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
from . import typesetting_funcs as tsf
# Caster backend
from . import monotype
# Casting stats
from .casting_stats import Stats
# Globally selected UI
from .global_settings import UI
# Typecase casting needs this
from . import letter_frequencies
# Matrix, wedge and typesetting data models
from . import typesetting_data
from . import matrix_data
from . import wedge_data


def choose_sensor_and_driver(casting_routine):
    """Checks current modes (simulation, perforation, testing)"""
    def wrapper(self, *args, **kwargs):
        """Wrapper function"""
        UI.debug_pause('About to %s...' %
                       (self.caster.mode.casting and 'cast composition' or
                        self.caster.mode.testing and 'test the outputs' or
                        self.caster.mode.calibration and
                        'calibrate the machine' or
                        self.caster.mode.punching and 'punch the ribbon'))
        # Instantiate and enter context
        with self.caster.mode.sensor() as self.caster.sensor:
            with self.caster.mode.output() as self.caster.output:
                with self.caster:
                    return casting_routine(self, *args, **kwargs)
    return wrapper


def cast_or_punch_result(ribbon_source):
    """Get the ribbon from decorated routine and cast it"""
    def wrapper(self, *args, **kwargs):
        """Wrapper function"""
        try:
            self.cast_queue(ribbon_source(self, *args, **kwargs))
        except e.CastingAborted:
            pass
        self.caster.mode.diagnostics = False
        self.caster.mode.hmn, self.caster.mode.unitshift = False, False
    return wrapper


def prepare_job(ribbon_casting_workflow):
    """Prepares the job for casting"""

    def wrapper(self, ribbon):
        """Wrapper function"""
        # Stop here if no ribbon
        if not ribbon:
            return
        # Mode aliases
        punching = self.caster.mode.punching
        casting = self.caster.mode.casting
        diagnostics = self.caster.mode.diagnostics
        # Rewind the ribbon if 0005 is found before 0005+0075
        if not diagnostics and not punching and p.stop_comes_first(ribbon):
            ribbon = [x for x in reversed(ribbon)]
        # New stats for the resulting ribbon
        self.stats.ribbon = ribbon
        UI.display_parameters({'Ribbon info': self.stats.ribbon_parameters})
        # Always 1 run for calibrating and punching
        if diagnostics or punching:
            self.stats.runs = 1
            l_skipped = 0
        else:
            prompt = 'How many times do you want to cast it?'
            self.stats.runs = abs(UI.enter_data_or_default(prompt, 1, int))
            # Line skipping - ask user if they want to skip any initial line(s)
            prompt = 'How many initial lines do you want to skip?'
            l_skipped = abs(UI.enter_data_or_default(prompt, 0, int))
        UI.display_parameters({'Session info': self.stats.session_parameters})
        # For each casting run repeat
        while self.stats.get_runs_left():
            queue = deque(ribbon)
            # Apply constraints: 0 <= lines_skipped < lines in ribbon
            l_skipped = max(0, l_skipped)
            l_skipped = min(l_skipped, self.stats.get_ribbon_lines() - 1)
            UI.display('Skipping %s lines' % l_skipped)
            # Take away combinations until we skip the desired number of lines
            # BEWARE: ribbon starts with galley trip!
            # We must give it back after lines are taken away
            code = ''
            while l_skipped + 1 > 0 and not diagnostics:
                code = queue.popleft()
                l_skipped -= 1 * p.check_newline(code)
            queue.appendleft(code)
            # The ribbon is ready for casting / punching
            self.stats.queue = queue
            exit_prompt = '[Y] to start next run or [N] to exit?'
            if ribbon_casting_workflow(self, queue):
                # Casting successful - ready to cast next run - ask to repeat
                # after the last run is completed (because user may want to
                # cast / punch once more?)
                if (self.stats.all_done() and
                        UI.confirm('One more run?', default=diagnostics)):
                    self.stats.add_one_more_run()
            elif casting and UI.confirm('Retry this run?', default=True):
                # Casting aborted - ask if user wants to repeat
                self.stats.undo_last_run()
                self.stats.add_one_more_run()
                lines_ok = self.stats.get_lines_done()
                prompt = 'Skip %s lines successfully cast?' % lines_ok
                if lines_ok > 0 and UI.confirm(prompt, default=True):
                    l_skipped = lines_ok
                # Start this run again
            elif (not self.stats.all_done() and
                  UI.confirm(exit_prompt, default=True)):
                # There are some more runs to do - go on?
                self.stats.undo_last_run()
            else:
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

    def __init__(self, ribbon_file='', diecase='', wedge=''):
        # Caster for this job
        self.caster = monotype.MonotypeCaster()
        self.stats = Stats(self)
        self.ribbon = (ribbon_file and
                       typesetting_data.SelectRibbon(filename=ribbon_file) or
                       typesetting_data.Ribbon())
        self.diecase = (diecase and
                        matrix_data.SelectDiecase(diecase) or self.diecase)
        self.wedge = wedge and wedge_data.SelectWedge(wedge) or self.wedge

    @choose_sensor_and_driver
    @prepare_job
    def cast_queue(self, casting_queue):
        """Casts the sequence of codes in ribbon or self.ribbon.contents,
        displaying the statistics (depending on context:
        casting, punching or testing)
        """
        mode = self.caster.mode
        generator = (p.parse_record(record) for record in casting_queue)
        if not mode.testing:
            self.caster.sensor.check_if_machine_is_working()
        while True:
            try:
                signals, comment = next(generator)
                if comment and not signals:
                    UI.display('\n\n' + comment + '\n' + '-' * len(comment))
                    continue
                # Check if HMN or unit-shift must be applied
                self.stats.signals = signals
                UI.display_parameters({comment: self.stats.code_parameters})
                # Let the caster do the job
                self.caster.process(signals)
            except StopIteration:
                self.stats.end_run()
                return True
            except (e.MachineStopped, KeyboardInterrupt, EOFError):
                # Allow resume in punching mode
                if (mode.punching and not mode.diagnostics and
                        UI.confirm('Continue?', default=True)):
                    self.caster.process(signals)
                else:
                    self.stats.end_run()
                    return False

    @cast_or_punch_result
    def _test_front_pinblock(self):
        """Sends signals 1...14, one by one"""
        UI.pause('Testing the front pinblock - signals 1 towards 14.')
        self.caster.mode.testing = True
        return [str(n) for n in range(1, 15)]

    @cast_or_punch_result
    def _test_rear_pinblock(self):
        """Sends NI, NL, A...N"""
        UI.pause('This will test the front pinblock - signals NI, NL, A...N. ')
        self.caster.mode.testing = True
        return [x for x in c.COLUMNS_17]

    @cast_or_punch_result
    def _test_all(self):
        """Tests all valves and composition caster's inputs in original
        Monotype order: NMLKJIHGFSED 0075 CBA 123456789 10 11 12 13 14 0005.
        """
        UI.pause('This will test all the air lines in the same order '
                 'as the holes on the paper tower: \n%s\n'
                 'MAKE SURE THE PUMP IS DISENGAGED.' % ' '.join(c.SIGNALS))
        self.caster.mode.testing = True
        return [x for x in c.SIGNALS]

    @cast_or_punch_result
    def _test_justification(self):
        """Tests the 0075-S-0005"""
        UI.pause('This will test the justification pin block (0075, S, 0005).')
        self.caster.mode.testing = True
        return ['0075', 'S', '0005']

    @choose_sensor_and_driver
    def _test_any_code(self):
        """Tests a user-specified combination of signals"""
        self.caster.mode.testing = True
        while True:
            UI.display('Enter the signals to send to the caster, '
                       'or leave empty to return to menu: ')
            prompt = 'Signals? (leave blank to exit)'
            signals = p.parse_signals(UI.enter_data_or_blank(prompt))
            if signals:
                self.caster.output.valves_off()
                UI.display('Activating ' + ' '.join(signals))
                self.caster.output.valves_on(signals)
            else:
                break
        self.caster.mode.testing = False

    @cast_or_punch_result
    def cast_composition(self):
        """Casts or punches the ribbon contents if there are any"""
        if not self.ribbon.contents:
            e.return_to_menu()
        return self.ribbon.contents

    def cast_sorts(self):
        """Sorts casting routine, based on the position in diecase.
        Ask user about the diecase row & column, as well as number of sorts.
        """
        order = []
        while True:
            if self.diecase:
                char = UI.enter_data_or_blank('Character?')
                matrix = self.diecase.lookup_matrix(char)
                delta = unit_correction()
            else:
                matrix = self.diecase.lookup_matrix()
                matrix.specify_units()
                delta = 0
            qty = UI.enter_data_or_default('How many sorts?', 10, int)
            order.append((matrix, delta, qty))
            prompt = 'More sorts? Otherwise, start casting'
            if not UI.confirm(prompt, default=True):
                break
        # Now let's calculate and cast it...
        self.cast_batch(order)

    def cast_typecases(self):
        """Casting typecases according to supplied font scheme."""
        enter = UI.enter_data_or_default
        freqs = letter_frequencies.CharFreqs()
        bill = freqs.type_bill
        UI.display('Styles to cast?')
        styles = UI.choose_styles()
        order = []
        for style in styles:
            UI.display_header(style)
            if len(styles) == 1 or style == 'roman':
                scale = 1
            else:
                scale = enter('Scale for %s?' % style, 100, int) / 100.0
            for char, correction, chars_qty in bill:
                qty = int(scale * chars_qty)
                UI.display('%s: %s' % (char, chars_qty))
                matrix = self.diecase.lookup_matrix(char, style)
                order.append((matrix, 0, qty))
            UI.pause()
        self.cast_batch(order)

    def cast_spaces(self):
        """Spaces casting routine, based on the position in diecase.
        Ask user about the space width and measurement unit.
        """
        order = []
        matrix = self.diecase.lookup_matrix(high_or_low_space())
        while True:
            prompt = ('Space width? [6] = 1/6em, [4] = 1/4em, [3] = 1/3em, '
                      '[2] = 1/2em, [1] = 1em, [C] for custom width: ')
            # Width in points
            width = UI.simple_menu(prompt, {'6': 1/6, '4': 1/4, '3': 1/3,
                                            '2': 1/2, '1': 1, 'C': 0}) * 12.0
            # Ask about custom value, then specify units
            while not 2 <= width <= 20:
                prompt = 'Custom width in points (decimal, 2...20)?'
                width = UI.enter_data_or_blank(prompt, float)
            width = round(width * self.wedge.pica / 0.1667 *
                          self.wedge.set_width / 8, 2)
            delta = width - matrix.units
            prompt = 'How many lines?'
            lines = UI.enter_data_or_default(prompt, 1, int)
            order.extend([(matrix, delta, 0)] * lines)
            prompt = 'More spaces? Otherwise, start casting'
            if not UI.confirm(prompt, default=True):
                break
        self.cast_batch(order)

    @cast_or_punch_result
    def cast_batch(self, order=()):
        """Cast a batch of characters, to a given galley width.

        Each character is specified by a tuple:
            (matrix, delta, qty),   where:
        matrix is a matrix_data.Matrix object,
        delta is unit width correction (-2...+10),
        qty is quantity (0 for a filled line, >0 for a given number of chars).

        If there is too many chars for a single line - will cast more lines.
        Not enough to fill the line - will quad out.
        Characters other than low spaces will be separated by double G2 spaces
        to prevent matrices from overheating.
        """
        queue = []
        if not order:
            e.return_to_menu()
        quad = self.diecase.decode_matrix('O15')
        quad.char = ' '
        order = [(quad, 0, 0)] * 2 + list(order)
        # Two quads before and after makes 72 - make line shorter
        line_length = (UI.enter_line_length() * 0.1667 / self.wedge.pica *
                       self.wedge.set_width / 12) - 72
        UI.display('Each line will have two em-quads at the start '
                   'and at the end, to support the type.\n'
                   'Starting with two lines of quads to heat up the mould.')
        for (matrix, delta, qty) in order:
            char_width = matrix.units + delta
            (pos_0075, pos_0005) = matrix.wedge_positions(delta)
            # Add comment if mat has a char specified
            comment = (matrix.islowspace() and ' // low space' or
                       matrix.ishighspace() and ' // high space' or
                       matrix.char and ' // ' + matrix.char or '')
            mat_code = matrix.get_code(delta, self.wedge) + comment
            units_left = 0
            codes = []
            # Qty = 0 means that we fill the line to the brim
            # (cast single line)
            if not qty and matrix.islowspace():
                # Low spaces - fill the line with them
                qty = max(line_length // char_width - 1, 0)
            elif not qty:
                # Chars separated by G-2 spaces - count these units too
                qty = max(line_length // (char_width + self.wedge[2]) - 1, 0)
            while qty > 0:
                # Start the line
                codes = double_justification(pos_0075, pos_0005) + ['O15'] * 2
                units_left = line_length
                # Fill line with sorts and spaces (to slow down casting
                # and prevent matrix overheating)
                while units_left > char_width and qty > 0:
                    codes.append(mat_code)
                    units_left -= char_width
                    qty -= 1
                    # For low spaces and quads, we can cast one after another
                    if not matrix.islowspace():
                        codes.extend(['G2'])
                        units_left -= self.wedge[2]
                while not qty and units_left > self.wedge[15]:
                    # Fill with quads first...
                    codes.append('O15')
                    units_left -= self.wedge[15]
                while not qty and units_left > self.wedge[2]:
                    # ...later with spaces...
                    codes.append('G2')
                    units_left -= self.wedge[2]
                # Finally add two quads at the end and add to queue
                codes.extend(['O15'] * 2)
                queue.extend(codes)
        return queue + END_CASTING

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
        pass

    @cast_or_punch_result
    def _calibrate_wedges(self):
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
        UI.display('Transfer wedge calibration:\n\n'
                   'This function will cast two lines of 5 spaces: '
                   'first: G5, second: GS5 with wedges at 3/8. \n'
                   'Adjust the 52D space transfer wedge '
                   'until the lengths are the same.')
        if not UI.confirm('\nProceed?', default=True):
            return None
        signals = 'G5'
        queue = [c.GALLEY_TRIP] + [signals] * 7
        queue.extend([c.GALLEY_TRIP + '8', c.PUMP_ON + '3'])
        queue.extend([signals + 'S'] * 7)
        queue.extend(c.END_CASTING)
        self.caster.mode.calibration = True
        return queue

    @cast_or_punch_result
    def _calibrate_mould(self):
        """Calculates the width, displays it and casts some 9-unit characters.
        Then, the user measures the width and adjusts the mould opening width.
        """
        UI.display('Mould blade opening calibration:\n'
                   'Cast G5 (9-units wide on S5 wedge), then measure '
                   'the width. Adjust if needed.')
        UI.display_parameters({'Wedge data': self.wedge.parameters})
        UI.display('\n9 units (1en) is %s" wide'
                   % round(self.wedge.em_width / 2, 4))
        UI.display('18 units (1em) is %s" wide\n'
                   % round(self.wedge.em_width, 4))
        if not UI.confirm('\nProceed?', default=True):
            return None
        signals = 'G5'
        self.caster.mode.calibration = True
        return [c.GALLEY_TRIP] + [signals] * 7 + c.END_CASTING

    @cast_or_punch_result
    def _calibrate_diecase(self):
        """Casts the "en dash" characters for calibrating the character X-Y
        relative to type body."""
        UI.display('X-Y character calibration:\n'
                   'Cast some en-dashes and/or lowercase "n" letters, '
                   'then check the position of the character relative to the '
                   'type body.\nAdjust if needed.')
        self.caster.mode.calibration = True
        # Build character list
        queue = []
        for char in ('--', 'n', 'h'):
            mat = self.diecase.lookup_matrix(char)
            if not self.diecase:
                mat.specify_units()
            wedge_positions = mat.wedge_positions()
            corrected = wedge_positions != (3, 8)
            if not queue:
                queue.extend(double_justification(wedge_positions))
            elif corrected:
                queue.extend(single_justification(wedge_positions))
            # Add S signal if width correction is in action
            char = [(corrected and 'S' or '') + mat.code + ' // ' + mat.char]
            queue.extend(char * 3)
        queue.extend(c.END_CASTING)
        return queue

    @choose_sensor_and_driver
    def _calibrate_draw_rods(self):
        """Keeps the diecase at G8 so that the operator can adjust
        the diecase draw rods until the diecase stops moving sideways
        when the centering pin is descending."""
        UI.display('Draw rods calibration:\n'
                   'The diecase will be moved to the central position (G-8), '
                   'turn on the machine\nand adjust the diecase draw rods '
                   'until the diecase stops moving sideways as the\n'
                   'centering pin is descending into the hole in the matrix.')
        if not UI.confirm('\nProceed?', default=True):
            return None
        self.caster.output.valves_on(['G', '8'])
        UI.pause('Sending G8, waiting for you to stop...')

    def diagnostics_submenu(self):
        """Settings and alignment menu for servicing the caster"""
        def menu_options():
            """Build a list of options, adding an option if condition is met"""
            caster = not self.caster.mode.punching
            opts = [(e.menu_level_up, 'Back',
                     'Returns to main menu', True),
                    (self._test_all, 'Test outputs',
                     'Test all the air outputs N...O15, one by one', True),
                    (self._test_front_pinblock, 'Test the front pin block',
                     'Test the pins 1...14', caster),
                    (self._test_rear_pinblock, 'Test the rear pin block',
                     'Test the pins NI, NL, A...N, one by one', caster),
                    (self._test_justification, 'Test the justification block',
                     'Test the pins for 0075, S and 0005, one by one', caster),
                    (self._test_any_code, 'Send specified signal combination',
                     'Send the specified signals to the machine', True),
                    (self._calibrate_wedges, 'Calibrate the 52D wedge',
                     'Calibrate the space transfer wedge for correct width',
                     caster),
                    (self._calibrate_mould, 'Calibrate mould opening',
                     'Cast 9-unit characters to adjust the type width',
                     caster),
                    (self._calibrate_draw_rods, 'Calibrate diecase draw rods',
                     'Keep the matrix case at G8 and adjust the draw rods',
                     caster),
                    (self._calibrate_diecase, 'Calibrate matrix X-Y',
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

    def _main_menu_options(self):
        """Build a list of options, adding an option if condition is met"""
        # Options are described with tuples: (function, description, condition)
        caster = not self.caster.mode.punching
        diecase = self.diecase
        ribbon = self.ribbon
        diecase_info = diecase and ' (current: %s)' % diecase or ''
        opts = [(e.exit_program, 'Exit', 'Exits the program', True),
                (self.cast_composition, 'Cast composition',
                 'Cast type from a selected ribbon',  ribbon and caster),
                (self.cast_composition, 'Punch ribbon',
                 'Punch a paper ribbon for casting without the interface',
                 ribbon and not caster),
                (self._choose_ribbon, 'Select ribbon',
                 'Select a ribbon from database or file', True),
                (self._choose_diecase, 'Select diecase',
                 'Select a matrix case from database' + diecase_info, caster),
                (self._choose_wedge, 'Select wedge',
                 'Enter a wedge designation (current: %s)' % self.wedge.name,
                 caster),
                (self.ribbon.display_contents, 'View codes',
                 'Display all codes in the selected ribbon', ribbon),
                (self.diecase.show_layout, 'Show diecase layout',
                 'View the matrix case layout', diecase and caster),
                # (self.adhoc_typesetting, 'Ad-hoc typesetting',
                # 'Compose and cast a line of text', self.diecase),
                (self.cast_sorts, 'Cast sorts for given characters',
                 'Cast from matrix based on a character', caster and diecase),
                (self.cast_sorts, 'Cast sorts from matrix coordinates',
                 'Cast from matrix at given position', caster and not diecase),
                (self.cast_spaces, 'Cast spaces or quads',
                 'Cast spaces or quads of a specified width', caster),
                (self.cast_typecases, 'Cast typecases',
                 'Cast a typecase based on a selected font scheme',
                 caster and diecase),
                (self._display_details, 'Show details...',
                 'Display ribbon, diecase, wedge and interface info', caster),
                (self._display_details, 'Show details...',
                 'Display ribbon and interface details', not caster),
                (matrix_data.diecase_operations, 'Matrix manipulation...',
                 'Work on matrix cases', True),
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
            except (e.ReturnToMenu, e.MenuLevelUp, KeyboardInterrupt):
                # Will skip to the end of the loop, and start all over
                pass

    @property
    def ribbon(self):
        """Ribbon for the casting session"""
        return self.__dict__.get('_ribbon', typesetting_data.Ribbon())

    @ribbon.setter
    def ribbon(self, ribbon):
        """Ribbon setter"""
        self.__dict__['_ribbon'] = ribbon or typesetting_data.Ribbon()
        self.diecase = ribbon.diecase
        self.wedge = ribbon.wedge

    @property
    def diecase(self):
        """Diecase for the casting session"""
        return self.__dict__.get('_diecase', matrix_data.Diecase())

    @diecase.setter
    def diecase(self, diecase):
        """Diecase setter"""
        self.__dict__['_diecase'] = diecase or matrix_data.Diecase()
        self.wedge = diecase.wedge

    @property
    def wedge(self):
        """Wedge for the casting session"""
        return self.__dict__.get('_wedge', wedge_data.Wedge())

    @wedge.setter
    def wedge(self, wedge):
        """Wedge setter"""
        self.__dict__['_wedge'] = wedge or wedge_data.SelectWedge()
        self.diecase.alternative_wedge = wedge

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
        display = UI.display_parameters
        punching = self.caster.mode.punching
        if self.ribbon:
            display({'Ribbon data': self.ribbon.parameters})
        if self.diecase and not punching:
            display({'Matrix case data': self.diecase.parameters})
        if self.wedge and not punching:
            display({'Wedge data': self.wedge.parameters})
        display({'Caster data': self.caster.parameters})
        UI.pause()


def single_justification(wedge_positions):
    """Returns a single justification sequence"""
    pos_0075, pos_0005 = wedge_positions
    return [c.PUMP_OFF + str(pos_0005), c.PUMP_ON + str(pos_0075)]


def double_justification(wedge_positions):
    """Returns a galley trip / double justification sequence"""
    pos_0075, pos_0005 = wedge_positions
    return [c.GALLEY_TRIP + str(pos_0005), c.PUMP_ON + str(pos_0075)]


def high_or_low_space():
    """Chooses high or low space"""
    spaces = {True: '_', False: ' '}
    high_or_low = UI.confirm('High space?', default=False)
    return spaces[high_or_low]
