#!/usr/bin/env python3
import ast

__author__ = 'Aollio Hou'
__email__ = 'aollio@outlook.com'


class Symbol:
    def __init__(self, name, type=None):
        self.type = type
        self.name = name


class BuiltinTypeSymbol(Symbol):
    def __init__(self, name):
        super(BuiltinTypeSymbol, self).__init__(name)

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<{class_name}(name='{name}')>".format(class_name=self.__class__.__name__, name=self.name)


class BuiltinFunctionSymbol(Symbol):
    """
    Builtin Function. the dynamic return type.
    """

    def __init__(self, name, value: callable, type=None):
        super().__init__(name, type)
        self.value = value
        self.type = type

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<{class_name}(name='{name}')>".format(class_name=self.__class__.__name__, name=self.name)


class VarSymbol(Symbol):
    """内存中变量模型, 每个变量包含它的名字, 类型, 值(或者指向的对象)"""

    def __init__(self, name, type, value):
        super(VarSymbol, self).__init__(name, type)
        self.value = value

    def __str__(self):
        return f'{self.__class__.__name__}(name={self.name}, type={self.type}, value={self.value})'

    __repr__ = __str__


class FunctionSymbol(Symbol):
    """
    The type is None because in default function don't return anything.
    """

    def __init__(self, name, params, block, type=None):
        super(FunctionSymbol, self).__init__(name, type)
        # a list of formal parameters
        self.params = params if params is not None else []
        self.block = block if block is not None else ast.EmptyOp()

    def __str__(self):
        return '<{class_name}(name={name}, parameters={params})>'.format(
            class_name=self.__class__.__name__,
            name=self.name,
            params=self.params
        )

    __repr__ = __str__


def _main():
    pass


if __name__ == '__main__':
    _main()
