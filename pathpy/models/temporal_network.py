"""Temporal network class"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : temporal_network.py -- Class for temporal networks
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Wed 2020-06-24 18:39 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================


from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional, Union, cast
from intervaltree import IntervalTree, Interval
from collections import defaultdict

from pathpy import logger
from pathpy.core.node import Node, NodeCollection
from pathpy.core.edge import Edge, EdgeCollection
from pathpy.core.path import Path
from pathpy.core.network import Network

from pathpy.models.models import ABCTemporalNetwork

# pseudo load class for type checking
if TYPE_CHECKING:
    from pathpy.core.edge import EdgeSet


# create logger for the Network class
LOG = logger(__name__)


class Timestamp:
    """Class to store timestamps."""


class TemporalNetwork(ABCTemporalNetwork, Network):
    """Base class for a temporal networks."""

    def __init__(self, uid: Optional[str] = None,
                 directed: bool = True, temporal: bool = False,
                 multiedges: bool = False, **kwargs: Any) -> None:
        """Initialize the temporal network object."""

        # initialize the base class
        super().__init__(uid=uid, directed=directed, temporal=True,
                         multiedges=multiedges, **kwargs)

        # a container for node objects
        self._nodes: TemporalNodeCollection = TemporalNodeCollection()

        # a container for edge objects
        self._edges: TemporalEdgeCollection = TemporalEdgeCollection(
            directed=directed,
            multiedges=multiedges,
            nodes=self._nodes)

    def add_edge(self, *edge: Union[str, tuple, list, Node, Edge],
                 uid: Optional[str] = None,
                 begin: Union[str, float] = float('-inf'),
                 end: Union[str, float] = float('inf'), **kwargs: Any) -> None:
        kwargs.update({'begin': begin, 'end': end})

        super().add_edge(*edge, uid=uid, **kwargs)


class TemporalNodeCollection(NodeCollection):
    """A collection of temporal nodes"""


class TemporalEdgeCollection(EdgeCollection):
    """A collection of temporal edges"""

    def __init__(self, directed: bool = True, multiedges: bool = False,
                 nodes: Optional[TemporalNodeCollection] = None) -> None:
        """Initialize the network object."""

        # collection of nodes
        self._nodes: TemporalNodeCollection = TemporalNodeCollection()
        if nodes is not None:
            self._nodes = nodes

        # initialize the base class
        super().__init__(directed=directed, multiedges=multiedges,
                         nodes=nodes)

        # map intervals to edges
        self._intervals: IntervalTree = IntervalTree()

        # map edges to intervals
        self._temporal_map: defaultdict = defaultdict(set)

    def _if_edge_exists(self, edge: Any, **kwargs: Any) -> None:

        # get the edge
        if isinstance(edge, list):
            _edge = cast(Edge, self[edge[0], edge[1]])
        elif isinstance(edge, (str, Edge)):
            _edge = cast(Edge, self[edge])
        else:
            raise KeyError
        begin = kwargs['begin']
        end = kwargs['end']

        self._intervals.addi(begin, end, _edge)
        self._temporal_map[_edge].add((begin, end))

    def _add(self, edge: Edge) -> None:
        """Add an edge to the set of edges."""
        begin = edge.attributes['begin']
        end = edge.attributes['end']

        self._intervals.addi(begin, end, edge)
        self._temporal_map[edge].add((begin, end))

        super()._add(edge)

    def items(self, temporal=False):
        if not temporal:
            return self._map.items()
        else:
            return [(i.data.uid, i.data, i.begin, i.end)
                    for i in sorted(self._intervals)]

    def __getitem__(self, key: Union[str, tuple, Edge]
                    ) -> Union[Edge, EdgeSet, TemporalEdgeCollection]:
        """Returns a node object."""
        _item: Any
        if isinstance(key, (int, float, slice)):
            _item = self._new_from_intervals(self._intervals[key])
        else:
            _item = super().__getitem__(key)
        return _item

    def _new_from_intervals(self, intervals: IntervalTree) -> TemporalEdgeCollection:
        new = TemporalEdgeCollection()
        for begin, end, edge in intervals:
            new.add(edge, begin=begin, end=end)

        return new

    def slice(self, begin, end) -> TemporalEdgeCollection:
        """Return a temporal slice"""

        tree = self._intervals.copy()
        tree.slice(begin)
        tree.slice(end)
        tree.remove_envelop(self._intervals.begin(), begin)
        tree.remove_envelop(end, self._intervals.end())

        return self._new_from_intervals(tree)

    def begin(self, finite=True) -> float:
        """Begin of the time"""

        _begin = self._intervals.begin()
        _end = float('inf')
        if finite:
            for b, _, _ in sorted(self._intervals):
                if b > float('-inf'):
                    _begin = b
                    break
            _end = sorted(self._intervals, key=lambda x: x[1])[0][1]
            if _begin == float('-inf') and _end < float('inf'):
                _begin = _end
        return min(_begin, _end)

    def end(self, finite=True) -> float:
        """End of the time"""

        _begin = float('-inf')
        _end = self._intervals.end()
        if finite:
            for _, e, _ in sorted(self._intervals, key=lambda x: x[1],
                                  reverse=True):
                if e < float('inf'):
                    _end = e
                    break
            _begin = sorted(self._intervals)[-1][0]
            if _begin > float('-inf') and _end == float('inf'):
                _end = _begin
        return max(_begin, _end)
# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
