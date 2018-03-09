#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging

logging.basicConfig(
    format='%(levelname)-7s %(filename)-17s %(lineno)-4d : %(message)s',
    level=logging.ERROR)

TABSIZE = 8


class Config:
    __slots__ = ['debug', 'test_dir', 'result_name']
    pass


config = Config()
config.debug = False
config.test_dir = 'tests_pysrc'
config.result_name = 'result'
