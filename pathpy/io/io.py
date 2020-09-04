#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : io.py -- Module for data import/export
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Fri 2020-09-04 16:11 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Union

import pandas as pd  # pylint: disable=import-error

from pathpy import config, logger

from pathpy.core.node import Node
from pathpy.core.edge import Edge
from pathpy.core.network import Network

# pseudo load class for type checking
if TYPE_CHECKING:
    from pathpy.models.temporal_network import TemporalNetwork


# create logger
LOG = logger(__name__)


def _check_column_name(frame: pd.DataFrame, name: str,
                       synonyms: list) -> pd.DataFrame:
    """Helper function to check column names and change them if needed."""
    if name not in frame.columns:
        LOG.info('No column %s, searching for synonyms', name)
        for col in frame.columns:
            if col in synonyms:
                LOG.info('Remapping column "%s" to "%s"', col, name)
                frame.rename(columns={col: name}, inplace=True)
                continue

    return frame


def to_network(frame: pd.DataFrame, loops: bool = True, directed: bool = True,
               multiedges: bool = False, **kwargs: Any) -> Network:
    """Read network from a pandas data frame."""

    # if no v/w columns are included, pick first synonym
    frame = _check_column_name(frame, 'v', config['edge']['v_synonyms'])
    frame = _check_column_name(frame, 'w', config['edge']['w_synonyms'])

    LOG.debug('Creating %s network', directed)

    node_set = set(frame['v']).union(set(frame['w']))

    if None in node_set:
        LOG.error('DataFrame minimally needs columns \'v\' and \'w\'')
        raise IOError

    nodes = {n: Node(n) for n in node_set}

    edges: list = []
    edge_set: set = set()

    # TODO: Make this for loop faster!
    for row in frame.to_dict(orient='records'):
        v = row.pop('v')
        w = row.pop('w')
        uid = row.pop('uid', None)

        if (v, w) in edge_set and not multiedges:
            LOG.warning('The edge (%s,%s) exist already '
                        'and will not be considered. '
                        'To capture this edge, please '
                        'enalbe multiedges and/or directed!', v, w)
        elif loops or v != w:
            edges.append(Edge(nodes[v], nodes[w], uid=uid, **row))
            edge_set.add((v, w))
            if not directed:
                edge_set.add((w, v))
        else:
            continue

    net = Network(directed=directed, multiedges=multiedges, **kwargs)
    for node in nodes.values():
        net.nodes.add(node)

    for edge in edges:
        net.edges._add(edge)

    net._add_edge_properties()
    return net


def to_temporal_network(frame: pd.DataFrame, loops: bool = True,
                        directed: bool = True, multiedges: bool = False,
                        **kwargs: Any) -> TemporalNetwork:
    """Read temporal network from a pandas data frame."""

    from pathpy.models.temporal_network import TemporalNetwork

    # if no v/w columns are included, pick first synonym
    frame = _check_column_name(frame, 'v', config['edge']['v_synonyms'])
    frame = _check_column_name(frame, 'w', config['edge']['w_synonyms'])

    _begin = config['temporal']['begin']
    _end = config['temporal']['end']
    _timestamp = config['temporal']['timestamp']
    _duration = config['temporal']['duration']

    _key_words = {'begin': _begin, 'end': _end,
                  'timestamp': _timestamp, 'duration': _duration}

    for key, name in _key_words.items():
        frame = _check_column_name(
            frame, name, config['temporal'][key+'_synonyms'])

    if _timestamp in frame.columns:
        frame[_begin] = frame[_timestamp]
        if _duration in frame.columns:
            frame[_end] = frame[_timestamp] + frame[_duration]
        else:
            frame[_end] = frame[_timestamp] + \
                config['temporal']['duration_value']

    if _begin and _end not in frame.columns:
        LOG.error('A TemporalNetwork needs "%s" and "%s" (or "%s" and "%s") '
                  'attributes!', _begin, _end, _timestamp, _duration)
        raise IOError

    LOG.debug('Creating %s network', directed)

    node_set = set(frame['v']).union(set(frame['w']))

    if None in node_set:
        LOG.error('DataFrame minimally needs columns \'v\' and \'w\'')
        raise IOError

    nodes = {n: Node(n) for n in node_set}

    net = TemporalNetwork(directed=directed, multiedges=multiedges, **kwargs)
    for node in nodes.values():
        net.nodes.add(node)

    # TODO: Make this for loop faster!
    rows = []
    edges = {}
    for row in frame.to_dict(orient='records'):
        v = row.pop('v')
        w = row.pop('w')
        uid = row.pop('uid', None)
        if (v, w) not in edges:
            edge = Edge(nodes[v], nodes[w], uid=uid, **row)
            net.edges._add(edge)
            edges[(v, w)] = edge
        else:
            begin = row.pop(_begin)
            end = row.pop(_end)
            net.edges._intervals.addi(begin, end, edges[(v, w)])
            net.edges._interval_map[edges[(v, w)]].add((begin, end))

    # net.add_edge(nodes[v], nodes[w], uid=uid, **row)
    net._add_edge_properties()
    return net


