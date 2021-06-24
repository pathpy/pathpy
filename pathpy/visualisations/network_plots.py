"""Network plots with d3js"""
#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : network_plots.py -- Network plots with d3js
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2021-06-24 15:31 juergen>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
from __future__ import annotations

import json
import numpy as np

from typing import TYPE_CHECKING, Any
from collections import defaultdict

from pathpy import logger
from pathpy.visualisations.new_plot import PathPyPlot
from pathpy.visualisations.xutils import rgb_to_hex, hex_to_rgb, Colormap

# pseudo load class for type checking
if TYPE_CHECKING:
    from pathpy.models.network import Network

# create logger
LOG = logger(__name__)


def network_plot(network: Network, **kwargs: Any):
    """Plot a static network.

    This function generates a static plot of the network, thereby different
    output can be chosen, including

    - interactive html with d3js
    - tex file with tikz code
    - pdf from the tex source
    - png based on matplotlib

    The appearance of the plot can be modified by keyword arguments which will
    be explained in more detail below.

    Parameters
    ----------
    network : Network

        A :py:class`Network` object

    kwargs : keyword arguments, optional (default = no attributes)

        Attributes used to modify the appearance of the plot.
        For details see below.

    Keyword arguments used for the plotting:

    filename : str optional (default = None)

        Filename to save. The file ending specifies the output. i.e. is the
        file ending with '.tex' a tex file will be created; if the file ends
        with '.pdf' a pdf is created; if the file ends with '.html', a html
        file is generated generated. If no ending is defined a temporary html
        file is compiled and shown.


    **Nodes:**

    - ``node_size`` : diameter of the node

    - ``node_color`` : The fill color of the node. Possible values are:

            - A single color string referred to by name, RGB or RGBA code, for
              instance 'red' or '#a98d19'.

            - A sequence of color strings referred to by name, RGB or RGBA
              code, which will be used for each point's color recursively. For
              instance ['green','yellow'] all points will be filled in green or
              yellow, alternatively.

            - A column name or position whose values will be used to color the
              marker points according to a colormap.

    - ``node_opacity`` : fill opacity of the node. The default is 1. The range
      of the number lies between 0 and 1. Where 0 represents a fully
      transparent fill and 1 a solid fill.


    References
    ----------
    .. [tn] https://github.com/hackl/tikz-network

    """
    return NetworkPlot(network, **kwargs)


class NetworkPlot(PathPyPlot):
    """Network plot class for a static network."""

    _kind = 'network'

    def __init__(self, network: Network, **kwargs: Any):
        """Initialize network plot class"""
        super().__init__()
        self.network = network
        self.config = kwargs
        self.generate()

    def generate(self):
        """Function to generate the plot"""
        self._compute_edge_data()
        self._compute_node_data()
        # self._convert_colors()
        # _convert_size()
        # _update_layout()
        self._cleanup_data()

    def _compute_node_data(self):
        """Generate the data structure for the nodes"""

        # generate temporary varialbes to store the data
        nodes: dict = {}
        attr: defaultdict = defaultdict(dict)

        for uid, node in self.network.nodes.items():
            nodes[uid] = {**{'uid': uid},
                          **node.attributes.copy()}

            attr['color'][uid] = node.attributes.get('color')

        attr['color'] = self._convert_colors(attr['color'])

        for attribute in attr:
            for key, value in attr[attribute].items():
                nodes[key][attribute] = value

        print(nodes)
        self.data['nodes'] = nodes

    def _compute_edge_data(self):
        """Generate the data structure for the edges"""
        edges: dict = {}
        for uid, edge in self.network.edges.items():
            edges[uid] = {**{'uid': uid,
                             'source': edge.v.uid,
                             'target': edge.w.uid,
                             'weight': edge.weight('weight')},
                          **edge.attributes.copy()}
        self.data['edges'] = edges

    def _convert_colors(self, colors: dict, mode: str = 'node') -> dict:
        """Convert colors to hex if rgb"""

        # get style from the config
        style = self.config.get(f'{mode}_color')

        # check if new attribute is a single object
        if isinstance(style, (str, int, float, tuple)):
            colors = {k: style for k in colors}

        # check if new attribute is a dict
        elif isinstance(style, dict):
            colors.update(**{k: v for k, v in style.items() if k in colors})

        # check if new attribute is a list
        elif isinstance(style, list):
            for i, k in enumerate(colors):
                try:
                    colors[k] = style[i]
                except IndexError:
                    pass

        # check if numerical values are given
        values = [v for v in colors.values() if isinstance(v, (int, float))]

        if values:
            # load colormap to map numerical values to color
            cmap = self.config.get(f'{mode}_cmap', Colormap())
            cdict = {values[i]: tuple(c[:3])
                     for i, c in enumerate(cmap(values, bytes=True))}

        # convert colors to hex if not already string
        for key, value in colors.items():
            if isinstance(value, tuple):
                colors[key] = rgb_to_hex(value)
            elif isinstance(value, (int, float)):
                colors[key] = rgb_to_hex(cdict[value])

        # return all colors wich are not None
        return {k: v for k, v in colors.items() if v is not None}

    def _cleanup_data(self):
        """Clean up final data structure"""
        self.data['nodes'] = list(self.data['nodes'].values())
        self.data['edges'] = list(self.data['edges'].values())

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
