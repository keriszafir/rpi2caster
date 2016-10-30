# -*- coding: utf-8 -*-
"""miscellaneous functions"""


def singleton(cls):
    """Decorator function for singletons"""
    instances = {}

    def getinstance(*args, **kwargs):
        """Check whether we already have an instance of the class"""
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return getinstance
