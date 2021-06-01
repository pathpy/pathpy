"""Algorithms to compute paths in temporal networks and directed acyclic graphs."""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : path_extraction.py -- Algorithms to compute paths in temporal networks and directed acyclic graphs
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Tue 2021-06-01 12:51 ingo>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================

from __future__ import annotations
from pathpy.models.temporal_network import TemporalNetwork
from typing import Any, List, Union, Optional, Tuple
from functools import singledispatch
from collections import defaultdict, deque
import itertools as it
import functools as ft
from collections import Counter

from pathpy import logger, tqdm

from pathpy.core.api import NodeCollection, Node
from pathpy.core.api import EdgeCollection
from pathpy.core.api import PathCollection
from pathpy.models.classes import BaseTemporalNetwork
from pathpy.models.models import ABCDirectedAcyclicGraph



# create logger
LOG = logger(__name__)


def _remove_repetitions(path):
    """
    Remove repeated nodes in the path

    Parameters
    ----------
    path

    Returns
    -------

    Examples
    -------
    >>> remove_repetitions((1, 2, 2, 3, 4, 1))
    (1, 2, 3, 4, 1)
    >>> remove_repetitions((1, 2, 2, 2, 3)) == remove_repetitions((1, 2, 2, 3, 3))
    True
    """
    return tuple(p[0] for p in it.groupby(path))


def _expand_set_paths(set_path):
    """returns all possible paths which are consistent with the sequence of sets

    Parameters
    ----------
    set_path: list
        a list of sets or other iterable

    Examples
    -------
    >>> node_path = [{1, 2}, {2, 5}, {1, 2}]
    >>> list(expand_set_paths(node_path))
    [(1, 2, 1), (2, 2, 1), (1, 5, 1), (2, 5, 1), (1, 2, 2), (2, 2, 2), (1, 5, 2), (2, 5, 2)]
    >>> node_path = [{1, 2}, {5}, {2, 5}]
    >>> list(expand_set_paths(node_path))
    [(1, 5, 2), (2, 5, 2), (1, 5, 5), (2, 5, 5)]


    Yields
    ------
    tuple
        a possible path
    """
    # how many possible combinations are there
    node_sizes = [len(n) for n in set_path]
    num_possibilities = ft.reduce(lambda x, y: x * y, node_sizes, 1)

    # create a list of lists such that each iterator is repeated the number of times
    # his predecessors have completed their cycle
    all_periodics = []
    current_length = 1
    for node_set in set_path:
        periodic_num = []
        for num in node_set:
            periodic_num.extend([num] * current_length)
        current_length *= len(node_set)
        all_periodics.append(periodic_num)

    iterator = [it.cycle(periodic) for periodic in all_periodics]
    for i, elements in enumerate(zip(*iterator)):
        if i >= num_possibilities:
            break
        yield elements



