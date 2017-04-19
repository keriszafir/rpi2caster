# -*- coding: utf-8 -*-
"""database_models - all database-dependent models for rpi2caster"""

from collections import OrderedDict
from contextlib import suppress
import json
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base
from . import basic_models as bm
from .config import CFG
from .data import UNIT_ARRANGEMENTS as UA
from .misc import MQ, weakref_singleton
from . import parsing as p
# make sqlalchemy use declarative base
BASE = declarative_base()


class Diecase(BASE):
    """Diecase: matrix case attributes and operations"""
    __tablename__ = 'matrix_cases'
    diecase_id = sa.Column('diecase_id', sa.Text, primary_key=True)
    typeface = sa.Column('typeface', sa.Text)
    _wedge_name = sa.Column('wedge_name', sa.Text,
                            nullable=False, default='S5-12E')
    _ua_mappings = sa.Column('unit_arrangements', sa.Text)
    _layout_json = sa.Column('layout', sa.Text, nullable=False)
    _wedge, _layout, _unit_arrangements = None, None, {}

    def __iter__(self):
        return iter(self.matrices)

    def __repr__(self):
        return ('<Diecase: diecase_id: {} typeface: {}>'
                .format(self.diecase_id, self.typeface))

    def __str__(self):
        return self.diecase_id

    def __bool__(self):
        return bool(self.diecase_id)

    def __call__(self):
        return self

    @property
    def matrices(self):
        """Gets an iterator of mats, read-only, immutable"""
        return (mat for mat in self.layout)

    @property
    def parameters(self):
        """Gets a list of parameters"""
        parameters = OrderedDict()
        parameters['Diecase ID'] = self.diecase_id
        parameters['Typeface'] = self.typeface
        parameters['Assigned wedge'] = self.wedge.name
        return parameters

    @property
    def styles(self):
        """Parses the diecase layout and gets available typeface styles.
        Returns a list of them."""
        return self.layout.styles

    @property
    def unit_arrangements(self):
        """Return a mapping of UnitArrangement objects to styles."""
        def get_ua(ua_id, ua_style):
            """Look up an arrangement for given UA ID and style string"""
            with suppress(KeyError):
                return bm.UnitArrangement(UA[ua_id][ua_style])
            raise bm.UnitArrangementNotFound

        if not self._unit_arrangements:
            # mappings: canonical dict: {'r': ('121', 'r'), 'b': ('150', 'r')}
            mappings = json.loads(self._ua_mappings)
            # found / returned: with styles by definition:
            # {STYLES.roman: UnitArrangement({'a': 8, 'b': 8...}),
            #  STYLES.bold: UnitArrangement({...})...}
            found = {style: get_ua(ua_id, ua_style)
                     for style in bm.Styles(mappings.keys())
                     for style_short, (ua_id, ua_style) in mappings.items()
                     if style.short == style_short}
            self._unit_arrangements = found
        return self._unit_arrangements

    @unit_arrangements.setter
    def unit_arrangements(self, unit_arrangements):
        """Set a dict of unit arrangements for styles in the diecase"""
        self._ua_mappings = json.dumps(unit_arrangements)

    @property
    def wedge(self):
        """Get a wedge based on wedge name stored in database"""
        cached_wedge = self._wedge
        if cached_wedge:
            return cached_wedge
        else:
            # instantiate and store in cache until changed
            wedge = bm.Wedge(self._wedge_name)
            self._wedge = wedge
            return wedge

    @wedge.setter
    def wedge(self, wedge):
        """Set a different wedge"""
        with suppress(AttributeError, TypeError):
            self._wedge = wedge
            self._wedge_name = wedge.name

    @property
    def layout(self):
        """Diecase layout model based on _layout_json.
        If needed, lazily initialize the empty layout."""
        layout = self._layout
        if not layout:
            layout = bm.DiecaseLayout(self._layout_json, self)
            self._layout = layout
        return layout

    @layout.setter
    def layout(self, layout_object):
        """Set the diecase layout object"""
        self._layout = layout_object

    @orm.reconstructor
    def load_layout(self, layout=None):
        """Build a DiecaseLayout() and store it on init"""
        new_layout = layout or self._layout_json
        self.layout = bm.DiecaseLayout(layout=new_layout, diecase=self)
        self.wedge = bm.Wedge()

    def store_layout(self):
        """Save the layout canonical form to ORM"""
        self._layout_json = self.layout.json_encoded


