#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : speed_node.py -- Test environment for the Node class performance
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Mon 2020-10-05 13:25 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from collections import defaultdict
from pathpy import Node, Edge
from pathpy.core.edge import EdgeCollection

NUMBER_OF_EDGES = 2000


def add_edges(pathpy=True, edges=[], indexing=True):
    """Add nodes to NodeCollection"""
    ec = EdgeCollection()
    ed = {}
    nodes_map: defaultdict = defaultdict(set)
    node_map: defaultdict = defaultdict(set)

    if pathpy and indexing:
        for edge in edges:
            # ec.add(edge)  # Too slow (> 1000)
            ec._add(edge)  # add edge with index structure
        l = len(ec)
    elif pathpy and not indexing:
        for edge in edges:
            ec << edge  # add edge no index structure
        # ec.update_index() # needed to generate index structure
        l = len(ec)
    elif not pathpy and not indexing:
        for edge in edges:
            ed[edge.uid] = edge
        l = len(ed)
    elif not pathpy and indexing:
        for edge in edges:
            _v = edge.v
            _w = edge.w
            ed[edge.uid] = edge
            nodes_map[(_v, _w)].add(edge)
            node_map[_v].add(edge)
            node_map[_w].add(edge)

        l = len(ed)

    return l


def test_add_edges_pathpy(benchmark):
    """Test the creation of nodes via pathpy"""
    # benchmark function
    edges = [Edge(Node(), Node()) for i in range(NUMBER_OF_EDGES)]
    result = benchmark(add_edges, True, edges, False)
    assert result == NUMBER_OF_EDGES


def test_add_nodes_dict(benchmark):
    """Test the creation of nodes via dicts"""
    # benchmark something, but add some arguments
    edges = [Edge(Node(), Node()) for i in range(NUMBER_OF_EDGES)]
    result = benchmark(add_edges, False, edges, False)
    assert result == NUMBER_OF_EDGES


def test_add_edges_pathpy_index(benchmark):
    """Test the creation of nodes via pathpy"""
    # benchmark function
    edges = [Edge(Node(), Node()) for i in range(NUMBER_OF_EDGES)]
    result = benchmark(add_edges, True, edges, True)
    assert result == NUMBER_OF_EDGES


def test_add_nodes_dict_index(benchmark):
    """Test the creation of nodes via dicts"""
    # benchmark something, but add some arguments
    edges = [Edge(Node(), Node()) for i in range(NUMBER_OF_EDGES)]
    result = benchmark(add_edges, False, edges, True)
    assert result == NUMBER_OF_EDGES


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
