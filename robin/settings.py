#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging

logging.basicConfig(
    format='%(levelname)-7s %(filename)-17s %(lineno)-4d : %(message)s',
    level=logging.INFO)

TABSIZE = 8

debug = False
test_dir = 'tests_pysrc'
result_name = 'result'
