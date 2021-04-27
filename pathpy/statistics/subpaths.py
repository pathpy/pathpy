"""Methods to calculate sub-path statistics in Paths and PathCollections"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : subpaths.py • models -- Module for sub-path statistics
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Sat 2020-09-05 13:03 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Optional
import sys
from collections import Counter, defaultdict

import numpy as np

from pathpy import logger, tqdm
from pathpy.core.api import PathCollection, Path

# create logger for the Network class
LOG = logger(__name__)


class SubPathCollection(PathCollection):
    """Class for sub-path statistics."""

    def __init__(self, paths: Optional[PathCollection] = None) -> None:
        """Initialize sub-paths object."""

        # check if inital paths are given
        if isinstance(paths, PathCollection):
            self._paths = paths
        else:
            self._paths = PathCollection()

        # initialize the base class
        super().__init__(directed=self._paths.directed,
                         multiedges=self._paths.multiedges,
                         multipaths=self._paths.multipaths,
                         nodes=self._paths.nodes,
                         edges=self._paths.edges)

        # initialize counters
        self._counter: Counter = Counter()
        self._observed: defaultdict = defaultdict(Counter)
        self._possible: defaultdict = defaultdict(Counter)

    def __call__(self, min_length: int = 0, max_length: int = sys.maxsize,
                 include_path: bool = False,
                 recalculate: bool = False) -> SubPathCollection:
        """Returns a sub-pahts"""
        if len(self) == 0 or recalculate:
            self.calculate(min_length=min_length, max_length=max_length,
                           include_path=include_path)
        return self

    def __str__(self) -> str:
        """Print a summary of the sub-paths."""
        return self.summary()

    @property
    def observed(self) -> defaultdict:
        """Returns observed paths as a dict of counters."""
        return self._observed

    @property
    def possible(self) -> defaultdict:
        """Returns possible paths as a dict of counters."""
        return self._possible

    @property
    def counter(self) -> Counter:
        """Returns a subpath counter"""
        return self._counter

    def calculate(self, min_length: int = 0, max_length: int = sys.maxsize,
                  include_path: bool = False) -> None:
        """Helper function to calculate subpaths."""

        if len(self) > 0:
            LOG.warning('Recalculating sub-paths!')
        # get the default max and min path lengths
        _min_length: int = min_length
        _max_length: int = max_length

        # iterrate over all paths
        for path in tqdm(self._paths.values(), desc='sub-path calculation'):

            # number of counted paths
            frequency = path.attributes.get('frequency', 1)

            # if min_length is zero, account also for nodes
            if _min_length <= 0:
                for node in path.nodes:
                    if (node,) not in self:
                        self._add(Path(node, possible=frequency, frequency=0))
                    else:
                        self[(node,)]['possible'] += frequency

            # get min and max length
            min_length = max(_min_length, 1)
            max_length = min(len(path)-1, _max_length)

            # get subpaths
            for i in range(min_length-1, max_length):
                for j in range(len(path)-i):
                    edges = tuple(path.edges[j:j+i+1])
                    if edges not in self:
                        self._add(Path(*edges, possible=frequency, frequency=0))
                    else:
                        # TODO: fix the frequency assignment
                        if self[edges]['possible'] is None:
                            self[edges]['possible'] = 0
                        self[edges]['possible'] += frequency

            # include the path
            if include_path:
                if path not in self and _min_length <= len(path) <= _max_length:
                    path['possible'] = 0
                    self._add(path)

        for path in self:
            self._observed[len(path)][path] += path['frequency'] or 0
            self._possible[len(path)][path] += path['possible'] or 0
            self._counter[path] += path['frequency'] or 0
            self._counter[path] += path['possible'] or 0

    def summary(self) -> str:
        """Returns a summary of the sub path statistic.

        Returns
        -------
        str
            Retruns a summary of the sub path statistics.

        """

        # check if sub path statistic is already calculated
        if len(self) == 0:
            return super().__str__()

        # initialize a data storage
        counter: Counter = Counter()

        # get max order
        max_order_obs = max(self.observed.keys())
        max_order_pos = max(self.possible.keys())
        max_order = max(max_order_obs, max_order_pos)

        # get data of observed paths
        for order in range(max_order_obs+1):
            counter[order] = int(sum(self.observed[order].values()))

        data: list = list(counter.elements())

        # TODO: Find better solution for printing
        # TODO: Move to util
        line_length = 54
        row = {}
        row['==='] = '='*line_length
        row['sf'] = '{:<25s}{:>15.3f}'
        row['s|sss|ss'] = '{:^6s} | {:^9s} {:^9s} {:^9s} | {:^6s} {:^6s}'
        row['-|---|--'] = '{:->6s} | {:->9s} {:->9s} {:->9s} | {:->6s} {:->6s}'
        row['d|ddd|dd'] = '{:>6d} | {:>9d} {:>9d} {:>9d} | {:>6d} {:>6d}'
        row['f|fff|ff'] = '{:>6.0f} | {:>9.0f} {:>9.0f} {:>9.0f} | {:>6.0f} {:>6.0f}'
        row['s| s | s'] = '{:^6s} | {:^29s} | {:^13s}'

        # initialize summary text
        summary: list = [
            row['==='],
            'Sub path statistics',
        ]

        if data:
            # add general statistics
            lines: list = [
                ['- General '],
                ['Number of unique nodes:', len(self.nodes)],
                ['Number of unique edges:', len(self.edges)],
                ['Number of unique paths:', len(self._paths)],
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
        data: list = [[], [], [], [], []]
        for order in range(max_order+1):

            data[0].append(sum(self.observed[order].values()))
            data[1].append(sum(self.possible[order].values()))
            data[2].append(data[0][-1]+data[1][-1])
            data[3].append(np.count_nonzero(
                list(self.observed[order].values())))
            data[4].append(np.count_nonzero(
                list(self.possible[order].values())))

            summary.append(row['f|fff|ff'].format(
                order, *[v[-1] for v in data]))

        # add line
        summary.append(row['-|---|--'].format('', '', '', '', '', ''))

        # add column sums
        summary.append(row['f|fff|ff'].format(order, *[sum(v) for v in data]))

        # add legend
        summary.append('obs ... observed paths (in the network)')
        summary.append('pos ... possible paths (but not observed)')
        summary.append('tot ... total number of paths')

        # add double line
        summary.append('='*line_length,)

        # # if logging is enabled print summary as INFO log
        # # TODO: Move this code to a helper function
        return '\n'.join(summary)

    @classmethod
    def from_paths(cls, paths: PathCollection,
                   min_length: int = 0,
                   max_length: int = sys.maxsize,
                   include_path: bool = False) -> SubPathCollection:
        """Create sub-paths statistic from a path collection object."""
        subpaths = cls(paths)
        subpaths.calculate(min_length=min_length, max_length=max_length,
                           include_path=include_path)
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
