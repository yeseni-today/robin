#!/usr/bin/env python3

"""
Simple Robin Interpreter
"""
import builtins

from pparser import *

__author__ = 'Aollio Hou'
__email__ = 'aollio@outlook.com'


###############################################################################
#                                                                             #
#  Interpreter                                                                #
#                                                                             #
###############################################################################


class Visitor:
    def visit(self, node):
        visit_func = getattr(self, 'visit_' + type(node).__name__.lower(), self.generic_visit)
        return visit_func(node)

    def generic_visit(self, node):
        raise Exception('Visit function {func} not exist'.format(
            func='visit_' + type(node).__name__.lower()))


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


def op_operate(left, op, right):
    if op == '+':
        return left + right
    elif op == '-':
        return left - right
    elif op == '*':
        return left * right
    elif op == '/':
        return left / right
    elif op == '//':
        return left // right
    elif op == '==':
        return left == right
    elif op == '<=':
        return left <= right
    elif op == '<':
        return left < right
    elif op == '>':
        return left > right
    elif op == '>=':
        return left >= right


class ScopeDict:
    def __init__(self, parent=None, init=False):
        self.scope = dict()
        self.parent = parent
        if init:
            self._init_builtin_symbol()

    def _init_builtin_symbol(self):
        # init builtin function
        for key, item in builtins.__dict__.items():
            if callable(item):
                builtin_fun = BuiltinFunctionSymbol(key, value=item)
                self.put(builtin_fun)

    def put(self, symbol: Symbol):
        self.scope[symbol.name] = symbol

    def get(self, name: str):
        value = self.scope.get(name, None)
        if value is not None:
            return value
        elif self.parent is not None:
            return self.parent.get(name)
        else:
            raise ValueError('Unknown Symbol name %r' % name)


class Memory(dict):
    def __init__(self, parent=None, init=False):
        super(Memory, self).__init__()
        self.parent = parent
        if init:
            self._init_built_symbol()

    def _init_built_symbol(self):
        # self['print'] = print
        for key, item in builtins.__dict__.items():
            if callable(item):
                self[key] = item

    def get(self, k, **kwargs):
        value = super(Memory, self).get(k, None)
        if value is not None:
            return value

        if self.parent is not None:
            return self.parent.get(k, **kwargs)


class Interpreter(Visitor):
    def __init__(self, tree):
        # symbol table
        self.tree = tree
        # global memory
        self.memory = Memory(init=True)
        self.scope = ScopeDict(init=True)

    def intreperter(self):
        self.visit(self.tree)

    def visit_program(self, node: ast.Program):
        self.visit(node.block)

    def visit_functiondef(self, node: ast.FunctionDef):
        """Build a function symbol. Put to symbol scope"""
        funsymbol = FunctionSymbol(name=node.name, params=node.params, block=node.block)
        self.scope.put(funsymbol)
        pass

    def visit_block(self, node: ast.Block):
        for statement in node.children:
            self.visit(statement)

    def visit_functioncall(self, node: ast.FunctionCall):
        # todo
        # not implement keyword argument and parameter that have default value.
        function = self.scope.get(node.name)

        # if the function is builtin function
        if isinstance(function, BuiltinFunctionSymbol):
            return function.value(*[self.visit(arg) for arg in node.args])

        # if the function is user custom function
        pre_scope = self.scope
        scope = ScopeDict(parent=self.scope)
        self.scope = scope
        # enter function scope
        # initialize args to function scope by param order
        for param_token in function.params:
            arg_value = self.visit(node.args.pop(0))
            param_sym = VarSymbol(name=param_token.value,
                                  type=type(arg_value),
                                  value=arg_value)
            scope.put(param_sym)

        # exit function scope
        self.visit(function.block)
        self.scope = pre_scope
        del scope

        # return self.memory[node.name](*[self.visit(arg) for arg in node.args])

    def visit_if(self, node: ast.If):
        condition = self.visit(node.condition)
        if condition:
            self.visit(node.right_block)
        else:
            self.visit(node.wrong_block)

    def visit_while(self, node: ast.While):
        while self.visit(node.condition):
            self.visit(node.block)

    def visit_assign(self, node: ast.Assign):
        """Assign value will check type of variable"""
        var_value = self.visit(node.right)
        var = VarSymbol(name=node.left.value, type=type(var_value), value=var_value)
        self.scope.put(var)

    def visit_var(self, node: ast.Var):
        value = self.scope.get(node.value).value
        if value is not None:
            return value
        raise NameError('Unknown Identity {name}'.format(name=node.value))

    def visit_unaryop(self, node: ast.UnaryOp):
        if node.value == '-':
            return -1 * self.visit(node.expr)
        return self.visit(node.expr)

    def visit_op(self, node: ast.Op):
        return op_operate(left=self.visit(node.left), op=node.value, right=self.visit(node.right))

    def visit_num(self, node: ast.Num):
        return node.value

    def visit_bool(self, node: ast.Bool):
        return node.value

    def visit_emptyop(self, node: ast.EmptyOp):
        pass


def main():
    import argparse
    parser = argparse.ArgumentParser("Simple pascal interpreter.")
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
