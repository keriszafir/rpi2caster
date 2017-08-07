# -*- coding: utf-8 -*-
"""Typesetter program"""

from collections import OrderedDict
from contextlib import suppress

from .rpi2caster import CFG, DB, UI, Abort, option as opt
from . import basic_models as bm, basic_controllers as bc, definitions as d
from . import parsing as p
from .main_models import Ribbon
from .main_controllers import DiecaseMixin


# Ribbon control routines

@DB
def get_all_ribbons():
    """Lists all ribbons we have."""
    try:
        rows = Ribbon.select().order_by(Ribbon.ribbon_id)
        ribbons = OrderedDict(enumerate(rows, start=1))
        return ribbons
    except DB.OperationalError:
        Ribbon.create_table(fail_silently=True)
        return get_all_ribbons()


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


def ribbon_from_file(file=None, manual_choice=True):
    """Import the ribbon from file object specified as argument.
    Choose the file manually if file object is not specified.

    file: any object with the readlines() method"""
    ribbon_file = (file if 'readlines' in dir(file)
                   else open(file, 'r') if file
                   else UI.import_file() if manual_choice else None)
    if ribbon_file:
        ribbon = Ribbon()
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


@DB
def get_ribbon(ribbon_id=None, fallback=choose_ribbon):
    """Get a ribbon with given ribbon_id"""
    if ribbon_id:
        try:
            return Ribbon.get(Ribbon.ribbon_id == ribbon_id)
        except Ribbon.DoesNotExist:
            UI.display('Ribbon {} not found in database.'.format(ribbon_id))
        except DB.OperationalError:
            Ribbon.create_table(fail_silently=True)
    return fallback()


class RibbonMixin:
    """Mixin for ribbon-related operations"""
    _ribbon = Ribbon()

    @property
    def ribbon(self):
        """Ribbon for the casting/typesetting session"""
        return self._ribbon

    @ribbon.setter
    def ribbon(self, ribbon):
        """Ribbon setter. False or None will result in new empty Ribbon()"""
        self._ribbon = ribbon or Ribbon()

    @ribbon.setter
    def ribbon_file(self, ribbon_file):
        """Use a ribbon file"""
        self.ribbon = ribbon_from_file(ribbon_file)

    @ribbon.setter
    def output_file(self, ribbon_file):
        """Use a ribbon file"""
        self.ribbon.file = ribbon_file

    @ribbon.setter
    def ribbon_id(self, ribbon_id):
        """Use a ribbon with a given ID, or an empty one"""
        self.ribbon = get_ribbon(ribbon_id, fallback=self.ribbon)

    def ribbon_by_name(self, name, choose_if_not_found=False):
        """Try to determine if the name supplied is a ribbon ID or filename.
        Otherwise use the fallback option."""
        # 1. try looking it up in the database
        # 2. try loading it from file
        # 3. optionally try choosing another ribbon if both lookups failed
        # 4. if all fails, just keep the current ribbon
        def sources():
            """try different ribbon sources"""
            # no name? fresh ribbon then
            if not name:
                yield Ribbon()
            # try looking it up in the database
            yield get_ribbon(name, fallback=lambda *_: None)
            # try to get a file
            yield ribbon_from_file(name, manual_choice=False)
            # choose manually
            if choose_if_not_found:
                yield choose_ribbon()
            # all of these failed = don't change anything
            yield self.ribbon

        for ribbon in sources():
            if ribbon:
                self.ribbon = ribbon
                break

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
    def text_file(self, text_file):
        """Use a file object as a source of text"""
        # If a string or None is passed as an argument,
        # AttributeError would be raised. We'd rather ignore it.
        with suppress(AttributeError), text_file:
            self.source = ''.join(text_file.readlines())

    def edit_text(self):
        """Edits the input text"""
        self.source = UI.edit(self.source)
        return self.source


class TypesettingContext(SourceMixin, DiecaseMixin, RibbonMixin):
    """Mixin for setting diecase, wedge and measure"""
    _measure, _default_alignment = None, 'left'
    manual_mode = False

    @property
    def measure(self):
        """Typesetting measure i.e. line length"""
        if not self._measure:
            # get measure configuration and return default one
            measure = CFG['Typesetting'].get('default_measure')
            unit = CFG['Typesetting'].get('measurement_unit')
            self._measure = bm.Measure(measure, unit, self.wedge.set_width)
        return self._measure

    @measure.setter
    def measure(self, measure):
        """Measure setter"""
        with suppress(ValueError):
            unit = CFG['Typesetting'].get('measurement_unit')
            self._measure = bm.Measure(measure, unit, self.wedge.set_width)

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
        options = {}
        for alignment in d.ALIGNMENTS:
            shorts = [alignment.name, alignment.name[0],
                      *(code.strip('^') for code in alignment.codes)]
            options.update({s: alignment for s in shorts})

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

    @property
    def compose(self):
        """Bridge for automatic/manual typesetting.
        Choice is made by manual_mode flag."""
        return self._manual_compose if self.manual_mode else self._auto_compose

    def _manual_compose(self, source=''):
        """Manual composition, where the user makes end-of-line decisions"""
        text = source or self.source

    def _auto_compose(self, source=''):
        """Automatic typesetting with hyphenation and justification"""


class Document:
    """A document represents a whole page of text to be cast in one run.
    It may and probably will consist of multiple paragraphs,
    separated by double newlines ('\n\n')."""
    def __init__(self, text, context):
        self.text = str(text)
        self.context = context
        # split the text into paragraphs with text and alignment
        parsed = p.cut_to_paragraphs(self.text)
        self.paragraphs = [Paragraph(t, a, self.context) for t, a in parsed]

    def compose(self):
        """Typeset the document. The context is a TypesettingContext
        and stores information such as line length, alignments etc."""
        for paragraph in self.paragraphs:
            paragraph.compose()

    def translate(self):
        """Translate the document into Monotype codes"""
        return sum((par.translate() for par in self.paragraphs), [])

    def make_ribbon(self):
        """Make a ribbon i.e. signals sequence out of the document"""
        sequence = (obj.get_ribbon_record() for obj in self.translate())
        contents = '\n'.join(sequence)
        ribbon = Ribbon()
        ribbon.contents = contents
        self.contxt.ribbon = ribbon


class Paragraph(object):
    """A page is broken into a series of paragraphs."""
    def __init__(self, text, alignment, context):
        self.text = text
        self.context = context
        self.alignment = alignment or context.default_alignment
        self.lines = []

    def display_text(self):
        """Prints the text"""
        UI.display(self.text)

    def compose(self, context):
        """Typeset the paragraph's text"""
        self.context = context

    def translate(self):
        """Translate the characters into a series of Monotype codes"""
