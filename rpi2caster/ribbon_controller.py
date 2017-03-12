# -*- coding: utf-8 -*-
"""Typesetting context routines"""
from contextlib import suppress
from . import exceptions as e
from .models import Database, Ribbon
from .matrix_controller import DiecaseMixin
from .measure import Measure
from .ui import UIFactory, Abort

UI = UIFactory()
DB = Database()


class RibbonMixin(object):
    """Mixin for ribbon-related operations"""
    @property
    def ribbon(self):
        """Ribbon for the casting session"""
        return self.__dict__.get('_ribbon') or Ribbon()

    @ribbon.setter
    def ribbon(self, ribbon):
        """Ribbon setter"""
        self.__dict__['_ribbon'] = ribbon or Ribbon()

    @ribbon.setter
    def ribbon_file(self, ribbon_file):
        """Use a ribbon file"""
        self.ribbon.import_from_file(ribbon_file)

    @ribbon.setter
    def ribbon_id(self, ribbon_id):
        """Use a ribbon with a given ID"""
        self.ribbon.import_from_db(ribbon_id)

    def choose_ribbon(self):
        """Chooses a ribbon from database or file"""
        def from_db():
            """Choose a ribbon from database"""
            prompt = 'Number of a ribbon? (0 for a new one, blank to abort): '
            while True:
                try:
                    # Manual choice if function was called without arguments
                    data = list_ribbons()
                    choice = UI.enter(prompt, exception=Abort, datatype=int)
                    ribbon_id = data[choice]
                    # Inform the caller if import was successful or not
                    return self.import_from_db(ribbon_id)
                except KeyError:
                    UI.pause('Ribbon number is incorrect. Choose again.')
                except (e.DatabaseQueryError, e.NoMatchingData):
                    UI.display('WARNING: Cannot find any ribbon data!',
                               min_verbosity=1)
                    return False
                except Abort:
                    return False

        def from_file():
            """Choose a ribbon from file"""
            # Open the file manually if calling the method without arguments
            try:
                ribbon_file = UI.import_file()
                self.ribbon.import_from_file(ribbon_file)
            except Abort:
                return False
        self.ribbon.choose_from_db() or self.ribbon.import_from_file()

    def display_ribbon_contents(self):
        """Displays the ribbon's contents, line after line"""
        UI.display('Ribbon contents preview:\n')
        contents_generator = (line for line in self.ribbon.contents if line)
        try:
            while True:
                UI.display(contents_generator.__next__())
        except StopIteration:
            # End of generator
            UI.pause('Finished', UI.MSG_MENU)
        except (EOFError, KeyboardInterrupt):
            # Press ctrl-C to abort displaying long ribbons
            UI.pause('Aborted', UI.MSG_MENU)


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
        return self.__dict__.get('_measure') or Measure(self)

    @measure.setter
    def measure(self, measure):
        """Measure setter"""
        self.__dict__['_measure'] = measure

    @measure.setter
    def line_length(self, measure):
        """Set the line length for typesetting"""
        if measure:
            self.measure = Measure(self, measure)

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
        self.measure = Measure(self, manual_choice=True)

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
