#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : csv.py -- Read data from csv files
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Wed 2019-10-23 16:59 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, List, Dict, Tuple, Optional
import datetime
import sys

from .. import logger, config
from ..classes import Node, Edge, Path

# create logger for the Edge class
log = logger(__name__)


def read_csv(self, filename: str, separator: str = ',', **kwargs: Any):

    log.debug('start reading csv file')
    a = datetime.datetime.now()

    with open(filename, 'r') as f:
        line = f.readline()
        n: int = 1
        while line and n <= sys.maxsize:
            path = line.rstrip().split(separator)
            edges = [(v+'-'+w, v, w) for v, w in zip(path[:-1], path[1:])]
            p_uid = '|'.join([v[0] for v in edges])
            _path = []
            if p_uid not in self.paths:
                for e, v, w in edges:
                    if e not in self.edges:

                        if v not in self.nodes:
                            self.nodes[v] = Node(v)

                        if w not in self.nodes:
                            self.nodes[w] = Node(w)

                        self.edges[e] = Edge(self.nodes[v], self.nodes[w])

                        self.edges[e].frequency += 1
                        self.nodes[v].frequency += 1
                        self.nodes[w].frequency += 1
                    _path.append(self.edges[e])
                #self.paths[p_uid] = None
                self.paths[p_uid] = Path(*_path)
                self.paths[p_uid].frequency += 1
            else:
                # print(path)
                for e, v, w in edges:
                    self.edges[e].frequency += 1
                    self.nodes[v].frequency += 1
                    self.nodes[w].frequency += 1

                self.paths[p_uid].frequency += 1

            line = f.readline()
            n += 1

    b = datetime.datetime.now()
    log.debug('end reading csv file after:' +
              ' {} seconds'.format((b-a).total_seconds()))

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
