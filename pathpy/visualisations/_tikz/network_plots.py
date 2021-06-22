"""Network plots with tikz"""
#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : network_plots.py -- Network plots with tikz
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2021-06-17 16:51 juergen>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional
from collections import defaultdict
from dataclasses import dataclass

from pathpy import logger
from pathpy.visualisations._tikz.core import TikzPlot

# pseudo load class for type checking
if TYPE_CHECKING:
    from pathpy.models.network import Network

# create logger
LOG = logger(__name__)


def network_plot(network: Network, **kwargs: Any):
    """Plot a static network with d3js"""
    result = NetworkPlot(network, **kwargs)
    result.generate()
    return result


class NetworkPlot(TikzPlot):
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
        nodes: list = []
        for uid, node in self.network.nodes.items():
            nodes.append({**{'uid': uid},
                          **node.attributes.copy()})
        self.data['nodes'] = nodes

    def _compute_edge_data(self):
        """Generate the data structure for the edges"""
        edges: list = []
        for uid, edge in self.network.edges.items():
            edges.append({**{'uid': uid,
                             'source': edge.v.uid,
                             'target': edge.w.uid,
                             'weight': edge.weight('weight')},
                          **edge.attributes.copy()})
        self.data['edges'] = edges

    def to_tex(self):
        """Converter to Tex"""

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
