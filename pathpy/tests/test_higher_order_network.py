#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_higher_order_network.py -- Test env. for the HON class
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Fri 2019-11-15 09:22 juergen>
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

    e = Edge('b', 'c')
    a.add_edge(e)

    assert a.uid == 'a-b|b-c'


def test_hon_order_0():
    """Test a HON of order 0."""
    p1 = Path('a', 'c', 'd', frequency=10)
    p2 = Path('b', 'c', 'e', frequency=10)

    net = Network(p1, p2)

    hon = HigherOrderNetwork(net, order=0)

    # for n, v in hon.nodes.items():
    #     print(n, v)

    # for e, v in hon.edges.items():
    #     print(e, v)

    # hon.subpaths.summary()

    # print(hon.edges.to_df())

    # print(hon.edges.counter())


def test_degrees_of_freedom():
    """Test the degree of freedom."""
    p1 = Path('a', 'c', 'd', frequency=2)
    p2 = Path('b', 'c', 'e', frequency=2)
    net = Network(p1, p2)

    h1 = HigherOrderNetwork(net, order=1)
    h2 = HigherOrderNetwork(net, order=2)

    print(h1.degrees_of_freedom())
    print(h2.degrees_of_freedom())

    # print(h2.transition_matrix())
    #h1 = HigherOrderNetwork(net,order=1)

# def test_degrees_of_freedom():
#     """Test the degree of freedom."""
#     # p1 = Path('a', 'c', 'd', frequency=10)
#     # p2 = Path('b', 'c', 'e', frequency=10)

#     # net = Network(p1, p2)

#     # h0 = HigherOrderNetwork(net, order=1)

#     e1 = Edge('a', 'c')
#     e2 = Edge('c', 'd')
#     e3 = Edge('b', 'c')
#     e4 = Edge('c', 'e')

#     p1 = Path.from_edges([e1, e2])
#     p2 = Path.from_edges([e3, e4])

#     net = Network(p1, p2)

#     print('HON')
#     hon = HigherOrderNetwork(net, order=2)
#     # h0.summary()

#     print(hon.degrees_of_freedom())

    # for e, v in h0.edges.items():
    #     print(e, v.v.uid, v.v.outgoing)
    #     print(e, v.w.uid, v.w.outgoing)

    # # for n, v in h0.nodes.items():
    # #     print(n, v.outgoing, v.incoming)

    # print('Network')
    # for n, v in hon.nodes.items():
    #     print(n, v.outgoing, v.incoming)

    # assert h0.degrees_of_freedom() == 4

    # h1 = HigherOrderNetwork(net, order=1)

    # assert h1.degrees_of_freedom() == 1

    # h2 = HigherOrderNetwork(net, order=2)

    # assert h2.degrees_of_freedom() == 0

    # p = Path('0', '0', '4', '2', '2', '1', '2', '4', '3', '4', '0')

    # net = Network(p)

    # net.summary()

    # print(net.nodes)
    # print(net.edges)
    # hon = HigherOrderNetwork(net, order=1)

    # print(hon.edges)
    # hon.summary()
    # print(hon.edges)
    # print(hon.edges)
    # print(hon.degrees_of_freedom())


# def test_likelihood():
#     """Test likelihood for higher order networks."""
#     p1 = Path('a', 'c', 'd', frequency=2)
#     p2 = Path('b', 'c', 'e', frequency=2)

#     net = Network(p1, p2)

#     hon = HigherOrderNetwork(net, order=1)

#     # print(hon.transition_matrix())

#     # hon.likelihood('xxx')


# def test_hon():
#     """Test some hon examples."""
#     p1 = Path('a', 'c', 'd', 'f', frequency=10)
#     p2 = Path('b', 'c', 'e', frequency=10)

#     net = Network(p1, p2)

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
