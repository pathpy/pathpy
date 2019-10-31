#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : counter.py -- Module for sub-path counters
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2019-10-31 11:05 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from collections import Counter

# TODO: Expand this to a major code


def subpath_counter(self, min_length: int = 0,
                    max_length: int = 999999,
                    include_path: bool = False) -> Counter:

    # initializing the counter object
    subpaths: Counter = Counter()
    _min_length = min_length
    _max_length = max_length
    # iterrate over all paths in the network
    for uid, path in self.paths.items():

        # number of counted paths
        frequency = path.frequency

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


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
