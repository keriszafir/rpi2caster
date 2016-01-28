# -*- coding: utf-8 -*-
"""caster_driver - abstract base classes for caster drivers"""
# Built-in time module
import time
# Custom exceptions module
from rpi2caster import exceptions
# Default user interface
from rpi2caster.global_settings import USER_INTERFACE as ui


class Caster(object):
    """Methods common for Caster classes, used for instantiating
    caster driver objects (whether real hardware or mockup for simulation)."""
    def __init__(self):
        self.name = 'Mockup caster for testing'
        self.is_perforator = False
        # Manual mode needs confirmation before casting each combination
        self.manual_mode = False
        self.lock = False
        # Attach a pump
        self.pump = Pump()
        # Set default wedge positions
        self.current_0005 = '15'
        self.current_0075 = '15'

    def __enter__(self):
        """Lock the resource so that only one object can use it
        with context manager"""
        ui.debug_info('Entering caster/interface context...')
        if self.lock:
            ui.display('Caster %s is already busy!' % self.name)
        else:
            # Set default wedge positions
            self.current_0005 = '15'
            self.current_0075 = '15'
            self.lock = True
            return self

    def process_signals(self, signals, cycle_timeout=5):
        """process_signals(signals, cycle_timeout):

        Checks for the machine's rotation, sends the signals (activates
        solenoid valves) after the caster is in the "air bar down" position.

        If no machine rotation is detected (sensor input doesn't change
        its state) during cycle_timeout, calls a function to ask user
        what to do (can be useful for resuming casting after manually
        stopping the machine for a short time - not recommended as the
        mould cools down and type quality can deteriorate).

        If the operator decides to go on with casting, the aborted sequence
        will be re-cast so as to avoid missing characters in the composition.

        Safety measure: this function will call "emergency_cleanup" routine
        whenever the operator decides to go back to menu or exit program
        after the machine stops rotating during casting. This is to ensure
        that the pump will not stay on afterwards, leading to lead squirts
        or any other unwanted effects.

        When casting, the pace is dictated by the caster and its RPM. Thus,
        we can't arbitrarily set the intervals between valve ON and OFF
        signals. We need to get feedback from the machine, and we can use
        contact switch (unreliable in the long run), magnet & reed switch
        (not precise enough) or a photocell sensor + LED (very precise).
        We can use a paper tower's operating lever for obscuring the sensor
        (like John Cornelisse did), or we can use a partially obscured disc
        attached to the caster's shaft (like Bill Welliver did).
        Both ways are comparable; the former can be integrated with the
        valve block assembly, and the latter allows for very precise tweaking
        of duty cycle (bright/dark area ratio) and phase shift (disc's position
        relative to 0 degrees caster position).
        """
        while True:
            # Escape this only by returning True on success,
            # or raising exceptions.CastingAborted, exceptions.ExitProgram
            # (which will be handled by the methods of the Casting class)
            try:
                # Casting cycle
                # (sensor on - valves on - sensor off - valves off)
                self._send_signals_to_caster(signals, cycle_timeout)
                # Successful ending - the combination has been cast
                return True
            except exceptions.MachineStopped:
                # Machine stopped during casting - ask what to do
                self._stop_menu()

    def _send_signals_to_caster(self, signals, cycle_timeout):
        """send_signals_to_caster

        Mocku of a real-world sending signals to the interface.
        We don't have a machine cycle sensor nor valves here,
        so we have to simulate their action by user's input.
        This function allows to decide whether the caster is turning
        or stopped, and then allows to make decision to continue casting,
        abort or exit program.
        """
        cycle_timeout = cycle_timeout
        try:
            # Ask whether to cast or simulate machine stop
            prompt = ('[Enter] to cast, [S] to stop '
                      'or [A] to switch to automatic mode? ')
            answer = self.manual_mode and ui.enter_data_or_blank(prompt)
            if answer in ['s', 'S']:
                ui.display('Simulating machine stop...')
                raise exceptions.MachineStopped
            elif answer in ['a', 'A']:
                ui.display('Running in automatic mode from now on...')
                self.manual_mode = False
            ui.display('Turning the valves on...')
            self.activate_valves(signals)
            ui.display('Turning the valves off...')
            self.deactivate_valves()
            ui.display('Sequence cast successfully.\n')
            return True
        except (KeyboardInterrupt, EOFError):
            # Let user decide if they want to continue / go to menu / exit
            self._stop_menu()

    def _stop_menu(self, casting=True):
        """_stop_menu:

        This allows us to choose whether we want to continue,
        return to menu or exit if the machine is stopped during casting.
        """
        def continue_casting():
            """Helper function - continue casting."""
            return True

        def with_cleanup_return_to_menu():
            """with_cleanup_return_to_menu

            Aborts casting. Makes sure the pump is turned off.
            Raise an exception to be caught by higher-level functions
            from the Casting class
            """
            self._emergency_cleanup()
            raise exceptions.CastingAborted

        def with_cleanup_exit_program():
            """with_cleanup_exit_program

            Helper function - throws an exception to exit the program.
            Also makes sure the pump is turned off."""
            self._emergency_cleanup()
            raise exceptions.ExitProgram

        # End of subroutine definitions
        # Now, a little menu...
        if casting:
            # This happens when the caster is already casting,
            # and stops running.
            self.deactivate_valves()
            options = {'C': continue_casting,
                       'M': with_cleanup_return_to_menu,
                       'E': with_cleanup_exit_program}
            message = ('Machine has stopped running! Check what happened.\n'
                       '[C]ontinue, return to [M]enu or [E]xit program? ')
        else:
            # This happens if the caster is not yet casting
            # No need to do cleanup; change description a bit
            options = {'C': continue_casting,
                       'M': exceptions.return_to_menu,
                       'E': exceptions.exit_program}
            message = ('Machine not running - you need to start it first.\n'
                       '[C]ontinue, return to [M]enu or [E]xit program? ')
        ui.simple_menu(message, options)()

    def _emergency_cleanup(self):
        """_emergency_cleanup:

        If the machine is stopped, we need to turn the pump off and then
        turn all the lines off. Otherwise, the machine will keep pumping
        while it shouldnot (e.g. after a splash).

        The program will hold execution until the operator clears the
        situation, it needs turning the machine at least one full
        revolution. The program MUST turn the pump off to go on.
        """
        stop_signal = ['N', 'J', '0005']
        while self.pump.working:
            try:
                # Try stopping the pump until we succeed!
                # Keep calling _send_signals_to_caster until it returns True
                # (the machine receives and processes the pump stop signal)
                ui.display('Stopping the pump...')
                self._send_signals_to_caster(stop_signal, 60)
            except exceptions.MachineStopped:
                # Loop over
                pass
        ui.display('Pump is off. All valves off, just in case...')
        self.deactivate_valves()
        time.sleep(1)
        return True

    def activate_valves(self, signals):
        """If there are any signals, print them out"""
        if signals:
            self.pump.check_working(signals)
            self.get_wedge_positions(signals)
            message = ('Activating valves: ' + ' '.join(signals))
            ui.display(message)

    def deactivate_valves(self):
        """No need to do anything"""
        ui.display('Valves deactivated.')

    def get_wedge_positions(self, signals):
        """Gets current positions of 0005 and 0075 wedges"""
        # Check 0005
        if '0005' in signals or {'N', 'J'}.issubset(signals):
            pos_0005 = [x for x in range(15) if str(x) in signals]
            if pos_0005:
                # One or more signals detected
                self.current_0005 = str(min(pos_0005))
            else:
                # 0005 with no signal = wedge at 15
                self.current_0005 = '15'
        # Check 0075
        if '0075' in signals or {'N', 'K'}.issubset(signals):
            pos_0075 = [x for x in range(15) if str(x) in signals]
            if pos_0075:
                # One or more signals detected
                self.current_0075 = str(min(pos_0075))
            else:
                # 0005 with no signal = wedge at 15
                self.current_0075 = '15'

    def detect_rotation(self):
        """Detect rotation:

        Ask if the machine is rotating or not (for testing
        the machine not running scenario).
        Also ask whether user wants to confirm each sequence.
        """
        question = 'Manual mode (you need to confirm each sequence)?'
        self.manual_mode = ui.yes_or_no(question)
        while True:
            prompt = 'Is the machine running? [Enter] - yes, [N] - no: '
            if ui.enter_data_or_blank(prompt) not in ['n', 'N']:
                # The machine is turning
                return True
            # Simulate machine stop
            self._stop_menu(casting=False)
            # Start over and check again (unless an exception occurred)

    def __exit__(self, *args):
        self.deactivate_valves()
        ui.debug_info('Caster no longer in use.')
        self.lock = False


class Pump(object):
    """Pump class for storing the pump working/non-working status."""
    def __init__(self):
        self.is_working = False

    def check_working(self, signals):
        """Checks if pump is working based on signals in sequence"""
        # 0075 / NK is satisfactory to turn the pump on...
        if '0075' in signals or set(['N', 'K']).issubset(signals):
            self.is_working = True
        # No 0075 / NK; then 0005 / NJ turns the pump off
        elif '0005' in signals or set(['N', 'J']).issubset(signals):
            self.is_working = False

    def status(self):
        """Displays info whether pump is working or not"""
        if self.is_working:
            return('Pump is ON')
        else:
            return('Pump is OFF')
