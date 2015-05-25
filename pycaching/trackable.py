#!/usr/bin/env python3

import logging
import datetime
from pycaching.errors import ValueError
from pycaching.point import Point
from pycaching.util import Util


def lazy_loaded(func):
    """Decorator providing lazy loading."""

    def wrapper(*args, **kwargs):
        self = args[0]
        assert isinstance(self, Cache)
        try:
            return func(*args, **kwargs)
        except AttributeError:
            logging.debug("Lazy loading: %s", func.__name__)
            self.geocaching.load_trackable(self.tid, self)
            return func(*args, **kwargs)

    return wrapper


class Trackable(object):

    def __init__(self, tid, geocaching, *, name=None, location=None, owner=None,
                 type=None, description=None, goal= None):
        self.geocaching = geocaching
        self.tid = tid # Tracking ID
        self.name = name
        self.location = location
        self.owner = owner
        self.desctiption = description

    def __str__(self):
        return self.tid

    def __eq__(self, other):
        return self.tid == other.tid

    @property
    def tid(self):
        return self._tid

    @tid.setter
    def tid(self, tid):
        tid = str(tid).upper().strip()
        if not tid.startswith("TB"):
            raise ValueError("Trackable ID '{}' doesn't start with 'TB'.".format(tid))
        self._tid = tid


