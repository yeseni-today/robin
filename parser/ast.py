#!/usr/bin/env python3

"""
AST, abstract semantic tree.
copy from robin.robin.ast
"""
from lexer.tokens import Token
from lexer import tokens
import json


class AST(object):
    def __repr__(self):
        return '<%s AST>' % self.__class__.__name__

    def error(self, msg=''):
        name = self.__class__.__name__
        raise Exception(f'{name} AST constructed error: {msg}')


class Literals(AST):
    def __init__(self, token: Token):
        self.token = token
        if token.type == tokens.STRING:
            # todo  转义
            pass
        elif token.type == tokens.BYTES:
            # todo  解码
            pass
        elif token.type == tokens.NUMBER:
            self.str2num()
        elif token.type == 'True':
            self.value = True
        elif token.type == 'False':
            self.value = False
        elif token.type == 'None':
            self.value = None
        else:
            self.error()

    def str2num(self):
        string = self.token.value.lower()
        if string[-1] == 'j':
            self.value = complex(string)
        elif 'x' in string:
            self.value = int(string, base=16)
        elif 'o' in string:
            self.value = int(string, base=8)
        elif 'b' in string:
            self.value = int(string, base=2)
        elif 'e' in string or '.' in string:
            self.value = float(string)
        else:
            self.value = int(string)


class Op(AST):
    def __init__(self, left: AST, op: Token, right: AST):
        self.right = right
        self.token = op
        self.value = op.value
        self.left = left


class UnaryOp(AST):
    def __init__(self, op: Token, expr: AST):
        self.token = op
        self.value = op.value
        self.expr = expr


class Var(AST):
    """Represent a variable. the field `value` is variable's name"""

    def __init__(self, token: Token):
        self.token = token
        self.value = token.value


class Suite(AST):
    """
    A code suite.
    """

    def __init__(self, children: list):
        self.children = children


class If(AST):
    """
    The if statement.
    """

    def __init__(self, condition: AST, right_suite: list, wrong_suite: list):
        self.condition = condition
        self.right_suite = right_suite
        self.wrong_suite = wrong_suite


class Assign(AST):
    """The assign statement. left is a variable, right is a express"""

    def __init__(self, left: AST, token: Token, right: AST):
        self.left = left
        self.token = token
        self.right = right


class While(AST):
    """
    The while statement.
    """

    def __init__(self, condition, token, block):
        self.block = block
        self.token = token
        self.condition = condition


class FunctionDef(AST):
    """
    Function definition.
    """

    def __init__(self, name: Var, params: list, suite: Suite):
        self.block = suite
        self.params = params
        self.name = name.value


class FunctionCall(AST):
    """
    Represent a function.
    """

    def __init__(self, name: Var, args: list):
        self.args = args
        self.name = name.value


class Program(AST):
    def __init__(self, suite: Suite):
        self.block = suite


class EmptyOp(AST):
    """Represent an empty statement. e.g. `BEGIN END` """
    pass
