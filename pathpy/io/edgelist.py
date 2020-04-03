#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : edgelist.py -- Module for input/output edges to pathpy
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Tue 2020-03-24 13:06 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations

import pandas as pd
import sqlite3

from typing import Any
from .. import config, logger
from pathpy.core.network import Network
from pathpy.core.edge import Edge

# create logger
log = logger(__name__)

def from_csv(filename: str, directed: bool=True, sep: str=',', header: bool=True, names: list= None, **kwargs: Any) -> Network:
    """Read network from a csv file"""
    if header:
        df = pd.read_csv(filename, sep=sep)
        return from_pd(df, directed, **kwargs)
    else:
        df = pd.read_csv(filename, header=0, names=names, sep=sep)
        return from_pd(df, directed, **kwargs)

def from_pd(df: pd.DataFrame, directed: bool=True, **kwargs: Any) -> Network:
    """Read network from a pandas dataframe."""
    n = Network(directed=directed, **kwargs)
    for row in df.to_dict(orient='records'):

        # get edge parameters                
        v = row.get('v', None)
        w = row.get('w', None)
        uid = row.get('uid', None)
        if 'v' is None or 'w' is None:
            log.error('DataFrame minimally needs columns \'v\' and \'w\'')
            raise IOError
        if uid ==None:
            edge = Edge(v, w)
        else:
            edge = Edge(v, w, uid=uid)
        n.add_edge(edge)
        reserved_columns = set(['v', 'w', 'uid'])
        for k in row:
            if k not in reserved_columns:
                n.edges[edge.uid][k] = row[k]
    return n

def from_sqlite(filename: str, directed: bool = True, con: sqlite3.Connection = None, sql: str = None, table: str = None, **kwargs: Any):
    """Read network from an sqlite database."""

    log.debug('Load sql file as pandas data frame.')

    # connect to database if not given
    if con is None:
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

    # load pandas data frame
    df = pd.read_sql(sql, con, **kwargs)

    # close connection to the database
    con.close()

    return from_pd(df)


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