def from_network(network: Network, exclude_edge_uid: bool = False,
                 export_indices: bool = False) -> pd.DataFrame:
    """Returns a pandas dataframe of the network.

    Returns a pandas dataframe data that contains all edges including all edge
    attributes. Node and network-level attributes are not included.

    """
    frame = pd.DataFrame()

    for edge in network.edges:
        v = edge.v.uid
        w = edge.w.uid
        if export_indices:
            v = network.nodes.index[v]
            w = network.nodes.index[w]
        if exclude_edge_uid:
            edge_frame = pd.DataFrame(columns=['v', 'w'])
            edge_frame.loc[0] = [v, w]
        else:
            edge_frame = pd.DataFrame(columns=['v', 'w', 'uid'])
            edge_frame.loc[0] = [v, w, edge.uid]
        edge_frame = pd.concat([edge_frame, edge.attributes.to_frame()], axis=1)
        frame = pd.concat([edge_frame, frame], ignore_index=True, sort=False)
    return frame


def from_temporal_network(network: TemporalNetwork,
                          exclude_edge_uid: bool = False,
                          export_indices: bool = False) -> pd.DataFrame:
    """Returns a pandas dataframe of the temporal network.

    Returns a pandas dataframe data that contains all edges including all edge
    attributes. Node and network-level attributes are not included.

    """
    frame = pd.DataFrame()

    for uid, edge, begin, end in network.edges.temporal():
        v = edge.v.uid
        w = edge.w.uid
        if export_indices:
            v = network.nodes.index[v]
            w = network.nodes.index[w]
        if exclude_edge_uid:
            edge_frame = pd.DataFrame(columns=['v', 'w', 'begin', 'end'])
            edge_frame.loc[0] = [v, w, begin, end]
        else:
            edge_frame = pd.DataFrame(columns=['v', 'w', 'uid', 'begin', 'end'])
            edge_frame.loc[0] = [v, w, uid, begin, end]
        edge_frame = pd.concat([edge_frame, edge.attributes.to_frame()], axis=1)
        frame = pd.concat([edge_frame, frame], ignore_index=True)
    return frame


def to_dataframe(network: Union[Network, TemporalNetwork],
                 exclude_edge_uid: bool = False,
                 export_indices: bool = False) -> pd.DataFrame:
    """Stores all edges including edge attributes in a csv file."""

    if isinstance(network, Network):
        frame = from_network(network, exclude_edge_uid=exclude_edge_uid,
                             export_indices=export_indices)
    elif isinstance(network, TemporalNetwork):
        frame = from_temporal_network(network,
                                      exclude_edge_uid=exclude_edge_uid,
                                      export_indices=export_indices)
    else:
        raise NotImplementedError

    return frame

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
