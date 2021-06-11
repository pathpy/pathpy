"""Network plots with d3js"""
#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : network_plots.py -- Network plots with d3js
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Fri 2021-06-11 12:23 juergen>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional
from pathpy.visualisations.new_plot import PathPyPlot

# pseudo load class for type checking
if TYPE_CHECKING:
    from pathpy.models.network import Network


def network_plot(network: Network, **kwargs: Any):
    """Plot a static network with d3js"""
    result = NetworkPlot(network, **kwargs)
    return result


class D3jsPlot(PathPyPlot):
    """Base class for plotting d3js objects"""

    def __init__(self, **kwargs: Any):
        """Initialize plot class"""
        super().__init__()
        if kwargs:
            self.config = kwargs

    def generate(self):
        """Function to generate the plot"""
        raise NotImplementedError

    def save(self):
        """Function to save the plot"""
        print('Save the plot')

    def show(self):
        """Function to show the plot"""
        print('Show the plot')


class NetworkPlot(D3jsPlot):
    """Network plot class for a static network."""

    _kind = 'network'

    def __init__(self, network: Network, **kwargs: Any):
        """Initialize network plot class"""
        super().__init__(**kwargs)
        self.network = network

    def generate(self):
        """Function to generate the plot"""
        raise NotImplementedError


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
