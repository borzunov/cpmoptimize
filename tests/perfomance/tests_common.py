#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import os
import sys
from time import time

sys.path.append(os.path.join(os.path.pardir, os.path.pardir))
from cpmoptimize import cpmoptimize


# Functions for making plots

support_plots = None

# Directory where plots will be saved
PLOTS_DIR = 'plots'


def init_plots():
    global plt, support_plots

    # Check whether plots drawing is already initialized
    if support_plots is not None:
        return

    # Check whether "matplotlib" library is installed
    try:
        import matplotlib.pyplot as plt
        support_plots = True
        print '[+] Matplotlib is found'
    except ImportError:
        support_plots = False
        print "[*] Matplotlib isn't found"
        return

    # If plots are supported, make directory for saving images
    try:
        os.makedirs(PLOTS_DIR)
        print '[+] Created directory "%s"' % PLOTS_DIR
    except OSError:
        # If directory already exists, do nothing
        pass


# Plots' size (in inches)
LINEAR_PLOT_SIZE = 6, 4
OTHER_PLOT_SIZE = 5, 5

# Font size for plots
LABEL_FONT_SIZE = 11
NORMAL_FONT_SIZE = 9


def make_plot(filename, title, arguments, methods, scale):
    if not support_plots:
        return

    is_linear = (scale == 'linear')

    plot_size = LINEAR_PLOT_SIZE if is_linear else OTHER_PLOT_SIZE
    plt.figure(figsize=plot_size)

    for name, func, measures in methods:
        plt.plot(arguments, measures, 'o-', label=name, markersize=3)

    if is_linear:
        axis = plt.axis()
        plt.axis((0, axis[1], 0, axis[3]))

    plt.xscale(scale)
    plt.yscale(scale)

    plt.xticks(fontsize=NORMAL_FONT_SIZE)
    plt.yticks(fontsize=NORMAL_FONT_SIZE)

    plt.grid(True)

    plt.title(title, fontsize=LABEL_FONT_SIZE)
    plt.xlabel('Argument', fontsize=NORMAL_FONT_SIZE)
    plt.ylabel('Time (seconds)', fontsize=NORMAL_FONT_SIZE)
    plt.legend(loc='upper left', fontsize=NORMAL_FONT_SIZE)

    plt.tight_layout(0.2)

    path = os.path.join(PLOTS_DIR, filename)
    plt.savefig(path)
    print '[*] Saved plot "%s"' % path


class Table(object):
    # Class for formatting simple tables in console output

    def __init__(self, cols):
        # "cols" must be a list of pairs of column name (it will be
        # used in table's head) and column width. Columns' values in
        # one line are filled to desired width by spaces. They also
        # will be separated by three-symbol delimiter " | " (first or
        # last space is skipped if cell is placed nead table side).

        self._cols = cols

    def head(self):
        # Print table's head (rows' titles)

        # Generate (and print) horizontal line consisting of dashes
        self._hor = '+'
        for name, width in self._cols:
            self._hor += '-' * (width + 2) + '+'
        print self._hor

        # Print table's head. Rows' names will be centered.
        line = '|'
        for name, width in self._cols:
            line += ' ' + name.center(width) + ' |'
        print line

        print self._hor

        # Make a variable for storing index of current column
        self._col_index = 0

    def append(self, data):
        # Fill next cell in the table

        try:
            # Convert table's cell to string and fill it to desired
            # width by spaces at the left
            elem = str(data).rjust(self._cols[self._col_index][1])

            line = ''
            if self._col_index == 0:
                # Usually delimiters are putted at the right of the
                # cell. If the cell is first in the row, we need also
                # put delimiter at the left.
                line += '|'
            line += ' ' + elem + ' |'
            if self._col_index == len(self._cols) - 1:
                # If the cell is last in the row, we need append
                # newline character.
                line += '\n'
            # Update screen after filling of every cell in the table
            sys.stdout.write(line)
            sys.stdout.flush()

            # Move to the next column. If this column was last in the
            # row, move to begin of the next row.
            self._col_index = (self._col_index + 1) % len(self._cols)
        except AttributeError:
            # If head weren't shown, column index is undefined
            raise AttributeError(
                "Need to print table's header before table's cols",
            )

    def footer(self):
        # Print table's footer

        try:
            # Print horizontal line
            print self._hor + '\n'
        except AttributeError:
            raise AttributeError(
                "Need to print table's header before table's footer",
            )


