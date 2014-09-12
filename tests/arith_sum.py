#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append(os.path.pardir)

from cpmoptimize import cpmoptimize, xrange


start = 32
step = 43

def raw_arith_sum(count):
    res = 0
    for elem in xrange(start, start + step * count, step):
        res += elem
    return res

cpm_arith_sum = cpmoptimize(strict=True, iters_limit=0)(raw_arith_sum)

def optimal_arith_sum(count):
    return (start * 2 + step * (count - 1)) * count / 2

pow10_wrapper = lambda func: (lambda arg: func(10 ** arg))


if __name__ == '__main__':
    import core

    core.run(
        'arith_sum', 'N elements',
        [
            ('raw', raw_arith_sum),
            ('cpm', cpm_arith_sum),
            ('optimal', optimal_arith_sum),
        ],
        [
            ('linear', None, core.linear_scale(500000, 10)),
        ],
        False, False,
    )
    core.run(
        'arith_sum', '10 ** N elements',
        [
            ('cpm', pow10_wrapper(cpm_arith_sum)),
            ('optimal', pow10_wrapper(optimal_arith_sum)),
        ],
        [
            ('linear', None, core.linear_scale(10000, 25)),
        ],
        False, False,
    )
