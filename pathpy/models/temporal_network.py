"""Temporal network class"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : temporal_network.py -- Class for temporal networks
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Fri 2021-05-28 18:59 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, Optional, Union
from collections import defaultdict
from singledispatchmethod import singledispatchmethod  # NOTE: not needed at 3.9

import pandas as pd
from intervaltree import IntervalTree

from pathpy import logger
from pathpy.core.core import PathPyObject
from pathpy.core.temporal import TemporalPathPyObject, _get_start_end

from pathpy.core.node import Node, NodeCollection
from pathpy.core.edge import Edge, EdgeCollection
from pathpy.models.network import Network

# from pathpy.core.base.attributes import TemporalAttributes

from pathpy.models.classes import BaseTemporalNetwork

# # pseudo load class for type checking
# if TYPE_CHECKING:
#     from pathpy.core.edge import EdgeSet


# create logger for the Network class
LOG = logger(__name__)


class TemporalNode(Node, TemporalPathPyObject):
    """Base class of a temporal node."""

    def __init__(self, *node: Union[str, PathPyObject],
                 uid: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize the node object."""

        # initializing the parent classes
        kwargs.pop('directed', None)
        Node.__init__(self, *node, uid=uid, **kwargs)
        TemporalPathPyObject.__init__(self, uid=self.uid, **kwargs)

    def summary(self) -> str:
        """Object summary. """
        summary = [
            'Observation periode:\t{} - {}'.format(self.start, self.end)
        ]

        return super().summary() + ''.join(summary)


class TemporalEdge(Edge, TemporalPathPyObject):
    """Base class of an temporal edge."""

    def __init__(self, v: Union[str, PathPyObject],
                 w: Union[str, PathPyObject],
                 uid: Optional[str] = None,
                 directed: bool = True,
                 **kwargs: Any) -> None:
        """Initialize the node object."""

        # initialize the parent class
        Edge.__init__(self, v, w, uid=uid, directed=directed, **kwargs)
        TemporalPathPyObject.__init__(self, uid=self.uid, **kwargs)

    def summary(self) -> str:
        """Object summary. """
        summary = [
            'Observation periode:\t{} - {}'.format(self.start, self.end)
        ]

        return super().summary() + ''.join(summary)


class TemporalNodeCollection(NodeCollection):
    """A collection of temporal nodes"""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the NodeCollection object."""

        # initialize the base class
        super().__init__(*args, **kwargs)

        # initialize an intervaltree to save events
        self._events = IntervalTree()

        # class of objects
        self._default_class: Any = TemporalNode

    @singledispatchmethod
    def __getitem__(self, key: Any) -> Any:
        return super().__getitem__(key)

    @__getitem__.register(slice)  # type: ignore
    @__getitem__.register(int)  # type: ignore
    @__getitem__.register(float)  # type: ignore
    def _(self, key: Union[int, float, slice]) -> Any:
        # pylint: disable=arguments-differ
        start, end, _ = _get_start_end(key)
        for start, end, uid in sorted(self._events[start:end]):
            for obj in self[uid][start:end]:
                yield obj

    @property
    def start(self):
        """start of the object"""
        return self._events.begin()

    @property
    def end(self):
        """end of the object"""
        return self._events.end()

    @property
    def events(self):
        """Temporal events"""
        return self._events

    @singledispatchmethod
    def add(self, *args, **kwargs: Any) -> None:
        """Add multiple nodes. """
        super().add(*args, **kwargs)

    def _add(self, obj: Any, **kwargs: Any) -> None:
        """Add an node to the set of nodes."""
        super()._add(obj, **kwargs)
        start, end, _ = obj.last()
        self._events[start:end] = obj.uid

    def _if_exist(self, obj: Any, **kwargs: Any) -> None:
        """Helper function if node already exists."""
        element = self[obj.relations]
        element.event(**kwargs)
        start, end, _ = obj.last()
        self._events[start:end] = element.uid

    def _remove(self, obj) -> None:
        """Add an edge to the set of edges."""
        for interval in sorted(self._events):
            if interval.data == obj.uid:
                self._events.remove(interval)
        super()._remove(obj)


class TemporalEdgeCollection(EdgeCollection):
    """A collection of temporal edges"""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the EdgeCollection object."""

        # initialize the base class
        super().__init__(*args, **kwargs)

        # indicator whether the network has multi-edges
        self._multiple: bool = kwargs.pop('multiedges', False)

        # initialize an intervaltree to save events
        self._events = IntervalTree()

        # class of objects
        self._default_class: Any = TemporalEdge

    @singledispatchmethod
    def __getitem__(self, key: Any) -> Any:
        return super().__getitem__(key)

    @__getitem__.register(slice)  # type: ignore
    @__getitem__.register(int)  # type: ignore
    @__getitem__.register(float)  # type: ignore
    def _(self, key: Union[int, float, slice]) -> Any:
        # pylint: disable=arguments-differ
        start, end, _ = _get_start_end(key)
        for start, end, uid in sorted(self._events[start:end]):
            for obj in self[uid][start:end]:
                yield obj

    @property
    def start(self):
        """start of the object"""
        return self._events.begin()

    @property
    def end(self):
        """end of the object"""
        return self._events.end()

    @property
    def events(self):
        """Temporal events"""
        return self._events

    @singledispatchmethod
    def add(self, *args, **kwargs: Any) -> None:
        """Add multiple nodes. """
        super().add(*args, **kwargs)

    def _add(self, obj: Any, **kwargs: Any) -> None:
        """Add an edge to the set of edges."""
        super()._add(obj, **kwargs)
        start, end, _ = obj.last()
        self._events[start:end] = obj.uid

    def _if_exist(self, obj: Any, **kwargs: Any) -> None:
        """Helper function if node already exists."""
        element = self[obj.relations]
        element.event(**kwargs)
        start, end, _ = obj.last()
        self._events[start:end] = element.uid

    def _remove(self, obj) -> None:
        """Add an edge to the set of edges."""
        for interval in sorted(self._events):
            if interval.data == obj.uid:
                self._events.remove(interval)
        super()._remove(obj)


