# -*- coding: utf-8 -*-
"""Typesetting context routines"""
from contextlib import suppress
from collections import OrderedDict
from sqlalchemy.orm import exc as orm_exc
from .models import Database, Ribbon
from .matrix_controller import DiecaseMixin
from .measure import Measure
from .ui import UIFactory, Abort

UI = UIFactory()
DB = Database()


def get_all_ribbons():
    """Lists all ribbons we have."""
    ribbons = OrderedDict(enumerate(DB.query(Ribbon).all(), start=1))
    return ribbons


def list_ribbons(data=get_all_ribbons()):
    """Display all ribbons in a dictionary, plus an empty new one"""
    UI.display('\nAvailable ribbons:\n\n' +
               'No.'.ljust(4) +
               'Ribbon ID'.ljust(20) +
               'Diecase ID'.ljust(20) +
               'Wedge name'.ljust(12) +
               'Customer'.ljust(20) +
               'Description')
    for index, ribbon in data.items():
        row = ''.join([str(index).ljust(4),
                       ribbon.ribbon_id.ljust(20),
                       ribbon.diecase_id.ljust(20),
                       ribbon.wedge.name.ljust(12),
                       ribbon.customer.ljust(20),
                       ribbon.description])
        UI.display(row)


def ribbon_from_file():
    """Choose the ribbon from file"""
    ribbon = Ribbon()
    ribbon_file = UI.import_file()
    ribbon.import_from_file(ribbon_file)
    return ribbon


def choose_ribbon(fallback=Ribbon, fallback_description='new empty ribbon'):
    """Select ribbons from database and let the user choose one of them"""
    prompt = 'Number? (0: %s, leave blank to exit)' % fallback_description
    while True:
        try:
            data = get_all_ribbons()
            if not data:
                return fallback()
            else:
                UI.display('Choose a ribbon:', end='\n\n')
                list_ribbons(data)
                choice = UI.enter(prompt, exception=Abort, datatype=int)
                data[0] = None
                return data[choice] or fallback()
        except KeyError:
            UI.pause('Ribbon number is incorrect!')


def get_ribbon(ribbon_id=None, fallback=choose_ribbon):
    """Get a ribbon with given ribbon_id"""
    try:
        return DB.query(Ribbon).filter(Ribbon.ribbon_id == ribbon_id).one()
    except orm_exc.NoResultFound:
        return fallback()


class RibbonMixin(object):
    """Mixin for ribbon-related operations"""
    @property
    def ribbon(self):
        """Ribbon for the casting session"""
        ribbon = self.__dict__.get('_ribbon')
        if not ribbon:
            # instantiate a new one and cache it
            ribbon = Ribbon()
            self.__dict__['_ribbon'] = ribbon
        return ribbon

    @ribbon.setter
    def ribbon(self, ribbon):
        """Ribbon setter"""
        self.__dict__['_ribbon'] = ribbon or Ribbon()

    @ribbon.setter
    def ribbon_file(self, ribbon_file):
        """Use a ribbon file"""
        with suppress(Abort):
            new_ribbon = Ribbon()
            new_ribbon.import_from_file(ribbon_file)
            self.ribbon = new_ribbon

    @ribbon.setter
    def ribbon_id(self, ribbon_id):
        """Use a ribbon with a given ID, or an empty one"""
        with suppress(Abort):
            self.ribbon = get_ribbon(ribbon_id, fallback=self.ribbon)

    def choose_ribbon(self):
        """Chooses a ribbon from database or file"""
        with suppress(Abort):
            ribbon = choose_ribbon(fallback=ribbon_from_file,
                                   fallback_description='import from file')
            self.ribbon = ribbon

    def display_ribbon_contents(self):
        """Displays the ribbon's contents, line after line"""
        UI.display('Ribbon contents preview:\n')
        contents_generator = (line for line in self.ribbon.contents if line)
        try:
            while True:
                UI.display(contents_generator.__next__())
        except StopIteration:
            # End of generator
            UI.pause('\nFinished')
        except (EOFError, KeyboardInterrupt):
            # Press ctrl-C to abort displaying long ribbons
            UI.pause('\nAborted')


