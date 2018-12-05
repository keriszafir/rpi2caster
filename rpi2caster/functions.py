# coding: utf-8
"""rpi2caster routines and functions"""

from collections import deque
from functools import lru_cache
from .models import Ribbon, ParsedRecord, Matrix, Wedge

# parsing delimiters
COMMENT_SYMBOLS = ['**', '*', '//', '##', '#']
ASSIGNMENT_SYMBOLS = ['=', ':', ' ']
OUTPUT_SIGNALS = tuple(['0075', 'S', '0005', *'ABCDEFGHIJKLMN',
                        *(str(x) for x in range(1, 15)), 'O15'])


# matrix routines

@lru_cache(maxsize=350)
def parse_coordinates(code):
    """Sets the coordinates for the matrix"""
    def row_generator():
        """Generate matching rows, removing them from input sequence"""
        yield None
        nonlocal sigs
        for number in range(16, 0, -1):
            string = str(number)
            if string in sigs:
                sigs = sigs.replace(string, '')
                yield number

    def column_generator():
        """Generate column numbers"""
        nonlocal sigs
        for column in ['NI', 'NL', *'ABCDEFGHIJKLMNO']:
            if column in sigs:
                sigs = sigs.replace(column, '')
                yield column
        yield None

    # needs to work with strings and iterables
    sigs = ''.join(str(l) for l in code or '').upper()

    # get a first possible row (caveat: recognize double-digit numbers)
    all_rows = [x for x in row_generator()]
    rows = (x for x in reversed(all_rows))
    # get the first possible column -> NI, NL, A...O
    columns = column_generator()
    return (next(columns) or 'O', next(rows) or 15)


# ribbon routines

@lru_cache(maxsize=350)
def parse_record(input_data):
    """Parses the record and gets its row, column and justification codes.
    First split the input data into two parts:
    -the Monotype signals (unprocessed),
    -any comments delimited by symbols from COMMENT_SYMBOLS list.

    Looks for any comment symbols defined here - **, *, ##, #, // etc.
    splits the line at it and saves the comment to return it later on.
    If it's an inline comment (placed after Monotype code combination),
    this combination will be returned for casting."""
    def split_on_delimiter(sequence):
        """Iterate over known comment delimiter symbols to find
        whether a record has a comment; split on that delimiter
        and normalize the signals"""
        source = ''.join(str(x) for x in sequence)
        for symbol in COMMENT_SYMBOLS:
            if symbol in source:
                # Split on the first encountered symbol
                raw_signals, comment = source.split(symbol, 1)
                break
        else:
            # no comment symbol encountered, so we only have signals
            raw_signals, comment = source, ''

        return raw_signals.upper().strip(), comment.strip()

    def is_present(value):
        """Detect and dispatch known signals in source string"""
        nonlocal signals
        found = False
        string = str(value)
        if string in signals:
            signals = signals.replace(string, '')
            found = True
        return found

    def analyze():
        """Check if signals perform certain functions"""
        has_signals = any((columns, rows, justification))
        column = (None if not has_signals
                  else 'NI' if set('NI').issubset(columns)
                  else 'NL' if set('NL').issubset(columns)
                  else columns[0] if columns else 'O')
        row = None if not has_signals else rows[0] if rows else 15
        has_0005 = '0005' in justification or set('NJ').issubset(columns)
        has_0075 = '0075' in justification or set('NK').issubset(columns)
        uses_row_16 = row == 16
        is_pump_start = has_0075
        is_pump_stop = has_0005 and not has_0075
        is_newline = has_0005 and has_0075
        is_char = not justification
        has_s_needle = 'S' in signals

        return dict(has_signals=has_signals, column=column, row=row,
                    has_0005=has_0005, has_0075=has_0075, is_char=is_char,
                    is_newline=is_newline, uses_row_16=uses_row_16,
                    is_pump_start=is_pump_start, is_pump_stop=is_pump_stop,
                    has_s_needle=has_s_needle)

    # we know signals and comment right away
    raw_signals, comment = split_on_delimiter(input_data)
    signals = raw_signals

    # read the signals to know what's inside
    justification = tuple(x for x in ('0075', '0005') if is_present(x))
    parsed_rows = [x for x in range(16, 0, -1) if is_present(x)]
    rows = tuple(x for x in reversed(parsed_rows))
    columns = tuple(x for x in [*'ABCDEFGHIJKLMNO'] if is_present(x))

    return ParsedRecord(signals=raw_signals, comment=comment,
                        raw=input_data, **analyze())


