#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_temporal_network.py -- Test environment for temp networks
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2021-04-01 17:59 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================

import pytest
from pathpy import Node, Edge
import pandas as pd
import numpy as np

from pathpy.models.temporal_network import (
    TemporalNetwork,
    TemporalNode,
    TemporalEdge,
    TemporalAttributes,
    TemporalNetwork,
    TemporalActivities
)


def test_temporal_node():
    """Test temporal nodes"""
    a = TemporalNode('a', start=1, end=4, color='red')
    a2 = TemporalNode('a', start=8, end=10, color='black')

    # a = TemporalNode('a', color='red')
    # a2 = TemporalNode('a', color='black')

    b = TemporalNode('b', color='blue')
    c = TemporalNode('c', color='green')

    e = TemporalEdge(a, b, uid='e', start=1, end=3, color='blue')
    f = TemporalEdge(b, c, uid='f', start=5, end=6, color='orange')

    # a.activities[4:50] = True
    # print(a.activities.attributes)
    net = TemporalNetwork()
    net.add_edge(e)
    net.add_edge(f)

    net.add_node(a2)

    print(net.nodes['a'].attributes)
    print(net.nodes['a'].activities)
    # print(net.edges)

    print(net.tnodes)
    #g = TemporalEdge(a, b, start=7, end=8, color='red')
    # net.add_edge(g)

    net.add_edge(a, b, uid='e', start=7, end=8, color='orange')
    net.add_edge('c', 'd', uid='g', timestamp=16, duration=30, color='yellow')
    # print(net.edges[a, b].attributes.attributes)
    # print(net.edges[a, b].activities.attributes)

    # print(net.edges[a, b]['color'])
    # print(net.edges)
    # print(net.edges.keys())
    # print(net.edges.values())
    # # print(net.tedges.set_index('interval').index.left.min())
    # # print(net.tedges.set_index('interval').index.right.max())
    # print(net.nodes)
    print(net.edges['g'].activities)
    # left = net.tnodes.set_index('interval').index.left
    # right = net.tnodes.set_index('interval').index.right

    # #left = left.loc[left != float('-inf')]

    # print(left[left != float('-inf')].min())
    # print(right[right != float('inf')].max() is np.nan)
    # # print(net.tnodes.set_index('interval').index.left.min())
    # # print(net.tnodes.set_index('interval').index.right.max())

    # # print(len(net.tedges))
    print(net)
    # print(net.start())
    # print(net.end())
    # for e in net.tedges.iterrows():
    #     print(e)
    # print(e['auto'])
    # a['color'] = 'blue'
    # # print(a.attributes)
    # # print(a['color'])
    # print(a[1:8])

    # a = TemporalAttributes()
    # # a[3.:6.:34.] = True
    # # a[5:9] = False
    # # a[1] = True
    # a[3:5, 'color'] = 'red'
    # a['color', 6] = 'blue'
    # a['value', 4] = 34.2343434
    # a['shape'] = 'rectangle'

    # a = TemporalActivities()
    # a[3.:6.:34.] = True
    # a[5:9] = False
    # a[1] = True

    # print(a[1:7])
    # print(a())
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
