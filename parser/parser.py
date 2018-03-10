#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from lexer import tokens, PeekTokenLexer
from robin import ast
from abc import ABC, abstractmethod

"""
语法根据Grammar1.md 
"""


class Parser(ABC):
    def __init__(self, lexer: PeekTokenLexer):
        self.lexer = lexer
        self.indent = 0
        self.current_token = lexer.next_token()

    @abstractmethod
    def parse(self):
        # todo change ExprParser to root
        return ExprParser(self.lexer).parse()

    def error(self, type=None, value=None):
        msg = 'Invalid syntax. Unknown identity %s. ' % (self.current_token,)
        if type:
            msg += 'Need Token %r, %r' % (type, value)
        raise Exception(msg)

    def eat(self, type):
        if self.current_token.type == type:
            self.current_token = self.lexer.next_token()
        else:
            self.error(type)

    def binary_op(self, op, next_expr: str):
        method = getattr(self, next_expr, self.generic_expr)
        node = method()
        while self.current_token.type in op:
            op = self.current_token
            self.eat(self.current_token.type)
            right = method()
            node = ast.Op(left=node, op=op, right=right)
        return node

    def generic_expr(self, expr: str):
        raise Exception('No {} method'.format(expr))


class ExprParser(Parser):
    """
    expr: xor_expr ('|' xor_expr)*
    xor_expr: and_expr ('^' and_expr)*
    and_expr: shift_expr ('&' shift_expr)*
    shift_expr: arith_expr (('<<'|'>>') arith_expr)*
    arith_expr: term (('+'|'-') term)*
    term: factor (('*'|'@'|'/'|'%'|'//') factor)*
    factor: ('+'|'-'|'~') factor | power
    power: atom_expr ['**' factor]
    atom_expr: [AWAIT] atom trailer*
    """

    def __init__(self, lexer: PeekTokenLexer):
        super().__init__(lexer)

        class Op(object):
            xor_expr = 'xor_expr'
            and_expr = 'and_expr'
            shift_expr = 'shift_expr'
            arith_expr = 'arith_expr'
            term = 'term'
            factor = 'factor'
            power = 'power'
            atom_expr = 'atom_expr'

        self.op = Op

    def parse(self):
        self.binary_op('|', self.op.xor_expr)

    def xor_expr(self):
        self.binary_op('^', self.op.and_expr)

    def and_expr(self):
        self.binary_op('&', self.op.shift_expr)

    def shift_expr(self):
        self.binary_op(('<<', '>>'), self.op.arith_expr)

    def arith_expr(self):
        self.binary_op('+-', self.op.term)

    def term(self):
        self.binary_op(('*', '@', '/', '%', '//'), self.op.factor)

    def factor(self):
        if self.current_token.type in '+-~':
            op = self.current_token
            self.eat(self.current_token.type)
            return ast.UnaryOp(op=op, expr=self.factor())
        else:
            return self.power()

    def power(self):
        node = self.atom_expr()
        if self.current_token.type == '**':
            op = self.current_token
            return ast.Op(left=node, op=op, right=self.factor())
        return node

    def atom_expr(self):
        # todo  await
        # if self.current_token.type == 'await':
        node = AtomParser(self.lexer).parse()
        while self.current_token.type in '({.':
            trailer_node = TrailerParser(self.lexer).parse()
            # todo ast trailer
        return node


class AtomParser(Parser):
    """
    atom: ('(' [yield_expr|testlist_comp] ')' |
           '[' [testlist_comp] ']' |
           '{' [dictorsetmaker] '}' |
           NAME | NUMBER | STRING+ | '...' | 'None' | 'True' | 'False')
    testlist_comp: (test|star_expr) ( comp_for | (',' (test|star_expr))* [','] )
    dictorsetmaker: ( ((test ':' test | '**' expr)
                       (comp_for | (',' (test ':' test | '**' expr))* [','])) |
                      ((test | star_expr)
                       (comp_for | (',' (test | star_expr))* [','])) )
    """

    # todo AtomParser
    def parse(self):
        token = self.current_token
        if token.type == '(':
            pass
        elif token.type == '[':
            pass
        elif token.type == '{':
            pass
        elif token.type == tokens.ID:
            return ast.Var(token)
        elif token.type == tokens.NUMBER:
            return ast.Num(token)
        elif token.type == tokens.STRING:
            # todo 多个string
            return ast.RegularStr(token)
        elif token.type == '...':
            pass
        elif token.type == 'None':
            pass
        elif token.type in ('True', 'False'):
            return ast.Bool(token)
        else:
            self.error()

    def testlist_comp(self):
        pass

    def dictorsetmaker(self):
        pass


class TrailerParser(Parser):
    """
    trailer: '(' [arglist] ')' | '[' subscriptlist ']' | '.' NAME
    subscriptlist: subscript (',' subscript)* [',']
    subscript: test | [test] ':' [test] [sliceop]
    sliceop: ':' [test]
    """

    # todo TrailerParser
    def parse(self):
        pass


class OrTestParser(Parser):
    """
    or_test: and_test ('or' and_test)*
    and_test: not_test ('and' not_test)*
    not_test: 'not' not_test | comparison
    comparison: expr (comp_op expr)*
    comp_op: '<'|'>'|'=='|'>='|'<='|'<>'|'!='|'in'|'not' 'in'|'is'|'is' 'not'
    """

    def parse(self):
        return self.binary_op('or', 'and_test')

    def and_test(self):
        return self.binary_op('and', 'not_test')

    def not_test(self):
        if self.current_token.type == 'not':
            return ast.UnaryOp(self.current_token, self.not_test())
        return self.comparison()

    def comparison(self):
        if self.lexer.peek_token(1).type in ('not', 'is'):
            # todo 'not' 'in'     'is' 'not'
            pass
        return self.binary_op(('<', '>', '==', '>=', '<=', '<>', '!=', 'in', 'is',), 'expr')

    def expr(self):
        return ExprParser(self.lexer).parse()


if __name__ == '__main__':
    async = 1
