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


class Session(object):
    """TextUI:

    Use this class for creating a text-based console user interface.
    A caster object must be created before instantiating this class.
    Suitable for controlling a caster from the local terminal or via SSH,
    supports UTF-8 too.
    """

    def __init__(self, ui='text_ui', job='casting', caster='monotype'):
        self.ui = __import__(ui)
        self.job = __import__(job)
        self.caster = __import__(caster)

    def __enter__(self):
        """Try to call main menu for a job.

        Display a message when user presses ctrl-C.
        """
        # Print some debug info
        self.ui.debug_info('Entering text UI context...')
        try:
            self.job.main_menu()
        except KeyboardInterrupt:
            print '\nUser pressed ctrl-C. Exiting.'
        finally:
            print '\nGoodbye!\n'

    def __exit__(self, *args):
        self.ui.debug_info('Exiting text UI context.')


class Deprecated(object):
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
    session = Session(caster='simulation')
