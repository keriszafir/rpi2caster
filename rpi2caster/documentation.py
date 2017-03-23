# -*- coding: utf-8 -*-
"""User help messages for rpi2caster"""


casting_menu = (
    """This program lets you:

    -cast composition or punch paper ribbon
        The program asks you how many times you want to cast the job,
        how many lines to skip (for casting multi-line jobs),
        then casts type or punches ribbon, displaying information about
        current combination, progress, wedge positions and pump status.
        After the last run is finished, the program will pause and ask you
        whether you want to cast it once more. Otherwise, you return to menu.

        Sometimes the machine stops or you need to abort casting type;
        for an emergency stop, press Ctrl-C. The program will send signals
        to stop the pump (if it was working), and ask you whether you want
        to continue or abort. You can retry the last run; in this case,
        you can skip all lines cast successfully. Two lines will be cast
        to heat up the mould, so that the temperature is stable.

    -cast sorts from specified matrix coordinates, e.g. H2
        Enter a number of units to which the character will be cast.
        Enter a number of characters.
        The program will let you enter as many as you want. After you decide
        to cast the queue, the program asks for the desired line length
        (set the galley width accordingly), calculates the number of sorts
        to fits in a line. Characters are separated with spaces to prevent
        matrix overheating. The program will cast one or more lines,
        the remaining part of the line will be quadded out.

    -cast typecases from diecase for a given language
        This option is available after you choose a diecase.
        Choose a language

    -add, edit and delete diecases

    -do caster/interface diagnostics and calibration
    """)
