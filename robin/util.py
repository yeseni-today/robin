#!/usr/bin/env python3
import logging

__author__ = 'Aollio Hou'
__email__ = 'aollio@outlook.com'

# _log = logging.getLogger('Util')

_level = -1
_step = '    '


def log_def(name=None, log=None, *args, **kwargs):
    def decorator(func):

        def wrapper(*args, **kw):
            if name:
                logger = logging.getLogger(name=name)
            else:
                logger = logging.getLogger('Util')
            global _level
            _level += 1
            logger.info(_level * _step + '⭕️ %s(), args: %r, kw: %r. ', func.__name__, args, kw)
            rv = func(*args, **kw)
            logger.info(_level * _step + '✅ %s(), return: %r, args: %r, kw:%r.', func.__name__, rv, args, kw)
            _level -= 1
            return rv

        return wrapper

    return decorator
