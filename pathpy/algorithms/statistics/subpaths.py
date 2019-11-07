#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : subpaths.py -- Modules for subpath analysis
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2019-11-07 15:14 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================

from __future__ import annotations
from typing import Tuple, Optional
from collections import Counter, defaultdict
import datetime
import sys
import numpy as np

from ... import logger, config, tqdm
from ...classes.base.containers import PathDict

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

        # initialize variables
        self.subpaths: Counter = Counter()
        self._observed = defaultdict(Counter)
        self._possible = defaultdict(Counter)

    def __call__(self, min_length: int = 0,
                 max_length: int = sys.maxsize,
                 include_path: bool = False) -> PathDict:
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

    @property
    def observed(self) -> defaultdict:
        """Returns observed paths as a dict of counters."""
        if not self._observed:
            self.statistics()
        return self._observed

    @property
    def possible(self) -> defaultdict:
        """Returns possible paths as a dict of counters."""
        if not self._possible:
            self.statistics()
        return self._possible

    def counter(self, min_length: int = 0,
                max_length: int = sys.maxsize,
                include_path: bool = False, leave: bool = False) -> Counter:
        """Returns a counter of all sub-paths"""

        # initializing the counter object
        subpaths: Counter = Counter()
        _min_length = min_length
        _max_length = max_length

        # iterrate over all paths in the network
        for uid, path in tqdm(self.paths.items(),
                              desc='subpath counter', leave=leave):

            # number of counted paths
            frequency = path['frequency']

            # if min_length is zero, account also for nodes
            if _min_length <= 0:
                for node in path.as_nodes:
                    subpaths[node] += frequency

            # get min and max length
            min_length = max(_min_length, 1)
            max_length = min(len(path)-1, _max_length)

            # get subpaths
            for i in range(min_length-1, max_length):
                for j in range(len(path)-i):
                    subpaths['|'.join(path.as_edges[j:j+i+1])] += frequency

            # include the path
            if include_path:
                subpaths[uid] += frequency

        # store result as a class variable
        self.subpaths = subpaths

        # return the subpath counter
        return subpaths

    def statistics(self) -> Tuple:
        """Calculates the sub-path statistics based on path length."""

        log.debug('start generate subpath statistics')
        a = datetime.datetime.now()

        # initialize variables
        observed = defaultdict(Counter)
        possible = defaultdict(Counter)

        # counter of the path frequencies
        counter = self.paths.counter()

        # get subpath uids with count
        # NOTE: Very time consuming method!
        subpaths = self.counter(include_path=False)

        # iterate over all subpaths
        for uid, count in subpaths.items():
            # get order of the elements

            # check if object is a path
            if uid in self.paths:
                order = len(self.paths[uid])

            # check if object is an edge
            elif uid in self.edges:
                order = 1

            # check if object is a node
            elif uid in self.nodes:
                order = 0

            # if object not in the network observe length from the uid
            else:
                order = len(uid.split(self.separator['path']))

            # assigne path
            possible[order][uid] += count

        # iterate over all observed paths
        for uid, path in self.paths.items():
            observed[len(path)][uid] += counter[uid]

        # store results as class variables
        self._observed = observed
        self._possible = possible

        b = datetime.datetime.now()
        log.debug('end generate subpath statistics:' +
                  ' {} seconds'.format((b-a).total_seconds()))

        return observed, possible

    def summary(self) -> Optional[str]:
        """Returns a summary of the sub path statistic.

        Returns
        -------
        str
            Retruns a summary of the sub path statistics.

        """

        # check if sub path statistic is already calculated
        if not self.observed:
            self.statistics()

        # initialize a data storage
        data = Counter()

        # get data of observed paths
        for order in range(max(self.observed.keys())+1):
            data[order] = sum(self.observed[order].values())

        data = list(data.elements())

        # TODO: Find better solution for printing
        # TODO: Move to util
        line_length = 54
        row = {}
        row['==='] = '='*line_length
        row['sf'] = '{:<25s}{:>15.3f}'
        row['s|sss|ss'] = '{:^6s} | {:^9s} {:^9s} {:^9s} | {:^6s} {:^6s}'
        row['-|---|--'] = '{:->6s} | {:->9s} {:->9s} {:->9s} | {:->6s} {:->6s}'
        row['d|ddd|dd'] = '{:>6d} | {:>9d} {:>9d} {:>9d} | {:>6d} {:>6d}'
        row['s| s | s'] = '{:^6s} | {:^29s} | {:^13s}'

        # initialize summary text
        summary = [
            row['==='],
            'Sub path statistics',
        ]

        # add general statistics
        lines = [
            ['- General '],
            ['Number of unique nodes:', len(self.nodes)],
            ['Number of unique edges:', len(self.edges)],
            ['Number of unique paths:', len(self.paths)],
            ['- Path statistics '],
            ['Mean path length:', np.mean(data)],
            ['Standard derivation:', np.std(data)],
            ['Min. path length:', np.min(data)],
            ['25% quantile:', np.quantile(data, 0.25)],
            ['50% quantile:', np.quantile(data, 0.50)],
            ['75% quantile:', np.quantile(data, 0.75)],
            ['Max. path length:', np.max(data)],
            ['- Sub path statistics ']
        ]

        for line in lines:
            if len(line) == 1:
                summary.append('{}'.format(line[0]).ljust(line_length, '-'))
            else:
                summary.append(row['sf'].format(line[0], line[1]))

        # add sub path statistics
        # add headings
        summary.append(row['s| s | s'].format('path', 'frequencies', 'unique'))
        summary.append(row['s|sss|ss'].format(
            'length', 'obs', 'pos', 'tot', 'obs', 'pos'))

        # add line
        summary.append(row['-|---|--'].format('', '', '', '', '', ''))

        # add row for each order
        data = [[], [], [], [], []]
        for order in range(max(self.observed.keys())+1):

            data[0].append(sum(self.observed[order].values()))
            data[1].append(sum(self.possible[order].values()))
            data[2].append(data[0][-1]+data[1][-1])
            data[3].append(len(self.observed[order]))
            data[4].append(len(self.possible[order]))

            summary.append(row['d|ddd|dd'].format(
                order, *[v[-1] for v in data]))

        # add line
        summary.append(row['-|---|--'].format('', '', '', '', '', ''))

        # add column sums
        summary.append(row['d|ddd|dd'].format(order, *[sum(v) for v in data]))

        # add legend
        summary.append('obs ... observed paths (in the network)')
        summary.append('pos ... possible paths (but not observed)')
        summary.append('tot ... total number of paths')

        # add double line
        summary.append('='*line_length,)

        # if logging is enabled print summary as INFO log
        if config['logging']['enabled']:
            for line in summary:
                log.info(line.rstrip())
            return None

        # otherwise return the summary as string
        else:
            return '\n'.join(summary)

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
