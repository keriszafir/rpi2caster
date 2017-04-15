# -*- coding: utf-8 -*-
"""User interface tests"""

from rpi2caster import ui
UI = ui.UIFactory()


class SpanishInquisition(Exception):
    """Custom testing exception mockup."""


def open_file():
    """Test the file opening utility."""
    suite = {UI.import_file: {'I no default - give filename': None,
                              'I no default - leave blank': None,
                              'I def. /etc/shadow - forbidden': '/etc/shadow',
                              'I def. /root/foo - forbidden dir': '/root/foo'},
             UI.export_file: {'E no default - give filename': None,
                              'E no default - leave blank': None,
                              'E def. /tmp/foo': '/tmp/foo',
                              'E def. /etc/shadow': '/etc/shadow'}}
    for function, testcases in suite.items():
        for case, default_name in testcases.items():
            print('******{}******'.format(case))
            try:
                if default_name:
                    function(default_name)
                else:
                    function()
            except ui.Abort:
                print('Aborted. OK.\n\n')


def simple_menu():
    """Test the simple menu function."""
    suite = [('[a], b; abort OK', dict(a='abc', b=123), 'a', True),
             ('[a], b; abort not OK', dict(a='abc', b=123), 'a', False),
             ('a, b, Esc; abort not OK',
              {'a': 'abc', 'b': 123, ui.KEYS['esc']: 'foobar'}, '', False),
             ('a, b, Esc; abort OK',
              {'a': 'abc', 'b': 123, ui.KEYS['esc']: 'foobar'}, None, True),
             ('a, b, abort OK, b raises CustomException',
              dict(a='abc', b=SpanishInquisition), None, True),
             ('a, b, abort OK, b raises CustomException',
              dict(a='abc', b=SpanishInquisition), None, True),
             ('a, b; abort OK', dict(a='abc', b=123), None, True),
             ('a, b; abort not OK', dict(a='abc', b=123), None, False),
             ('a, b, Esc; abort not OK',
              {'a': 'abc', 'b': 123, ui.KEYS['esc']: 'foobar'}, None, False),
             ('a, b, Esc, [1]; abort OK',
              {'a': 'abc', 'b': 123,
               ui.KEYS['esc']: 'foobar', 1: 123}, 1, True),
             ('a, b, abort OK, b raises CustomException',
              dict(a='abc', b=SpanishInquisition), None, True),
             ('a, b, abort OK, b raises CustomException',
              dict(a='abc', b=SpanishInquisition), None, True)]
    for text, options, default_key, allow_abort in suite:
        try:
            print(', '.join('{}: {}'.format(key, option)
                  for key, option in options.items()))
            result = (UI.simple_menu(text, options, default_key, allow_abort))
            print(result)
        except ui.Abort:
            print('Aborted. OK.\n\n')
        except SpanishInquisition:
            print('As expected, SpanishInquisition!')
