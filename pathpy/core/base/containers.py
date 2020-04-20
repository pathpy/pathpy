"""Modules to contain pathpy objects."""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : containers.py -- Base containers for pathpy
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Sat 2020-04-18 17:09 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import TYPE_CHECKING, Set, Dict, Union

from collections import defaultdict

from pathpy import logger

# pseudo load class for type checking
if TYPE_CHECKING:
    from pathpy.core.node import Node
    from pathpy.core.edge import Edge

# create logger for the Network class
LOG = logger(__name__)


class Properties():
    """Class to store network properties"""

    # pylint: disable=too-many-instance-attributes

    def __init__(self, directed: bool = True) -> None:
        """Initialize the NodeContainer object."""
        # initialize variables
        self._directed: bool = directed

        self._successors: defaultdict = defaultdict(set)
        self._predecessors: defaultdict = defaultdict(set)
        self._outgoing: defaultdict = defaultdict(set)
        self._incoming: defaultdict = defaultdict(set)
        self._neighbors: defaultdict = defaultdict(set)
        self._incident_edges: defaultdict = defaultdict(set)
        self._indegrees: defaultdict = defaultdict(float)
        self._outdegrees: defaultdict = defaultdict(float)
        self._degrees: defaultdict = defaultdict(float)

    @property
    def successors(self) -> defaultdict:
        """Retuns a dict with sets of successors."""
        return self._successors

    @property
    def predecessors(self) -> defaultdict:
        """Retuns a dict with sets of predecessors."""
        return self._predecessors

    @property
    def outgoing(self) -> defaultdict:
        """Retuns a dict with sets of outgoing edges."""
        return self._outgoing

    @property
    def incoming(self) -> defaultdict:
        """Retuns a dict with sets of incoming edges."""
        return self._incoming

    @property
    def neighbors(self) -> defaultdict:
        """Retuns a dict with sets of adjacent nodes."""
        return self._neighbors

    @property
    def incident_edges(self) -> defaultdict:
        """Retuns a dict with sets of adjacent edges."""
        return self._incident_edges

    @property
    def indegrees(self) -> defaultdict:
        """Retuns a dict with the number of incoming edges."""
        return self._indegrees

    @property
    def outdegrees(self) -> defaultdict:
        """Retuns a dict with the number of outgoing edges."""
        return self._outdegrees

    @property
    def degrees(self) -> defaultdict:
        """Retuns a dict with the number of incident edges."""
        return self._degrees

    def add_edge(self, edge: Edge) -> None:
        """Update properties given an new edge."""
        # create list of temproal nodes
        _nodes: list = [(edge.v, edge.w), (edge.w, edge.v)]

        for _v, _w in _nodes:
            self._successors[_v].add(_w)
            self._outgoing[_v].add(edge)
            self._predecessors[_w].add(_v)
            self._incoming[_w].add(edge)

            if self._directed:
                break

        for _v, _w in _nodes:
            self._neighbors[_v].add(_w)
            self._incident_edges[_v].add(edge)

            self._indegrees[_v] = len(self._incoming[_v])
            self._outdegrees[_v] = len(self._outgoing[_v])
            self._degrees[_v] = len(self._incident_edges[_v])

    def remove_edge(self, edge: Edge) -> None:
        """Update properties given an new edge."""
        # create list of temproal nodes
        _nodes: list = [(edge.v, edge.w), (edge.w, edge.v)]

        for _v, _w in _nodes:
            self._successors[_v].discard(_w)
            self._outgoing[_v].discard(edge)
            self._predecessors[_w].discard(_v)
            self._incoming[_w].discard(edge)

            if self._directed:
                break

        for _v, _w in _nodes:
            self._neighbors[_v].discard(_w)
            self._incident_edges[_v].discard(edge)

            self._indegrees[_v] = len(self._incoming[_v])
            self._outdegrees[_v] = len(self._outgoing[_v])
            self._degrees[_v] = len(self._incident_edges[_v])