def all_paths_from_dag(dag: ABCDirectedAcyclicGraph, node_mapping=None, max_subpath_length=None, separator=',', repetitions=True, unique=False) -> PathCollection:
    """
    Calculates path statistics in a directed acyclic graph.
    All paths between all roots (nodes with zero indegree)
    and all leafs (nodes with zero outdegree) are generated.

    Parameters
    ----------
    dag: DAG
        the directed acyclic graph instance for which paths are calculated
    node_mapping: dict
        can be a simple mapping (1-to-1) or a 1-to-many (a dict with sets as values)
    max_subpath_length: int
        This can be used to limit the calculation of sub path statistics to a given
        maximum length. This is useful, as the statistics of sub paths of length k
        are only needed to fit a higher-order model with order k. Hence, if we know
        that the model selection is limited to a given maximum order K, we can safely
        set the maximum sub path length to K. By default, sub paths of any length
        will be calculated. Note that, independent of the sub path calculation
        longest path of any length will be considered in the likelihood calculation!
    separator: str
        separator to use to separate nodes in the generated Paths object. Default is ','.
    repetitions: bool
        whether or not to remove repeated nodes in the paths. Such repeated paths can occur
        if a non-injective node_mapping is applied. If set to True, a path a,a,b,b,c,c,d is
        returned as a,b,c,d.
    unique: bool
        whether or not multiple identical mapped paths should be counted separately. For
        DAG representations of temporal networks with delta > 1, where nodes are temporal copies,
        we do not want to count multiple paths from the same root that pass through different
        temporal copies of the same physical node. For instance with delta=2, time-stamped edges
        (a,b;1), (b,c;3) are transformed into a DAG a1->b2, a1->b3, b3->c4. With the mapping to
        physical nodes we would find two different paths a->b->c of length two, which only differ
        in terms of WHEN they arrive in node c


    Returns
    -------
    Paths

    """
    # Check whether we are doing a one-to-many mapping
    if node_mapping is None:
        node_mapping = { v.uid: v.uid for v in dag.nodes }

    if node_mapping:
        first_key = list(node_mapping.keys())[0]
        ONE_TO_MANY = isinstance(node_mapping[first_key], set)
    else:
        ONE_TO_MANY = False

    # Try to topologically sort the graph if not already sorted
    if dag.acyclic is None:
        dag.topological_sorting()
    if not dag.acyclic:
        LOG.error('Cannot extract statistics from a cyclic graph')
        raise ValueError
    else:
        # path object which will hold the detected (projected) paths
        paths = PathCollection()
        # if max_subpath_length:
        #     p.max_subpath_length = max_subpath_length
        # else:
        #     p.max_subpath_length = sys.maxsize

        LOG.info('Creating paths from directed acyclic graph')

        # construct all paths originating from root nodes for 1 to 1
        if not ONE_TO_MANY:
            for s in dag.roots:
                extracted_paths = dag.routes_from(s.uid, node_mapping)
                if unique:
                    extracted_paths = set(tuple(x) for x in extracted_paths)
                for path in extracted_paths:   # add detected paths to paths object                    
                    if repetitions:
                        p = path                                          
                    else:
                        p = _remove_repetitions(path)
                    paths.add(p, count=1, uid='-'.join(p))
        else:
            path_counter = defaultdict(lambda: 0)
            for root in dag.roots:
                for set_path in dag.routes_from_node(root.uid, node_mapping):
                    for blown_up_path in _expand_set_paths(set_path):
                        path_counter[blown_up_path] += 1

            for path, count in path_counter.items():
                if repetitions:
                    p = path
                else:
                    p = _remove_repetitions(path)
                paths.add(p, count=count, uid='-'.join(p))

        #LOG.info('Expanding Subpaths')
        # p.expand_subpaths()
        #LOG.info('finished.')
        return paths


def all_paths_from_temporal_network(tempnet: TemporalNetwork, delta: int=1, max_subpath_length: int=-1) -> PathCollection:
    """
    Calculates the frequency of causal paths in a temporal network assuming a 
    maximum temporal distance of delta between consecutive
    time-stamped links on a path. This method first creates a directed and acyclic
    time-unfolded graph based on the given parameter delta. This directed acyclic
    graph is used to calculate all time-respecting paths for a given delta.
    I.e., for time-stamped links (a,b,1), (b,c,5), (b,d,7) and delta = 5 the
    time-respecting path (a,b,c) will be found.

    Parameters
    ----------
    tempnet : pathpy.TemporalNetwork
        TemporalNetwork to extract the time-respecting paths from
    delta : int
        Indicates the maximum temporal distance up to which time-stamped
        links will be considered to contribute to a causal path.
        For (u,v;3) and (v,w;7) a causal path (u,v,w) is generated
        for 0 < delta <= 4, while no causal path is generated for
        delta > 4. Every time-stamped edge is a causal path of
        length one. Default value is 1.
    max_subpath_length : int
        Can be used to limit the calculation of sub path statistics to a given
        maximum length. This is useful as statistics of sub paths of length k
        are only needed to fit higher-order model with order k and larger. If model
        selection is limited to a maximum order K, we can set the maximum sub path length
        to K. Default is None, which means all subpaths are calculated.

    Returns
    -------
    Paths
        An instance of the class Paths, which can be used to generate higher- and multi-order
        models of causal paths in temporal networks.

    Examples
    ---------
    >>> t = pp.TemporalNetwork()
    >>> t.add_edge('a', 'b', 1)
    >>> t.add_edge('b', 'a', 3)
    >>> t.add_edge('b', 'c', 3)
    >>> t.add_edge('d', 'c', 4)
    >>> t.add_edge('c', 'd', 5)
    >>> t.add_edge('c', 'b', 6)

    >>> >>>causal_paths = pp.path_extraction.paths_from_temporal_network_dag(t, delta=2)
    >>> [Severity.INFO]	Constructing time-unfolded DAG ...
    >>> [Severity.INFO]	finished.
    >>> [Severity.INFO]	Generating causal trees for 2 root nodes ...
    >>> [Severity.INFO]	finished.
    >>> print(causal_paths)
    >>> Total path count: 		4.0 
    >>> [Unique / Sub paths / Total]: 	[4.0 / 24.0 / 28.0]
    >>> Nodes:				    4 
    >>> Edges:				    6
    >>> Max. path length:		3
    >>> Avg path length:		2.25 
    >>> Paths of length k = 0		0.0 [ 0.0 / 13.0 / 13.0 ]
    >>> Paths of length k = 1		0.0 [ 0.0 / 9.0 / 9.0 ]
    >>> Paths of length k = 2		3.0 [ 3.0 / 2.0 / 5.0 ]
    >>> Paths of length k = 3		1.0 [ 1.0 / 0.0 / 1.0 ]

    >>> The calculated (longest) causal paths in this example are:
    >>> (a, b, c, d), (d, c, b), (d, c, d), (a, b, a)
    """
    from pathpy.models.directed_acyclic_graph import DirectedAcyclicGraph

    # generate a single time-unfolded DAG
    LOG.info('Constructing time-unfolded DAG ...')
    dag = DirectedAcyclicGraph.from_temporal_network(tempnet, delta)
    node_map = { v.uid: v['original'].uid for v in dag.nodes }
    LOG.info('finished.')

    # path statistics
    causal_paths = PathCollection()
    
    # For each root in the time-unfolded DAG, we generate a
    # causal tree and use it to count all causal paths
    # that originate at this root
    num_roots = len(dag.roots)
    current_root = 1

    LOG.info('Generating causal trees for {0} root nodes ...'.format(num_roots))
    for root in tqdm(dag.roots):

        # generate the causal tree from this root node
        causal_tree, causal_mapping = generate_causal_tree(dag, root, node_map)

        # output
        if num_roots > 10:
            step = num_roots/10
            if current_root % step == 0:
                LOG.info('Analyzing tree {0}/{1} ...'.format(current_root, num_roots))

        # calculate all unique longest path in the causal tree
        # TODO: replace by add operator
        paths = all_paths_from_dag(causal_tree, causal_mapping, repetitions=False, max_subpath_length=max_subpath_length)
        for p in paths:
            causal_paths.add(p, count=paths.counter[p.uid], uid=p.uid)
        current_root += 1

    LOG.info('finished.')

    return causal_paths


