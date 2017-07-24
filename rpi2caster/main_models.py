# -*- coding: utf-8 -*-
"""main_models - all big/database-dependent models for rpi2caster"""

from collections import defaultdict, OrderedDict
from contextlib import suppress
from itertools import chain
from functools import singledispatch
import json

import peewee as pw

from .rpi2caster import DB
from . import basic_models as bm, definitions as d, parsing as p, data


class BaseModel(pw.Model):
    """Base class for all models"""
    # define the class exception here, to appease linters
    DoesNotExist = pw.DoesNotExist

    class Meta:
        """Database metadata"""
        database = DB

        def db_table_func(self):
            """get a table name for a model"""
            try:
                model_name = self.__name__
            except AttributeError:
                model_name = self.__class__.__name__
            tables = dict(Diecase='matrix_cases', Ribbon='ribbons')
            return tables.get(model_name) or '{}s'.format(model_name.lower())


class Diecase(BaseModel):
    """Diecase: matrix case attributes and operations"""
    diecase_id = pw.TextField(db_column='diecase_id', primary_key=True)
    _typeface = pw.TextField(db_column='typeface', null=True,
                             help_text='JSON-encoded typeface metadata')
    _wedge_name = pw.TextField(db_column='wedge_name', default='S5-12E',
                               help_text='wedge series and set width')
    _layout_json = pw.TextField(db_column='layout',
                                help_text='JSON-encoded diecase layout')
    _wedge, _layout = None, None

    def __iter__(self):
        return iter(self.matrices)

    def __repr__(self):
        return ('<Diecase: {} - {}>'
                .format(self.diecase_id, self.description))

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
    def description(self):
        """Get the diecase description"""
        if not self.typeface_data:
            return self._typeface
        faces = [face for (face, _) in self.typeface_data.values()]
        series = '+'.join(sorted({tf.series for tf in faces}))
        names = ', '.join(sorted({tf.name for tf in faces}))
        return '{} - {}'.format(series, names)

    @property
    def parameters(self):
        """Gets a list of parameters"""
        parameters = OrderedDict()
        parameters['Diecase ID'] = self.diecase_id
        parameters['Typeface'] = self.description
        parameters['Assigned wedge'] = self.wedge.name
        return parameters

    @property
    def styles(self):
        """Get declared styles from typeface metadata
        or look them up in layout"""
        typeface_styles = bm.Styles(self.typeface_data)
        return typeface_styles or self.layout.styles

    @property
    def typeface_data(self):
        """Typeface data"""
        _cached = self.__dict__.get('_typeface_data')
        if _cached:
            # early return = don't calculate it again
            return _cached

        try:
            source = json.loads(self._typeface)
        except (json.JSONDecodeError, TypeError):
            # revert to default 327-12
            typeface = TypefaceVariant()
            typeface_tuple = (typeface, typeface.unit_arrangement)
            _typeface_data = OrderedDict({typeface.style: typeface_tuple})
            self.__dict__['_typeface_data'] = _typeface_data
            return _typeface_data

        # each style (roman, bold, italic) has a typeface and UA assigned
        # e.g. {'r': ('327', '12D', 'r', '325', 'r'),
        #       'i': ('327', '12D', 'i', '324', 'r')}
        _typeface_data = OrderedDict()
        for style in bm.Styles(source.keys()):
            type_id, size, style_id, ua_id, ua_variant = source[style.short]
            typeface_variant = TypefaceVariant(type_id, size, style_id)
            try:
                unit_arrangement = UAVariant(ua_id, ua_variant)
            except ValueError:
                try:
                    unit_arrangement = UAVariant(ua_id, style.short)
                except ValueError:
                    unit_arrangement = typeface_variant.unit_arrangement
            # update the data
            _typeface_data[style] = (typeface_variant, unit_arrangement)

        # data ready to ship (cache to avoid recalculating)
        self.__dict__['_typeface_data'] = _typeface_data
        return _typeface_data

    @typeface_data.setter
    def typeface_data(self, typeface_data):
        """Set the typeface metadata"""
        # prepare the output data
        output = OrderedDict()
        for style, (tface, arrangement) in typeface_data.items():
            output[style.short] = (tface.series, tface.size, tface.style.short,
                                   arrangement.number, arrangement.short)
        self._typeface = json.dumps(output)
        self.__dict__['_typeface_data'] = typeface_data

    @property
    def unit_arrangements(self):
        """Return a mapping of UAVariant objects to styles."""
        return {s: ua for s, (_, ua) in self.typeface_data.items()}

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
                   if not mat.styles.use_all) or bm.Styles(None)

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
            if wedge:
                wdg = wedge
            elif self.diecase:
                wdg = self.diecase.wedge
            else:
                wdg = bm.Wedge()
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


