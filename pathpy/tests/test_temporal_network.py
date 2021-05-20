#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_temporal_network.py -- Test environment for temp networks
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2021-05-20 17:22 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================

import pytest
import pathpy as pp
from pathpy import Node, Edge
import pandas as pd
import numpy as np

from pathpy.models.temporal_network import (
    TemporalDict,
    TemporalNode,
    TemporalEdge,
    TemporalNetwork
)


def test_temporal_dict():
    """Test the temporal dict"""

    d = TemporalDict()

    assert len(d) == 0

    d['a'] = 'first value'

    assert len(d) == 1
    for key, value in d.items():
        assert isinstance(key, tuple)
        assert value == 'first value'

        assert len(key) == 3
        assert key[0] == float('-inf')
        assert key[1] == float('inf')
        assert key[2] == 'a'

    d = TemporalDict()
    d[1, 3, 'color'] = 'red'

    assert (1, 3, 'color') in d
    assert d[1, 3, 'color'] == 'red'

    for key, value in d.items():
        assert key[0] == 1
        assert key[1] == 3
        assert key[2] == 'color'

    d[2:4, 'color'] = 'blue'
    d['color', 1:5] = 'green'
    d[2, 'color'] = 'pink'
    d['color', 5] = 'yellow'

    assert len(d) == 5
    assert 'yellow' in d.values()

    d[5, 'color'] = 'black'

    assert 'yellow' not in d.values()
    assert 'black' in d.values()

    d.update(2, 4, color='orange')

    assert d[2, 4, 'color'] == 'orange'
    assert 'blue' not in d.values()

    d.update(1, 5, color='magenta', shape='rectangle')

    assert d[1, 5, 'color'] == 'magenta'
    assert d[1, 5, 'shape'] == 'rectangle'
    assert 'green' not in d.values()

    assert len(d) == 6


def test_temporal_node():
    """Test temporal nodes"""

    a = TemporalNode('a', start=1, end=4, color='red')

    # a.event(start=5, end=7, active=True)
    # a.event(start=12, end=14)

    a.event(start=3, end=14, shape='circle')

    a.event(timestamp=8, color='blue')
    a.event(start=2, end=3, active=False)

    print(a._events)
    # print(a._temp_attributes)
    print(a.attributes)

    for node in a:
        print(node.attributes)
        print(node.start(), node.end())

    print(a.start(total=True))

    print(a._events.at(2.5))

    print(a['shape'])

    print(a[5:10])

    print(a[5, 'shape'])
    # # print(a._itree)
    # for i in a._events:
    #     print(i)
    # # print(node.attributes)

    # a['color']
    # a['color', 1:3]
    # a[5:8]

    # assert a[1, 4, 'color'] == 'red'
    # assert len(a.activities) == 1

    # a.active(start=7, end=9)
    # assert len(a.activities) == 2

    # print(a['color'])


# def test_temporal_edge():
#     """Test the temporal edge class"""

#     a = TemporalNode('a')
#     b = TemporalNode('b')

#     e = TemporalEdge(a, b, uid='a-b', start=5, end=10, color='red')
#     e = TemporalEdge(a, b, uid='a-b', timestamp=5, color='red')
#     e = TemporalEdge(a, b, uid='a-b', timestamp=5, duration=3, color='red')

#     # print(e.activities)
#     # print(e.attributes)

#     # e.update(2, 6, color='green')
#     # e.active(12, 16)
#     # print(e.activities)
#     # print(e.attributes)


# def test_direction_temporal_network():
#     """Test the directions of a temporal network"""
#     net = TemporalNetwork(directed=False)

#     net.add_edge('a', 'b', start=1, end=2)
#     net.add_edge('b', 'a', start=3, end=4)

#     assert len(net.edges) == 1
#     assert len(net.tedges) == 2

#     net = TemporalNetwork(directed=True)

#     net.add_edge('a', 'b', start=1, end=2)
#     net.add_edge('b', 'a', start=3, end=4)

#     assert len(net.edges) == 2
#     assert len(net.tedges) == 2

#     net.add_edge('a', 'b', start=3, end=4)

