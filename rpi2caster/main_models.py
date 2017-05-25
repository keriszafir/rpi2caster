# -*- coding: utf-8 -*-
"""main_models - all big/database-dependent models for rpi2caster"""

from collections import OrderedDict
from contextlib import suppress
from itertools import chain
import json

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.ext.declarative import declarative_base

from . import basic_models as bm
from .config import CFG
from .data import TYPEFACES as TF
from .misc import MQ, weakref_singleton
from . import definitions as d, parsing as p
# make sqlalchemy use declarative base
BASE = declarative_base()
BASE.DoesNotExist = NoResultFound


class Diecase(BASE):
    """Diecase: matrix case attributes and operations"""
    __tablename__ = 'matrix_cases'
    diecase_id = sa.Column('diecase_id', sa.Text, primary_key=True)
    _typeface = sa.Column('typeface', sa.Text)
    _wedge_name = sa.Column('wedge_name', sa.Text,
                            nullable=False, default='S5-12E')
    _layout_json = sa.Column('layout', sa.Text, nullable=False)
    _wedge, _layout = None, None

    def __iter__(self):
        return iter(self.matrices)

    def __repr__(self):
        return ('<Diecase: diecase_id: {} typeface: {}>'
                .format(self.diecase_id, self.typeface.text))

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
        parameters['Typeface'] = self.typeface.text
        parameters['Assigned wedge'] = self.wedge.name
        return parameters

    @property
    def styles(self):
        """Get declared styles from typeface metadata
        or look them up in layout"""
        return self.typeface.styles or self.layout.styles

    @property
    def typeface(self):
        """Typeface data"""
        def get_name(number):
            """find a typeface name in defined typefaces"""
            return TF.get(number, {}).get('typeface', '')

        try:
            # new-style typeface data
            raw = json.loads(self._typeface)
            styles = bm.Styles(raw)
            raw_numbers = {st.get('typeface', '') for st in raw.values()}
            # sort strings as if they were integers
            ids = [*sorted(raw_numbers, key=lambda x: (len(x), x))]
            # typefaces (num, name) -> num name + num2 name2...
            typefaces = [(num, get_name(num)) for num in ids if num]
            text = ' + '.join('{} {}'.format(*face) for face in typefaces)
            # unit arrangements
            uas = {s: data.get('ua') for s, data in raw.items()}

        except (json.JSONDecodeError, TypeError, KeyError, AttributeError):
            # old typeface data (should be OK after reconfiguring)
            styles, text = bm.Styles('rbi'), self._typeface
            raw, ids, uas = {}, [], {}

        return d.Typeface(styles=styles, ids=ids, raw=raw, text=text, uas=uas)

    @typeface.setter
    def typeface(self, metadata):
        """Set the typeface metadata"""
        try:
            # typeface namedtuple
            self._typeface = json.dumps(metadata.raw)
        except AttributeError:
            # raw typeface dict
            self._typeface = json.dumps(metadata)

    @property
    def unit_arrangements(self):
        """Return a mapping of UnitArrangement objects to styles."""
        # mappings: canonical dict: {'r': ('121', 'r'), 'b': ('150', 'r')}
        uas = self.typeface.uas or {}
        return {bm.Styles(s): bm.UnitArrangement(*ua) for s, ua in uas.items()}

    @property
    def wedge(self):
        """Get a wedge based on wedge name stored in database"""
        cached_wedge = self._wedge
        if cached_wedge:
            return cached_wedge
        else:
            # instantiate and store in cache until changed
            wedge = bm.Wedge(wedge_name=self._wedge_name)
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
            layout = DiecaseLayout(self._layout_json, diecase=self)
            self._layout = layout
        return layout

    @layout.setter
    def layout(self, layout_object):
        """Set the diecase layout object"""
        self._layout = layout_object

    def load_layout(self, layout=None):
        """Build a DiecaseLayout() and store it on init"""
        new_layout = layout or self._layout_json
        self.layout = DiecaseLayout(layout=new_layout, diecase=self)

    def store_layout(self):
        """Save the layout canonical form to ORM"""
        self._layout_json = self.layout.json_encoded


