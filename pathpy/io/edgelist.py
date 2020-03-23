#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : edgelist.py -- Module for input/output edges to pathpy
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Mon 2020-03-23 12:07 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations

import pandas as pd

from typing import Any
from .. import logger

# create logger
log = logger(__name__)


def read_edgelist(self, filename: str, separator: str = ',',
                  **kwargs: Any):
    """Read edges from a file."""
    log.debug('Read edges from a file.')
    # check the file format given
    if filename.endswith('.csv'):
        log.debug('Load csv file as pandas data frame.')
        # load pandas data frame
        data = pd.read_csv(filename, sep=separator, **kwargs)
    else:
        log.error('The file format for the file "{}" ' +
                  'is not supported currently! ' +
                  'Please try to use a "csv" ' +
                  'file instead.'.format(filename))
        raise IOError
    print(data.head())
    # check string of the nodes and edge uids
    data[data.columns[0]] = (data[data.columns[0]]
                             .str.replace('-', '_')
                             .str.replace('|', '_')
                             .str.replace('=', '_'))
    data[data.columns[1]] = (data[data.columns[1]]
                             .str.replace('-', '_')
                             .str.replace('|', '_')
                             .str.replace('=', '_'))

    # add edges to the network
    for index, row in data.iterrows():
        self.add_edge(row[0], row[1])


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
