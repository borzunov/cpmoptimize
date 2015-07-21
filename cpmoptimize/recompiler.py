#!/usr/bin/env python
# -*- coding: utf-8 -*-

import byteplay

from matcode import *



class RecompilationError(Exception):
    def __init__(self, message, state):
        self.message = "Can't optimize loop: %s" % message
        if state.lineno is not None:
            self.message += ' at line %s' % state.lineno
        self.message += ' in %s' % state.settings['function_info']

    def __str__(self):
        return self.message


class UnpredictableArgsError(Exception):
    pass


class RecompilerState(object):
    def __init__(self, settings):
        self._settings = settings
        self.lineno = settings['head_lineno']

        self.stack = []
        self._content = []
        # List of straight references of all used variables
        self._vars_storage = []
        # List of indexes of really existing variables in
        # self._vars_storage (we need to save their values at the end of
        # the loop)
        self._real_vars_indexes = []
        # Map from a straight variable reference to a pair of variable
        # index in a unified storage (actually in
        # self._vars_storage) and its effective unified
        # reference (VAR, index) or (CONST, const_no)
        self._vars_map = {}
        # Storage for folded instructions sets of constants. This
        # instructions will be executed during run-time once. Calculated
        # values will be inserted into matrices.
        self._consts = []

    @property
    def settings(self):
        return self._settings

    @property
    def content(self):
        return self._content

    @property
    def consts(self):
        return self._consts

    @property
    def vars_storage(self):
        return self._vars_storage

    @property
    def real_vars_indexes(self):
        return self._real_vars_indexes

    _real_folded_arr = '__cpm::folded'

    @property
    def real_folded_arr(self):
        return self._real_folded_arr

    def add_const(self, straight):
        arg_type, arg = straight
        if arg_type == FOLD_TOS:
            lines = self.stack[-arg - 1]
            if lines is None:
                raise ValueError(
                    'Unpredictable value to fold for FOLD_TOS'
                )
        elif arg_type == FOLD:
            lines = arg
        else:
            raise ValueError((
                "Can't add constant from argument with type %s " +
                "to matrix code"
            ) % arg_type)
        index = len(self._consts)
        self._consts.append(lines)
        return CONST, index

    def add_var(self, straight, mutation):
        # If a variable was changed at least once in a loop's body, we need
        # mark it as mutable at the beginning of compilation.
        # During the compilation its value can become predictable.
        try:
            index, unified = self._vars_map[straight]

            if mutation and unified[0] != VAR:
                unified = VAR, index
                self.store_var(straight, unified)
        except KeyError:
            index = len(self._vars_storage)
            self._vars_storage.append(straight)
            var_type = straight[0]
            if var_type in (NAME, GLOBAL, FAST, DEREF):
                self._real_vars_indexes.append(index)

            if mutation:
                unified = VAR, index
            else:
                load_oper = vars_opers_map[var_type][0]
                unified = self.add_const((FOLD, [
                    (load_oper, straight[1]),
                ]))
            self._vars_map[straight] = [index, unified]
        return unified

    def _translate_arg(self, arg):
        # Translate argument of types used in matcode generation to
        # argument with type VALUE, CONST or VAR (make unified
        # reference from straight)

        arg_type = arg[0]

        if arg_type in (VALUE, CONST, PARAM):
            return arg
        if arg_type == FOLD_TOS:
            return self.add_const(arg)

        if arg_type not in vars_opers_map.keys() + [COUNTER, TOS]:
            raise ValueError((
                "Can't add variable from argument with type %s " +
                "to matrix code"
            ) % arg_type)
        if arg_type == TOS:
            # If argument type was TOS, translate it to argument with
            # type STACK first (make absolute reference from relative)
            arg = STACK, len(self.stack) - 1 - arg[1]
        return self.add_var(arg, True)

    def append(self, *instrs):
        for instr in instrs:
            oper = instr[0]
            args = map(self._translate_arg, instr[1:])
            self._content.append([oper] + args)

    def load_var(self, straight):
        return self._vars_map[straight][1]

    def store_var(self, straight, unified):
        self._vars_map[straight][1] = unified



def handle_nop(state, instr):
    pass

