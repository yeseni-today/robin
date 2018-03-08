#!/usr/bin/env python3

import os
import logging
import click

from config import config
from robin.interpreter import *

from robin import tokens

__author__ = 'Aollio Hou'
__email__ = 'aollio@outlook.com'


class FileLexer(Lexer):
    def __init__(self, file):
        text = open(file=file, encoding='utf-8').read()
        super().__init__(text)


class FileParser(Parser):
    def __init__(self, file):
        super().__init__(FileLexer(file))


class FileInterpreter(Interpreter):
    def __init__(self, file):
        super().__init__(FileParser(file).parse())


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    pass


def set_debug(ctx, param, debug):
    if debug:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)


@cli.command(help='Run Python files.')
@click.argument('file')
@click.option('-d', '--debug', is_flag=True, callback=set_debug,
              expose_value=False, is_eager=True, help='Show the debug message.')
def run(file):
    interpreter = FileInterpreter(file=file)
    interpreter.intreperter()


@cli.command(help='Parsing Python files to Tokens')
@click.argument('file')
@click.option('-d', '--debug', is_flag=True, callback=set_debug,
              expose_value=False, is_eager=True, help='Show the debug message.')
def lexer(file):
    a_lexer = FileLexer(file)
    token = a_lexer.get_token()
    print(token)

    while token.type != tokens.ENDMARKER:
        token = a_lexer.get_token()
        print(token)


@cli.command(help='Procedure correctness test.')
def test():
    dir = config.test_dir
    for each_file in os.listdir(dir):
        path = os.path.join(dir, each_file)
        logging.info(f'begin test {path}')
        inter = FileInterpreter(path)
        try:
            inter.intreperter()
            # get result from global scope
            result = inter.get_global().get(config.result_name)
        except Exception as e:
            print(f'{path} test failed. raise {e}')
            raise e
        if result:
            print(f'{path} test passed')


def _main():
    cli()


if __name__ == '__main__':
    _main()
