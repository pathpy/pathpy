#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : speed_node.py -- Test environment for the Node class performance
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Sun 2020-10-04 13:04 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from pathpy import Node
from pathpy.core.node import NodeCollection


def create_nodes(pathpy=True):
    """
    Function that needs some serious benchmarking.
    """

    if pathpy:
        a = Node('a', color='blue')
    else:
        a = node = {}
        node.update(uid='a', attributes={'color': 'blue'})

    return True


def add_nodes(pathpy=True, numbers=1000):
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


def test_create_nodes_pathpy(benchmark):
    """Test the creation of nodes via pathpy"""
    # benchmark function
    result = benchmark(create_nodes)
    assert result


def test_create_nodes_dict(benchmark):
    """Test the creation of nodes via dicts"""
    # benchmark something, but add some arguments
    result = benchmark(create_nodes, False)
    assert result


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


# def node_creation():
#     """Test note creation"""
#     L = []
#     for i in range(100):
#         L.append(i)


# def test_node_speed():
#     print(timeit.timeit("node_creation()", setup="from pathpy import Node"))

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