def handle_pop_top(state, instr):
    state.stack.pop()

def create_rot(count):
    def handle_rot(state, instr):
        for index in xrange(-1, count - 1):
            if state.stack[-index - 2] is None:
                state.append(
                    [MOV, (TOS, index), (TOS, index + 1)],
                )
        if state.stack[-1] is None:
            state.append(
                [MOV, (TOS, count - 1), (TOS, -1)],
            )
        if state.settings['opt_clear_stack']:
            # Stack clearing is busy because program will works
            # slower if big values will remains on the stack
            state.append(
                [MOV, (TOS, -1), (VALUE, 0)],
            )

        state.stack[-count:] = (
            [state.stack[-1]] + state.stack[-count:-1]
        )
    return handle_rot

def create_dup(count):
    def handle_dup(state, instr):
        for index in xrange(count):
            if state.stack[-count + index] is None:
                state.append(
                    [MOV, (TOS, index - count), (TOS, index)],
                )

        state.stack += state.stack[-count:]
    return handle_dup

def handle_dup_topx(state, instr):
    create_dup(instr[1])(state, instr)

def handle_unary_negative(state, instr):
    if state.stack[-1] is not None:
        state.stack[-1].append(instr)
    else:
        state.append(
            [MOV, (TOS, -1), (TOS, 0)],
            [MOV, (TOS, 0), (VALUE, 0)],
            [SUB, (TOS, 0), (TOS, -1)],
        )
        if state.settings['opt_clear_stack']:
            state.append(
                [MOV, (TOS, -1), (VALUE, 0)],
            )

def handle_unary_const(state, instr):
    if state.stack[-1] is not None:
        state.stack[-1].append(instr)
    else:
        raise UnpredictableArgsError


def handle_binary_multiply(state, instr):
    if state.stack[-2] is not None and state.stack[-1] is not None:
        state.stack[-2] += state.stack[-1] + [instr]
        state.stack.pop()
    elif state.stack[-2] is not None:
        state.append(
            [MUL, (TOS, 0), (FOLD_TOS, 1)],
            [MOV, (TOS, 1), (TOS, 0)],
        )
        if state.settings['opt_clear_stack']:
            state.append(
                [MOV, (TOS, 0), (VALUE, 0)],
            )

        state.stack[-2] = None
        state.stack.pop()
    elif state.stack[-1] is not None:
        state.append(
            [MUL, (TOS, 1), (FOLD_TOS, 0)],
        )

        state.stack.pop()
    else:
        raise RecompilationError((
            'Multiplication of two unpredictable values is unsupported'
        ), state)

def handle_binary_add(state, instr):
    if state.stack[-2] is not None and state.stack[-1] is not None:
        state.stack[-2] += state.stack[-1] + [instr]
        state.stack.pop()
    elif state.stack[-2] is not None:
        state.append(
            [ADD, (TOS, 0), (FOLD_TOS, 1)],
            [MOV, (TOS, 1), (TOS, 0)],
        )
        if state.settings['opt_clear_stack']:
            state.append(
                [MOV, (TOS, 0), (VALUE, 0)],
            )

        state.stack[-2] = None
        state.stack.pop()
    elif state.stack[-1] is not None:
        state.append(
            [ADD, (TOS, 1), (FOLD_TOS, 0)],
        )

        state.stack.pop()
    else:
        state.append(
            [ADD, (TOS, 1), (TOS, 0)],
        )
        if state.settings['opt_clear_stack']:
            state.append(
                [MOV, (TOS, 0), (VALUE, 0)],
            )

        state.stack.pop()

def handle_binary_subtract(state, instr):
    if state.stack[-2] is not None and state.stack[-1] is not None:
        state.stack[-2] += state.stack[-1] + [instr]
        state.stack.pop()
    elif state.stack[-2] is not None:
        state.append(
            [SUB, (TOS, 0), (FOLD_TOS, 1)],
            [MOV, (TOS, 1), (VALUE, 0)],
            [SUB, (TOS, 1), (TOS, 0)],
        )
        if state.settings['opt_clear_stack']:
            state.append(
                [MOV, (TOS, 0), (VALUE, 0)],
            )

        state.stack[-2] = None
        state.stack.pop()
    elif state.stack[-1] is not None:
        state.append(
            [SUB, (TOS, 1), (FOLD_TOS, 0)],
        )

        state.stack.pop()
    else:
        state.append(
            [SUB, (TOS, 1), (TOS, 0)],
        )
        if state.settings['opt_clear_stack']:
            state.append(
                [MOV, (TOS, 0), (VALUE, 0)],
            )

        state.stack.pop()

