# -*- coding: utf-8 -*-
"""Letter frequencies for casting typecases

Data obtained from https://en.wikipedia.org/wiki/Letter_frequency
All data is letter occurences relative to all letters in a sample of text.
"""
from math import ceil
from itertools import chain, zip_longest
from .global_config import UI
from .exceptions import ReturnToMenu

FREQS = {'sv': {'ä': 1.797, 'r': 8.431, 'u': 1.919, 'd': 4.702, 'l': 5.275,
                'f': 2.027, 'v': 2.415, 'n': 8.542, 'å': 1.338, 'g': 2.862,
                'x': 0.159, 'o': 4.482, 'k': 3.14, 's': 6.59, 'b': 1.535,
                'w': 0.142, 'p': 1.839, 'y': 0.708, 'h': 2.09, 'm': 3.471,
                'j': 0.614, 'z': 0.07, 'a': 9.383, 't': 7.691, 'c': 1.486,
                'ö': 1.305, 'i': 5.817, 'e': 10.149, 'q': 0.02},
         'nl': {'r': 6.411, 'u': 1.99, 'd': 5.933, 'l': 3.568, 'f': 0.805,
                'v': 2.85, 'n': 10.032, 'g': 3.403, 'x': 0.036, 'o': 6.063,
                'k': 2.248, 's': 3.73, 'b': 1.584, 'w': 1.52, 'p': 1.57,
                'y': 0.035, 'h': 2.38, 'm': 2.213, 'j': 1.46, 'z': 1.39,
                'a': 7.486, 't': 6.79, 'c': 1.242, 'i': 6.499, 'e': 18.91,
                'q': 0.009},
         'fi': {'ä': 3.577, 'r': 2.872, 'u': 5.008, 'd': 1.043, 'l': 5.761,
                'f': 0.194, 'v': 2.25, 'n': 8.826, 'å': 0.003, 'g': 0.392,
                'x': 0.031, 'o': 5.614, 'k': 4.973, 's': 7.862, 'b': 0.281,
                'w': 0.094, 'p': 1.842, 'y': 1.745, 'h': 1.851, 'm': 3.202,
                'j': 2.042, 'z': 0.051, 'a': 12.217, 't': 8.75, 'c': 0.281,
                'ö': 0.444, 'i': 10.817, 'e': 7.968, 'q': 0.013},
         'cz': {'ú': 0.045, 'r': 4.799, 'ů': 0.204, 'ý': 0.995, 'c': 0.74,
                'u': 2.16, 'd': 3.475, 'i': 6.073, 'é': 0.633, 'ď': 0.015,
                'á': 0.867, 'í': 1.643, 'ž': 0.721, 'v': 5.344, 'n': 6.468,
                'ň': 0.007, 'f': 0.084, 'o': 6.695, 'k': 2.894, 's': 5.212,
                'b': 0.822, 'w': 0.016, 'j': 1.433, 'g': 0.092, 'p': 1.906,
                'y': 1.043, 'ť': 0.006, 'm': 2.446, 'ř': 0.38, 'ó': 0.024,
                'a': 8.421, 'č': 0.462, 'z': 1.503, 'h': 1.356, 't': 5.727,
                'š': 0.688, 'l': 3.802, 'e': 7.562, 'x': 0.027, 'ě': 1.222,
                'q': 0.001},
         'da': {'r': 8.956, 'u': 1.979, 'd': 5.858, 'l': 5.229, 'f': 2.406,
                'v': 2.332, 'n': 7.24, 'å': 1.19, 'g': 4.077, 'x': 0.028,
                'o': 4.636, 'k': 3.395, 'ø': 0.939, 's': 5.805, 'b': 2.0,
                'w': 0.069, 'p': 1.756, 'y': 0.698, 'h': 1.621, 'm': 3.237,
                'j': 0.73, 'z': 0.034, 'a': 6.025, 't': 6.862, 'c': 0.565,
                'i': 6.0, 'e': 15.453, 'æ': 0.872, 'q': 0.007},
         'pt': {'r': 6.53, 'c': 3.882, 'u': 3.639, 'd': 4.992, 'i': 6.186,
                'é': 0.337, 'â': 0.562, 'á': 0.118, 'í': 0.132, 'f': 1.023,
                'à': 0.072, 'ü': 0.026, 'ú': 0.207, 'b': 1.043, 'o': 9.735,
                'k': 0.015, 's': 6.805, 'w': 0.037, 'g': 1.303, 'p': 2.523,
                'y': 0.006, 'h': 0.781, 'm': 4.738, 'ó': 0.296, 'x': 0.253,
                'j': 0.397, 'z': 0.47, 'ã': 0.733, 'a': 14.634, 't': 4.336,
                'v': 1.575, 'ê': 0.45, 'l': 2.779, 'e': 12.57, 'n': 4.446,
                'q': 1.204, 'ô': 0.635, 'ç': 0.53},
         'fr': {'r': 6.693, 'c': 3.26, 'u': 6.311, 'd': 3.669, 'î': 0.045,
                'i': 7.529, 'é': 1.504, 'â': 0.051, 'œ': 0.018, 'f': 1.066,
                'à': 0.486, 'n': 7.095, 'ù': 0.058, 'b': 0.901, 'o': 5.796,
                'k': 0.049, 's': 7.948, 'w': 0.074, 'è': 0.271, 'g': 0.866,
                'p': 2.521, 'y': 0.128, 'h': 0.737, 'm': 2.968, 'x': 0.427,
                'j': 0.613, 'z': 0.326, 'a': 7.636, 't': 7.244, 'v': 1.838,
                'ê': 0.218, 'ë': 0.008, 'l': 5.456, 'e': 14.715, 'ï': 0.005,
                'q': 1.362, 'ô': 0.023, 'ç': 0.085},
         'eo': {'r': 5.914, 'u': 3.183, 'ĵ': 0.055, 'd': 3.044, 'l': 6.104,
                'ĥ': 0.022, 'v': 1.904, 'n': 7.955, 'g': 1.171, 'b': 0.98,
                'o': 8.779, 'f': 1.037, 's': 6.092, 'ĝ': 0.691, 'ŝ': 0.385,
                'p': 2.755, 'h': 0.384, 'm': 2.994, 'ŭ': 0.52, 'j': 3.501,
                'z': 0.494, 'a': 12.117, 't': 5.276, 'c': 0.776, 'i': 10.012,
                'e': 8.995, 'k': 4.163, 'ĉ': 0.657},
         'es': {'r': 6.871, 'u': 2.927, 'd': 5.01, 'é': 0.433, 'n': 6.712,
                'á': 0.502, 'í': 0.725, 'f': 0.692, 'v': 1.138, 'ü': 0.012,
                'ú': 0.168, 'b': 2.215, 'o': 8.683, 'k': 0.011, 's': 7.977,
                'w': 0.017, 'g': 1.768, 'p': 2.51, 'y': 1.008, 'h': 0.703,
                'ñ': 0.311, 'm': 3.157, 'ó': 0.827, 'x': 0.215, 'j': 0.493,
                'z': 0.467, 'a': 11.525, 't': 4.632, 'c': 4.019, 'i': 6.247,
                'e': 12.181, 'l': 4.967, 'q': 0.877},
         'it': {'r': 6.367, 'u': 3.011, 'd': 3.736, 'l': 6.51, 'c': 4.501,
                'f': 1.153, 'ì': 0.03, 'à': 0.635, 'n': 6.883, 'ù': 0.166,
                'b': 0.927, 'o': 9.832, 'k': 0.009, 's': 4.981, 'w': 0.033,
                'g': 1.644, 'p': 3.056, 'y': 0.02, 'ò': 0.002, 'm': 2.512,
                'x': 0.003, 'j': 0.011, 'z': 1.181, 'a': 11.745, 't': 5.623,
                'v': 2.097, 'h': 0.636, 'i': 10.143, 'e': 11.792, 'è': 0.263,
                'q': 0.505},
         'pl': {'r': 5.243, 'u': 2.062, 'd': 3.725, 'ń': 0.362, 'l': 2.564,
                'f': 0.143, 'v': 0.012, 'n': 6.237, 'ą': 0.699, 'g': 1.731,
                'b': 1.74, 'o': 6.667, 'k': 2.753, 's': 5.224, 'w': 5.813,
                'ś': 0.814, 'ć': 0.743, 'p': 2.445, 'y': 3.206, 'a': 10.503,
                'm': 2.515, 'ó': 1.141, 'x': 0.004, 'j': 1.836, 'z': 4.852,
                'ę': 1.035, 'h': 1.015, 't': 2.475, 'c': 3.895, 'i': 8.328,
                'e': 7.352, 'ł': 2.109, 'ż': 0.706, 'ź': 0.078},
         'tr': {'r': 7.722, 'u': 3.235, 'd': 5.206, 'l': 5.922, 'f': 0.461,
                'ğ': 1.125, 'v': 0.959, 'n': 7.987, 'g': 1.253, 'b': 2.844,
                'o': 2.976, 'k': 5.683, 'ı': 5.114, 'p': 0.886, 'y': 3.336,
                'h': 1.212, 'm': 3.752, 'j': 0.034, 'z': 1.5, 's': 3.014,
                'ş': 1.78, 'a': 12.92, 't': 3.314, 'c': 1.463, 'ö': 0.777,
                'i': 9.6, 'e': 9.912, 'ü': 1.854, 'ç': 1.156},
         'en': {'r': 5.987, 'u': 2.758, 'd': 4.253, 'l': 4.025, 'f': 2.228,
                'v': 0.978, 'n': 6.749, 'g': 2.015, 'x': 0.15, 'o': 7.507,
                'k': 0.772, 's': 6.327, 'b': 1.492, 'w': 2.361, 'p': 1.929,
                'y': 1.974, 'h': 6.094, 'm': 2.406, 'j': 0.153, 'z': 0.074,
                'a': 8.167, 't': 9.056, 'c': 2.782, 'i': 6.966, 'e': 12.702,
                'q': 0.095},
         'de': {'ä': 0.578, 'r': 7.003, 'u': 4.166, 'd': 5.076, 'l': 3.437,
                'ß': 0.307, 'f': 1.656, 'v': 0.846, 'n': 9.776, 'g': 3.009,
                'b': 1.886, 'o': 2.594, 'k': 1.417, 's': 7.27, 'w': 1.921,
                'p': 0.67, 'y': 0.039, 'a': 6.516, 'm': 2.534, 'x': 0.034,
                'j': 0.268, 'z': 1.134, 'h': 4.577, 't': 6.154, 'c': 2.732,
                'ö': 0.443, 'i': 6.55, 'e': 16.396, 'ü': 0.995, 'q': 0.018},
         'is': {'r': 8.581, 'ý': 0.228, 'u': 4.562, 'd': 1.575, 'é': 0.647,
                'þ': 1.455, 'í': 1.57, 'b': 1.043, 'v': 2.437, 'n': 7.711,
                'ú': 0.613, 'x': 0.046, 'o': 2.166, 'f': 3.013, 's': 5.63,
                'i': 7.578, 'ð': 4.393, 'g': 4.241, 'p': 0.789, 'y': 0.9,
                'h': 1.871, 'm': 4.041, 'ó': 0.994, 'j': 1.144, 'a': 10.11,
                't': 4.953, 'ö': 0.777, 'l': 4.532, 'e': 6.418, 'æ': 0.867,
                'k': 3.314, 'á': 1.799},
         '#': {'1': 10, '2': 10, '3': 10, '4': 10, '5': 10, '6': 10,
               '7': 10, '8': 10, '9': 10, '0': 10}}


