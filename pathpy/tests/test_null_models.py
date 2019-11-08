#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_null_models.py -- Test environment for null models
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Fri 2019-11-08 15:02 juergen>
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

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
