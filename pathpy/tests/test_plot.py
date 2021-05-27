#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_plot.py -- Test environment for the Plot class
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2021-05-27 14:28 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================

import pytest
from pathpy import Network, TemporalNetwork, Node
from pathpy.visualisations import plot
import pathpy as pp


def test_network_plot():
    """Test the plot function on a network."""
    net = Network()
    net.add_node('a', color='red')
    net.add_node('b', size=40)
    net.add_edge('a', 'b', uid='a-b', color='blue')

    net.plot(filename='simple_plot.html')


# def test_parse_config():
#     """Test config parser."""

#     # Network
#     # -------
#     nodes = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
#     edges = [('a', 'b'), ('a', 'c'), ('c', 'd'), ('d', 'e'), ('e', 'c'), ('c', 'f'),
#              ('f', 'a'), ('f', 'g'), ('g', 'd'), ('g', 'g')]
#     net = (nodes, edges)

#     # Network attributes
#     # ------------------
#     name = ['Alice', 'Bob', 'Claire', 'Dennis', 'Esther', 'Frank', 'George']
#     age = [25, 31, 18, 47, 22, 23, 50]
#     gender = ['f', 'm', 'f', 'm', 'f', 'm', 'm']
#     is_formal = [False, False, True, True,
#                  True, False, True, False, False, False]

#     # Network dicts
#     # -------------
#     color_dict = {"m": "blue", "f": "red"}
#     shape_dict = {"m": "circle", "f": "rectangle"}
#     style_dict = {"m": "{shading=ball}", "f": None}
#     layout = {'a': (4.3191, -3.5352), 'b': (0.5292, -0.5292),
#               'c': (8.6559, -3.8008), 'd': (12.4117, -7.5239),
#               'e': (12.7, -1.7069), 'f': (6.0022, -9.0323),
#               'g': (9.7608, -12.7)}

#     # layout = {'a': (1, 1), 'b': (1, 1),
#     #           'c': (1, 1), 'd': (1, 1),
#     #           'e': (1, 1), 'f': (1, 1),
#     #           'g': (1, 1)}

#     # Visual style dict
#     # -----------------
#     visual_style = {}

#     # node styles
#     # -----------
#     #visual_style['node_size'] = 8
#     visual_style['node_color'] = [color_dict[g] for g in gender]
#     visual_style['node_opacity'] = .1
#     # visual_style['node_label'] = name
#     visual_style['node_label_position'] = 'below'
#     visual_style['node_label_distance'] = 15
#     visual_style['node_label_color'] = 'gray'
#     visual_style['node_label_size'] = 2
#     visual_style['node_shape'] = [shape_dict[g] for g in gender]
#     visual_style['node_style'] = [style_dict[g] for g in gender]
#     visual_style['node_label_off'] = {'e': True}
#     visual_style['node_math_mode'] = [True]
#     visual_style['node_id_as_label'] = {'f': True}
#     visual_style['node_pseudo'] = {'d': True}
#     # visual_style['node_coordinates'] = layout

#     # edge styles
#     # -----------
#     #visual_style['edge_size'] = [.3 + .3 * int(f) for f in is_formal]
#     visual_style['edge_color'] = 'black'
#     visual_style['edge_opacity'] = .8
#     visual_style['edge_curved'] = 0.1
#     visual_style['edge_label'] = {e[0]+'-'+e[1]: e[0]+e[1] for e in net[1]}
#     visual_style['edge_label_position'] = 'above'
#     visual_style['edge_label_distance'] = .6
#     visual_style['edge_label_color'] = 'gray'
#     visual_style['edge_label_size'] = {'a-c': 5}
#     visual_style['edge_style'] = 'dashed'
#     visual_style['edge_arrow_size'] = .2
#     visual_style['edge_arrow_width'] = .2

#     visual_style['edge_loop_size'] = 15
#     visual_style['edge_loop_position'] = 90
#     visual_style['edge_loop_shape'] = 45
#     visual_style['edge_directed'] = [True, True, False, True, True, False, True,
#                                      True, True, True]
#     visual_style['edge_label'][('a', 'c')] = '\\frac{\\alpha}{\\beta}'
#     visual_style['edge_math_mode'] = {'a-c': True}
#     visual_style['edge_not_in_bg'] = {'f-a': True}

#     # general options
#     # ---------------
#     visual_style['unit'] = 'mm'
#     visual_style['layout'] = layout
#     visual_style["margin"] = 5
#     visual_style["width"] = 100
#     visual_style["height"] = 60
#     visual_style['keep_aspect_ratio'] = True
#     visual_style['edge_curved'] = 0.1

