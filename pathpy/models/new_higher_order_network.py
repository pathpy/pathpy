"""Higher-order network class"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : higher_order_network.py -- Basic class for a HON
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Mon 2021-05-24 17:55 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from typing import Any, Optional
from itertools import islice
from collections import Counter
from singledispatchmethod import singledispatchmethod  # NOTE: not needed at 3.9

from pathpy import logger
from pathpy.core.edge import Edge, EdgeCollection
from pathpy.core.path import Path, PathCollection
from pathpy.models.classes import BaseHigherOrderNetwork
from pathpy.models.network import Network

# create logger for the Network class
LOG = logger(__name__)


class HigherOrderNode(Path):
    """Base class of a higher-order node."""

    @property
    def order(self):
        "Return the order of the higher-oder node"
        return len(self)


class HigherOrderNodeCollection(PathCollection):
    """A collection of edges"""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the EdgeCollection object."""

        # initialize the base class
        super().__init__(*args, **kwargs)

        # class of objects
        self._default_class: Any = HigherOrderNode


class HigherOrderEdge(Edge):
    """Base class of an higher-order edge."""

    def first_order_relations(self):
        """converts edge relations to first order"""
        _v = self.objects[self.v].relations
        _w = self.objects[self.w].relations
        return _v, _w


class HigherOrderEdgeCollection(EdgeCollection):
    """A collection of edges"""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the EdgeCollection object."""

        # initialize the base class
        super().__init__(*args, **kwargs)

        # class of objects
        self._default_class: Any = HigherOrderEdge


class HigherOrderNetwork(BaseHigherOrderNetwork, Network):
    """Base class for a Higher Order Network (HON)."""

    def __init__(self, uid: Optional[str] = None, order: int = 1,
                 **kwargs: Any) -> None:
        """Initialize the higer-order network object."""

        # initialize the base class
        super().__init__(uid=uid, directed=True, multiedges=False, **kwargs)

        # order of the higher-order network
        self._order: int = order

        # a container for node objects
        self._nodes: Any = HigherOrderNodeCollection()

        # a container for edge objects
        self._edges: Any = HigherOrderEdgeCollection()

        # a counter for observed paths
        self._observed: Counter = Counter()

        # a counter for possible paths
        self._possible: Counter = Counter()

    @property
    def order(self) -> int:
        """Return the order of the higher-order network."""
        return self._order

    @property
    def possible(self) -> Counter:
        """Return a counter of possible paths."""
        return self._possible

    @property
    def observed(self) -> Counter:
        """Return a counter of observed paths."""
        return self._observed

    @singledispatchmethod
    def fit(self, data, order: Optional[int] = None,
            subpaths: bool = True) -> None:
        """Fit data to a HigherOrderNetwork"""
        raise NotImplementedError

    @fit.register(PathCollection)
    def _(self, data: PathCollection, order: Optional[int] = None,
          subpaths: bool = True) -> None:

        if order is not None:
            self._order = order

        # iterate over all paths
        for uid, path in data.items():

            nodes: list = []

            if self.order == 0:
                for node, obj in path.nodes.items():
                    if node not in self.nodes:
                        self.add_node(obj, uid=node, frequency=0)

                for node in path.nodes:
                    self.nodes.counter[node] += data.counter[uid]

            elif 1 <= self.order <= len(path):
                for subpath in self.window(path.relations, size=self.order+1):
                    nodes.append(subpath)

            elif self.order == len(path)+1:
                if path.relations not in self.nodes:
                    self.add_node(*path, frequency=0)
                self.nodes.counter[self.nodes[path.relations].uid] += data.counter[uid]

            else:
                pass

            edges: list = []

            for _v, _w in zip(nodes[:-1], nodes[1:]):

                if _v not in self.nodes:
                    self.nodes.add(_v)

                if _w not in self.nodes:
                    self.nodes.add(_w)

                _v = self.nodes[_v]
                _w = self.nodes[_w]

                if (_v, _w) not in self.edges:
                    edge = HigherOrderEdge(_v, _w)
                    self.add_edge(edge, frequency=0)
                    edges.append(edge)

            for edge in edges:
                self.edges.counter[edge.uid] += data.counter[uid]
                if order == len(path):
                    self._observed[edge.relations] += data.counter[uid]
                else:
                    self._possible[edge.relations] += data.counter[uid]

                # for edge in _edges:
                # edge['frequency'] += frequency
                # if order == len(path):
                #     edge['observed'] += frequency
                # else:
                #     edge['possible'] += frequency

                # print(_v, _w)

    @staticmethod
    def window(iterable, size=2):
        """Sliding window for path length"""
        _iter = iter(iterable)
        result = tuple(islice(_iter, size))
        if len(result) == size:
            yield result
        for element in _iter:
            result = result[1:] + (element,)
            yield result


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
