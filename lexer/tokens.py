#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import keyword
from collections import namedtuple
from robin.util import CaseInsensitiveUserDict

EOF = ENDMARKER = 'endmarker'
NEWLINE = 'newline'
INDENT = 'indent'  # value为缩进格数
DEDENT = 'dedent'  # value为DEDENT的个数 todo DEDENT的个数

# NAME = 'name'
ID = 'id'
KEYWORDS = 'keywords'

LITERALS = 'literals'
NUMBER = 'number'
STRING = 'string'
BYTES = 'bytes'

OPERATOR = 'operator'
DELIMITER = 'delimiter'

# ERRORTOKEN = 'errortoken'

_operator_list = '''
    +       -       *       **      /       //      %
    <<      >>      &       |       ^       ~
    <       >       <=      >=      ==      !=
'''.split()
operator = CaseInsensitiveUserDict({keyword: keyword for keyword in _operator_list})

_delimiter_list = '''
    (       )       [       ]       {       }
    ,       :       .       ;       @       =       ->
    +=      -=      *=      /=      //=     %=
    &=      |=      ^=      >>=     <<=     **=
'''.split()
delimiter = CaseInsensitiveUserDict({keyword: keyword for keyword in _delimiter_list})

# 关键字 33
# False      class      finally    is         return
# None       continue   for        lambda     try
# True       def        from       nonlocal   while
# and        del        global     not        with
# as         elif       if         or         yield
# assert     else       import     pass
# break      except     in         raise

# keywords = frozenset()
_keywords_list = '''
if          else        elif       
False       True        None
class       def         return      pass
from        import
raise
for         in          while
is          not
del
'''.split()
keywords = CaseInsensitiveUserDict({keyword: keyword for keyword in _keywords_list})


def iskeyword(string):
    """用于标识符和关键字的判断"""
    if string in keywords:
        return True
    if string in keyword.kwlist:
        # todo 是否需要行列号
        raise KeyError(f"'{string}'关键字未实现")
    return False


Token = namedtuple('Token', ['type', 'value', 'line', 'column'])
