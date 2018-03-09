#!/usr/bin/env python3
import logging
from functools import wraps

__author__ = 'Aollio Hou'
__email__ = 'aollio@outlook.com'

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


def log_cls(cls):
    class NewCls(object):
        def __init__(self, *args, **kwargs):
            print('in NewCls __init__', args, kwargs)
            self.oInstance = cls(*args, **kwargs)

        def __getattribute__(self, s):
            """
            this is called whenever any attribute of a NewCls object is accessed. This function first tries to
            get the attribute off NewCls. If it fails then it tries to fetch the attribute from self.oInstance (an
            instance of the decorated class). If it manages to fetch the attribute from self.oInstance, and
            the attribute is an instance method then `time_this` is applied.
            """
            try:
                x = super(NewCls, self).__getattribute__(s)
            except AttributeError:
                pass
            else:
                return x
            x = self.oInstance.__getattribute__(s)
            if type(x) == type(self.__init__):  # it is an instance method
                return log_def(cls.__name__)(x)  # this is equivalent of just decorating the method with time_this
            else:
                return x

    return NewCls


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
