""" Null Model class """
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : null_models.py -- Null models for pathpy
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Fri 2021-05-28 16:17 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from typing import Optional, Any
from singledispatchmethod import singledispatchmethod
from collections import Counter

from pathpy import logger, tqdm
from pathpy.models.higher_order_network import HigherOrderNetwork
from pathpy.core.path import PathCollection
# from pathpy.core.node import NodeCollection
# from pathpy.core.edge import EdgeCollection
# from pathpy.models.network import Network

# from pathpy.statistics.subpaths import SubPathCollection

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
    def fit(self, data, order: Optional[int] = None,
            subpaths: bool = True) -> None:
        """Fit data to a HigherOrderNetwork"""
        raise NotImplementedError

    @fit.register(PathCollection)  # type: ignore
    def _(self, data: PathCollection, order: Optional[int] = None) -> None:

        # check order
        if order is not None:
            self._order = order

        # generate first order hon
        hon = HigherOrderNetwork.from_paths(data, order=1)

        # get node index and transition matrix
        idx = {node.relations[0]: i for i, node in enumerate(hon.nodes)}
        mat = hon.transition_matrix(weight='frequency')

        # generate possible paths
        paths = self.possible_relations(data, self.order)

        subpaths: Counter = Counter()
        for path in tqdm(data, desc='calculate possible sub-paths'):
            for subpath in path.subpaths(min_length=self.order-1,
                                         max_length=self.order-1,
                                         include_self=True, paths=False):
                subpaths[subpath] += data.counter[path.uid]

        for path in paths:
            # get higher-oder nodes
            _v, _w = path[:-1], path[1:]
            if _v not in self.nodes:
                self.add_node(*_v, frequency=0)
            if _w not in self.nodes:
                self.add_node(*_w, frequency=0)
            node_v, node_w = self.nodes[_v], self.nodes[_w]

            frequency = subpaths[_v] * mat[idx[path[-2]], idx[path[-1]]]

            if (node_v, node_w) not in self.edges:
                self.add_edge(node_v, node_w, frequency=0)

            edge = self.edges[node_v, node_w]
            self.edges.counter[edge.uid] += frequency

    @classmethod
    def from_paths(cls, paths: PathCollection, **kwargs: Any):
        """Create higher oder network from paths."""

        order: int = kwargs.get('order', 2)

        null = cls(order=order)
        null.fit(paths)

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
