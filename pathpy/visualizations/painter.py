#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : painter.py --
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Fri 2020-02-28 12:15 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================

from typing import Any
import pandas as pd
import numpy as np
from collections import defaultdict
# from functools import singledispatchmethod
from singledispatchmethod import singledispatchmethod
from .. import logger
from ..core.base import BaseStaticNetwork, BaseTemporalNetwork, BaseHigherOrderNetwork


log = logger(__name__)


class Painting:
    def __init__(self):
        self.data = {}
        self.config = {}


# {"nodes":
#  {
#      "uid": "a",
#      "size": 3,
#      "color": "#97b330",
#      "opacity": 1,
#      "label": "Diamonds On The Soles Of Her Shoes",
#      "text": "Paul Simon",
#      "group": "A",
#      "coordinates": (1, 2),
#      "label_position": 'top',
#      "label_distance": 2,
#      "label_color": "red",
#      "label_size": "large",
#      "shape": "circle",
#      "style": None,
#      "layer": 2,
#      "label_off": False,
#      "label_as_id": False,
#      "math_mode": False,
#      "pseudo": False,
#      "time": 20,
#  },
#  }

# {"edges":
#  {
#      "uid": "a",
#      "width": 3,
#      "color": "#97b330",
#      "opacity": 1,
#      "label": "Diamonds On The Soles Of Her Shoes",
#      "label_position": 'top',
#      "label_distance": 2,
#      "label_color": "red",
#      "label_size": "large",
#      "text": "Paul Simon",
#      "shape": "circle",
#      "style": None,
#      "arrow_size": 3,
#      "arrow_width": 3,
#      "loop_size": "xxx",
#      "loop_position": "xxx",
#      "loop_shape": "ddd",
#      "directed": False,
#      "math_mode": False,
#      "edge_not_in_bg": False,
#      "time": 20,
#      "source":"a",
#      "Target":"b",
#  },
#  }


class PaintConfig(defaultdict):
    def __init__(self, *args, **kwargs: Any) -> None:
        """Initialize the BaseDict object."""

        # initialize the base class
        super().__init__(dict)

        # base structure {key:name}
        self.structure = {'node_': 'nodes',
                          'edge_': 'edges', 'general_': 'general'}

        # initialize base structure
        for name in self.structure.values():
            self[name] = {}

        self.initialize(**kwargs)

        if args:
            for i, category in enumerate(list(self.structure.values())):
                self[category]['uids'] = args[i]
                if i+1 == len(args):
                    break
            self.expand()
        self.to_dict('nodes')

    def initialize(self, **kwargs):
        # rename keys of the kwargs
        kwargs = self.rename_kwargs(**kwargs)

        # assign dict to the sub-categories
        for indicator, category in self.structure.items():
            for key, value in kwargs.items():
                if indicator in key:
                    self[category][key.replace(indicator, '')] = value

        # add all other entries to the general dict
        for key, value in kwargs.items():
            _add = True
            for indicator, category in self.structure.items():
                if indicator in key:
                    _add = False
            if _add:
                self['general'][key] = value

    def expand(self):
        # assign dict to the sub-categories
        for category in self.structure.values():
            uids = self[category].get('uids', None)
            attributes = list(self[category])
            if uids is not None:
                attributes.remove('uids')
                for key in attributes:
                    self[category][key] = self.expand_value(
                        uids, self[category][key])

    def expand_value(self, uids, value):
        """Returns a dict with edge ids and assigned values."""
        # check if value is string, list or dict
        _values = {}
        if isinstance(value, str) or isinstance(value, int) or \
           isinstance(value, float) or isinstance(value, bool) \
           or isinstance(value, tuple):
            for k in uids:
                _values[k] = value
        elif isinstance(value, list):
            for i, k in enumerate(uids):
                try:
                    _values[k] = value[i]
                except:
                    _values[k] = None
        elif isinstance(value, dict):
            for k in uids:
                try:
                    _values[k] = value[k]
                except:
                    _values[k] = None
        else:
            log.error('Something went wrong, by formatting the values!')
            raise ValueError
        return _values

    def to_dict(self, category):
        _dict = defaultdict(dict)
        uids = self[category].get('uids', None)
        attributes = list(self[category])
        if uids is not None:
            attributes.remove('uids')
            for uid in uids:
                for key in attributes:
                    _dict[uid][key] = self[category][key][uid]

        return _dict

    def to_frame(self, category):
        _dict = self.to_dict(category)
        frame = pd.DataFrame.from_dict(_dict, orient='index')
        frame['uid'] = frame.index
        return frame

    @staticmethod
    def rename_kwargs(**kwargs):
        """Rename node and edge attributes.

        In the style dictionary multiple keywords can be used to address
        attributes. These keywords will be converted to an unique key word,
        used in the remaining code. This allows to keep the keywords used in
        'igrap'.

        ========= ===========================
        keys      other valid keys
        ========= ===========================
        node      vertex, v, n
        edge      link, l, e
        margins   margin
        canvas    bbox, figure_size
        units     unit
        ========= ===========================

        """
        names = {'node_': ['vertex_', 'v_', 'n_'],
                 'edge_': ['edge_', 'link_', 'l_', 'e_'],
                 'margins': ['margin'],
                 'canvas': ['bbox', 'figure_size'],
                 'units': ['units', 'unit'],
                 'group': ['group', 'groups'],
                 }
        _kwargs = {}
        del_keys = []
        for key, value in kwargs.items():
            for attr, name_list in names.items():
                for name in name_list:
                    if name in key and name[0] == key[0]:
                        _kwargs[key.replace(name, attr)] = value
                        del_keys.append(key)
                        break
        # remove the replaced keys from the dict
        for key in del_keys:
            del kwargs[key]

        return {**_kwargs, **kwargs}


