#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_converters.py -- Test environment for pathpy converters
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Sun 2020-10-04 10:07 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
import pytest
from pathpy import TemporalNetwork
from pathpy.converters.paco import all_paths_from_temporal_data


@pytest.fixture
def tn1():
    """Temporal test Network 1"""
    tn1 = TemporalNetwork(directed=False)
    tn1.add_edge("a", "b", t=1)  # 0
    tn1.add_edge("a", "b", t=2)  # 1
    tn1.add_edge("b", "a", t=3)  # 2
    tn1.add_edge("b", "c", t=3)  # 3
    tn1.add_edge("d", "c", t=3)  # 4
    tn1.add_edge("d", "c", t=4)  # 5
    tn1.add_edge("c", "d", t=5)  # 6
    tn1.add_edge("c", "b", t=6)  # 7
    tn1.add_edge("b", "c", t=7)  # 8
    return(tn1)


@pytest.fixture
def tn2():
    """Temporal test Network 2"""
    tn2 = TemporalNetwork(directed=False)
    tn2.add_edge("a", "b", t=1)  # 0
    tn2.add_edge("a", "c", t=2)  # 1
    tn2.add_edge("b", "c", t=2)  # 2
    tn2.add_edge("c", "d", t=3)  # 3
    tn2.add_edge("b", "d", t=4)  # 4
    tn2.add_edge("d", "c", t=4)  # 5
    tn2.add_edge("d", "c", t=5)  # 6
    tn2.add_edge("d", "a", t=5)  # 7
    tn2.add_edge("c", "b", t=6)  # 8
    return(tn2)


@pytest.fixture
def tn1_delta2():
    """Correct solution"""
    return {1: {('a', 'b'): 2,
                ('b', 'a'): 1,
                ('b', 'c'): 2,
                ('c', 'b'): 1,
                ('c', 'd'): 1,
                ('d', 'c'): 2},
            2: {('a', 'b', 'a'): 2,
                ('a', 'b', 'c'): 2,
                ('b', 'c', 'd'): 1,
                ('c', 'b', 'c'): 1,
                ('d', 'c', 'b'): 1,
                ('d', 'c', 'd'): 2},
            3: {('a', 'b', 'c', 'd'): 2,
                ('d', 'c', 'b', 'c'): 1}}


@pytest.fixture
def tn1_delta3():
    """Correct solution"""
    return {1: {('a', 'b'): 2,
                ('b', 'a'): 1,
                ('b', 'c'): 2,
                ('c', 'b'): 1,
                ('c', 'd'): 1,
                ('d', 'c'): 2},
            2: {('a', 'b', 'a'): 2,
                ('a', 'b', 'c'): 2,
                ('b', 'c', 'b'): 1,
                ('b', 'c', 'd'): 1,
                ('c', 'b', 'c'): 1,
                ('d', 'c', 'b'): 2,
                ('d', 'c', 'd'): 2},
            3: {('a', 'b', 'c', 'b'): 2,
                ('a', 'b', 'c', 'd'): 2,
                ('b', 'c', 'b', 'c'): 1,
                ('d', 'c', 'b', 'c'): 2},
            4: {('a', 'b', 'c', 'b', 'c'): 2}}


@pytest.fixture
def tn2_delta1():
    """Correct solution"""
    return {1: {('a', 'b'): 1,
                ('a', 'c'): 1,
                ('b', 'c'): 1,
                ('b', 'd'): 1,
                ('c', 'b'): 1,
                ('c', 'd'): 1,
                ('d', 'a'): 1,
                ('d', 'c'): 2},
            2: {('a', 'b', 'c'): 1,
                ('a', 'c', 'd'): 1,
                ('b', 'c', 'd'): 1,
                ('b', 'd', 'a'): 1,
                ('b', 'd', 'c'): 1,
                ('c', 'd', 'c'): 1,
                ('d', 'c', 'b'): 1},
            3: {('a', 'b', 'c', 'd'): 1,
                ('a', 'c', 'd', 'c'): 1,
                ('b', 'c', 'd', 'c'): 1,
                ('b', 'd', 'c', 'b'): 1},
            4: {('a', 'b', 'c', 'd', 'c'): 1}}


@pytest.fixture
def tn2_delta2():
    """Correct solution"""
    return {1: {('a', 'b'): 1,
                ('a', 'c'): 1,
                ('b', 'c'): 1,
                ('b', 'd'): 1,
                ('c', 'b'): 1,
                ('c', 'd'): 1,
                ('d', 'a'): 1,
                ('d', 'c'): 2},
            2: {('a', 'b', 'c'): 1,
                ('a', 'c', 'd'): 1,
                ('b', 'c', 'd'): 1,
                ('c', 'd', 'c'): 2,
                ('b', 'd', 'c'): 1,
                ('c', 'd', 'a'): 1,
                ('b', 'd', 'a'): 1,
                ('d', 'c', 'b'): 2},
            3: {('a', 'b', 'c', 'd'): 1,
                ('a', 'c', 'd', 'c'): 2,
                ('b', 'c', 'd', 'c'): 2,
                ('b', 'd', 'c', 'b'): 1,
                ('a', 'c', 'd', 'a'): 1,
                ('b', 'c', 'd', 'a'): 1,
                ('c', 'd', 'c', 'b'): 2},
            4: {('a', 'b', 'c', 'd', 'a'): 1,
                ('a', 'c', 'd', 'c', 'b'): 2,
                ('b', 'c', 'd', 'c', 'b'): 2,
                ('a', 'b', 'c', 'd', 'c'): 2},
            5: {('a', 'b', 'c', 'd', 'c', 'b'): 2}}


def test_paco(tn1, tn2, tn1_delta3):
    """Test the paco algorithm"""
    print('test paco')
    print(tn1)
    print(tn2)

    correct = tn1_delta3
    paths = all_paths_from_temporal_data(tn1, 3, skip_first=0, up_to_k=10)
    print(paths)
    for path in paths:
        print(path.nodes, path['frequency'])

    for e in tn1.edges.items(temporal=True):
        print(e)

    # for l in correct:
    #     for path in correct[l]:
    #         bug = True
    #         if path in paths:
    #             if paths[path]['frequency'] == correct[l][path]:
    #                 bug = False
    #         if bug:
    #             print("Error:")
    #             print(path)
    #             print(correct[l][path])
    #             if path in paths:
    #                 print(paths[path]["frequency"])
    #             else:
    #                 print(0)
# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
