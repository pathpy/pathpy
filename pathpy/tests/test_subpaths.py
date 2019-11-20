#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_subpaths.py -- Test environment for the Subpaths class
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Fri 2019-11-15 06:56 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================

from pathpy import Path, Network, HigherOrderNetwork


def test_basic():
    """Test basic functions."""

    p1 = Path('a', 'b', 'c', 'd', frequency=10)
    p2 = Path('a', 'b', 'e', frequency=10)
    p3 = Path('b', 'c', 'd', frequency=10)
    net = Network(p1, p2, p3)

    # net.subpaths.statistics()
    # net.subpaths.summary()

    # print(net.subpaths.possible[2])
    #sp = net.subpaths()

    # print(sp)


def test_call():
    """Test subpaths generaten via call function."""
    p1 = Path('a', 'b', 'c', 'a', 'b', 'c', frequency=15)
    p2 = Path('x', 'y', 'z', 'x', 'y', 'z', frequency=13)
    p3 = Path('u', 'v', frequency=1)
    p4 = Path('u', 'v', 'w', frequency=1)

    net = Network(p2, p1, p3, p4)

    # net.subpaths.summary()
    # sp = net.subpaths.expand(4, include_path=True)
    # for x in sp:
    #     print(x)

    hon = HigherOrderNetwork(net, order=1)

    # for n in hon.nodes:
    #     print(n)

    # for e in hon.edges.values():
    #     print(e.uid, e.attributes.frequency)

    # print(hon.edges.counter())
    # hon.subpaths.summary()
    # print(hon.edges.to_df())
    # print(sp.counter())


def test_counter():
    """Test counter for sub paths."""

    p = Path('a', 'b', 'c', 'a')
    net = Network(p)
    c = net.subpaths.counter()

    assert c['a'] == 2
    assert c['b'] == c['c'] == 1
    assert c['a-b'] == 1

    p = Path('a', 'b', 'c', 'a', frequency=8)
    net = Network(p)
    c = net.subpaths.counter()

    assert c['a'] == 16
    assert c['b'] == c['c'] == 8
    assert c['a-b'] == 8


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
