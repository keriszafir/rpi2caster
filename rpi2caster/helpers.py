# -*- coding: utf-8 -*-
"""Helper routines and classes"""


def singleton(cls):
    """Decorator function for singletons"""
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance
