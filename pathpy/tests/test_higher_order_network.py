#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_higher_order_network.py -- Test environment for HONs
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Wed 2020-06-10 12:09 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================

import pytest
from pathpy import Node, Edge, Path
from pathpy.models.higher_order_network import (HigherOrderNetwork,
                                                HigherOrderNode,
                                                HigherOrderEdge)


def test_higher_order_node():
    """Test higher order nodes."""
    a = Node('a', color='azure')
    b = Node('b', color='blue')
    c = Node('c', color='cyan')

    ab = Edge(a, b, uid='ab')
    bc = Edge(b, c, uid='bc')

    abc = HigherOrderNode(ab, bc, uid='abc')

    # print(abc.uid)
    # print(abc)


def test_higher_order_edge():
    """Test higher order edges."""

    a = Node('a', color='azure')
    b = Node('b', color='blue')
    c = Node('c', color='cyan')
    d = Node('d', color='desert')

    ab = Edge(a, b, uid='ab')
    bc = Edge(b, c, uid='bc')
    cd = Edge(c, d, uid='cd')

    abc = HigherOrderNode(ab, bc, uid='abc')
    bcd = HigherOrderNode(bc, cd, uid='bcd')

    abc_bcd = HigherOrderEdge(abc, bcd, uid='abc-bcd')
    # print(abc_bcd)
    # pass


def test_higher_order_network():
    """Default test for development"""
    hon = HigherOrderNetwork()
    hon.add_node('a')
    hon.add_node('b')
    hon.add_edge('a', 'b', uid='e1')
    # print(hon)
    # print(hon.nodes)
    # print(hon.edges)


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
