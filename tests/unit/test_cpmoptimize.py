#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import dis
import itertools
import os
import sys

python_version = sys.version_info

if python_version < (2, 7):
    import unittest2 as unittest
else:
    import unittest

sys.path.append(os.path.join(os.path.pardir, os.path.pardir))
from cpmoptimize import cpmoptimize
from cpmoptimize.recompiler import RecompileError


LOOP_ITERATIONS = 12345


def generalized_fib_func(a_start, iterator):
    a = a_start
    b = 1
    for i in iterator:
        a, b = b, a + b
    return a


def dump_locals(dictionary):
    return tuple(sorted(dictionary.items(), key=lambda item: item[0]))


def check_correctness(args=[], kwargs={}, iters_limit=0):
    def decorator(func):
        def testcase_method(self):
            expected = func(*args, **kwargs)
            options_variants = itertools.product([False, True], repeat=2)
            actual_variants = []
            for opt_min_rows, opt_clear_stack in options_variants:
                bound_decorator = cpmoptimize(
                    strict=True, iters_limit=iters_limit,
                    opt_min_rows=opt_min_rows,
                    opt_clear_stack=opt_clear_stack)
                actual_variants.append(bound_decorator(func)(*args, **kwargs))

            for actual in actual_variants:
                self.assertEqual(expected, actual)

        testcase_method.func_name = func.func_name
        testcase_method.func_doc = func.func_doc
        return testcase_method

    return decorator


GLOBAL_CONST = 43
global_var = 894


class TestIntCalculations(unittest.TestCase):
    @check_correctness()
    def test_complex_expressions():
        a = 12
        b = 22
        c = 32
        d = 42
        e = 52
        f = 62
        offset = -433
        res = 0

        for i in xrange(LOOP_ITERATIONS):
            a, b, c = b, c, a
            a, b = b, (a + b * (d | e)) * f + offset
            res = b

        return dump_locals(locals())

    @check_correctness()
    def test_unary_ops_with_constants():
        local_const = 9
        d = 4348

        for i in xrange(LOOP_ITERATIONS):
            d += -local_const
            d += +GLOBAL_CONST
            d += not local_const
            d += ~GLOBAL_CONST

        return dump_locals(locals())

    @check_correctness()
    def test_unary_ops_with_variables():
        c = 899
        d = 654

        for i in xrange(LOOP_ITERATIONS):
            c = c * 2 - 434
            d = d * 3 - 326

            c += -d
            d += +c

        return dump_locals(locals())

    @check_correctness()
    def test_binary_ops_with_constants():
        local_const = 328
        e = 8944

        for i in xrange(LOOP_ITERATIONS):
            e -= local_const ** GLOBAL_CONST
            e += local_const * GLOBAL_CONST
            e -= local_const / GLOBAL_CONST
            e += local_const // GLOBAL_CONST
            e -= local_const % GLOBAL_CONST
            e += local_const + GLOBAL_CONST
            e -= local_const - GLOBAL_CONST
            e += local_const >> GLOBAL_CONST
            e -= local_const & GLOBAL_CONST
            e += local_const ^ GLOBAL_CONST
            e -= local_const | GLOBAL_CONST
            g = f = e

        return dump_locals(locals())

    @check_correctness()
    def test_binary_ops_with_variables():
        a = 4893
        b = 834

        for i in xrange(LOOP_ITERATIONS):
            loop_const = 321
            h = a * loop_const - b + i * GLOBAL_CONST
            a += h
            b -= i

        return dump_locals(locals())

    @check_correctness()
    def test_namespace_resolution():
        global global_var

        global_var = 392
        c = 324

        for i in xrange(LOOP_ITERATIONS):
            c = c * 8 + 311
            c -= global_var
            global_var = c
            local_var = global_var

        return dump_locals(locals())

    @check_correctness()
    def test_for_with_stop():
        a = 94
        res = 943
        start = 439
        stop = -3323

        for i in xrange(start, stop):
            res = res * 33 + a
            a -= res

        return dump_locals(locals())

    @check_correctness()
    def test_for_with_step():
        a = 94
        res = 943
        start = 439
        stop = -LOOP_ITERATIONS * 52 - 499
        step = 24

        for i in xrange(start, stop, step):
            res = res * 33 + a
            a -= res

        return dump_locals(locals())

    @check_correctness()
    def test_for_with_else():
        a = 94
        res = 943
        start = -a * 2
        stop = LOOP_ITERATIONS + res * 3

        for i in xrange(start, stop):
            res = res * 33 + a
            a -= res
        else:
            res += 78 - a * 3

        return dump_locals(locals())

    @check_correctness()
    def test_new_variables_after_loop():
        c = 899
        local_const = 654

        for i in xrange(LOOP_ITERATIONS):
            c = c * 2 - 434
            d = c + 43

        return dump_locals(locals())

    @check_correctness()
    def test_used_loop_counter():
        q = 43

        for counter in xrange(LOOP_ITERATIONS):
            q = (3 + 445) * q - (counter * 2 - 8) * 3

        return dump_locals(locals())

    @check_correctness()
    def test_modified_loop_counter():
        q = 43
        e = 7483

        for counter in xrange(LOOP_ITERATIONS):
            e = e - 89 * q
            q = (3 + 445) * q - (counter * 2 - 8) * 3
            counter = q + 3 - e
            q -= counter * 12

        return dump_locals(locals())

    @check_correctness()
    def test_empty_loop():
        for i in xrange(LOOP_ITERATIONS):
            pass

    @check_correctness()
    def test_opt_clear_stack():
        a = 12
        b = 22

        for i in xrange(LOOP_ITERATIONS):
            a, b = b * 2, a + b

        return dump_locals(locals())

    @check_correctness()
    def test_opt_min_rows():
        a = 12
        b = 22
        c = 32
        d = 42

        for i in xrange(LOOP_ITERATIONS):
            a, b = b, a + b
            b = a

            d += c
            c = 3
            d -= 32

        return dump_locals(locals())

    test_fib = check_correctness(
        args=(0, xrange(LOOP_ITERATIONS)))(generalized_fib_func)


