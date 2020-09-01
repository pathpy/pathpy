#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_dag.py -- Test environment for the DAG class
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Tue 2020-09-01 16:56 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================

import pytest
from pathpy import Node, Edge, Network
from pathpy.models.directed_acyclic_graph import DirectedAcyclicGraph


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

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