class TemporalNetwork(BaseTemporalNetwork, Network):
    """Base class for a temporal networks."""

    def __init__(self, uid: Optional[str] = None, directed: bool = True,
                 multiedges: bool = False, **kwargs: Any) -> None:
        """Initialize the temporal network object."""

        # initialize the base class
        super().__init__(uid=uid, directed=directed,
                         multiedges=multiedges, **kwargs)

        # a container for node objects
        self._nodes: TemporalNodeCollection = TemporalNodeCollection()

        # a container for edge objects
        self._edges: TemporalEdgeCollection = TemporalEdgeCollection(
            directed=directed, multiedges=multiedges)

    @property
    def nodes(self) -> TemporalNodeCollection:
        """Return the associated nodes of the network."""
        return self._nodes

    @property
    def edges(self) -> TemporalEdgeCollection:
        """Return the associated edges of the network."""
        return self._edges

    @property
    def start(self):
        """start of the object"""
        node = self.nodes.start
        edge = self.edges.start
        if isinstance(node, pd.Timestamp) and isinstance(edge, pd.Timestamp):
            return min(node, edge)
        elif isinstance(node, pd.Timestamp):
            return node
        elif isinstance(edge, pd.Timestamp):
            return edge

        _min = min(self.nodes.start, self.edges.start)
        _max = max(self.nodes.start, self.edges.start)
        return _min if _min > float('-inf') else _max

    @property
    def end(self):
        """end of the object"""
        node = self.nodes.end
        edge = self.edges.end
        if isinstance(node, pd.Timestamp) and isinstance(edge, pd.Timestamp):
            return max(node, edge)
        elif isinstance(node, pd.Timestamp):
            return node
        elif isinstance(edge, pd.Timestamp):
            return edge

        _min = min(self.nodes.end, self.edges.end)
        _max = max(self.nodes.end, self.edges.end)
        return _max if _max < float('inf') else _min

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

        summary = [
            'Uid:\t\t\t{}\n'.format(self.uid),
            'Type:\t\t\t{}\n'.format(self.__class__.__name__),
            'Directed:\t\t{}\n'.format(str(self.directed)),
            'Multi-Edges:\t\t{}\n'.format(str(self.multiedges)),
            'Number of unique nodes:\t{}\n'.format(self.number_of_nodes()),
            'Number of unique edges:\t{}\n'.format(self.number_of_edges()),
            'Number of temp nodes:\t{}\n'.format(len(self.nodes.events)),
            'Number of temp edges:\t{}\n'.format(len(self.edges.events)),
            'Observation periode:\t{} - {}\n'.format(self.start, self.end),
            'Observation time:\t{}'.format(self.end - self.start)
        ]
        attr = self.attributes
        if len(attr) > 0:
            summary.append('\n\nNetwork attributes\n')
            summary.append('------------------\n')
        for key, value in attr.items():
            summary.append('{}:\t{}\n'.format(key, value))

        return ''.join(summary)

    def to_continuous_time(self, sampling_period: int) -> TemporalNetwork:
        """
        Returns a temporal network with start/end/duration information
        on temporal edges.
        """
        tn = TemporalNetwork(directed=self.directed,
                             multiedges=self.multiedges, **self.attributes)

        # collect all activities for edges
        edge_activities = defaultdict(list)
        for e in self.edges[:]:
            edge_activities[e].append((e.start, e.end))

        for e in edge_activities:
            # find all activity intervals for this edge
            current_interval = None
            for start, _ in edge_activities[e]:
                if current_interval is None:
                    current_interval = [start, start+sampling_period]
                # expand current activity interval
                elif start == current_interval[1]:
                    current_interval[1] += sampling_period
                else:  # conclude current activity interval
                    tn.add_edge(
                        e.v.uid, e.w.uid, start=current_interval[0], end=current_interval[1])
                    current_interval = [start, start+sampling_period]
            # flush current activity
            if current_interval is not None:
                tn.add_edge(e.v.uid, e.w.uid,
                            start=current_interval[0], end=current_interval[1])
        return tn

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
