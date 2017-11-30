#!/usr/bin/env python3


from interpreter import *

__author__ = 'Aollio Hou'
__email__ = 'aollio@outlook.com'


def main():
    import logging
    logging.basicConfig(level=logging.INFO)
    import argparse
    parser = argparse.ArgumentParser("Simple Robin interpreter.")
    parser.add_argument('file', help='the pascal file name')
    args = parser.parse_args()
    text = open(file=args.file, encoding='utf-8').read()
    lexer = Lexer(text)
    parser = Parser(lexer)
    # parser
    root_node = parser.parse()
    # semantic analyzer
    interpreter = Interpreter(root_node)
    interpreter.intreperter()


if __name__ == '__main__':
    main()
    exit(0)
