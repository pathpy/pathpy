"""Network plots with tikz"""
#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : network_plots.py -- Network plots with tikz
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2021-06-24 18:20 juergen>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
from __future__ import annotations

from typing import Any


from pathpy import logger
from pathpy.visualisations.xutils import hex_to_rgb
from pathpy.visualisations._tikz.core import TikzPlot

# create logger
LOG = logger(__name__)


class NetworkPlot(TikzPlot):
    """Network plot class for a static network."""

    _kind = 'network'

    def __init__(self, data, **kwargs: Any):
        """Initialize network plot class"""
        super().__init__()
        self.data = data
        self.config = kwargs
        self.config['width'] = self.config.pop('width', 6)
        self.config['height'] = self.config.pop('height', 6)
        self.generate()

    def generate(self):
        """Clen up data"""
        self._compute_node_data()
        self._compute_edge_data()
        self._update_layout()

    def _compute_node_data(self):
        """Generate the data structure for the nodes"""
        default = {'uid', 'x', 'y', 'size', 'color', 'opacity'}
        mapping = {}

        for node in self.data['nodes']:
            for key in list(node):
                if key in mapping:
                    node[mapping[key]] = node.pop(key)
                if key not in default:
                    node.pop(key)

            color = node.get('color', None)
            if isinstance(color, str) and '#' in color:
                color = hex_to_rgb(color)
                node['color'] = f'{{{color[0]},{color[1]},{color[2]}}}'
                node['RGB'] = True

    def _compute_edge_data(self):
        """Generate the data structure for the edges"""
        default = {'uid', 'source', 'target', 'lw', 'color', 'opacity'}
        mapping = {'size': 'lw'}

        for edge in self.data['edges']:
            for key in list(edge):
                if key in mapping:
                    edge[mapping[key]] = edge.pop(key)
                if key not in default:
                    edge.pop(key)

            color = edge.get('color', None)
            if isinstance(color, str) and '#' in color:
                color = hex_to_rgb(color)
                edge['color'] = f'{{{color[0]},{color[1]},{color[2]}}}'
                edge['RGB'] = True

    def _update_layout(self):
        """update the layout"""
        layout = self.config.get('layout')

        if layout is None:
            return

        layout = {n['uid']: (n['x'], n['y']) for n in self.data['nodes']}

        width = self.config['width']
        height = self.config['height']
        keep_aspect_ratio = self.config.get('keep_aspect_ratio', True)
        margins = {'top': 0, 'left': 0, 'bottom': 0, 'right': 0}

        # calculate the scaling ratio
        ratio_x = float('inf')
        ratio_y = float('inf')

        # find min and max values of the points
        min_x = min(layout.items(), key=lambda item: item[1][0])[1][0]
        max_x = max(layout.items(), key=lambda item: item[1][0])[1][0]
        min_y = min(layout.items(), key=lambda item: item[1][1])[1][1]
        max_y = max(layout.items(), key=lambda item: item[1][1])[1][1]

        if max_x-min_x > 0:
            ratio_x = (width-margins['left']-margins['right']) / (max_x-min_x)
        if max_y-min_y > 0:
            ratio_y = (height-margins['top']-margins['bottom']) / (max_y-min_y)

        if keep_aspect_ratio:
            scaling = (min(ratio_x, ratio_y), min(ratio_x, ratio_y))
        else:
            scaling = (ratio_x, ratio_y)

        if scaling[0] == float('inf'):
            scaling = (1, scaling[1])
        if scaling[1] == float('inf'):
            scaling = (scaling[0], 1)

        # apply scaling to the points
        _layout = {}
        for n, (x, y) in layout.items():
            _x = (x)*scaling[0]
            _y = (y)*scaling[1]
            _layout[n] = (_x, _y)

        # find min and max values of new the points
        min_x = min(_layout.items(), key=lambda item: item[1][0])[1][0]
        max_x = max(_layout.items(), key=lambda item: item[1][0])[1][0]
        min_y = min(_layout.items(), key=lambda item: item[1][1])[1][1]
        max_y = max(_layout.items(), key=lambda item: item[1][1])[1][1]

        # calculate the translation
        translation = (((width-margins['left']-margins['right'])/2
                        + margins['left']) - ((max_x-min_x)/2 + min_x),
                       ((height-margins['top']-margins['bottom'])/2
                       + margins['bottom']) - ((max_y-min_y)/2 + min_y))

        # apply translation to the points
        for n, (x, y) in _layout.items():
            _x = (x)+translation[0]
            _y = (y)+translation[1]
            _layout[n] = (_x, _y)

        for node in self.data['nodes']:
            node['x'], node['y'] = _layout[node['uid']]

    def to_tikz(self):
        """Converter to Tex"""

        def _add_args(args: dict):
            string = ''
            for key, value in args.items():
                string += f',{key}' if value is True else f',{key}={value}'
            return string

        tikz = ''
        for node in self.data['nodes']:
            uid = node.pop('uid')
            string = '\\Vertex['
            string += _add_args(node)
            string += ']{{{}}}\n'.format(uid)
            tikz += string

        for edge in self.data['edges']:
            uid = edge.pop('uid')
            source = edge.pop('source')
            target = edge.pop('target')
            string = '\\Edge['
            string += _add_args(edge)
            string += ']({})({})\n'.format(source, target)
            tikz += string
        return tikz
# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
