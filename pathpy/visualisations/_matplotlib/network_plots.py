"""Network plots with matplotlib"""
#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : network_plots.py -- Network plots with matplotlib
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2021-06-24 17:48 juergen>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
from typing import Any, Optional

import numpy as np
from pathpy import logger
from pathpy.visualisations._matplotlib.core import MatplotlibPlot

# create logger
LOG = logger(__name__)


class NetworkPlot(MatplotlibPlot):
    """Network plot class for a static network."""

    _kind = 'network'

    def __init__(self, data, **kwargs: Any):
        """Initialize network plot class"""
        super().__init__()
        self.data = data
        self.config = kwargs
        self.generate()

    def generate(self):
        """Clen up data"""
        self._compute_node_data()
        self._compute_edge_data()

    def _compute_node_data(self):
        """Generate the data structure for the nodes"""
        default = {'uid': None, 'x': 0, 'y': 0,
                   'size': 30, 'color': 'blue', 'opacity': 1.0}

        nodes = {key: [] for key in default}

        for node in self.data['nodes']:
            for key, value in default.items():
                nodes[key].append(node.get(key, value))

        self.data['nodes'] = nodes

    def _compute_edge_data(self):
        """Generate the data structure for the edges"""
        default = {'uid': None, 'size': 5, 'color': 'red', 'opacity': 1.0}

        edges = {**{key: [] for key in default}, **{'line': []}}

        for edge in self.data['edges']:
            source = self.data['nodes']['uid'].index(edge.get('source'))
            target = self.data['nodes']['uid'].index(edge.get('target'))
            edges['line'].append([(self.data['nodes']['x'][source],
                                   self.data['nodes']['x'][target]),
                                  (self.data['nodes']['y'][source],
                                   self.data['nodes']['y'][target])])

            for key, value in default.items():
                edges[key].append(edge.get(key, value))

        self.data['edges'] = edges

    def to_fig(self):
        """Convert data to figure"""
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        ax.set_axis_off()

        # plot edges
        for i in range(len(self.data['edges']['uid'])):
            ax.plot(*self.data['edges']['line'][i],
                    color=self.data['edges']['color'][i],
                    alpha=self.data['edges']['opacity'][i],
                    zorder=1
                    )

        # plot nodes
        ax.scatter(
            self.data['nodes']['x'],
            self.data['nodes']['y'],
            s=self.data['nodes']['size'],
            c=self.data['nodes']['color'],
            alpha=self.data['nodes']['opacity'],
            zorder=2,
        )
        return plt

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
