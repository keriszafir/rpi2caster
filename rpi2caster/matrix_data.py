# -*- coding: utf-8 -*-
"""matrix_data

Module containing functions for diecase retrieval and parsing,
diecase storing, parameter searches.
"""

from rpi2caster import text_ui as ui
from rpi2caster import exceptions
from rpi2caster import database
DB = database.Database()


def lookup_diecase(type_series, type_size):
    """lookup_diecase

    Searches for a diecase of given type series (e.g. 327) and size (e.g. 12),
    if several matches found - allows to choose one of them, returns data.
    """
    matches = DB.diecase_by_series_and_size(type_series, type_size)
    if not matches:
    # List is empty. Notify the user:
        ui.display('Sorry - no results found.')
        return False
    elif len(matches) == 1:
    # One result found
        return matches[0]
    else:
    # More than one match - decide which one to use:
        idents = [record[0] for record in matches]
    # Associate diecases with IDs to select one later
        assoc = dict(zip(idents, matches))
    # Display a menu with diecases from 1 to the last:
        options = dict([(i, k) for i, k in enumerate(matches, start=1)])
        header = 'Choose a diecase:'
        choice = ui.menu(options, header)
    # Choose one
        chosen_id = options[choice]
    # Return a list with chosen diecase's parameters:
        return assoc[chosen_id]
