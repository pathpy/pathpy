#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : speed_node.py -- Test environment for the Node class performance
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Sun 2020-10-04 13:16 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from pathpy import Node


def create_nodes(pathpy=True):
    """ Create nodes without attributes. """

    if pathpy:
        a = Node('a', color='blue')
    else:
        a = node = {}
        node.update(uid='a', attributes={'color': 'blue'})

    return True


def create_nodes_attributes(pathpy=True, number=5):
    """ Create Nodes with attributes. """
    attr = {str(a): a for a in range(number)}
    if pathpy:
        a = Node('a', **attr)
    else:
        a = {}
        a.update(uid='a', attributes={})
        a['attributes'].update(**attr)

    return True


def test_create_nodes_pathpy(benchmark):
    """Test the creation of nodes via pathpy. """
    # benchmark function
    result = benchmark(create_nodes)
    assert result


def test_create_nodes_dict(benchmark):
    """Test the creation of nodes via dicts. """
    # benchmark something, but add some arguments
    result = benchmark(create_nodes, False)
    assert result


def test_create_nodes_attr_pathpy(benchmark):
    """Test the creation of nodes via pathpy"""
    # benchmark function
    result = benchmark(create_nodes_attributes)
    assert result


def test_create_nodes_attr_dict(benchmark):
    """Test the creation of nodes via dicts"""
    # benchmark something, but add some arguments
    result = benchmark(create_nodes_attributes, False)
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
