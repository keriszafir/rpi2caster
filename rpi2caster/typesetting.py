# -*- coding: utf-8 -*-
"""Typesetter program"""

from collections import OrderedDict
from contextlib import suppress
from sqlalchemy.orm import exc as orm_exc
from . import basic_models as bm, basic_controllers as bc, definitions as d
from .config import CFG
from .main_models import DB, Ribbon
from .matrix_controller import DiecaseMixin
from .parsing import token_parser
from .ui import UI, Abort, option as opt

PREFS_CFG = CFG.preferences


# Ribbon control routines

def get_all_ribbons():
    """Lists all ribbons we have."""
    rows = DB.session.query(Ribbon).all()
    ribbons = OrderedDict(enumerate(rows, start=1))
    return ribbons


def list_ribbons(data=get_all_ribbons()):
    """Display all ribbons in a dictionary, plus an empty new one"""
    UI.display('\nAvailable ribbons:\n')
    template = ('|{no:<5}  {ribbon_id:<20} {diecase_id:<20} '
                '{wedge:<12} {customer:<20} {desc:<50}|')
    fields = dict(no='No.', ribbon_id='Ribbon ID', diecase_id='Diecase ID',
                  wedge='Wedge name', customer='Customer', desc='Description')
    UI.display_header(template.format(**fields))
    for index, ribbon in data.items():
        values = dict(no=index, desc=ribbon.description,
                      ribbon_id=ribbon.ribbon_id, diecase_id=ribbon.diecase_id,
                      wedge=ribbon.wedge.name, customer=ribbon.customer)
        UI.display(template.format(**values))


def ribbon_from_file():
    """Choose the ribbon from file"""
    ribbon = Ribbon()
    ribbon_file = UI.import_file()
    ribbon.import_from_file(ribbon_file)
    return ribbon


def choose_ribbon(fallback=Ribbon, fallback_description='new empty ribbon'):
    """Select ribbons from database and let the user choose one of them"""
    prompt = 'Your choice? (0 = {})'.format(fallback_description)
    data = get_all_ribbons()
    if not data:
        return fallback()
    UI.display('Choose a ribbon:', end='\n\n')
    list_ribbons(data)
    qty = len(data)
    # let the user choose the ribbon
    choice = UI.enter(prompt, default=0, datatype=int, minimum=0, maximum=qty)
    return data.get(choice) or fallback()


def get_ribbon(ribbon_id=None, fallback=choose_ribbon):
    """Get a ribbon with given ribbon_id"""
    try:
        rows = DB.session.query(Ribbon).filter(Ribbon.ribbon_id == ribbon_id)
        return rows.one()
    except orm_exc.NoResultFound:
        return fallback()


class RibbonMixin:
    """Mixin for ribbon-related operations"""
    _ribbon = Ribbon()

    @property
    def ribbon(self):
        """Ribbon for the casting session"""
        if not self._ribbon:
            # instantiate a new one and cache it
            self._ribbon = Ribbon()
        return self._ribbon

    @ribbon.setter
    def ribbon(self, ribbon):
        """Ribbon setter"""
        self._ribbon = ribbon or Ribbon()

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

    def display_ribbon_contents(self, ribbon=None):
        """Displays the ribbon's contents, line after line"""
        UI.paged_display(ribbon or self.ribbon.contents, sep='\n')


class SourceMixin(object):
    """Mixin for source text"""
    _source = ''

    @property
    def source(self):
        """Source text for typesetting"""
        return self._source

    @source.setter
    def source(self, text):
        """Source setter"""
        self._source = text or ''

    @source.setter
    def input_text(self, text):
        """Set a string of text as the typesetting source"""
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
    _measure, _default_alignment = None, 'left'
    manual_mode = False

    @property
    def measure(self):
        """Typesetting measure i.e. line length"""
        if not self._measure:
            # get measure configuration and return default one
            m_cfg = (PREFS_CFG.default_measure, PREFS_CFG.measurement_unit)
            self._measure = bm.Measure(*m_cfg, set_width=self.wedge.set_width)
        return self._measure

    @measure.setter
    def measure(self, measure):
        """Measure setter"""
        with suppress(ValueError):
            self._measure = bm.Measure(measure, PREFS_CFG.measurement_unit,
                                       set_width=self.wedge.set_width)

    @measure.setter
    def line_length(self, measure):
        """Set the line length for typesetting"""
        self.measure = measure

    @property
    def default_alignment(self):
        """Default alignment:
        Determines how paragraphs ending with a double newline ("\n\n")
        and the end of the source text will be aligned.
        Valid options: "left", "right", "center", "both".
        """
        return self._default_alignment

    @default_alignment.setter
    def default_alignment(self, alignment):
        """Default alignment setter"""
        options = {'cr': d.ALIGNMENTS.left, 'cc': d.ALIGNMENTS.center,
                   'cl': d.ALIGNMENTS.right, 'cf': d.ALIGNMENTS.both,
                   'left': d.ALIGNMENTS.left, 'center': d.ALIGNMENTS.center,
                   'right': d.ALIGNMENTS.right, 'flat': d.ALIGNMENTS.both,
                   'both': d.ALIGNMENTS.both, 'f': d.ALIGNMENTS.both,
                   'l': d.ALIGNMENTS.left, 'c': d.ALIGNMENTS.center,
                   'r': d.ALIGNMENTS.right, 'b': d.ALIGNMENTS.both}
        string = alignment.strip().replace('^', '').lower()
        value = options.get(string)
        if value:
            self._default_alignment = value

    def change_measure(self):
        """Change a line length"""
        old_meas = self.measure
        measure = bc.set_measure(old_meas, what='line length / galley width')
        self.measure = measure

    def change_alignment(self):
        """Changes the default text alignment"""
        msg = 'Choose default alignment for paragraphs:'
        opts = [opt(key='l', value=d.ALIGNMENTS.left, text='left', seq=1),
                opt(key='c', value=d.ALIGNMENTS.center, text='center', seq=2),
                opt(key='r', value=d.ALIGNMENTS.right, text='right', seq=3),
                opt(key='b', value=d.ALIGNMENTS.both, text='justify', seq=4)]
        align = UI.simple_menu(msg, opts, default_key='b', allow_abort=True)
        self.default_alignment = align

    def toggle_manual_mode(self):
        """Changes the manual/automatic typesetting mode"""
        self.manual_mode = not self.manual_mode