@lru_cache(maxsize=350)
def parse_signals(input_signals, row16_mode):
    """Prepare the incoming signals for casting, testing or punching."""
    def strip_16():
        """Get rid of the "16" signal and replace it with "15"."""
        if '16' in parsed_signals:
            parsed_signals.discard('16')
            parsed_signals.add('15')

    def convert_hmn():
        """HMN addressing mode - developed by Monotype, based on KMN.
        Uncommon."""
        # NI, NL, M -> add H -> HNI, HNL, HM
        # H -> add N -> HN
        # N -> add M -> MN
        # O -> add HMN
        # {ABCDEFGIJKL} -> add HM -> HM{ABCDEFGIJKL}

        # earlier rows than 16 won't trigger the attachment -> early return
        for i in range(1, 16):
            if str(i) in parsed_signals:
                return

        columns = 'NI', 'NL', 'H', 'M', 'N', 'O'
        extras = 'H', 'H', 'N', 'H', 'M', 'HMN'
        if '16' in parsed_signals:
            parsed_signals.discard('16')
            for column, extra in zip(columns, extras):
                if parsed_signals.issuperset(column):
                    parsed_signals.update(extra)
                    return
            parsed_signals.update('HM')

    def convert_kmn():
        """KMN addressing mode - invented by a British printshop.
        Very uncommon."""
        # NI, NL, M -> add K -> KNI, KNL, KM
        # K -> add N -> KN
        # N -> add M -> MN
        # O -> add KMN
        # {ABCDEFGHIJL} -> add KM -> KM{ABCDEFGHIJL}

        # earlier rows than 16 won't trigger the attachment -> early return
        for i in range(1, 16):
            if str(i) in parsed_signals:
                return

        columns = 'NI', 'NL', 'K', 'M', 'N', 'O'
        extras = 'K', 'K', 'N', 'K', 'M', 'HMN'
        if '16' in parsed_signals:
            parsed_signals.discard('16')
            for column, extra in zip(columns, extras):
                if parsed_signals.issuperset(column):
                    parsed_signals.update(extra)
                    return
            parsed_signals.update('KM')

    def convert_unitshift():
        """Unit-shift addressing mode - rather common,
        designed by Monotype and introduced in 1963"""
        if 'D' in parsed_signals:
            # when the attachment is on, the D signal is routed
            # to unit-shift activation piston instead of column D air pin
            # this pin is activated by EF combination instead
            parsed_signals.discard('D')
            parsed_signals.update('EF')
        if '16' in parsed_signals:
            # use unit shift if the row signal is 16
            # make it possible to shift the diecase on earlier rows
            parsed_signals.update('D')
            parsed_signals.discard('16')

    def formatted_output():
        """Arrange the signals so that NI, NL will be present at the
        beginning of the signals collection"""
        arranged = deque(s for s in OUTPUT_SIGNALS if s in parsed_signals)
        # put NI, NL, NK, NJ, NKJ etc. at the front
        if 'N' in arranged:
            for other in 'JKLI':
                if other in parsed_signals:
                    arranged.remove('N')
                    arranged.remove(other)
                    arranged.appendleft(other)
                    arranged.appendleft('N')
        return list(arranged)

    try:
        source = input_signals.upper()
    except AttributeError:
        source = ''.join(str(x) for x in input_signals).upper()

    valid_signals = ['0005', '0075', *(str(x) for x in range(16, 0, -1)),
                     *'ABCDEFGHIJKLMNOS']

    parsed_signals = set()
    for signal in valid_signals:
        if signal in source:
            source.replace(signal, '')
            parsed_signals.add(signal)

    # based on row 16 addressing mode,
    # decide which signal conversion should be applied
    if row16_mode == 'HMN':
        convert_hmn()
    elif row16_mode == 'KMN':
        convert_kmn()
    elif row16_mode == 'unit shift':
        convert_unitshift()
    else:
        strip_16()
    # all ready for sending
    return formatted_output()


def parse_ribbon(ribbon):
    """Get the metadata and contents out of a sequence of lines"""
    def get_value(line, symbol):
        """Helper function - strips whitespace and symbols"""
        # Split the line on an assignment symbol, get the second part,
        # strip any whitespace or multipled symbols
        return line.split(symbol, 1)[-1].strip(symbol).strip()

    # What to look for
    keywords = ['diecase', 'diecase_id', 'description', 'desc',
                'wedge', 'stopbar', 'wedge_name']
    targets = ['diecase', 'diecase_id', 'description', 'description',
               'wedge', 'wedge', 'wedge']
    parameters = dict(zip(keywords, targets))
    # Metadata (anything found), contents (the rest)
    metadata = {}
    contents = []
    # Look for parameters line per line, get parameter value
    # If parameters exhausted, append the line to contents
    for line in ribbon:
        if not str(line).strip():
            # omit empty lines
            continue
        for keyword, target in parameters.items():
            if line.startswith(keyword):
                for sym in ASSIGNMENT_SYMBOLS:
                    if sym in line:
                        # Data found
                        metadata[target] = get_value(line, sym)
                        break
                # don't test for further keywords on that line
                break
        else:
            # non-empty line without metadata = useful codes
            contents.append(line)
    return Ribbon(*metadata, contents=contents)


