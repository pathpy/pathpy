"""Backend for tikz."""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : tikz.py -- Module to draw a tikz-network
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Tue 2020-05-05 14:26 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from __future__ import annotations  # remove for python 3.8
from random import uniform

from pathpy import logger
from pathpy.visualisations.utils import UnitConverter, bend_factor

# create logger
LOG = logger(__name__)


class Tikz:
    """Class to draw tikz objects."""

    def __init__(self) -> None:
        """Initialize tikz drawer"""
        self.default_node_kwargs = {
            'size': 'size',
            'color': 'color',
            'opacity': 'opacity',
            'label': 'label',
            'label_position': 'position',
            'label_distance': 'distance',
            'label_color': 'fontcolor',
            'label_size': 'fontscale',
            'shape': 'shape',
            'style': 'style',
            'layer': 'layer',
        }
        self.default_node_args = {
            'label_off': 'NoLabel',
            'id_as_label': 'IdAsLabel',
            'math_mode': 'Math',
            'rgb': 'RGB',
            'pseudo': 'Pseudo',
        }
        self.default_edge_kwargs = {
            'size': 'lw',
            'color': 'color',
            'opacity': 'opacity',
            'curved': 'bend',
            'label': 'label',
            'label_position': 'position',
            'label_distance': 'distance',
            'label_color': 'fontcolor',
            'label_size': 'fontscale',
            'style': 'style',
            'loop_size': 'loopsize',
            'loop_position': 'loopposition',
            'loop_shape': 'loopshape',
        }
        self.default_edge_args = {
            'directed': 'Direct',
            'math_mode': 'Math',
            'rgb': 'RGB',
            'not_in_bg': 'NotInBG',
        }
        self.default_kwargs = {
            'nodes': self.default_node_kwargs,
            'edges': self.default_edge_kwargs,
        }

        self.default_args = {
            'nodes': self.default_node_args,
            'edges': self.default_edge_args,
        }

    def to_tex(self, figure) -> str:
        """Convert figure to a single html document."""
        LOG.debug('Generate single tex document.')

        # clean config
        config = figure['config']
        config.pop('node')
        config.pop('edge')

        # initialize unit converters
        px2cm = UnitConverter('px', 'cm')
        px2pt = UnitConverter('px', 'pt')

        for key in ['width', 'height']:
            config[key] = px2cm(config[key])

        # clean data
        data = figure['data']

        for node in data['nodes']:
            node['size'] = px2cm(node['size'])
        for edge in data['edges']:
            edge['size'] = px2pt(edge['size'])
            if edge.get('curved', None) is not None:
                if not config.get('curved', False):
                    edge.pop('curved')
                else:
                    edge['curved'] = bend_factor(edge['curved'])
            if not config.get('directed', False):
                edge.pop('directed', None)

        tex = ''
        for element in ['nodes', 'edges']:
            for obj in data[element]:
                if element == 'nodes':
                    _xy = obj.get('coordinates', None)
                    if _xy is None:
                        _xy = (uniform(0, config['width']),
                               uniform(0, config['height']))
                    else:
                        _xy = (px2cm(_xy[0]), px2cm(_xy[1]))
                    string = '\\Vertex[x={x:.{n}f},y={y:.{n}f}' \
                        ''.format(x=_xy[0], y=_xy[1], n=3)
                else:
                    string = '\\Edge['

                for key, value in self.default_kwargs[element].items():
                    if key in obj:
                        string += ',{}={}'.format(value, obj[key])

                for key, value in self.default_args[element].items():
                    if key in obj and obj[key] is True:
                        string += ',{}'.format(value)

                if element == 'nodes':
                    string += ']{{{}}}\n'.format(obj['uid'])
                else:
                    string += ']({})({})\n'.format(obj['source'],
                                                   obj['target'])
                tex += string
        return tex

    def to_csv(self, figure) -> str:
        """Convert figure to a single html document."""
        LOG.debug('Generate csv documents.')
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
