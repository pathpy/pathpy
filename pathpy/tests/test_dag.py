#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_dag.py -- Test environment for the DAG class
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Wed 2020-09-02 16:10 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================

import pytest
from pathpy import Node, Edge, Network, TemporalNetwork, DirectedAcyclicGraph
from collections import Counter

def test_basic():
    """Test some basic functions"""

    dag = DirectedAcyclicGraph()

    dag.add_edge('a', 'b')
    dag.add_edge('a', 'c')
    dag.add_edge('c', 'b')
    dag.add_edge('b', 'e')
    dag.add_edge('b', 'f')
    dag.add_edge('f', 'g')
    dag.add_edge('c', 'g')
    dag.add_edge('h', 'i')
    dag.add_edge('h', 'j')

    dag.topological_sorting()

    assert dag.acyclic is True


# # def test_to_paths():
# #     """Test converter to paths"""
#     paths = dag.to_paths()

# for path in paths.values():
#     print(path.nodes)

# print('roots', dag.roots)
# print('leafs', dag.leafs)

# # dag.remove_edge('b', 'c')

# # print('roots', dag.roots)
# # print('leafs', dag.leafs)

# dag.topological_sorting()
# print(dag._topsort['sorting'])
# print(dag._topsort['parent'])
# print(dag._topsort['start'])
# print(dag._topsort['end'])
# print(dag._topsort['class'])
# print(dag._topsort['count'])
# print(dag.acyclic)

# print(dag)

def test_dag_node_creation():
    """
    """
    dag = DirectedAcyclicGraph()
    dag.add_edge('a', 'b')
    assert dag.nodes['b'] in dag.successors['a']

def test_from_temporal_network():
    """Test converter from temporal networks"""
    tn = TemporalNetwork()
    tn.add_edge('a', 'b', timestamp=1)
    tn.add_edge('b', 'a', timestamp=3)
    tn.add_edge('b', 'c', timestamp=3)
    tn.add_edge('d', 'c', timestamp=4)
    tn.add_edge('c', 'd', timestamp=5)
    tn.add_edge('c', 'b', timestamp=6)
    tn.add_edge('a', 'b', timestamp=7)
    tn.add_edge('b', 'a', timestamp=8)
    dag = DirectedAcyclicGraph.from_temporal_network(tn)
    dag.topological_sorting()
    assert dag.acyclic is True
    assert dag.number_of_nodes() == 13
    assert dag.number_of_edges() == 8


def test_routes_from():
    """Test converter from temporal networks"""
    tn = TemporalNetwork()
    tn.add_edge('a', 'b', timestamp=1)
    tn.add_edge('b', 'c', timestamp=2)
    tn.add_edge('b', 'd', timestamp=5)
    dag = DirectedAcyclicGraph.from_temporal_network(tn, delta=2)
    p = dag.routes_from('a_1')
    assert p == Counter({('a_1', 'b_3'): 1,
         ('a_1', 'b_2', 'c_4'): 1,
         ('a_1', 'b_2', 'c_3'): 1})

    p = dag.routes_from('b_5')
    assert p == Counter({('b_5', 'd_7'): 1, ('b_5', 'd_6'): 1})
    

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