def measure_time(func, arg):
    start = time()
    data = func(arg)
    interval = time() - start
    return interval, data


# Functions for easy generating arguments case


def linear_scale(max_value, count):
    base = max_value / count
    return [base * i for i in xrange(count + 1)]


def log_scale(max_value, count):
    log_base = math.log(max_value) / count
    res = []
    for i in xrange(count + 1):
        res.append(int(round(math.exp(log_base * i))))
    return res


# Table's columns widths
ARG_COL_WIDTH = 6
CONTROL_COL_WIDTH = 8
COMPARED_COL_WIDTH = 12
COMPARED_COMMENT_WIDTH = 8
MATCH_COL_WIDTH = 5

# If argument of functions is lesser or equal this value, comparison of
# execution time of different implementations will not be executed
COMPARE_ARG_BORDER = 0


def run(name, comment, functions, cases, exec_compare=True, draw_plot=True):
    if draw_plot:
        init_plots()
        print

    comment = '' if comment is None else ', ' + comment
    title = 'Function "%s"%s:\n' % (name, comment)
    print title

    cols = [('arg', ARG_COL_WIDTH)]
    methods = []
    for index, (desc, func) in enumerate(functions):
        width = COMPARED_COL_WIDTH if index else CONTROL_COL_WIDTH
        cols.append(('%s, s' % desc, width))
        methods.append([desc, func, None])
    cols.append(('match', MATCH_COL_WIDTH))

    for case_desc, plot_type, arguments in cases:
        if case_desc is not None:
            print '(*) Testcase "%s":' % case_desc

        # Clear previous measures
        for method in methods:
            method[2] = []

        # Make table object
        table = Table(cols)
        table.head()
        for arg in arguments:
            # Fill "arg" column
            table.append(arg)

            # Fill measures columns
            prev_time = None
            data_set = set()
            for method_desc, func, measures in methods:
                cur_time, data = measure_time(func, arg)
                cell = '%.2lf' % cur_time
                if exec_compare and prev_time is not None:
                    if arg > COMPARE_ARG_BORDER:
                        ratio = float(prev_time) / cur_time
                        comment = ' (%.1lfx)' % ratio
                    else:
                        comment = ''
                    cell += comment.rjust(COMPARED_COMMENT_WIDTH)
                prev_time = cur_time
                table.append(cell)
                measures.append(cur_time)
                data_set.add(data)

            # Fill "match" column
            table.append(str(len(data_set) == 1))
        table.footer()

        if draw_plot and plot_type is not None:
            suffix = '' if case_desc is None else '_' + case_desc
            make_plot(
                '%s%s.png' % (name, suffix),
                title, arguments, methods, plot_type,
            )
            print


# Functions for generate optimized variants of naive methods


def apply_options(settings, naive_func, clear_stack, min_rows):
    name = 'cpm'
    if not clear_stack or not min_rows:
        name += ' -'
    if not clear_stack:
        name += 'c'
    if not min_rows:
        name += 'm'

    return (name,
            cpmoptimize(opt_clear_stack=clear_stack,
                        opt_min_rows=min_rows, **settings)(naive_func))


def optimized(naive_func, iters_limit=0, try_options=False):
    settings = {'strict': True, 'iters_limit': iters_limit}
    functions = [('naive', naive_func)]
    if try_options:
        functions += [
            apply_options(settings, naive_func, False, False),
            apply_options(settings, naive_func, False, True),
            apply_options(settings, naive_func, True, False)]
    functions.append(apply_options(settings, naive_func, True, True))
    return functions
