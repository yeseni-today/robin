#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging

logging.basicConfig(
    format='%(levelname)-7s %(name)-17s %(lineno)-4d : %(message)s',
    level=logging.INFO)

TABSIZE = 8

DEBUG = False
TESTS_PY_SOURCE = 'tests_pysrc'
TESTS_PY_SOURCE_RESULT_NAME = 'result'
