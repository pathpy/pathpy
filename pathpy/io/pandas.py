"""Functions to read and write network and path data to/from pandas data frames"""
#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : io.py -- Module for data import/export
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Fri 2021-06-04 18:02 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, Union, Optional
from collections import Counter

import pandas as pd  # pylint: disable=import-error

from pathpy import config, logger
from pathpy.core.core import PathPyRelation
from pathpy.core.api import Node
from pathpy.core.api import Edge
from pathpy.models.api import Network, TemporalNetwork

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


def to_network(df: pd.DataFrame, loops: bool = True, directed: bool = True,
               multiedges: bool = False, **kwargs: Any) -> Network:
    """Reads a network from a pandas data frame.

    The data frame is expected to have a minimum of two columns `v` and `w`
    that give the source and target nodes of edges. Additional column names to
    be used can be configured in `config.cfg` as `v_synonyms` and `w` synonyms.
    Each row in the data frame is mapped to one edge. Additional columns in the
    data frame will be mapped to edge attributes.

    Parameters
    ----------

    df: pandas.DataFrame

        A data frame with rows containing edges and optional edge attributes.

    loops: Optional[bool]=True

        Whether or not to add self-loops, i.e. rows in the data frame where
        columns `v` and `w` (or configured synonyms) are identical. Default is
        True.

    directed: Optional[bool]=True

        Whether or not to add edges as directed edges.

    multiedges: Optional[bool]=False

        Whether or not to allow multiple edges between the same node pair. By
        default multi edges are ignored.

    **kwargs: Any

        Arbitrary keyword arguments that will be set as network-level
        attributes.

    Returns
    -------
    Network

        a static network object


    Examples
    --------

    Create simple data frame and convert into network

    >>> import pathpy as pp
    >>> import pandas as pd
    >>> df = pd.DataFrame({
    ...     'v': ['a', 'b', 'c'],
    ...     'w': ['b', 'c', 'a'],
    ...     'color': ['red', 'green', 'blue']})
    >>> n = pp.io.to_network(df, uid='pandasNetwork')
    >>> print(n)
    Uid:			pandasNetwork
    Type:			Network
    Directed:		True
    Multi-Edges:		False
    Number of nodes:	3
    Number of edges:	3

    """

    # if no v/w columns are included, pick first synonym
    df = _check_column_name(df, 'v', config['edge']['v_synonyms'])
    df = _check_column_name(df, 'w', config['edge']['w_synonyms'])

    LOG.debug('Creating %s network', directed)

    # create a set of all node uids
    node_set: set = set(df['v']).union(set(df['w']))

    if None in node_set:
        LOG.error('DataFrame minimally needs columns \'v\' and \'w\'')
        raise IOError

    # create dict with node.uid and node
    nodes: dict = {n: Node(n) for n in node_set}

    # initialize variables
    edges: list = []
    edge_set: set = set()

    # counter for multiple edges
    counter: Counter = Counter()

    # TODO: Make this for loop faster!
    for row in df.to_dict(orient='records'):
        # get node and edge  uids
        _v, _w = row.pop('v'), row.pop('w')
        uid = row.pop('uid', None)

        # check if edge was already generated
        if (_v, _w) in edge_set and not multiedges:
            counter[(_v, _w)] += 1

        elif loops or _v != _w:
            # generate edge object
            edges.append(Edge(nodes[_v], nodes[_w],
                              uid=uid, directed=directed, **row))
            edge_set.add((_v, _w))
            if not directed:
                edge_set.add((_w, _v))
        else:
            continue

    # check if multiple versions of the edges are given
    if len(counter) > 0:
        LOG.warning('%i edges existed already '
                    'and were not be considered. '
                    'To capture those edges, consider creating '
                    'a multiedge and/or directed network.', sum(counter.values()))

    # create network
    net = Network(directed=directed, multiedges=multiedges, **kwargs)
    net.add_edges(edges)

    # update counter
    for key, value in counter.items():
        net.edges.counter[key] += value

    return net


