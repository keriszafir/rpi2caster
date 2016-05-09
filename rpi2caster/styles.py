# -*- coding: utf-8 -*-
"""Style manager"""
from .global_config import UI


class Styles(object):
    """Manage styles"""
    order = [x for x in 'rbislu']
    names = ['roman', 'bold', 'italic', 'smallcaps', 'inferior', 'superior']
    style_dict = dict(zip(order, names))

    def __init__(self, styles_string=None, allow_multiple=True,
                 manual_choice=False):
        self.styles_list = []
        self.allow_multiple = allow_multiple
        if manual_choice or styles_string is None:
            self.styles_string = styles_string or 'r'
            self.choose()
        elif styles_string:
            self.styles_string = styles_string
        else:
            # Setting an empty style will set all'
            self.styles_list = Styles.order

    def __iter__(self):
        return (x for x in self.styles_list)

    def __str__(self):
        if self.styles_list == Styles.order:
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
        styles_list = [x for x in Styles.order if x in styles_string]
        if self.allow_multiple:
            self.styles_list = styles_list
        else:
            self.styles_list = styles_list[:1]

    def keys(self):
        """Return a list of style letters"""
        return [x for x in self.styles_list]

    def values(self):
        """Return a list of style names for each style"""
        names = (Styles.style_dict.get(item, '') for item in self.styles_list)
        return [name for name in names if name]

    def items(self):
        """Returns a list of tuples: (char, name)"""
        return zip(self.keys(), self.values())

    def choose(self):
        """Chooses one or more styles and returns a list of them"""
        header = 'Choose one text style.'
        if self.allow_multiple:
            header = 'Choose one or more text styles.'
        string = self.styles_string
        prompt = ('%s Available options:\n'
                  'r - roman, b - bold, i - italic, s - small caps,\n'
                  'l - lower index (inferior), u - upper index (superior)\n'
                  'Your choice?' % header)
        self.styles_string = UI.enter_data_or_default(prompt, string)
