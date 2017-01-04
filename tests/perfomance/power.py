#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tests_common as common


base = 78


def naive(n):
    res = 1
    for i in xrange(n):
        res *= base
    return res


def binary_exp(n):
    """Binary exponentiation algorithm"""

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


def built_in(n):
    return base ** n


if __name__ == '__main__':
    common.run(
        'power', None,
        common.optimized(naive) + [
            ('binary', binary_exp),
            ('built-in', built_in),
        ],
        [
            (None, 'linear', common.linear_scale(10000, 15)),
        ],
    )
