""" Null Model class """
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : null_models.py -- Null models for pathpy
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Wed 2021-03-31 11:18 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Optional, Any
import datetime

from singledispatchmethod import singledispatchmethod

from pathpy import logger, tqdm
from pathpy.core.node import NodeCollection
from pathpy.core.edge import EdgeCollection
from pathpy.core.path import PathCollection
from pathpy.models.network import Network

from pathpy.models.higher_order_network import (HigherOrderNetwork,
                                                HigherOrderNodeCollection)
from pathpy.statistics.subpaths import SubPathCollection

# create logger
LOG = logger(__name__)


class NullModel(HigherOrderNetwork):
    """A null model for higher order networks."""

    def __init__(self, uid: Optional[str] = None, order: int = 2,
                 **kwargs: Any) -> None:
        """Initialize the null model"""

        # initialize the base class
        super().__init__(uid=uid, order=order, **kwargs)

    @singledispatchmethod
    def fit(self, data, order: Optional[int] = None) -> None:
        """Fit data to a NullModel"""
        raise NotImplementedError

    @fit.register(PathCollection)  # type: ignore
    def _(self, data: PathCollection, order: Optional[int] = None) -> None:

        # Check order
        if order is not None:
            self._order = order

        if 0 <= self.order <= 1:
            super().fit(data, order=self.order)

        elif self.order > 1:
            # --- START ---
            nc = NodeCollection()
            for node in data.nodes.values():
                nc.add(node)

            ec = EdgeCollection(nodes=nc)
            for edge in data.edges.values():
                ec.add(edge)

            self._nodes = HigherOrderNodeCollection(nodes=nc, edges=ec)
            # --- END ---

            # get path data
            paths = data

            # generate first order representation of data
            network = Network.from_paths(paths, frequencies=True)

            self.calculate(network, paths)

        else:
            LOG.error('A Null Model with order %s is not supported', self.order)
            raise AttributeError

    @fit.register(Network)  # type: ignore
    def _(self, data: Network, order: Optional[int] = None) -> None:

        # Check order
        if order is not None:
            self._order = order

        if 0 <= self.order <= 1:
            super().fit(data, order=self.order)

        elif self.order > 1:

            # TODO: create function to transfer base data from PathCollection object
            # --- START ---
            nc = NodeCollection()
            for node in data.nodes.values():
                nc.add(node)

            ec = EdgeCollection(nodes=nc)
            for edge in data.edges.values():
                ec.add(edge)

            self._nodes = HigherOrderNodeCollection(nodes=nc, edges=ec)
            # --- END ---

            # get network data
            network = data

            # generate a path representation of the data
            paths = PathCollection(directed=network.directed,
                                   nodes=network.nodes, edges=network.edges)
            for edge in data.edges:
                paths.add(edge, frequency=edge.attributes.get('frequency', 1))

            self.calculate(network, paths)

        else:
            LOG.error('A Null Model with order %s is not supported', self.order)
            raise AttributeError

    def calculate(self, network: Network, paths: PathCollection) -> None:
        """Calculate the null modell"""

        # get transition matrix of the underlying network
        transition_matrix = network.transition_matrix(weight='frequency')

        # generate all possible paths
        possible_paths = self.possible_paths(paths.edges, self.order)

        # Get all sub-paths of order-1
        subpaths = SubPathCollection.from_paths(paths,
                                                min_length=self.order-1,
                                                max_length=self.order-1,
                                                include_path=True)

        # add paths to the higer-order network
        for path in possible_paths:
            nodes: list = []
            for subpath in self.window(path, size=self.order-1):
                nodes.append(subpath)

            for _v, _w in zip(nodes[:-1], nodes[1:]):

                if _v not in self.nodes:
                    self.nodes.add(_v)

                if _w not in self.nodes:
                    self.nodes.add(_w)

                _nodes = (self.nodes[_v], self.nodes[_w])

                # generate the expected frequencies of all possible paths
                if _v in subpaths:
                    frequency = subpaths.counter[subpaths[_v]] * \
                        transition_matrix[network.nodes.index[_w[-1].v.uid],
                                          network.nodes.index[_w[-1].w.uid]]

                else:
                    frequency = 0.0

                if _nodes not in self.edges:
                    self.add_edge(*_nodes, possible=0,
                                  observed=frequency, frequency=frequency)

    def degrees_of_freedom(self, mode: str = 'path') -> int:
        """Returns the degrees of freedom of the higher order network.

        Since probabilities must sum to one, the effective degree of freedom is
        one less than the number of nodes

        .. math::

           \\text{dof} = \\sum_{n \\in N} \\max(0,\\text{outdeg}(n)-1)

        """
        # initialize degree of freedom
        degrees_of_freedom: int = 0

        if self.order == 0:
            degrees_of_freedom = max(0, self.number_of_nodes()-1)

        # elif mode == 'old':
        #     # TODO : Remove this part after proper testing
        #     A = self.network.adjacency_matrix()

        #     degrees_of_freedom = int(
        #         (A ** self.order).sum()
        #         - np.count_nonzero((A ** self.order).sum(axis=0)))

        elif mode == 'ngram':
            number_of_nodes = len(self.nodes.nodes)
            degrees_of_freedom = (number_of_nodes ** self.order) * \
                (number_of_nodes-1)

        elif mode == 'path':

            # iterate over all nodes and count outdegree
            for outdegree in self.outdegrees().values():
                degrees_of_freedom += max(0, int(outdegree)-1)

        # return degree of freedom
        return degrees_of_freedom

    @staticmethod
    def possible_paths(edges, order) -> list:
        """Returns a dictionary of all paths with a given length
           that can possible exists.
        """
        # some information for debugging
        LOG.debug('start generate possible paths')
        _start = datetime.datetime.now()

        # start with edges, i.e. paths of length one
        paths = [[k] for k in edges.values()]

        # extend all of those paths by an edge k-1 times
        # TODO: speed up this function !!!
        for _ in tqdm(range(order - 1), desc='possilbe paths'):
            _new = list()
            for e_1 in paths:
                for e_2 in edges.values():
                    if e_1[-1].w == e_2.v:
                        _new.append(e_1 + [e_2])
            paths = _new

        # some information for debugging
        _end = datetime.datetime.now()
        LOG.debug('end generate possible paths: %s seconds',
                  (_end-_start).total_seconds())
        return paths

    @classmethod
    def from_paths(cls, paths: PathCollection, **kwargs: Any):
        """Create higher oder network from paths."""

        order: int = kwargs.get('order', 2)

        null = cls(order=order)
        null.fit(paths)

        return null

    @classmethod
    def from_network(cls, network: Network, **kwargs: Any):
        """Create higher oder network from networks."""

        order: int = kwargs.get('order', 2)

        null = cls(order=order)
        null.fit(network)

        return null


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