#     #visual_style['template'] = 'test.html'
#     net = Network()
#     net.add_node('a', age=25, color='red')
#     net.add_node('b', age=31, color='yellow')
#     net.add_node('c', age=18, color='green')
#     net.add_node('d', age=47, color='orange')
#     net.add_node('e', age=22, size=2)
#     net.add_node('f', age=23, size=10)
#     net.add_node('g', age=50, opacity=.6)

#     net.add_edge('a', 'b')
#     net.add_edge('a', 'c')
#     net.add_edge('c', 'd')
#     net.add_edge('d', 'e')
#     net.add_edge('e', 'c')
#     net.add_edge('c', 'f')
#     net.add_edge('f', 'a')
#     net.add_edge('f', 'g')
#     net.add_edge('g', 'd')
#     net.add_edge('g', 'g')

#     # plot(net, filename=None, mapping={'age': 'size'}, **visual_style)
#     # plot(net, filename='MyTestPDF.pdf', **visual_style)
#     #plot(net, filename=None, **visual_style)
#     #plot(net, filename='d3js_test.html', **visual_style)
#     # net.plot()
#     # plot(net, filename='MyTestTEX.tex', **visual_style)
#     # pp.plot(net, filename='MyTestPDF.pdf', **visual_style)

#     #plot(net, filename='MyTestTEX.tex')
#     # net.plot(filename='MyTestPDF.pdf', **visual_style)
#     # l = pp.layout(net, layout='fr')
#     # net.plot(layout=l)
#     # # plot(net, filename=None, **visual_style)

#     #net.plot(filename='d3js_test.html', **visual_style)


# def test_d3js():
#     """Modify d3js"""
#     net = Network(directed=False)
#     net.add_node('a', size=10, coordinates=(0, 0))
#     net.add_node('b', size=15, coordinates=(1, 1))
#     net.add_node('c', size=20, coordinates=(2, 2))
#     net.add_edge('a', 'b')
#     net.add_edge('b', 'c')

#     # net.add_edge('b', 'c')
#     # net.plot(filename='d3js_test.html', curved=True,
#     #          edge_style='{stubs=5mm}', template='test_template.html', css='style.css')

#     style = {
#         'node_color': 'red',
#         'label_color': 'black',
#         'edge_color': 'red',
#     }
#     net.plot(filename='d3js_test.html', **style)


def test_temporal_network():
    """Test to plot a temporal network."""
    tn = TemporalNetwork(directed=False)
    # tn.add_node('a', color='green', size=20)
    # tn.nodes['a'].update(color='blue', size=40, t=4)
    # tn.add_node('b', color='blue', t=8)
    tn.add_edge('a', 'b', timestamp=1, color='red', size=4)
    tn.add_edge('b', 'a', timestamp=3, color='blue')
    tn.add_edge('b', 'c', timestamp=3, color='green')
    tn.add_edge('d', 'c', timestamp=4, color='orange')
    tn.add_edge('c', 'd', timestamp=5, color='yellow')
    tn.add_edge('c', 'b', timestamp=6, color='black')
    tn.add_edge('a', 'b', timestamp=7, color='gray', size=8)
    tn.add_edge('b', 'a', timestamp=8, color='white')

    tn.nodes['a'][2, 'color'] = 'green'
    tn.nodes['a'][3, 'color'] = 'red'
    tn.nodes['a'][6, 'color'] = 'yellow'
    style = {
        # 'node_color': 'gray',
        'curved': True,
    }

    # print(tn)

    # print('\n\n')
    tn.plot(filename='d3js_test.html', **style)
    # tn.add_node('g')
    # print(tn.nodes['a']._events)
    # for e in tn.nodes['a'][:]:
    #     print(e.attributes)
# #     # for node in tn.nodes.values():
#     #     node.update(color='gray', size=16, t=0)

#     # for i, (uid, edge, begin, end) in enumerate(tn.edges.temporal()):
#     #     edge.v.update(color='red', size=20, t=begin)
#     #     edge.v.update(color='gray', size=16, t=end)
#     #     edge.w.update(color='red', size=20, t=begin)
#     #     edge.w.update(color='gray', size=16, t=end)
#     # #     print('-------')
#     # #     print(begin)
#     # #     if i == 2:
#     # #         break


#     # print(type(tn.edges['a', 'b'].attributes))

#     # print(tn.number_of_edges())
#     # v = Node('v')

#     # v.update(color='a')
#     # print(type(v.attributes))
#     # print(v.attributes)
#     # a = TemporalAttributes()
#     # a.update(color='green', timestamp=5)
#     # a.update(color='orange', timestamp=6)
#     # print(a.to_frame(history=True))

#     # print(a['color'])
#     # print(a)

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
