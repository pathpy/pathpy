#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_null_model.py -- Test environment for null models
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Wed 2019-11-20 16:12 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================

import pytest

from pathpy import Path, Network, NullModel, HigherOrderNetwork


def test_basic():
    """Test basic functions."""

    p1 = Path('a', 'c', 'd', frequency=10)
    p2 = Path('b', 'c', 'e', frequency=10)

    net = Network(p1, p2)

    null = NullModel(net)
    n2 = null.generate(2)

    assert isinstance(n2, HigherOrderNetwork)
    assert n2.number_of_edges() == 4
    assert n2.number_of_nodes() == 4

    e = n2.edges.counter()

    assert e['a-c=c-d'] == 5.0
    assert e['a-c=c-e'] == 5.0
    assert e['b-c=c-d'] == 5.0
    assert e['b-c=c-e'] == 5.0

    assert n2 == null(2)


def test_possible_paths():
    """Test to generate all possible paths."""
    p = Path('a', 'a', 'b', 'b', 'a')
    net = Network(p)
    null = NullModel(net)

    assert len(null.possible_paths(3)) == 16


def test_loops():
    """Test paths which repeat."""
    p = Path('a', 'b', 'c', 'a', 'b', 'c')
    net = Network(p)
    null = NullModel(net)
    n2 = null(4)
    # n2.summary()
    # for k, v in n2.edges.items():
    #     print(k, v.attributes.frequency)

    # print(n2.paths.counter())
    #c = n2.subpaths.observed
    # n2.subpaths.summary()
    # print(c)


def test_degrees_of_freedom():
    """Test the degree of freedom."""
    #p1 = Path('a', 'c', 'd', frequency=2)
    #p2 = Path('b', 'c', 'e', frequency=2)
    p = Path('a', 'a', 'b', 'b', 'a')
    net = Network(p)

    print(net.adjacency_matrix())
    h1 = HigherOrderNetwork(net, order=1)
    h2 = HigherOrderNetwork(net, order=8)

    print(h1.degrees_of_freedom())
    print(h2.degrees_of_freedom())

    null = NullModel(net)

    n1 = null(1)
    n2 = null(8)

    # print(n2)
    # print(n2.adjacency_matrix())
    print(n1.degrees_of_freedom(mode='path'))
    print(n2.degrees_of_freedom(mode='path'))

    # for e in n2.edges.values():
    #     print(e.uid)


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
