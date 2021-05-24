# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_hyperedge.py -- Test environment for the HyperEdge class
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Mon 2021-05-24 10:42 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================

import pytest

from pathpy import Node, Edge

from pathpy.core.hyperedge import HyperEdge


def test_HyperEdge():
    """Test an hyperedge."""
    a = Node('a')
    b = Node('b')
    c = Node('c')
    d = Node('d')
    e = Node('e')

    h0 = HyperEdge(a, b, c, uid='h0')
    h1 = HyperEdge(a, c, d, uid='h1')
    h2 = HyperEdge(b, d, e, uid='h2')

    print(h0)
    #print(h0 == h1)
#     assert e.uid == 'ab-cd'
#     assert len(e.nodes) == 4
#     assert a and b and c and d in e.nodes

#     assert isinstance(e.v, NodeSet)
#     assert isinstance(e.w, NodeSet)

#     assert len(e.v) == 2 and a and b in e.v
#     assert len(e.w) == 2 and c and d in e.w

#     e = HyperEdge({a, b, c}, uid='abc')

#     assert e.uid == 'abc'
#     assert len(e.nodes) == 3
#     assert a and b and c in e.nodes

#     assert isinstance(e.v, NodeSet)
#     assert isinstance(e.w, NodeSet)
#     assert e.v == e.w

#     e = HyperEdge(a, b, uid='a-b')
#     assert e.uid == 'a-b'
#     assert len(e.nodes) == 2
#     assert a and b in e.nodes

#     assert isinstance(e.v, NodeSet)
#     assert isinstance(e.w, NodeSet)

#     assert len(e.v) == 1 and a in e.v
#     assert len(e.w) == 1 and b in e.w


# def test_EdgeCollection_for_HyperEdges():
#     """Test the EdgeCollection with hyperedges."""

#     a = Node('a')
#     b = Node('b')
#     c = Node('c')
#     d = Node('d')

#     e = HyperEdge({a, b}, {c, d}, uid='ab-cd')

#     edges = EdgeCollection(hyperedges=False)

#     with pytest.raises(Exception):
#         edges.add(e)

#     with pytest.raises(Exception):
#         edges.add({a, b}, {c, d})

#     edges = EdgeCollection(hyperedges=True)
#     edges.add(e)

#     assert len(edges) == 1
#     assert e in edges
#     assert len(edges.nodes) == 4
#     assert a and b and c and d in edges.nodes

#     assert ({'a', 'b'}, {'c', 'd'}) in edges
#     assert ({'b', 'a'}, {'c', 'd'}) in edges
#     assert ({'a', 'b'}, {'d', 'c'}) in edges
#     assert ({'b', 'a'}, {'d', 'c'}) in edges

#     assert edges[{'a', 'b'}, {'c', 'd'}] == e
#     assert edges[{'b', 'a'}, {'c', 'd'}] == e
#     assert edges[{'a', 'b'}, {'d', 'c'}] == e
#     assert edges[{'b', 'a'}, {'d', 'c'}] == e

#     edges.add({a, 'c'}, {'b', d}, uid='ac-bd')

#     assert len(edges) == 2
#     assert ({'c', 'a'}, {'b', 'd'}) in edges

#     edges.remove({'a', 'b'}, {'c', 'd'})
#     assert len(edges) == 1
#     assert 'ab-cd' not in edges

#     edges.remove('ac-bd')
#     assert len(edges) == 0


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
