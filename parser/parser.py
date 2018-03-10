#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from lexer import tokens, PeekTokenLexer
from parser import ast
from abc import ABC, abstractmethod

"""
语法根据Grammar1.md 
"""


class Parser(ABC):
    def __init__(self, lexer: PeekTokenLexer):
        self.lexer = lexer
        self.indent = 0
        self.current_token = lexer.next_token()
        self.first_set = ()

        self.simple_stmt_parser = SimpleStmtParser(lexer)
        self.compound_stmt_parser = CompoundStmtParser(lexer)
        self.expr_parser = ExprParser(lexer)
        self.trailer_parser = TrailerParser(lexer)
        self.test_parser = TestParser(lexer)
        self.varargslist_parser = VarArgsListParser(lexer)

    @abstractmethod
    def parse(self):
        # todo change ExprParser to root
        return self.expr_parser.parse()

    def error(self, type=None, value=None):
        msg = 'Invalid syntax. Unknown identity %s. ' % (self.current_token,)
        if type:
            msg += 'Need Token %r, %r' % (type, value)
        raise Exception(msg)

    def eat(self, type=None):
        if type is None:
            self.current_token = self.lexer.next_token()
            return

        if self.current_token.type == type:
            self.current_token = self.lexer.next_token()
        else:
            self.error(type)

    def binary_op(self, op, next_expr: str):
        method = getattr(self, next_expr, self.generic_expr)
        node = method()
        while self.current_token.type in op:
            op = self.current_token
            self.eat()
            node = ast.Op(left=node, op=op, right=method())
        return node

    def generic_expr(self, expr: str):
        raise Exception('No {} method'.format(expr))


class SimpleStmtParser(Parser):

    def parse(self):
        pass


class CompoundStmtParser(Parser):
    """
    compound_stmt: if_stmt | while_stmt | for_stmt | try_stmt | with_stmt | funcdef | classdef | decorated | async_stmt
    """

    def __init__(self, lexer: PeekTokenLexer):
        super().__init__(lexer)
        self.first_set = ('if', 'while', 'for', 'try', 'with', 'def', 'class', '@', 'async')

    def parse(self):
        token = self.current_token
        if token.type == 'if':
            return self.if_stmt()
        elif token.type == 'while':
            return self.while_stmt()
        elif token.type == 'for':
            return self.for_stmt()
        elif token.type == 'try':
            return self.try_stmt()
        elif token.type == 'with':
            return self.with_stmt()
        elif token.type == 'def':
            return self.funcdef()
        elif token.type == 'class':
            return self.classdef()
        elif token.type == '@':
            return self.decorated()
        elif token.type == tokens.ID and token.value == 'async':
            return self.async_stmt()
        else:
            self.error()

    def if_stmt(self):
        """
        if_stmt: 'if' test ':' suite ('elif' test ':' suite)* ['else' ':' suite]
        """
        self.eat('if')
        condition = self.test_parser.parse()
        self.eat(':')
        right_suite = self.suite()

        if_root = ast.If(condition, right_suite, [])
        last_if = if_root

        while self.current_token.type == 'elif':
            self.eat()
            condition = self.test_parser.parse()
            self.eat(':')
            right_suite = self.suite()

            last_if.wrong_suite = ast.If(condition, right_suite, [])
            last_if = last_if.wrong_suite

        if self.current_token.type == 'else':
            self.eat()
            self.eat(':')
            last_if.wrong_suite = self.suite()

        return if_root

    def while_stmt(self):
        pass

    def for_stmt(self):
        pass

    def try_stmt(self):
        pass

    def with_stmt(self):
        pass

    def funcdef(self):
        pass

    def classdef(self):
        pass

    def decorated(self):
        pass

    def async_stmt(self):
        pass

    def suite(self):
        """
        suite: simple_stmt | NEWLINE INDENT (simple_stmt | compound_stmt)+ DEDENT
        """
        node_list = []
        if self.current_token.type == tokens.NEWLINE:
            self.eat(tokens.NEWLINE)
            self.eat(tokens.INDENT)

            if self.current_token.type in self.compound_stmt_parser.first_set:
                node = self.compound_stmt_parser.parse()
            else:
                node = self.simple_stmt_parser.parse()
            node_list.append(node)

            while self.current_token.type != tokens.DEDENT:
                if self.current_token.type in self.compound_stmt_parser.first_set:
                    node = self.compound_stmt_parser.parse()
                else:
                    node = self.simple_stmt_parser.parse()
                node_list.append(node)
            self.eat(tokens.DEDENT)
        else:
            node_list.append(self.simple_stmt_parser.parse())
        return node_list


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

    def parse(self):
        self.binary_op('|', 'xor_expr')

    def xor_expr(self):
        self.binary_op('^', 'and_expr')

    def and_expr(self):
        self.binary_op('&', 'shift_expr')

    def shift_expr(self):
        self.binary_op(('<<', '>>'), 'arith_expr')

    def arith_expr(self):
        self.binary_op('+-', 'term')

    def term(self):
        self.binary_op(('*', '@', '/', '%', '//'), 'factor')

    def factor(self):
        if self.current_token.type in '+-~':
            op = self.current_token
            self.eat()
            return ast.UnaryOp(op=op, expr=self.factor())
        else:
            return self.power()

    def power(self):
        node = self.atom_expr()
        if self.current_token.type == '**':
            op = self.current_token
            self.eat()
            return ast.Op(left=node, op=op, right=self.factor())
        return node

    def atom_expr(self):
        # todo  await
        if self.current_token.type == tokens.ID and self.current_token.value == 'await':
            self.eat()
            pass

        node = AtomParser(self.lexer).parse()
        # todo ast trailer
        while self.current_token.type in '({.':
            self.eat()
            trailer_node = self.trailer_parser.parse()

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
            self.eat()
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