class UnitArrangement:
    """Unit arrangement definition.
    Can contain one or more variants for different type styles.
    """
    variant_sequence = ('r', 'i', 's', 'ar', 'ai', 'as', 'br', 'g'
                        's1', 's2', 's3', 's4', 's5')
    variant_definitions = dict(r=('regular', 'roman or the only style'),
                               i=('italic', ''),
                               s=('small caps', ''),
                               g=('Gaelic accents', ''),
                               ar=('regular A', 'modified char widths'),
                               ai=('italic A', 'modified char widths'),
                               br=('regular B', 'modified char widths'),
                               s1=('size 1', 'titling'),
                               s2=('size 2', 'titling'),
                               s3=('size 3', 'titling'),
                               s4=('size 4', 'titling'),
                               s5=('size 5', 'titling'))
    variant_definitions['as'] = ('small caps A', 'modified char widths')

    def __init__(self, number=0):
        # store the number (string in case int was supplied)
        self.number = str(number)

        # look up the unit arrangement data
        arrangement_data = data.UNIT_ARRANGEMENTS.get(self.number, {})
        if not arrangement_data:
            raise ValueError('Unit arrangement {} not found!'.format(number))

        # store the underlying data
        self._raw_data = OrderedDict([(variant, arrangement_data[variant])
                                      for variant in self.variant_sequence
                                      if arrangement_data.get(variant)])

    def __str__(self):
        return 'UA #{}'.format(self.number)

    def __repr__(self):
        return '<UnitArrangement #{}>'.format(self.number)

    def __getitem__(self, item):
        return self(item)

    def __call__(self, variant):
        return self.get_variant(variant)

    def get_variant(self, variant):
        """Make a UAVariant instance for a specified variant"""
        return UAVariant(self.number, variant)

    @property
    def variants(self):
        """Get all variants for this unit arrangement"""
        return [self.get_variant(var) for var in self._raw_data]

    @property
    def variant_names(self):
        """Get a string with UA variant names and letters"""
        return ', '.join('{}: {}'.format(s, self.variant_definitions[s][0])
                         for s in self.variant_sequence)


class UAVariant(UnitArrangement):
    """Unit arrangement variant class. Stores unit values for characters.
    Each unit arrangement has one or more variants
    (for example: roman, italic, small caps, Gaelic accents,
    size 1, 2, 3, 4, 5 - mostly for titling,
    modifications with different units for some characters)."""
    def __init__(self, number, variant='r'):
        super().__init__(number)
        self.short = variant

        # is this the valid unit arrangement variant?
        variant_definition = self.variant_definitions.get(variant)
        if not variant_definition:
            raise ValueError('Incorrect variant: {}'.format(variant))
        self.name, self.alternatives = variant_definition

        # get the unit values for this variant
        arrangement = self._raw_data.get(self.short, {})
        if not arrangement:
            raise ValueError('{} has no character unit values!'.format(self))

        # parse the UA
        by_units = defaultdict(list)
        for char, units in sorted(arrangement.items()):
            by_units[units].append(char)
        # store the result
        self.by_char, self.by_units = arrangement, by_units

    def __str__(self):
        return 'Unit arrangement #{} {}'.format(self.number, self.name)

    def __repr__(self):
        return '<UAVariant: #{} {}>'.format(self.number, self.name)

    def __call__(self, item):
        """Get a unit arrangement for a given style"""
        @singledispatch
        def getter(_):
            """dispatch on type, accept only strings or numeric values"""
            raise TypeError('Unknown type')

        getter.register(int, self.get_chars)
        getter.register(float, self.get_chars)
        getter.register(str, self.get_units)
        return getter(item)

    def get_chars(self, unit_value):
        """Get the characters list for a given unit value"""
        value = int(unit_value)
        return sorted(self.by_units.get(value))

    def get_units(self, char):
        """Get unit value from an arrangement"""
        # first try to look it up in arrangement
        with suppress(KeyError):
            return self.by_char[char]
        # might be an accented version
        base_char = d.REVERSE_ACCENTS.get(char)
        if not char:
            return 0
        with suppress(KeyError):
            return self.by_char[base_char]
        # no character in UA
        raise ValueError('Unit value for {} not found!'.format(char))

    def get_mat_units(self, matrix):
        """Get unit value for a Matrix object"""
        return self.get_units(matrix.char)


