#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from robin import settings
from robin import util
from lexer import util, automate
from lexer import tokens
from lexer.tokens import Token, iskeyword
import logging
from robin.util import log_def, log_cls


def lf_lines(text):
    """将text中的换行符替换为\n"""
    lines = []
    for line in text.splitlines():
        lines.append(line + '\n')

    # logging.info(f'\nlines{lines}')
    # logging.info('\n'+text)
    return lines


class Context(object):
    def __init__(self, text):
        self.lines = lf_lines(text)
        self.line_no = 0
        self.line = self.lines[self.line_no]
        self.position = 0  # todo offset  '\t'
        self.current_char = self.line[self.position]
        self.indent_stack = [0]  # 处理indent dedent
        self.brackets_stack = []  # 处理隐式行连接 在() [] {}中


class Scanner(ABC):
    def __init__(self, context):
        self.context = context

    def __str__(self):
        return '<%s>' % self.__class__.__name__

    __repr__ = __str__

    @property
    def lines(self):
        return self.context.lines

    @property
    def line_no(self):
        return self.context.line_no

    @line_no.setter
    def line_no(self, line_no):
        self.context.line_no = line_no

    @property
    def line(self):
        return self.context.line

    @line.setter
    def line(self, line):
        self.context.line = line

    @property
    def position(self):
        return self.context.position

    @position.setter
    def position(self, position):
        self.context.position = position

    @property
    def current_char(self):
        return self.context.current_char

    @current_char.setter
    def current_char(self, current_char):
        self.context.current_char = current_char

    @property
    def indent_stack(self):
        return self.context.indent_stack

    @indent_stack.setter
    def indent_stack(self, indent_stack):
        self.context.indent_stack = indent_stack

    @property
    def brackets_stack(self):
        return self.context.brackets_stack

    @brackets_stack.setter
    def brackets_stack(self, brackets_stack):
        self.context.brackets_stack = brackets_stack

    #############################

    def look_around(self, n):
        """:argument n 左负 右正"""
        pos = self.position + n
        if pos <= len(self.line) - 1:
            return self.line[pos]

    def next_char(self):
        if self.current_char == '\n':  # 行末
            self.next_line()
        else:
            self.position += 1
            self.current_char = self.line[self.position]

    def next_line(self):
        if self.line_no == len(self.lines) - 1:  # 结束
            self.current_char = None
            return
        self.line_no += 1
        self.position = 0
        self.line = self.lines[self.line_no]
        self.current_char = self.line[self.position]

    def make_token(self, type, value=None):
        return Token(type=type, value=value, line=self.line_no, column=self.position)  # todo offset  '\t'

    def skip_whitespace(self):
        while self.current_char not in (None, '\n') and self.current_char.isspace():
            self.next_char()

    def error(self):
        # todo 自定义异常  offset  '\t'
        print(f'line {self.line_no}')
        print(self.lines[self.line_no][0:-1])
        print(' ' * self.position + '^')
        print('Lexical error: invalid char')
        exit()

    #############################

    # 判断当前位置是否符合子类需要的token类型
    @abstractmethod
    def match(self):
        pass

    # 扫描并返回token

    @abstractmethod
    def scan(self):
        pass


class IndentScanner(Scanner):
    def match(self):
        if self.position != 0:
            return False
        if len(self.brackets_stack) != 0:  # 行连接
            return False
        if self.line_no and len(self.lines[self.line_no - 1]) > 1 and self.lines[self.line_no - 1][-2] == '\\':  # 行连接
            return False
        return True

    @log_def(name='IndentScanner')
    def scan(self):
        indent_num = self.indent_skip()
        while self.current_char in ('#', '\n'):  # 跳过 注释行 空白行
            self.next_line()
            indent_num = self.indent_skip()

        return self.indent_judge(indent_num)

    def indent_skip(self):
        """跳过缩进，并返回缩进的格数"""
        indent_num = 0
        while self.current_char in (' ', '\t'):  # 空格符 制表符
            if self.current_char == ' ':
                indent_num += 1
            else:
                indent_num += settings.TABSIZE - indent_num % settings.TABSIZE
            self.next_char()
        return indent_num

    def indent_judge(self, indent_num):
        """:argument indent_num 以此判断应该INDENT还是DEDENT或没有"""
        last_indent = self.indent_stack[-1]

        if indent_num > last_indent:  # INDENT
            self.indent_stack.append(indent_num)
            return self.make_token(tokens.INDENT, indent_num)
        elif indent_num < last_indent:  # DEDENT
            dedent_count = 0
            while indent_num < last_indent:
                dedent_count += 1
                last_indent = self.indent_stack[-1 - dedent_count]
            self.indent_stack = self.indent_stack[:- dedent_count]
            return self.make_token(tokens.DEDENT, dedent_count)
        elif indent_num == last_indent:
            return None

        self.error()  # IndentationError: unindent does not match any outer indentation level