class TestParser(Parser):
    """
    test: or_test ['if' or_test 'else' test] | lambdef

    lambdef: 'lambda' [varargslist] ':' test

    or_test: and_test ('or' and_test)*
    and_test: not_test ('and' not_test)*
    not_test: 'not' not_test | comparison
    comparison: expr (comp_op expr)*
    comp_op: '<'|'>'|'=='|'>='|'<='|'<>'|'!='|'in'|'not' 'in'|'is'|'is' 'not'
    """

    def parse(self):
        if self.current_token.type == 'lambda':
            return self.lambdef()
        else:
            node = self.or_test()
            if self.current_token.type == 'if':
                # todo or_test ['if' or_test 'else' test]
                self.eat()
                self.or_test()
                self.eat('else')
                self.parse()
            return node

    def or_test(self):
        return self.binary_op('or', 'and_test')

    def and_test(self):
        return self.binary_op('and', 'not_test')

    def not_test(self):
        if self.current_token.type == 'not':
            op = self.current_token
            self.eat()
            return ast.UnaryOp(op=op, expr=self.not_test())
        return self.comparison()

    def comparison(self):
        if self.lexer.peek_token(1).type in ('not', 'is'):
            # todo 'not' 'in'     'is' 'not'
            pass
        return self.binary_op(('<', '>', '==', '>=', '<=', '<>', '!=', 'in', 'is'), 'expr')

    def expr(self):
        return self.expr_parser.parse()

    def lambdef(self):
        self.eat('lambda')
        if self.current_token.type in (tokens.ID, '*', '**'):
            self.varargslist_parser.parse()
        self.eat(':')
        self.test_parser.parse()


class VarArgsListParser(Parser):
    """
    varargslist: (    arg (',' arg)*  [',' [  var_args | keyword_arg  ]]
                    | var_args
                    | keyword_arg
                 )

    var_args: '*' [fpdef] (',' arg)* [',' [keyword_arg]]
    keyword_args: '**' fpdef [',']
    arg: fpdef ['=' test]

    vfpdef: NAME
    tfpdef: NAME [':' test]
    """

    # first集    tokens.ID, '*', '**'

    # 函数参数：tfpdef  typed = True
    # lambda:vfpdef

    def parse(self, typed: bool = True):
        self.typed = typed  #

        if self.current_token.type == tokens.ID:
            self.arg()
            while self.current_token.type == ',' and self.lexer.peek_token(1).type == tokens.ID:
                self.eat()
                self.arg()
            if self.current_token.type == ',':
                self.eat()
                if self.current_token.type == '*':
                    self.var_args()
                elif self.current_token.type == '**':
                    self.keyword_args()

        elif self.current_token.type == '*':
            self.var_args()
        elif self.current_token.type == '**':
            self.keyword_args()

    def var_args(self):
        self.eat()
        if self.current_token.type == tokens.ID:
            arg_node = ast.Var(self.current_token)
            self.eat()
        while self.current_token.type == ',' and self.lexer.peek_token(1).type == tokens.ID:
            self.eat()
            self.arg()
        if self.current_token.type == ',':
            self.eat()
            if self.current_token.type == '**':
                self.keyword_args()

    def keyword_args(self):
        self.eat()
        self.fpdef()
        if self.current_token.type == ',':
            self.eat()

    def arg(self):
        self.fpdef()

        if self.current_token.type == '=':
            self.eat()
            default_node = self.test_parser.parse()

    def fpdef(self):
        arg_node = ast.Var(self.current_token)
        self.eat()
        if self.typed and self.current_token.type == ':':
            self.eat()
            type_node = self.test_parser.parse()


if __name__ == '__main__':
    async = 1