#     assert len(net.edges) == 2
#     assert len(net.tedges) == 3

#     a = TemporalNode('a')
#     b = TemporalNode('b')

#     ab = TemporalEdge(a, b, start=5, end=10, color='red')
#     ba = TemporalEdge(b, a, start=1, end=2, color='blue')
#     net = TemporalNetwork(directed=False)

#     net.add_edge(ab)
#     net.add_edge(ba)

#     assert len(net.edges) == 1
#     assert len(net.tedges) == 2


# def test_temporal_network():
#     """Test the temporal network class"""
#     net = TemporalNetwork()

#     a = TemporalNode('a')
#     b = TemporalNode('b')

#     net = TemporalNetwork()
#     net.add_node(a)
#     net.add_node(b)

#     net.add_edge(a, b, uid='a-b', start=1, end=2)
#     net.add_edge(a, b, uid='a-b', start=3, end=5)
#     # print(net)
#     # e = TemporalEdge(a, b, uid='a-b', start=5, end=10, color='red')

#     # # net.add_edge(e)
#     # net.add_edge('a', 'b', uid='a-b', start=1, end=6, color='red')
#     # net.add_edge('a', 'b', uid='a-b', start=13, end=16, color='green')
#     # net.add_edge('b', 'c', uid='b-c', start=4, end=8, color='red')
#     # net.add_edge('b', 'c', uid='b-c', start=10, end=18, color='green')
#     # net.add_edge('c', 'd', uid='b-c', color='green')

#     # print(net.edges['a-b'].attributes)
#     # print(net.edges['a-b'].activities)

#     # # d = {}
#     # # for edge in net.edges:
#     # #     print(edge.activities)
#     # # d = {**edge.activities for edge in net.edges}
#     # # print(d)

#     # print(net)

#     # x = {(1, 2): 2, (3, 4): 4, (4, 9): 3, (2, 5): 1, (0, 10): 0, (4, 5): 6}
#     # y = dict(sorted(x.items(), key=lambda item: item[0]))

#     # print(y)
# #     # a['color', 6] = 'blue'
# #     # a['value', 4] = 34.2343434
# #     # a['shape'] = 'rectangle'

#     # print(d)
#     # print('a' in d)

# # def test_temporal_node():
# #     """Test temporal nodes"""
# #     a = TemporalNode('a', start=1, end=4, color='red')
# #     a2 = TemporalNode('a', start=8, end=10, color='black')

# #     # a = TemporalNode('a', color='red')
# #     # a2 = TemporalNode('a', color='black')

# #     b = TemporalNode('b', color='blue')
# #     c = TemporalNode('c', color='green')

# #     e = TemporalEdge(a, b, uid='e', start=1, end=3, color='blue')
# #     f = TemporalEdge(b, c, uid='f', start=5, end=6, color='orange')

# #     # a.activities[4:50] = True
# #     # print(a.activities.attributes)
# #     net = TemporalNetwork()
# #     net.add_edge(e)
# #     net.add_edge(f)

# #     net.add_node(a2)

# #     print(net.nodes['a'].attributes)
# #     print(net.nodes['a'].activities)
# #     # print(net.edges)

# #     print(net.tnodes)
# #     #g = TemporalEdge(a, b, start=7, end=8, color='red')
# #     # net.add_edge(g)

# #     net.add_edge(a, b, uid='e', start=7, end=8, color='orange')
# #     net.add_edge('c', 'd', uid='g', timestamp=16, duration=30, color='yellow')
# #     # print(net.edges[a, b].attributes.attributes)
# #     # print(net.edges[a, b].activities.attributes)

# #     # print(net.edges[a, b]['color'])
# #     # print(net.edges)
# #     # print(net.edges.keys())
# #     # print(net.edges.values())
# #     # # print(net.tedges.set_index('interval').index.left.min())
# #     # # print(net.tedges.set_index('interval').index.right.max())
# #     # print(net.nodes)
# #     print(net.edges['g'].activities)
# #     # left = net.tnodes.set_index('interval').index.left
# #     # right = net.tnodes.set_index('interval').index.right

# #     # #left = left.loc[left != float('-inf')]

