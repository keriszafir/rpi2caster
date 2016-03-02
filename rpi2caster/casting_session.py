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
# Caster backend
from . import monotype
# Casting stats
from .casting_stats import Stats
# Globally selected UI
from .global_settings import UI
# Matrix, wedge and typesetting data models
from . import typesetting_data
from . import matrix_data
from . import wedge_data
# Constants for control sequences
GALLEY_TRIP = 'NKJS 0005 0075'
PUMP_OFF = 'NJS 0005'
PUMP_ON = 'NKS 0075'


def choose_sensor_and_driver(casting_routine):
    """Checks current modes (simulation, perforation, testing)"""
    def wrapper(self, *args, **kwargs):
        """Wrapper function"""
        UI.debug_pause('About to %s' %
                       (self.caster.mode.casting and 'cast composition...' or
                        self.caster.mode.testing and 'test outputs...' or
                        self.caster.mode.punching and 'punch ribbon...'))
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
    line_of_quads = ['O15'] * 20 + ['NKJS 0005 0075']
    # Alias to make it shorter
    enter = UI.enter_data_or_blank

    def wrapper(self, ribbon):
        """Wrapper function"""
        # Mode aliases
        punching = self.caster.mode.punching
        diagnostics = self.caster.mode.diagnostics
        # Rewind the ribbon if 0005 is found before 0005+0075
        if not diagnostics and not punching and p.stop_comes_first(ribbon):
            ribbon = [x for x in reversed(ribbon)]
        # New stats for the resulting ribbon
        self.stats.ribbon = ribbon
        UI.display_parameters({'Ribbon info': self.stats.ribbon_parameters})
        # Always 1 run for calibrating and punching
        prompt = 'How many times do you want to cast it? (default: 1) : '
        self.stats.runs = abs(not diagnostics and not punching and
                              enter(prompt, int) or 1)
        # Line skipping - ask user if they want to skip any initial line(s)
        prompt = 'How many lines do you want to skip?  (default: 0): '
        l_skipped = abs(not diagnostics and not punching and
                        enter(prompt, int) or 0)
        # Leave at least one line in the ribbon to cast
        l_skipped = min(l_skipped, self.stats.get_ribbon_lines() - 1)
        UI.display_parameters({'Session info': self.stats.session_parameters})
        # For each casting run repeat
        while self.stats.get_runs_left():
            queue = deque(ribbon)
            quad_lines = 0
            if (not punching and not diagnostics and
                    self.stats.get_current_run() < 2 and
                    UI.confirm('Cast 2 extra lines to heat up the mould?')):
                l_skipped -= 2
                # When less than 2 lines can be skipped, we'll cast quads
                quad_lines = max(-l_skipped, 0)
            # Apply constraints: 0 <= lines_skipped < lines in ribbon
            l_skipped = max(0, l_skipped)
            UI.display(l_skipped and ('Skipping %s lines' % l_skipped) or '')
            UI.display(quad_lines and ('Casting %s line(s) of 20 quads'
                                       % quad_lines) or '')
            # Make sure we take off lines from the beginning of the
            # casting job - i.e. last lines of text; count the lines
            code = ''
            # Add one more line to skip - because ribbon starts with 0075-0005
            # Guard against negative infinite loop if l_skipped == -2
            while l_skipped + 1 > 0 and not diagnostics:
                code = queue.popleft()
                l_skipped -= 1 * p.check_newline(code)
            # Add it back, then add those quads
            queue.appendleft(code)
            queue.extendleft(quad_lines * line_of_quads)
            # The ribbon is ready for casting / punching
            self.stats.queue = queue
            UI.display_parameters({'Current run': self.stats.run_parameters})
            if not ribbon_casting_workflow(self, queue):
                l_skipped = self.stats.get_lines_done()
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
        self.stats = Stats(self)
        self.ribbon = (ribbon_file and
                       typesetting_data.SelectRibbon(filename=ribbon_file) or
                       typesetting_data.Ribbon())

    @choose_sensor_and_driver
    @prepare_job
    def cast_queue(self, casting_queue):
        """Casts the sequence of codes in ribbon or self.ribbon.contents,
        displaying the statistics (depending on context:
        casting, punching or testing)
        """
        generator = (p.parse_record(record) for record in casting_queue)
        if not self.caster.mode.testing:
            self.caster.sensor.check_if_machine_is_working()
        try:
            while True:
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
            # End of ribbon - ready to cast next run - ask to repeat casting
            self.stats.next_run()
            if not self.stats.get_runs_left() and UI.confirm('Repeat?'):
                self.stats.one_more_run()
            return True
        except (e.MachineStopped, KeyboardInterrupt, EOFError):
            exit_prompt = '[Y] to start next run or [N] to exit?'
            if UI.confirm('Retry this job?'):
                return False
            elif self.stats.get_runs_left() and not UI.confirm(exit_prompt):
                # Bypass the caller function
                raise e.ReturnToMenu

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
        self.caster.mode.testing = False
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
        self.caster.mode.testing = False

    @cast_or_punch_result
    def cast_composition(self):
        """Casts or punches the ribbon contents"""
        ribbon = self.ribbon.contents
        return ribbon and ribbon or e.return_to_menu()

    @cast_or_punch_result
    def cast_sorts(self, source=()):
        """Sorts casting routine, based on the position in diecase.
        Ask user about the diecase row & column, as well as number of sorts.
        """
        queue = []
        casting_queue = [x for x in source] or [(None, None, 0)]
        for (char, style, qty) in casting_queue:
            # Make an infinite iterator when we call this function without
            # the list of character-style pairs
            prompt = ('Character: %s\n'
                      'Y: add to casting queue, N: skip it?' % char)
            if not char:
                casting_queue.append((char, style, 0))
            elif not UI.confirm(prompt):
                continue
            prompt = 'Character? (leave blank to end specifying characters): '
            char = char or UI.enter_data_or_blank(prompt)
            if not char:
                break
            available_styles = {'r': 'roman', 'b': 'bold',
                                'i': 'italic', 's': 'smallcaps',
                                'l': 'subscript', 'u': 'superscript'}
            style = style or (available_styles.get(UI.enter_data_or_blank(
                'Styles: [r]oman, [b]old, [i]talic, [s]mall caps, '
                '[l]ower index, [u]pper index (default: roman): ', str), 'r'))
            matrix = self.diecase.get_matrix(char, [style])
            diff = matrix.units - matrix.row_units
            wedge_positions = self._calculate_wedges(diff)
            # Ask for number of sorts and lines, no negative numbers here
            prompt = '\nHow many sorts per line? (default: 10): '
            qty = qty or abs(UI.enter_data_or_blank(prompt, int) or 10)
            prompt = '\nHow many lines? (default: 1): '
            lines = abs(UI.enter_data_or_blank(prompt, int) or 1)
            UI.display('\n')
            # Warn if we want to cast too many sorts from a single matrix
            warning = ('Warning: you want to cast a single character more than'
                       ' 10 times. This may lead to matrix overheating!\n')
            if qty > 10:
                UI.display(warning)
            UI.display('\n')
            line_codes = [GALLEY_TRIP + str(wedge_positions['0005']),
                          PUMP_ON + str(wedge_positions['0075'])] + ['O15'] * 2
            # 2 quads in the beginning, then spaces, then 2 quads in the end
            line_codes.extend([matrix.code + (diff and 'S' or '') +
                               '// ' + matrix.char] * qty)
            line_codes.extend(['O15'] * 2)
            # Ask for confirmation
            queue.extend(line_codes * lines)
        # No sequences? No casting.
        if queue and UI.confirm('Cast the sequence?'):
            UI.display('\nEach line will have two em-quads at the start '
                       'and at the end, to support the type.\n')
            return queue + [GALLEY_TRIP, PUMP_OFF, PUMP_OFF]
        else:
            e.return_to_menu()

    @cast_or_punch_result
    def cast_spaces(self):
        """Spaces casting routine, based on the position in diecase.
        Ask user about the space width and measurement unit.
        """
        queue = []
        # Measurement system
        prompt = ('Measurement unit to use? \n'
                  '[A]merican Johnson pica = 0.166",'
                  '[B]ritish pica = 0.1667",\n[D]idot cicero = 0.1776", '
                  '[F]ournier cicero = 0.1629": ')
        pica = UI.simple_menu(prompt, {'A': 0.1660, 'B': 0.1667,
                                       'D': 0.1776, 'F': 0.1629})
        # Ask about line length
        prompt = 'Galley line length in above units? (default: 25) : '
        line_length = abs(UI.enter_data_or_blank(prompt, int) or 25)*1.0
        # We need 72 additional units for two quads before and after line
        line_length = int(18 * pica / 0.1667 * line_length *
                          self.wedge.set_width / 12) - 72
        while True:
            matrix = self.diecase.get_matrix(' ')
            prompt = ('Space width? [6] = 1/6em, [4] = 1/4em, [3] = 1/3em, '
                      '[2] = 1/2em, [1] = 1em, [C] for custom width: ')
            # Width in points
            width = UI.simple_menu(prompt, {'6': 1/6, '4': 1/4, '3': 1/3,
                                            '2': 1/2, '1': 1, 'C': 0}) * 12.0
            # Ask about custom value, then specify units
            while not 2 <= width <= 20:
                prompt = 'Custom width in points (decimal, 2...20) ? : '
                width = UI.enter_data_or_blank(prompt, float)
            prompt = '\nHow many lines? (default: 1): '
            lines = abs(UI.enter_data_or_blank(prompt, int) or 1)
            prompt = ('Casting %s lines of %s-point spaces from %s%s. OK?'
                      % (lines, width, matrix.column, matrix.row))
            # Save for later
            comment = '%s-point space' % width
            # Repeat
            if not UI.confirm(prompt):
                continue
            # Calculate unit width of said number of points
            # We do it this way:
            # units = picas * set_width/12 * 18
            # a pica is 12 points, so:
            # units = points * set_width/12 * 1 / 12 * 18
            # 18 / (12*12) = 0.125, hence division by 8
            width = round(width * pica / self.wedge.pica *
                          self.wedge.set_width / 8, 2)
            # How many spaces will fit in a line? Calculate it...
            qty = int(line_length // width)
            # Check if the corrections are needed at all
            diff = width - matrix.row_units
            wedge_positions = self._calculate_wedges(diff)
            # Add 'S' if there is width difference
            signals = matrix.code + (diff and 'S' or '') + '// ' + comment
            line_codes = [GALLEY_TRIP + str(wedge_positions['0005']),
                          PUMP_ON + str(wedge_positions['0075'])]
            # 2 quads in the beginning, then spaces, then 2 quads in the end
            line_codes.extend(['O15'] * 2 + [signals] * qty + ['O15'] * 2)
            # Ask for confirmation
            queue.extend(line_codes * lines)
            if queue and UI.confirm('Y to cast, N to add some more spaces?'):
                return queue + [GALLEY_TRIP, PUMP_OFF, PUMP_OFF]

    def cast_typecases(self):
        """Casting typecases according to supplied font scheme."""
        scheme = typesetting_data.SelectFontScheme()
        prompt = ('Scale in %, relative to 100 "a" characters:\n'
                  '(leave blank to exit) ?: ')
        scale = UI.enter_data_or_blank(prompt, float) / 100
        if not scale:
            return
        available_styles = {'r': 'roman', 'b': 'bold',
                            'i': 'italic', 's': 'smallcaps',
                            'l': 'subscript', 'u': 'superscript'}
        print('Styles to cast?\n'
              'Available styles: [r]oman, [b]old, [i]talic, [s]mall caps,\n'
              '[l]ower index (a.k.a. subscript, inferior), '
              '[u]pper index (a.k.a. superscript, superior).\n'
              'Leave blank for roman.')
        styles_string = UI.enter_data_or_blank('Styles?: ') or 'r'
        styles = [available_styles.get(char, None) for char in styles_string]
        styles = [style for style in styles if style is not None]
        # Now generate and display the casting queue
        sorts = {style: [(char, style, round(qty * scale))
                         for (char, ch_style, qty) in scheme.layout
                         if ch_style == style] for style in styles}
        queue = []
        for style in sorts:
            UI.display_header(style)
            queue.extend(sorts[style])
            for (char, _, qty) in sorts[style]:
                UI.display('%s : %s' % (char, qty))
        self.cast_sorts(queue)

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
        intro = ('Transfer wedge calibration:\n\n'
                 'This function will cast two lines of 5 spaces: '
                 'first: G5, second: GS5 with wedges at 3/8. \n'
                 'Adjust the 52D space transfer wedge '
                 'until the lengths are the same.')
        UI.display(intro)
        signals = 'G5'
        queue = [GALLEY_TRIP] + [signals] * 7
        queue.extend([GALLEY_TRIP + '8', PUMP_ON + '3'] + [signals + 'S'] * 7)
        queue.extend([GALLEY_TRIP, PUMP_OFF, PUMP_OFF])
        self.caster.mode.calibration = True
        return queue

    @cast_or_punch_result
    def _calibrate_mould(self):
        """Calculates the width, displays it and casts some 9-unit characters.
        Then, the user measures the width and adjusts the mould opening width.
        """
        intro = ('Mould blade opening calibration:\n'
                 'Cast G5 (9-units wide on S5 wedge), then measure the width. '
                 'Adjust if needed.')
        UI.display(intro)
        # We calculate the width of double 9 units = 18 units, i.e. 1 pica em
        em_width = self.wedge.pica * self.wedge.set_width / 12.0
        UI.display('9 units (1en) is %s" wide' % round(0.5 * em_width, 4))
        UI.display('18 units (1em) is %s" wide' % round(em_width, 4))
        signals = 'G5'
        self.caster.mode.calibration = True
        return [GALLEY_TRIP] + [signals] * 7 + [GALLEY_TRIP] + [PUMP_OFF] * 2

    def _calibrate_diecase(self):
        """Casts the "en dash" characters for calibrating the character X-Y
        relative to type body."""
        UI.display('X-Y character calibration:\n'
                   'Cast some en-dashes and/or lowercase "n" letters, '
                   'then check the position of the character relative to the '
                   'type body.\nAdjust if needed.')
        self.caster.mode.calibration = True
        self.cast_sorts([('–', 'roman', 7), ('n', 'roman', 7),
                         ('h', 'roman', 7)])

    def diagnostics_submenu(self):
        """Settings and alignment menu for servicing the caster"""
        def menu_options():
            """Build a list of options, adding an option if condition is met"""
            caster = not self.caster.mode.punching
            opts = [(e.menu_level_up, 'Back',
                     'Returns to main menu', True),
                    (self._test_all, 'Test outputs',
                     'Tests all the air outputs one by one', True),
                    (self._test_front_pinblock, 'Test the front pinblock',
                     'Tests the pins 1...14', caster),
                    (self._test_rear_pinblock, 'Test the rear pinblock',
                     'Tests the pins NI, NL, A...N one by one', caster),
                    (self._test_justification, 'Test the 0075-S-0005 pinblock',
                     'Tests the pins for justification wedges', caster),
                    (self._test_any_code, 'Send specified signals',
                     'Sends the specified signal combination', True),
                    (self._calibrate_wedges, 'Calibrate the 52D wedge',
                     'Calibrate the space transfer wedge for correct width',
                     caster),
                    (self._calibrate_mould, 'Calibrate mould opening',
                     'Casts 9-unit characters to adjust the type width',
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
        ribbon = self.ribbon.contents
        diecase_selected = self.diecase.diecase_id
        opts = [(e.exit_program, 'Exit', 'Exits the program', True),
                (self.cast_composition, 'Cast or punch composition',
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
                (self.cast_typecases, 'Cast typecases',
                 'Casts a typecase based on a selected font scheme',
                 caster and diecase_selected),
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

    @property
    def ribbon(self):
        """Ribbon for the casting session"""
        return self.__dict__.get('_ribbon', typesetting_data.Ribbon())

    @ribbon.setter
    def ribbon(self, ribbon):
        """Ribbon setter"""
        rib = (isinstance(ribbon, typesetting_data.Ribbon) and ribbon or
               typesetting_data.SelectRibbon())
        self.__dict__['_ribbon'] = rib
        self.diecase = self.ribbon.diecase

    @property
    def diecase(self):
        """Ribbon for the casting session"""
        return self.__dict__.get('_diecase', matrix_data.Diecase())

    @diecase.setter
    def diecase(self, diecase):
        """Ribbon setter"""
        case = (isinstance(diecase, matrix_data.Diecase) and diecase or
                matrix_data.SelectDiecase())
        self.__dict__['_diecase'] = case
        self.wedge = self.diecase.wedge

    @property
    def wedge(self):
        """Ribbon for the casting session"""
        return self.__dict__.get('_wedge', wedge_data.Wedge())

    @wedge.setter
    def wedge(self, wedge):
        """Ribbon setter"""
        self.__dict__['_wedge'] = (isinstance(wedge, wedge_data.Wedge) and
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
        UI.display_parameters({'Caster data': self.caster.parameters,
                               'Ribbon data': self.ribbon.parameters,
                               'Matrix case data': self.diecase.parameters,
                               'Wedge data': self.wedge.parameters})
        UI.pause()

    def _calculate_wedges(self, diff):
        """calculate_wedges:

        Calculates and returns wedge positions for character.
        Uses pre-calculated unit width difference between row's unit width
        and character's width (with optional corrections).
        """
        # Calculate the inch width of delta
        # 1 pica = 18 units 12 set = 0.1667 (old British pica)
        # or 0.1660 (Am. pica); unit_width = 12 * pica / (set width * 18)
        steps_0005 = int(diff * 0.166 / self.wedge.pica *
                         self.wedge.set_width * 2000 / 1296) + 53
        # Adjust the wedges
        # You do it in respect to the neutral position i.e. 3/8:
        # 3 steps of 0075 and 8 steps of 0005 wedge.
        # 3 / 8 = 1 * 15 + 8 = 53 - that would be 53 steps of 0005 wedge
        # Add safeguards against wrong wedge positions
        # Minimum wedge positions (0075/0005) are 1/1, maximum 15/15
        # This is equivalent to min 1*15+1=16 steps and max 15*15+15=240 steps
        # WARNING - the actual value when casting chars/high spaces must not be
        # wider than the matrix (.2" for small composition, 0.4 for 2x2 etc),
        # otherwise we get a splash between mats!
        steps_0005 = min(steps_0005, 240)
        # Lower limit: 1/1 wedge positions:
        steps_0005 = max(16, steps_0005)
        steps_0075 = 0
        while steps_0005 > 15:
            steps_0005 -= 15
            steps_0075 += 1
        # Got the wedge positions, return them
        return {'0075': steps_0075, '0005': steps_0005}