class BaseContainer:
    """Class to store nodes"""

    def __init__(self, directed: bool = True) -> None:
        """Initialize the NodeContainer object."""
        # initialize variables
        self._set: set = set()
        self._map: dict = dict()
        self._directed: bool = directed

    def __len__(self) -> int:
        """Returns the number of nodes"""
        return len(self._set)

    def __iter__(self):
        """Iterator over the note set."""
        return self._set.__iter__()

    def __str__(self) -> str:
        """Print the NodeContainer object"""
        return self._set.__str__()

    def items(self):
        """Return a new view of the container’s items ((key, value) pairs)."""
        return self._map.items()

    def keys(self):
        """Return a new view of the container’s keys. """
        return self._map.keys()

    def values(self):
        """Return a new view of the container’s values."""
        return self._map.values()

    @property
    def uids(self) -> Set[str]:
        """Returns a set of object uids"""
        return set(self._map)


class NodeContainer(BaseContainer):
    """Class to store nodes"""

    def __init__(self, properties: Properties, directed: bool = True) -> None:
        """Initialize the NodeContainer object."""
        # initialize the base class
        super().__init__(directed=directed)
        self._properties: Properties = properties

    def __getitem__(self, key: str) -> Node:
        """Returns a node object."""
        return self._map[key]

    @property
    def dict(self) -> Dict[str, Node]:
        """Returns a dictionary of node objects."""
        return self._map

    @property
    def index(self) -> Dict[str, int]:
        """Returns a dictionary that maps object uids to  integer indices.

        The indices of nodes correspond to the row/column ordering of objects
        in any list/array/matrix representation generated by pathpy, e.g. for
        degrees.sequence or adjacency_matrix.

        Returns
        -------
        dict
            maps node uids to zero-based integer index

        """
        return dict(zip(self._map, range(len(self))))

    def add(self, node: Node) -> None:
        """Add a node to the set of nodes."""
        self._set.add(node)
        self._map[node.uid] = node

    def remove(self, node: Node) -> None:
        """Remove a node from the set of nodes."""
        self._set.discard(node)
        self._map.pop(node.uid, None)

    def contain(self, node: Node) -> bool:
        """Returns true if node is available."""
        boolean: bool
        if node not in self and node.uid not in self.uids:
            boolean = False
        else:
            boolean = True
        return boolean


class EdgeContainer(BaseContainer):
    """Class to store edges"""

    def __init__(self, properties: Properties, directed: bool = True) -> None:
        """Initialize the NodeContainer object."""
        # initialize the base class
        super().__init__(directed=directed)

        self._nodes: defaultdict = defaultdict(set)
        self._properties: Properties = properties

    def __getitem__(self, key: Union[str, tuple]) -> Union[Edge, Set[Edge]]:
        """Returns a node object."""
        edges: Union[Edge, set]
        if isinstance(key, tuple):
            try:
                _v = key[0].uid
            except AttributeError:
                _v = key[0]

            try:
                _w = key[1].uid
            except AttributeError:
                _w = key[1]

            edges = self._nodes[(_v, _w)]
        else:
            edges = self._map[key]
        return edges

    @property
    def dict(self) -> Dict[str, Edge]:
        """Returns a dictionary of edge objects."""
        return self._map

    def add(self, edge: Edge) -> None:
        """Add an edge to the set of edges."""
        self._set.add(edge)
        self._map[edge.uid] = edge
        self._nodes[(edge.v.uid, edge.w.uid)].add(edge)
        if not self._directed:
            self._nodes[(edge.w.uid, edge.v.uid)].add(edge)
        self._properties.add_edge(edge)

    def remove(self, edge: Edge) -> None:
        """Remove an edge from the set of edges."""
        self._set.discard(edge)
        self._map.pop(edge.uid, None)
        self._nodes[(edge.v.uid, edge.w.uid)].discard(edge)

        if len(self._nodes[(edge.v.uid, edge.w.uid)]) == 0:
            self._nodes.pop((edge.v.uid, edge.w.uid), None)

        if not self._directed:
            self._nodes[(edge.w.uid, edge.v.uid)].discard(edge)
            if len(self._nodes[(edge.w.uid, edge.v.uid)]) == 0:
                self._nodes.pop((edge.w.uid, edge.v.uid), None)

        self._properties.remove_edge(edge)

    def contain(self, edge: Edge) -> bool:
        """Returns true if edge is available."""
        boolean: bool
        if edge not in self and edge.uid not in self.uids:
            boolean = False
        else:
            boolean = True
        return boolean


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