class SourceMixin(object):
    """Mixin for source text"""
    @property
    def source(self):
        """Source text for typesetting"""
        return self.__dict__.get('_source') or ''

    @source.setter
    def source(self, text):
        """Source setter"""
        self.__dict__['_source'] = text

    @source.setter
    def input_text(self, text):
        """Set a string of text as the typesetting source"""
        if text:
            self.source = text

    @source.setter
    def text_file(self, text_file):
        """Use a file object as a source of text"""
        # If a string or None is passed as an argument,
        # AttributeError would be raised. We'd rather ignore it.
        with suppress(AttributeError), text_file:
            self.source = ''.join(text_file.readlines())

    def edit_text(self):
        """Edits the input text"""
        self.source = UI.edit(self.source)


class TypesettingContext(SourceMixin, DiecaseMixin, RibbonMixin):
    """Mixin for setting diecase, wedge and measure"""
    @property
    def measure(self):
        """Typesetting measure i.e. line length"""
        return self.__dict__.get('_measure') or Measure(context=self)

    @measure.setter
    def measure(self, measure):
        """Measure setter"""
        self.__dict__['_measure'] = measure

    @measure.setter
    def line_length(self, measure):
        """Set the line length for typesetting"""
        if measure:
            self.measure = Measure(measure, context=self)

    @property
    def manual_mode(self):
        """Decides whether to use an automatic or manual typesetting engine."""
        # On by default
        return self.__dict__.get('_manual_mode') or False

    @manual_mode.setter
    def manual_mode(self, manual_mode):
        """Manual mode setter"""
        self.__dict__['_manual_mode'] = True if manual_mode else False

    @property
    def default_alignment(self):
        """Default alignment:
        Determines how paragraphs ending with a double newline ("\n\n")
        and the end of the source text will be aligned.
        Valid options: "left", "right", "center", "both".
        """
        return self.__dict__.get('_default_alignment') or 'left'

    @default_alignment.setter
    def default_alignment(self, alignment):
        """Default alignment setter"""
        options = {'cr': 'left', 'cc': 'center', 'cl': 'right', 'cf': 'both',
                   'left': 'left', 'center': 'center', 'right': 'right',
                   'flat': 'both', 'both': 'both', 'f': 'both',
                   'l': 'left', 'c': 'center', 'r': 'right', 'b': 'both'}
        string = alignment.strip().replace('^', '').lower()
        value = options.get(string)
        if value:
            self.__dict__['_default_alignment'] = value

    def change_measure(self):
        """Change a line length"""
        UI.display('Set the galley width...')
        self.measure = Measure(manual_choice=True, context=self)

    def change_alignment(self):
        """Changes the default text alignment"""
        UI.display('Default alignment for paragraphs:')
        message = 'Choose alignment: [L]eft, [C]enter, [R]ight, [B]oth? '
        options = {'l': 'left', 'r': 'right', 'c': 'center', 'b': 'both'}
        self.default_alignment = UI.simple_menu(message, options)

    def toggle_manual_mode(self):
        """Changes the manual/automatic typesetting mode"""
        self.manual_mode = not self.manual_mode


def list_ribbons():
    """Lists all ribbons in the database."""
    data = DB.get_all_ribbons()
    results = {}
    UI.display('\n' +
               'No.'.ljust(5) +
               'Ribbon name'.ljust(30) +
               'Description'.ljust(30) +
               'Customer'.ljust(30) +
               'Diecase'.ljust(30) +
               'Wedge'.ljust(30) +
               '\n\n0 - start a new empty ribbon\n')
    for index, ribbon in enumerate(data, start=1):
        # Collect ribbon parameters
        row = [str(index).ljust(5)]
        # Add ribbon name, description, diecase ID
        row.extend([field.ljust(30) for field in ribbon[:-1]])
        # Display it all
        UI.display(''.join(row))
        # Add number and ID to the result that will be returned
        results[index] = ribbon[0]
    UI.display('\n\n')
    # Now we can return the number - ribbon ID pairs
    return results
