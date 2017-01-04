#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tests_common as common
from cpmoptimize import cpmoptimize, xrange


start = 32
step = 43


def naive(count):
    res = 0
    for elem in xrange(start, start + step * count, step):
        res += elem
    return res


def formula(count):
    return (start * 2 + step * (count - 1)) * count / 2


def pow10_wrapper(func):
    return lambda arg: func(10 ** arg)


if __name__ == '__main__':
    common.run(
        'arith_sum', 'N elements',
        common.optimized(naive) + [
            ('formula', formula),
        ],
        [
            ('linear', None, common.linear_scale(600000, 5)),
        ],
        exec_compare=False, draw_plot=False,
    )
    common.run(
        'arith_sum', '10 ** N elements',
        [
            ('cpm', pow10_wrapper(cpmoptimize()(naive))),
            ('formula', pow10_wrapper(formula)),
        ],
        [
            ('exp', None, common.linear_scale(10000, 5)),
        ],
        exec_compare=False, draw_plot=False,
    )