def to_temporal_network(df: pd.DataFrame, loops: bool = True,
                        directed: bool = True, multiedges: bool = False,
                        **kwargs: Any) -> TemporalNetwork:
    """Reads a temporal network from a pandas data frame.

    The data frame is expected to have a minimum of two columns `v` and `w`
    that give the source and target nodes of edges. Additional column names to
    be used can be configured in `config.cfg` as `v_synonyms` and `w`
    synonyms. The time information on edges can either be stored in an
    additional `timestamp` column (for instantaneous interactions) or in two
    columns `start`, `end` or `timestamp`, `duration` respectively for networks
    where edges appear and exist for a certain time. Synonyms for those column
    names can be configured in config.cfg.  Each row in the data frame is
    mapped to one temporal edge. Additional columns in the data frame will be
    mapped to edge attributes.

    Parameters
    ----------

    df: pandas.DataFrame

        A data frame with rows containing time-stamped edges and optional edge
        attributes.

    loops: Optional[bool]=True

        Whether or not to ignore self-loops, i.e. rows in the data frame where
        columns `v` and `w` (or configured synonyms) are identical. Default is
        False.

    directed: Optional[bool]=True

        Whether or not to add temporal edges as directed edges.

    multiedges: Optional[bool]=False

        Whether or not to allow multiple edges between the same node pair. By
        default multi-edges are ignored.

    **kwargs: Any

        Arbitrary keyword arguments that will be set as network-level
        attributes.

    Returns
    -------
    TemporalNetwork

        a temporal network object


    Examples
    --------

    Create data frame with instantaneous time stamps and read it as temporal
    networks

    >>> import pathpy as pp
    >>> import pandas as pd
    >>> df = pd.DataFrame({
    ...         'v': ['a', 'b', 'c'],
    ...         'w': ['b', 'c', 'a'],
    ...         'timestamp': [1, 2, 3]})
    >>> tn = pp.io.to_network(df, uid='pandasNetwork')
    >>> print(tn)
    Uid:			pandasNetwork
    Type:			TemporalNetwork
    Directed:		True
    Multi-Edges:		False
    Number of unique nodes:	3
    Number of unique edges:	3
    Number of temp nodes:	3
    Number of temp edges:	3
    Observation period: 	1 - 4

    Create data frame with temporal edges that have a start and end time

    >>> import pathpy as pp
    >>> import pandas as pd
    >>> df = pd.DataFrame({
    ...         'v': ['a', 'b', 'c'],
    ...         'w': ['b', 'c', 'a'],
    ...         'start': [1, 2, 3]
    ...         'end': [5, 5, 5 ]})
    >>> tn = pp.io.to_network(df, uid='pandasNetwork')
    >>> print(tn)
    Uid:			pandasNetwork
    Type:			TemporalNetwork
    Directed:		True
    Multi-Edges:		False
    Number of unique nodes:	3
    Number of unique edges:	3
    Number of temp nodes:	3
    Number of temp edges:	3
    Observation period: 	1 - 5

    Create data frame with temporal edges that have a timestamp and duration

    >>> import pathpy as pp
    >>> import pandas as pd
    >>> df = pd.DataFrame({
    ...         'v': ['a', 'b', 'c'],
    ...         'w': ['b', 'c', 'a'],
    ...         'timestamp': [1, 2, 3]
    ...         'duration': [4, 1, 1 ]})
    >>> tn = pp.io.to_network(df, uid='pandasNetwork')
    >>> print(tn)
    Uid:			pandasNetwork
    Type:			TemporalNetwork
    Directed:		True
    Multi-Edges:		False
    Number of unique nodes:	3
    Number of unique edges:	3
    Number of temp nodes:	3
    Number of temp edges:	3
    Observation period: 	1 - 5

    """

    from pathpy.models.temporal_network import TemporalNetwork, TemporalEdge, TemporalNode

    # if no v/w columns are included, pick first synonym
    df = _check_column_name(df, 'v', config['edge']['v_synonyms'])
    df = _check_column_name(df, 'w', config['edge']['w_synonyms'])

    # get keyword for temporal objects
    _start = config['temporal']['start']
    _end = config['temporal']['end']
    _timestamp = config['temporal']['timestamp']
    _duration = config['temporal']['duration']

    _key_words = {'start': _start, 'end': _end,
                  'timestamp': _timestamp, 'duration': _duration}

    # changes column names
    for key, name in _key_words.items():
        df = _check_column_name(
            df, name, config['temporal'][key+'_synonyms'])

    LOG.debug('Creating %s network', directed)

    node_set = set(df['v']).union(set(df['w']))

    if None in node_set:
        LOG.error('DataFrame minimally needs columns \'v\' and \'w\'')
        raise IOError

    # create dict with node.uid and node
    nodes: dict = {str(n): TemporalNode(str(n)) for n in node_set}

    # create empty network
    net = TemporalNetwork(directed=directed, multiedges=multiedges, **kwargs)

    # TODO: Make this for loop faster!
    for row in df.to_dict(orient='records'):
        # get node and edge  uids
        _v, _w = str(row.pop('v')), str(row.pop('w'))
        uid = row.pop('uid', None)
        net.add_edge(nodes[_v], nodes[_w], uid=uid,
                     update_properties=False, **row)

    net._add_edge_properties()

    return net


