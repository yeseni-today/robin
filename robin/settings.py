#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging

logging.basicConfig(
    format='%(levelname)-7s %(name)-17s %(lineno)-4d : %(message)s',
    level=logging.INFO
)
logging.getLogger('OpDelimiterScanner').setLevel(logging.ERROR)
logging.getLogger('NumberScanner').setLevel(logging.ERROR)
logging.getLogger('EndScanner').setLevel(logging.ERROR)
logging.getLogger('IndentScanner').setLevel(logging.ERROR)
logging.getLogger('NameScanner').setLevel(logging.ERROR)
# logging.getLogger('Lexer').setLevel(logging.ERROR)
TABSIZE = 8
INDENT_LENGTH = 4

DEBUG = False
TESTS_PY_SOURCE = 'tests_pysrc'
TESTS_PY_SOURCE_RESULT_NAME = 'result'
