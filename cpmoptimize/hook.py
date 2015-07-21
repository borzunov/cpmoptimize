#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

python_version = sys.version_info

import byteplay

import run
from matcode import *


class CPMRange(object):
    # Built-in xrange iterator in Python 2 doesn't support "long" type.
    # This is replacement for it. All abilities of original xrange are
    # saved (this implementation almost completely passes Python 2.7.8
    # xrange unit tests, see file "test_xranges.py").

    def __init__(self, arg1, arg2=None, step=1):
        if arg2 is None:
            arg1, arg2 = 0, arg1
        for arg in (arg1, arg2, step):
            if isinstance(arg, float):
                raise TypeError('integer argument expected, got float')
            if not isinstance(arg, (int, long)):
                raise TypeError('an integer is required')
        if step == 0:
            raise ValueError('arg 3 must not be zero')

        rem = (arg2 - arg1) % step
        if rem != 0:
            arg2 += step - rem
        if cmp(arg1, arg2) != cmp(0, step):
            arg2 = arg1
        self._start, self._stop, self._step = arg1, arg2, step

    def __iter__(self):
        number = self._start
        while cmp(number, self._stop) == cmp(0, self._step):
            yield number
            number += self._step


    def __contains__(self, value):
        if value == self._start:
            return self._start != self._stop
        if cmp(self._start, value) != cmp(0, self._step):
            return False
        if cmp(value, self._stop) != cmp(0, self._step):
            return False
        return (value - self._start) % self._step == 0

    def __getitem__(self, key):
        if key < 0:
            key = self.__len__() + key
            if key < 0:
                raise IndexError('index out of range')
            return self[key]
        number = self._start + self._step * key
        if cmp(number, self._stop) != cmp(0, self._step):
            raise IndexError('index out of range')
        return number

    def __len__(self):
        return (self._stop - self._start) / self._step

    def __repr__(self):
        args = []
        if self._start != 0 or self._step != 1:
            args.append(self._start)
        args.append(self._stop)
        if self._step != 1:
            args.append(self._step)
        return 'xrange(%s)' % ', '.join(map(str, args))

    def __reversed__(self):
        return CPMRange(
            self._stop - self._step, self._start - self._step,
            -self._step,
        )


def check_iterable(settings, iterable):
    if not isinstance(iterable, (xrange, CPMRange)):
        raise TypeError(
            'Iterator has type %s instead of type "xrange"' % type(iterable)
        )

    iters_count = iterable.__len__()
    if iters_count <= settings['iters_limit']:
        if settings['verbose']:
            settings['logger'].debug("Execution of %s iterations wasn't "
                                     "optimized" % iters_count)
        return None

    start = iterable[0]
    step = iterable[1] - start
    last = iterable[-1]
    return start, step, iters_count, last

def get_var_space(straight, globals_dict, locals_dict):
    arg_type, name = straight
    if arg_type == NAME:
        if name not in locals_dict and name in globals_dict:
            return globals_dict
        return locals_dict
    if arg_type == GLOBAL:
        return globals_dict
    if arg_type in (FAST, DEREF):
        return locals_dict
    return None

var_undef_value = 0

def load_vars(settings, used_vars, globals_dict, locals_dict):
    vector = []
    for straight in used_vars:
        space = get_var_space(straight, globals_dict, locals_dict)
        name = straight[1]
        try:
            value = space[name]
            check_value = True
            vector.append(value)
        except (TypeError, KeyError):
            check_value = False
            vector.append(var_undef_value)

        if check_value and not isinstance(value, settings['types']):
            allowed_types = ', '.join(map(repr, settings['types']))
            raise TypeError((
                'Variable "%s" has an unallowed type %s instead of ' +
                'one of allowed types: %s'
            ) % (name, type(value), allowed_types))
    return vector


def define_values(matcode, folded, params):
    new_matcode = []
    for instr in matcode:
        new_instr = [instr[0]]
        for index in xrange(1, len(instr)):
            arg = instr[index]
            arg_type, value = arg
            if arg_type == CONST:
                new_arg = VALUE, folded[value]
            elif arg_type == PARAM:
                new_arg = VALUE, params[value]
            else:
                new_arg = arg
            new_instr.append(new_arg)
        new_matcode.append(new_instr)
    return new_matcode


