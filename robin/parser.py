#!/usr/bin/env python3
from functools import partial
import logging
from lexer import Lexer
from robin.util import log_def
from robin import ast
from lexer import tokens

__author__ = 'Aollio Hou'
__email__ = 'aollio@outlook.com'

log_def = log_def('parser')
logger = logging.getLogger('parser')


###############################################################################
#                                                                             #
#  Parser                                                                     #
#                                                                             #
###############################################################################

class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.indent = 0
        self.current_token = lexer.get_token()

    def error(self, need=None):
        msg = 'Invalid syntax. Unknown identity %r. ' % self.current_token
        if need:
            msg += 'Need Token %r' % need
        raise Exception(msg)

    def eat(self, token_type):
        if isinstance(token_type, list):
            for item in token_type:
                if self.current_token.type == item:
                    self.current_token = self.lexer.get_token()
                    return
            self.error(token_type)
            return
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_token()
        else:
            self.error(token_type)

    @log_def
    def program(self):
        """
        Program.
            <program> -> <block>
        :return:
        """
        logger.info('parsing program...')
        return ast.Program(self.block())

    @log_def
    def function_def(self):
        """
        Function definition.
            <function_def> -> DEF <variable> <argument_list> COLON NEWLINE INDENT <block>
        :return:
        """
        # todo using <params_list> replace the <argument_list>
        token = self.current_token
        self.eat(tokens.keywords.DEF)
        name = self.variable()
        params = self.argument_list()
        self.eat(tokens.delimiter[':'])
        self.eat(tokens.NEWLINE)
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
        while self.check_indent() and self.current_token.type != tokens.EOF:
            self.eat_indent()
            result.append(self.statement())
        return ast.Block(children=result)

    @log_def
    def statement(self):
        """
        A statementokens.
             <statement> -> <assign_statement>
                         -> <function_call> NEWLINE
                         -> <empty>
                         -> <if_statement>
                         -> <while_statement>
                         -> <function_def>
        :return:
        """
        statement = None
        # 分辨是赋值，还是函数调用
        if self.current_token.type == tokens.ID:
            if self.lexer.get_token() is None:
                statement = self.empty()
            elif self.lexer.get_token().type == tokens.delimiter['(']:
                statement = self.function_call()
                self.eat(tokens.NEWLINE)
            elif self.lexer.get_token().type == tokens.delimiter['=']:
                statement = self.assign_statement()
            else:
                statement = self.empty()
        elif self.current_token.type == tokens.keywords.IF:
            statement = self.if_statement()
        elif self.current_token.type == tokens.keywords.WHILE:
            statement = self.while_statement()
        elif self.current_token.type == tokens.keywords.DEF:
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
        Argument listokens.
            <argument_list> -> LPAREN (<expr> (COMMA <expr>)*)? RPAREN
        :return:
        """
        args = []
        self.eat(tokens.delimiter['('])
        if self.current_token.type != tokens.delimiter[')']:
            args.append(self.expr())
            while self.current_token.type == tokens.delimiter[',']:
                self.eat(tokens.delimiter[','])
                args.append(self.expr())
        self.eat(tokens.delimiter[')'])
        return args

    @log_def
    def while_statement(self):
        """
        `while` statement:
            <while_statement> -> WHILE <epxr> COLON NEWLINE INDENT <block>
        :return:
        """
        token = self.current_token
        self.eat(tokens.keywords.WHILE)
        condition = self.expr()
        self.eat(tokens.delimiter[':'])
        self.eat(tokens.NEWLINE)
        self.eat(tokens.INDENT)
        right_block = self.block()
        self.eat(tokens.DEDENT)

        return ast.While(condition=condition, token=token, block=right_block)

    @log_def
    def if_statement(self):
        """
        `if` statement:
            <if_statement> -> IF <expr> COLON NEWLINE INDENT <block> <elif_statement>

        :return:
        """
        token = self.current_token
        self.eat(tokens.keywords.IF)
        condition = self.expr()
        self.eat(tokens.delimiter[':'])
        self.eat(tokens.NEWLINE)

        self.eat(tokens.INDENT)
        right_block = self.block()
        self.eat(tokens.DEDENT)
        wrong_block = self.elif_statement()

        return ast.If(condition=condition, token=token, right_block=right_block, wrong_block=wrong_block)

    @log_def
    def elif_statement(self):
        """
        `elif` statement:
            <elif_statement> -> ELIF <expr> COLON NEWLINE INDENT <block> <elif_statement>*
                             -> ELSE COLON NEWLINE INDENT <block>
                             -> <empty>
        :return:
        """
        if self.current_token.type == tokens.keywords.ELIF:
            token = self.current_token
            self.eat(tokens.keywords.ELIF)
            condition = self.expr()
            self.eat(tokens.delimiter[':'])
            self.eat(tokens.NEWLINE)
            self.eat(tokens.INDENT)
            right_block = self.block()
            self.eat(tokens.DEDENT)
            wrong_block = self.elif_statement()
            return ast.If(condition, token, right_block, wrong_block)
        elif self.current_token.type == tokens.keywords.ELSE:
            self.eat(tokens.keywords.ELSE)
            self.eat(tokens.delimiter[':'])
            self.eat(tokens.NEWLINE)

            self.eat(tokens.INDENT)
            block = self.block()
            self.eat(tokens.DEDENT)
            return block
        else:
            return self.empty()

    @log_def
    def empty(self):
        if self.current_token.type == tokens.NEWLINE:
            self.eat(tokens.NEWLINE)
        return ast.EmptyOp()

    @log_def
    def assign_statement(self):
        """
        Assign statementokens.
            <assign_statement> -> <variable> ASSIGN <expr> NEWLINE
        :return:
        """
        left = self.variable()
        token = self.current_token
        self.eat(tokens.delimiter['='])
        right = self.expr()
        self.eat(tokens.NEWLINE)
        return ast.Assign(left=left, token=token, right=right)

    @log_def
    def variable(self):
        """
        A variable.
            <variable> -> Identity
        :return:
        """
        vartoken = self.current_token
        self.eat(tokens.ID)
        return ast.Var(token=vartoken)

    @log_def
    def expr(self):
        """
        A expression statementokens.
            <expr> -> <term_plus_minus> ((EQUAL|LESS_THAN|LESS_EQUAL|GREAT_THAN|GREAT_EQUAL) <term_plus_minus>)*
        :return:
        """
        node = self.term_plus_minus()

        while self.current_token.type in tokens.operator:
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

        while self.current_token.type in (tokens.operator['-'], tokens.operator['+']):
            # operator plus or minus
            op = self.current_token
            self.eat(self.current_token.type)
            right = self.term_mul_div()
            node = ast.Op(left=node, op=op, right=right)

        return node

    @log_def
    def term_mul_div(self):
        """
        One or Two terms of multiplication or division.
            <term_mul_div> -> <factor> ((MUL|DIV) <factor>)*
        :return:
        """
        node = self.factor()

        while self.current_token.type in (tokens.operator['*'], tokens.operator['/']):
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
                     -> tokens.keywords.TRUE
                     -> CONST_REGULAR_STR
        :return:
        """

        if self.current_token.type in (tokens.operator['+'], tokens.operator['-']):
            op = self.current_token
            if self.current_token.type == tokens.operator['+']:
                self.eat(tokens.operator['+'])
                return ast.UnaryOp(op=op, expr=self.factor())
            elif self.current_token.type == tokens.operator['-']:
                self.eat(tokens.operator['-'])
                return ast.UnaryOp(op=op, expr=self.factor())

        elif self.current_token.type == tokens.NUMBER:
            integer = self.current_token
            self.eat(self.current_token.type)
            return ast.Num(integer)

        elif self.current_token.type == tokens.ID:
            if self.lexer.get_token().type == tokens.delimiter['(']:
                return self.function_call()
            else:
                return self.variable()
        elif self.current_token.type == tokens.delimiter['(']:
            self.eat(tokens.delimiter['('])
            expr = self.expr()
            self.eat(tokens.delimiter[')'])
            return expr
        elif self.current_token.type in (tokens.keywords.TRUE, tokens.keywords.FALSE):
            booltoken = self.current_token
            self.eat([tokens.keywords.TRUE, tokens.keywords.FALSE])
            return ast.Bool(booltoken)
        elif self.current_token.type == tokens.STRING:
            strtoken = self.current_token
            self.eat(tokens.STRING)
            return ast.RegularStr(strtoken)

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
        if self.current_token.type not in (tokens.INDENT, tokens.DEDENT):
            return False
        count = 0
        seek = 0
        while self.lexer.get_token(seek).type in (tokens.INDENT, tokens.DEDENT):
            count += 1
            seek += 1
        if count == indent - 1:
            return True
        else:
            return False

    @log_def
    def eat_indent(self):
        indent = self.indent
        while indent != 0 and self.current_token.type in (tokens.INDENT, tokens.DEDENT):
            self.eat([tokens.INDENT, tokens.DEDENT])
            indent -= 1
        if indent:
            raise IndentationError()

    def __repr__(self):
        return '<%s>' % self.__class__.__name__


def _main():
    import argparse
    import os
    parser = argparse.ArgumentParser("Simple pascal interpreter.")
    parser.add_argument('file', help='the pascal file name')
    args = parser.parse_args()
    text = open(file=os.path.join(__file__, args.file), encoding='utf-8').read()
    lexer = Lexer(text)
    parser = Parser(lexer)
    # parser
    root_node = parser.parse()
    return root_node


if __name__ == '__main__':
    import logging

    logging.basicConfig(level=logging.INFO)
    _main()
