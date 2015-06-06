#!/usr/bin/python
# -*- coding: utf-8 -*-

"""rpi2caster - control a Monotype composition caster with Raspberry Pi.

Monotype composition caster & keyboard paper tower control program.

This program sends signals to the solenoid valves connected to the
composition caster's (or keyboard's) paper tower. When casting,
the program uses methods of the Monotype class and waits for the machine
to send feedback (i.e. an "air bar down" signal), then turns on
a group of valves. On the "air bar up" signal, valves are turned off and
the program reads another code sequence, just like the original paper
tower.

The application consists of several layers:
layer 5 - user interface
layer 4 - casting job layer which implements the logic (Casting class)
layer 3 - signals processing for the caster, or mockup caster for testing
layer 2 - lower-level hardware control routines
          (activate_valves, deactivate_valves and send_signals_to_caster)
layer 1 - dependencies: wiringPi library, sysfs GPIO interface
layer 0 - hardware, kernel and /dev filesystem

In "punching" mode, the program sends code sequences to the paper tower
(controlled by valves as well) in arbitrary time intervals, and there is
no machine feedback.

rpi2caster can also:
-cast a user-specified number of sorts from a matrix with given
coordinates (the "pump on", "pump off" and "line to the galley"
code sequences will be issued automatically),
-test all the valves, pneumatic connections and control mechanisms in a
caster (i.e. pinblocks, 0005/S/0075 mechs, unit-adding & unit-shift valves
and attachments), line by line,
-send a user-defined combination of signals for a time as long as the user
desires - just like piercing holes in a piece of ribbon and clamping the
air bar down,
-help calibrating the space transfer wedge by casting a combination without
and with the S-needle with 0075 wedge at 3 and 0005 wedge at 8 (neutral)
-heat the mould up by casting some em-quads

During casting, the program automatically detects the machine movement,
so no additional actions on user's part are required.

In the future, the program will have an "emergency stop" feature.
When an interrupt on a certain Raspberry Pi's GPIO is detected, the program
stops sending codes to the caster and sends a 0005 combination instead.
The pump is immediately stopped.
"""

