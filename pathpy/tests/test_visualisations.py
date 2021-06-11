#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_visualisations.py -- Test environment for the plotting
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Fri 2021-06-11 12:45 juergen>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================

import pytest
import pathpy as pp
from pathpy.visualisations.new_plot import _get_plot_backend, network_plot


def test_get_backend():
    """Test to load the plotting backends"""
    module = _get_plot_backend(backend=None, filename=None)
    d3js = _get_plot_backend(backend='d3js', filename=None)
    tikz = _get_plot_backend(backend='tikz', filename=None)
    matplotlib = _get_plot_backend(backend='matplotlib', filename=None)


def test_network_plot_d3js():
    """Test the plot function of a static network with d3js"""
    net = pp.Network()
    net.add_edge('a', 'b')
    net.add_edge('b', 'c')

    plot = network_plot(net, backend='d3js')
    # print(plot)


def test_network_plot_tikz():
    """Test the plot function of a static network with tikz"""
    plot = network_plot('net', backend='tikz')
    assert plot == 'tikz'


def test_network_plot_matplotlib():
    """Test the plot function of a static network with matplotlib"""
    plot = network_plot('net', backend='matplotlib')
    assert plot == 'matplotlib'


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