class Painter:

    def __init__(self):

        self.coordinates = {'x': 'euclidean',
                            'y': 'euclidean',
                            'euclidean': ('x', 'y'),
                            'lat': 'utm',
                            'lon': 'utm',
                            'utm': ('lat', 'log'),
                            }

    @singledispatchmethod
    def parse(self, network, **kwargs):
        """Parses the pathpy network into a json like dict."""
        raise NotImplementedError

    @parse.register(BaseStaticNetwork)
    @parse.register(BaseHigherOrderNetwork)
    def _parse_static(self, network, **kwargs):
        log.debug('I\'m a static network')

        # initialize base config
        self.config = PaintConfig(list(network.nodes),
                                  list(network.edges),
                                  **kwargs)

        # update config
        self.config['general']['temporal'] = False
        self.config['general']['directed'] = network.directed

        # initialize data container
        data = {}

        # assigne objects to data dict
        data['nodes'] = self.convert_nodes(network.nodes.to_frame())
        data['edges'] = self.convert_edges(network.edges.to_frame())

        return data, self.config

    def convert_edges(self, edges):

        # convert edges
        edges = (edges
                 .rename(columns={'v': 'source', 'w': 'target'})
                 .replace({np.nan: None}))

        # rename columns if requested
        if self.config['general'].get('mapping', None) is not None:
            edges = edges.rename(columns=self.config['general']['mapping'])

        # get attributes from the config
        _edges = self.config.to_frame('edges')

        # update attributes
        overwrite = self.config['general'].get('overwrite', None)
        if not _edges.empty:
            edges = self.update_frame(edges, _edges, overwrite)

        # return the edges
        return edges

    def convert_nodes(self, nodes):

        # convert nodes
        nodes = (nodes
                 .replace({np.nan: None}))

        # check if coordinates key words are given and clean them
        if any([col in self.coordinates for col in list(nodes)]):
            nodes = self.convert_coordinates(nodes)

        # rename columns if requested
        if self.config['general'].get('mapping', None) is not None:
            nodes = nodes.rename(columns=self.config['general']['mapping'])

        # get attributes from the config
        _nodes = self.config.to_frame('nodes')

        # update attributes
        overwrite = self.config['general'].get('overwrite', None)
        if not _nodes.empty:
            nodes = self.update_frame(nodes, _nodes, overwrite)

        # return the nodes
        return nodes

    def update_frame(self, old, new, overwrite=None):

        for column in new.columns:
            if column not in old:
                old[column] = old['uid'].map(new[column])
            else:
                if overwrite is None:
                    old[column] = old[column].fillna(
                        old['uid'].map(new[column]))
                elif overwrite:
                    old[column] = old['uid'].map(new[column])

        return old

    @parse.register(BaseTemporalNetwork)
    def _parse_temporal(self, network, **kwargs):
        log.debug('I\'m a temporal network')

        # get uids for the nodes and edges
        nodes = list(network.nodes)
        edges = list(network.edges)

        # initialize base config
        self.config = PaintConfig(nodes, edges, **kwargs)

        # initialize data container
        data = {}

        frequency = self.config['general'].get('frequency', 's')

        # case 1: both are temporal
        if network.edges.temporal and network.nodes.temporal:
            log.debug('Temporal edges and nodes observed')

            nodes = network.nodes.to_temporal_frame(frequency=frequency)

            # get start and endtime as well as the time range
            start = nodes['time'].min()
            end = nodes['time'].max()
            index = (pd.date_range(
                start=start, end=end, freq=frequency, name='time')
                .to_frame(index=False)
                .reset_index())

            nodes['time'] = nodes['time'].map(index.set_index('time')['index'])

            _nodes = (nodes[['uid', 'active']]
                      .groupby('uid')
                      .first()
                      .reset_index())

            _nodes = self.convert_nodes(_nodes).set_index('uid')

            # update attributes
            overwrite = self.config['general'].get('overwrite', None)
            nodes = (self.update_frame(nodes, _nodes, overwrite)
                     .replace({np.nan: None})
                     .drop(['active'], axis=1))

            data['changes'] = nodes

            data['nodes'] = (nodes
                             .groupby('uid')
                             .first()
                             .reset_index())

            edges = network.edges.to_temporal_frame(frequency=frequency)

            edges['time'] = edges['time'].map(index.set_index('time')['index'])

            _edges = (edges[['uid', 'v', 'w']]
                      .groupby('uid')
                      .first()
                      .reset_index())

            _edges = self.convert_edges(_edges).set_index('uid')

            # update attributes
            overwrite = self.config['general'].get('overwrite', None)
            edges = (self.update_frame(edges, _edges, overwrite)
                     .replace({np.nan: None})
                     .drop(['v', 'w', 'active'], axis=1))

            data['edges'] = edges

        elif network.edges.temporal:
            log.debug('Only temporal edges observed')

            data['nodes'] = self.convert_nodes(network.nodes.to_frame())
            data['changes'] = pd.DataFrame()

            edges = network.edges.to_temporal_frame(frequency=frequency)

            # get start and endtime as well as the time range
            start = edges['time'].min()
            end = edges['time'].max()
            index = (pd.date_range(
                start=start, end=end, freq=frequency, name='time')
                .to_frame(index=False)
                .reset_index())

            edges['time'] = edges['time'].map(index.set_index('time')['index'])

            _edges = (edges[['uid', 'v', 'w']]
                      .groupby('uid')
                      .first()
                      .reset_index())

            _edges = self.convert_edges(_edges).set_index('uid')

            # update attributes
            overwrite = self.config['general'].get('overwrite', None)
            edges = (self.update_frame(edges, _edges, overwrite)
                     .replace({np.nan: None})
                     .drop(['v', 'w', 'active'], axis=1))

            data['edges'] = edges

        elif network.nodes.temporal:
            log.debug('Only temporal nodes observed')

            nodes = network.nodes.to_temporal_frame(frequency=frequency)

            # get start and endtime as well as the time range
            start = nodes['time'].min()
            end = nodes['time'].max()
            index = (pd.date_range(
                start=start, end=end, freq=frequency, name='time')
                .to_frame(index=False)
                .reset_index())

            nodes['time'] = nodes['time'].map(index.set_index('time')['index'])

            _nodes = (nodes[['uid', 'active']]
                      .groupby('uid')
                      .first()
                      .reset_index())

            _nodes = self.convert_nodes(_nodes).set_index('uid')

            # update attributes
            overwrite = self.config['general'].get('overwrite', None)
            nodes = (self.update_frame(nodes, _nodes, overwrite)
                     .replace({np.nan: None})
                     .drop(['active'], axis=1))

            data['changes'] = nodes

            data['nodes'] = (nodes
                             .groupby('uid')
                             .first()
                             .reset_index())

            # TODO fix edges
            edges = self.convert_edges(network.edges.to_frame())
            edges['time'] = 0
            data['edges'] = edges

        # update config
        self.config['general']['temporal'] = True
        self.config['general']['directed'] = network.directed
        self.config['animation']['start'] = start.strftime('%Y-%m-%dT%H:%M:%SZ')
        self.config['animation']['end'] = end.strftime('%Y-%m-%dT%H:%M:%SZ')
        self.config['animation']['enabled'] = True
        self.config['animation']['steps'] = len(index)-1
        self.config['animation']['unit'] = 'seconds'

        return data, self.config

    def convert_coordinates(self, nodes):
        # get the observed key workd

        # update config
        self.config['general']['coordinates'] = True

        coordinates = {v for k, v in self.coordinates.items()
                       if k in list(nodes)}

        for v in coordinates:
            if isinstance(v, str):
                # update config
                self.config['general'][v] = True
                # get the column captions
                a = self.coordinates[v][0]
                b = self.coordinates[v][1]
                # check if columns exist otherwise add new with None values
                if a not in nodes.columns:
                    nodes[a] = None
                if b not in nodes.columns:
                    nodes[b] = None
                # add new column with the coordinates
                nodes[v] = list(zip(nodes[a], nodes[b]))
            elif isinstance(v, tuple):
                # update config
                self.config['general'][self.coordinates[v[0]]] = True
                pass
        return nodes


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