class Ribbon(BASE):
    """Ribbon objects - no matter whether files or database entries.

    A ribbon has the following attributes:
    description, customer - strings
    diecase_id (diecase is selected automatically on casting, so user can e.g.
                view the layout or know which wedge to use)
    contents - series of Monotype codes

    Methods:
    choose_ribbon - choose ribbon automatically or manually,
        first try to get a ribbon with ribbon_id, and if that fails
        ask and select ribbon manually from database, and if that fails
        ask and load ribbon from file
    read_from_file - select a file, parse the metadata, set the attributes
    export_to_file - store the metadata and contents in text file
    store_in_db - store the metadata and contents in db
    set_[description, customer, diecase_id] - set parameters manually"""
    __tablename__ = 'ribbons'
    ribbon_id = sa.Column('ribbon_id', sa.Text, primary_key=True,
                          default='New Ribbon')
    description = sa.Column('description', sa.Text, default='')
    customer = sa.Column('customer', sa.Text, default='')
    diecase_id = sa.Column('diecase_id', sa.Text,
                           sa.schema.ForeignKey('matrix_cases.diecase_id'))
    wedge_name = sa.Column('wedge_name', sa.Text, default='', nullable=False)
    contents = sa.Column('contents', sa.Text, default='', nullable=False)

    def __iter__(self):
        return iter(self.contents)

    def __next__(self):
        yield from self.contents

    def __repr__(self):
        return self.ribbon_id or ''

    def __bool__(self):
        return bool(self.contents)

    def __call__(self):
        return self

    @property
    def parameters(self):
        """Gets a list of parameters"""
        parameters = OrderedDict()
        parameters['Ribbon ID'] = self.ribbon_id
        parameters['Description'] = self.description
        parameters['Customer'] = self.customer
        parameters['Diecase ID'] = self.diecase_id
        parameters['Wedge'] = self.wedge_name
        return parameters

    def update(self, source=None):
        """Updates the object attributes with a dictionary"""
        # Allow to use this method to initialize a new empty ribbon
        if not source:
            source = {}
        with suppress(AttributeError):
            self.ribbon_id = source.get('ribbon_id', '')
            self.description = source.get('description', '')
            self.customer = source.get('customer', '')
            self.diecase_id = source.get('diecase_id', '')
            self.wedge_name = source.get('wedge_name', '')
            self.contents = source.get('contents', [])

    def import_from_file(self, ribbon_file):
        """Imports ribbon from file, parses parameters, sets attributes"""
        with suppress(AttributeError):
            # Try to open it and get only the lines containing non-whitespace
            with ribbon_file:
                raw_data = (line.strip() for line in ribbon_file.readlines())
                ribbon = [line for line in raw_data if line]
            metadata = p.parse_ribbon(ribbon)
            # Update the attributes with what we found
            self.update(metadata)

    def export_to_file(self, ribbon_file):
        """Exports the ribbon to a text file"""
        # Choose file, write metadata, write contents
        with ribbon_file:
            ribbon_file.write('description: ' + self.description)
            ribbon_file.write('customer: ' + self.customer)
            ribbon_file.write('diecase: ' + self.diecase_id)
            ribbon_file.write('wedge: ' + self.wedge_name)
            for line in self.contents:
                ribbon_file.write(line)


@weakref_singleton
class Database:
    """Database object sitting on top of SQLAlchemy"""
    Session = orm.sessionmaker()

    def __init__(self, url='', echo=False):
        self.session, self.engine = None, None
        self.url = url or CFG.get_option('database_url')
        self.echo = echo
        MQ.subscribe(self, 'database')
        self.make_session()

    @property
    def query(self):
        """Query the session"""
        return self.session.query

    def get_diecase(self, diecase_id):
        """Get one diecase with given id; otherwise return empty"""
        try:
            objs = self.query(Diecase).filter(Diecase.diecase_id == diecase_id)
            return objs.one()
        except orm.exc.NoResultFound:
            return Diecase(diecase_id=diecase_id)

    def get_ribbon(self, ribbon_id):
        """Get one diecase with given id; otherwise return empty"""
        try:
            objs = self.query(Ribbon).filter(Ribbon.ribbon_id == ribbon_id)
            return objs.one()
        except orm.exc.NoResultFound:
            return Ribbon(ribbon_id=ribbon_id)

    def update(self, source=None):
        """Update the connection parameters"""
        if source:
            self.url = source.get('url') or self.url
            # turn the sqlalchemy echo (i.e. debug) mode on or off
            self.echo = source.get('debug', self.echo)
            self.make_session()

    def make_session(self):
        """Allows to create a new database session"""
        self.engine = sa.create_engine(self.url, echo=self.echo)
        self.Session.configure(bind=self.engine)
        BASE.metadata.create_all(bind=self.engine)
        self.session = self.Session()


# make exactly one instance of database
DB = Database()