def make_mat(code='', units=0, wedge=None):
    """Define a matrix (coordinates, unit width).
    Returns Matrix together with justifying wedge positions.
    """
    normal_wedge = wedge or Wedge()
    column, row = parse_coordinates(code)
    row_units = normal_wedge[row]
    unit_width = units or row_units
    # calculate the 0075 / 0005 wedge corrections
    wedges = normal_wedge.corrections(row, unit_width)
    if wedges != (3, 8):
        # use S needle because adjustments are needed
        mat_code = '{} S {}'.format(column, row)
    else:
        # no S-needle nor unit correction
        mat_code = '{} {}'.format(column, row)
    return Matrix(column, row, unit_width, row_units, mat_code, wedges)


def make_order(source, wedge=None, chunk_size=5):
    """Make a galley of type separated by spaces and quads"""
    normal_wedge = wedge or Wedge()
    quad = make_mat('O15', units=0, wedge=normal_wedge)
    order = []
    for mat, quantity in source:
        # chunks of specified size separated with quads
        num_chunks = quantity // chunk_size
        last_chunk_size = quantity % chunk_size
        chunk = [mat] * chunk_size
        last_chunk = [mat] * last_chunk_size
        if num_chunks > 0:
            order.extend([*chunk, quad] * (num_chunks - 1))
            order.extend([*chunk, *last_chunk, quad])
        elif last_chunk:
            # just that tiny bit
            order.extend([*last_chunk, quad])
    return order


def make_galley(queue, galley_units, wedge=None):
    """Iterate over the queue in order to transform all the items
    to Monotype codes."""
    def start_line():
        """Start a new line"""
        nonlocal units_left
        units_left = galley_units
        ribbon.append(quad.code)

    def end_line():
        """Fill the line with quads and add a variable space
        in order to get the length equal (for tying the type)."""
        num_quads = int(units_left // quad.units + 1)
        # space width: the remainder from dividing units left by 18
        # (or whatever the quad unit width is), in units
        space_units = units_left % quad.units
        # choose a matrix for the space
        space_position = 'G2' if 5 <= space_units < 16 else 'O15'
        # make a quad wider and use it as a space
        if space_units < 5:
            num_quads -= 1
            space_units += quad.units
        space = make_mat(space_position, space_units, normal_wedge)
        # use single justification to set the character width
        if wedges != (3, 8) and space.wedges not in (wedges, (3, 8)):
            ribbon.extend(single_justification(wedges))
        # add a space to get the width equal
        ribbon.append(space.code)
        # fill in with quads
        ribbon.extend([quad.code] * num_quads)
        ribbon.extend(double_justification(space.wedges))

    # use a default wedge if not specified
    normal_wedge = wedge or Wedge()
    # initialize a ribbon with line out and pump stop
    # no justification here
    ribbon = [*pump_stop(), *double_justification()]
    quad = make_mat('O15', wedge=normal_wedge)
    galley_units -= 2 * quad.units
    # store the justifying wedge positions
    wedges = (3, 8)

    start_line()
    # a list of (n, n+1) pairs of matrices for next char prediction
    pairs = zip(queue, [*queue[1:], None])
    for curr_mat, next_mat in pairs:
        # add a mat to the sequence and update the units count
        ribbon.append(curr_mat.code)
        # update the justifying wedge positions only when the character
        # is wider or narrower than wedge[row] i.e. uses S-needle
        if curr_mat.wedges != (3, 8):
            wedges = curr_mat.wedges
        units_left -= curr_mat.units
        if not next_mat:
            # all matrices done; fill the line
            end_line()
            break

        # predict if we can put the next sort into the line;
        # if that's not the case, fill and start a new one
        elif next_mat.units > units_left:
            end_line()
            start_line()

        elif wedges != (3, 8) and next_mat.wedges not in (wedges, (3, 8)):
            # next character will fit in (next iteration)
            # check if we need to change the justification wedges
            ribbon.extend(single_justification(wedges))

    return ribbon

# caster control combinations


def single_justification(wedges=(15, 15)):
    """0075 then 0005 (will be cast in reverse order)
    with justifying wedge positions.
    NB if positions are the same, mere 0075+pos is enough;
    if positions are 3, 8 - then no codes needed"""
    w_0075, w_0005 = wedges
    return ([] if (w_0075, w_0005) == (3, 8)
            else ['NKS 0075 {}'.format(w_0005)] if w_0075 == w_0005
            else ['NKS 0075 {}'.format(w_0075), 'NJS 0005 {}'.format(w_0005)])


def double_justification(wedges=(15, 15)):
    """0075 then 0005+0075 (will be cast in reverse order)
    with or without justifying wedge positions.
    Used for putting a line to the galley, setting the wedges as well.
    """
    w_0075, w_0005 = wedges
    return (['NKJS 0075 0005 {}'.format(w_0005)] if w_0075 == w_0005
            else ['NKS 0075 {}'.format(w_0075),
                  'NKJS 0075 0005 {}'.format(w_0005)])


def pump_stop():
    """Double 0005 to stop the pump."""
    return ['NJS 0005', 'NJS 0005']


def pump_start():
    """0075 to start the pump."""
    return ['NKS 0075']
