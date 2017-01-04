#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tests_common as common


# Some global constant
global_const = 4


def naive(n):
    # Definition of using some global variable
    global global_var

    # Some local constants
    local_const = 9
    k1_base = 4
    k1_or = 32
    k2 = 3
    offset = -43

    # Some variables
    a = 1
    b = 2
    res = 0
    # Test complex "xrange" expression
    # in loop with used but not modified counter
    for i in xrange(n, -143, -23):
        # Test stack usage and expressions processing
        a, b = b, a
        a, b = b, (a + b * (k1_base | k1_or)) * k2 + offset
        c = b

        # Test unary operations with constants
        d = 4348
        d -= +d
        d += -d
        d -= not local_const
        d += ~global_const

        # Test unary operations with variables
        c = +c
        c = -c

        # Test binary operations with constants
        e = 8944
        e -= local_const ** global_const
        e += local_const * global_const
        e -= local_const / global_const
        e += local_const // global_const
        e -= local_const % global_const
        e += local_const + global_const
        e -= local_const - global_const
        e += local_const >> global_const
        e -= local_const & global_const
        e += local_const ^ global_const
        e -= local_const | global_const
        g = f = e

        # Execute some namescope resolutions
        global_var = g
        local_var = global_var

        # Test binary operations with variables
        h = d - e
        loop_const = 321
        h = g * loop_const + d * local_const + a * loop_const + i
        a += h
        a += i
        res += a
    else:
        # Test "else" case
        res += 8943 * (res ^ 2321)
    # Test that local and global variables were successfully assigned
    # after the ending of the loop
    res += global_var + local_var

    r = 3
    # Loop with unused counter
    for it1 in xrange(-3231, n):
        r = r - 33 + d * 2

    q = 43
    # Loop with used and modified counter
    for it2 in xrange(-3231, n, 4345):
        q = (3 + 4) * q - (it2 * 2 - 8) * 3
        it2 = q + 3 - e

    # Empty loop
    for it3 in xrange(n):
        pass

    # Return ordered list with values of all local variables
    return tuple(sorted(locals().items(), key=lambda item: item[0]))


if __name__ == '__main__':
    common.run(
        'int_operations', None,
        common.optimized(naive),
        [
            (None, 'linear', common.linear_scale(600000, 15)),
        ],
    )