class CharFreqs(object):
    """Read and calculate char frequencies, translate that to casting order"""
    frequencies = FREQS
    langs = {'en': 'English', 'nl': 'Dutch', 'pl': 'Polish', 'de': 'German',
             'eo': 'Esperanto', 'tr': 'Turkish', 'it': 'Italian',
             'cz': 'Czech', 'fr': 'French', 'es': 'Spanish',
             'pt': 'Portugese', 'da': 'Danish', 'fi': 'Finnish',
             'sv': 'Swedish', '#': 'numbers'}

    def __init__(self, lang=None):
        self.lang = lang in CharFreqs.langs and lang or choose_language()
        self.scale = 1.0
        self.case_ratio = 1

    def __getitem__(self, item):
        return self.freqs.get(item, 0)

    def __repr__(self):
        return self.lang

    def __str__(self):
        return CharFreqs.langs.get(self.lang, '')

    def __iter__(self):
        return (char for char in self.freqs)

    @property
    def freqs(self):
        """Get a dictionary of character frequencies"""
        return (CharFreqs.frequencies.get(self.lang) or
                CharFreqs.frequencies.get('en'))

    @property
    def type_bill(self):
        """Returns an iterator object of tuples: (char, qty)
        for each character."""
        def quantity(char, upper=False):
            """Calculate character quantity based on frequency"""
            ratio = upper and self.case_ratio or 1
            normalized_qty = self.freqs.get(char, 0) / self.freqs.get('a', 1)
            return max(ceil(normalized_qty * self.scale * ratio), 10)

        # Start with lowercase
        lower_bill = ((char, quantity(char)) for char in sorted(self.freqs))
        upper_bill = ((char.upper(), quantity(char, upper=True))
                      for char in sorted(self.freqs) if char.isalpha())
        return chain(lower_bill, upper_bill)

    def define_scale(self):
        """Define scale of production"""
        prompt = ('How much lowercase "a" characters do you want to cast?\n'
                  'The quantities of other characters will be calculated\n'
                  'based on the letter frequency of the language.\n'
                  'Minimum of 10 characters each will be cast.')
        self.scale = UI.enter_data_or_default(prompt, 100, int)

    def define_case_ratio(self):
        """Define uppercase to lowercase ratio"""
        prompt = ('Uppercase to lowercase ratio in %?')
        self.case_ratio = UI.enter_data_or_default(prompt, 20, float) / 100.0


def choose_language():
    """Display available languages and let user choose one.
    Returns a string with language code (e.g. en, nl, de)."""
    lang_it = ('%s - %s' % (lang, CharFreqs.langs[lang])
               for lang in sorted(CharFreqs.langs))
    # Group by three
    grouper = zip_longest(lang_it, lang_it, lang_it, fillvalue='')
    descriptions = '\n'.join('\t'.join(z) for z in grouper)
    UI.display('Choose language:\n\n%s\n' % descriptions)
    prompt = 'Language code (e.g. "en") or leave blank to go back to menu'
    lang_code = UI.enter_data_or_exception(prompt, ReturnToMenu)
    return lang_code
