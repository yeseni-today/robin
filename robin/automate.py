# -*- coding: utf-8 -*-
from enum import Enum


class Automate(object):
    def __init__(self, arcs, status_map, final_status):
        """
        :param arcs 注：每个弧之间不含相同的字符！
        :param status_map 状态转换图 二维
        :param final_status 对应的状态是不是终态 是True非False
        """
        self.arcs = arcs
        self.status_map = status_map
        self.final_status = final_status
        self.status = 0  # 当前状态
        self.string = ''  # 已识别的部分
        self.check_map()
        self.fill_map()

    def error(self):
        raise Exception('Automate error!')

    def fill_map(self):
        """每行若不足则补充None，若多出则报错"""
        arcs_num = len(self.arcs)
        for row in self.status_map:
            if len(row) > arcs_num:
                self.error()
            row += [None] * (arcs_num - len(row))

    def check_map(self):
        """检查行数"""
        if len(self.final_status) != len(self.status_map):
            self.error()

    def reset(self):
        self.status = 0
        self.string = ''

    def is_final(self):
        """当前状态是否为终态"""
        return self.final_status[self.status]

    def accept(self, char):
        """
        :return 能否接受char
        """
        row = self.status_map[self.status]
        for i, arc in enumerate(self.arcs):
            if row[i] and char in arc.value:
                # print(f'log:   char:{char}, arc:{arc.value}, i:{i},next:{row[i]}')
                self.string += char
                self.status = row[i]
                return True
        return False

    def recognise(self, string):
        """
        :return: 能否识别string
        """
        for char in string:
            if self.accept(char) is False:
                return False
        return self.is_final()


class Arcs(Enum):
    zero = '0'
    no_zero = '123456789'
    digit = '0123456789'
    dot = '.'
    sign_bit = '+-'

    exponent_sign = 'eE'
    complex_sign = "jJ"
    oct_sign = 'oO'
    oct = '012345678'
    hex_sign = "xX"
    hex = '0123456789abcdefABCDEF'
    bin_sign = "bB"
    bin = '01'


# 被number_dfa替代
float_complex_dfa = Automate(
    arcs=(Arcs.digit, Arcs.dot, Arcs.exponent_sign, Arcs.complex_sign, Arcs.sign_bit),
    status_map=[[1, 2],
                [1, 3, 4, 7],
                [3],
                [3, None, 4, 7],
                [6, None, None, None, 5],
                [6],
                [6, None, None, 7],
                []],
    final_status=(False, False, False, True, False, False, True, True)
)

# 被number_dfa替代
int_dfa = Automate(
    arcs=(Arcs.no_zero, Arcs.zero, Arcs.bin_sign, Arcs.oct_sign, Arcs.hex_sign, Arcs.bin, Arcs.oct, Arcs.hex),
    status_map=[[1, 2],
                [1, 1],
                [None, 3, 4, 5, 6],
                [None, 3],
                [None, None, None, None, None, 7],
                [None, None, None, None, None, None, 8],
                [None, None, None, None, None, None, None, 9],
                [None, None, None, None, None, 7],
                [None, None, None, None, None, None, 8],
                [None, None, None, None, None, None, None, 9]],
    final_status=(False, True, True, True, False, False, False, True, True, True)
)

number_dfa = Automate(
    arcs=(Arcs.no_zero, Arcs.zero, Arcs.dot, Arcs.exponent_sign, Arcs.complex_sign, Arcs.bin_sign, Arcs.oct_sign,
          Arcs.hex_sign, Arcs.sign_bit, Arcs.bin, Arcs.oct, Arcs.hex),
    status_map=[[1, 2, 3],
                [1, 1, 4, 5, 6],
                [7, 8, 4, 5, 6, 9, 10, 11],
                [4, 4],
                [4, 4, None, 5, 6],
                [12, 12, None, None, None, None, None, None, 13],
                [],
                [7, 7, 4, 5, 6],
                [7, 8, 4, 5, 6],
                [None, None, None, None, None, None, None, None, None, 14],
                [None, None, None, None, None, None, None, None, None, None, 15],
                [None, None, None, None, None, None, None, None, None, None, None, 16],
                [12, 12, None, None, 6],
                [12, 12],
                [None, None, None, None, None, None, None, None, None, 14],
                [None, None, None, None, None, None, None, None, None, None, 15],
                [None, None, None, None, None, None, None, None, None, None, None, 16]],
    final_status=(
        False, True, True, False, True, False, True, False, True, False, False, False, True, False, True, True, True)
)
