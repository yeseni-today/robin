#!/usr/bin/env python3

import os
import logging
import click

from robin import settings
from robin.interpreter import *
from lexer import Lexer
from lexer import tokens

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


@cli.command(help='Using lexer parse Python file to Tokens')
@click.argument('file')
@click.option('-d', '--debug', is_flag=True, callback=set_debug,
              expose_value=False, is_eager=True, help='Show the debug message.')
def lexer(file):
    a_lexer = FileLexer(file)
    token = a_lexer.get_token()
    print(token)

    while token is not None and token.type != tokens.ENDMARKER:
        token = a_lexer.get_token()
        print(token)
    print(token)


@cli.command(help='Using parser parse Python file to AST')
@click.argument('file')
@click.option('-d', '--debug', is_flag=True, callback=set_debug,
              expose_value=False, is_eager=True, help='Show the debug message.')
def parser(file):
    a_parser = FileParser(file)
    root = a_parser.parse()
    print('>' * 10, root)


@cli.command(help='Test python source.')
def test_pysrc():
    dir = settings.TESTS_PY_SOURCE
    for each_file in os.listdir(dir):
        path = os.path.join(dir, each_file)
        logging.info(f'begin tests_pysrc {path}')
        inter = FileInterpreter(path)
        try:
            inter.intreperter()
            # get result from global scope
            result = inter.get_global().get(settings.TESTS_PY_SOURCE_RESULT_NAME)
        except Exception as e:
            print(f'{path} tests_pysrc failed. raise {e}')
            raise e
        if result:
            print(f'{path} tests_pysrc passed')


@cli.command(help='Run test scripts. Unimplemented!')
def test():
    # TODO
    from lexer import tests as lexer_tests
    # from robin import tests as robin_tests

    # tests_modules = [lexer_tests, robin_tests]
    #
    # for module_tests in tests_modules:
    #     mod_path = module_tests.__path__[0]
    #     for file in os.listdir(mod_path):
    #         if not file.startswith('test_'):
    #             continue
    pass


def _main():
    cli()


if __name__ == '__main__':
    _main()
