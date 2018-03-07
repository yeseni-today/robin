# -*- coding: utf-8 -*-
import sys


class Interpreter(object):
    def run(self):
        pass


def main():
    # text = open(sys.argv[1], 'r').read()
    text = open('1.txt', 'r', encoding='utf-8').readlines()
    print(text)

    interpreter = Interpreter()
    interpreter.run()


if __name__ == '__main__':
    main()
