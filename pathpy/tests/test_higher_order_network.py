#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_higher_order_network.py -- Test environment for HONs
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Mon 2020-08-31 11:23 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================

import pytest
from pathpy import Node, Edge, Path
from pathpy.models.higher_order_network import (
    HigherOrderNode,
    HigherOrderEdge,
    HigherOrderNodeCollection,
    HigherOrderEdgeCollection,
    HigherOrderNetwork,
)
from pathpy.core.path import PathCollection
# #                                                 # HigherOrderEdge
# #                                                 )
# from pathpy.core.path import HigherOrderNode


def test_higher_order_node():
    """Test higher order nodes."""
    a = Node('a', color='azure')
    b = Node('b', color='blue')
    c = Node('c', color='cyan')

    ab = Edge(a, b, uid='a-b')
    bc = Edge(b, c, uid='b-c')

    abc = HigherOrderNode(ab, bc, uid='abc')

    nodes = HigherOrderNodeCollection()
    nodes.add(abc)

    assert nodes[abc] == abc
    assert nodes['abc'] == abc
    assert nodes[a, b, c] == abc
    assert nodes['a', 'b', 'c'] == abc
    assert nodes[ab, bc] == abc
    assert nodes['a-b', 'b-c'] == abc

    assert abc in nodes
    assert 'abc' in nodes
    assert (a, b, c) in nodes
    assert ('a', 'b', 'c') in nodes
    assert (ab, bc) in nodes
    assert ('a-b', 'b-c') in nodes


def test_higher_order_edge():
    """Test higher order edges."""

    a = Node('a', color='azure')
    b = Node('b', color='blue')
    c = Node('c', color='cyan')
    d = Node('d', color='desert')

    ab = Edge(a, b, uid='a-b')
    bc = Edge(b, c, uid='b-c')
    cd = Edge(c, d, uid='c-d')

    abc = HigherOrderNode(ab, bc, uid='abc')
    bcd = HigherOrderNode(bc, cd, uid='bcd')

    abc_bcd = HigherOrderEdge(abc, bcd, uid='abc-bcd')


def test_higher_order_edge_collection():
    """Test HigherOrderEdgeCollection."""

    a = Node('a', color='azure')
    b = Node('b', color='blue')
    c = Node('c', color='cyan')
    d = Node('d', color='desert')
    e = Node('e', color='desert')

    ab = Edge(a, b, uid='a-b')
    bc = Edge(b, c, uid='b-c')
    cd = Edge(c, d, uid='c-d')
    de = Edge(d, e, uid='d-e')

    abc = HigherOrderNode(ab, bc, uid='abc')
    bcd = HigherOrderNode(bc, cd, uid='bcd')
    cde = HigherOrderNode(cd, de, uid='cde')

    abc_bcd = HigherOrderEdge(abc, bcd, uid='abc-bcd')
    bcd_cde = HigherOrderEdge(bcd, cde, uid='bcd-cde')

    edges = HigherOrderEdgeCollection()

    edges.add(abc_bcd)

    assert edges[abc_bcd] == abc_bcd
    assert edges['abc-bcd'] == abc_bcd
    assert edges[abc, bcd] == abc_bcd
    assert edges['abc', 'bcd'] == abc_bcd
    assert edges[(a, b, c), (b, c, d)] == abc_bcd
    assert edges[('a', 'b', 'c'), ('b', 'c', 'd')] == abc_bcd
    assert edges[(ab, bc), (bc, cd)] == abc_bcd
    assert edges[('a-b', 'b-c'), ('b-c', 'c-d')] == abc_bcd

    # NotImplemented
    # edges['a','b','c','d'] # path node uids
    # edges['a-b','b-c','c-d'] # path edge uids
    # edges[a,b,c,d] # node objects
    # edges[ab,bc,cd] # edge objects

    assert abc_bcd in edges
    assert 'abc-bcd' in edges
    assert (abc, bcd) in edges
    assert ('abc', 'bcd') in edges
    assert ((a, b, c), (b, c, d)) in edges
    assert (('a', 'b', 'c'), ('b', 'c', 'd')) in edges
    assert ((ab, bc), (bc, cd)) in edges
    assert (('a-b', 'b-c'), ('b-c', 'c-d')) in edges


def test_higher_order_network():
    """Default test for development"""
    hon = HigherOrderNetwork()

    hon.add_node('a', 'b', 'c', uid='abc')
    hon.add_node('b', 'c', 'd', uid='bcd')
    hon.add_edge('abc', 'bcd', uid='abc-bcd')
#     print(hon.nodes)
#     #hon.add_edge('a', 'b', uid='e1')
    # print(hon)
    # print(len(hon.nodes.edges))
    # print(hon.edges)


def test_fit_path_collection():
    """Fit PathCollection to a HON"""
    paths = PathCollection()
    paths.add('a', 'c', 'd', uid='acd', frequency=10)
    paths.add('b', 'c', 'e', uid='bce', frequency=10)

    hon = HigherOrderNetwork()
    hon.fit(paths, order=0)

    assert hon.order == 0
    assert hon.number_of_nodes() == 5
    assert hon.number_of_edges() == 0

    hon = HigherOrderNetwork()
    hon.fit(paths, order=1)

    assert hon.order == 1
    assert hon.number_of_nodes() == 5
    assert hon.number_of_edges() == 4

    hon = HigherOrderNetwork()
    hon.fit(paths, order=2)

    assert hon.order == 2
    assert hon.number_of_nodes() == 4
    assert hon.number_of_edges() == 2

    hon = HigherOrderNetwork.from_paths(paths, order=2)

    assert hon.order == 2
    assert hon.number_of_nodes() == 4
    assert hon.number_of_edges() == 2


def test_outdegrees():
    """Fit PathCollection to a HON"""
    paths = PathCollection()
    paths.add('a', 'c', 'd', uid='acd', frequency=10)
    paths.add('b', 'c', 'e', uid='bce', frequency=10)

    hon = HigherOrderNetwork()
    hon.fit(paths, order=2)

    assert sum(hon.outdegrees().values()) == 2

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
