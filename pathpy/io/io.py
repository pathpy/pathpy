#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : io.py -- Module for data import/export
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Mon 2020-04-20 11:51 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, Optional, cast

import sqlite3
import pandas as pd  # pylint: disable=import-error

from pathpy import config, logger
from pathpy.core.edge import Edge
from pathpy.core.network import Network

# create logger
LOG = logger(__name__)


def from_csv(filename: str, directed: bool = True, sep: str = ',',
             header: bool = True, names: Optional[list] = None,
             **kwargs: Any) -> Network:
    """Read network from a csv file,"""

    if header:
        df = pd.read_csv(filename, sep=sep)
    else:
        df = pd.read_csv(filename, header=0, names=names, sep=sep)

    return from_dataframe(df, directed=directed, **kwargs)


def from_dataframe(df: pd.DataFrame, directed: bool = True,
                   **kwargs: Any) -> Network:
    """Reads a network from a pandas dataframe.

    By default, columns `v` and `w` will be used as source and target of
    edges. If no column 'v' or 'w' exists, the list of synonyms for `v` and
    `w`` in the config file will be used to remap columns, choosing the first
    matching entries. Any columns not used to create edges will be used as edge
    attributes, e.g. if a column 'v' is present and an additional column
    `source`is given, `source` will be assigned as an edge property.

    In addition, an optional column `uid` will be used to assign node uids. If
    this column is not present, default edge uids will be created.  Any other
    columns (e.g. weight, type, time, etc.) will be assigned as edge
    attributes. kwargs will be assigned as network attributes.

    Parameters
    ----------

    directed: bool

        Whether to generate a directed or undirected network.

    **kwargs: Any

        List of key-value pairs that will be assigned as network attributes

    Examples
    --------

    """

    # if no v/w columns are included, pick first synonym
    if 'v' not in df.columns:
        LOG.info('No column v, searching for synonyms')
        for col in df.columns:
            if col in config['edge']['v_synonyms']:
                LOG.info('Remapping column \'%s\' to \'v\'', col)
                df.rename(columns={col: "v"}, inplace=True)
                continue

    if 'w' not in df.columns:
        LOG.info('No column w, searching for synonyms')
        for col in df.columns:
            if col in config['edge']['w_synonyms']:
                LOG.info('Remapping column \'%s\' to \'w\'', col)
                df.rename(columns={col: "w"}, inplace=True)
                continue

            LOG.debug('Creating %s network', directed)

    net = Network(directed=directed, **kwargs)
    for row in df.to_dict(orient='records'):

        # get edge
        v = row.get('v', None)
        w = row.get('w', None)
        uid = row.get('uid', None)
        if v is None or w is None:
            LOG.error('DataFrame minimally needs columns \'v\' and \'w\'')
            raise IOError
        if v not in net.nodes.uids:
            net.add_node(v)
        if w not in net.nodes.uids:
            net.add_node(w)
        if uid is None:
            edge = Edge(net.nodes[v], net.nodes[w])
        else:
            edge = Edge(net.nodes[v], net.nodes[w], uid=uid)
        net.add_edge(edge)

        reserved_columns = set(['v', 'w', 'uid'])
        for k in row:
            if k not in reserved_columns:
                edge[k] = row[k]
    return net


def from_sqlite(filename: Optional[str] = None, directed: bool = True,
                con: Optional[sqlite3.Connection] = None,
                sql: Optional[str] = None, table: Optional[str] = None,
                **kwargs: Any) -> Network:
    """Read network from an sqlite database."""

    LOG.debug('Load sql file as pandas data frame.')

    if con is None and filename is None:
        LOG.error('Either an SQL connection or a filename is required')
        raise IOError

    con_close = False
    # connect to database if not given
    if con is None and filename is not None:
        con_close = True
        con = sqlite3.connect(filename)

    # if sql query is not given check availabe tables
    if sql is None:

        # create cursor and get all tables availabe
        cursor = cast(sqlite3.Connection, con).cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = list(sum(cursor.fetchall(), ()))

        # check if table is given
        if table is None:
            table = tables[0]
        elif table not in tables:
            LOG.error('Given table "%s" not in database!', table)
            raise IOError

        # generate sql query
        sql = 'SELECT * from {}'.format(table)

    # read to pandas data frame
    df = pd.read_sql(sql, con)

    # close connection to the database
    if con_close:
        _con = cast(sqlite3.Connection, con)
        _con.close()

    # construct network from pandas data frame
    return from_dataframe(df, directed=directed, **kwargs)


def to_dataframe(network: Network) -> pd.DataFrame:
    """Returns a pandas dataframe of the network.

    Returns a pandas dataframe data that contains all edges including all edge
    attributes. Node and network-level attributes are not included.

    """
    df = pd.DataFrame()
    for edge in network.edges:
        edge_df = pd.DataFrame(columns=['v', 'w', 'uid'])
        edge_df.loc[0] = [edge.v.uid, edge.w.uid, edge.uid]        
        edge_df = pd.concat([edge_df, edge.attributes.to_frame()], axis=1)
        df = pd.concat([edge_df, df], ignore_index=True)
    return df


def to_csv(network: Network, path_or_buf: Any = None, **pdargs: Any):
    """Stores all edges including edge attributes in a csv file.

    Node and network-level attributes are not included.

    Parameters
    ----------

    network: Network

        The network to save as csv file

    path_or_buf: Any

        This can be a string, a file buffer, or None (default). Follows
        pandas.DataFrame.to_csv semantics.  If a string filename is given, the
        network will be saved in a file. If None, the csv file contents is
        returned as a string. If a file buffer is given, the csv file will be
        saved to the file.

    **pdargs:

        Keyword args that will be passed to pandas.DataFrame.to_csv. This
        allows full control of the csv export.

    """

    df = to_dataframe(network)
    return df.to_csv(path_or_buf=path_or_buf, index=False, **pdargs)


def to_sqlite(network: Network,  table: str,
              filename: Optional[str] = None,
              con: Optional[sqlite3.Connection] = None, **pdargs: Any) -> None:
    """Stores all edges including edge attributes in an sqlite database table.

    Node and network-level attributes are not included.

    Parameters
    ----------

    network: Network

        The network to store in the sqlite database

    filename: str

        The name of the SQLite database in which the network will be stored

    con: sqlite3.Connection

        The SQLite3 connection in which the network will be stored

    table: str

        Name of the table in the database in which the network will be stored.

    **pdargs:

        Keyword args that will be passed to pandas.DataFrame.to_sql.

    """

    df = to_dataframe(network)

    LOG.debug('Store network as sql database.')

    if con is None and filename is None:
        LOG.error('Either an SQL connection or a filename is required')
        raise IOError

    con_close = False
    # connect to database if not given
    if con is None:
        con = sqlite3.connect(cast(str, filename))
        con_close = True

    df.to_sql(table, con, **pdargs)

    if con_close:
        _con = cast(sqlite3.Connection, con)
        _con.close()

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
