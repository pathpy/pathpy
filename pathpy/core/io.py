#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : io.py -- Module for data import/export
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Tue 2020-04-03 12:41 ingo>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations

import pandas as pd
import sqlite3

from typing import Any
from pathpy import config, logger
from pathpy.core.network import Network
from pathpy.core.edge import Edge

# create logger
log = logger(__name__)

def from_csv(filename: str, directed: bool=True, sep: str=',', header: bool=True, names: list= None, **kwargs: Any) -> Network:
    """Read network from a csv file"""
    if header:
        df = pd.read_csv(filename, sep=sep)
        return from_dataframe(df, directed, **kwargs)
    else:
        df = pd.read_csv(filename, header=0, names=names, sep=sep)
        return from_dataframe(df, directed=directed, **kwargs)

def from_dataframe(df: pd.DataFrame, directed: bool=True, **kwargs: Any) -> Network:
    """Reads a network from a pandas dataframe. By default, columns `v` and `w` will be used 
    as source and target of edges. If no column 'v' or 'w' exists, the list of synonyms for `v` and `w``
    in the config file will be used to remap columns, choosing the first matching entries. Any columns not 
    used to create edges will be used as edge attributes, e.g. if a column 'v' is present and an additional 
    column `source`is given, `source` will be assigned as an edge property.
    
    In addition, an optional column `uid` will be used to 
    assign node uids. If this column is not present, default edge uids will be created. 
    Any other columns (e.g. weight, type, time, etc.) will be assigned as edge attributes. kwargs 
    will be assigned as network attributes.
    

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
        log.info('No column v, searching for synonyms')
        for col in df.columns:
            if col in config['edge']['v_synonyms']:
                log.info('Remapping column \'{}\' to \'v\''.format(col))
                df.rename(columns = {col: "v"}, inplace=True)
                continue

    if 'w' not in df.columns:
        log.info('No column w, searching for synonyms')
        for col in df.columns:
            if col in config['edge']['w_synonyms']:
                log.info('Remapping column \'{}\' to \'w\''.format(col))
                df.rename(columns = {col: "w"}, inplace=True)
                continue
    log.debug('Creating {} network'.format(directed))
    n = Network(directed=directed, **kwargs)
    for row in df.to_dict(orient='records'):

        # get edge
        v = row.get('v', None)
        w = row.get('w', None)
        uid = row.get('uid', None)
        if v is None or w is None:
            log.error('DataFrame minimally needs columns \'v\' and \'w\'')
            raise IOError
        if uid ==None:
            edge = Edge(v, w, directed=directed)
        else:
            edge = Edge(v, w, uid=uid, directed=directed)
        n.add_edge(edge)

        reserved_columns = set(['v', 'w', 'uid'])
        for k in row:
            if k not in reserved_columns:
                n.edges[edge.uid][k] = row[k]
    return n

def from_sqlite(filename: str = None, directed: bool = True, con: sqlite3.Connection = None, sql: str = None, table: str = None, **kwargs: Any) -> Network:
    """Read network from an sqlite database."""

    log.debug('Load sql file as pandas data frame.')

    if con is None and filename is None:
        log.error('Either an SQL connection or a filename is required')
        raise IOError

    con_close = False
    # connect to database if not given
    if con is None:
        con_close = True
        con = sqlite3.connect(filename)

    # if sql query is not given check availabe tables
    if sql is None:

        # create cursor and get all tables availabe
        cursor = con.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = list(sum(cursor.fetchall(), ()))

        # check if table is given
        if table is None:
            table = tables[0]
        elif table not in tables:
            log.error('Given table "{}" not in database!'.format(table))
            raise IOError

        # generate sql query
        sql = 'SELECT * from {}'.format(table)

    # read to pandas data frame
    df = pd.read_sql(sql, con)

    # close connection to the database
    if con_close:
        con.close()

    # construct network from pandas data frame
    return from_dataframe(df, directed=directed, **kwargs)

def to_dataframe(network: Network) -> pd.DataFrame:
    """Returns a pandas dataframe data that contains all edges including 
    all edge attributes. Node and network-level attributes are not included."""

    df = pd.DataFrame()
    for e in network.edges:
        edge = network.edges[e]
        edge_df = edge.attributes.to_frame()
        edge_df['v'] = edge.v.uid
        edge_df['w'] = edge.w.uid
        edge_df['uid'] = edge.uid
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

        This can be a string, a file buffer, or None (default). Follows pandas.DataFrame.to_csv semantics. 
        If a string filename is given, the network will be saved in a file. If None, the csv file contents
        is returned as a string. If a file buffer is given, the csv file will be saved to the file. 

    **pdargs:

        Keyword args that will be passed to pandas.DataFrame.to_csv. This allows full control of the 
        csv export.
    """

    df = to_dataframe(network)
    return df.to_csv(path_or_buf = path_or_buf, **pdargs)

def to_sqlite(network: Network,  table: str, filename: str = None, con: sqlite3.Connection = None, **pdargs: Any):
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

    log.debug('Store network as sql database.')

    if con is None and filename is None:
        log.error('Either an SQL connection or a filename is required')
        raise IOError

    con_close = False
    # connect to database if not given
    if con is None:
        con_close = True
        con = sqlite3.connect(filename)

    df.to_sql(table, con, **pdargs)

    if con_close: 
        con.close()

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