def check_exception(exception, regexp, args=[], kwargs={}, iters_limit=0):
    def decorator(func):
        def testcase_method(self):
            options_variants = itertools.product([False, True], repeat=2)
            for opt_min_rows, opt_clear_stack in options_variants:
                bound_decorator = cpmoptimize(
                    strict=True, iters_limit=iters_limit,
                    opt_min_rows=opt_min_rows,
                    opt_clear_stack=opt_clear_stack)
                with self.assertRaisesRegexp(exception, regexp):
                    bound_decorator(func)(*args, **kwargs)

        testcase_method.func_name = func.func_name
        testcase_method.func_doc = func.func_doc
        return testcase_method

    return decorator


class TestExceptions(unittest.TestCase):
    @check_exception(RecompileError,
                     r"^Can't optimize loop: Unsupported instruction")
    def test_unsupported_instruction():
        res = 0
        for i in xrange(LOOP_ITERATIONS):
            if i < 100:
                res += 1
            else:
                res += 2
        return res

    @check_exception(RecompileError,
                     r"^Can't optimize loop: Multiplication of "
                     r"two unpredictable values is unsupported")
    def test_unpredictable_multiplication_operands():
        res = 1
        for i in xrange(LOOP_ITERATIONS):
            res *= res
        return res

    @check_exception(RecompileError,
                     r"^Can't optimize loop: All operands of instruction "
                     r".+ must be a constant or must have a predictable value")
    def test_unpredictable_binary_and_operands():
        res = 1
        for i in xrange(LOOP_ITERATIONS):
            res += res & i
        return res

    @check_exception(RecompileError,
                     r"^Can't optimize loop: Constant 'a' has an unallowed "
                     r"type .+ instead of one of allowed types")
    def test_unallowed_constant_type():
        res = ''
        for i in xrange(6000):
            res += 'a'
        return res

    test_unsupported_iterator_type = check_exception(
        TypeError, r"^Can't run optimized loop: "
                   r"Iterator has type .+ instead of ",
        args=(0, range(LOOP_ITERATIONS)))(generalized_fib_func)

    test_unallowed_variable_type = check_exception(
        TypeError, r"^Can't run optimized loop: "
                   r"Variable \"a\" has an unallowed type .+ instead of "
                   r"one of allowed types",
        args=(0.5, xrange(LOOP_ITERATIONS)))(generalized_fib_func)


class TestItersLimit(unittest.TestCase):
    test_disabled_optimization = check_correctness(
        args=(0.5, xrange(LOOP_ITERATIONS)),
        iters_limit=LOOP_ITERATIONS)(generalized_fib_func)
        # This test can be passed only if the optimization was disabled.
        # It would have fallen with TypeError (because variable "a" has
        # an unallowed type) otherwise.


if __name__ == '__main__':
    unittest.main()
