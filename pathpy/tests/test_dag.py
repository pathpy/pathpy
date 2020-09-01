#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_dag.py -- Test environment for the DAG class
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Tue 2020-09-01 12:45 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================

import pytest
from pathpy import Node, Edge, Network
from pathpy.models.directed_acyclic_graph import DirectedAcyclicGraph


def test_basic():
    """Test some basic functions"""

    dag = DirectedAcyclicGraph()
    print(dag)


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
