#!/usr/bin/env python
# -*- coding: utf-8 -*-

import core

start = 3
coeff = 5

def naive(count):
    elem = start
    res = 0
    for i in xrange(count):
        res += elem
        elem *= coeff
    return res

def _optimal(first, count):
    # Returns (sum, coeff ** count)
    
    if count & 1:
        sub_sum, sub_pow = _optimal(first, count - 1)
        return first + sub_sum * coeff, sub_pow * coeff
    if not count:
        return 0, 1
    sub_sum, sub_pow = _optimal(first, count >> 1)
    return sub_sum * (1 + sub_pow), sub_pow * sub_pow

def optimal(count):
    """Optimal algorithm based on the idea similar to the binary
    exponentiation."""
    
    return _optimal(start, count)[0]

if __name__ == '__main__':
    core.run(
        'geom_sum', None,
        core.optimized(naive) + [
            ('optimal', optimal),
        ],
        [
            (None, 'linear', core.linear_scale(10000, 15)),
        ],
    )
