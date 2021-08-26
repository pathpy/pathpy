#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_hypergraph.py • tests -- Test environment for the HyperGraph class
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2021-08-26 15:55 juergen>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
import pytest

from pathpy import Node, Edge, Network
from pathpy.core.hyperedge import HyperEdge, HyperEdgeCollection

from pathpy.models.hypergraph import HyperGraph


def test_hypergraph():
    """Test the hypergraph"""
    a = Node('a')
    b = Node('b')
    c = Node('c')
    d = Node('d')
    e = Node('e')

    h1 = HyperEdge(a, b, c, uid='h1')
    h2 = HyperEdge(a, c, d, uid='h2')
    h3 = HyperEdge(b, d, e, uid='h3')

    hg = HyperGraph()
    hg.add_edges(h1, h2, h3)

    print(hg)
    print(hg.incident_edges)
    print(hg.degrees())

    hg = HyperGraph()
    hg.add_edge('0', '1', '3', uid='h1')

    assert hg.number_of_edges() == 1
    assert hg.number_of_nodes() == 3

    assert ('3', '1', '0') in hg.edges


def test_hyperedge():
    hg = HyperGraph()
    hg.add_edge('a', 'b')
    hg.add_edge('a', 'b')
    # hg
    # n = Network()
    # n.add_edge('a', 'b')
    # n.add_edge('a', 'b')
    assert hg.edges.counter[hg.edges['a', 'b'].uid] == 2
# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
