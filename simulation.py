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
import newexceptions

class Monotype(object):
    """Monotype (mockup)

    A class which allows to test rpi2caster without an actual interface
    or caster. Most functionality can be developped without an access
    to the physical machine.
    """

    def __init__(self, name='Monotype Simulator', is_perforator=False):
        self.UI = None
        self.name = name
        self.is_perforator = is_perforator

    def __enter__(self):
        self.UI.debug_info('Entering caster/keyboard simulation context...')
        # Display some info
        self.UI.display('Using caster name:', self.name)
        self.UI.display('This is not an actual caster or interface. ')
        self.UI.enter_data('Press [ENTER] to continue...')
        # Debugging is ON by default
        self.UI.debugMode = True
        return self

    def process_signals(self, signals, machine_timeout=5):
        """Simulates sending signals to the caster.

        Ask if user wants to simulate the machine stop.
        """
        def send_signals_to_caster(signals, timeout):
            """send_signals_to_caster

            Mocku of a real-world sending signals to the interface.
            We don't have a machine cycle sensor nor valves here,
            so we have to simulate their action by user's input.
            This function allows to decide whether the caster is turning
            or stopped, and then allows to make decision to continue casting,
            abort or exit program.
            """
            timeout = timeout
            prompt = '[Enter] to cast or [S] to stop? '
            if self.UI.enter_data(prompt) in ['s', 'S']:
                self.UI.display('Simulating machine stop...')
                return False
            self.UI.display('Turning the valves on...')
            self.activate_valves(signals)
            self.UI.display('Turning the valves off...')
            self.deactivate_valves()
            self.UI.display('Sequence cast successfully.')
            return True

        def continue_after_machine_stopped():
            """continue_after_machine_stopped:

            This allows us to choose whether we want to continue,
            return to menu or exit if the machine is stopped during casting.
            """
            def continue_casting():
                """Helper function - continue casting."""
                return True

            def return_to_menu():
                """return_to_menu

                Aborts casting. Makes sure the pump is turned off.
                Raise an exception to be caught by higher-level functions
                from the Casting class
                """
                emergency_cleanup()
                raise newexceptions.CastingAborted

            def exit_program():
                """exit_program

                Helper function - throws an exception to exit the program.
                Also makes sure the pump is turned off."""
                emergency_cleanup()
                raise newexceptions.ExitProgram

            # End of subroutine definitions
            # Now, a little menu
            options = {'C' : continue_casting,
                       'M' : return_to_menu,
                       'E' : exit_program}
            message = ('Machine has stopped running! Check what happened.\n'
                       '[C]ontinue, return to [M]enu or [E]xit program? ')
            choice = self.UI.simple_menu(message, options).upper()
            return options[choice]()

        def emergency_cleanup():
            """emergency_cleanup:

            If the machine is stopped, we need to turn the pump off and then
            turn all the lines off. Otherwise, the machine will keep pumping
            while it shouldnot (e.g. after a splash).

            The program will hold execution until the operator clears the
            situation, it needs turning the machine at least one full
            revolution. The program MUST turn the pump off to go on.
            """
            pump_off = False
            stop_signal = ['N', 'J', '0005']
            self.UI.display('Stopping the pump...')
            while not pump_off:
            # Try stopping the pump until we succeed!
            # Keep calling process_signals until it returns True
            # (the machine receives and processes the pump stop signal)
                pump_off = send_signals_to_caster(stop_signal, machine_timeout)
            else:
                self.UI.display('Pump stopped. All valves off...')
                self.deactivate_valves()
                time.sleep(1)
                return True
        # End of subroutine definitions
        while not send_signals_to_caster(signals, 30):
            # Keep trying to cast the combination, or end here
            # (subroutine will throw an exception if operator exits)
            continue_after_machine_stopped()
        else:
            # Successful ending - the combination has been cast
            return True

    def activate_valves(self, signals):
        """If there are any signals, print them out"""
        if len(signals) != 0:
            message = ('Activating valves: ' + ' '.join(signals))
            self.UI.display(message)

    def deactivate_valves(self):
        """No need to do anything"""
        self.UI.display('Valves deactivated.')

    def detect_rotation(self):
        """Detect rotation:

        Ask if the machine is rotating or not (for testing
        the machine not running scenario).
        """
        # Subroutine definition
        def start_the_machine():
            """start_the_machine

            Allows user to decide what to do if the machine is not rotating.
            Continue, abort or exit program.
            """
            def continue_casting():
                """Helper function - continue casting."""
                return True
            def return_to_menu():
                """Raise an exception to return to main menu"""
                raise newexceptions.ReturnToMenu
            def exit_program():
                """Raise an exception to exit program"""
                raise newexceptions.ExitProgram
            options = {'C' : continue_casting,
                       'M' : return_to_menu,
                       'E' : exit_program}
            message = ('Machine not running - you need to start it first.\n'
                       '[C]ontinue, return to [M]enu or [E]xit program? ')
            choice = self.UI.simple_menu(message, options).upper()
            return options[choice]()
        prompt = 'Is the machine running? [Enter] - yes, [N] - no: '
        if self.UI.enter_data(prompt) not in ['n', 'N']:
        # Machine is running
            return True
        elif start_the_machine():
        # Check again recursively:
            return self.detect_rotation()
        else:
        # This will lead to return to menu
            return False

    def __exit__(self, *args):
        self.deactivate_valves()
        self.UI.debug_info('Exiting caster/keyboard simulation context.')
