#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : helper.py -- Little helpers for pathpy
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Fri 2020-03-27 12:03 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================


def window(iterable, size=2):
    """Sliding window."""
    i = iter(iterable)
    win = []
    for e in range(0, size):
        win.append(next(i))
    yield win
    for e in i:
        win = win[1:] + [e]
        yield win


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
