#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : _d3js.py -- Module to draw a d3js-network
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Tue 2020-01-14 16:01 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
import os
import json
from functools import singledispatchmethod
from .. import logger
from ..core.base import BaseStaticNetwork, BaseTemporalNetwork, BaseHigherOrderNetwork
from .painter import Painter, Painting
from .utils import _clean_dict

log = logger(__name__)


class D3jsNetworkPainter(Painter):
    def __init__(self):

        # initialize the base class
        super().__init__()

        # node and edge kwds
        self.d3js_kwds = ['uid', 'label', 'text', 'size', 'color', 'time',
                          'group', 'source', 'target', 'euclidean', 'utm',
                          'opacity']

        # config args
        self.d3js_args = ['width', 'height',
                          'coordinates', 'euclidean', 'utm', 'temporal']

    @singledispatchmethod
    def draw(self, network, **kwargs):
        raise NotImplementedError

    @draw.register(BaseStaticNetwork)
    @draw.register(BaseHigherOrderNetwork)
    def _draw_static(self, network, **kwargs):
        log.debug('I\'m a static d3js-network')

        # get data and config from the original network
        data, config = self.parse(network, **kwargs)

        # create new painting
        painting = Painting()

        # load base config and add it to the painting
        painting.config.update(self._load_base_config())

        # get data in a nicer format
        nodes = data['nodes']
        edges = data['edges']

        # update config
        for key in self.d3js_args:
            if key in config['general']:
                painting.config[key] = config['general'][key]

        # check for grouped nodes
        if 'group' in nodes.columns:
            groups = list(nodes
                          .groupby('group')
                          .groups.keys())
            painting.config['widgets']['filter']['enabled'] = True
            painting.config['widgets']['filter']['groups'].extend(groups)

        if 'euclidean' in nodes.columns:
            painting.config['widgets']['layout']['enabled'] = True

        # check if a layout is defined
        _layout = self.config['general'].get('layout', None)

        # initialize layout
        layout = None

        # if layout is a sting and appears as a node attribute
        if isinstance(_layout, str) and _layout in nodes.columns:
            layout = dict(zip(nodes['uid'], nodes[_layout]))
        # if layout is a dictionary of nodes and coordinates
        elif isinstance(_layout, dict):
            # TODO: check if the dictionary is correct
            layout = _layout

        # TODO :FIX euclidean assignment
        # if an layout is defined add it
        if layout is not None:
            log.debug('NOTE: Layout is assigned with Euclidean coordinates')
            nodes['euclidean'] = nodes['uid'].map(layout)

        # add data to painting
        painting.data['nodes'] = [_clean_dict(n, keep=self.d3js_kwds)
                                  for n in nodes.to_dict(orient='records')]

        painting.data['links'] = [_clean_dict(e, keep=self.d3js_kwds)
                                  for e in edges.to_dict(orient='records')]

        return painting

    @draw.register(BaseTemporalNetwork)
    def _draw_temporal(self, network, **kwargs):
        log.debug('I\'m a temporal d3js-network')

        # get data and config from the original network
        data, config = self.parse(network, **kwargs)

        # create new painting
        painting = Painting()

        # load base config and add it to the painting
        painting.config.update(self._load_base_config())

        # get data in a nicer format
        nodes = data['nodes']
        changes = data['changes']
        edges = data['edges']

        # print(changes)
        # print(nodes)
        # update config
        for key in self.d3js_args:
            if key in config['general']:
                painting.config[key] = config['general'][key]

        painting.config['animation'] = config['animation']

        # check for grouped nodes
        groups = self._check_groups(nodes).union(self._check_groups(changes))
        if groups:
            painting.config['widgets']['filter']['enabled'] = True
            painting.config['widgets']['filter']['groups'].extend(list(groups))

        # check for coordinates
        if 'euclidean' in nodes.columns:
            painting.config['widgets']['layout']['enabled'] = True
            painting.config['euclidean'] = True
            painting.config['coordinates'] = True

        # add data to painting
        painting.data['nodes'] = [_clean_dict(n, keep=self.d3js_kwds)
                                  for n in nodes.to_dict(orient='records')]

        painting.data['changes'] = [_clean_dict(c, keep=self.d3js_kwds)
                                    for c in changes.to_dict(orient='records')]

        painting.data['links'] = [_clean_dict(e, keep=self.d3js_kwds)
                                  for e in edges.to_dict(orient='records')]

        # print(painting.config)
        return painting

    def _check_groups(self, df):
        groups = set()
        if 'group' in df.columns:
            groups = set(df
                         .groupby('group')
                         .groups.keys())
        return groups

    def _load_base_config(self):

        # get path to the pathpy directory
        _base_config = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            os.path.normpath('visualizations/network/config.json'))

        # load basic json config for d3js
        with open(_base_config) as json_file:
            _config = json.load(json_file)

        return _config


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
