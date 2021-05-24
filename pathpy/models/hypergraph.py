"""Hypergraph class"""
# pylint: disable=too-many-lines
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : hypergraph.py -- Base class for a hypergraph
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Mon 2021-05-24 12:07 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, Optional, Union, Dict, Set, cast
from collections import defaultdict

from pathpy import logger
from pathpy.models.classes import BaseHyperGraph
from pathpy.core.node import Node, NodeCollection
from pathpy.core.hyperedge import HyperEdge, HyperEdgeCollection

# create custom types
Weight = Union[str, bool, None]

# create logger for the Network class
LOG = logger(__name__)


class HyperGraph(BaseHyperGraph):
    """Class for a hypergraph."""
    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-many-public-methods

    def __init__(self, uid: Optional[str] = None,
                 multiedges: bool = False, **kwargs: Any) -> None:
        """Initialize the hypergraph object."""

        # initialize the base class
        super().__init__(uid=uid, **kwargs)

        # indicator whether the network has multi-edges
        self._multiedges: bool = multiedges

        # # a container for the network properties
        self._properties: defaultdict = defaultdict()

        # a container for node objects
        self._nodes: NodeCollection = NodeCollection()

        # a container for edge objects
        self._edges: HyperEdgeCollection = HyperEdgeCollection(
            multiedges=multiedges,
            nodes=self._nodes)

        # add network properties
        self._properties['edges'] = set()
        self._properties['incident_edges'] = defaultdict(set)
        self._properties['degrees'] = defaultdict(float)

    def __str__(self) -> str:
        """Print the summary of the hypergraph. """
        return self.summary()

    @property
    def uid(self) -> str:
        """Returns the unique id of the hypergraph."""
        return super().uid

    def __add__(self, other: HyperGraph) -> HyperGraph:
        """Add a hypergraph to a hypergraph."""
        raise NotImplementedError

    def __sub__(self, other: HyperGraph) -> HyperGraph:
        """Remove a hypergraph from a hypergraph."""
        raise NotImplementedError

    def __iadd__(self, other: HyperGraph) -> HyperGraph:
        """Add a hypergraph to it self."""
        raise NotImplementedError

    def __isub__(self, other: HyperGraph) -> HyperGraph:
        """Remove a hypergraph."""
        raise NotImplementedError

    @property
    def multiedges(self) -> bool:
        """Return if edges are directed. """
        return self._multiedges

    @property
    def nodes(self) -> NodeCollection:
        """Return the associated nodes of the hypergraph. """
        return self._nodes

    @property
    def edges(self) -> HyperEdgeCollection:
        """Return the associated edges of the hypergraph. """
        return self._edges

    @property
    def incident_edges(self) -> Dict[str, Set[HyperEdge]]:
        """Retuns a dict with sets of adjacent edges."""
        return {n: self._properties['incident_edges'][n] for n in self.nodes.keys()}

    def _degrees(self, _dict: defaultdict,
                 weight: Weight = None) -> Dict[str, float]:
        """Helper function to calculate the degrees."""
        _degrees: dict = {}
        if weight is None:
            _degrees = {node: _dict[node] for node in self.nodes.keys()}
        else:
            for node in self.nodes.keys():
                _degrees[node] = sum([self.edges[e].weight(weight)
                                      for e in _dict[node]])
        return _degrees

    def degrees(self, weight: Weight = None) -> Dict[str, float]:
        """Retuns a dict with degrees of the nodes."""
        if weight is None:
            _d = self._degrees(self._properties['degrees'], weight)
        else:
            _d = self._degrees(self._properties['incident_edges'], weight)
        return _d

    def summary(self) -> str:
        """Returns a summary of the hypergraph. """
        summary = [
            'Uid:\t\t\t{}\n'.format(self.uid),
            'Type:\t\t\t{}\n'.format(self.__class__.__name__),
            'Multi-Edges:\t\t{}\n'.format(str(self.multiedges)),
            'Number of nodes:\t{}\n'.format(self.number_of_nodes()),
            'Number of edges:\t{}'.format(self.number_of_edges()),
        ]
        attr = self.attributes
        if len(attr) > 0:
            summary.append('\n\nNetwork attributes\n')
            summary.append('------------------\n')
        for key, value in attr.items():
            summary.append('{}:\t{}\n'.format(key, value))

        return ''.join(summary)

    def number_of_nodes(self) -> int:
        """Return the number of nodes in the hypergraph. """
        # if unique:
        return len(self.nodes)

    def number_of_edges(self) -> int:
        """Return the number of edges in the hypergraph. """
        # if unique:
        return len(self.edges)

    def add_node(self, *node: Union[str, Node], **kwargs: Any) -> None:
        """Add a single node to the hypergraph. """
        self.nodes.add(*node, **kwargs)
        self._add_node_properties()

    def add_edge(self, *edge: Union[str, tuple, list, Node, HyperEdge],
                 uid: Optional[str] = None, **kwargs: Any) -> None:
        """Add a single edge to the hypergraph. """
        self.edges.add(*edge, uid=uid, **kwargs)
        self._add_edge_properties()

    def add_nodes(self, *nodes: Union[str, Node],
                  **kwargs: Any) -> None:
        """Add multiple nodes from a list to the hypergraph. """
        for node in nodes:
            self.nodes.add(node, **kwargs)
        self._add_node_properties()

    def add_edges(self, *edges: Union[str, tuple, list, Node, HyperEdge],
                  **kwargs: Any) -> None:
        """Add multiple edges from a list to the hypergraph. """

        uid: Optional[str] = kwargs.pop('uid', None)
        nodes: bool = kwargs.pop('nodes', True)

        if all(isinstance(arg, (str, Node)) for arg in edges) and nodes:
            edges = tuple(cast(Union[str, Node], edge)
                          for edge in zip(edges[:-1], edges[1:]))

        if isinstance(edges[0], list) and len(edges) == 1:
            edges = tuple(edges[0])

        if not edges:
            LOG.warning('No edge was added!')

        for edge in edges:
            self.add_edge(edge, uid=uid, nodes=nodes, **kwargs)

    def remove_node(self, node: Union[str, Node]) -> None:
        """Remove a single node from the hypergraph. """
        if node in self.nodes:
            for _edge in list(self.incident_edges[self.nodes[node].uid]):
                self.remove_edge(_edge)
        self.nodes.remove(node)
        self._remove_node_properties()

    def remove_edge(self, *edge: Union[str, tuple, Node, HyperEdge],
                    uid: Optional[str] = None) -> None:
        """Remove a single edge from the hypergraph. """
        self.edges.remove(*edge, uid=uid)
        self._remove_edge_properties()

    def remove_edges(self, *edges: Union[str, tuple, list, Node, HyperEdge]) -> None:
        """Remove multiple edges from the hypergraph."""
        self.edges.remove(*edges)
        self._remove_edge_properties()

    def remove_nodes(self, *nodes: Union[str, Node]) -> None:
        """Remove multiple nodes from the network."""
        for node in nodes:
            self.remove_node(node)

    def _add_node_properties(self):
        """Helper function to update node properties."""

    def _remove_node_properties(self):
        """Helper function to update node properties."""

    def _add_edge_properties(self):
        """Helper function to update network properties."""

        edges = set(self.edges.values()).difference(self._properties['edges'])

        for edge in edges:
            relations = edge.relations
            uid = edge.uid

            for node in relations:
                self._properties['incident_edges'][node].add(uid)
                self._properties['degrees'][node] = len(
                    self._properties['incident_edges'][node])

            for uid, node in edge.nodes.items():
                if node is None and uid in self._nodes:
                    self.nodes[uid] = self.nodes[uid]
                elif uid not in self.nodes and node is None:
                    self.nodes.add(uid, uid=uid)
                elif uid not in self.nodes and node is not None:
                    self.nodes.add(node)

            self._properties['edges'].add(edge)

    def _remove_edge_properties(self):
        """Helper function to update network properties."""

        edges = self._properties['edges'].difference(set(self.edges.values()))

        for edge in edges:
            relations = edge.relations
            uid = edge.uid

            for node in relations:
                self._properties['incident_edges'][node].discard(uid)
                self._properties['degrees'][node] = len(
                    self._properties['incident_edges'][node])

            self._properties['edges'].discard(edge)

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
