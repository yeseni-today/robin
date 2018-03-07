# -*- coding: utf-8 -*-
from lexer import Lexer
import tokens


def test_lexer(string):
    print(string)
    lines = []
    for line in string.split('\n'):
        lines.append(line + '\n')
    lexer = Lexer(lines)
    while True:
        token = lexer.get_token()
        print(token)
        if token.type == tokens.ENDMARKER:
            break


def test_number():
    test_lexer('0077')
    # test_lexer('''
    #     007      0o177       00b100110111
    #     3        0o377    0x100000000  0xdeadbeef
    #     3.14    10.     .001    1e100    3.14e-10   0e0
    #     3.14j   10.j    10j     .001j    1e100j     3.14e-10j
    #      ''')


def test_name():
    test_lexer('''a b sadgsas _dsagdig ''')


if __name__ == '__main__':
    test_number()
    # test_name()
    '''
    a
    '''
