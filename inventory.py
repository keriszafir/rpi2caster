#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Inventory:

Allows to add, list and delete wedges and diecases.
"""
import text_ui as ui

import database
db = database.Database()

import newexceptions


# Placeholders for functionality not implemented yet:
def list_diecases():
    pass
def show_diecase_layout():
    pass
def add_diecase():
    pass
def edit_diecase():
    pass
def clear_diecase():
    pass
def delete_diecase():
    pass

def add_wedge(wedge_name='', set_width='', brit_pica=None, steps=''):
    """add_wedge(wedge_name, set_width, brit_pica, steps)

    Used for adding wedges.

    Can be called with or without arguments.

    wedge_name - string - series name for a wedge (e.g. S5, S111)
    set_width  - float - set width of a particular wedge (e.g. 9.75)
    brit_pica - boolean - whether the wedge is based on British pica
    (0.1667") or not (American pica - 0.1660")
    True if the wedge is for European market ("E" after set width number)
    steps - string with unit values for steps - e.g. '5,6,7,8,9,9,9...,16'

    Start with defining the unit arrangements for some known wedges.
    This data will be useful when adding a wedge. The setup program
    will look up a wedge by its name, then get unit values.

    The MONOSPACE wedge is a special wedge, where all steps have
    the same unit value of 9. It is used for casting constant-width
    (monospace) type, like the typewriters have. You could even cast
    from regular matrices, provided that you use 0005 and 0075 wedges
    to add so many units that you can cast wide characters
    like "M", "W" etc. without overhang. You'll get lots of spacing
    between narrower characters, because they'll be cast on a body
    wider than necessary.

    In this program, all wedges have the "S" (for stopbar) letter
    at the beginning of their designation. However, the user can enter
    a designation with or without "S", so check if it's there, and
    append if needed (only for numeric designations - not the "monospace"
    or other text values!)

    If no name is given, assume that the user means the S5 wedge, which is
    very common and most casting workshops have a few of them.
    """
    wedge_data = {'S5'     : '5,6,7,8,9,9,9,10,10,11,12,13,14,15,18,18',
                  'S96'    : '5,6,7,8,9,9,10,10,11,12,13,14,15,16,18,18',
                  'S111' : '5,6,7,8,8,8,9,9,9,9,10,12,12,13,15,15',
                  'S334' : '5,6,7,8,9,9,10,10,11,11,13,14,15,16,18,18',
                  'S344' : '5,6,7,9,9,9,10,11,11,12,12,13,14,15,16,16',
                  'S377' : '5,6,7,8,8,9,9,10,10,11,12,13,14,15,18,18',
                  'S409' : '5,6,7,8,8,9,9,10,10,11,12,13,14,15,16,16',
                  'S467' : '5,6,7,8,8,9,9,9,10,11,12,13,14,15,18,18',
                  'S486' : '5,7,6,8,9,11,10,10,13,12,14,15,15,18,16,16',
                  'S526' : '5,6,7,8,9,9,10,10,11,12,13,14,15,17,18,18',
                  'S536' : '5,6,7,8,9,9,10,10,11,12,13,14,15,17,18,18',
                  'S562' : '5,6,7,8,9,9,9,10,11,12,13,14,15,17,18,18',
                  'S607' : '5,6,7,8,9,9,9,9,10,11,12,13,14,15,18,18',
                  'S611' : '6,6,7,9,9,10,11,11,12,12,13,14,15,16,18,18',
                  'S674' : '5,6,7,8,8,9,9,9,10,10,11,12,13,14,15,18',
                  'S724' : '5,6,7,8,8,9,9,10,10,11,13,14,15,16,18,18',
                  'S990' : '5,5,6,7,8,9,9,9,9,10,10,11,13,14,18,18',
                  'S1063': '5,6,8,9,9,9,9,10,12,12,13,14,15,15,18,18',
                  'S1329': '4,5,7,8,9,9,9,9,10,10,11,12,12,13,15,15',
                  'S1331': '4,5,7,8,8,9,9,9,9,10,11,12,12,13,15,15',
                  'S1406': '4,5,6,7,8,8,9,9,9,9,10,10,11,12,13,15',
                  'MONOSPACE' : '9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9'}
    # Enter the wedge name:
    while not wedge_name:
        wedge_name = ui.enter_data('Enter the wedge name, e.g. S5 '
                                   '(very typical, default): ')
        if not wedge_name:
            wedge_name = 'S5'
        elif wedge_name[0].upper() is not 'S' and wedge_name.isdigit():
            wedge_name = 'S' + wedge_name
        wedge_name = wedge_name.upper()
    # Enter the set width:
    while not set_width:
        prompt = 'Enter the wedge set width as decimal, e.g. 9.75E: '
        set_width = ui.enter_data(prompt)
    # Determine if it's a British pica wedge automatically - E is present:
    if set_width[-1].upper() == 'E':
        set_width = set_width[:-1]
        brit_pica = True
    elif brit_pica is None:
    # Otherwise, let user choose if it's American or British pica:
        options = {'A' : False, 'B' : True}
        message = '[A]merican (0.1660"), or [B]ritish (0.1667") pica? '
        choice = ui.simple_menu(message, options).upper()
        brit_pica = options[choice]
    try:
        set_width = float(set_width)
    except ValueError:
        set_width = 12
    # Enter the wedge unit arrangement for steps 1...15 (optionally 16):
    while not steps:
    # Check if we have the values hardcoded already:
        try:
            steps = wedge_data[wedge_name]
        except (KeyError, ValueError):
        # No wedge - enter data manually:
            prompt = ('Enter the wedge unit values for steps 1...16, '
                      'separated by commas. If empty, entering values '
                      'for wedge S5 (very common): ')
            steps = ui.enter_data(prompt)
            if not steps:
                steps = wedge_data['S5']
        steps = steps.split(',')
    # Now we need to be sure that all whitespace is stripped,
    # and the value written to database is a list of integers
        steps = [int(step.strip()) for step in steps]
    # Display warning if the number of steps is anything other than
    # 15 or 16 (15 is most common, 16 was used for HMN and KMN systems).
    # If length is correct, tell user it's OK.
        warn_min = ('Warning: the wedge you entered has less than 15 steps!'
                    '\nThis is almost certainly a mistake.\n')
        warn_max = ('Warning: the wedge you entered has more than 16 steps!'
                    '\nThis is almost certainly a mistake.\n')
        steps_ok = ('The wedge has ', len(steps), 'steps. That is OK.')
        if len(steps) < 15:
            ui.display(warn_min)
        elif len(steps) > 16:
            ui.display(warn_max)
        else:
            ui.display(steps_ok)
    # Display a summary:
    summary = {'Wedge' : wedge_name,
               'Set width' : set_width,
               'British pica wedge?' : brit_pica}
    for parameter in summary:
        ui.display(parameter, ':', summary[parameter])
    # Loop over all unit values in wedge's steps and display them:
    for i, step in zip(range(len(steps)), steps):
        ui.display('Step', i+1, 'unit value:', step, '\n')
    # Subroutines:
    def commit_wedge():
        if db.add_wedge(wedge_name, set_width, brit_pica, steps):
            ui.display('Wedge added successfully.')
        else:
            ui.display('Failed to add wedge!')
    def reenter():
        ui.enter_data('Enter parameters again from scratch... ')
        # TODO: ugly hack, get rid of it, use a "while" loop
        add_wedge()
    def return_to_menu():
        raise newexceptions.ReturnToMenu
    # Confirmation menu:
    message = ('\nCommit wedge to database? \n'
               '[Y]es / [N]o (enter values again) / return to [M]enu: ')
    options = {'Y' : commit_wedge, 'N' : reenter, 'M' : return_to_menu}
    ans = ui.simple_menu(message, options).upper()
    options[ans]()

def delete_wedge():
    """Used for deleting a wedge from database.
    """
    list_wedges()
    ID = ui.enter_data('Enter the wedge ID to delete: ')
    if ID.isdigit():
        ID = int(ID)
        if db.delete_wedge(ID):
            ui.display('Wedge deleted successfully.')
    else:
        ui.display('Wedge ID must be a number!')

def list_wedges():
    """lists all wedges we have
    """
    db.list_wedges()

def main_menu():
    def exit_program():
        """Helper subroutine, throws an exception to exit the program"""
        raise newexceptions.ExitProgram
    options = {1 : 'List matrix cases',
               2 : 'Show matrix case layout',
               3 : 'Add a new, empty matrix case',
               4 : 'Edit matrix case layout',
               5 : 'Clear matrix case layout',
               6 : 'Delete matrix case',
               7 : 'List wedges',
               8 : 'Add wedge',
               9 : 'Delete wedge',
               0 : 'Exit program'}
    commands = {1 : list_diecases,
                2 : show_diecase_layout,
                3 : add_diecase,
                4 : edit_diecase,
                5 : clear_diecase,
                6 : delete_diecase,
                7 : list_wedges,
                8 : add_wedge,
                9 : delete_wedge,
                0 : exit_program}
    while True:
        h = 'Setup utility for rpi2caster CAT.\nMain menu:'
        choice = ui.menu(options, header=h, footer='')
        try:
            # Execute it!
            with db:
                commands[choice]()
            ui.hold_on_exit()
        except newexceptions.ReturnToMenu:
            pass
        except newexceptions.ExitProgram:
            ui.exit_program()


# Initialize the console interface when running the program directly.
if __name__ == '__main__':
    main_menu()
