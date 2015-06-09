#!/usr/bin/python
# -*- coding: utf-8 -*-
"""rpi2caster

Session management for the rpi2caster package
TODO: get this thing to set up objects dynamically
(i.e. changing a caster etc.)
"""
from __future__ import absolute_import
from rpi2caster import text_ui as UI


def set_ui(dependencies, userinterface=UI):
    """Sets the user interface for dependencies"""
    for module in dependencies:
        module.ui = userinterface
    return userinterface


class Session(object):
    """TextUI:

    Use this class for creating a text-based console user interface.
    A caster object must be created before instantiating this class.
    Suitable for controlling a caster from the local terminal or via SSH,
    supports UTF-8 too.
    """

    def __init__(self, db, job, caster):
        """Instantiates job, caster, database classes to work with"""
        self.job = job
        self.caster = caster
        self.database = db

        self.job.caster = self.caster
        self.job.db = self.database

    def __enter__(self):
        """Try to call main menu for a job.

        Display a message when user presses ctrl-C.
        """
        # Print some debug info
        UI.debug_info('Entering text UI context...')
        try:
            self.job.main_menu()
        except KeyboardInterrupt:
            print '\nUser pressed ctrl-C. Exiting.'
        finally:
            print '\nGoodbye!\n'

    def __exit__(self, *args):
        UI.debug_info('Exiting text UI context.')


# End of class definitions.
# And now, for something completely different...
# Initialize the console interface when running the program directly.
if __name__ == '__main__':
    # Imports
    import monotype
    import database
    import casting
    DEP = [monotype, database, casting]
    UI = set_ui(DEP, UI)
    with Session(caster=monotype.Monotype('mkart-cc'),
                 job=casting.Casting(),
                 db=database.Database()) as session:
        pass
