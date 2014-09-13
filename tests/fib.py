#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Calculate n-th number in Fibonacci sequence"""

import core

from cpmoptimize.matrices import Matrix

def naive(n):
    a = 0
    b = 1
    for i in xrange(n):
        a, b = b, a + b
    return a

def classic_matrixes(n):
    """Implementation via explicit fast matrix exponentiation"""
    
    if not n:
        return 0
    return (Matrix([
        [0, 1],
        [1, 1],
    ]) ** (n - 1)).content[1][1]

def _fast_doubling(n):
    # Returns (F[n], F[n + 1])
    
    if not n:
        return 0, 1
    a, b = _fast_doubling(n >> 1)
    c = a * (2 * b - a)
    d = b * b + a * a
    if n & 1:
        return d, c + d
    return c, d

def fast_doubling(n):
    """Fast doubling - implementation via matrix exponentiation
    with the redundant calculations removed."""
    
    return _fast_doubling(n)[0]

if __name__ == '__main__':
    # Test all functions on different testcases
    core.run(
        'fib', None,
        core.optimized(naive) + [
            ('matrixes', classic_matrixes),
            ('fast dbl', fast_doubling),
        ],
        [
            ('small', 'linear', core.linear_scale(30000, 15)),
            ('big', 'linear', core.linear_scale(300000, 15)),
        ],
    )
    
    # Test optimized function with different settings
    core.run(
        'fib', None,
        core.optimized(naive),
        [('demo', 'linear', core.linear_scale(60000, 30))],
    )
    core.run(
        'fib', None,
        core.optimized(naive, iters_limit=10000),
        [('border', 'linear', core.linear_scale(60000, 30))],
    )
    core.run(
        'fib', None,
        core.optimized(naive, try_options=True),
        [('options', 'linear', core.linear_scale(120000, 30))],
    )
