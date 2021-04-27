"""Algorithms to compute paths in temporal networks."""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : path_extraction.py -- Algorithms to compute paths in temporal networks
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Tue 2021-04-26 18:28 ingo>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================

from __future__ import annotations
from typing import Any, List, Union, Optional
from functools import singledispatch
from collections import defaultdict, deque

from pathpy import logger

from pathpy.core.api import NodeCollection
from pathpy.core.api import EdgeCollection
from pathpy.core.api import PathCollection

from pathpy.models.models import (ABCDirectedAcyclicGraph,
                                  ABCTemporalNetwork)

# create logger
LOG = logger(__name__)


@singledispatch
def to_path_collection(self, **kwargs: Any) -> PathCollection:
    """Converts object to path collection"""
    raise NotImplementedError


@to_path_collection.register(ABCDirectedAcyclicGraph)
def _dag(self, **kwargs):
    """Convert a DAG to paths."""

    # check if dag is acyclic
    if self.acyclic is None:
        self.topological_sorting()

    if not self.acyclic:
        LOG.error('Cannot extract statistics from a cyclic graph')
        raise ValueError

    paths = PathCollection(edges=self.edges.copy())

    for root in self.roots:
        paths = self.routes_from(root, paths)

    return paths


@to_path_collection.register(ABCTemporalNetwork)
def _temp(self, **kwargs):
    """Convert a temporal network to paths."""
    from pathpy.models.directed_acyclic_graph import DirectedAcyclicGraph

    #paths = PathCollection(edges=self.edges.copy())
    paths = PathCollection()

    delta = kwargs.get('delta', 1)
    # generate a single time-unfolded DAG
    dag = DirectedAcyclicGraph.from_temporal_network(self, delta=delta)

    for root in dag.roots:
        causal_tree = _causal_tree(dag, root)

        _paths = causal_tree.to_paths()

        for path in _paths:
            edges = [e['original'] for e in path.edges]
            if edges not in paths:
                paths.add(*edges, frequency=1)
            else:
                paths[edges]['frequency'] += 1
    return paths


def _causal_tree(dag, root):
    """Generate a causal tree"""
    LOG.debug('Generate causal tree for root: %s', root.uid)
    from pathpy.models.directed_acyclic_graph import DirectedAcyclicGraph

    tree = DirectedAcyclicGraph()
    node_map = {}
    edge_map = {}
    visited = defaultdict(lambda: False)
    queue = deque()

    # launch breadth-first-search at root of tree
    # root nodes are necessarily at depth 0
    queue.append((root, 0))
    edges = []

    while queue:
        # take out left-most element from FIFO queue
        v, depth = queue.popleft()

        # x is the node ID of the node in the causal tree
        # the second component captures the distance from
        # the root of the causal tree. These IDs ensure
        # that the same physical nodes can occur at different
        # distances from the root
        x = '{0}_{1}'.format(v['original'].uid, depth)
        node_map[x] = v['original']

        # process nodes at next level
        for w in dag.successors[v.uid]:

            if (w, depth+1) not in queue:
                queue.append((w, depth+1))
                # only consider nodes that have not already
                # been added to this level

                if not visited[w['original'].uid, depth+1]:
                    # add edge to causal tree
                    y = '{0}_{1}'.format(w['original'].uid, depth+1)
                    edges.append((x, y))

                    visited[w['original'].uid, depth+1] = True
                    node_map[y] = w['original']
                    edge_map[(x, y)] = dag.edges[v, w]['original']

    for x, y in edges:
        if x not in tree.nodes:
            tree.add_node(x, original=node_map[x])
        if y not in tree.nodes:
            tree.add_node(y, original=node_map[y])
        tree.add_edge(x, y, original=edge_map[(x, y)])

    return tree