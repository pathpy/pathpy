#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_temporal_network.py -- Test environment for temp networks
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2020-06-25 21:13 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================

import pytest
from pathpy import Node, Edge

from pathpy.models.temporal_network import (TemporalNetwork)


def test_temporal_network():
    """Test temporal network"""

    tn = TemporalNetwork()
    tn.add_node('a', start=1, end=9, time=1)
    tn.add_node('b', start=2, end=10, time=1)

    tn.add_edge('a', 'b', uid='a-b', begin=1, end=5, duration=3)
    tn.add_edge('a', 'b', uid='a-b', begin=15, end=20, duration=3)
    style = {}
    style['animation_begin'] = 3
    style['animation_end'] = 16
    style['animation_steps'] = 100
    style['animation_speed'] = 20
    # tn.plot('temp_net.html', **style)
    # tn.add_edge('b', 'c', uid='b-c', begin=10, end=15, duration=3)

    # print(tn.edges['a-b'].attributes)

    # print(tn.edges._intervals)
    # print(tn.edges._temporal_map)
    # for k, d, b, e in tn.edges.items(temporal=True):
    #     print(e)

    # print(tn.edges[0:30]._intervals)

    # print(tn.edges.slice(3, 7))
    # print(tn.edges.begin(finite=True))
    # print(tn.edges.end(finite=True))
    # tn.edges['a-b',1]
    # tn.edges[]
    # print(tn.edges.items(temporal=False))
    # print(tn.edges)


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
