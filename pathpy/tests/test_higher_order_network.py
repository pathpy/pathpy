#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_higher_order_network.py -- Test env. for the HON class
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Fri 2019-11-08 16:22 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
# import pytest

from pathpy import Node, Edge, Path, Network, HigherOrderNetwork, HigherOrderNode


def test_basic():
    """Test basic functions of the HON."""
    pass


def test_higher_order_node():
    """Test higher order nodes."""
    p = Path('a', 'b')
    a = HigherOrderNode(p)

    assert a.uid == 'a-b'
    print(a)

    e = Edge('b', 'c')
    a.add_edge(e)

    assert a.uid == 'a-b|b-c'


def test_degrees_of_freedom():
    """Test the degree of freedom."""
    p1 = Path('a', 'c', 'd', frequency=10)
    p2 = Path('b', 'c', 'e', frequency=10)

    net = Network(p1, p2)

    h0 = HigherOrderNetwork(net, order=0)

    assert h0.degrees_of_freedom() == 4

    h1 = HigherOrderNetwork(net, order=1)

    assert h1.degrees_of_freedom() == 1

    h2 = HigherOrderNetwork(net, order=2)

    assert h2.degrees_of_freedom() == 0


def test_hon():
    """Test some hon examples."""
    p1 = Path('a', 'c', 'd', 'f', frequency=10)
    p2 = Path('b', 'c', 'e', frequency=10)

    net = Network(p1, p2)

    # net.summary()
    # net.subpaths.summary()

    # hon = HigherOrderNetwork(net, order=2)

    # hon.summary()
    # print(hon.edges.to_df())

    # print(net.edges.to_df())

    # print(net.edges['a-c'].attributes.to_dict()['separator'])

    # hon.subpaths.summary()

    # print(net.adjacency_matrix(weight='frequency'))

    # print(hon.edges.to_df())
    # print(hon.adjacency_matrix(subpaths=True))
    # d = net.paths['f-g'].attributes.data
    # # print(net.paths.data_frame())
    # print(d)
    # net.subpaths.statistics()

    # hon = HigherOrderNetwork(net, order=3)
    # hon.summary()

    # hon.subpaths.statistics()

    # for n in hon.nodes:
    #     print(n)

    # for e in hon.edges.values():
    #     print(e.uid, e['frequency'], e['observed'])

    # print(hon.edges.counter())

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
