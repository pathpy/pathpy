#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_visualisations.py -- Test environment for the plotting
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Tue 2021-06-22 12:51 juergen>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================

import pytest
import pathpy as pp
from pathpy.visualisations.new_plot import _get_plot_backend
from pathpy.visualisations.network_plots import network_plot


def test_get_backend():
    """Test to load the plotting backends"""
    module = _get_plot_backend(backend=None, filename=None)
    d3js = _get_plot_backend(backend='d3js', filename=None)
    tikz = _get_plot_backend(backend='tikz', filename=None)
    matplotlib = _get_plot_backend(backend='matplotlib', filename=None)


def test_network_plot_d3js():
    """Test the plot function of a static network with d3js"""
    net = pp.Network()
    net.add_node('a', color='blue', x=1, y=2)
    net.add_node('b', color='green', x=2, y=3)
    net.add_node('c', color='yellow', x=3, y=1)
    net.add_edge('a', 'b', color='red')
    net.add_edge('b', 'c')

    plot = network_plot(net, backend='d3js')
    #plot = network_plot(net)
    plot.save('test.html')
    # plot.show()

    # plot.save('test.tex')
    # plot.show()


# def test_network_plot_tikz():
#     """Test the plot function of a static network with tikz"""

#     net = pp.Network()
#     net.add_edge('a', 'b', color='red')
#     net.add_edge('b', 'c')

#     plot = network_plot(net, backend='tikz')
#     print(plot)


# def test_network_plot_matplotlib():
#     """Test the plot function of a static network with matplotlib"""
#     plot = network_plot('net', backend='matplotlib')
#     assert plot == 'matplotlib'


# def possible_patterns():
#     """some possible plotting patern"""

#     net = pp.Network()
#     net.add_edge('a', 'b', color='red')
#     net.add_edge('b', 'c')

#     net.plot()
#     net.plot('test.html')
#     net.plot('test.tex')
#     net.plot('test.png')
#     net.plot('test.pdf', backend='matplotlib')
#     net.plot('test.pdf', backend='tikz')

#     fig = network_plot(net)
#     fig.show()
#     fig.save('test.html')
#     fig.save('test.pdf')

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
