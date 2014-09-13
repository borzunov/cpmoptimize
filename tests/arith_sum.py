#!/usr/bin/env python
# -*- coding: utf-8 -*-

import core

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

pow10_wrapper = lambda func: (lambda arg: func(10 ** arg))

if __name__ == '__main__':
    core.run(
        'arith_sum', 'N elements',
        core.optimized(naive) + [
            ('formula', formula),
        ],
        [
            ('linear', None, core.linear_scale(600000, 5)),
        ],
        exec_compare=False, draw_plot=False,
    )
    core.run(
        'arith_sum', '10 ** N elements',
        [
            ('cpm', pow10_wrapper(cpmoptimize()(naive))),
            ('formula', pow10_wrapper(formula)),
        ],
        [
            ('exp', None, core.linear_scale(10000, 5)),
        ],
        exec_compare=False, draw_plot=False,
    )
