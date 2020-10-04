#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : speed_node.py -- Test environment for the Node class performance
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Sun 2020-10-04 14:48 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from pathpy import Node, Edge
from pathpy.core.edge import EdgeCollection


def add_edges(pathpy=True, edges=[], iterations=100):
    """Add nodes to NodeCollection"""
    if pathpy:
        ec = EdgeCollection()
        for edge in edges:
            # ec.add(edge) # Too slow (> 1000)
            # ec._add(edge) # add edge with index structure
            ec << edge  # add edge no index structure
        ec.update_index()
        l = len(ec)
    else:
        ed = {}
        for edge in edges:
            ed[edge.uid] = edge
        l = len(ed)
        #ed[(edge.v.uid, edge.w.uid)] = edge
    # if pathpy:
    #     edges = EdgeCollection()
    #     for e in range(numbers):
    #         edges._add(Edge(Node(), Node()))
    # else:
    #     edges = {}
    #     for e in range(numbers):
    #         edge = Edge(Node(), Node())
    #         edges[(edge.v.uid, edge.w.uid)] = edge

    return l


def test_add_edges_pathpy(benchmark):
    """Test the creation of nodes via pathpy"""
    # benchmark function
    edges = [Edge(Node(), Node()) for i in range(2000)]
    result = benchmark(add_edges, True, edges)
    assert result == 2000


def test_add_nodes_dict(benchmark):
    """Test the creation of nodes via dicts"""
    # benchmark something, but add some arguments
    edges = [Edge(Node(), Node()) for i in range(2000)]
    result = benchmark(add_edges, False, edges)
    assert result == 2000


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
