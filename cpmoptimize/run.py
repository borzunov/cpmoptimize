#!/usr/bin/env python
# -*- coding: utf-8 -*-

from itertools import izip

from matcode import *
from matrices import Matrix


class InvalidMatcodeError(RuntimeError):
    pass


def handle_mov(table, dest, src):
    table[dest[1]][dest[1]] = 0
    if src[0] == VALUE:
        table[-1][dest[1]] = src[1]
    else:
        table[src[1]][dest[1]] = 1

def handle_add(table, dest, src):
    if src[0] == VALUE:
        table[-1][dest[1]] = src[1]
    else:
        table[src[1]][dest[1]] = 1

def handle_sub(table, dest, src):
    if src[0] == VALUE:
        table[-1][dest[1]] = -src[1]
    else:
        table[src[1]][dest[1]] = -1

def handle_mul(table, dest, src):
    if src[0] == VALUE:
        table[dest[1]][dest[1]] = src[1]
    else:
        raise InvalidMatcodeError

matcode_map = {
    MOV: handle_mov,
    ADD: handle_add,
    SUB: handle_sub,
    MUL: handle_mul,
}


def skip_rows(mat):
    need_unit_row = False
    unskipped_indexes = []
    fix_mat = Matrix.identity(mat.rows)
    for index in xrange(mat.rows - 1):
        cur_row = mat.content[index]
        cur_col = [row[index] for row in mat.content]

        index_can_be_skipped = False
        prev_value_coeff = cur_col[index]
        const_coeff = cur_col[-1]
        # If an original value of a variable isn't used in calculations of
        # other variables and a new value doesn't depend on other variables
        if (
            all(elem == 0 for j, elem in enumerate(cur_row) if j != index) and
            all(elem == 0 for j, elem in enumerate(cur_col[:-1]) if j != index)
        ):
            # If a new variable value is a constant
            if prev_value_coeff == 0:
                handle_mov(fix_mat.content, (VAR, index), (VALUE, const_coeff))
                index_can_be_skipped = True
            # Or the value wasn't changed
            elif prev_value_coeff == 1 and const_coeff == 0:
                index_can_be_skipped = True

        if not index_can_be_skipped:
            unskipped_indexes.append(index)
            if const_coeff != 0:
                need_unit_row = True

    if need_unit_row:
        unskipped_indexes.append(mat.rows - 1)
    lite_content = []
    for y in unskipped_indexes:
        row = []
        for x in unskipped_indexes:
            row.append(mat.content[y][x])
        lite_content.append(row)
    return Matrix(lite_content), unskipped_indexes, fix_mat

def restore_rows(lite_mat, unskipped_indexes, fix_mat):
    mat = Matrix.identity(fix_mat.rows)
    for y, row in izip(unskipped_indexes, lite_mat.content):
        for x, elem in izip(unskipped_indexes, row):
            mat.content[y][x] = elem
    return mat * fix_mat


def run_loop(settings, matcode, index, vector_len):
    mat = Matrix.identity(vector_len)
    while True:
        instr = matcode[index]
        oper = instr[0]
        if oper == END:
            return mat, index

        try:
            if oper == LOOP:
                if len(instr) != 2 or instr[1][0] != VALUE:
                    raise InvalidMatcodeError
                sub_mat, index = run_loop(
                    settings, matcode, index + 1, vector_len,
                )

                need_min_rows = settings['opt_min_rows']
                if need_min_rows:
                    sub_mat, unskipped, fix_mat = skip_rows(sub_mat)
                cur_mat = sub_mat ** instr[1][1]
                if need_min_rows:
                    cur_mat = restore_rows(cur_mat, unskipped, fix_mat)
            else:
                if len(instr) != 3 or instr[1][0] != VAR:
                    raise InvalidMatcodeError
                cur_mat = Matrix.identity(vector_len)
                matcode_map[oper](cur_mat.content, instr[1], instr[2])
        except InvalidMatcodeError as err:
            if err.args:
                raise err
            raise InvalidMatcodeError((
                'Invalid matrix code instruction: %s'
            ) % ' '.join(map(repr, instr)))

        mat *= cur_mat
        index += 1


def run_matcode(settings, matcode, vector):
    mat = run_loop(settings, matcode, 0, len(vector))[0]
    return (Matrix([vector]) * mat).content[0]
