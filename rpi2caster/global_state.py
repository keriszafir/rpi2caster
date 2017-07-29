# -*- coding: utf-8 -*-
"""Global configuration"""

from configparser import ConfigParser
from contextlib import suppress
from functools import wraps
import os

import click
import peewee as pw
from playhouse import db_url

from .ui import ClickUI


class DBProxy(pw.Proxy):
    """Database object sitting on top of Peewee"""
    OperationalError = pw.OperationalError

    def __init__(self, url=''):
        super().__init__()
        if url:
            self.load(url)

    def __call__(self, routine):
        @wraps(routine)
        def wrapper(*args, **kwargs):
            """decorator for routines needing database connection"""
            with self:
                retval = routine(*args, **kwargs)
            return retval

        return wrapper

    def __enter__(self):
        """context manager for routines needing database connection"""
        with suppress(pw.OperationalError):
            self.connect()
        return self

    def __exit__(self, *_):
        with suppress(pw.OperationalError):
            self.close()

    def load(self, url):
        """New database session"""
        try:
            base = db_url.connect(url)
            self.initialize(base)
        except RuntimeError:
            UI.display('Failed loading database at {}'.format(url))


class UIProxy(object):
    """UI abstraction layer"""
    impl = ClickUI()
    implementations = {'text_ui': ClickUI,
                       'click': ClickUI}

    def __init__(self, impl='click', verbosity=0):
        self.load(impl, verbosity)

    def __getattr__(self, name):
        result = getattr(self.impl, name)
        if result is None:
            raise NameError('{implementation} has no function named {function}'
                            .format(implementation=self.impl.__name__,
                                    function=name))
        else:
            return result

    def get_name(self):
        """Get the underlying user interface implementation's name."""
        return self.impl.__name__

    def load(self, implementation, verbosity):
        """Load another user interface implementation"""
        impl = self.implementations.get(implementation, ClickUI)
        self.impl = impl(verbosity)

USER_DATA_DIR = click.get_app_dir('rpi2caster', force_posix=True, roaming=True)
with suppress(FileExistsError):
    os.mkdir(USER_DATA_DIR, mode=0o775)

INITIAL_CONFIG = {"System": {}, "Typesetting": {}}
DEFAULTS = dict(database='sqlite:////{}/rpi2caster.db'.format(USER_DATA_DIR),
                interfaces='''http://localhost:23017,
                              http://localhost:23017/interfaces/0,
                              http://monotype:23017/interfaces/0''',
                default_measure='25cc', measurement_unit='cc',
                extra_typefaces='extra_typefaces.json',
                extra_unit_arrangements='extra_unit_arrangements.json',
                extra_wedges='extra_wedges.json',
                extra_languages='extra_languages.json')

UI = UIProxy()
CFG = ConfigParser(defaults=DEFAULTS)
CFG.read_dict(INITIAL_CONFIG)
DB = DBProxy(CFG['System']['database'])
