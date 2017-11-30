#!/usr/bin/env python3

"""
AST, abstract semantic tree.
"""

__author__ = 'Aollio Hou'
__email__ = 'aollio@outlook.com'


class AST:
    def __repr__(self):
        return '<%s AST>' % self.__class__.__name__


class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value


class Bool(AST):
    def __init__(self, token):
        self.token = token,
        self.value = token.value


class Op(AST):
    def __init__(self, left, op, right):
        self.right = right
        self.token = op
        self.value = op.value
        self.left = left


class UnaryOp(AST):
    def __init__(self, op, expr):
        self.expr = expr
        self.token = op
        self.value = op.value


class EmptyOp(AST):
    """Represent an empty statement. e.g. `BEGIN END` """
    pass


class Var(AST):
    """Represent a variable. the field `value` is variable's name"""

    def __init__(self, token):
        self.token = token
        self.value = token.value


class Assign(AST):
    """The assign statement. left is a variable, right is a express"""

    def __init__(self, left, token, right):
        self.left = left
        self.token = token
        self.right = right


class If(AST):
    """
    The if statement.
    """

    def __init__(self, condition, token, right_block, wrong_block):
        self.wrong_block = wrong_block
        self.right_block = right_block
        self.token = token
        self.condition = condition


class While(AST):
    """
    The while statement.
    """

    def __init__(self, condition, token, block):
        self.block = block
        self.token = token
        self.condition = condition


class Block(AST):
    """
    A code block. The collection of statement in same level(indent).
    """

    def __init__(self, children: list):
        self.children = children


class FunctionDef(AST):
    """
    Function definition.
    """

    def __init__(self, name: Var, params: list, block: Block):
        self.block = block
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
    def __init__(self, block: Block):
        self.block = block
