#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : null_models.py -- Null models for pathpy
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Fri 2019-11-08 15:21 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import List
import datetime
from ..classes import HigherOrderNetwork, HigherOrderNode, Edge
from .. import logger, tqdm

# create logger
log = logger(__name__)


class NullModel:
    """A null model for higher order networks."""

    def __init__(self, network):
        """Initialize the null model"""
        self.network = network
        self.order = 0
        self.hon = HigherOrderNetwork()

    def __call__(self, order: int = 1) -> HigherOrderNetwork:
        """Returns a null model of given order."""

        # check if null model was already calculated
        if order == self.order and self.hon.number_of_nodes() > 0:

            # if so return pre calculated model
            return self.hon
        else:

            # if not generate new model and return
            return self.generate(order)

    def generate(self, order: int = 1) -> HigherOrderNetwork:
        """Generate a null model."""

        # some information for debugging
        log.debug('start generate null model')
        a = datetime.datetime.now()

        # generate all possible paths
        possible_paths = self.possible_paths(order=order)

        # get observed paths
        observed = self.network.subpaths.counter(min_length=order-1,
                                                 max_length=order-1)

        # get transition matrix of the underlying network
        transition_matrix = self.network.transition_matrix()

        # get the ordered node uids of the underlying network as a list
        nodes = list(self.network.nodes)

        # generate hon with possible paths
        hon = HigherOrderNetwork()

        for path in possible_paths:

            # generate "empty" higher order nodes
            v = HigherOrderNode()
            w = HigherOrderNode()

            # add first order edges to the higher oder nodes
            for v_uid, w_uid in zip(path[:-1], path[1:]):
                v.add_edge(self.network.edges[v_uid])
                w.add_edge(self.network.edges[w_uid])

            # generate the expected frequencies of all possible paths
            uid = self.network.separator['path'].join(path[:-1])
            frequency = 0
            if uid in observed:
                frequency = observed[uid] * transition_matrix[
                    nodes.index(w.as_nodes[-2]), nodes.index(w.as_nodes[-1])]

            # add higher order nodes to the hon
            # TODO: use automatically hon separator
            hon.add_edge(Edge(v, w, separator=hon.separator['hon']),
                         frequency=frequency)

        # some information for debugging
        b = datetime.datetime.now()
        log.debug('end generate null model:' +
                  ' {} seconds'.format((b-a).total_seconds()))

        # safe hon in class and order
        self.hon = hon
        self.order = order

        # return null model
        return hon

    def possible_paths(self, order: int = 1) -> List[List[str]]:
        """Returns a dictionary of all paths with a given length
           that can possible exists.
        """
        # some information for debugging
        log.debug('start generate possible paths')
        a = datetime.datetime.now()

        # generate mapping between edges and nodes
        e2n = {e.uid: (e.v.uid, e.w.uid)for e in self.network.edges.values()}

        # start with edges, i.e. paths of length one
        possible_paths = [[k] for k in e2n.keys()]

        # generate a sequence of edges
        edges = [(e, v, w) for e, (v, w) in e2n.items()]

        # extend all of those paths by an edge k-1 times
        # TODO: speed up this function !!!
        for i in tqdm(range(order - 1), desc='possilbe paths'):
            _new = list()
            for e1 in tqdm(possible_paths):
                for (e2, v, w) in edges:
                    if e2n[e1[-1]][1] == v:
                        p = e1 + [e2]
                        _new.append(p)
            possible_paths = _new

        # some information for debugging
        b = datetime.datetime.now()
        log.debug('end generate possible paths:' +
                  ' {} seconds'.format((b-a).total_seconds()))
        return possible_paths

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
