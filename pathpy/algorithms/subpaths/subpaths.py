#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : subpaths.py -- Modules for subpath analysis
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2019-10-31 17:31 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================

from __future__ import annotations
from typing import Any, List, Dict, Tuple, Optional
from collections import Counter
import datetime
import sys
from ...classes.base.containers import PathDict
# from copy import deepcopy

from ... import logger  # , config
#from .classes import Node, Edge, Path

# create logger for the class
log = logger(__name__)


class SubPaths:
    """Class to analyze sub-paths"""

    def __init__(self, network):
        """Initialize the sub-paths object"""

        # get information from the network
        self.nodes = network.nodes
        self.edges = network.edges
        self.paths = network.paths
        self.separator = network.separator

    def __call__(self, min_length: int = 0,
                 max_length: int = sys.maxsize,
                 include_path: bool = False):
        """Returns a dictionary of sub-pahts"""

        # initialize empty dict
        subpaths = PathDict(dict)

        # iterate through the given paths
        for path in self.paths.values():

            # get the subpaths
            paths = path.subpaths(min_length=min_length,
                                  max_length=max_length,
                                  include_path=include_path)

            # update the list of the subpaths
            # TODO: update also the frequency
            subpaths.update(paths)

        # return dict of sub-paths
        return subpaths

    def counter(self, min_length: int = 0,
                max_length: int = sys.maxsize,
                include_path: bool = False) -> Counter:
        """Returns a counter of all sub-paths"""

        # initializing the counter object
        subpaths: Counter = Counter()
        _min_length = min_length
        _max_length = max_length
        # iterrate over all paths in the network
        for uid, path in self.paths.items():

            # number of counted paths
            frequency = path['frequency']

            # if min_length is zero, account also for nodes
            if _min_length <= 0:
                for node in path.as_nodes:
                    subpaths[node] += frequency

            min_length = max(_min_length, 1)
            max_length = min(len(path)-1, _max_length)

            # get subpaths
            for i in range(min_length-1, max_length):
                for j in range(len(path)-i):
                    subpaths['|'.join(path.as_edges[j:j+i+1])] += frequency

            # include the path
            if include_path:
                subpaths[uid] += frequency
        return subpaths

    def statistics(self):
        """Calculates the sub-path statistics."""
        log.debug('I\'m a Network')
        log.debug('start generate subpath statistics')
        a = datetime.datetime.now()

        path_counter = self.paths.counter()
        # observed paths of length k
        op = Counter()
        for uid, count in path_counter.items():
            op[len(uid.split(self.separator['path']))] += count

        print('op', op)

        # unique paths of length k
        up = Counter()
        for uid in self.paths:
            up[len(uid.split(self.separator['path']))] += 1

        print(up)

        # subpaths of length k
        sp = Counter()

        # NOTE: Very time consuming method!
        spc = self.counter()

        # print(spc)
        for uid, count in spc.items():

            # print(uid, count)
            split = uid.split(self.separator['path'])
            if len(split) == 1:
                if split[0] in self.nodes:
                    sp[0] += count
                elif split[0] in self.edges:
                    sp[1] += count

            elif len(split) >= 2:
                sp[len(split)] += count

        print(sp)

        # get max length
        max_length = max(max(up), max(sp))
        min_length = min(min(up), min(sp))
        for i in range(min_length, max_length+1):
            _values = {
                'k': i-min_length,
                'op': op[i],
                'up': up[i],
                'sp': sp[i],
                'tp': op[i] + sp[i]
            }
            print('k={k}: {op} / {up} / {sp} / {tp}'.format(**_values))

        # total paths of length k

        b = datetime.datetime.now()
        log.debug('end generate subpath statistics:' +
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
