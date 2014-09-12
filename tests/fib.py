#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append(os.path.pardir)

from cpmoptimize import cpmoptimize
from cpmoptimize.matrices import Matrix


def raw_fib(n):
    a = 0
    b = 1
    for i in xrange(n):
        a, b = b, a + b
    return a

#cpm_fib_no_mc = cpmoptimize(
#    strict=True, iters_limit=0,
#    opt_min_rows=False, opt_clear_stack=False,
#)(raw_fib)
#cpm_fib_no_m = cpmoptimize(
#    strict=True, iters_limit=0,
#    opt_min_rows=False,
#)(raw_fib)
#cpm_fib_no_c = cpmoptimize(
#    strict=True, iters_limit=0,
#    opt_clear_stack=False,
#)(raw_fib)
cpm_fib = cpmoptimize(
    strict=True, iters_limit=0,
)(raw_fib)

def mat_fib(n):
    # Implementation via explicit fast matrix exponentiation
    
    if not n:
        return 0
    return (Matrix([
        [0, 1],
        [1, 1],
    ]) ** (n - 1)).content[1][1]

def _optimal_fib(n):
    # Returns (F[n], F[n + 1])

    if not n:
        return 0, 1
    a, b = _optimal_fib(n >> 1)
    c = a * (2 * b - a)
    d = b * b + a * a
    if n & 1:
        return d, c + d
    return c, d

def optimal_fib(n):
    # Implementation via explicit fast matrix exponentiation
    
    return _optimal_fib(n)[0]


if __name__ == '__main__':
    import core

    core.run(
        'fib', None,
        [
            ('raw', raw_fib),
            #('cpm -mc', cpm_fib_no_mc),
            #('cpm -m', cpm_fib_no_m),
            #('cpm -m', cpm_fib_no_c),
            ('cpm', cpm_fib),
            ('mat', mat_fib),
            ('optimal', optimal_fib),
        ],
        [
            ('small', 'linear', core.linear_scale(20000, 25)),
            ('big', 'linear', core.linear_scale(500000, 10)),
        ],
        True, True,
    )