class DiecaseLayout:
    """Matrix case layout and outside characters data structure.
    layout : a tuple/list of tuples/lists denoting matrices:
              [(char, styles_string, position, units),...]
    diecase : a Diecase() class object

    Mats without position (None or empty string) will end up in the
    outside characters collection."""
    __slots__ = ('used_mats', 'outside_mats', '_diecase')

    def __init__(self, layout=None, diecase=None):
        self.used_mats, self.outside_mats = {}, []
        self._diecase = diecase
        try:
            self.json_encoded = layout
        except (TypeError, json.JSONDecodeError):
            self.raw = layout

    def __repr__(self):
        return ('<DiecaseLayout ({} rows, {} columns)>'
                .format(self.size.rows, self.size.columns))

    def __iter__(self):
        return (mat for mat in self.used_mats.values())

    def __contains__(self, obj):
        return obj in self.used_mats.values()

    @property
    def diecase(self):
        """Diecase class object associated with this layout"""
        return self._diecase

    @diecase.setter
    def diecase(self, diecase):
        """Diecase to use this layout with"""
        self._diecase = diecase
        for mat in self.all_mats:
            mat.diecase = diecase

    @property
    def size(self):
        """Get the LayoutSize for this diecase layout."""
        rows = len({row for (_, row) in self.used_mats})
        columns = len({column for (column, _) in self.used_mats})
        return bm.LayoutSize(rows=rows, columns=columns)

    @size.setter
    def size(self, size):
        """Resize the diecase layout"""
        self.resize(*size)

    @property
    def all_mats(self):
        """A list of all matrices - both used and outside"""
        return list(chain(self.used_mats.values(), self.outside_mats))

    @property
    def styles(self):
        """Get all available character styles from the diecase layout."""
        return sum(mat.styles for mat in self.all_mats
                   if not mat.styles.use_all)

    def get_charset(self, diecase_chars=True, outside_chars=False):
        """Diecase character set"""
        charset = {}
        used = self.used_mats.values() if diecase_chars else []
        unused = self.outside_mats if outside_chars else []
        for mat in chain(used, unused):
            if not mat.char or mat.isspace():
                continue
            for style in mat.styles:
                charset.setdefault(style, {})[mat.char] = mat
        return charset

    def get_lookup_table(self, diecase_chars=True, outside_chars=False):
        """Return a structure of {(mat char, style): mat}"""
        used = self.used_mats.values() if diecase_chars else []
        unused = self.outside_mats if outside_chars else []
        return {(mat.char, style): mat for mat in chain(used, unused)
                for style in mat.styles}

    @property
    def raw(self):
        """Raw layout i.e. list of tuples with matrix parameters"""
        all_mats = chain(self.used_mats.values(), self.outside_mats)
        in_diecase = (mat.get_layout_record() for mat in all_mats)
        outside = (mat.get_layout_record(pos='') for mat in self.outside_mats)
        return [*in_diecase, *outside]

    @raw.setter
    def raw(self, raw_layout):
        """Sort the raw layout into matrices in diecase and outside chars.
        Accepts any iterator of (char, style_string, position, units)"""
        size = bm.LayoutSize(15, 15)
        try:
            # Get matrices from supplied layout's canonical form
            raw_records = (d.MatrixRecord(*record) for record in raw_layout)
            mats = [bm.Matrix(char=rec.char, styles=rec.styles, code=rec.code,
                              units=rec.units, diecase=self.diecase)
                    for rec in raw_records]
            # parse the source layout to get its size,
            # reversing the order increases the chance of finding row 16 faster
            for matrix in reversed(mats):
                if matrix.position.row == 16:
                    # finish here as the only 16-row diecases were 16x17
                    size.rows, size.columns = 16, 17
                    break
                if matrix.position.column in ('NI', 'NL'):
                    # update the columns number
                    # iterate further because we can still find 16th row
                    size.columns = 17
        except (TypeError, ValueError):
            # Layout supplied is incorrect; use a default size of 15x17
            mats, size.rows, size.columns = [], 15, 17
        # Build empty layout determining its size
        used_mats = size.clean_layout(diecase=self.diecase)
        # Fill it with matrices for existing positions
        for mat in mats[:]:
            position = mat.position
            if used_mats.get(position):
                used_mats[position] = mat
                mats.remove(mat)
        # The remaining mats will be stored in outside layout
        self.used_mats, self.outside_mats = used_mats, mats

    @property
    def json_encoded(self):
        """JSON-encoded list of tuples denoting matrices in the diecase."""
        return json.dumps(self.raw)

    @json_encoded.setter
    def json_encoded(self, layout_json):
        """Parse a JSON-encoded list to read a layout"""
        self.raw = json.loads(layout_json)

    @property
    def spaces(self):
        """Get all available spaces"""
        return [mat for mat in self.used_mats.values() if mat.isspace()]

    def purge(self):
        """Resets the layout to an empty one of the same size"""
        self.outside_mats = []
        self.used_mats = self.size.clean_layout(diecase=self.diecase)

    def resize(self, rows=15, columns=17):
        """Rebuild the layout to adjust it to the new diecase format"""
        # manipulate data structures locally
        old_layout = self.used_mats
        new_size = bm.LayoutSize(rows, columns)
        new_layout = new_size.clean_layout(diecase=self.diecase)
        # new list of outside characters
        old_extras = self.outside_mats
        new_extras = []
        # preserve mats as outside characters when downsizing the layout
        for position, mat in old_layout.items():
            if new_layout.get(position):
                # the new layout has a position for this matrix
                new_layout[position] = mat
            else:
                # no place for it = put it in outside chars
                new_extras.append(mat)
        # pull the mats from outside layout to diecase automatically
        # if so, remove them from outside layout
        for mat in old_extras[:]:
            position = mat.position
            if new_layout.get(position):
                # there is something at this position
                new_layout[position] = mat
                old_extras.remove(mat)
        # finally update the instance attributes
        self.used_mats = new_layout
        self.outside_mats = old_extras + new_extras

    def select_many(self, char=None, styles=None, code=None, units=None,
                    islowspace=None, ishighspace=None):
        """Get all matrices with matching parameters"""
        def match(matrix):
            """Test the matrix for conditions unless they evaluate to False"""
            # guard against returning True if no conditions are valid
            # end right away
            wants = (char, styles, code, units, islowspace, ishighspace)
            if not any(wants):
                return False
            finds = (matrix.char, matrix.styles, matrix.code, matrix.units,
                     matrix.islowspace(), matrix.ishighspace())
            # check all that apply and break on first mismatch
            for wanted, found in zip(wants, finds):
                if wanted and wanted != found:
                    return False
            # all conditions match
            return True

        results = [mat for mat in self.used_mats.values() if match(mat)]
        return results

    def select_one(self, *args, **kwargs):
        """Get a matrix with denoted parameters"""
        with suppress(IndexError):
            search_results = self.select_many(*args, **kwargs)
            return search_results[0]
        raise bm.MatrixNotFound

    def get_space(self, units=0, low=True, wedge=None):
        """Find a suitable space in the diecase layout"""
        def mismatch(checked_space):
            """Calculate the unit difference between space's width
            and desired unit width"""
            wdg = wedge or self.diecase.wedge
            # how much adjustment would be needed? single or double mat?
            difference = units - wdg[checked_space.position.row]
            low = checked_space.islowspace()
            cells = checked_space.size.horizontal
            # calculate minimum and maximum
            limits = wdg.get_adjustment_limits(low_space=low, cell_width=cells)
            shrink, stretch = limits.shrink, limits.stretch
            return abs(difference) if -shrink < difference < stretch else -1

        spaces = [mat for mat in self.spaces if mismatch(mat) >= 0 and
                  mat.islowspace() == low and mat.ishighspace() != low]
        matches = sorted(spaces, key=mismatch)
        try:
            return matches[0]
        except IndexError:
            # can't match a space no matter how we try
            exc_message = 'Cannot find a {} space close enough to {} units.'
            high_or_low = 'low' if low else 'high'
            raise bm.MatrixNotFound(exc_message.format(high_or_low, units))

    def select_row(self, row_number):
        """Get all matrices from a given row"""
        row_num = int(row_number)
        return [mat for (_, r), mat in self.used_mats.items() if r == row_num]

    def select_column(self, column):
        """Get all matrices from a given column"""
        col_num = column.upper()
        return [mat for (c, _), mat in self.used_mats.items() if c == col_num]

    def by_rows(self):
        """Get all matrices row by row"""
        return [self.select_row(row) for row in self.size.row_numbers]

    def by_columns(self):
        """Get all matrices column by column"""
        return [self.select_column(col) for col in self.size.column_numbers]


class Ribbon(BASE):
    """Ribbon objects - no matter whether files or database entries.

    A ribbon has the following attributes:
    description, customer - strings,
    diecase_id (diecase is selected automatically on casting, so user can e.g.
                view the layout or know which wedge to use),
    source_text - original text the ribbon was set from; useful for
                  re-composing for different parameters,
    contents - series of Monotype codes.

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
    source_text = sa.Column('source_text', sa.Text, default='', nullable=False)
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

    def get_diecase(self, diecase_id):
        """Get one diecase with given id; otherwise return empty"""
        try:
            query = self.session.query(Diecase)
            objs = query.filter(Diecase.diecase_id == diecase_id)
            return objs.one()
        except orm.exc.NoResultFound:
            return Diecase(diecase_id=diecase_id)

    def get_ribbon(self, ribbon_id):
        """Get one diecase with given id; otherwise return empty"""
        try:
            query = self.session.query(Ribbon)
            objs = query.filter(Ribbon.ribbon_id == ribbon_id)
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
