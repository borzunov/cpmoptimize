#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import time
from traceback import format_exc

def echo(settings, message):
    settings['verbose'].write('[%.3lf] Loop at line %s in %s:\n%s\n\n' % (
        time(), settings['head_lineno'], settings['repr'], message,
    ))

def exc(settings, message, exc):
    if settings['strict']:
        raise exc
    echo(settings, '[-] %s:\n%s' % (message, format_exc(exc)[:-1]))

def note(settings, message):
    echo(settings, '[*] ' + message)

def success(settings, message):
    echo(settings, '[+] ' + message)
