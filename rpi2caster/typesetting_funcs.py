# -*- coding: utf-8 -*-
"""
typesetting_functions:

Contains functions used for calculating line length, justification,
setting wedge positions, breaking the line etc.
"""
from collections import deque
from . import exceptions as e
from .justification import Box, Glue, Penalty, ObjectList
from .measure import Measure
from .global_config import UI
from .matrix_data import Diecase, Matrix

STYLES = {'^00': 'r', '^01': 'b', '^02': 'i',
          '^03': 's', '^04': 'l', '^05': 'u',
          '^RR': 'r', '^BB': 'b', '^II': 'i',
          '^SS': 's', '^LL': 'l', '^UU': 'u'}
ALIGNMENT = {'^CR': 'left', '^CC': 'center', '^CL': 'right', '^CF': 'both'}


class InputData(object):
    """Gets the input text, parses it, generates a sequence of characters
    or commands"""
    def __init__(self, text, context):
        self.context = context
        self.text = text

    def parse_input(self, input_text):
        """Generates a sequence of characters from the input text.
        For each character, this function predicts what two next characters
        and one next character are."""
        # This variable will prevent yielding a number of subsequent chars
        # after a ligature or command has been found and yielded.
        skip_steps = 0
        # Default style is roman
        style = 'r'
        # Characters which will be skipped
        ignored = ('\n',)
        # Determine the length of character combinations parsed
        max_len = max((len(mat.char) for mat in self.context.diecase) +
                      (len(x) for x in ignored) +
                      (len(x) for x in STYLES) +
                      (len(x) for x in ALIGNMENT))
        # Build a dict of matrices
        mats = {(mat.char, mat.styles): mat for mat in self.context.diecase}
        # What if char in text not present in diecase? Hmmm...
        for index, _ in enumerate(input_text):
            if skip_steps:
                # Skip the characters to be skipped
                skip_steps -= 1
                continue
            for i in range(max_len, 0, -1):
                # Start from longest, end with shortest
                try:
                    char = input_text[index:index+i]
                    skip_steps = i - 1
                    if char in ignored:
                        continue
                    elif char in ALIGNMENT:
                        alignment = ALIGNMENT.get(char, 'both')
                        yield Justify(alignment)
                    elif char in STYLES:
                        # Change the current style
                        style = STYLES.get(char, 'r')
                    else:
                        # Try to look it up in spaces
                        yield mats.get((char, style))
                        # End on first (largest) combination found
                        break
                except (TypeError, AttributeError, ValueError):
                    pass


class Justify(object):
    """Justification class"""
    def __init__(self, method='both'):
        pass


class Line(deque):
    """A line of type, justified to the left, center,right or both."""
    def __init__(self, length):
        super().__init__()
        self.length = length

    def __add__(self, new):
        if isinstance(new, Matrix):
            self.append(new)
        elif isinstance(new, (int, float)):
            self.length += new
        elif isinstance(new, (tuple, list, iter)):
            self.extend([x for x in new])

    def __radd__(self, new):
        if isinstance(new, Matrix):
            self.appendleft(new)
        elif isinstance(new, (int, float)):
            self.length += new
        elif isinstance(new, (tuple, list, iter)):
            self.extendleft([x for x in new])

    def render(self):
        """Renders a line into a series of Matrix objects with appropriate
        widths, and justified spaces."""
        # TODO
        pass

    def _align_left(self):
        """Aligns the previous chunk to the left."""
        pass

    def _align_right(self):
        """Aligns the previous chunk to the right."""
        pass

    def _align_center(self):
        """Aligns the previous chunk to the center."""
        pass

    def _align_both(self):
        """Aligns the previous chunk to both edges and ends the line."""
        pass


class Paragraph(object):
    """A page is broken into a series of paragraphs."""
    def __init__(self, width, style, indent, justification):
        self.width = width
        self.style = style
        self.indent = indent
        self.justification = justification

    def __iter__(self):
        return (x for x in self.nodes)

    def render(self):
        """Render all lines into combinations of Monotype codes"""
        pass

    @property
    def nodes(self):
        """Nodes are all characters, including ligatures, spaces
        and line-breaks"""
        return (node for line in self.lines for node in line)

    @property
    def lines(self):
        """Paragraph's lines"""
        return (line for line in self.lines)


class Page(object):
    """A page is a collection of paragraphs"""
    def __init__(self, width, height):
        self.width = width
        self.height = height