# #     # print(left[left != float('-inf')].min())
# #     # print(right[right != float('inf')].max() is np.nan)
# #     # # print(net.tnodes.set_index('interval').index.left.min())
# #     # # print(net.tnodes.set_index('interval').index.right.max())

# #     # # print(len(net.tedges))
# #     print(net)
# #     # print(net.start())
# #     # print(net.end())
# #     # for e in net.tedges.iterrows():
# #     #     print(e)
# #     # print(e['auto'])
# #     # a['color'] = 'blue'
# #     # # print(a.attributes)
# #     # # print(a['color'])
# #     # print(a[1:8])

# #     # a = TemporalAttributes()
# #     # # a[3.:6.:34.] = True
# #     # # a[5:9] = False
# #     # # a[1] = True
# #     # a[3:5, 'color'] = 'red'
# #     # a['color', 6] = 'blue'
# #     # a['value', 4] = 34.2343434
# #     # a['shape'] = 'rectangle'

# #     # a = TemporalActivities()
# #     # a[3.:6.:34.] = True
# #     # a[5:9] = False
# #     # a[1] = True

# #     # print(a[1:7])
# #     # print(a())
# #     # print(a._activities)

# #     # print(a['color', 0:9])
# #     # print(a['color'])
# #     # print(a[1])
# #     # df = pd.DataFrame(columns=['interval', 'active'])
# #     # df = df.append({'interval': pd.Interval(
# #     #     1, 4), 'active': True}, ignore_index=True)
# #     # df = df.append({'interval': pd.Interval(
# #     #     0, 8), 'active': True}, ignore_index=True)
# #     # df = df.append({'interval': pd.Interval(
# #     #     2, 3), 'active': True}, ignore_index=True)
# #     # df = df.append({'interval': pd.Interval(
# #     #     2, 3), 'active': False}, ignore_index=True)

# #     # df = df.set_index('interval')
# #     # print(df)
# #     # print(df.index.overlaps(pd.Interval(4, 7)))

# #     # print(df.sort_values(by=['interval']))

# #     # print(df['interval'].overlaps(pd.Interval(6, 7)))
# #     # v = TAttributes(color='red')
# #     # print(v['color'])
# #     # print(a['color', 0:5])


# # def test_temporal_network():
# #     """Test temporal network"""

# #     tn = TemporalNetwork()
# #     tn.add_node('a', start=1, end=9, time=1)
# #     tn.add_node('b', start=2, end=10, time=1)

# #     tn.add_edge('a', 'b', uid='a-b', begin=1, end=5, duration=3)
# #     tn.add_edge('a', 'b', uid='a-b', begin=15, end=20, duration=3)

# #     tn.add_edge('a', 'b', uid='a-b', timestamp=7)
# #     tn.add_edge('a', 'b', uid='a-b', timestamp=10)

# #     style = {}
# #     style['animation_begin'] = 3
# #     style['animation_end'] = 16
# #     style['animation_steps'] = 100
# #     style['animation_speed'] = 20

# # tn.plot('temp_net.html', **style)
# # tn.add_edge('b', 'c', uid='b-c', begin=10, end=15, duration=3)

# # print(tn.edges['a-b'].attributes)

# # print(tn.edges._intervals)
# # print(tn.edges._temporal_map)
# # for k, d, b, e in tn.edges.items(temporal=True):
# #     print(e)

# # print(tn.edges[0:30]._intervals)

# # print(tn.edges.slice(3, 7))
# # print(tn.edges.begin(finite=True))
# # print(tn.edges.end(finite=True))
# # tn.edges['a-b',1]
# # tn.edges[]
# # print(tn.edges.items(temporal=False))
# # print(tn.edges)


# def test_read_csv():
#     """Read temporal network from csv"""
#     # tn = pp.io.csv.read_temporal_network(
#     #     'temporal_edges.tedges', directed=True)
#     # tn = pp.io.csv.read_temporal_network(
#     #     'temporal_clusters.tedges', directed=False)

#     # print('done')
#     # # # print(tn.tnodes)
#     # print(tn)
#     # print(tn.nodes)

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
