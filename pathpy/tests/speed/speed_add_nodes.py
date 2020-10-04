#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : speed_node.py -- Test environment for the Node class performance
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Sun 2020-10-04 13:22 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from pathpy import Node
from pathpy.core.node import NodeCollection


def add_nodes(pathpy=True, numbers=100):
    """Add nodes to NodeCollection"""
    if pathpy:
        nodes = NodeCollection()
        for n in range(numbers):
            nodes << Node(n)
    else:
        nodes = {}
        for n in range(numbers):
            nodes[str(n)] = Node(n)

    return True


def test_add_nodes_pathpy(benchmark):
    """Test the creation of nodes via pathpy"""
    # benchmark function
    result = benchmark(add_nodes)
    assert result


def test_add_nodes_dict(benchmark):
    """Test the creation of nodes via dicts"""
    # benchmark something, but add some arguments
    result = benchmark(add_nodes, False)
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
