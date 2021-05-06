#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_path_extraction.py -- Test path extraction in temporal networks and DAGs
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Wed 2021-05-05 17:52 ingo>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================

import pytest
import pathpy as pp

from collections import Counter

@pytest.fixture
def tempnet():
    tn = pp.TemporalNetwork()
    tn.add_edge('a', 'b', timestamp=1)
    tn.add_edge('b', 'c', timestamp=2)
    tn.add_edge('b', 'd', timestamp=5)
    tn.add_edge('c', 'd', timestamp=5)
    return tn

@pytest.fixture
def dag():
    dag = pp.DirectedAcyclicGraph()
    dag.add_edge('a', 'b')
    dag.add_edge('b', 'c')
    dag.add_edge('b', 'd')
    dag.add_edge('c', 'e')
    return dag

pathdata = [
    (1, Counter({('a', 'b', 'c'): 1, ('b', 'd'): 1, ('c', 'd'): 1} )),
    (2, Counter({('a', 'b', 'c'): 1, ('b', 'd'): 1, ('c', 'd'): 1} )),
    (3, Counter({('a', 'b', 'c', 'd'): 1, ('b', 'd'): 1} )),
    (4, Counter({('a', 'b', 'c', 'd'): 1, ('a', 'b', 'd'): 1} ))
]

dagdata = [
    (1, [('a_1', 'b_2'), ('b_2', 'c_3'), ('b_5', 'd_6'), ('c_5', 'd_6')]),
    (2, [('a_1', 'b_2'), ('a_1', 'b_3'), ('b_2', 'c_3'), ('b_2', 'c_4'), ('b_5', 'd_6'), ('b_5', 'd_7'), ('c_5', 'd_6'), ('c_5', 'd_7')]),
    (3, [('a_1', 'b_2'), ('a_1', 'b_3'), ('b_2', 'c_3'), ('b_2', 'c_4'), ('b_5', 'd_6'), ('b_5', 'd_7'), ('c_5', 'd_6'), ('c_5', 'd_7'), ('a_1', 'b_4')]),
    (4, [('a_1', 'b_2'), ('a_1', 'b_3'), ('b_2', 'c_3'), ('b_2', 'c_4'), ('b_5', 'd_6'), ('b_5', 'd_7'), ('c_5', 'd_6'), ('c_5', 'd_7'), ('a_1', 'b_4'), ('a_1', 'b_5')])
]

@pytest.mark.parametrize("delta,path_counts", pathdata)
def test_path_extraction_temporal_network(tempnet, delta, path_counts):
    paths = pp.algorithms.path_extraction.all_paths_from_temporal_network(tempnet, delta=delta)
    assert paths == path_counts


def test_path_extraction_dag(dag):
    paths = pp.algorithms.path_extraction.all_paths_from_dag(dag)
    assert paths == Counter({('a', 'b', 'c', 'e'): 1, ('a', 'b', 'd'): 1})


@pytest.mark.parametrize("delta,expected_edges", dagdata)
def test_temporal_net_to_dag(tempnet, delta, expected_edges):
    dag = pp.DirectedAcyclicGraph.from_temporal_network(tempnet, delta=delta)
    for e in expected_edges:
        assert e in dag.edges