# IMPORTS:
# Built-in time library
import time
# Signals parsing methods for rpi2caster
import parsing
# Database module for rpi2caster:
import database
# Physical caster module for rpi2caster:
import monotype
# Mockup caster module for rpi2caster:
import simulation
# User interfaces module for rpi2caster:
import userinterfaces
# Custom exceptions
import newexceptions
# MCP23017 driver & hardware abstraction layer library:
UI = userinterfaces.TextUI()


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

    def __init__(self, ribbonFile=''):
        self.UI = None
        self.caster = None
        self.ribbonFile = ribbonFile
        self.ribbon = []
        self.lineAborted = None
        self.metadata = {}
        self.diecase = None

    def __enter__(self):
        self.UI.debug_info('Entering casting job context...')
        with self.UI:
            self.main_menu()

    def cast_composition(self):
        """cast_composition()

        Composition casting routine. The input file is read backwards -
        last characters are cast first, after setting the justification.
        """
        # Count all characters and lines in the ribbon
        [linesAll, charsAll] = parsing.count_lines_and_characters(self.ribbon)
        # Characters already cast - start with zero
        currentChar = 0
        charsLeft = charsAll
        # Line currently cast: since the caster casts backwards
        # (from the last to the first line), this will decrease.
        currentLine = linesAll
        # The program counts galley trip sequences and determines line count.
        # The first code to send to machine is galley trip (which also sets the
        # justification wedges and turns the pump on). So, subtract this one
        # to have the correct number of lines.
        linesAll -= 1
        # Show the numbers to the operator
        self.UI.display('Lines found in ribbon: %i' % linesAll)
        self.UI.display('Characters: %i' % charsAll)
        # For casting, we need to read the contents in reversed order
        content = reversed(self.ribbon)
        # Display a little explanation
        intro = ('\nThe combinations of Monotype signals will be displayed '
                 'on screen while the machine casts the type.\n'
                 'Turn on the machine and the program will start.\n')
        self.UI.display(intro)
        # Start only after the machine is running
        self.caster.detect_rotation()
        # Read the reversed file contents, line by line, then parse
        # the lines, display comments & code combinations, and feed the
        # combinations to the caster
        for line in content:
        # Parse the row, return a list of signals and a comment.
        # Both can have zero or positive length.
            [rawSignals, comment] = parsing.comments_parser(line)
        # Parse the signals
            signals = parsing.signals_parser(rawSignals)
            # A string with information for user: signals, comments, etc.
            userInfo = ''
            if parsing.check_newline(signals):
            # Decrease the counter for each started new line
                currentLine -= 1
            # Percent of all lines done:
                linePercentDone = 100 * (linesAll - currentLine) / linesAll
            # Display number of the working line,
            # number of all remaining lines, percent done
                userInfo += ('Starting line: %i of %i, %i%% done...\n'
                             % (currentLine, linesAll, linePercentDone))
            elif parsing.check_character(signals):
            # Increase the current character and decrease characters left,
            # then do some calculations
                currentChar += 1
                charsLeft -= 1
            # % of chars to cast in the line
                charPercentDone = 100 * currentChar / charsAll
            # Display number of chars done,
            # number of all and remaining chars, % done
                userInfo += ('Casting character: %i / %i, '
                             '%i remaining, %i%% done...\n'
                             % (currentChar, charsAll,
                                charsLeft, charPercentDone))
        # Append signals to be cast
            userInfo += ' '.join(signals).ljust(15)
        # Add comment
            userInfo += comment
            # Display the info
            self.UI.display(userInfo)
        # Proceed with casting only if code is explicitly stated
        # (i.e. O15 = cast, empty list = don't cast)
            if signals:
                signals = parsing.strip_o_and_15(signals)
                # Cast the sequence
                try:
                    self.caster.process_signals(signals)
                except newexceptions.CastingAborted:
                # On failure - abort the whole job.
                # Check the aborted line so we can get back to it.
                    self.lineAborted = currentLine
                    self.UI.display('\nCasting aborted on line %i.'
                                    % self.lineAborted)
                    self.UI.hold_on_exit()
                    return False
        # After casting is finished, notify the user
        self.UI.display('\nCasting finished successfully!')
        self.UI.hold_on_exit()
        return True

    def punch_composition(self):
        """punch_composition():

        When punching, the input file is read forwards. An additional line
        (O+15) is switched on for operating the paper tower, if less than
        two signals are found in a sequence.

        We can't use automatic machine cycle detection like we do in
        cast_composition, because keyboard's paper tower doesn't run
        by itself - it must get air into tubes to operate, punches
        the perforations, and doesn't give any feedback.

        For punching, O+15 are needed if <2 lines are active.
        That's because of how the keyboard's paper tower is built -
        it has a balance mechanism that advances paper tape only if two
        signals can outweigh constant air pressure on the other side.
        Basically: less than two signals - no ribbon advance...
        """
        # Count a number of combinations punched in ribbon
        combinationsAll = parsing.count_combinations(self.ribbon)
        self.UI.display('Combinations in ribbon: %i', combinationsAll)
        # Wait until the operator confirms.
        intro = ('\nThe combinations of Monotype signals will be displayed '
                 'on screen while the paper tower punches the ribbon.\n')
        self.UI.display(intro)
        prompt = ('\nInput file found. Turn on the air, fit the tape '
                  'on your paper tower and press return to start punching.')
        self.UI.enter_data(prompt)
        for line in self.ribbon:
        # Parse the row, return a list of signals and a comment.
        # Both can have zero or positive length.
            [rawSignals, comment] = parsing.comments_parser(line)
        # Parse the signals
            signals = parsing.signals_parser(rawSignals)
        # A string with information for user: signals, comments, etc.
            userInfo = ''
        # Add signals to be cast
            if signals:
                userInfo += ' '.join(signals).ljust(20)
        # Add comment
            if comment:
                userInfo += comment
        # Display the info
            self.UI.display(userInfo)
        # Send the signals, adding O+15 whenever needed
            if signals:
            # Convert O or 15 to a combined O+15 signal:"""
                signals = parsing.convert_o15(signals)
                if len(signals) < 2:
                    signals.append('O15')
            # Punch it!"""
                self.caster.activate_valves(signals)
            # The pace is arbitrary, let's set it to 200ms/200ms
                time.sleep(0.2)
                self.caster.deactivate_valves()
                time.sleep(0.2)
        # After punching is finished, notify the user:"""
        self.UI.display('\nPunching finished!')
        self.UI.hold_on_exit()
        return True

    def line_test(self):
        """line_test():

        Tests all valves and composition caster's inputs to check
        if everything works and is properly connected. Signals will be tested
        in order: 0075 - S - 0005, 1 towards 14, A towards N, O+15.
        """
        intro = ('This will check if the valves, pin blocks and 0075, S, '
                 '0005 mechanisms are working. Press return to continue... ')
        self.UI.enter_data(intro)
        combinations = (['0075', 'S', '0005']
                        + [str(n) for n in range(1, 15)]
                        + [s for s in 'ABCDEFGHIJKLMNO'])
        # Send all the combinations to the caster, one by one.
        # Set _machine_stopped timeout at 120s.
        try:
            for code in combinations:
                self.UI.display(code)
                code = parsing.signals_parser(code)
                code = parsing.convert_o15(code)
                self.caster.process_signals(code, 120)
        except newexceptions.CastingAborted:
            return False
        else:
            self.UI.display('\nTesting finished!')
            self.UI.hold_on_exit()
            return True

    def cast_sorts(self):
        """cast_sorts():

        Sorts casting routine, based on the position in diecase.
        Ask user about the diecase row & column, as well as number of sorts.
        """
        while True:
        # Outer loop
            self.UI.clear()
            self.UI.display('Calibration and Sort Casting:\n\n')
            prompt = 'Enter column and row symbols (default: G 5): '
            signals = self.UI.enter_data(prompt)
            if not signals:
                signals = 'G 5'
            # Ask for number of sorts and lines
            prompt = '\nHow many sorts? (default: 10): '
            n = self.UI.enter_data(prompt)
            # Default to 10 if user enters non-positive number or letters
            if not n.isdigit() or int(n) < 0:
                n = 10
            else:
                n = int(n)
            prompt = '\nHow many lines? (default: 1): '
            lines = self.UI.enter_data(prompt)
            # Default to 10 if user enters non-positive number or letters
            if not lines.isdigit() or int(lines) < 0:
                lines = 1
            else:
                lines = int(lines)
            # Warn if we want to cast too many sorts from a single matrix
            warning = ('Warning: you want to cast a single character more than '
                       '10 times. This may lead to matrix overheating!\n')
            if n > 10:
                self.UI.display(warning)
            # After entering parameters, ask the operator if they're OK
            try:
                while True:
                # Inner loop
                # Menu subroutines
                    def cast_it():
                        """Cast the combination or go back to menu"""
                        if self.cast_from_matrix(signals, n, lines):
                            self.UI.display('Casting finished successfully.')
                        else:
                            raise newexceptions.ReturnToMenu
                    def different():
                        """Start the outer loop again - with new parameters"""
                        raise newexceptions.ChangeParameters
                    def return_to_menu():
                        """Throw an exception caught by the menu function"""
                        raise newexceptions.ReturnToMenu
                    def exit_program():
                        """Throw an exception caught by the menu function"""
                        raise newexceptions.ExitProgram
                    # End of menu subroutines.
                    options = {'C' : cast_it,
                               'D' : different,
                               'M' : return_to_menu,
                               'E' : exit_program}
                    message = ('Casting %s, %i lines of %i sorts.\n'
                               '[C]ast it, [D]ifferent code/quantity, '
                               '[M]enu or [E]xit? '
                               % (signals, lines, n))
                    choice = self.UI.simple_menu(message, options).upper()
                    # Execute choice
                    options[choice]()
            except newexceptions.ChangeParameters:
            # Skip the menu and casting altogether, repeat the outer loop
                pass

    def cast_from_matrix(self, signals, n=5, lines=1, pos0075=3, pos0005=8):
        """cast_from_matrix(combination, n, pos0075, pos0005):

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
        self.lineAborted = None
        # Convert the positions to strings
        pos0005 = str(pos0005)
        pos0075 = str(pos0075)
        # Signals for setting 0005 and 0075 justification wedges
        set0005 = ['N', 'J', '0005', pos0005]
        set0075 = ['N', 'K', '0075', pos0075]
        # Galley trip signal
        galleyTrip = ['N', 'K', 'J', '0005', '0075']
        # Parse the combination
        combination = parsing.signals_parser(signals)
        combination = parsing.strip_o_and_15(combination)
        # Check if the machine is running first, end here if not
        self.UI.display('Start the machine...')
        self.caster.detect_rotation()
        # We're here because the machine is rotating. Start casting the job...
        for currentLine in range(1, lines + 1):
        # Cast each line and if the CastingAborted exception is caught,
        # remember the last line and stop casting.
            try:
            # Cast the sorts: set wedges, turn pump on, cast, line out
            # Set up the justification, turn the pump on
                self.UI.display('Casting line %i of %i' % (currentLine, lines))
                self.UI.display('0005 wedge at ' + pos0005)
                self.caster.process_signals(set0005)
                self.UI.display('0075 wedge at ' + pos0075)
                self.UI.display('Starting the pump...')
                self.caster.process_signals(set0075)
            # Start casting characters
                self.UI.display('Casting characters...')
            # Cast n combinations of row & column, one by one
                for i in range(1, n+1):
                    info = ('%s - casting character %i of %i, %i%% done.'
                            % (' '.join(combination).ljust(20),
                               i, n, 100 * i / n))
                    self.UI.display(info)
                    parsing.strip_o_and_15(combination)
                    self.caster.process_signals(combination)
            # If everything went normally, put the line out to the galley
                self.UI.display('Putting line to the galley...')
                self.caster.process_signals(galleyTrip)
            # After casting sorts we need to stop the pump
                self.UI.display('Stopping the pump...')
                self.caster.process_signals(set0005)
            except newexceptions.CastingAborted:
                self.lineAborted = currentLine
                self.UI.display('Casting aborted on line %i'
                                % self.lineAborted)
                return False
        # We'll be here if casting ends successfully
        return True

    def send_combination(self):
        """send_combination():

        This function allows us to give the program a specific combination
        of Monotype codes, and will keep the valves on until we press return
        (useful for calibration). It also checks the signals' validity.
        """
        signals = ''
        while not signals:
            prompt = 'Enter the signals to send to the caster: '
            signals = self.UI.enter_data(prompt)
        # Parse the combination, get the signals (first item returned
        # by the parsing function)
            signals = parsing.signals_parser(signals)
        # Add O+15 signal if it was desired
            signals = parsing.convert_o15(signals)
        # Turn the valves on
        self.UI.display(' '.join(signals))
        self.caster.activate_valves(signals)
        # Wait until user decides to stop sending those signals to valves
        self.UI.enter_data('Press [Enter] to stop. ')
        self.caster.deactivate_valves()
        return True

    def align_wedges(self, spaceAt='G5'):
        """align_wedges(spaceAt='G5'):

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
        self.UI.display(intro)
        while True:
            # Subroutines for menu options
            def continue_aligning():
                pass
            def back_to_menu():
                raise newexceptions.ReturnToMenu
            def exit_program():
                raise newexceptions.ExitProgram
            # Finished. Return to menu.
            options = {'C' : continue_aligning,
                       'M' : back_to_menu,
                       'E' : exit_program}
            message = '\n[C]ontinue, [M]enu or [E]xit? '
            choice = self.UI.simple_menu(message, options).upper()
            # Execute choice
            options[choice]()
            #
            # Cast 10 spaces without correction.
            # End here if casting unsuccessful.
            self.UI.display('Now casting with a normal wedge only.')
            if not self.cast_from_matrix(spaceAt, 10):
                continue
            # Cast 10 spaces with the S-needle.
            # End here if casting unsuccessful.
            self.UI.display('Now casting with justification wedges...')
            if not self.cast_from_matrix(spaceAt + 'S', 10):
                continue
            # At the end of successful sequence, some info for the user:
            self.UI.display('Done. Compare the lengths and adjust if needed.')


    def main_menu(self):
        """main_menu:

        Calls self.UI.menu() with options, a header and a footer.
        Options: {option_name : description}
        Header: string displayed over menu
        Footer: string displayed under menu (all info will be added here).
        """
        # Declare subroutines for menu options
        def choose_ribbon_filename():
            """choose_ribbon_filename

            Asks the user for the ribbon filename.
            Checks if the file is readable, and pre-processes it.
            """
            self.ribbonFile = self.UI.enter_input_filename()
            self.ribbon = parsing.read_file(self.ribbonFile)
            # If file read failed, end here
            if not self.ribbon:
                self.UI.display('Error reading file!')
                time.sleep(1)
                return False
            # Read the metadata at the beginning of the ribbon file
            self.metadata = parsing.get_metadata(self.ribbon)
            try:
                self.diecase = self.metadata['diecase']
            except KeyError:
                pass
            # Reset the "line aborted" on a new casting job
            self.lineAborted = None
            return True

        def debug_notice():
            """debug_notice

            Prints a notice if the program is in debug mode.
            """
            if self.UI.debugMode:
                return '\n\nThe program is now in debugging mode!'
            else:
                return ''

        def additional_info():
            """additional_info:

            Displays additional info as a menu footer.
            Starts with an empty list, and checks whether the casting job
            objects has attributes that are parameters to be displayed.
            """
            info = []
            # Add ribbon filename, if any
            if self.ribbonFile:
                info.append('Input file name: ' + self.ribbonFile)
            # Add a caster name
            info.append('Using caster: ' + self.caster.name)
            # Add metadata for ribbon
            for parameter in self.metadata:
                value = str(self.metadata[parameter])
                info.append(str(parameter).capitalize() + ': ' + value)
            # Display the line last casting was aborted on, if applicable:
            if self.lineAborted:
                info.append('Last casting was aborted on line '
                            + str(self.lineAborted))
            # Convert it all to a multiline string
            return '\n'.join(info)

        def heatup():
            """heatup

            Allows to heat up the mould before casting, in order to
            stabilize the mould temperature (affects the type quality).
            Casts two lines of em-quads, which can be thrown back to the pot.
            """
            self.UI.clear()
            self.cast_from_matrix('O15', n=20, lines=2)

        def cast_or_punch():
            """cast_or_punch:

            Determines if the caster specified for the job is actually
            a perforator - if so, a "punch ribbon" feature will be
            available instead of "cast composition".
            """
            if self.caster.is_perforator:
                return ('Punch composition', self.punch_composition)
            else:
                return ('Cast composition', self.cast_composition)

        def preview_ribbon():
            """preview_ribbon:

            Determines if we have a ribbon file that can be previewed,
            and displays its contents line by line, or displays
            an error message.
            """
            self.UI.clear()
            self.UI.display('Ribbon preview:\n')
            self.UI.display('\n'.join([line for line in self.ribbon]))
            self.UI.enter_data('[Enter] to return to menu...')

        def exit_program():
            """exit_program:

            Throws an exception caught after the option is chosen."""
            raise newexceptions.ExitProgram

        # End of menu subroutines
        # Now construct the menu, starting with available options
        options = {1 : 'Load a ribbon file',
                   2 : 'Preview ribbon',
                   3 : cast_or_punch()[0],
                   4 : 'Cast sorts',
                   5 : 'Test the valves and pinblocks',
                   6 : 'Lock the caster on a specified diecase position',
                   7 : 'Calibrate the 52D space transfer wedge',
                   8 : 'Cast two lines of 20 quads to heat up the mould',
                   0 : 'Exit program'}
        # Commands: {option_name : function}
        commands = {1 : choose_ribbon_filename,
                    2 : preview_ribbon,
                    3 : cast_or_punch()[1],
                    4 : self.cast_sorts,
                    5 : self.line_test,
                    6 : self.send_combination,
                    7 : self.align_wedges,
                    8 : heatup,
                    0 : exit_program}
        h = ('rpi2caster - CAT (Computer-Aided Typecasting) '
             'for Monotype Composition or Type and Rule casters.'
             '\n\n'
             'This program reads a ribbon (input file) '
             'and casts the type on a composition caster.'
             + debug_notice() + '\n\nMain Menu:')
        # Keep displaying the menu and go back here after any method ends
        while True:
            choice = self.UI.menu(options, header=h, footer=additional_info())
            # Call the function and return to menu.
            try:
            # Catch "return to menu" and "exit program" exceptions here
                if choice in [0, 1, 2]:
                    commands[choice]()
                else:
                # Use the caster context for everything that needs it.
                # (casting, punching, testing routines)
                    with self.caster:
                        commands[choice]()
            except newexceptions.ReturnToMenu:
            # Will skip to the end of the loop, and start all over
                pass
            except newexceptions.ExitProgram:
            # Will exit program
                self.UI.exit_program()

    def __exit__(self, *args):
        self.UI.debug_info('Exiting casting job context.')


