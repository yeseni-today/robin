#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from other.lexer import automate


def test_automate(automate, cases):
    for num_str in cases:
        automate.reset()
        if automate.recognise(num_str):
            print(automate.string)
        else:
            print('error')


def test_float_complex_dfa():
    test_automate(automate.float_complex_dfa, '''
        3.14    10.     .001    1e100    3.14e-10   0e0
        3.14j   10.j    10j     .001j    1e100j     3.14e-10j
        '''.split())


def test_int_dfa():
    test_automate(automate.int_dfa, '''
        7   2147483647                        0o177             0b100110111
        3   79228162514264337593543950336     0o377             0x100000000
        79228162514264337593543950336                       0xdeadbeef
        '''.split())


def test_number_dfa():
    test_automate(automate.number_dfa, ['0001123', '0o', '0.124e', '1.e'])
    test_automate(automate.number_dfa, '''
        7   2147483647                        0o177            0b100110111
        3   79228162514264337593543950336     0o377             0x100000000
        79228162514264337593543950336                       0xdeadbeef
        3.14    10.     .001    1e100    3.14e-10   0e0
        3.14j   10.j    10j     .001j    1e100j     3.14e-10j
        '''.split())


if __name__ == '__main__':
    test_number_dfa()
    # test_float_complex_dfa()
    # test_int_dfa()
    pass
