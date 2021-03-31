#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_temporal_network.py -- Test environment for temp networks
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Wed 2021-03-31 18:19 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================

import pytest
from pathpy import Node, Edge
import pandas as pd


from pathpy.models.temporal_network import (
    TemporalNetwork,
    TemporalNode,
    TemporalEdge,
    TemporalAttributes,
    TemporalNetwork)


def test_temporal_node():
    """Test temporal nodes"""
    a = TemporalNode('a', start=1, end=4, color='red')
    b = TemporalNode('b', color='blue')
    c = TemporalNode('c', color='green')

    e = TemporalEdge(a, b, start=1, end=3, color='blue')
    f = TemporalEdge(b, c, start=5, end=6, color='orange')

    net = TemporalNetwork()
    net.add_edge(e)
    net.add_edge(f)
    print(net.edges)

    # print(e['auto'])
    # a['color'] = 'blue'
    # # print(a.attributes)
    # # print(a['color'])
    # print(a[1:8])

    # a = TemporalAttributes()
    # a[3.:6.:34.] = True
    # a[5:9] = False
    # a[1] = True
    # a[3:5, 'color'] = 'red'
    # a['color', 6] = 'blue'
    # a['value', 4] = 34.2343434
    # a['shape'] = 'rectangle'

    # print(a._activities)

    # print(a['color', 0:9])
    # print(a['color'])
    # print(a[1])
    # df = pd.DataFrame(columns=['interval', 'active'])
    # df = df.append({'interval': pd.Interval(
    #     1, 4), 'active': True}, ignore_index=True)
    # df = df.append({'interval': pd.Interval(
    #     0, 8), 'active': True}, ignore_index=True)
    # df = df.append({'interval': pd.Interval(
    #     2, 3), 'active': True}, ignore_index=True)
    # df = df.append({'interval': pd.Interval(
    #     2, 3), 'active': False}, ignore_index=True)

    # df = df.set_index('interval')
    # print(df)
    # print(df.index.overlaps(pd.Interval(4, 7)))

    # print(df.sort_values(by=['interval']))

    # print(df['interval'].overlaps(pd.Interval(6, 7)))
    # v = TAttributes(color='red')
    # print(v['color'])
    # print(a['color', 0:5])


# def test_temporal_network():
#     """Test temporal network"""

#     tn = TemporalNetwork()
#     tn.add_node('a', start=1, end=9, time=1)
#     tn.add_node('b', start=2, end=10, time=1)

#     tn.add_edge('a', 'b', uid='a-b', begin=1, end=5, duration=3)
#     tn.add_edge('a', 'b', uid='a-b', begin=15, end=20, duration=3)

#     tn.add_edge('a', 'b', uid='a-b', timestamp=7)
#     tn.add_edge('a', 'b', uid='a-b', timestamp=10)

#     style = {}
#     style['animation_begin'] = 3
#     style['animation_end'] = 16
#     style['animation_steps'] = 100
#     style['animation_speed'] = 20

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
