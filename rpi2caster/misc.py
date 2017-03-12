# -*- coding: utf-8 -*-
"""miscellaneous functions and classes"""
from weakref import WeakSet, WeakValueDictionary
from collections import OrderedDict
from contextlib import suppress


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


@singleton
class PubSub:
    """Publish/subscribe engine for object updates"""
    def __init__(self):
        self.observers = {}

    def subscribe(self, observer, *channels):
        """Add an observer to one or more channels"""
        for channel in channels:
            try:
                self.observers[channel].add(observer)
            except (KeyError, AttributeError):
                # initialize the channel observer set
                # WeakSet to make sure the objects are unique and properly GCed
                self.observers[channel] = WeakSet()
                self.observers[channel].add(observer)

    def unsubscribe(self, observer, *channels):
        """Remove an observer from given channel"""
        for channel in channels:
            with suppress(KeyError, ValueError, AttributeError):
                self.observers[channel].remove(observer)

    def unsubscribe_all_from(self, *channels):
        """Unsubscribe all observers from a given channel"""
        for channel in channels:
            with suppress(KeyError):
                self.observers.pop(channel)

    def unsubscribe_observers(self, *observers):
        """Unsubscribe an observer from all channels"""
        for observer in observers:
            for observer_set in self.observers.values():
                with suppress(ValueError, AttributeError):
                    observer_set.remove(observer)

    def unsubscribe_all_from_all(self):
        """Unsubscribe all observers from all channels"""
        self.observers.clear()

    def update(self, channel, message):
        """Update observers' parameters on channel
        using their update(message) method. Message is any data,
        preferably dict. Only observers subscribed to channel will get the
        message."""
        with suppress(KeyError):
            for observer in self.observers[channel]:
                observer.update(message)


class Parameters:
    """Data structure for grouping parameters to display"""
    def __init__(self, title, data=()):
        self.title = title
        self.storage = OrderedDict(data)

    def __str__(self):
        return self.text_block

    def __iter__(self):
        return self.contents_iterator()

    def __getitem__(self, item):
        return self.storage.get(item)

    def __setitem__(self, item, value):
        self.storage[item] = value

    def __delitem__(self, item):
        with suppress(KeyError):
            del self.storage[item]

    def __contains__(self, item):
        return item in self.storage

    def get(self, item, default=None):
        """facade for dict get method of self.storage"""
        return self.storage.get(item, default)

    @property
    def contents_iterator(self):
        """Get an iterator of name: value parameters"""
        return ('%s: %s' % (k, v) for k, v in self.storage.items())

    @property
    def contents_string(self):
        """Get a string listing all contents"""
        return '\n'.join(self.contents_iterator)

    @property
    def text_block(self):
        """Get a text block complete with a header"""
        dashes = '-' * len(self.title)
        return '\n'.join(['', dashes, self.title, dashes, '',
                          self.contents_string, ''])
