#!/usr/bin/env python
# -*- coding: utf-8 -*-

import byteplay


# Make constants from enumerate in globals
def make_enum(variants):
    class Variant(int):
        def __repr__(self):
            return variants[self]

        __str__ = __repr__

    for index, elem in enumerate(variants):
        globals()[elem] = Variant(index)


# Operations in matrix code
matcode_opers = 'MOV ADD SUB MUL LOOP END'.split()
make_enum(matcode_opers)

# Types of arguments in matrix code
matcode_arg_types = ' '.join([
    # Raw constant value
    'VALUE',

    # Folded constant ID
    'CONST',
    # Named constant for various parameters
    'PARAM',

    # Straight variable references
    'NAME GLOBAL FAST DEREF',
    # Variable for loop's counter
    'COUNTER',
    # References to relative stack position
    'TOS FOLD_TOS',
    # List of instructions that makes folded constant value
    'FOLD',

    # Reference to absolute stack position
    'STACK',

    # Unified mutable variable ID
    'VAR',
]).split()
make_enum(matcode_arg_types)
# Lifecycle of arguments:
#   1). Before creating a matcode some constants are folded using
#       method "recompiler.RecompilerState.add_const" from type "FOLD"
#       to type "CONST". This may occur in method
#       `recompiler.handle_store_var`.
#   2). There are types used in the matcode generation and passed to method
#       `recompiler.RecompilerState.append`:
#           VALUE
#           CONST PARAM
#           NAME GLOBAL FAST DEREF COUNTER TOS FOLD_TOS
#   3). During recompilation, firstly relative stack references with type
#       "TOS" are replaced by absolute references with type
#       "STACK". Then arguments with types "NAME", "GLOBAL", "FAST",
#       "DEREF", "COUNTER" and "STACK" are replaced by arguments with
#       type "VAR", and arguments with type "FOLD_TOS" are replaced by
#       arguments with type "CONST". This occurs in private method
#       `recompiler.RecompilerState._translate_arg`.
#   4). So, there are types used in the matcode after the recompilation and
#       passed to function `hook.exec_loop`:
#           VALUE
#           CONST PARAM
#           VAR
#   5). During run-time, constant references with types "CONST" and
#       "PARAM" are replaced by their values (only at this moment they have
#       become known) with type "VALUE". This occurs in function
#       `hook.define_values`.
#   6). So, there are types used in the matcode before its running and passed
#       to function `run.run_matcode`:
#           VALUE
#           VAR

# Map from a variable type to bytecode operations working with it
vars_opers_map = {
    NAME: (byteplay.LOAD_NAME, byteplay.STORE_NAME),
    GLOBAL: (byteplay.LOAD_GLOBAL, byteplay.STORE_GLOBAL),
    FAST: (byteplay.LOAD_FAST, byteplay.STORE_FAST),
    DEREF: (byteplay.LOAD_DEREF, byteplay.STORE_DEREF),
}

# Make map from bytecode operation to variable type and status (is this
# variable mutable in this operation)
vars_types_map = {}
for arg_type, opers in vars_opers_map.items():
    for index, oper in enumerate(opers):
        vars_types_map[oper] = arg_type, bool(index)


__all__ = matcode_opers + matcode_arg_types + [
    'vars_opers_map', 'vars_types_map',
]
