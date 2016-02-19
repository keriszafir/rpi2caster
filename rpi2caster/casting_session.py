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
from . import parsing as p
# Custom exceptions
from . import exceptions
# Constants shared between modules
from . import constants as c
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


def check_modes(func):
    """Checks current modes (simulation, perforation, testing)"""
    def wrapper(self, *args, **kwargs):
        """Wrapper function"""
        UI.debug_confirm('About to cast, punch or test')
        # Instantiate and enter context
        with self.mode.sensor() as self.caster.sensor:
            with self.mode.output() as self.caster.output:
                with self.caster:
                    retval = func(self, *args, **kwargs)
                    return retval
    return wrapper


def testing_mode(func):
    """Decorator for setting the testing mode for certain functions"""
    def wrapper(self, *args, **kwargs):
        """Wrapper function"""
        self.mode.testing = True
        retval = func(self, *args, **kwargs)
        self.mode.testing = False
        return retval
    return wrapper


def repeat(func):
    """Decorator for repeating all over"""
    def wrapper(self, *args, **kwargs):
        """Wrapper function"""
        while True:
            func(self, *args, **kwargs)
    return wrapper


def repeat_or_exit(func):
    """Decorator for repeating all over or stopping"""
    def wrapper(self, *args, **kwargs):
        """Wrapper function"""
        while True:
            func(self, *args, **kwargs)
            if not UI.yes_or_no('Start again?'):
                break
    return wrapper


def cast_result(func):
    """Ask for confirmation and cast the resulting ribbon"""
    def wrapper(self, *args, **kwargs):
        """Wrapper function"""
        new_ribbon = func(self, *args, **kwargs)
        if self.mode.testing or UI.yes_or_no('Cast it?'):
            self.ribbon.contents, old_ribbon = new_ribbon, self.ribbon.contents
            retval = self.cast()
            self.ribbon.contents = old_ribbon
            return retval
        else:
            return False
    return wrapper


def stringify(func):
    """Converts the list of tuples to a newline-separated string"""
    def wrapper(self):
        """Wrapper function"""
        data = func(self)
        info = ['%s: %s' % (desc, value) for (value, desc) in data if value]
        return '\n'.join(info) + '\n'
    return wrapper


