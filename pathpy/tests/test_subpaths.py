#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_subpaths.py -- Test environment for the Subpaths class
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2019-11-07 14:09 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================

from pathpy import Path, Network


def test_basic():
    """Test basic functions."""

    p1 = Path('a', 'b', 'c', 'd', frequency=10)
    p2 = Path('a', 'b', 'e', frequency=10)
    p3 = Path('b', 'c', 'd', frequency=10)
    net = Network(p1, p2, p3)

    net.subpaths.statistics()
    net.subpaths.summary()

    # print(net.subpaths.possible[2])
    #sp = net.subpaths()

    # print(sp)
# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
