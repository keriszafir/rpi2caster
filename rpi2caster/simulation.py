# -*- coding: utf-8 -*-
"""
simulation

A module which allows to simulate working with a Monotype composition caster,
and should be used for testing the higher-level casting routines
without an access to the actual caster.
"""
# Built-in time module
import time
# Custom exceptions module
from rpi2caster import exceptions
# Default user interface
from rpi2caster.global_settings import USER_INTERFACE as ui
# Constants shared between modules
from rpi2caster import constants


class Monotype(object):
    """Monotype (mockup)

    A class which allows to test rpi2caster without an actual interface
    or caster. Most functionality can be developped without an access
    to the physical machine.
    """

    def __init__(self, name='Monotype Simulator', is_perforator=False):
        self.name = name
        self.is_perforator = is_perforator
        self.manual_mode = False

    def __enter__(self):
        ui.debug_info('Entering caster/keyboard simulation context...')
        # Display some info
        ui.display('Using caster name:', self.name)
        ui.display('This is not an actual caster or interface. ')
        ui.confirm('Press [ENTER] to continue...')
        return self

    def process_signals(self, signals, cycle_timeout=5):
        """Simulates sending signals to the caster.

        Ask if user wants to simulate the machine stop.
        """
        while True:
            # Escape this only by returning True on success,
            # or raising exceptions.CastingAborted, exceptions.ExitProgram
            # (which will be handled by the methods of the Casting class)
            try:
                # Casting cycle
                # (sensor on - valves on - sensor off - valves off)
                self._send_signals_to_caster(signals, cycle_timeout)
            except exceptions.MachineStopped:
                # Machine stopped during casting - ask what to do
                self._stop_menu()
            else:
                # Successful ending - the combination has been cast
                return True

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
        # Ask whether to cast or simulate machine stop
        prompt = '[Enter] to cast or [S] to stop? '
        if self.manual_mode and ui.enter_data_or_blank(prompt) in ['s', 'S']:
            ui.display('Simulating machine stop...')
            raise exceptions.MachineStopped
        ui.display('Turning the valves on...')
        self.activate_valves(signals)
        ui.display('Turning the valves off...')
        self.deactivate_valves()
        ui.display('Sequence cast successfully.\n')
        return True

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
        pump_off = False
        stop_signal = ['N', 'J', '0005']
        ui.display('Stopping the pump...')
        while not pump_off:
            try:
                # Try stopping the pump until we succeed!
                # Keep calling _send_signals_to_caster until it returns True
                # (the machine receives and processes the pump stop signal)
                pump_off = self._send_signals_to_caster(stop_signal, 60)
            except exceptions.MachineStopped:
                # Loop over
                pass
        ui.display('Pump stopped. All valves off...')
        self.deactivate_valves()
        time.sleep(1)
        return True

    def activate_valves(self, signals):
        """If there are any signals, print them out"""
        if signals:
            message = ('Activating valves: ' + ' '.join(signals))
            ui.display(message)

    def deactivate_valves(self):
        """No need to do anything"""
        ui.display('Valves deactivated.')

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
        ui.debug_info('Exiting caster/keyboard simulation context.')
