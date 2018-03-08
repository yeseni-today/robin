# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from robin import tokens
from robin.tokens import Token, iskeyword
from robin import automate
import config


def lf_lines(text):
    """将text中的换行符替换为\n"""
    lines = []
    for line in text.splitlines():
        lines.append(line + '\n')
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


class Scaner(ABC):
    def __init__(self, context):
        self.context = context

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
        return self.line[self.position + n]

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

    def skip_whitespace(self):
        while self.current_char and self.current_char.isspace():
            self.next_char()

    def make_token(self, type, value):
        return Token(type=type, value=value, line=self.line_no, column=self.position)  # todo offset  '\t'

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


class IndentScaner(Scaner):
    def match(self):
        return self.position == 0

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
                indent_num += config.TABSIZE - indent_num % config.TABSIZE
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
        raise Exception('IndentationError: unindent does not match any outer indentation level')


class EndScaner(Scaner):
    def match(self):
        return self.current_char in ('\\', '\n', None)

    # 全文结束ENDMARKER 或 行结束NEWLINE 或 None
    def scan(self):
        if self.current_char is None:  # 全结束
            return self.make_token(tokens.ENDMARKER, '')

        if self.current_char == '\n':  # 物理行结束
            if len(self.brackets_stack) == 0:  # 逻辑行结束
                token = self.make_token(tokens.NEWLINE, '')
                self.next_line()
                return token
            else:  # 隐式行连接
                self.next_line()
                self.skip_whitespace()

        if self.current_char == '\\' and self.look_around(1) == '\n':  # 显式行连接
            self.next_line()
            self.skip_whitespace()


class NumberScaner(Scaner):
    def match(self):
        return self.current_char in '0123456789' or (self.current_char == '.' and self.look_around(1) in '0123456789')

    def scan(self):
        number_dfa = automate.number_dfa

        while number_dfa.accept(self.current_char):
            self.next_char()
        if number_dfa.is_final():
            token = self.make_token(tokens.LITERALS, self.str2num(number_dfa.string))
            number_dfa.reset()
            return token
        else:
            self.error()

    def str2num(self, string):
        string = string.lower()
        if string[-1] == 'j':
            return complex(string)
        if 'x' in string:
            return int(string, base=16)
        if 'o' in string:
            return int(string, base=8)
        if 'b' in string:
            return int(string, base=2)
        if 'e' in string or '.' in string:
            return float(string)
        return int(string)


class NameScaner(Scaner):
    def match(self):
        return self.current_char and self.current_char.isidentifier()

    def scan(self):
        name = self.current_char
        self.next_char()
        while self.current_char and self.current_char.isidentifier() or self.current_char in '0123456789':
            name += self.current_char
            self.next_char()

        if iskeyword(name):
            return self.make_token(tokens.KEYWORDS, name)
        return self.make_token(tokens.ID, name)


class StrScaner(Scaner):
    def __init__(self, context):
        super().__init__(context)
        self.prefix = ''  # 前缀

    def match(self):
        if self.current_char in 'uU' and self.look_around(1) in '\'\"':
            return True
        elif self.current_char in 'rR':
            if self.look_around(1) in '\'\"':
                return True
            elif self.look_around(1) in 'bB' and self.look_around(2) in '\'\"':
                return True
        elif self.current_char in 'bB':
            if self.look_around(1) in '\'\"':
                return True
            elif self.look_around(1) in 'rR' and self.look_around(2) in '\'\"':
                return True
        elif self.current_char in 'fF' and self.look_around(1) in '\'\"':  # 格式化字符串
            return True
        return False

    def scan(self):
        self.scan_prefix()

    def scan_prefix(self):
        while self.current_char != '\'\"':
            self.prefix += self.current_char
            self.next_char()


class Lexer(Scaner):
    def match(self):
        pass

    def scan(self):
        pass

    def __init__(self, text):
        super().__init__(Context(text))
        self.indent_scaner = IndentScaner(self.context)
        self.str_scaner = StrScaner(self.context)
        self.name_scaner = NameScaner(self.context)
        self.number_scaner = NumberScaner(self.context)
        self.end_scaner = EndScaner(self.context)

    def get_token(self):

        if self.indent_scaner.match():  # 行开始
            token = self.indent_scaner.scan()
            if token: return token

        self.skip_whitespace()

        # TODO 临时逻辑，通过测试
        # @author: aollio
        if not self.current_char:
            return self.end_scaner.scan()

        if self.str_scaner.match():  # 字符串  在标识符或关键字之前判断
            return self.str_scaner.scan()

        if self.name_scaner.match():  # 标识符或关键字
            return self.name_scaner.scan()

        if self.number_scaner.match():  # 数字
            return self.number_scaner.scan()

        if self.end_scaner.match():  # 全结束 或 行结束
            token = self.end_scaner.scan()
            if token: return token

        # todo 操作符 分割符

        # indent_scaner 和 end_scaner 可能返回None 就再次调用get_token()
        return self.get_token()


if __name__ == '__main__':
    a = 'a\n    b\nc\rd\r\ne\n\n\nif    '
    import tokenize

    lexer = Lexer(a)
    token = lexer.get_token()
    while token.type != tokens.ENDMARKER:
        print(token)
        token = lexer.get_token()