class Typeface:
    """Typeface definition. Gets all data for the given typeface number.

    Typeface data is stored in data/typefaces.json as a dictionary:
        {"262": {"name": "Gill Sans",
                 "scripts": ["Latin", "Cyrillic"],
                 "tags": ["sans serif", "modern", "humanist", "Eric Gill"],
                 "related": {"b": (275, "r"), "q": (275, "i")},
                 "sizes": {"6": [6.5, .1220],
                           "8": [8.25, .1285] etc.},
                 "uas": {"r": (82, "r"), "i": (82, "i")}},
        "327": {"name": "Times New Roman"...}}
    Keys in the main dictionary are typeface series numbers.
    Values are the typeface data:
        name - typeface name,
        scripts - a list of scripts/alphabets the typeface was designed for,
        tags - a list of tags describing the typeface (e.g. Vox-ATypI classes),
        related - a dictionary of related typefaces by style,
        sizes - size-specific data: [set_width, calibration_line, ua_overrides]
            where calibration_line is the "M line" parameter from the
            type specimen book, and ua_overrides are optional corrections
            to the unit arrangement mappings for some sizes or styles,
        uas - unit arrangement mapping for each of the styles.
    """
    def __init__(self, series='327'):
        self.series = str(series)
        raw_data = data.TYPEFACES.get(self.series, {})
        self._raw_data = raw_data
        self.name = raw_data.get('name', 'unknown typeface')
        self.classification = ', '.join(raw_data.get('tags', ['']))
        self.script = ', '.join(raw_data.get('scripts', ['Latin']))
        uas = raw_data.get('uas', {})
        self.sizes = self._raw_data.get('sizes', {})
        self.unit_arrangements = {bm.STYLES.get(st): UAVariant(ua_id, ua_v)
                                  for st, (ua_id, ua_v) in uas.items()}

    def __call__(self, size):
        return self.get_size(size)

    def __getitem__(self, item):
        return self(item)

    def __repr__(self):
        return '<Typeface: {t.series} {t.name}>'.format(t=self)

    def __str__(self):
        return ('{t.series} {t.name} ({t.script} {stylenames})'
                .format(t=self, stylenames=self.styles.names))

    def get_size(self, size):
        """Get a variant in a specified size"""
        return TypefaceSize(self.series, size)

    @property
    def related(self):
        """Get related (combinable in diecase) typefaces for this typeface,
        e.g. 334 Times Bold for 327 Times New Roman"""
        related = self._raw_data.get('related', {})
        roman = bm.Styles.definitions.roman
        retval = {}
        # related styles are defined similar to unit arrangements:
        # {rel_style: (typeface_number, style_in_typeface)}
        for raw_style, (rel_tface, rel_style) in related.items():
            style = bm.STYLES.get(raw_style)
            if not style:
                continue
            related_style = bm.STYLES.get(rel_style) or roman
            tface = Typeface(rel_tface)
            retval[style] = (tface, related_style)

        return retval

    @property
    def styles(self):
        """Get the styles for this typeface."""
        # DEPRECATED: styles will be stored in unit arrangement mappigns only!
        # use the "styles" as a fallback only
        typeface_styles = self._raw_data.get('styles', '')
        return bm.Styles(self.unit_arrangements or typeface_styles)

    @property
    def related_styles(self):
        """Get all related styles. These are combinable in the same diecase."""
        return bm.Styles(self.related)

    @property
    def combined_styles(self):
        """Get all styles for this typeface and related typefaces combined."""
        return self.styles + self.related_styles


