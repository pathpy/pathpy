"""Higher-order network class"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : higher_order_network.py -- Basic class for a HON
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Wed 2021-03-31 11:02 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, Optional, Union, cast
from itertools import islice
from singledispatchmethod import singledispatchmethod
import numpy as np

from pathpy import logger
from pathpy.core.node import Node, NodeCollection
from pathpy.core.edge import Edge, EdgeCollection#, EdgeSet
from pathpy.core.path import Path, PathCollection
from pathpy.models.network import Network

from pathpy.models.models import ABCHigherOrderNetwork
from pathpy.statistics.subpaths import SubPathCollection

# create logger for the Network class
LOG = logger(__name__)


class HigherOrderNetwork(ABCHigherOrderNetwork, Network):
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
        self._edges: Any = HigherOrderEdgeCollection(nodes=self._nodes)

        # a container for for subpaths
        self._subpaths: SubPathCollection = SubPathCollection()

    @property
    def order(self) -> int:
        """Return the order of the higher-order network."""
        return self._order

    def summary(self) -> str:
        """Returns a summary of the higher-order network.

        The summary contains the name, the used network class, the order, the
        number of nodes and edges.

        If logging is enabled (see config), the summary is written to the log
        file and showed as information on in the terminal. If logging is not
        enabled, the function will return a string with the information, which
        can be printed to the console.

        Returns
        -------
        str
            Returns a summary of important higher-order network properties.

        """
        summary = [
            'Uid:\t\t\t{}\n'.format(self.uid),
            'Type:\t\t\t{}\n'.format(self.__class__.__name__),
            # 'Directed:\t\t{}\n'.format(str(self.directed)),
            # 'Multi-Edges:\t\t{}\n'.format(str(self.multiedges)),
            'Order:\t\t\t{}\n'.format(self.order),
            'Number of nodes:\t{}\n'.format(self.number_of_nodes()),
            'Number of edges:\t{}'.format(self.number_of_edges()),
        ]
        attr = self.attributes.to_dict()
        if len(attr) > 0:
            summary.append('\n\nNetwork attributes\n')
            summary.append('------------------\n')
        for k, v in attr.items():
            summary.append('{}:\t{}\n'.format(k, v))

        text = ''.join(summary)
        if self._subpaths:
            text = text + '\n' + self._subpaths.summary()
        return text

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

        order = self.order
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

        # iterate over all paths
        for path in data:

            # get frequency of the observed path
            # TODO: define keyword in config file
            frequency = path.attributes.get('frequency', 1)

            nodes: list = []
            if order == 0:
                for node in path.nodes:
                    if (node,) not in self.nodes:
                        self.add_node(node, frequency=0.0)
                    #self.nodes[(node,)]['frequency'] += frequency

                for node in path.nodes:
                    self.nodes[(node,)]['frequency'] += frequency
            elif order == 1:
                nodes.extend([tuple([n]) for n in path.nodes])

            elif 1 < order <= len(path):
                for subpath in self.window(path.edges, size=order-1):
                    nodes.append(subpath)

            elif order == len(path)+1:
                if tuple(path.edges) not in self.nodes:
                    self.nodes.add(tuple(path.edges))

            else:
                pass

            _edges = []
            for _v, _w in zip(nodes[:-1], nodes[1:]):

                if _v not in self.nodes:
                    self.nodes.add(_v)

                if _w not in self.nodes:
                    self.nodes.add(_w)

                _nodes = (self.nodes[_v], self.nodes[_w])
                if _nodes not in self.edges:
                    self.add_edge(*_nodes, possible=0, observed=0, frequency=0)

                _edges.append(self.edges[_nodes])

            for edge in _edges:
                edge['frequency'] += frequency
                if order == len(path):
                    edge['observed'] += frequency
                else:
                    edge['possible'] += frequency

        if order == 0:
            frequencies = [n['frequency'] for n in self.nodes]
            for node in self.nodes:
                node['frequency'] = node['frequency']/sum(frequencies)

        if subpaths:
            self._subpaths = SubPathCollection.from_paths(data,
                                                          max_length=order,
                                                          include_path=True)

    def likelihood(self, data: PathCollection, log: bool = False) -> float:
        """Returns the likelihood given some observation data."""

        # some information for debugging
        LOG.debug('I\'m a likelihood of a HigherOrderNetwork')

        # get a list of nodes for the matrix indices
        n = self.nodes.index

        # get the transition matrix
        T = self.transition_matrix(weight='frequency', transposed=True)

        # # generate hon network for the observed paths
        # hon = self.from_paths(data, order=self.order)

        # initialize likelihood
        if log:
            likelihood = 0.0
            _path_likelihood = 0.0
        else:
            likelihood = 1.0
            _path_likelihood = 1.0

        # iterate over observed hon paths
        for path in data:

            # get frequency of the observed path
            # TODO: define keyword in config file
            frequency = path.attributes.get('frequency', 1)

            # initial path likelihood
            path_likelihood = _path_likelihood

            nodes: list = []

            if self.order == 1:
                nodes.extend([tuple([n]) for n in path.nodes])

            elif 1 < self.order <= len(path):

                for subpath in self.window(path.edges, size=self.order-1):
                    nodes.append(subpath)

            for _v, _w in zip(nodes[:-1], nodes[1:]):

                # calculate path likelihood
                if log:
                    path_likelihood += np.log(T[n[self.nodes[_w].uid],
                                                n[self.nodes[_v].uid]])
                else:
                    path_likelihood *= T[n[self.nodes[_w].uid],
                                         n[self.nodes[_v].uid]]

            # calculate likelihood
            if log:
                likelihood += path_likelihood * frequency
            else:
                likelihood *= path_likelihood ** frequency

        return likelihood

    @staticmethod
    def window(iterable, size=2):
        """Sliding window for path length"""
        ite = iter(iterable)
        result = tuple(islice(ite, size))
        if len(result) == size:
            yield result
        for elem in ite:
            result = result[1:] + (elem,)
            yield result

    @classmethod
    def from_paths(cls, paths: PathCollection, **kwargs: Any):
        """Create higher oder network from paths."""

        order: int = kwargs.get('order', 1)
        subpaths: bool = kwargs.get('subpath', True)
        hon = cls(order=order)
        hon.fit(paths, subpaths=subpaths)
        return hon


class HigherOrderNode(Node, Path):
    """Base class of a higher order node."""

    def __init__(self, *args: Union[Node, Edge], uid: Optional[str] = None,
                 **kwargs: Any) -> None:

        # initializing the parent classes
        Node.__init__(self, uid, **kwargs)
        Path.__init__(self, *args, uid=uid, **kwargs)

        self['label'] = '-'.join([n.uid for n in self.nodes])

    @property
    def order(self) -> int:
        """Returns the order of the higher-order node."""
        return self.number_of_nodes(unique=False)

    def summary(self) -> str:
        """Returns a summary of the higher-order node.

        The summary contains the name, the used node class, the order, the
        number of nodes and the number of edges.

        If logging is enabled(see config), the summary is written to the log
        file and showed as information on in the terminal. If logging is not
        enabled, the function will return a string with the information, which
        can be printed to the console.

        Returns
        -------
        str

        Return a summary of the path.

        """
        summary = [
            'Uid:\t\t\t{}\n'.format(self.uid),
            'Type:\t\t\t{}\n'.format(self.__class__.__name__),
            'Order:\t\t\t{}\n'.format(self.order),
            'Number of unique nodes:\t{}\n'.format(self.number_of_nodes()),
            'Number of unique edges:\t{}'.format(self.number_of_edges()),
        ]
        return ''.join(summary)


class HigherOrderNodeCollection(PathCollection):
    """Higher-order node collection."""

    def __init__(self, nodes=None, edges=None) -> None:
        """Initialize the NodeCollection object."""

        # initialize the base class
        super().__init__(nodes=nodes, edges=edges)

        # class of objects
        self._path_class = HigherOrderNode

    @singledispatchmethod
    def __contains__(self, item) -> bool:
        """Returns if item is in path collection."""
        return super().__contains__(item)

    @__contains__.register(HigherOrderNode)  # type: ignore
    def _(self, item: HigherOrderNode) -> bool:
        _contain: bool = False
        if item in self.values():
            _contain = True
        return _contain

    @singledispatchmethod
    def add(self, *path, **kwargs: Any) -> None:
        """Add multiple paths."""
        super().add(*path, **kwargs)

    @add.register(HigherOrderNode)  # type: ignore
    def _(self, *path: HigherOrderNode, **kwargs: Any) -> None:

        # if checking is disabed add path directly to the collection
        if not kwargs.pop('checking', True):
            self._add(path[0], indexing=kwargs.pop('indexing', True))
            return

        # check if more then one path is given raise an AttributeError
        if len(path) != 1:
            for _path in path:
                self.add(_path)
            return

        # get path object
        _path = path[0]

        # update path attributes
        _path.update(**kwargs)

        # check if path already exists
        if _path not in self and _path.uid not in self.keys():

            # if path has len zero add single node
            if len(_path) == 0 and _path.start not in self.nodes:
                self.nodes.add(_path.start)

            # check if edges exists already
            for edge in _path.edges:
                if edge not in self.edges:
                    self.edges.add(edge)

            # add path to the paths
            self._add(_path)
        else:
            # raise error if path already exists
            self._if_exist(_path, **kwargs)

    def _if_exist(self, path: Any, **kwargs: Any) -> None:
        """If the node already exists"""
        pass


class HigherOrderEdge(Edge):
    """Base class of a higher order edge."""

    def __init__(self, v: HigherOrderNode, w: HigherOrderNode,
                 uid: Optional[str] = None, **kwargs: Any) -> None:
        # initializing the parent classes
        super().__init__(v=v, w=w, uid=uid, **kwargs)

    def summary(self) -> str:
        """Returns a summary of the higher-order edge.
        """
        s = [self.v.nodes[0].uid]
        for n in self.w.nodes:
            s.append(n.uid)

        return '(' + ', '.join(s) + ')'
        # summary = [
        #     'Uid:\t\t{}\n'.format(self.uid),
        #     'Type:\t\t{}\n'.format(self.__class__.__name__),
        #     'Source node:\t{}\n'.format(self.v.__repr__()),
        #     'Target node:\t{}'.format(self.w.__repr__()),
        # ]

        # return ''.join(summary)


class HigherOrderEdgeCollection(EdgeCollection):
    """Higher-order node collection."""

    def __init__(self, nodes: Optional[HigherOrderNodeCollection] = None) -> None:
        """Initialize the HigherOrderEdgeCollection object."""

        # initialize the base class
        super().__init__()

        self._nodes = HigherOrderNodeCollection()
        if nodes is not None:
            self._nodes = nodes

        # class of objects
        self._edge_class = HigherOrderEdge

    def __getitem__(self,
                    key: Union[str, tuple, Edge]) -> Union[Edge, EdgeSet, EdgeCollection]:
        """Returns a node object."""

        if isinstance(key, tuple):
            _node = tuple(self.nodes[i] for i in key)
            if self.multiedges:
                edge = self._nodes_map[_node]
            else:
                edge = self._nodes_map[_node][-1]

        elif isinstance(key, self._edge_class) and key in self:
            edge = key
        else:
            edge = self._map[key]
        return edge

    @singledispatchmethod
    def __contains__(self, item) -> bool:
        """Returns if item is in edges."""
        return super().__contains__(item)

    @__contains__.register(tuple)  # type: ignore
    @__contains__.register(list)
    def _(self, item: Union[tuple, list]) -> bool:
        """Returns if item is in edges."""
        _contain: bool = False

        if all([isinstance(i, (str, Node)) for i in item]):
            try:
                if tuple(self.nodes[i] for i in item) in self._nodes_map:
                    _contain = True
            except KeyError:
                pass
        elif all([isinstance(i, tuple) for i in item]):
            try:
                if self._nodes_map[(self.nodes[item[0]],
                                    self.nodes[item[1]])] is not None:
                    _contain = True
            except KeyError:
                pass

        return _contain

    @singledispatchmethod
    def add(self, *edge, **kwargs: Any) -> None:
        """Add multiple edges. """

        raise NotImplementedError

    @add.register(HigherOrderEdge)  # type: ignore
    def _(self, *edge: HigherOrderEdge, **kwargs: Any) -> None:
        super().add(*edge, **kwargs)

    @add.register(HigherOrderNode)  # type: ignore
    def _(self, *edge: HigherOrderNode, **kwargs: Any) -> None:
        super().add(*edge, **kwargs)

    @add.register(str)  # type: ignore
    def _(self, *edge: str, **kwargs: Any) -> None:
        super().add(*edge, **kwargs)


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
