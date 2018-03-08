#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging


def is_ascii(char):
    # todo which is better
    return ord(char) < 128
    # try:
    #     char.encode('ascii')
    # except UnicodeEncodeError:o
    #     return False
    # return True


def log_def(text):
    def decorator(func):
        def wrapper(*args, **kw):
            logging.debug('call %s, %s():' % (func.__name__, text))
            return func(*args, **kw)

        return wrapper

    return decorator
