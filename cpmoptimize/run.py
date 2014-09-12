#!/usr/bin/env python
# -*- coding: utf-8 -*-

from itertools import izip

from matcode import *
from matrices import Matrix


class MatcodeFoldingError(RuntimeError):
    pass

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
    transposed = mat.transposed()
    fix_mat = Matrix.identity(mat.rows)
    unskipped_indexes = []
    need_unit_row = False
    for x, col in enumerate(transposed.content[:-1]):
        is_prev_value_used = False
        for y, elem in enumerate(col[:-1]):
            # Let's explicity check element's equality to zero
            # (in theory element can have another type than "int")
            if elem != 0:
                if y == x and elem == 1:
                    # Variable's value depends from previous value
                    is_prev_value_used = True
                else:
                    # Variable's value depends from values of another
                    # variables or depends from previous value but used
                    # multiplication
                    break
        else:
            if (
                # If variable is unchanged
                (is_prev_value_used and col[-1] == 0) or
                # Or variable has assigned to constant value
                not is_prev_value_used
            ):
                if not is_prev_value_used:
                    handle_mov(fix_mat.content, (VAR, x), (VALUE, col[-1]))
                
                for index, elem in enumerate(mat.content[x]):
                    if elem != 0 and index != x:
                        raise MatcodeFoldingError(
                            'Folded variable is used in calculations ' +
                            'of another variables'
                        )
                continue
        
        unskipped_indexes.append(x)
        if col[-1] != 0:
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
                    rows_count = sub_mat.rows
                    sub_mat, unskipped, fix_mat = skip_rows(sub_mat)
                cur_mat = sub_mat ** instr[1][1]
                if need_min_rows:
                    cur_mat = restore_rows(cur_mat, unskipped, fix_mat)
            else:
                if len(instr) != 3 or instr[1][0] != VAR:
                    raise InvalidMatcodeError
                cur_mat = Matrix.identity(vector_len)
                matcode_map[oper](cur_mat.content, instr[1], instr[2])
        except (InvalidMatcodeError, KeyError, TypeError) as err:
            if isinstance(err, InvalidMatcodeError) and err.args:
                raise err
            raise InvalidMatcodeError((
                'Invalid matrix code instruction: %s'
            ) % ' '.join(map(repr, instr)))
    
        mat *= cur_mat
        index += 1


def run_matcode(settings, matcode, vector):
    mat = run_loop(settings, matcode, 0, len(vector))[0]
    return (Matrix([vector]) * mat).content[0]
