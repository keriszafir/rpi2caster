"""texlib.wrap

Implements TeX's algorithm for breaking paragraphs into lines.

This module provides a straightforward implementation of the algorithm
used by TeX to format paragraphs.  The algorithm uses dynamic
programming to find a globally optimal division into lines, enabling
it to produce more attractive results than a first-fit or best-fit
algorithm can.  For a full description, see the reference.

The module provides the ObjectList class, which is a list of Box,
Glue, and Penalty instances.  The elements making up a paragraph of
text should be assembled into a single ObjectList.  Boxes represent
characters of type, and their only attribute is width.  Glue
represents a space of variable size; in addition to a preferred width,
glue can also stretch and shrink, to an amount that's specified by the
user.  Penalties are used to encourage or discourage breaking a line
at a given point.  Positive values discourage line breaks at a given
point, and a value of INFINITY forbids breaking the line at the
penalty.  Negative penalty values encourage line breaks at a given
point, and a value of -INFINITY forces a line break at a particular
point.

The compute_breakpoints() method of ObjectList returns a list of
integers containing the indexes at which the paragraph should be
broken.  If you're setting the text to be ragged-right (or
ragged-left, I suppose), then simply loop over the text and insert
breaks at the appropriate points.  For full justification, you'll have
to loop over each line's contents, calculate its adjustment ratio by
calling compute_adjustment_ratio(), and for each bit of glue, call its
compute_width() method to figure out how long this dab of glue should
be.

Reference:
    "Breaking Paragraphs into Lines", D.E. Knuth and M.F. Plass,
    chapter 3 of _Digital Typography_, CSLI Lecture Notes #78.

This software is available under the MIT license.

Copyright (c) 2010, A.M. Kuchling

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom
the Software is furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included
  in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH
THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import sys

INFINITY = 1000

# Three classes defining the three different types of object that
# can go into an ObjectList.


class Box:
    """Class representing a glyph or character.  Boxes have a fixed
    width that doesn't change.
    """

    def __init__(self, b_width, character=None):
        self.character = character
        self.width = b_width
        self.stretch = 0
        self.shrink = 0
        self.penalty = 0
        self.flagged = 0
        self.is_glue = False
        self.is_box = True
        self.is_penalty = False
        self.is_forced_break = False


class Glue:
    """Class representing a bit of glue.  Glue has a preferred width,
    but it can stretch up to an additional distance, and can shrink
    by a certain amount.  Line breaks can be placed at any point where
    glue immediately follows a box.
    """

    def __init__(self, width, shrink, stretch):
        self.width, self.stretch, self.shrink = width, stretch, shrink
        self.is_glue = True
        self.is_box = False
        self.is_penalty = False
        self.is_forced_break = False

    def compute_width(self, ratio):
        """Return how long this glue should be, for the given adjustment
        ratio r."""
        if ratio < 0:
            return self.width + ratio * self.shrink
        else:
            return self.width + ratio * self.stretch


class Penalty:
    """Class representing a penalty.  Negative penalty values
    encourage line breaks at a given point, and positive values
    discourage breaks.  A value of INFINITY either absolutely requires
    or forbids a break.  Penalties have a width of zero unless a break
    is taken at the penalty point, at which point the value of the
    penalty's 'width' attribute is used.

    """

    def __init__(self, width, penalty, flagged=0):
        self.width = width
        self.penalty = penalty
        self.flagged = flagged
        self.stretch = self.shrink = 0
        self.is_glue = False
        self.is_box = False
        self.is_penalty = True
        self.is_forced_break = self.penalty == INFINITY


class _BreakNode:
    "Internal class representing an active breakpoint."

    def __init__(self, position, line, fitness_class,
                 totalwidth, totalstretch, totalshrink,
                 demerits, previous=None):
        self.position, self.line = position, line
        self.fitness_class = fitness_class
        self.totalwidth, self.totalstretch = totalwidth, totalstretch
        self.totalshrink, self.demerits = totalshrink, demerits
        self.previous = previous

    def __repr__(self):
        return '<_BreakNode at %i>' % self.position


class ObjectList(list):

    """Class representing a list of Box, Glue, and Penalty objects.
    Supports the same methods as regular Python lists.
    """
    # Set this to 1 to trace the execution of the algorithm.
    debug = 0

    def __init__(self):
        super().__init__()
        self.sum_width, self.sum_stretch, self.sum_shrink = {}, {}, {}

    def add_closing_penalty(self):
        "Add the standard glue and penalty for the end of a paragraph"
        self.append(Penalty(0, INFINITY, 0))
        self.append(Glue(0, 0, INFINITY))
        self.append(Penalty(0, -INFINITY, 1))

    def is_feasible_breakpoint(self, i):
        "Return true if position 'i' is a feasible breakpoint."
        box = self[i]
        if box.is_penalty and box.penalty < INFINITY:
            return 1
        elif i > 0 and box.is_glue and self[i-1].is_box:
            return 1
        else:
            return 0

    def is_forced_break(self, i):
        "Return true if position 'i' is a forced breakpoint."
        box = self[i]
        if box.is_penalty and box.penalty == -INFINITY:
            return 1
        else:
            return 0

    def measure_width(self, pos1, pos2):
        "Add up the widths between positions 1 and 2"

        return self.sum_width[pos2] - self.sum_width[pos1]

    def measure_stretch(self, pos1, pos2):
        "Add up the stretch between positions 1 and 2"

        return self.sum_stretch[pos2] - self.sum_stretch[pos1]

    def measure_shrink(self, pos1, pos2):
        "Add up the shrink between positions 1 and 2"
        return self.sum_shrink[pos2] - self.sum_shrink[pos1]

    def compute_adjustment_ratio(self, pos1, pos2, line, line_lengths):
        "Compute adjustment ratio for the line between pos1 and pos2"
        length = self.measure_width(pos1, pos2)
        if self[pos2].is_penalty:
            length = length + self[pos2].width
        if self.debug:
            print('\tline length=', length)

        # Get the length of the current line; if the line_lengths list
        # is too short, the last value is always used for subsequent
        # lines.

        if line < len(line_lengths):
            available_length = line_lengths[line]
        else:
            available_length = line_lengths[-1]

        # Compute how much the contents of the line would have to be
        # stretched or shrunk to fit into the available space.
        if length < available_length:
            stretch = self.measure_stretch(pos1, pos2)
            if self.debug:
                print('\tLine too short: shortfall = %i, stretch = %i'
                      % (available_length - length, stretch))
            if stretch > 0:
                ratio = (available_length - length) / float(stretch)
            else:
                ratio = INFINITY

        elif length > available_length:
            shrink = self.measure_shrink(pos1, pos2)
            if self.debug:
                print('\tLine too long: extra = %s, shrink = %s'
                      % (available_length - length, shrink))
            if shrink > 0:
                ratio = (available_length - length) / float(shrink)
            else:
                ratio = INFINITY
        else:
            # Exactly the right length!
            ratio = 0

        return ratio

    def add_active_node(self, active_nodes, node):
        """Add a node to the active node list.
        The node is added so that the list of active nodes is always
        sorted by line number, and so that the set of (position, line,
        fitness_class) tuples has no repeated values.
        """
        index = 0
        # Find the first index at which the active node's line number
        # is equal to or greater than the line for 'node'.  This gives
        # us the insertion point.
        while (index < len(active_nodes) and
               active_nodes[index].line < node.line):
            index = index + 1
        insert_index = index
        # Check if there's a node with the same line number and
        # position and fitness.  This lets us ensure that the list of
        # active nodes always has unique (line, position, fitness)
        # values.
        while (index < len(active_nodes) and
               active_nodes[index].line == node.line):
            if (active_nodes[index].fitness_class == node.fitness_class and
                    active_nodes[index].position == node.position):
                # A match, so just return without adding the node
                return
            index += 1
        active_nodes.insert(insert_index, node)

    def compute_breakpoints(self, line_lengths, looseness=0, tolerance=1,
                            fitness_demerit=100, flagged_demerit=100):
        """Compute a list of optimal breakpoints for the paragraph
        represented by this ObjectList, returning them as a list of
        integers, each one the index of a breakpoint.

        line_lengths : a list of integers giving the lengths of each
                       line.  The last element of the list is reused
                       for subsequent lines.
        looseness : An integer value. If it's positive, the paragraph
                   will be set to take that many lines more than the
                   optimum value.   If it's negative, the paragraph is
                   set as tightly as possible.  Defaults to zero,
                   meaning the optimal length for the paragraph.
        tolerance : the maximum adjustment ratio allowed for a line.
                    Defaults to 1.
        fitness_demerit : additional value added to the demerit score
                          when two consecutive lines are in different
                          fitness classes.
        flagged_demerit : additional value added to the demerit score
                          when breaking at the second of two flagged
                          penalties.
        """
        length = len(self)
        if not len(self):
            return []            # No text, so no breaks

        # Precompute lists containing the numeric values for each box.
        # The variable names follow those in Knuth's description.
        widths, stretches, shrinks = [0] * length, [0] * length, [0] * length
        penalties, flags = [0] * length, [0] * length
        for i in range(length):
            box = self[i]
            widths[i] = box.width
            if box.is_glue:
                stretches[i] = box.stretch
                shrinks[i] = box.shrink
            elif box.is_penalty:
                penalties[i] = box.penalty
                flags[i] = box.flagged

        # Precompute the running sums of width, stretch, and shrink
        # (W,Y,Z in the original paper).  These make it easy to measure the
        # width/stretch/shrink between two indexes; just compute
        # sum_*[pos2] - sum_*[pos1].  Note that sum_*[i] is the total
        # up to but not including the box at position i.
        width_sum = stretch_sum = shrink_sum = 0
        for i in range(length):
            self.sum_width[i] = width_sum
            self.sum_stretch[i] = stretch_sum
            self.sum_shrink[i] = shrink_sum

            box = self[i]
            width_sum += box.width
            stretch_sum += box.stretch
            shrink_sum += box.shrink

        # Initialize list of active nodes to a single break at the
        # beginning of the text.
        a_node = _BreakNode(position=0, line=0, fitness_class=1,
                            totalwidth=0, totalstretch=0,
                            totalshrink=0, demerits=0)
        active_nodes = [a_node]
        for i in range(length):
            breakpoint = self[i]
            # Determine if this box is a feasible breakpoint and
            # perform the main loop if it is.
            if self.is_feasible_breakpoint(i):
                # Loop over the list of active nodes, and compute the fitness
                # of the line formed by breaking at A and B.  The resulting
                breaks = []                 # List of feasible breaks
                for a_node in active_nodes[:]:
                    ratio = self.compute_adjustment_ratio(a_node.position, i,
                                                          a_node.line,
                                                          line_lengths)
                    # XXX is 'or' really correct here?  This seems to
                    # remove all active nodes on encountering a forced break!
                    if ratio < -1 or breakpoint.is_forced_break:
                        # Deactivate node A
                        if len(active_nodes) == 1:
                            if self.debug:
                                print("Can't remove last node!")
                                # XXX how should this be handled?
                                # Raise an exception?
                        else:
                            active_nodes.remove(a_node)

                    if -1 <= ratio <= tolerance:
                        # Compute demerits and fitness class
                        if penalties[i] >= 0:
                            demerits = (1 + 100 * abs(ratio)**3 +
                                        penalties[i]) ** 3
                        elif self.is_forced_break(i):
                            demerits = ((1 + 100 * abs(ratio)**3) ** 2 -
                                        penalties[i]**2)
                        else:
                            demerits = (1 + 100 * abs(ratio)**3) ** 2
                        demerits += (flagged_demerit * flags[i] *
                                     flags[a_node.position])
                        # Figure out the fitness class of this line
                        # (tight, loose, very tight or very loose).
                        if ratio < -.5:
                            fitness_class = 0
                        elif ratio <= .5:
                            fitness_class = 1
                        elif ratio <= 1:
                            fitness_class = 2
                        else:
                            fitness_class = 3
                        # If two consecutive lines are in very
                        # different fitness classes, add to the
                        # demerit score for this break.
                        if abs(fitness_class - a_node.fitness_class) > 1:
                            demerits += fitness_demerit
                        # Record a feasible break from A to B
                        brk = _BreakNode(position=i, line=a_node.line + 1,
                                         fitness_class=fitness_class,
                                         totalwidth=self.sum_width[i],
                                         totalstretch=self.sum_stretch[i],
                                         totalshrink=self.sum_shrink[i],
                                         demerits=demerits,
                                         previous=a_node)
                        breaks.append(brk)
                for brk in breaks:
                    self.add_active_node(active_nodes, brk)
        # Find the active node with the lowest number of demerits.
        a_node = min(active_nodes, key=lambda a_node: a_node.demerits)
        if looseness:
            # The search for the appropriate active node is a bit more
            # complicated; we look for a node with a paragraph length
            # that's as close as possible to (A.line+looseness), and
            # with the minimum number of demerits.
            best = 0
            demerits = INFINITY
            for node in active_nodes:
                delta = node.line - a_node.line
                # The two branches of this 'if' statement
                # are for handling values of looseness that are
                # either positive or negative.
                if looseness <= delta < best or best < delta < looseness:
                    # s = delta
                    demerits = node.demerits
                    breaking_node = node
                elif delta == best and node.demerits < demerits:
                    # This break is of the same length, but has fewer
                    # demerits and hence is a more attractive one.
                    demerits = node.demerits
                    breaking_node = node
            a_node = breaking_node
        # Use the chosen node A to determine the optimum breakpoints,
        # and return the resulting list of breakpoints.
        breaks = []
        while a_node is not None:
            breaks.append(a_node.position)
            a_node = a_node.previous
        breaks.reverse()
        return breaks


# Simple test code.
def main():
    """Test it"""
    text = """Writing this summary was difficult, because there were no large
    themes in the last two weeks of discussion.  Instead there were lots
    and lots of small items; as the release date for 2.0b1 nears, people are
    concentrating on resolving outstanding patches, fixing bugs, and
    making last-minute tweaks.
    Computes a Adler-32 checksum of string.  (An Adler-32
    checksum is almost as reliable as a CRC32 but can be computed much
    more quickly.)  If value is present, it is used as the
    starting value of the checksum; otherwise, a fixed default value is
    used.  This allows computing a running checksum over the
    concatenation of several input strings.  The algorithm is not
    cryptographically strong, and should not be used for
    authentication or digital signatures."""
    text = ' '.join(text.split())

    line_width = 100   # Line width to use for formatting
    full_justify = True   # Boolean; if true, do full justification
    # Turn chunk of text into an ObjectList.
    obj_list = ObjectList()
    for character in text:
        if character in ' \n':
            # Append interword space -- 2 units +/- 1
            obj_list.append(Glue(3, 2, 10))
        elif character == '@':
            # Append forced break
            obj_list.append(Penalty(0, -INFINITY))

        else:
            # All characters are 1 unit wide
            obj_list.append(Box(1, character))

    # Append closing penalty and glue
    obj_list.add_closing_penalty()

    # Compute the breakpoints
    line_lengths = [line_width]
    # line_lengths = range(120, 20, -10)
    breaks = obj_list.compute_breakpoints(line_lengths, tolerance=2)

    assert breaks[0] == 0
    line_start = 0
    line_no = 0
    for breakpoint in breaks[1:]:
        adj_ratio = obj_list.compute_adjustment_ratio(line_start, breakpoint,
                                                      line_no, line_lengths)
        line_no += 1
        for i in range(line_start, breakpoint):
            box = obj_list[i]
            if box.is_glue:
                if full_justify:
                    box_width = int(box.compute_width(adj_ratio))
                else:
                    box_width = 1
                sys.stdout.write(' ' * box_width)

            elif hasattr(box, 'character'):
                sys.stdout.write(box.character)
        line_start = breakpoint + 1
        sys.stdout.write('\n')

if __name__ == '__main__':
    main()
