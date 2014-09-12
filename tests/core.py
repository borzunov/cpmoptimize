#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import os
import sys
from time import time

sys.path.append(os.path.pardir)
from cpmoptimize import cpmoptimize


# Functions for making plots

support_plots = None

# Directory where plots will be saved
plots_dir = 'plots'

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
        os.makedirs(plots_dir)
        print '[+] Created directory "%s"' % plots_dir
    except OSError:
        # If directory already exists, do nothing
        pass
 
# Plots' size (in inches)
linear_plots_size = 6, 4
other_plots_size = 5, 5
 
# Font size for plots
lable_fontsize = 11
normal_fontsize = 9

def make_plot(filename, title, arguments, methods, scale):
    if not support_plots:
        return
    
    is_linear = (scale == 'linear')
    
    # Create new plot with specified size
    plot_size = linear_plots_size if is_linear else other_plots_size
    plt.figure(figsize=plot_size)
    
    for name, func, measures in methods:
        # For every sequence draw it on the plot. Specify markers'
        # style (circles with specified size) and add record about this
        # sequence to the legend of the plot.
        plt.plot(arguments, measures, 'o-', label=name, markersize=3)

    if is_linear:
        # Define that both axes always starts from zero
        axis = plt.axis()
        plt.axis((0, axis[1], 0, axis[3]))
    
    # Specify scale type (linear or logarithmical)
    plt.xscale(scale)
    plt.yscale(scale)
    
    # Specify font for axes' ticks
    plt.xticks(fontsize=normal_fontsize)
    plt.yticks(fontsize=normal_fontsize)
    
    # Enable grid in the background
    plt.grid(True)

    # Specify plot's title, axes' labels and legend block location.
    # Also specify font size for text elements above.
    plt.title(title, fontsize=lable_fontsize)
    plt.xlabel('Argument', fontsize=normal_fontsize)
    plt.ylabel('Time (seconds)', fontsize=normal_fontsize)
    plt.legend(loc='upper left', fontsize=normal_fontsize)

    # Fix paddings in the plot
    plt.tight_layout(0.2)

    # Save plot to the specified file
    path = os.path.join(plots_dir, filename)
    plt.savefig(path)
    print '[*] Saved plot "%s"' % path


# Class for formatting simple tables in console output

class Table(object):
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


# Function for measuring time of function running

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


# Function for running testcase

# Table's columns widths
arg_col_width = 6
control_col_width = 8
compared_col_width = 12
compare_comment_width = 8
match_col_width = 5

# If argument of functions is lesser or equal this value, comparison of
# execution time of different implementations will not be executed
compare_arg_border = 0

def run(name, comment, functions, cases, exec_compare=True, draw_plot=True):
    if draw_plot:
        init_plots()
        print
    
    comment = '' if comment is None else ', ' + comment
    title = 'Function "%s"%s:\n' % (name, comment)
    print title
    
    cols = [('arg', arg_col_width)]
    methods = []
    for index, (desc, func) in enumerate(functions):
        width = compared_col_width if index else control_col_width
        cols.append(('%s, s' % desc, width))
        methods.append([desc, func, None])
    cols.append(('match', match_col_width))
    
    for case_desc, plot_type, arguments in cases:
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
                    if arg > compare_arg_border:
                        ratio = float(prev_time) / cur_time
                        comment = ' (%.1lfx)' % ratio
                    else:
                        comment = ''
                    cell += comment.rjust(compare_comment_width)
                prev_time = cur_time
                table.append(cell)
                measures.append(cur_time)
                data_set.add(data)
            
            # Fill "match" column
            table.append(str(len(data_set) == 1))
        table.footer()

        if draw_plot and plot_type is not None:
            make_plot(
                '%s_%s.png' % (name, case_desc),
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
    
    return (name, cpmoptimize(
        opt_clear_stack=clear_stack, opt_min_rows=min_rows, **settings
    )(naive_func))

def optimized(naive_func, try_options=False, disable_limit=False):
    settings = {'strict': True}
    if not disable_limit:
        settings['iters_limit'] = 0
    functions = [
        ('naive', naive_func),
    ]
    if try_options:
        functions += [
            apply_options(settings, naive_func, False, False),
            apply_options(settings, naive_func, False, True),
            apply_options(settings, naive_func, True, False),
        ]
    functions.append(apply_options(settings, naive_func, True, True))
    return functions