def generate_causal_tree(dag, root, node_map) -> Tuple(ABCDirectedAcyclicGraph, defaultdict):
    """
    For a directed acyclic graph and a non-injective mapping of nodes,
    this method creates a *causal tree* for a given root node.
    This is useful for the extraction of causal paths in time-unfolded DAG
    representations of temporal networks. The nodes "{v}_{d}" in the resulting
    causal tree capture that - starting from the root node at step 0 - there is
    a causal path to node v at distance d from the root. Note that the same node
    can be represented by multiple nodes in the causal tree (at different distances d).
    """
    from pathpy.models.directed_acyclic_graph import DirectedAcyclicGraph
    causal_tree = DirectedAcyclicGraph()

    causal_mapping = {}
    visited = defaultdict(lambda: False)
    queue = deque()

    # launch breadth-first-search at root of tree
    # root nodes are necessarily at depth 0
    queue.append((root.uid, 0))
    edges = []
    while queue:
        # take out left-most element from FIFO queue
        v, depth = queue.popleft()

        # x is the node ID of the node in the causal tree
        # the second component captures the distance from
        # the root of the causal tree. These IDs ensure
        # that the same physical nodes can occur at different
        # distances from the root
        x = '{0}_{1}'.format(node_map[v], depth)
        causal_mapping[x] = node_map[v]

        # process nodes at next level
        for w in dag.successors[v]:
            if (w.uid, depth+1) not in queue:
                queue.append((w.uid, depth+1))
                # only consider nodes that have not already
                # been added to this level
                if not visited[node_map[w.uid], depth+1]:
                    # add edge to causal tree
                    y = '{0}_{1}'.format(node_map[w.uid], depth+1)
                    edges.append((x, y))

                    visited[node_map[w.uid], depth+1] = True
                    causal_mapping[y] = node_map[w.uid]
    
    # Adding all edges at once is more efficient!
    for e in edges:
        causal_tree.add_edges(e)

    return causal_tree, causal_mapping


    
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

    path_collection = PathCollection()

    # current_path_stack[i][p] is the number of paths p that go from
    # current_edge of index i.
    current_path_stack = defaultdict(lambda: defaultdict(int))

    # for e, current_edge in enumerate(D):
    for e, edge in enumerate(tn.edges[:]):
        current_edge = (edge.v.uid, edge.w.uid, edge.start)
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
                                # path_collection[p] += current_path_stack[enu][path]
                                path_collection.add(p, uid='-'.join(p), count=current_path_stack[enu][path])
        current_path_stack[e][(current_edge[0], current_edge[1])] += 1

        if e >= skip_first:
            p = (current_edge[0], current_edge[1])
            path_collection.add(p[0], p[1], uid='-'.join(p), count=1)
            # path_collection[p] += 1

        # add this current_edge at the end of delta_window,
        # so that the next current_edge can have all the entries it needs.
        delta_window.append((e, current_edge))

    return path_collection

    