# -*- coding: utf-8 -*-
"""miscellaneous functions and classes"""
from weakref import WeakValueDictionary


def singleton(cls):
    """Decorator function for singletons"""
    instances = {}

    def getinstance(*args, **kwargs):
        """Check whether we already have an instance of the class"""
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return getinstance


def weakref_singleton(cls):
    """Decorator function for singletons, but don't keep instances alive
    after all references are lost"""
    instances = WeakValueDictionary({})

    def getinstance(*args, **kwargs):
        """Check whether we already have an instance of the class"""
        try:
            return instances[cls]
        except KeyError:
            instance = cls(*args, **kwargs)
            instances[cls] = instance
            return instance

    return getinstance
