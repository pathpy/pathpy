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
from pathpy.models.classes import BaseTemporalNetwork
from pathpy.models.models import ABCDirectedAcyclicGraph

# create logger
LOG = logger(__name__)

@singledispatch
def extract_path_collection(self, **kwargs: Any) -> PathCollection:
    raise NotImplementedError

@extract_path_collection.register(ABCDirectedAcyclicGraph)
def _dag_paths(self, **kwargs):
    """Calculates path statistics from a directed acyclic graph
    """

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


@extract_path_collection.register(BaseTemporalNetwork)
def _temporal_paths(self, **kwargs):
    """Convert a temporal network to paths."""
    from pathpy.models.directed_acyclic_graph import DirectedAcyclicGraph

    #paths = PathCollection(edges=self.edges.copy())
    paths = PathCollection()

    delta : float = kwargs.get('delta', 1)

    # generate a single time-unfolded DAG
    dag = DirectedAcyclicGraph.from_temporal_network(self, delta=delta)

    # extract causal tree for each root node
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
    """ Generates a causal tree in a DAG, starting from a 
    given root node
    """
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


    
def PaCo(
    tn: BaseTemporalNetwork,
    delta: float,
    skip_first: int = 0,
    up_to_k: int = 10 ) -> PathCollection:
    """
    Path counting algorithm PaCo.
    Published at TempWeb 2021 workshop.
    in: 
        tn : BaseTemporalNetwork,
            temporal network in which we count paths.

        delta : float
            maximal time difference that between two links that can form a path.  
        
        skip_first = 0 : int,
            paths computed in the first `skip_first' temporal links are not counted towards the total path count. This feature is for parallel computing.

        up_to_k = 10 : int
            maximal lengt of paths that we count.
    """
    # all the entries that are at max distance delta away from the current entry
    delta_window = []

    path_stack = PathCollection()

    # current_path_stack[i][p] is the number of paths p that go from
    # current_edge of index i.
    current_path_stack = defaultdict(lambda: defaultdict(int))

    # for e, current_edge in enumerate(D):
    for e, ((timestamp, end, uid), edge) in enumerate(tn.tedges.items()):
        current_edge = (edge.v.uid, edge.w.uid, timestamp)
        # since we go in forward direction, delta window is back in time.
        # not every entry from delta window is important for the current
        # considered current_edge some are happening at the same time.

        # check if there is anything to update about delta window
        # and current stack
        if len(delta_window) > 0:
            # I throw away the ones in delta_window that are too far away
            # (in temporal sense)
            i = 0
            didnt_find_one_yet = True
            # since the data is sorted, I just need to find the one that
            # is inside the delta time window.
            # This while loop identifies the first entry saved in delta window,
            # that is inside the new delta window so it only loops through the
            # ones that are outside the new delta window.
            while i < len(delta_window) and didnt_find_one_yet:
                # i'th entry [i], then I need the entry,
                # and not the ennumerator [1],
                # and then I need time, which is the third column[2]
                if delta_window[i][1][2] >= current_edge[2]-delta:
                    didnt_find_one_yet = False
                else:
                    # i didn't find yet one which is inside the new delta window.
                    i += 1

            # keep all starting from the first that is inside the
            # new delta window.
            if i < len(delta_window):
                first_index_in_delta_window = delta_window[i][0]
                old_inx = [
                    e for (e, current_edge) in delta_window if e < first_index_in_delta_window]
                delta_window = delta_window[i:]
            else:
                # all from delta window should be removed.
                # asign current index
                first_index_in_delta_window = e
                old_inx = [
                    e for (e, current_edge) in delta_window if e < first_index_in_delta_window]
                delta_window = []
            # delta_window is now corresponding to the current_edge that I am
            # considering.
            # go through outdated indices
            for j in old_inx:
                # remove them from the current stack.
                del current_path_stack[j]
        # all stacks updated now.

        # compute for the next
        for enu, past_edge in delta_window:
            # if target of the link in delta_window is the same as the
            # source in considered entry
            if past_edge[1] == current_edge[0]:
                # the interactions should not happen at the same time!
                # the considered one should happen AFTER the one from the
                # delta window.
                if current_edge[2] > past_edge[2]:
                    # i know that the link happened in the appropriate time,
                    # and that the link continues the link I consider.
                    # so I can add the paths to the current_path_stack
                    for path in current_path_stack[enu]:
                        p = (*path, current_edge[1])
                        if len(p)-1 <= up_to_k:
                            current_path_stack[e][p] += current_path_stack[enu][path]

                            if e >= skip_first:
                                if p not in path_stack:
                                    path_stack.add(
                                        p, frequency=current_path_stack[enu][path])
                                else:
                                    path_stack[p]['frequency'] += current_path_stack[enu][path]
        current_path_stack[e][(current_edge[0], current_edge[1])] += 1

        if e >= skip_first:
            p = (current_edge[0], current_edge[1])
            if p not in path_stack:
                path_stack.add(p, frequency=1)
            else:
                path_stack[p]['frequency'] += 1

        # add this current_edge at the end of delta_window,
        # so that the next current_edge can have all the entries it needs.
        delta_window.append((e, current_edge))

    return path_stack

    