def exec_loop(
    iterable, settings, matcode, used_vars, real_vars_indexes,
    need_store_counter, globals_dict, locals_dict, folded,
):
    try:
        # Check whether an iterable has type "xrange" and the required
        # number of iterations
        range_params = check_iterable(settings, iterable)
        if range_params is None:  # If the number of iterations is too little
            return None
        start, step, iters_count, last = range_params

        # Load necessary variables, check their types and make a vector
        # for further operations with matrixes (including a unit row)
        vector = load_vars(
            settings, used_vars, globals_dict, locals_dict,
        ) + [1]
    except TypeError as err:
        generic_err = TypeError("Can't run optimized loop: %s" % err)
        if settings['verbose']:
            settings['logger'].debug(generic_err)
        if settings['strict']:
            raise generic_err
        return None

    # Define constant values in matrix code
    matcode = define_values(matcode, folded, {
        'start': start, 'step': step, 'iters_count': iters_count,
    })

    matcode.append([END])

    # Run matrix code
    vector = run.run_matcode(settings, matcode, vector)

    if settings['verbose']:
        settings['logger'].debug('Execution of %s iterations was optimized '
                                 'successfully' % iters_count)

    # Pack values of real variables to a list. It will be unpacked in
    # a main function to values that will be assigned to the
    # globals and the locals. We can't just modify `locals_dict`
    # because locals() dictionary is read-only.
    packed = [vector[index] for index in real_vars_indexes]
    if need_store_counter:
        packed.append(last)
    return packed


def create_head_hook(state, loop_end_label):
    vars_storage = state.vars_storage
    real_vars_indexes = state.real_vars_indexes
    manual_store_counter = state.manual_store_counter

    unpacked_straight = []
    for index in real_vars_indexes:
        unpacked_straight.append(vars_storage[index])
    if manual_store_counter is not None:
        unpacked_straight.append(manual_store_counter)

    content = [
        (byteplay.DUP_TOP, None),
        (byteplay.LOAD_CONST, exec_loop),
        (byteplay.ROT_TWO, None),
        (byteplay.LOAD_CONST, state.settings),
        (byteplay.LOAD_CONST, state.content),
        (byteplay.LOAD_CONST, vars_storage),
        (byteplay.LOAD_CONST, real_vars_indexes),
        (byteplay.LOAD_CONST, manual_store_counter is not None),
        (byteplay.LOAD_CONST, globals),
        (byteplay.CALL_FUNCTION, 0),
        (byteplay.LOAD_CONST, locals),
        (byteplay.CALL_FUNCTION, 0),
        (byteplay.BUILD_LIST, 0),
        (byteplay.DUP_TOP, None),
        (byteplay.STORE_FAST, state.real_folded_arr),
    ]
    if python_version < (2, 7):
        for folded_code in state.consts:
            content += [
                (byteplay.DUP_TOP, None),
            ] + folded_code + [
                (byteplay.LIST_APPEND, None),
            ]
    else:
        for folded_code in state.consts:
            content += folded_code + [
                (byteplay.LIST_APPEND, 1),
            ]
    content += [
        (byteplay.CALL_FUNCTION, 9),
        (byteplay.DELETE_FAST, state.real_folded_arr),
        (byteplay.DUP_TOP, None),
        (byteplay.LOAD_CONST, None),
    ]
    head_end_label = byteplay.Label()

    # Let's "res" is a return value of "exec_loop".
    # Now the stack looks like:
    #     None, res, res, iterator, ...
    content += [
        (byteplay.COMPARE_OP, 'is not'),
    ]
    if python_version < (2, 7):
        content += [
            (byteplay.JUMP_IF_FALSE, head_end_label),
            (byteplay.POP_TOP, None),
        ]
    else:
        content += [
            (byteplay.POP_JUMP_IF_FALSE, head_end_label),
        ]

    # Code below runs if res is not None (optimization was successful).
    # Now the stack looks like:
    #     res, iterator, ...
    content += [
        (byteplay.UNPACK_SEQUENCE, len(unpacked_straight)),
    ]
    # Store changed variables
    for straight in unpacked_straight:
        content.append(
            (vars_opers_map[straight[0]][1], straight[1])
        )
    # We need to pop the iterator because the loop will be skipped
    content += [
        (byteplay.POP_TOP, None),
        (byteplay.JUMP_ABSOLUTE, loop_end_label),
    ]

    # Code below runs if res is None (optimization failed).
    # Now the stack looks like:
    #     None, iterator, ...           (in Python 2.7)
    #     False, None, iterator, ...    (in Python < 2.7)
    content += [
        (head_end_label, None),
        (byteplay.POP_TOP, None),
    ]
    if python_version < (2, 7):
        content += [
            (byteplay.POP_TOP, None),
        ]
    # Right before the loop (before GET_ITER instruction) iterator
    # must be at the top of the stack.
    return content
