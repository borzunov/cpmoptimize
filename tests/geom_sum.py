#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append(os.path.pardir)

from cpmoptimize import cpmoptimize


start = 3
coeff = 5

def raw_geom_sum(n):
    elem = start
    res = 0
    for i in xrange(n):
        res += elem
        elem *= coeff
    return res

cpm_geom_sum = cpmoptimize(strict=True, iters_limit=0)(raw_geom_sum)

def _optimal_geom_sum(first, count):
    # Returns (sum, coeff ** count)
    
    if count & 1:
        sub_sum, sub_pow = _optimal_geom_sum(first, count - 1)
        return first + sub_sum * coeff, sub_pow * coeff
    if not count:
        return 0, 1
    sub_sum, sub_pow = _optimal_geom_sum(first, count >> 1)
    return sub_sum * (1 + sub_pow), sub_pow * sub_pow

def optimal_geom_sum(count):
    return _optimal_geom_sum(start, count)[0]


if __name__ == '__main__':
    import core

    core.run(
        'geom_sum', None,
        [
            ('raw', raw_geom_sum),
            ('cpm', cpm_geom_sum),
            ('optimal', optimal_geom_sum),
        ],
        [
            ('small', 'linear', core.linear_scale(10000, 25)),
            ('big', None, core.linear_scale(200000, 10)),
        ],
        True, True,
    )
