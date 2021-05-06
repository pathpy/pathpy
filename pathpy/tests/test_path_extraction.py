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

pathdata = [
    (1, Counter({('a', 'b', 'c'): 1, ('b', 'd'): 1} )),
    (2, Counter({('a', 'b', 'c'): 1, ('b', 'd'): 1} )),
    (3, Counter({('a', 'b', 'c', 'd'): 1, ('b', 'd'): 1} )),
    (4, Counter({('a', 'b', 'c', 'd'): 1, ('a', 'b', 'd'): 1} ))
]

@pytest.mark.parametrize("delta,path_counts", pathdata)
def test_path_extraction(tempnet, delta, path_counts):
    paths = pp.algorithms.path_extraction.all_paths_from_temporal_network(tempnet, delta=delta)
    assert paths == path_counts