def from_network(network: Network, include_edge_uid: Optional[bool] = False,
                 export_indices: Optional[bool] = False) -> pd.DataFrame:
    """Returns a pandas dataframe of the network.

    Returns a pandas dataframe data that contains all edges including all edge
    attributes. Node and network-level attributes are not included. To
    facilitate the import into network analysis tools that only support integer
    node identifiers, node uids can be replaced by a consecutive, zero-based
    index.

    Parameters
    ----------

    network: Network

        The (static) network to export as pandas DataFrame

    include_edge_uids: Optional[bool]=False

        Whether or not to include a column that stores the uids of the edge
        objects

    export_indices: Optional[bool]=False

        Whether or not to use node indices rather than node uids. This is useful to
        import network data in tools that only support integer node identifiers.

    Returns
    -------

    pandas.DataFrame

        pandas DataFrame containing the edges of the network

    Examples
    --------

    Export static network with edge attributes and node uids

    >>> n = pp.Network(directed=True)
    >>> n.add_edge('a', 'b', color='red')
    >>> n.add_edge('b', 'c', color='green')
    >>> n.add_edge('c', 'a', color='blue')
    >>> df = pp.io.to_dataframe(n)
    >>> print(df)
        v  w  color
    0   c  a   blue
    1   b  c  green
    2   a  b    red

    Export static network with edge attributes, edge uids and node indices

    >>> n = pp.Network(directed=True)
    >>> n.add_edge('a', 'b', color='red')
    >>> n.add_edge('b', 'c', color='green')
    >>> n.add_edge('c', 'a', color='blue')
    >>> df = pp.io.to_dataframe(n, export_indices=True, include_edge_uid=True)
    >>> print(df)
       v  w            uid  color
    0  2  0  0x2cf75244630   blue
    1  1  2  0x2cf75244a20  green
    2  0  1  0x2cf752449e8    red

    """
    df = pd.DataFrame()

    for edge in network.edges:
        v = edge.v.uid
        w = edge.w.uid
        if export_indices:
            v = network.nodes.index[v]
            w = network.nodes.index[w]
        if include_edge_uid:
            edge_frame = pd.DataFrame.from_dict(
                {'v': [v], 'w': [w], 'uid': [edge.uid]})
        else:
            edge_frame = pd.DataFrame.from_dict({'v': [v], 'w': [w]})
        data = pd.DataFrame.from_dict(
            {k: [v] for k, v in edge.attributes.items()})
        edge_frame = pd.concat([edge_frame, data], axis=1)
        df = pd.concat([edge_frame, df], ignore_index=True, sort=False)
    return df