def handle_binary_const(state, instr):
    if state.stack[-2] is not None and state.stack[-1] is not None:
        state.stack[-2] += state.stack[-1] + [instr]
        state.stack.pop()
    else:
        raise UnpredictableArgsError


def handle_load_const(state, instr):
    arg = instr[1]
    if not isinstance(arg, state.settings['types']):
        allowed_types = ', '.join(map(repr, state.settings['types']))
        raise RecompilationError((
            'Constant %s has an unallowed type %s instead of ' +
            'one of allowed types: %s'
        ) % (repr(arg), type(arg), allowed_types), state)
    state.stack.append([instr])

def handle_load_var(state, instr):
    oper, name = instr
    straight = vars_types_map[oper][0], name
    unified = state.load_var(straight)
    if unified[0] == CONST:
        state.stack.append([
            (byteplay.LOAD_FAST, state.real_folded_arr),
            (byteplay.LOAD_CONST, unified[1]),
            (byteplay.BINARY_SUBSCR, None),
        ])
    else:
        state.append(
            [MOV, (TOS, -1), straight],
        )

        state.stack.append(None)

def handle_store_var(state, instr):
    oper, name = instr
    straight = vars_types_map[oper][0], name
    lines = state.stack[-1]
    if lines is not None:
        if (
            len(lines) == 3 and
            lines[0] == (byteplay.LOAD_FAST, state.real_folded_arr) and
            lines[1][0] == byteplay.LOAD_CONST and
            isinstance(lines[1][1], int) and
            lines[2] == (byteplay.BINARY_SUBSCR, None)
        ):
            const_ref = CONST, lines[1][1]
        else:
            const_ref = state.add_const((FOLD_TOS, 0))
        state.append(
            [MOV, straight, const_ref],
        )
        state.store_var(straight, const_ref)
    else:
        state.append(
            [MOV, straight, (TOS, 0)],
        )
        if state.settings['opt_clear_stack']:
            state.append(
                [MOV, (TOS, 0), (VALUE, 0)],
            )
        state.store_var(straight, straight)

    state.stack.pop()


load_opers, store_opers = zip(*vars_opers_map.values())
bytecode_handlers = [
    (handle_nop, [byteplay.NOP]),
    (handle_pop_top, [byteplay.POP_TOP]),
    (create_rot(2), [byteplay.ROT_TWO]),
    (create_rot(3), [byteplay.ROT_THREE]),
    (create_rot(4), [byteplay.ROT_FOUR]),
    (create_dup(1), [byteplay.DUP_TOP]),

    (handle_nop, [byteplay.UNARY_POSITIVE]),
    (handle_unary_negative, [byteplay.UNARY_NEGATIVE]),
    (handle_unary_const, [
        byteplay.UNARY_NOT, byteplay.UNARY_INVERT,
    ]),

    (handle_binary_const, [byteplay.BINARY_POWER]),
    (handle_binary_multiply, [byteplay.BINARY_MULTIPLY]),
    (handle_binary_const, [
        byteplay.BINARY_DIVIDE, byteplay.BINARY_FLOOR_DIVIDE,
        byteplay.BINARY_TRUE_DIVIDE, byteplay.BINARY_MODULO,
    ]),
    (handle_binary_add, [byteplay.BINARY_ADD]),
    (handle_binary_subtract, [byteplay.BINARY_SUBTRACT]),
    (handle_binary_const, [
        byteplay.BINARY_LSHIFT, byteplay.BINARY_RSHIFT,
        byteplay.BINARY_AND, byteplay.BINARY_XOR, byteplay.BINARY_OR,
    ]),

    (handle_binary_const, [byteplay.INPLACE_POWER]),
    (handle_binary_multiply, [byteplay.INPLACE_MULTIPLY]),
    (handle_binary_const, [
        byteplay.INPLACE_DIVIDE, byteplay.INPLACE_FLOOR_DIVIDE,
        byteplay.INPLACE_TRUE_DIVIDE, byteplay.INPLACE_MODULO,
    ]),
    (handle_binary_add, [byteplay.INPLACE_ADD]),
    (handle_binary_subtract, [byteplay.INPLACE_SUBTRACT]),
    (handle_binary_const, [
        byteplay.INPLACE_LSHIFT, byteplay.INPLACE_RSHIFT,
        byteplay.INPLACE_AND, byteplay.INPLACE_XOR, byteplay.INPLACE_OR,
    ]),

    (handle_dup_topx, [byteplay.DUP_TOPX]),
    (handle_load_const, [byteplay.LOAD_CONST]),
    (handle_load_var, load_opers),
    (handle_store_var, store_opers),
]