class Session(object):
    """Session:

    This is a top-level abstraction layer.
    Used for injecting dependencies for objects.
    """
    def __init__(self, job, caster, UI, db):
        # Set dependencies as object attributes.
        # Make sure we've got an UI first.
        try:
            assert (isinstance(UI, userinterfaces.TextUI)
                    or isinstance(UI, userinterfaces.WebInterface))
        except NameError:
            print 'Error: User interface not specified!'
            exit()
        except AssertionError:
            print 'Error: User interface of incorrect type!'
            exit()
        # Make sure database and config are of the correct type
        try:
            assert isinstance(db, database.Database)
        except NameError:
        # Not set up? Move on
            pass
        except AssertionError:
        # We can be sure that UI can handle this now
            UI.display('Invalid database!')
            UI.exit_program()
        # We need a job: casting, setup, typesetting...
        try:
        # Any job needs UI and database
            job.UI = UI
            job.db = db
        # UI needs job context
            UI.job = job
        except NameError:
            UI.display('Job not specified!')
        # Database needs UI to communicate messages to user
        db.UI = UI
        # Assure that we're using a caster or simulator for casting
        try:
            if isinstance(job, Casting):
                assert (isinstance(caster, monotype.Monotype)
                or isinstance(caster, simulation.Monotype))
        # Set up mutual dependencies
                job.caster = caster
                caster.UI = UI
                caster.job = job
        except (AssertionError, NameError, AttributeError):
            UI.display('You cannot do any casting without a proper caster!')
            UI.exit_program()
        # An __enter__ method of UI will call main_menu method in job
        with job:
            pass


# End of class definitions.
# And now, for something completely different...
# Initialize the console interface when running the program directly.
if __name__ == '__main__':
    caster = monotype.Monotype(name='mkart-cc')
    UI = userinterfaces.TextUI()
    db = database.Database()
    job = Casting()
    session = Session(job, caster, UI, db)
