"""Network plots with d3js"""
#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : network_plots.py -- Network plots with d3js
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Fri 2021-06-11 13:34 juergen>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional
from dataclasses import dataclass, asdict

from pathpy.visualisations.new_plot import PathPyPlot

# pseudo load class for type checking
if TYPE_CHECKING:
    from pathpy.models.network import Network


def network_plot(network: Network, **kwargs: Any):
    """Plot a static network with d3js"""
    result = NetworkPlot(network, **kwargs)
    result.generate()
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


@dataclass
class NodeData:
    """Class to store nodes for plotting"""
    uid: str
    size: Optional[float] = None
    color: Optional[str] = None
    opacity: Optional[float] = None
    x: Optional[float] = None
    y: Optional[float] = None


@dataclass
class EdgeData:
    """Class to store nodes for plotting"""
    uid: str
    source: str
    target: str
    size: Optional[float] = None
    color: Optional[str] = None
    opacity: Optional[float] = None
    weight: float = 1.0
    # directed: bool = True
    # curved: bool = True


class NetworkPlot(D3jsPlot):
    """Network plot class for a static network."""

    _kind = 'network'

    def __init__(self, network: Network, **kwargs: Any):
        """Initialize network plot class"""
        super().__init__(**kwargs)
        self.network = network

    def generate(self):
        """Function to generate the plot"""
        self._compute_edge_data()
        self._compute_node_data()

    def _compute_node_data(self):
        """Generate the data structure for the nodes"""
        nodes: dict = {}
        for uid, node in self.network.nodes.items():
            nodes[uid] = NodeData(
                uid,
                size=node['size'],
                color=node['color'],
                opacity=node['opacity'],
                x=node['x'],
                y=node['y'],
            )
        self.data['nodes'] = nodes

    def _compute_edge_data(self):
        """Generate the data structure for the edges"""
        edges: dict = {}
        for uid, edge in self.network.edges.items():
            edges[uid] = EdgeData(
                uid,
                edge.v.uid,
                edge.w.uid,
                size=edge['size'],
                color=edge['color'],
                opacity=edge['opacity'],
                weight=edge.weight('weight'),
            )
        self.data['edges'] = edges

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
