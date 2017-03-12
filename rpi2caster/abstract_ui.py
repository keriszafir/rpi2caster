# -*- coding: utf-8 -*-
"""User interface abstraction for rpi2caster"""
from .misc import weakref_singleton, PubSub


def text_user_interface():
    """Click-based text UI"""
    from . import text_ui
    return text_ui


def flask_user_interface():
    """Flask-based web UI"""
    from . import flask_web_ui
    return flask_web_ui


def web_cli():
    """Web command line interface"""
    from . import web_cli_ui
    return web_cli_ui


@weakref_singleton
class UIFactory(object):
    """UI abstraction layer"""
    implementations = {'text_ui': text_user_interface,
                       'click': text_user_interface,
                       'flask': flask_user_interface,
                       'web_cli': web_cli,
                       }

    def __init__(self):
        PubSub().subscribe(self, 'UI')
        self.impl = text_user_interface()

    def __getattr__(self, name):
        result = self.impl.__dict__.get(name)
        if result is None:
            raise NameError('%s has no function named %s'
                            % (self.impl.__name__, name))
        else:
            return result

    def update(self, source):
        """Update the UI implementation"""
        name = source.get('impl') or source.get('implementation')
        impl = self.implementations.get(name)
        if impl:
            self.impl = impl()
