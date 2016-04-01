# -*- coding: utf-8 -*-
"""Style manager"""
from .global_settings import UI


# Styles definitions
STYLES_ORDER = [x for x in 'rbislu']
STYLES_NAMES = ['roman', 'bold', 'italic', 'smallcaps', 'inferior', 'superior']
STYLES = dict(zip(STYLES_ORDER, STYLES_NAMES))


class Styles(object):
    """Manage styles"""
    def __init__(self, styles_string=None, allow_multiple=True):
        self.styles_list = []
        self.allow_multiple = allow_multiple
        if styles_string is None:
            self.styles_string = 'r'
            self.choose()
        elif styles_string:
            self.styles_string = styles_string
        else:
            # Setting an empty style will set all'
            self.styles_list = STYLES_ORDER

    def __iter__(self):
        return (x for x in self.styles_list)

    def __str__(self):
        if self.styles_list == STYLES_ORDER:
            return 'all'
        else:
            return ', '.join(self.values())

    def __repr__(self):
        return ''.join(self.styles_list)

    def __call__(self):
        return ''.join(self.styles_list)

    @property
    def styles_string(self):
        """Return a styles string"""
        return ''.join(self.styles_list)

    @styles_string.setter
    def styles_string(self, styles_string):
        """Set styles based on string"""
        styles_list = [x for x in STYLES_ORDER if x in styles_string]
        if self.allow_multiple:
            self.styles_list = styles_list
        else:
            self.styles_list = styles_list[:1]

    def keys(self):
        """Return a list of style letters"""
        return [x for x in self.styles_list]

    def values(self):
        """Return a list of style names for each style"""
        names = (STYLES.get(item, '') for item in self.styles_list)
        return [name for name in names if name]

    def items(self):
        """Returns a list of tuples: (char, name)"""
        return zip(self.keys(), self.values())

    def choose(self):
        """Chooses one or more styles and returns a list of them"""
        desc = ('\nAvailable options:\n' +
                '\n'.join(['%s - %s' % (x, STYLES[x]) for x in STYLES_ORDER]))
        header = 'Choose a text style.\n'
        if self.allow_multiple:
            header = ('Choose one or more text styles, '
                      'e.g. roman and small caps.\n')
        current = '\nCurrent: %s\n' % self
        UI.display(header + current + desc)
        self.styles_string = UI.enter_data_or_default('Your choice?',
                                                      self.styles_string)