class GalleyBuilder(object):
    """Builds a galley from input sequence"""
    def __init__(self, source, diecase=None, measure=Measure(manual=False)):
        self.source = (x for x in source)
        self.points = measure.points
        self.diecase = diecase or Diecase()
        self.cooldown = False
        self.mould_heatup = True
        self.quad_padding = 1

    def preheat_mould(self):
        """Appends two lines of em-quads at the end"""
        chunk = []
        if self.mould_heatup:
            quad = self.diecase.decode_matrix('O15')
            quad_qty = int(self.points // quad.points)
            chunk = ['%s preheat' % quad] * quad_qty
            comment = 'Casting quads for mould heatup'
            chunk.extend(double_justification(comment=comment))
        return chunk * 2

    def make_ribbon(self):
        """Instantiates a Ribbon() object from whatever we've generated"""
        pass

    def build_galley(self):
        """Builds a line of characters from source"""
        def decode_mat(mat):
            """Gets the mat's parameters and stores them
            to avoid recalculation"""
            parameters = {}
            if mat:
                parameters['wedges'] = mat.wedge_positions()
                parameters['points'] = mat.points
                parameters['code'] = str(mat)
                parameters['lowspace'] = mat.islowspace()
            return parameters

        def start_line():
            """Starts a new line"""
            nonlocal points_left, queue
            points_left = self.points - 2 * self.quad_padding * quad['points']
            quads = [quad['code'] + ' quad padding'] * self.quad_padding
            queue.extend(quads)

        def build_line():
            """Puts the matrix in the queue, changing the justification
            wedges if needed, and adding a space for cooldown, if needed."""
            # Declare variables in non-local scope to preserve them
            # after the function exits
            nonlocal queue, points_left, working_mat, current_wedges
            # Take a mat from stash if there is any
            working_mat = working_mat or decode_mat(next(self.source, None))
            # Try to add another character to the line
            # Empty mat = end of line, start filling
            if points_left > working_mat.get('points', 1000):
                # Store wedge positions
                new_wedges = working_mat.get('wedges', (3, 8))
                # Wedges change? Drop in some single justification
                # (not needed if wedge positions were 3, 8)
                if current_wedges != new_wedges:
                    if current_wedges and current_wedges != (3, 8):
                        queue.extend(single_justification(current_wedges))
                    current_wedges = new_wedges
                # Add the mat
                queue.append(working_mat['code'])
                points_left -= working_mat['points']
                # We need to know what comes next
                working_mat = decode_mat(next(self.source, None))
                if working_mat:
                    next_points = space['points'] + working_mat['points']
                    space_needed = (points_left > next_points and not
                                    working_mat.get('lowspace', True))
                    if self.cooldown and space_needed:
                        # Add a space for matrix cooldown
                        queue.append(space['code'] + ' for cooldown')
                        points_left -= space['points']
                    # Exit and loop further
                    return
            # Finish the line
            var_sp = self.diecase.decode_matrix('G1')
            wedges = current_wedges
            current_wedges = None
            while points_left > quad['points']:
                # Coarse fill with quads
                queue.append(quad['code'] + ' coarse filling line')
                points_left -= quad['points']
            while points_left > space['points'] * 2:
                # Fine fill with fixed spaces
                queue.append(space['code'] + ' fine filling line')
                points_left -= space['points']
            if points_left >= var_sp.get_min_points():
                # Put an adjustable space if possible to keep lines equal
                if wedges:
                    queue.extend(single_justification(wedges))
                var_sp.points = points_left
                queue.append(str(var_sp))
                wedges = var_sp.wedge_positions()
            # Always cast as many quads as needed, then put the line out
            queue.extend([quad['code'] + ' quad padding'] * self.quad_padding)
            queue.extend(double_justification(wedges or (3, 8)))
            points_left = 0

        # Store the code and wedge positions to speed up the process
        space = decode_mat(self.diecase.decode_matrix('G1'))
        quad = decode_mat(self.diecase.decode_matrix('O15'))
        working_mat = None
        current_wedges = None
        queue, points_left = end_casting(), 0
        # Build the whole galley, line by line
        while working_mat != {}:
            start_line()
            while points_left > 0:
                build_line()
        return queue + self.preheat_mould()


def single_justification(wedge_positions=(3, 8),
                         comment='Single justification'):
    """Add 0075 + pos_0075, then 0005 + pos_0005"""
    (pos_0075, pos_0005) = wedge_positions
    return pump_start(pos_0075, comment) + pump_stop(pos_0005)


def double_justification(wedge_positions=(3, 8),
                         comment='Double justification'):
    """Add 0075 + pos_0075, then 0005-0075 + pos_0005"""
    (pos_0075, pos_0005) = wedge_positions
    return pump_start(pos_0075, comment) + galley_trip(pos_0005)


def galley_trip(pos_0005=8, comment='Line to the galley'):
    """Put the line to the galley"""
    attach = comment and (' // ' + comment) or ''
    return ['NKJS 0075 0005 %s%s' % (pos_0005, attach)]


def pump_start(pos_0075=3, comment='Starting the pump'):
    """Start the pump and set 0075 wedge"""
    attach = comment and (' // ' + comment) or ''
    return ['NKS 0075 %s%s' % (pos_0075, attach)]


def pump_stop(pos_0005=8, comment='Stopping the pump'):
    """Stop the pump"""
    attach = comment and (' // ' + comment) or ''
    return ['NJS 0005 %s%s' % (pos_0005, attach)]


def end_casting():
    """Alias for ending the casting job"""
    return (pump_stop(comment='End casting') +
            galley_trip(comment='Last line out'))


def high_or_low_space():
    """Chooses high or low space"""
    spaces = {True: '_', False: ' '}
    high_or_low = UI.confirm('High space?', default=False)
    return spaces[high_or_low]
