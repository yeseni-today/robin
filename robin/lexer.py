#!/usr/bin/env python3


from functools import partial
import logging

from robin.tokens import Token
from robin import tokens as t
from robin.util import log_def

__author__ = 'Aollio Hou'
__email__ = 'aollio@outlook.com'

log = logging.getLogger('Lexer')
log_def = partial(log_def, log=log)

DEFAULT_ENCODING = 'utf-8'


###############################################################################
#                                                                             #
#  Lexer                                                                      #
#                                                                             #
###############################################################################


class Lexer:
    def __init__(self, text: str):
        self.tokens = []

        self.text = text
        if len(text) == 0:
            self.current_char = None
            self.tokens.append(Token(type=t.EOF))
            return

        self.pos = 0
        self.current_char = self.text[self.pos]
        while self.current_char is not None:
            self._parse_token()
        self.tokens.append(Token(type=t.EOF))

    def next_pos(self):
        """将当前位置向后移一位"""
        if self.pos is None:
            return None
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.pos = None
            self.current_char = None
            return
        self.current_char = self.text[self.pos]

    @log_def
    def id(self):
        """从输入中获取一个标识符 Identity"""
        chars = ''
        while self.current_char is not None and \
                self.current_char.isalnum() \
                or self.current_char == '_':
            chars += self.current_char
            self.next_pos()
        token = t.PRESERVE_DICT.get(chars, Token(type=t.ID, value=chars))
        return token

    def newline_and_indent(self):
        if self.current_char == '\n':
            self.tokens.append(Token(type=t.LINE_END, value=t.LINE_END))
            self.next_pos()
        count = 0
        while self.current_char == ' ':
            count += 1
            self.next_pos()
        if count % 4 != 0:
            raise Exception("Wrong Indent")
        a = count // 4
        [self.tokens.append(Token(type=t.INDENT)) for x in range(a)]

    @log_def
    def number(self):
        """从输入中获取一个数字串"""
        chars = ''
        while self.current_char is not None and self.text[self.pos].isdigit():
            chars += self.text[self.pos]
            self.next_pos()

        if self.current_char == '.':
            chars += self.current_char
            self.next_pos()
            while self.current_char is not None and self.current_char.isdigit():
                chars += self.current_char
                self.next_pos()
            return Token(type=t.CONST_REAL, value=float(chars))
        else:
            return Token(type=t.CONST_INTEGER, value=int(chars))

    @log_def
    def regular_str(self):
        """Parsing a regular str from input stream."""
        chars = self._parse_string()
        # escape processing
        chars = chars.encode().decode('unicode-escape')
        return Token(t.CONST_STR, chars)

    @log_def
    def prefix_str(self):
        """Parsing a string with prefix like 'r', 'b' and 'f'"""
        prefix = self.current_char
        self.next_pos()
        chars = self._parse_string()
        if prefix == 'b':
            # escape processing
            chars = chars.encode().decode('unicode-escape')
            return Token(t.CONST_BYTES, bytes(chars, encoding=DEFAULT_ENCODING))
        elif prefix == 'r':
            return Token(t.CONST_STR, chars)
        elif prefix == 'f':
            raise SyntaxError("'f' string not support.")

    def error(self):
        raise Exception("Invalid Character '%s'" % self.text[self.pos])

    def skip_comment(self):
        if self.current_char is not None and self.text[self.pos] == '#':
            self.next_pos()
            while self.current_char is not None and self.text[self.pos] != '\n':
                self.next_pos()
            self.tokens.append(Token(type=t.LINE_END))
        # self.next_pos is `\n` character
        # so if the next line begin with `#`, eat the NEWLINE token
        if self.current_char == '\n' and self._peek_char() in (None, '#'):
            self.next_pos()

    def skip_space(self):
        while self.current_char == ' ':
            self.next_pos()

    @log_def
    def _parse_token(self):
        """获取下一个token"""

        while self.current_char is not None:

            current_char = self.current_char

            # regular string. like 'something' or "something"
            if current_char in "\'\"":
                self.tokens.append(self.regular_str())
                return
            # parse string with prefix. like r,b,f(not support)
            if current_char in 'rbf' \
                    and self._peek_char() in "\'\"":
                self.tokens.append(self.prefix_str())
                return

            # id. keyword or variable
            if current_char.isalpha() or current_char == '_':
                self.tokens.append(self.id())
                return

            # (multi)integer.
            if current_char.isdigit():
                self.tokens.append(self.number())
                return

                # new line
            if current_char == '\n':
                self.newline_and_indent()
                return

            # double mark， like '==', '<='...
            if self._peek_char() is not None \
                    and self.current_char is not None \
                    and self.current_char + self._peek_char() in t.DOUBLE_MARK_DICT:
                mark = self.current_char + self._peek_char()
                self.next_pos()
                self.next_pos()
                self.tokens.append(t.DOUBLE_MARK_DICT.get(mark, ))
                return

            # single mark, like '=', '+'...
            if current_char in t.SINGLE_MARK_DICT:
                self.next_pos()
                self.tokens.append(t.SINGLE_MARK_DICT.get(current_char, ))
                return

            # comment
            if current_char == '#':
                self.skip_comment()
                continue
            if current_char == ' ':
                self.skip_space()
                continue
                # return SINGLE_MARK_DICT.get(current_char,)

            self.error()
            # 如果输入流结束, 返回一个EOF Token
            # if self.current_char is None:
            #     return Token(type=EOF)

    def _parse_string(self):
        chars = ''
        # begin char is \' or \"
        begin = self.current_char
        self.next_pos()
        while self.current_char is not None and self.text[self.pos] != begin:
            chars += self.current_char
            self.next_pos()
        # skip the ending character
        self.next_pos()
        return chars

    def _peek_char(self, seek=1):
        """向前看一个字符"""
        if self.pos + seek < len(self.text):
            return self.text[self.pos + seek]
        else:
            return None

    def peek_token(self, seek=0):
        if len(self.tokens) > seek + 1:
            return self.tokens[seek]
        else:
            return Token(type=t.EOF)

    def read(self):
        if self.tokens:
            return self.tokens.pop(0)
        return Token(type=t.EOF)


def _main():
    import argparse
    parser = argparse.ArgumentParser("Simple pascal interpreter.")
    parser.add_argument('file', help='the pascal file name')
    args = parser.parse_args()
    text = open(file=args.file, encoding='utf-8').read()
    lexer = Lexer(text)
    token = lexer.read()
    while token.type != t.EOF:
        print(token)
        token = lexer.read()
    print(Token(type=t.EOF))


if __name__ == '__main__':
    import logging

    logging.basicConfig(level=logging.INFO)
    _main()
