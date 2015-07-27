#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import warnings
from types import FunctionType

import byteplay

import hook
import recompiler


__author__ = 'Alexander Borzunov'
__version__ = '0.3.post2'


orig_xrange = xrange
xrange = hook.CPMRange


def analyze_loop(settings, code, index):
    instr = code[index]
    if not (
        instr[0] == byteplay.FOR_ITER and
        (index >= 2 and code[index - 2][0] == byteplay.GET_ITER)
    ):
        return 0
    # Now we found GET_ITER and FOR_ITER instructions

    # Try to find SETUP_LOOP
    for rel_index in orig_xrange(index - 3, -1, -1):
        if code[rel_index][0] == byteplay.SETUP_LOOP:
            setup_index = rel_index
            break
    else:
        return 0

    # Try to find JUMP_ABSOLUTE and POP_BLOCK by label from FOR_ITER
    pop_block_label = instr[1]
    for rel_index in orig_xrange(index + 1, len(code) - 1):
        if code[rel_index][0] is pop_block_label:
            pop_block_index = rel_index + 1
            break
    else:
        return 0
    if not (
        code[pop_block_index - 2][0] == byteplay.JUMP_ABSOLUTE and
        code[pop_block_index - 2][1] is code[index - 1][0] and
        code[pop_block_index][0] == byteplay.POP_BLOCK
    ):
        return 0
    # It's important to check POP_BLOCK instruction existence to
    # distinguish real for-loops from a list comprehensions

    # Try to find marker of current line's number
    for rel_index in orig_xrange(setup_index - 1, -1, -1):
        if code[rel_index][0] == byteplay.SetLineno:
            head_lineno = code[rel_index][1]
            break
    else:
        head_lineno = None

    head = code[setup_index + 1:index - 2]
    body = code[index + 1:pop_block_index - 2]
    # Don't forget that "else_body" loop part is also exists

    settings['head_lineno'] = head_lineno
    try:
        state = recompiler.recompile_body(settings, body)
    except recompiler.RecompilationError as err:
        if settings['verbose']:
            settings['logger'].debug(err)
        if settings['strict']:
            raise
        return 0

    # Insert head_handler right before GET_ITER instruction
    head_hook = hook.create_head_hook(state, pop_block_label)
    code[index - 2:index - 2] = head_hook

    if settings['verbose']:
        settings['logger'].debug('Recompilation successful')

    # Return length of analyzed code
    return len(head_hook)


def patch_copied_func(func, new_code):
    return FunctionType(
        new_code, func.func_globals, name=func.func_name,
        argdefs=func.func_defaults, closure=func.func_closure,
    )


def remove_excess_line_numbers(code):
    # CPython < 2.7 and PyPy add excess SetLineno instructions in some places
    # that break search of loops.

    excess_instructions_indexes = []
    cur_line_number = None
    for index, instr in enumerate(code):
        if instr[0] == byteplay.SetLineno:
            new_line_number = instr[1]
            if cur_line_number == new_line_number:
                excess_instructions_indexes.append(index)
            else:
                cur_line_number = new_line_number

    for offset, index in enumerate(excess_instructions_indexes):
        index -= offset
        code[index:index + 1] = []


default_types = int, long
default_iters_limit = 5000
min_iters_limit = 2

def cpmoptimize(
    strict=False, iters_limit=default_iters_limit, types=default_types,
    opt_min_rows=True, opt_clear_stack=True,
    verbose=False,
):
    iters_limit = max(iters_limit, min_iters_limit)
    if not isinstance(verbose, bool):
        warnings.warn('Starting with cpmoptimize 0.3, "verbose" parameter '
                      'must be of type "bool" (now "logging" module is '
                      'always used for debug messages)')
    params = locals()

    def upgrade_func(func):
        settings = params.copy()

        func_code = func.func_code
        settings['function_info'] = '%s, file "%s"' % (func_code.co_name,
                                                       func_code.co_filename)

        if settings['verbose']:
            settings['logger'] = logging.LoggerAdapter(
                    logging.getLogger(__name__),
                    {'function_info': settings['function_info']})

        internals = byteplay.Code.from_code(func_code)
        code = internals.code

        remove_excess_line_numbers(code)

        index = 0
        while index < len(code):
            index += analyze_loop(settings, code, index) + 1

        return patch_copied_func(func, internals.to_code())

    return upgrade_func


RecompilationError = recompiler.RecompilationError


__all__ = ['cpmoptimize', 'xrange', 'RecompilationError']