class Typesetting(TypesettingContext):
    """Typesetting session - choose and translate text with control codes
    into a sequence of Monotype control codes, which can be sent to
    the machine to cast composed and justified type.
    """
    def main_menu(self):
        """Main menu for the typesetting utility."""
        def finish():
            """Stop the loop"""
            nonlocal finished
            finished = True

        def menu_options():
            """Build a list of options, adding an option"""
            # Options are described with tuples:
            # (function, description, condition)
            opts = [(finish, 'Exit', 'Exits the program', True),
                    (self.edit_text, 'Edit the source text',
                     'Enter or edit the text you want to translate', True),
                    (self.compose, 'Typesetting', 'Translate the text',
                     self.diecase and self.source),
                    (self.choose_diecase, 'Select diecase',
                     'Select a matrix case from database (current: %s)'
                     % (self.diecase or 'not selected'), True),
                    (self.choose_wedge, 'Select wedge',
                     'Enter a wedge designation (current: %s)'
                     % self.wedge, True),
                    (self.change_measure, 'Change measure',
                     'Set new line length (current: %s)' % self.measure, True),
                    (self.change_alignment, 'Change default alignment',
                     'Set a text alignment if no code is present (current: %s)'
                     % self.default_alignment, True),
                    (self.toggle_manual_mode, 'Change the typesetting mode',
                     'Switch to automatic typesetting', self.manual_mode),
                    (self.toggle_manual_mode, 'Change the typesetting mode',
                     'Switch to manual typesetting', not self.manual_mode),
                    (self.display_diecase_layout, 'Show diecase layout',
                     'View the matrix case layout', True),
                    (self.diecase_manipulation, 'Matrix manipulation',
                     'Work on matrix cases', True)]
            # Built a list of menu options conditionally
            return [(func, desc, long_desc)
                    for (func, desc, long_desc, condition) in opts
                    if condition]

        header = ('rpi2caster - CAT (Computer-Aided Typecasting) '
                  'for Monotype Composition or Type and Rule casters.\n\n'
                  'Composition Menu:')
        # Keep displaying the menu and go back here after any method ends
        finished = False
        while not finished:
            with suppress(Abort, EOFError, KeyboardInterrupt):
                UI.menu(menu_options(), header=header, footer='')()

    def get_paragraphs(self):
        """Parse a text into paragraphs with justification modes."""
        # Get a dict of alignment codes
        # Add a default alignment for double line break i.e. new paragraph
        alignments = d.ALIGN_COMMANDS.copy()
        alignments['\n\n'] = self.default_alignment
        # Make a generator function and loop over it
        paragraph_generator = token_parser(self.source, alignments,
                                           skip_unknown=False)
        paragraphs, tokens = [], []
        finished = False
        while not finished:
            try:
                token = next(paragraph_generator)
            except StopIteration:
                # Processed the whole text; any non-whitespace remaining part
                # must be also cast! (will be left-justified)
                end_text = ''.join(tokens).strip()
                if end_text:
                    last = Paragraph(end_text, self.default_alignment)
                    paragraphs.append(last)
                finished = True
            try:
                # Justification token detected - end paragrapgh
                justification = d.ALIGN_COMMANDS[token]
                current_text = ''.join(tokens)
                # Reset the tokens on line currently worked on
                tokens = []
                paragraphs.append(Paragraph(current_text, justification))
            except KeyError:
                # No justification detected = keep adding more characters
                tokens.append(token)
        return paragraphs

    def compose(self):
        """Main composition engine."""
        paragraphs = self.get_paragraphs()
        for paragraph in paragraphs:
            paragraph.display_text()


class Paragraph(object):
    """A page is broken into a series of paragraphs."""
    def __init__(self, text, alignment):
        self.text = text
        self.alignment = alignment
        self.lines = []

    def display_text(self):
        """Prints the text"""
        UI.display(self.text)
