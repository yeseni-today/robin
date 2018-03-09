#!/usr/bin/env python3
import logging
import collections
from functools import wraps

__author__ = 'Aollio Hou'
__email__ = 'aollio@outlook.com'

# _log = logging.getLogger('Util')

_level = -1
_step = '    '


def log_def(name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kw):
            logger = logging.getLogger(name)
            global _level
            _level += 1
            logger.info(_level * _step + '-->️ %s(), args: %r, kw: %r. ', func.__name__, args, kw)
            rv = func(*args, **kw)
            logger.info(_level * _step + '<-- %s(), rv: %r, args: %r, kw:%r.', func.__name__, rv, args, kw)
            _level -= 1

        return wrapper

    return decorator



class UserDict(dict):

    def __getattr__(self, item):
        try:
            return super(UserDict, self).__getattr__(item)
        except AttributeError:
            return super(UserDict, self).__getitem__(item)

    def __setattr__(self, item, val):
        super(UserDict, self).__setitem__(item, val)

    def __delattr__(self, item):
        return super(UserDict, self).__delitem__(item)


class CaseInsensitiveUserDict(UserDict):
    def __setitem__(self, key, value):
        super(CaseInsensitiveUserDict, self).__setitem__(key.lower(), value)

    def __getitem__(self, key):
        return super(CaseInsensitiveUserDict, self).__getitem__(key.lower())
