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
from ..core.edge import Edge

# create logger
log = logger(__name__)


def read_edgelist(self, filename: str, separator: str = ',',
                  directed: bool = True,
                  con: str = None, sql: str = None, table: str = None,
                  **kwargs: Any):
    """Read edges from a file."""
    log.debug('Read edges from a file.')

    # check the file format given
    if filename.endswith('.csv'):

        log.debug('Load csv file as pandas data frame.')

        # load pandas data frame
        data = pd.read_csv(filename, sep=separator, **kwargs)

    elif filename.endswith('.db'):

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
                log.error('The given table "{}" ' +
                          'is not in the database!'.format(table))
                raise IOError

            # generate sql query
            sql = 'SELECT * from {}'.format(table)

        # load pandas data frame
        data = pd.read_sql(sql, con, **kwargs)

        # close connection to the database
        con.close()

    else:
        # raise error if file is not supported
        log.error('The file format for the file "{}" ' +
                  'is not supported currently! ' +
                  'Please try to use a "csv" ' +
                  'file instead.'.format(filename))
        raise IOError

    columns: dict = {}
    # check columns of the data frame
    for column in data.columns:
        if column.lower() in config['edge']['v_synonyms']:
            columns[column] = 'v'
        if column.lower() in config['edge']['w_synonyms']:
            columns[column] = 'w'

    # rename columns
    data.rename(columns, axis=1, inplace=True)

    # check string of the nodes and edge uids
    for column in ['v', 'w', 'uid']:
        if column in data.columns:
            for k, v in self.separator.items():
                # replace seperators with other characters
                data[column] = (data[column]
                                .str.replace(v, config[k]['replace']))

    # iterate over edges and add them to the network
    # TODO: make this faster!!!
    for edge in data.to_dict(orient='records'):

        # get edge parameters
        v = edge['v']
        w = edge['w']
        uid = edge.get('uid', None)

        # delete edge parameters
        del edge['v']
        del edge['w']
        if uid in edge:
            del edge['uid']

        # add edges to the network
        self.add_edge(Edge(v, w, uid, directed=self.directed, **edge))


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
