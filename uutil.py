#!/usr/bin/env python3
import logging

__author__ = 'Aollio Hou'
__email__ = 'aollio@outlook.com'

# _log = logging.getLogger('Util')

_level = -1
_step = '    '


def log_def(func, log=logging.getLogger('Util')):
    def wrapper(*args, **kw):
        global _level
        _level += 1
        log.info(_level * _step + 'enter %s(), args: %r, kw: %r. ', func.__name__, args, kw)
        returnvalue = func(*args, **kw)
        log.info(_level * _step + 'exit  %s(), return: %r, args: %r, kw:%r.', func.__name__, returnvalue, args, kw)
        _level -= 1
        return returnvalue

    return wrapper
