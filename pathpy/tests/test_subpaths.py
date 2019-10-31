#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_subpaths.py -- Test environment for the Subpaths class
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2019-10-31 17:22 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================

from pathpy import Path, Network


def test_basic():
    """Test basic functions."""

    p1 = Path('a', 'b', 'c', 'd', frequency=10)
    p2 = Path('a', 'b', 'e', frequency=10)
    net = Network(p1, p2)

    print(net.subpaths.counter())
    net.subpaths.statistics()

    sp = net.subpaths()

    print(sp)
# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