supported_opers = {}
for handler, opers in bytecode_handlers:
    for oper in opers:
        supported_opers[oper] = handler



def browse_vars(state, body):
    # Browse used in loop's body variables to determine their mutability
    for oper, arg in body:
        try:
            arg_type, mutation = vars_types_map[oper]
            state.add_var((arg_type, arg), mutation)
        except KeyError:
            pass

def browse_counter(state, body):
    store_instr = body[0]
    oper, name = store_instr
    try:
        arg_type, mutation = vars_types_map[oper]
        if not mutation:
            raise KeyError
    except KeyError:
        raise RecompilationError((
            'Unsupported iterator usage in instruction %s' % repr(instr)
        ), state)
    load_instr = vars_opers_map[arg_type][0], name

    if state.settings['opt_min_rows']:
        status = 'n' # Return 'n' if loop's counter isn't used
        for index in xrange(1, len(body)):
            instr = body[index]
            if instr == store_instr:
                status = 'w' # Return 'w' if counter
                             # is changed at least once
                break
            if instr == load_instr:
                status = 'r' # Return 'r' if counter
                             # isn't changed but was read at least once
    else:
        status = 'w'
    return (arg_type, name), status, body[1:]

def recompile_body(settings, body):
    state = RecompilerState(settings)

    elem_straight, counter_status, rem_body = browse_counter(
        state, body,
    )
    if counter_status == 'w':
        # If real counter is mutable, we need special variable to
        # store real counter value
        counter_service = COUNTER, None
    elif counter_status == 'r':
        # If real counter isn't mutable but used, we need to
        # maintain its value
        counter_service = elem_straight
    if counter_status == 'n':
        # If real counter isn't used at all, we don't need to
        # maintain this variable in the loop, but we need to save
        # its final value after the loop
        state.manual_store_counter = elem_straight
    else:
        # We must mark real counter as mutable at the beginning of the
        # loop, because first instruction (counter storing) was removed
        # from rem_body and system doesn't know that counter is mutable
        state.add_var(elem_straight, True)
        state.manual_store_counter = None

    browse_vars(state, rem_body)

    if counter_status != 'n':
        state.append(
            [MOV, counter_service, (PARAM, 'start')],
        )
    state.append(
        [LOOP, (PARAM, 'iters_count')],
    )
    if counter_status == 'w':
        state.append(
            [MOV, elem_straight, (COUNTER, None)],
        )

    for instr in rem_body:
        oper = instr[0]
        if oper == byteplay.SetLineno:
            state.lineno = instr[1]
            continue

        try:
            supported_opers[oper](state, instr)
        except UnpredictableArgsError:
            raise RecompilationError((
                'All operands of instruction %s must be a constant ' +
                'or must have a predictable value'
            ) % oper, state)
        except IndexError:
            raise RecompilationError((
                'Unsupported loop type or invalid stack usage in bytecode'
            ), state)
        except KeyError:
            raise RecompilationError((
                'Unsupported instruction %s'
            ) % repr(instr), state)

    if counter_status != 'n':
        state.append(
            [ADD, counter_service, (PARAM, 'step')],
        )
    state.append(
        [END],
    )
    if counter_status == 'r':
        state.append(
            [SUB, counter_service, (PARAM, 'step')],
        )
    return state