class EndScanner(Scanner):
    def match(self):
        return self.current_char in ('#', '\\', '\n', None)

    # 全文结束ENDMARKER 或 行结束NEWLINE 或 None
    @log_def(name='EndScanner')
    def scan(self):
        char = self.current_char
        if char is None:  # 全结束
            return self.make_token(tokens.ENDMARKER)

        if char in '#\n' and len(self.brackets_stack) == 0:  # 逻辑行结束
            token = self.make_token(tokens.NEWLINE)
            self.next_line()
            return token

        if (char == '\\' and self.look_around(1) == '\n') \
                or (char == '\n' and len(self.brackets_stack) != 0):  # 显式行连接 隐式行连接
            self.next_line()
            self.skip_whitespace()


class NumberScanner(Scanner):
    def match(self):
        return self.current_char in '0123456789' or (self.current_char == '.' and self.look_around(1) in '0123456789')

    @log_def(name='NumberScanner')
    def scan(self):
        number_dfa = automate.number_dfa

        while number_dfa.accept(self.current_char):
            self.next_char()
        if number_dfa.is_final():
            token = self.make_token(tokens.NUMBER, number_dfa.string)
            # token = self.make_token(tokens.NUMBER, self.str2num(number_dfa.string))
            number_dfa.reset()
            return token
        else:
            self.error()

    # def str2num(self, string):
    #     # todo 移到语法分析中
    #     string = string.lower()
    #     if string[-1] == 'j':
    #         return complex(string)
    #     if 'x' in string:
    #         return int(string, base=16)
    #     if 'o' in string:
    #         return int(string, base=8)
    #     if 'b' in string:
    #         return int(string, base=2)
    #     if 'e' in string or '.' in string:
    #         return float(string)
    #     return int(string)


class NameScanner(Scanner):
    def match(self):
        return self.current_char and self.current_char.isidentifier()

    @log_def(name='NameScanner')
    def scan(self):
        name = self.current_char
        self.next_char()
        while (self.current_char and self.current_char.isidentifier()) or self.current_char in '0123456789':
            name += self.current_char
            self.next_char()

        if iskeyword(name):
            return self.make_token(name)
        return self.make_token(tokens.ID, name)


class StrScanner(Scanner):
    def match(self):
        head = self.current_char
        if head in '\'\"':
            return True
        if head.lower() in 'rufb':
            if self.look_around(1) in '\'\"':
                return True
            head += self.look_around(1)
            if head.lower() in ('fr', 'rf', 'br', 'rb') and self.look_around(2) in '\'\"':
                return True
        return False

    @log_def(name='StrScanner')
    def scan(self):
        string = ''
        while self.current_char not in '\'\"':  # 前缀
            string += self.current_char
            self.next_char()

        is_bytes = False
        if 'b' in string.lower():
            is_bytes = True

        quote = self.current_char  # 单引号或双引号
        quote_num = self.quote_num()  # 1 or 3

        string += quote * quote_num
        while True:
            char = self.current_char
            if quote_num == 1 and char == '\n' or char is None:
                self.error()  # SyntaxError: EOL while scanning string literal
            elif char == '\\':
                string += '\\'
                self.next_char()
                string += self.current_char
                self.next_char()
            elif char == quote and self.quote_num() == quote_num:
                string += quote * quote_num
                if is_bytes:
                    return self.make_token(tokens.BYTES, string)
                else:
                    return self.make_token(tokens.STRING, string)
            elif is_bytes and not util.is_ascii(char):
                self.error()  # SyntaxError: bytes can only contain ASCII literal characters.
            else:
                string += char
                self.next_char()

    def quote_num(self):
        if self.current_char == self.look_around(1) == self.look_around(2):
            self.next_char()
            self.next_char()
            self.next_char()
            return 3
        else:
            self.next_char()
            return 1


