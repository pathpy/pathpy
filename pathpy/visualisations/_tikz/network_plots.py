"""Network plots with tikz"""
#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : network_plots.py -- Network plots with tikz
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Mon 2021-06-28 15:25 juergen>
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
                    node.pop(key, None)

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
                    edge.pop(key, None)

            color = edge.get('color', None)
            if isinstance(color, str) and '#' in color:
                color = hex_to_rgb(color)
                edge['color'] = f'{{{color[0]},{color[1]},{color[2]}}}'
                edge['RGB'] = True

    def _update_layout(self, size: float = .6):
        """update the layout"""
        layout = self.config.get('layout')

        if layout is None:
            return

        # get data
        layout = {n['uid']: (n['x'], n['y']) for n in self.data['nodes']}
        sizes = {n['uid']: n.get('size', size) for n in self.data['nodes']}

        # get config values
        width = self.config['width']
        height = self.config['height']
        keep_aspect_ratio = self.config.get('keep_aspect_ratio', True)
        margin = self.config.get('margin', 0.0)
        margins = {'top': margin, 'left': margin,
                   'bottom': margin, 'right': margin}

        # calculate the scaling ratio
        x_ratio = y_ratio = float('inf')

        # calculate absolute min and max coordinates
        x_absolute = []
        y_absolute = []
        for uid, (_x, _y) in layout.items():
            _s = sizes[uid]/2
            x_absolute.extend([_x-_s, _x+_s])
            y_absolute.extend([_y-_s, _y+_s])

        # calculate min and max center coordinates
        x_values, y_values = zip(*layout.values())
        x_min, x_max = min(x_values), max(x_values)
        y_min, y_max = min(y_values), max(y_values)

        # adaped margins
        margins['left'] += abs(x_min-min(x_absolute))
        margins['bottom'] += abs(y_min-min(y_absolute))
        margins['top'] += abs(y_max-max(y_absolute))
        margins['right'] += abs(x_max-max(x_absolute))

        if x_max-x_min > 0:
            x_ratio = (width-margins['left']-margins['right']) / (x_max-x_min)
        if y_max-y_min > 0:
            y_ratio = (height-margins['top']-margins['bottom']) / (y_max-y_min)

        if keep_aspect_ratio:
            scaling = (min(x_ratio, y_ratio), min(x_ratio, y_ratio))
        else:
            scaling = (x_ratio, y_ratio)

        if scaling[0] == float('inf'):
            scaling = (1, scaling[1])
        if scaling[1] == float('inf'):
            scaling = (scaling[0], 1)

        x_values = []
        y_values = []

        # apply scaling to the points
        _layout = {n: (x*scaling[0], y*scaling[1])
                   for n, (x, y) in layout.items()}

        # find min and max values of the points
        x_values, y_values = zip(*_layout.values())
        x_min, x_max = min(x_values), max(x_values)
        y_min, y_max = min(y_values), max(y_values)

        # calculate the translation
        translation = (((width-margins['left']-margins['right'])/2
                        + margins['left']) - ((x_max-x_min)/2 + x_min),
                       ((height-margins['top']-margins['bottom'])/2
                       + margins['bottom']) - ((y_max-y_min)/2 + y_min))

        # apply translation to the points
        _layout = {n: (x+translation[0], y+translation[1])
                   for n, (x, y) in _layout.items()}

        # update node position for the plot
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
