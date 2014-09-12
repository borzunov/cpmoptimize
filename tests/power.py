#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append(os.path.pardir)

from cpmoptimize import cpmoptimize


base = 78

def raw_power(n):
    res = 1
    for i in xrange(n):
        res *= base
    return res

cpm_power = cpmoptimize(strict=True, iters_limit=0)(raw_power)

def optimal_power(n):
    cur = base
    res = 1
    if not n:
        return res
    while True:
        if n & 1:
            res *= cur
            if n == 1:
                return res
        cur *= cur
        n >>= 1

def built_in_power(n):
    return base ** n


if __name__ == '__main__':
    import core

    core.run(
        'power', None,
        [
            ('raw', raw_power),
            ('cpm', cpm_power),
            ('optimal', optimal_power),
            ('built-in', built_in_power),
        ],
        [
            ('small', 'linear', core.linear_scale(10000, 25)),
            ('big', None, core.linear_scale(200000, 10)),
        ],
        True, True,
    )