def temporary_stats(func):
    """Uses brand new stats object for the job"""
    def wrapper(self, *args, **kwargs):
        """Wrapper function"""
        old_stats, self.stats = self.stats, Stats(self)
        retval = func(self, *args, **kwargs)
        self.stats = old_stats
        return retval
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
                       typesetting_data.choose_ribbon(filename=ribbon_file) or
                       typesetting_data.EmptyRibbon())

    @check_modes
    def cast(self):
        """Casts the sequence of codes in self.ribbon.contents,
        displaying the statistics (depending on context:
        casting, punching or testing)"""
        source = self.ribbon.contents
        # Casting mode: cast backwards
        # 0005 at the beginning signals that the ribbon needs rewind
        if p.rewind_needed(source) and self.mode.casting:
            source = [x for x in reversed(source)]
        # Ask how many times to repeat this
        prompt = 'How many repetitions? (default: 1) : '
        jobs = self.mode.casting and UI.enter_data_or_blank(prompt, int) or 1
        self.stats.ribbon_data['all_jobs'] = jobs
        # Get the ribbon statistics
        self.stats.display_ribbon_info()
        # Wait for machine to start
        self.caster.sensor.detect_rotation()
        # Cast/punch it a given number of times
        while jobs:
            self.stats.update_job_info()
            self.stats.display_job_info()
            # Now process the queue
            generator = (p.parse_record(record) for record in source)
            for (signals, comment) in generator:
                comment = comment and UI.display(comment)
                if not signals:
                    # No signals (comment only)- go to the next combination
                    continue
                elif not self.mode.punching:
                    # Use O15 only in punching mode
                    signals = [sig for sig in signals if sig is not 'O15']
                self.stats.update(signals)
                self.stats.display()
                self.caster.process_signals(signals)
            jobs -= 1
            if jobs:
                UI.confirm('%s more job(s) remaining' % jobs)
        # This is the end
        UI.confirm('Finished!')

    @repeat_or_exit
    @testing_mode
    @cast_result
    @temporary_stats
    def test_front_pinblock(self):
        """Sends signals 1...14, one by one"""
        intro = 'Testing the front pinblock - signals 1 towards 14.'
        UI.confirm(intro)
        return [str(n) for n in range(1, 15)]

    @repeat_or_exit
    @testing_mode
    @cast_result
    @temporary_stats
    def test_rear_pinblock(self):
        """Sends NI, NL, A...N"""
        intro = ('This will test the front pinblock - signals NI, NL, A...N. ')
        UI.confirm(intro)
        return [x for x in c.COLUMNS_17]

    @repeat_or_exit
    @testing_mode
    @cast_result
    @temporary_stats
    def test_all(self):
        """Tests all valves and composition caster's inputs in original
        Monotype order: NMLKJIHGFSED 0075 CBA 123456789 10 11 12 13 14 0005.
        """
        intro = ('This will test all the air lines in the same order '
                 'as the holes on the paper tower: \n%s\n'
                 'MAKE SURE THE PUMP IS DISENGAGED.' % ' '.join(c.SIGNALS))
        UI.confirm(intro)
        return [x for x in c.SIGNALS]

    @repeat
    @testing_mode
    @cast_result
    @temporary_stats
    def send_combination(self):
        """Send a specified combination to the caster, repeat"""
        # You can enter new signals or exit
        prompt = ('Enter the signals to send to the caster, '
                  'or leave empty to return to menu: ')
        signals = (UI.enter_data_or_blank(prompt) or
                   exceptions.return_to_menu())
        return [signals]

    @repeat_or_exit
    @temporary_stats
    @cast_result
    # TODO: Selection from diecase by character
    def cast_sorts(self):
        """cast_sorts():

        Sorts casting routine, based on the position in diecase.
        Ask user about the diecase row & column, as well as number of sorts.
        """
        queue = []
        # Outer loop
        while True:
            UI.clear()
            UI.display('Sorts casting by matrix coordinates\n\n')
            prompt = 'Combination? (default: G5): '
            user_code = UI.enter_data_or_blank(prompt).upper() or 'G5'
            combination = p.parse_signals_string(user_code)
            row = p.get_row(combination)
            column = p.get_column(combination)
            units = 0
            # If we want to cast from row 16, we need unit-shift
            # HMN or KMN systems are not supported yet
            question = 'Trying to access 16th row. Use unit shift?'

            unit_shift = row == 16 and UI.yes_or_no(question)
            if row == 16 and not unit_shift:
                UI.confirm('Aborting.')
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
                units = (UI.enter_data_or_blank(prompt, float) or
                         row_units)
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
            if UI.yes_or_no(prompt):
                line_codes = ['NKJS 0005 0075' + str(pos_0005),
                              'NKS 0075' + str(pos_0075)]
                line_codes.extend([signals] * sorts)
                queue.extend(line_codes * lines)
            if not UI.yes_or_no('Another combination?'):
                # Finished gathering data
                break
        queue.append('NKJS 0005 0075')
        queue.append('NJS 0005')
        return queue

    @cast_result
    @temporary_stats
    def cast_spaces(self):
        """cast_spaces():

        Spaces casting routine, based on the position in diecase.
        Ask user about the space width and measurement unit.
        """
        # Make a queue
        queue = []
        # Ask about line length
        prompt = 'Galley line length? [pica or cicero] (default: 25) : '
        line_length = abs(UI.enter_data_or_blank(prompt, int) or 25)
        # Measurement system
        options = {'A': 0.1660,
                   'B': 0.1667,
                   'D': 0.1776,
                   'F': 0.1629}
        message = ('Measurement? [A]merican Johnson pica = 0.166", '
                   '[B]ritish pica = 0.1667",\n [D]idot cicero = 0.1776", '
                   '[F]ournier cicero = 0.1629": ')
        pica_def = UI.simple_menu(message, options)
        # Unit line length:
        unit_line_length = int(18 * pica_def / 0.1667 * line_length *
                               self.wedge.set_width / 12)
        # Now we can cast multiple different spaces
        while True:
            prompt = 'Combination? (default: G5): '
            code_string = UI.enter_data_or_blank(prompt).upper() or 'G5'
            combination = p.parse_signals_string(code_string)
            row = p.get_row(combination)
            column = p.get_column(combination)
            width = 0.0
            # Not using unit shift by default, ask for row 16
            question = 'Trying to access 16th row. Use unit shift?'
            unit_shift = row == 16 and UI.yes_or_no(question)
            if row == 16 and not unit_shift:
                UI.confirm('Aborting.')
                continue
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
            if UI.yes_or_no(prompt):
                line_codes = ['NKJS 0005 0075' + str(pos_0005),
                              'NKS 0075' + str(pos_0075)]
                line_codes.extend([signals] * sorts)
                queue.extend(line_codes * lines)
            if not UI.yes_or_no('Another combination?'):
                # Finished gathering data
                break
        queue.extend(['NKJS 0005 0075', 'NJS 0005'])
        return queue

    @repeat_or_exit
    @cast_result
    @temporary_stats
    def align_wedges(self):
        """Allows to align the justification wedges so that when you're
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
        queue = ['NKJS 0005 0075'] + [signals] * 7
        queue.extend(['NKJS 0005 0075 8', 'NKS 0075 3'] + [signals + 'S'] * 7)
        queue.extend(['NKJS 0005 0075', 'NJS 0005'])
        return queue

    @repeat_or_exit
    @cast_result
    @temporary_stats
    def align_mould(self):
        """align_mould:

        Calculates the width, displays it and casts some 9-unit characters.
        Then, the user measures the width and adjusts the mould opening width.
        """
        intro = ('Mould blade opening calibration:\n'
                 'Cast G5 (9-units wide on S5 wedge), then measure the width. '
                 'Adjust if needed.')
        UI.display(intro)
        if self.wedge.brit_pica:
            pica = 0.1667
        else:
            pica = 0.166
        # We calculate the width of double 9 units = 18 units, i.e. 1 pica em
        em_width = pica * self.wedge.set_width / 12.0
        UI.display('9 units (1en) is %s wide' % round(em_width / 2, 4))
        UI.display('18 units (1em) is %s wide' % round(em_width, 4))
        signals = 'G5'
        queue = ['NKJS 0005 0075'] + [signals] * 7
        queue.extend(['NKJS 0005 0075', 'NJS 0005'])
        return queue

    @repeat_or_exit
    @cast_result
    @temporary_stats
    def align_diecase(self):
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

    @cast_result
    @temporary_stats
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
        typesetter.session_setup(self.diecase)
        # Enter text
        text = UI.enter_data("Enter text to compose: ")
        typesetter.text_source = typesetter.parse_and_generate(text)
        # Translate the text to Monotype signals
        typesetter.compose()
        queue = typesetter.justify()
        self.ribbon.contents, old_ribbon = queue, self.ribbon.contents
        if UI.yes_or_no('Show the codes?'):
            self.ribbon.display_contents()
        self.ribbon.contents = old_ribbon
        return queue

    def heatup(self):
        """Casts 2 lines x 20 quads from the O15 matrix to heat up the mould"""
        queue = (['NKJS 0005 0075'] + ['O15'] * 20 +
                 ['NKJS 0005 0075'] + ['NJS 0005'])
        return queue

    def diagnostics_submenu(self):
        """Settings and alignment menu for servicing the caster"""
        def menu_options():
            """Build a list of options, adding an option if condition is met"""
            perforator = self.mode.punching
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

    @property
    def stats(self):
        """Ribbon/job statistics"""
        return self.__dict__['stats']

    @stats.setter
    def stats(self, stats):
        """Parse the stats to get the ribbon data"""
        self.__dict__['stats'] = stats
        self.__dict__['stats'].update_ribbon_info()

    @property
    def ribbon(self):
        """Ribbon for the casting session"""
        return self.__dict__['ribbon']

    @ribbon.setter
    def ribbon(self, ribbon):
        """Ribbon setter"""
        self.__dict__['ribbon'] = ribbon
        self.diecase = self.__dict__['ribbon'].diecase
        # New stats after choosing a different ribbon
        self.stats = Stats(self)

    @property
    def diecase(self):
        """Ribbon for the casting session"""
        return self.__dict__['diecase']

    @diecase.setter
    def diecase(self, diecase):
        """Ribbon setter"""
        self.__dict__['diecase'] = diecase
        self.wedge = self.__dict__['diecase'].wedge

    @property
    def wedge(self):
        """Ribbon for the casting session"""
        return self.__dict__['wedge']

    @wedge.setter
    def wedge(self, wedge):
        """Ribbon setter"""
        self.__dict__['wedge'] = wedge

    def _choose_ribbon(self):
        """Chooses a ribbon from database or file"""
        self.ribbon = typesetting_data.choose_ribbon()

    def _choose_diecase(self):
        """Chooses a diecase from database"""
        self.diecase = matrix_data.choose_diecase()

    def _choose_wedge(self):
        """Chooses a wedge from registered ones"""
        self.wedge = wedge_data.choose_wedge()

    @stringify
    def _display_additional_info(self):
        """Collect ribbon, diecase and wedge data here"""
        data = self.caster.get_parameters()
        data.extend(self.ribbon.get_parameters())
        data.extend(self.diecase.get_parameters())
        data.extend(self.wedge.get_parameters())
        data.extend(self.stats.get_parameters())
        return data

    def _main_menu_options(self):
        """Build a list of options, adding an option if condition is met"""
        # Options are described with tuples: (function, description, condition)
        perforator = self.mode.punching
        ribbon = self.ribbon.contents
        diecase_selected = self.diecase.diecase_id
        opts = [(exceptions.exit_program, 'Exit', 'Exits the program', True),
                (self.cast, 'Cast or punch composition',
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


class Stats(object):
    """Casting statistics gathering and displaying functions"""
    def __init__(self, session):
        self.ribbon_data = {'lines_done': 0, 'all_lines': 0, 'current_job': 0,
                            'all_jobs': 0, 'job_lines': 0, 'job_chars': 0,
                            'job_codes': 0, 'all_chars': 0}
        self.current = {'combination': [], '0075': '15', '0005': '15'}
        self.previous = self.current
        self.session = session

    def display(self):
        """Displays the current stats depending on session parameters"""
        if self.session.mode.casting:
            UI.display(self._full_info())
        elif self.session.mode.punching:
            UI.display(self._brief_info())
        elif self.session.mode.testing:
            UI.display(self._brief_info())

    def display_ribbon_info(self):
        """Displays the ribbon data"""
        UI.display(self._get_ribbon_info())

    def display_job_info(self):
        """Displays info at the beginning of the job"""
        UI.display(self._get_job_info() + self._get_ribbon_info())

    @stringify
    def _get_job_info(self):
        """Gets info about current job"""
        return [(self.ribbon_data['current_job'], 'Current job'),
                (self.ribbon_data['all_jobs'] -
                 self.ribbon_data['current_job'], 'Jobs remaining')]

    @stringify
    def _get_ribbon_info(self):
        """Gets ribbon parameters"""
        return [(self.ribbon_data['job_codes'], 'Combinations in ribbon'),
                (self.ribbon_data['job_lines'], 'Lines to cast'),
                (self.ribbon_data['job_chars'], 'Characters incl. spaces')]

    def get_parameters(self):
        """Gets ribbon parameters"""
        return [(self.ribbon_data['job_codes'], 'Combinations in ribbon'),
                (self.ribbon_data['job_lines'], 'Lines to cast'),
                (self.ribbon_data['job_chars'], 'Characters incl. spaces')]

    @stringify
    def _brief_info(self):
        """Brief info: current combination, comment, combinations done,
        all combinations, percent done"""
        return [(' '.join(self.current['combination']), 'Current combination')]

    @stringify
    def _full_info(self):
        """Full statistics: all from brief info and wedge positions"""
        return [(' '.join(self.current['combination']), 'Current combination')]

    def update(self, combination):
        """Updates the stats based on current combination"""
        # Remember the previous state
        self.previous = self.current
        # Update line info
        self._set_current(combination)
        # Check the pump working/non-working status in the casting mode
        if self.session.mode.casting:
            self._check_pump()

    def update_job_info(self):
        """Updates the info on starting the new job"""
        pass

    def update_ribbon_info(self):
        """Parses the ribbon, counts combinations, lines and characters"""
        self.ribbon_data['job_codes'] = 0
        self.ribbon_data['job_lines'] = 0
        self.ribbon_data['job_chars'] = 0
        generator = (p.parse_record(x) for x in self.session.ribbon.contents)
        for (combination, _) in generator:
            if combination:
                # Guards against empty combination i.e. line with comment only
                self.ribbon_data['job_codes'] += 1
            if p.check_newline(combination):
                self.ribbon_data['job_lines'] += 1
            elif p.check_character(combination):
                self.ribbon_data['job_chars'] += 1

    def _set_current(self, combination):
        """Gets the current combination and updates casting statistics"""
        self.current['combination'] = combination or ['O15']
        self._update_wedge_positions(combination)

    def _check_pump(self):
        """Checks pump based on current and previous combination"""
        previous = self.previous['combination']
        current = self.current['combination']
        # Was it running until now? Get it from the pump object
        running = self.session.caster.pump.is_working
        # Was it started before (0075 with or without 0005)?
        started = p.check_0075(previous)
        # Was it stopped (0005 without 0075)
        stopped = p.check_0005(previous) and not p.check_0075(previous)
        # Is 0005 or 0075 in current combination? (if so - temporary stop)
        on_hold = p.check_0005(current) or p.check_0075(current)
        # Determine the current status
        pump_status = (running or started) and not stopped and not on_hold
        self.current['pump_status'] = pump_status
        # Feed it back to pump object
        self.session.caster.pump.is_working = self.current['pump_status']
        self.session.caster.pump.current_0005 = self.current['0005']
        self.session.caster.pump.current_0075 = self.current['0075']

    def _update_wedge_positions(self, combination):
        """Gets current positions of 0005 and 0075 wedges"""
        # Check 0005
        if p.check_0005(combination):
            candidates = [x for x in range(15) if str(x) in combination]
            self.current['0005'] = candidates and str(min(candidates)) or '15'
        # Check 0075
        if p.check_0075(combination):
            candidates = [x for x in range(15) if str(x) in combination]
            self.current['0075'] = candidates and str(min(candidates)) or '15'
