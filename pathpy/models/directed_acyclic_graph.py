""""Directed Acyclic Graph class"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : directed_acyclic_graph.py -- Network model for a DAG
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Fri 2021-06-04 14:21 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations
from pathpy.models.temporal_network import TemporalNode, TemporalEdge
from typing import Any, Optional, Set
from collections import defaultdict

from numpy import inf

from pathpy import logger
from pathpy.utils.errors import ParameterError
from pathpy.core.path import PathCollection
from pathpy.core.api import Node
from pathpy.models.network import Network

from pathpy.algorithms import path_extraction

from pathpy.models.models import ABCDirectedAcyclicGraph

# create logger
LOG = logger(__name__)


class DirectedAcyclicGraph(ABCDirectedAcyclicGraph, Network):
    """Base class for a directed acyclic graph."""

    # load external functions to the network
    to_paths = path_extraction.all_paths_from_dag  # type: ignore

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

    def _add_edge_properties(self, *args):
        """Helper function to update network properties."""

        edges = set(self.edges).difference(self._properties['edges'])

        for edge in edges:

            # update nodes in the network
            for uid, node in edge.nodes.items():
                if uid not in self.nodes.keys():
                    self.nodes.add(node)

            # get node objects
            node_v, node_w = self.nodes[edge.v.uid], self.nodes[edge.w.uid]
            uid = edge.uid

            _nodes: list = [(node_v, node_w), (node_w, node_v)]

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

    def _remove_edge_properties(self, *args):
        """Helper function to update network properties."""

        edges = self._properties['edges'].difference(set(self.edges))

        for edge in edges:
            # get node objects
            node_v, node_w = self.nodes[edge.v.uid], self.nodes[edge.w.uid]
            uid = edge.uid

            _nodes: list = [(node_v, node_w), (node_w, node_v)]

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

    def routes_from(self, v, node_mapping=None) -> PathCollection:
        """
        Constructs all paths from node v to any leaf nodes

        Parameters
        ----------
        v:  str
            uid of node from which to start
        node_mapping: dict
            an optional mapping from node to a different set.

        Returns
        -------
        list
            a list of lists, where each list contains one path from the source
            node v until a leaf node is reached
        """

        if node_mapping is None:
            node_mapping = {w.uid: w.uid for w in self.nodes}

        paths = PathCollection()

        # Collect temporary paths, indexed by the target node
        temp_paths = defaultdict(list)
        temp_paths[v] = [[v]]

        # set of unprocessed nodes
        queue = {v}
        # print('Queue = ', queue)

        while queue:
            # take one unprocessed node
            x = queue.pop()
            # print('Dequeued ', x)
            # successors of x expand all temporary
            # paths, currently ending in x
            if len(self.successors[x]) > 0:
                for w in self.successors[x]:                    
                    for p in temp_paths[x]:
                        temp_paths[w.uid].append(p + [w.uid])
                    # print('Adding ', w.uid)
                    queue.add(w.uid)
                del temp_paths[x]
            #print('Queue = ', queue)

        # flatten list
        for possible_paths in temp_paths.values():
            for path in possible_paths:
                if node_mapping:
                    path = [node_mapping[k] for k in path]
                paths.add(path, count=1, uid='-'.join(path))

        return paths

    @classmethod
    def from_temporal_network(cls, temporal_network, delta=1):
        """Creates a time-unfolded directed acyclic graph representation of 
        a temporal network with instantaneous edges.
        """

        dag = cls()

        # dictionary that maps time-unfolded nodes to actual nodes
        node_map = {}

        i = 0
        for edge in temporal_network.edges[:]:
            v: TemporalNode = edge.v
            w: TemporalNode = edge.w

            if edge.end - edge.start != 1:
                raise ParameterError(
                    'Directed acyclic graphs can only be generated for temporal networks with instantaneous edges (i.e. with duration of 1 discrete time step).')

            if delta < inf:
                current_delta = int(delta)
            else:
                current_delta = temporal_network.end-edge.start

            v_t = "{0}_{1}".format(v.uid, edge.start)

            # create one time-unfolded link for all delta in [1, delta]
            # this implies that for delta = 2 and an edge (a,b,1) two
            # time-unfolded links (a_1, b_2) and (a_1, b_3) will be created
            for x in range(1, int(current_delta)+1):
                w_t = "{0}_{1}".format(w.uid, edge.start+x)
                #node_map[w_t] = edge.w.uid
                if v_t not in dag.nodes:
                    dag.add_node(v_t, original=v)
                if w_t not in dag.nodes:
                    dag.add_node(w_t, original=w)
                dag.add_edge(v_t, w_t, original=edge)

            if not temporal_network.directed:
                # add reverse edge for undirected edge
                v_t = "{0}_{1}".format(w.uid, edge.start)

                for x in range(1, int(current_delta)+1):
                    w_t = "{0}_{1}".format(v.uid, edge.start+x)
                    #node_map[w_t] = edge.w.uid
                    if w_t not in dag.nodes:
                        dag.add_node(w_t, original=v)
                    if v_t not in dag.nodes:
                        dag.add_node(v_t, original=w)
                    dag.add_edge(v_t, w_t, original=edge)
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