class OpDelimiterScanner(Scanner):
    def __init__(self, context):
        super().__init__(context)
        self.len = 0
        self.brackets_dict = {'(': ')', '[': ']', '{': '}'}

    def deal_brackets(self, bracket):
        logging.debug(f'brackets_stack: {self.brackets_stack}, cur_char:{self.current_char}')
        if bracket in '([{':
            self.brackets_stack.append(bracket)
        elif len(self.brackets_stack) == 0 or self.brackets_dict[self.brackets_stack[-1]] != bracket:
            self.error()
        else:
            self.brackets_stack.pop()

    @log_def(name='OpDelimiterScanner')
    def match(self):
        self.len = 0
        op_delimiter = self.current_char
        if op_delimiter is None:
            return False
        if op_delimiter in '()[]{},:.;@~':
            if op_delimiter in '()[]{}':
                self.deal_brackets(op_delimiter)
            self.len = 1
            return True
        elif op_delimiter in '+-*/%&|^<>=':
            if self.look_around(1) == '=':
                self.len = 2
            else:
                self.len = 1
            return True

        op_delimiter += self.look_around(1)
        if op_delimiter in ('->', '!='):
            self.len = 2
            return True
        elif op_delimiter in ('**', '//', '<<', '>>'):
            if self.look_around(2) == '=':
                self.len = 3
            else:
                self.len = 2
            return True
        return False

    @log_def(name='OpDelimiterScanner')
    def scan(self):
        op_delimiter = ''
        for i in range(self.len):
            op_delimiter += self.current_char
            self.next_char()
        logging.debug(f'op_delimiter= "{op_delimiter}"  len={self.len}')
        if op_delimiter in tokens.operator & tokens.delimiter:
            return self.make_token(op_delimiter)
        else:
            self.error()


# @log_cls
class Lexer(Scanner):
    def match(self):
        pass

    def scan(self):
        pass

    def __init__(self, text: str):
        super().__init__(Context(text))
        self.indent_scanner = IndentScanner(self.context)
        self.str_scanner = StrScanner(self.context)
        self.name_scanner = NameScanner(self.context)
        self.number_scanner = NumberScanner(self.context)
        self.end_scanner = EndScanner(self.context)
        self.op_delimiter_scanner = OpDelimiterScanner(self.context)

    @log_def(name='Lexer')
    def get_token(self):
        if self.indent_scanner.match():  # 行开始
            token = self.indent_scanner.scan()
            if token:
                return token
        if self.end_scanner.match():  # 全结束 或 行结束
            token = self.end_scanner.scan()
            if token:
                return token

        self.skip_whitespace()  # 空白符
        if self.str_scanner.match():  # 字符串  在标识符或关键字之前判断
            return self.str_scanner.scan()
        elif self.name_scanner.match():  # 标识符或关键字
            return self.name_scanner.scan()
        elif self.number_scanner.match():  # 数字
            return self.number_scanner.scan()
        elif self.op_delimiter_scanner.match():  # 操作符 分割符
            return self.op_delimiter_scanner.scan()

        # indent_scanner 和 end_scanner 可能返回None   skip_whitespace没返回        就再次调用get_token()
        return self.get_token()


class PeekTokenLexer(object):
    def __init__(self, text):
        self.lexer = Lexer(text)
        self.index = -1
        self.token_stream = []
        self._stream_token()

    def _stream_token(self):
        token = self.lexer.get_token()
        while token.type != tokens.ENDMARKER:
            if token.type == tokens.DEDENT:
                self._add_dedent(token)
            else:
                self.token_stream.append(token)
            token = self.lexer.get_token()
            logging.info(token)
        self.token_stream.append(self.lexer.get_token())

    def _add_dedent(self, token):
        """根据DEDENT.value个数 拆成value个DEDENT"""
        num = 0
        while num != token.value:
            num += 1
            self.token_stream.append(Token(tokens.DEDENT, None, token.line, token.column))

    def next_token(self):
        self.index += 1
        return self.token_stream[self.index]

    def peek_token(self, peek=1):
        index = self.index + peek
        if index >= len(self.token_stream):
            return self.token_stream[-1]
        return self.token_stream[index]
