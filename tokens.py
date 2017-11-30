#!/usr/bin/env python3

"""
Token and Token types
"""
__author__ = 'Aollio Hou'
__email__ = 'aollio@outlook.com'


class Token:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value

    def __str__(self):
        return 'Token({type}, {value})'.format(type=self.type, value=repr(self.value))

    __repr__ = __str__


# operators. integer div is integer div.
PLUS, MINUS, MUL, DIV = 'PLUS', 'MINUS', 'MUL', 'DIV'
GREAT_THAN, LESS_THAN = 'GREAT_THAN', 'LESS_THAN'
DOT, COMMA, SEIM, LPAREN, RPAREN, COLON = 'DOT', 'COMMA', 'SEIM', 'LPAREN', 'RPAREN', 'COLON'
SPACE = 'SPACE'
ASSIGN = 'ASSIGN'
EOF = 'EOF'
# identity, variable type token
ID = 'ID'
CONST_REAL = 'REAL'
CONST_INTEGER = 'INTEGER'
CONST_BOOL = 'BOOL'


# 单个符号标记
SINGLE_MARK_DICT = {
    '+': Token(type=PLUS, value='+'),
    '-': Token(type=MINUS, value='-'),
    '*': Token(type=MUL, value='*'),
    '/': Token(type=DIV, value='/'),
    '.': Token(type=DOT, value='.'),
    ';': Token(type=SEIM, value=';'),
    '(': Token(type=LPAREN, value='('),
    ')': Token(type=RPAREN, value=')'),
    ',': Token(type=COMMA, value=','),
    ':': Token(type=COLON, value=':'),
    # '\n': Token(type=NEWLINE, value='\n'),
    # ' ': Token(type=SPACE, value=' '),
    '=': Token(type=ASSIGN, value='='),
    '>': Token(type=GREAT_THAN, value='>'),
    '<': Token(type=LESS_THAN, value='<')
}
LESS_EQUAL, GREAT_EQUAL = '<=', '>='
EQUAL = '=='
# 双符号组合
DOUBLE_MARK_DICT = {
    '<=': Token(LESS_EQUAL, value=LESS_EQUAL),
    '>=': Token(GREAT_EQUAL, value=GREAT_EQUAL),
    '==': Token(EQUAL, value=EQUAL)
}


INDENT, LINE_END = 'INDENT', 'LINE_END'
# keyword
DEF = 'def'
IF, ELIF, ELSE = 'if', 'elif', 'else'
WHILE = 'while'
PRESERVE_DICT = {
    IF: Token(type=IF, value=IF),
    ELIF: Token(type=ELIF, value=ELIF),
    ELSE: Token(type=ELSE, value=ELSE),
    WHILE: Token(type=WHILE, value=WHILE),
    DEF: Token(type=DEF, value=DEF),
    'False': Token(type=CONST_BOOL, value=False),
    'True': Token(type=CONST_BOOL, value=True)
}
