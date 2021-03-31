"""Temporal network class"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : temporal_network.py -- Class for temporal networks
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Mon 2021-03-29 17:30 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional, Union, cast
from intervaltree import IntervalTree, Interval
from collections import defaultdict

from pathpy import logger, config
from pathpy.core.node import Node, NodeCollection
from pathpy.core.edge import Edge, EdgeCollection
from pathpy.models.network import Network

from pathpy.core.base.attributes import TemporalAttributes

from pathpy.converters import to_paths

from pathpy.models.models import ABCTemporalNetwork

# pseudo load class for type checking
if TYPE_CHECKING:
    from pathpy.core.edge import EdgeSet


# create logger for the Network class
LOG = logger(__name__)
TIMESTAMP = config['temporal']['timestamp']


class Timestamp:
    """Class to store timestamps."""


class TemporalNetwork(ABCTemporalNetwork, Network):
    """Base class for a temporal networks."""

    # load external functions to the network
    to_paths = to_paths.to_path_collection  # type: ignore

    def __init__(self, uid: Optional[str] = None,
                 directed: bool = True, multiedges: bool = False,
                 **kwargs: Any) -> None:
        """Initialize the temporal network object."""

        # initialize the base class
        super().__init__(uid=uid, directed=directed,
                         multiedges=multiedges, **kwargs)

        # add network properties
        self._properties['nodes'] = set()

        # a container for node objects
        self._nodes: TemporalNodeCollection = TemporalNodeCollection()

        # a container for edge objects
        self._edges: TemporalEdgeCollection = TemporalEdgeCollection(
            directed=directed,
            multiedges=multiedges,
            nodes=self._nodes)

    def _add_node_properties(self):
        """Helper function to update node properties."""

        nodes = set(self.nodes).difference(self._properties['nodes'])

        for node in nodes:
            attr = node.attributes
            time = attr.pop(TIMESTAMP, float('-inf'))
            # if attr:
            #     attributes = TemporalAttributes()
            #     attributes.update(**{**attr, **{TIMESTAMP: time}})
            #     node.attributes = attributes

            self._properties['nodes'].add(node)

    def add_edge(self, *edge: Union[str, tuple, list, Node, Edge],
                 uid: Optional[str] = None, **kwargs: Any) -> None:
        """Add an temporal edge."""

        # get keywords defined in the config file
        _begin = kwargs.pop(config['temporal']['begin'], float('-inf'))
        _end = kwargs.pop(config['temporal']['end'], float('inf'))
        _timestamp = kwargs.pop(config['temporal']['timestamp'], None)
        _duration = kwargs.pop(config['temporal']['duration'], None)

        # check if timestamp is given
        if isinstance(_timestamp, (int, float)):
            if isinstance(_duration, (int, float)):
                _begin = _timestamp
                _end = _timestamp + _duration
            else:
                _begin = _timestamp
                _end = _timestamp + config['temporal']['duration_value']

        # TODO: Add other checks eg begin and duration

        kwargs.update({'begin': _begin, 'end': _end})

        super().add_edge(*edge, uid=uid, **kwargs)

    def summary(self) -> str:
        """Returns a summary of the network.

        The summary contains the name, the used network class, if it is
        directed or not, the number of nodes and edges.

        If logging is enabled (see config), the summary is written to the log
        file and showed as information on in the terminal. If logging is not
        enabled, the function will return a string with the information, which
        can be printed to the console.

        Returns
        -------
        str
            Returns a summary of important network properties.

        """
        try:
            _begin = self.edges.begin()
            _end = self.edges.end()
        except IndexError:
            _begin = 0
            _end = 0
        summary = [
            'Uid:\t\t\t{}\n'.format(self.uid),
            'Type:\t\t\t{}\n'.format(self.__class__.__name__),
            'Directed:\t\t{}\n'.format(str(self.directed)),
            'Multi-Edges:\t\t{}\n'.format(str(self.multiedges)),
            'Number of unique nodes:\t{}\n'.format(self.number_of_nodes()),
            'Number of unique edges:\t{}\n'.format(self.number_of_edges()),
            'Number of temp edges:\t{}\n'.format(len(self.edges.temporal())),
            'Observation periode:\t{} - {}'.format(_begin, _end)
        ]
        attr = self.attributes
        if len(attr) > 0:
            summary.append('\n\nNetwork attributes\n')
            summary.append('------------------\n')
        for k, v in attr.items():
            summary.append('{}:\t{}\n'.format(k, v))

        return ''.join(summary)


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
        self._interval_map: defaultdict = defaultdict(set)

    @property
    def intervals(self):
        """Return an interval tree of the temporal edges."""
        return self._intervals

    def temporal(self):
        """Return a list of temporal edges."""
        return [(i.data.uid, i.data, i.begin, i.end)
                for i in sorted(self._intervals)]

    def _if_exist(self, edge: Any, **kwargs: Any) -> None:
        """Helper function if edge already exists."""
        # get the edge
        if isinstance(edge, (tuple, list)):
            _edge = cast(Edge, self[edge[0], edge[1]])
        elif isinstance(edge, (str, Edge)):
            _edge = cast(Edge, self[edge])
        else:
            raise KeyError
        begin = kwargs['begin']
        end = kwargs['end']

        if kwargs:
            _edge.update(**{**kwargs, **{TIMESTAMP: begin}})

        self._intervals.addi(begin, end, _edge)
        self._interval_map[_edge].add((begin, end))

    def _add(self, edge: Edge) -> None:
        """Add an edge to the set of edges."""
        begin = edge.attributes['begin']
        end = edge.attributes['end']

        # attributes = TemporalAttributes()
        # attributes.update(**{**edge.attributes.to_dict(), **{TIMESTAMP: begin}})
        # edge.attributes = attributes

        self._intervals.addi(begin, end, edge)
        self._interval_map[edge].add((begin, end))

        super()._add(edge)

    def items(self, temporal=False):
        """Return a new view of the edge’s items ((key, value) pairs)."""
        if not temporal:
            return self._map.items()
        else:
            return self.temporal()

    def __getitem__(self, key: Union[str, tuple, Edge]
                    ) -> Union[Edge, EdgeSet, TemporalEdgeCollection]:
        """Returns a edge object."""
        _item: Any
        if isinstance(key, (int, float, slice)):
            _item = self._new_from_intervals(self._intervals[key])
        else:
            _item = super().__getitem__(key)
        return _item

    def _new_from_intervals(self, intervals: IntervalTree) -> TemporalEdgeCollection:
        """Helper function which creates a new collection from an interval."""

        # TODO: FIX THIS EDGE ASSIGMENT
        new = TemporalEdgeCollection()
        for begin, end, uid in intervals:
            print('uid', uid)
            new.add(self[uid], begin=begin, end=end)

        # new = []
        # for begin, end, edge in intervals:
        #     print('uid', edge.uid)
        #     new.append((edge, begin, end))

        return new

    def slice(self, begin, end) -> TemporalEdgeCollection:
        """Return a temporal slice of the collection."""

        tree = self._intervals.copy()
        tree.slice(begin)
        tree.slice(end)
        tree.remove_envelop(self._intervals.begin(), begin)
        tree.remove_envelop(end, self._intervals.end())

        return self._new_from_intervals(tree)

    def begin(self, finite=True) -> float:
        """Begin time of the temporal edges."""

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
        """End time if the temporal edges."""
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