def from_temporal_network(network: TemporalNetwork,
                          include_edge_uid: bool = False,
                          export_indices: bool = False) -> pd.DataFrame:
    """Returns a pandas dataframe of the temporal network.

    Returns a pandas dataframe data that contains all edges including all edge
    attributes. Node and network-level attributes are not included. To facilitate the
    import into network analysis tools that only support integer node identifiers,
    node uids can be replaced by a consecutive, zero-based index.

    Parameters
    ----------

    network: Network

        The (static) network to export as pandas DataFrame

    include_edge_uids: Optional[bool]=False

        Whether or not to include a column that stores the uids of the edge objects

    export_indices: Optional[bool]=False

        Whether or not to use node indices rather than node uids. This is useful to
        import network data in tools that only support integer node identifiers.

    Returns
    -------

    pandas.DataFrame

        pandas DataFrame containing the edges of the network

    Examples
    --------

    Export static network with edge attributes and node uids

    >>> n = pp.Network(directed=True)
    >>> n.add_edge('a', 'b', color='red')
    >>> n.add_edge('b', 'c', color='green')
    >>> n.add_edge('c', 'a', color='blue')
    >>> df = pp.io.to_dataframe(n)
    >>> print(df)
        v  w  color
    0   c  a   blue
    1   b  c  green
    2   a  b    red

    Export static network with edge attributes, edge uids and node indices

    >>> n = pp.Network(directed=True)
    >>> n.add_edge('a', 'b', color='red')
    >>> n.add_edge('b', 'c', color='green')
    >>> n.add_edge('c', 'a', color='blue')
    >>> df = pp.io.to_dataframe(n, export_indices=True, include_edge_uid=True)
    >>> print(df)
       v  w            uid  color
    0  2  0  0x2cf75244630   blue
    1  1  2  0x2cf75244a20  green
    2  0  1  0x2cf752449e8    red
    """
    frame = pd.DataFrame()

    for edge in network.edges[:]:
        v = edge.v.uid
        w = edge.w.uid
        if export_indices:
            v = network.nodes.index[v]
            w = network.nodes.index[w]
        if include_edge_uid:
            edge_frame = pd.DataFrame.from_dict(
                {'v': [v], 'w': [w], 'uid': [edge.uid]})
        else:
            edge_frame = pd.DataFrame.from_dict({'v': [v], 'w': [w]})
        data = pd.DataFrame.from_dict(
            {k: [v] for k, v in edge.attributes.items()})
        edge_frame = pd.concat([edge_frame, data], axis=1)
        frame = pd.concat([edge_frame, frame], ignore_index=True)
    return frame


def to_dataframe(network: Union[Network, TemporalNetwork],
                 include_edge_uid: bool = False,
                 export_indices: bool = False) -> pd.DataFrame:
    """Returns a pandas dataframe of a static or temporal network.

    Returns a pandas dataframe data that contains all edges including all edge
    attributes. Node and network-level attributes are not included. To facilitate the
    import into network analysis tools that only support integer node identifiers,
    node uids can be replaced by a consecutive, zero-based index.

    Parameters
    ----------

    network: Network

        The (static) network to export as pandas DataFrame

    include_edge_uids: Optional[bool]=False

        Whether or not to include a column that stores the uids of the edge objects

    export_indices: Optional[bool]=False

        Whether or not to use node indices rather than node uids. This is useful to
        import network data in tools that only support integer node identifiers.

    Returns
    -------

    pandas.DataFrame

        pandas DataFrame containing the edges of the network

    Examples
    --------

    Export static network with edge attributes and node uids

    >>> n = pp.Network(directed=True)
    >>> n.add_edge('a', 'b', color='red')
    >>> n.add_edge('b', 'c', color='green')
    >>> n.add_edge('c', 'a', color='blue')
    >>> df = pp.io.to_dataframe(n)
    >>> print(df)
        v  w  color
    0   c  a   blue
    1   b  c  green
    2   a  b    red

    Export static network with edge attributes, edge uids and node indices

    >>> n = pp.Network(directed=True)
    >>> n.add_edge('a', 'b', color='red')
    >>> n.add_edge('b', 'c', color='green')
    >>> n.add_edge('c', 'a', color='blue')
    >>> df = pp.io.to_dataframe(n, export_indices=True, include_edge_uid=True)
    >>> print(df)
       v  w            uid  color
    0  2  0  0x2cf75244630   blue
    1  1  2  0x2cf75244a20  green
    2  0  1  0x2cf752449e8    red
    """

    if isinstance(network, TemporalNetwork):
        frame = from_temporal_network(network,
                                      include_edge_uid=include_edge_uid,
                                      export_indices=export_indices)
    elif isinstance(network, Network):
        frame = from_network(network, include_edge_uid=include_edge_uid,
                             export_indices=export_indices)
    else:
        raise NotImplementedError(
            'Export to data frame is only implemented for Network and TemporalNetwork')

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