class TypefaceSize(Typeface):
    """A typeface in a specified size."""
    def __init__(self, series='327', size='12D'):
        def get_size_data(_size):
            """Get the size data from typeface data"""
            size_data = self.sizes.get(_size)
            with suppress(TypeError, AttributeError):
                # first try getting a reference to another size
                # it's a string so it should be convertible to uppercase
                return get_size_data(size_data.upper().strip())
            # check if we have a tuple/list of 3 or 2 items
            with suppress(TypeError, ValueError):
                # 3 values: set width, M-line, unit arrangement overrides
                set_width, calibration_line, raw_ua_data = size_data
                ua_overrides = {bm.STYLES.get(st): UAVariant(ua_id, ua_v)
                                for st, (ua_id, ua_v) in raw_ua_data.items()}
                self.unit_arrangements.update(ua_overrides)
                return set_width, calibration_line
            with suppress(TypeError, ValueError):
                # check if it's a 2-item tuple or list
                set_width, calibration_line = size_data
                return set_width, calibration_line
            # nothing above is correct? (for example, lookup returned None)
            return 0, 0

        super().__init__(series)
        converted_size = str(size).upper().strip()
        # strip all non-numeric characters
        if converted_size not in self.sizes:
            converted_size = ''.join(x for x in converted_size if x.isdigit())
        self.size = converted_size
        self.set_width, self.calibration_line = get_size_data(self.size)

    def __repr__(self):
        return '<TypefaceSize: {t.series}-{t.size} {t.name}>'.format(t=self)

    def __str__(self):
        return ('{t.series}-{t.size} {t.name} ({t.script} {stylenames})'
                .format(stylenames=self.styles.names, t=self))

    def __call__(self, style):
        return self.get_variant(style)

    @property
    def related(self):
        """Get related (combinable in diecase) TypefaceSize objects,
        e.g. 334 Times Bold for 327 Times New Roman"""
        related = super().related
        return {style: tface(self.size)(rel_style)
                for style, (tface, rel_style) in related.items()}

    def get_variant(self, style):
        """Get a typeface variant for a given style"""
        _style = bm.STYLES.get(style)
        if not _style:
            raise ValueError('Incorrect style: {}'.format(style))
        try:
            return TypefaceVariant(self.series, self.size, _style)
        except ValueError:
            # look it up in related typefaces
            with suppress(KeyError):
                return self.related[_style]
            msg = ('{} not present in {}-{} {} or any of its related typefaces'
                   .format(_style.name, self.series, self.size, self.name))
            raise ValueError(msg)


class TypefaceVariant(TypefaceSize):
    """A concrete typeface/size/style combination."""
    def __init__(self, series='327', size='12D', style=None):
        super().__init__(series, size)
        _style = (bm.STYLES.get(style) or
                  (self.styles.first if style is None else None))
        if not _style:
            raise ValueError('Incorrect style: {}'.format(style))
        elif _style not in self.styles:
            msg = ('{} not present in {}-{} {}'
                   .format(_style.name, self.series, self.size, self.name))
            raise ValueError(msg)
        self.style = _style
        self.unit_arrangement = self.unit_arrangements.get(_style, {})

    def __repr__(self):
        stylename = self.style.name if self.style else self.style
        return ('<TypefaceVariant: {t.series}-{t.size} {t.name} {style}>'
                .format(t=self, style=stylename))

    def __str__(self):
        return '{t.series}-{t.size} {t.name} {t.style.name}'.format(t=self)


class Ribbon(BaseModel):
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
    ribbon_id = pw.TextField(db_column='ribbon_id', primary_key=True,
                             default='New Ribbon',
                             help_text='Unique ribbon name')
    description = pw.TextField(db_column='description', default='')
    customer = pw.TextField(db_column='customer', default='')
    diecase = pw.ForeignKeyField(Diecase)
    wedge_name = pw.TextField(db_column='wedge_name', default='')
    source_text = pw.TextField(db_column='source_text', default='')
    contents = pw.TextField(db_column='contents', default='')

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
