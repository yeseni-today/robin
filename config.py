#!/usr/bin/env python3


__author__ = 'Aollio Hou'
__email__ = 'aollio@outlook.com'


class Config:
    __slots__ = ['debug', 'test_dir', 'result_name']
    pass


config = Config()
config.debug = False
config.test_dir = 'test'
config.result_name = 'result'
