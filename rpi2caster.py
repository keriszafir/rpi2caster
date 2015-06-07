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

# Imports
import text_ui
import casting
import monotype
import database
import simulation


class Session(object):
    """TextUI:

    Use this class for creating a text-based console user interface.
    A caster object must be created before instantiating this class.
    Suitable for controlling a caster from the local terminal or via SSH,
    supports UTF-8 too.
    """

    def __init__(self, ui, db, job, caster):
        """Instantiates job, caster, database classes to work with"""
        self.ui = ui
        self.job = job
        self.caster = caster
        self.database = db
        
        self.job.caster = self.caster
        self.job.db = self.database
        
        self.database.job = self.job

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


# End of class definitions.
# And now, for something completely different...
# Initialize the console interface when running the program directly.
if __name__ == '__main__':
    session = Session(caster=simulation.Monotype(),
                      job=casting.Casting(),
                      db=database.Database(),
                      ui=text_ui)
