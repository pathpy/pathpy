#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : speed_node.py -- Test environment for the Node class performance
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Sun 2020-10-04 13:33 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from pathpy import Node, Edge


def create_edges(pathpy=True, iterations=1000):
    """ Create nodes without attributes. """
    a = Node('a')
    b = Node('b')

    if pathpy:
        for i in range(iterations):
            e = Edge(a, b)
    else:
        for i in range(iterations):
            e = {}
            e.update(uid=None, v=a, w=b, nodes=set())
            e['nodes'].add(a)
            e['nodes'].add(b)

    return True


def test_create_edges_pathpy(benchmark):
    """Test the creation of nodes via pathpy. """
    # benchmark function
    result = benchmark(create_edges)
    assert result


def test_create_edges_dict(benchmark):
    """Test the creation of nodes via dicts. """
    # benchmark something, but add some arguments
    result = benchmark(create_edges, False)
    assert result


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
