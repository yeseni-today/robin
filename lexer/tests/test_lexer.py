#!/usr/bin/env python3

from lexer import Lexer, lf_lines, tokens
import logging


def test_lexer(string):
    lexer = Lexer(string)
    while True:
        token = lexer.get_token()
        logging.info(token)
        if token.type == tokens.ENDMARKER:
            break


def test_number():
    test_lexer('77')
    # test_lexer('''
    #     7      0o177       00b100110111
    #     3        0o377    0x100000000  0xdeadbeef
    #     3.14    10.     .001    1e100    3.14e-10   0e0
    #     3.14j   10.j    10j     .001j    1e100j     3.14e-10j
    #      ''')


def test_name():
    test_lexer('''a b sadgsas _dsagdig ''')


def test_lf_lines():
    a = 'a\n    b\nc\rd\r\ne'
    print(lf_lines(a))


def test_str():
    test_lexer('''
    "a"  r"a"  u"a" 
      'a'  r'a'  u'a' 
b
     ''')


def test_file():
    # test_lexer(open(r'C:\Users\22340\PycharmProjects\robin\tests_pysrc\test_if.py').read())
    # test_lexer(open(r'C:\Users\22340\PycharmProjects\robin\robin\interpreter.py').read())
    test_lexer(open(r'C:\Users\22340\PycharmProjects\robin\robin\parser.py').read())


if __name__ == '__main__':
    # test_number()
    # test_name()
    # test_name()
    # test_lf_lines()
    # test_str()
    test_file()
