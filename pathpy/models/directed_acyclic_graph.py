""""Directed Acyclic Graph class"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : directed_acyclic_graph.py -- Network model for a DAG
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Wed 2021-05-19 11:30 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations
from pathpy.models.temporal_network import TemporalNode, TemporalEdge
from typing import Any, Optional, Set
from collections import defaultdict

from numpy import inf

from pathpy import logger
from pathpy.core.node import NodeCollectionfrom pathpy.core.edge import EdgeCollection
from pathpy.core.path import PathCollection
from pathpy.models.network import Network

from pathpy.algorithms import path_extraction

from pathpy.models.models import ABCDirectedAcyclicGraph

# create logger
LOG = logger(__name__)


class DirectedAcyclicGraph(ABCDirectedAcyclicGraph, Network):
    """Base class for a directed acyclic graph."""

    # load external functions to the network
    to_paths = path_extraction.extract_path_collection  # type: ignore

    def __init__(self, uid: Optional[str] = None, multiedges: bool = False,
                 **kwargs: Any) -> None:
        """Initialize the directed acyclic graph."""

        # initialize the base class
        super().__init__(uid=uid, directed=True, multiedges=multiedges, **kwargs)

        # property for acyclic
        self._acyclic: Optional[bool] = None

        # add network properties
        self._properties['nodes'] = set()
        self._properties['roots'] = set()
        self._properties['leafs'] = set()

        # properties for topological sorting
        self._topsort = {'sorting': [], 'parent': {}, 'start': {}, 'end': {},
                         'class': {}, 'count': 0}

    @property
    def roots(self) -> Set[Node]:
        """Returns the roots as a set of nodes."""
        return self._properties['roots']

    @property
    def leafs(self) -> Set[Node]:
        """Returns the leafs as a set of nodes."""
        return self._properties['leafs']

    @property
    def acyclic(self) -> Optional[bool]:
        """Returns if the graph is acyclic or None if 
        this is currently unknown. Call topological_sorting
        on the network to calculate this property."""
        return self._acyclic

    def _add_node_properties(self):
        """Helper function to update node properties."""

        nodes = set(self.nodes).difference(self._properties['nodes'])

        for node in nodes:
            self._properties['roots'].add(node)
            self._properties['leafs'].add(node)

            self._properties['nodes'].add(node)

    def _remove_node_properties(self):
        """Helper function to update node properties."""

        nodes = set(self.nodes).difference(self._properties['nodes'])

        for node in nodes:
            self._properties['roots'].discard(node)
            self._properties['leafs'].discard(node)

            self._properties['nodes'].discard(node)

    def _add_edge_properties(self):
        """Helper function to update network properties."""

        edges = set(self.edges).difference(self._properties['edges'])

        for edge in edges:
            _nodes: list = [(edge.v, edge.w), (edge.w, edge.v)]

            for _v, _w in _nodes:
                self._properties['successors'][_v].add(_w)
                self._properties['outgoing'][_v].add(edge)
                self._properties['predecessors'][_w].add(_v)
                self._properties['incoming'][_w].add(edge)

                if _v not in self._properties['nodes']:
                    self._properties['roots'].add(_v)

                if _w not in self._properties['nodes']:
                    self._properties['leafs'].add(_w)

                self._properties['roots'].discard(_w)
                self._properties['leafs'].discard(_v)
                self._acyclic = None

                self._properties['nodes'].add(_v)
                self._properties['nodes'].add(_w)
                if self.directed:
                    break

            for _v, _w in _nodes:
                self._properties['neighbors'][_v].add(_w)
                self._properties['incident_edges'][_v].add(edge)

                self._properties['indegrees'][_v] = len(
                    self._properties['incoming'][_v])
                self._properties['outdegrees'][_v] = len(
                    self._properties['outgoing'][_v])
                self._properties['degrees'][_v] = len(
                    self._properties['incident_edges'][_v])

            self._properties['edges'].add(edge)

    def _remove_edge_properties(self):
        """Helper function to update network properties."""

        edges = self._properties['edges'].difference(set(self.edges))

        for edge in edges:
            _nodes: list = [(edge.v, edge.w), (edge.w, edge.v)]

            for _v, _w in _nodes:
                # print(_v.uid, _w.uid)
                self._properties['successors'][_v].discard(_w)
                self._properties['outgoing'][_v].discard(edge)
                self._properties['predecessors'][_w].discard(_v)
                self._properties['incoming'][_w].discard(edge)

                if not self._properties['predecessors'][_w]:
                    self._properties['roots'].add(_w)

                if not self._properties['successors'][_v]:
                    self._properties['leafs'].add(_v)

                if self.directed:
                    break

            for _v, _w in _nodes:
                self._properties['neighbors'][_v].discard(_w)
                self._properties['incident_edges'][_v].discard(edge)

                self._properties['indegrees'][_v] = len(
                    self._properties['incoming'][_v])
                self._properties['outdegrees'][_v] = len(
                    self._properties['outgoing'][_v])
                self._properties['degrees'][_v] = len(
                    self._properties['incident_edges'][_v])

            self._properties['edges'].discard(edge)

    def summary(self) -> str:
        """Returns a summary of the dag."""
        summary = [
            'Uid:\t\t\t{}\n'.format(self.uid),
            'Type:\t\t\t{}\n'.format(self.__class__.__name__),
            # 'Directed:\t\t{}\n'.format(str(self.directed)),
            'Acyclic:\t\t{}\n'.format(str(self.acyclic)),
            'Multi-Edges:\t\t{}\n'.format(str(self.multiedges)),
            'Number of nodes:\t{}\n'.format(self.number_of_nodes()),
            'Number of edges:\t{}\n'.format(self.number_of_edges()),
            'Number of roots:\t{}\n'.format(len(self.roots)),
            'Number of leafs:\t{}'.format(len(self.leafs)),
        ]
        attr = self.attributes
        if len(attr) > 0:
            summary.append('\n\nNetwork attributes\n')
            summary.append('------------------\n')
        for k, v in attr.items():
            summary.append('{}:\t{}\n'.format(k, v))

        return ''.join(summary)

    def topological_sorting(self):
        """ Topological sorting of the graph.

        Performs a topological sorting of the graph, classifying
        all edges as (1) tree, (2) forward, (3) back or (4) cross
        edges in the process.

        see Cormen 2001 for details
        """

        # reset topsort properties
        # properties for topological sorting
        self._topsort = {'sorting': [], 'parent': {}, 'start': {}, 'end': {},
                         'class': {}, 'count': 0}

        # asumption that the dag is acyclic
        self._acyclic = True

        for node in self.nodes.values():
            if node not in self._topsort['parent']:
                self._dfs_visit(node)
        self._topsort['sorting'].reverse()

    def _dfs_visit(self, node, parent=None):
        """Recursively visits nodes in the graph.

        Classifying edges as (1) tree, (2) forward, (3) back or (4) cross edges.

        """
        _v = node
        self._topsort['parent'][_v] = parent
        self._topsort['count'] += 1
        self._topsort['start'][_v] = self._topsort['count']

        if parent:
            self._topsort['class'][(parent, _v)] = 'tree'

        for _w in self.successors[_v.uid]:

            if _w not in self._topsort['parent']:
                self._dfs_visit(_w, _v)

            elif _w not in self._topsort['end']:
                self._topsort['class'][(_v, _w)] = 'back'
                self._acyclic = False

            elif self._topsort['start'][_v] < self._topsort['start'][_w]:
                self._topsort['class'][(_v, _w)] = 'forward'

            else:
                self._topsort['class'][(_v, _w)] = 'cross'

        self._topsort['count'] += 1
        self._topsort['end'][_v] = self._topsort['count']
        self._topsort['sorting'].append(_v)

    def routes_from(self, node, paths):
        """Constructs all paths from node v to any leaf nodes."""

        # TODO: allow also multiedges
        if self.multiedges:
            raise NotImplementedError

        # Collect temporary paths, indexed by the target node
        _paths = defaultdict(list)
        _paths[node] = [[node]]

        # set of unprocessed nodes
        queue = {node}

        while queue:
            # take one unprocessed node
            x = queue.pop()

            # successors of x expand all temporary
            # paths, currently ending in x
            if self.successors[x.uid]:
                for w in self.successors[x.uid]:
                    for p in _paths[x]:
                        _paths[w].append(p + [w])
                    queue.add(w)
                del _paths[x]

        for _p in _paths.values():
            for nodes in _p:
                if len(nodes) == 1:
                    paths.add(nodes[0], frequency=1)
                else:
                    edges = [self.edges[(v, w)]
                             for v, w in zip(nodes[:-1], nodes[1:])]
                    paths.add(*edges, frequency=1)

        return paths

    @classmethod
    def from_temporal_network(cls, temporal_network, **kwargs: Any):
        """Creates a time-unfolded directed acyclic graph representation of 
        the temporal network.
        """

        delta: float = kwargs.get('delta', 1)

        dag = cls()

        # dictionary that maps time-unfolded nodes to actual nodes
        node_map = {}

        i = 0
        for begin, end, uid in temporal_network.tedges:
            edge: TemporalEdge = temporal_network.edges[uid]
            v: TemporalNode = edge.v
            w: TemporalNode = edge.w

            if delta < inf:
                current_delta = int(delta)
            else:
                current_delta = temporal_network.end()-begin

            # create time-unfolded nodes v_t and w_{t+1}
            v_t = "{0}_{1}".format(v.uid, begin)
            #node_map[v_t] = edge.v.uid

            # create one time-unfolded link for all delta in [1, delta]
            # this implies that for delta = 2 and an edge (a,b,1) two
            # time-unfolded links (a_1, b_2) and (a_1, b_3) will be created
            for x in range(1, int(current_delta)+1):
                w_t = "{0}_{1}".format(w.uid, begin+x)
                #node_map[w_t] = edge.w.uid
                if v_t not in dag.nodes:
                    dag.nodes._add(Node(v_t, original=v))
                    #dag.add_node(v_t, original=edge.v)
                if w_t not in dag.nodes:
                    dag.nodes._add(Node(w_t, original=w))
                    #dag.add_node(w_t, original=edge.w)

                e = Edge(dag.nodes[v_t], dag.nodes[w_t], original=edge)
                dag.edges._add(e)
        dag._add_edge_properties()
        #dag.add_edge(v_t, w_t , original=edge)

        return dag


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
