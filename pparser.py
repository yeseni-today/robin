#!/usr/bin/env python3

from functools import partial
from logging import getLogger
from lexer import *
from uutil import log_def
import ast

__author__ = 'Aollio Hou'
__email__ = 'aollio@outlook.com'

log = getLogger('Parser')
log_def = partial(log_def, log=log)


###############################################################################
#                                                                             #
#  Parser                                                                     #
#                                                                             #
###############################################################################

class Parser:
    def __init__(self, lexer: Lexer):
        self.indent = 0
        self.lexer = lexer
        self.current_token = lexer.read()

    def error(self, need=None):
        msg = 'Invalid syntax. Unknown identity %r. ' % self.current_token
        if need:
            msg += 'Need Token %r' % need
        raise Exception(msg)

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.read()
        else:
            self.error(token_type)

    @log_def
    def program(self):
        """
        Program.
            <program> -> <block>
        :return:
        """
        log.info('parsing program...')
        return ast.Program(self.block())

    @log_def
    def function_def(self):
        """
        Function definition.
            <function_def> -> DEF <variable> <argument_list> COLON LINE_END INDENT <block>
        :return:
        """
        # todo using <params_list> replace the <argument_list>
        token = self.current_token
        self.eat(t.DEF)
        name = self.variable()
        params = self.argument_list()
        self.eat(t.COLON)
        self.eat(t.LINE_END)
        self.indent += 1
        block = self.block()
        self.indent -= 1
        return ast.FunctionDef(name=name, params=params, block=block)

    @log_def
    def block(self):
        """
        A code Block.
            <block> -> <statement> | <statement> (<statement>)*
        :return:
        """
        result = []
        while self.check_indent() and self.current_token.type != t.EOF:
            self.eat_indent()
            result.append(self.statement())
        return ast.Block(children=result)

    @log_def
    def statement(self):
        """
        A statement.
             <statement> -> <assign_statement>
                         -> <function_call> LINE_END
                         -> <empty>
                         -> <if_statement>
                         -> <while_statement>
                         -> <function_def>
        :return:
        """
        statement = None
        # 分辨是赋值，还是函数调用
        if self.current_token.type == t.ID:
            if self.lexer.peek_token() is None:
                statement = self.empty()
            elif self.lexer.peek_token().type == t.LPAREN:
                statement = self.function_call()
                self.eat(t.LINE_END)
            elif self.lexer.peek_token().type == t.ASSIGN:
                statement = self.assign_statement()
            else:
                statement = self.empty()
        elif self.current_token.type == t.IF:
            statement = self.if_statement()
        elif self.current_token.type == t.WHILE:
            statement = self.while_statement()
        elif self.current_token.type == t.DEF:
            statement = self.function_def()
        else:
            statement = self.empty()

        return statement

    @log_def
    def function_call(self):
        """
        Function call.
            <function_call> -> <variable> <argument_list>
        :return:
        """
        fun_name = self.variable()
        arg_list = self.argument_list()
        return ast.FunctionCall(name=fun_name, args=arg_list)

    @log_def
    def argument_list(self) -> list:
        """
        Argument list.
            <argument_list> -> LPAREN (<expr> (COMMA <expr>)*)? RPAREN
        :return:
        """
        args = []
        self.eat(t.LPAREN)
        if self.current_token.type != t.RPAREN:
            args.append(self.expr())
            while self.current_token.type == t.COMMA:
                self.eat(t.COMMA)
                args.append(self.expr())
        self.eat(t.RPAREN)
        return args

    @log_def
    def while_statement(self):
        """
        `while` statement:
            <while_statement> -> WHILE <epxr> COLON LINE_END INDENT <block>
        :return:
        """
        token = self.current_token
        self.eat(t.WHILE)
        condition = self.expr()
        self.eat(t.COLON)
        self.eat(t.LINE_END)
        self.indent += 1
        right_block = self.block()
        self.indent -= 1

        return ast.While(condition=condition, token=token, block=right_block)

    @log_def
    def if_statement(self):
        """
        `if` statement:
            <if_statement> -> IF <expr> COLON LINE_END INDENT <block> <elif_statement>

        :return:
        """
        token = self.current_token
        self.eat(t.IF)
        condition = self.expr()
        self.eat(t.COLON)
        self.eat(t.LINE_END)

        self.indent += 1
        right_block = self.block()
        self.indent -= 1
        wrong_block = self.elif_statement()

        return ast.If(condition=condition, token=token, right_block=right_block, wrong_block=wrong_block)

    @log_def
    def elif_statement(self):
        """
        `elif` statement:
            <elif_statement> -> ELIF <expr> COLON LINE_END INDENT <block> <elif_statement>*
                             -> ELSE COLON LINE_END INDENT <block>
                             -> <empty>
        :return:
        """
        if self.current_token.type == t.ELIF:
            token = self.current_token
            self.eat(t.ELIF)
            condition = self.expr()
            self.eat(t.COLON)
            self.eat(t.LINE_END)
            self.indent += 1
            right_block = self.block()
            self.indent -= 1
            wrong_block = self.elif_statement()
            return ast.If(condition, token, right_block, wrong_block)
        elif self.current_token.type == t.ELSE:
            self.eat(t.ELSE)
            self.eat(t.COLON)
            self.eat(t.LINE_END)

            self.indent += 1
            block = self.block()
            self.indent -= 1
            return block
        else:
            return self.empty()

    @log_def
    def empty(self):
        if self.current_token.type == t.LINE_END:
            self.eat(t.LINE_END)
        return ast.EmptyOp()

    @log_def
    def assign_statement(self):
        """
        Assign statement.
            <assign_statement> -> <variable> ASSIGN <expr> LINE_END
        :return:
        """
        left = self.variable()
        token = self.current_token
        self.eat(t.ASSIGN)
        right = self.expr()
        self.eat(t.LINE_END)
        return ast.Assign(left=left, token=token, right=right)

    @log_def
    def variable(self):
        """
        A variable.
            <variable> -> Identity
        :return:
        """
        vartoken = self.current_token
        self.eat(t.ID)
        return ast.Var(token=vartoken)

    @log_def
    def expr(self):
        """
        A expression statement.
            <expr> -> <term_plus_minus> ((EQUAL|LESS_THAN|LESS_EQUAL|GREAT_THAN|GREAT_EQUAL) <term_plus_minus>)*
        :return:
        """
        node = self.term_plus_minus()

        while self.current_token.type in (t.EQUAL, t.LESS_THAN, t.LESS_EQUAL, t.GREAT_THAN, t.GREAT_EQUAL):
            # operator plus or minus
            op = self.current_token
            self.eat(self.current_token.type)
            right = self.term_plus_minus()
            node = ast.Op(left=node, op=op, right=right)

        return node

    @log_def
    def term_plus_minus(self):
        """
        One or Two terms of addition or subtraction.
            <term_plus_minus> -> <term_mul_div> ((PLUS|MINUS) <term_mul_div>)*
        :return:
        """
        node = self.term_mul_div()

        while self.current_token.type in (t.MINUS, t.PLUS):
            # operator plus or minus
            op = self.current_token
            self.eat(self.current_token.type)
            right = self.term_mul_div()
            node = ast.Op(left=node, op=op, right=right)

        return node

    def skip_space(self):
        while self.current_token.type == t.SPACE:
            self.eat(t.SPACE)

    @log_def
    def term_mul_div(self):
        """
        One or Two terms of multiplication or division.
            <term_mul_div> -> <factor> ((MUL|DIV) <factor>)*
        :return:
        """
        node = self.factor()

        while self.current_token.type in (t.MUL, t.DIV):
            op = self.current_token
            self.eat(self.current_token.type)
            right = self.factor()

            node = ast.Op(left=node, op=op, right=right)

        return node

    @log_def
    def factor(self):
        """
        A factor.
            <factor> -> (+|-) <factor>
                     -> CONST_INTEGER
                     -> <variable>
                     -> LPAREN <expr> RPAREN
                     -> <function_call>
                     -> CONST_BOOL
        :return:
        """

        if self.current_token.type in (t.PLUS, t.MINUS):
            op = self.current_token
            if self.current_token.type == t.PLUS:
                self.eat(t.PLUS)
                return ast.UnaryOp(op=op, expr=self.factor())
            elif self.current_token.type == t.MINUS:
                self.eat(t.MINUS)
                return ast.UnaryOp(op=op, expr=self.factor())

        elif self.current_token.type in (t.CONST_INTEGER, t.CONST_REAL):
            integer = self.current_token
            self.eat(self.current_token.type)
            return ast.Num(integer)

        elif self.current_token.type == t.ID:
            if self.lexer.peek_token().type == t.LPAREN:
                return self.function_call()
            else:
                return self.variable()
        elif self.current_token.type == t.LPAREN:
            self.eat(t.LPAREN)
            expr = self.expr()
            self.eat(t.RPAREN)
            return expr
        elif self.current_token.type == t.CONST_BOOL:
            booltoken = self.current_token
            self.eat(t.CONST_BOOL)
            return ast.Bool(booltoken)

    def parse(self):
        node = self.program()
        # if self.current_token.type != EOF:
        #     self.error(need=EOF)
        return node

    @log_def
    def check_indent(self):
        indent = self.indent
        if indent == 0:
            return True
        if self.current_token.type != t.INDENT:
            return False
        count = 0
        seek = 0
        while self.lexer.peek_token(seek).type == t.INDENT:
            count += 1
            seek += 1
        if count == indent - 1:
            return True
        else:
            return False

    @log_def
    def eat_indent(self):
        indent = self.indent
        while indent != 0 and self.current_token.type == t.INDENT:
            self.eat(t.INDENT)
            indent -= 1
        if indent:
            raise IndentationError()

    def __repr__(self):
        return '<%s>' % self.__class__.__name__


def _main():
    import argparse
    parser = argparse.ArgumentParser("Simple pascal interpreter.")
    parser.add_argument('file', help='the pascal file name')
    args = parser.parse_args()
    text = open(file=args.file, encoding='utf-8').read()
    lexer = Lexer(text)
    parser = Parser(lexer)
    # parser
    root_node = parser.parse()
    return root_node


if __name__ == '__main__':
    import logging

    logging.basicConfig(level=logging.INFO)
    _main()
