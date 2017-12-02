#!/usr/bin/env python3

import argparse
import os
import logging
from robin.interpreter import *
from config import config

__author__ = 'Aollio Hou'
__email__ = 'aollio@outlook.com'



class FileParser(Parser):
    def __init__(self, file):
        text = open(file, mode='r+', encoding='utf-8').read()
        lexer = Lexer(text)
        super().__init__(lexer)


class FileInterpreter(Interpreter):
    def __init__(self, file):
        parser = FileParser(file)
        super().__init__(parser.parse())


def test():
    dir = config.test_dir
    for each_file in os.listdir(dir):
        path = os.path.join(dir, each_file)
        logging.info(f'begin test {path}')
        inter = FileInterpreter(path)
        result = False
        try:
            inter.intreperter()
            # get result from global scope
            result = inter.get_global().get(config.result_name)
            if result:
                logging.info(f'{path} test passed')
        except Exception as e:
            logging.error(f'{path} test failed. raise {e}')
            raise e


def run(file):
    interpreter = FileInterpreter(file=file)
    interpreter.intreperter()


def _main():
    parser = argparse.ArgumentParser("Simple Python interpreter named Robin.")
    parser.add_argument('file', help='the python file name. if input "test", program will enter test mode')
    parser.add_argument('-d', '--debug', help='show debug message', action='store_true', default=config.debug)
    parser.add_argument('test', help='test', action='store_true', default=False)

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)

    if args.file == 'test':
        test()
    else:
        run(file=args.file)


if __name__ == '__main__':
    _main()
    exit(0)
