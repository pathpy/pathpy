#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : higher_order_network.py -- Basic class for a HON
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Fri 2020-03-27 12:23 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================

from __future__ import annotations
from typing import Any
from copy import deepcopy
from typing import Any, List, Optional

import numpy as np

from .. import logger, config
from .base import BaseHigherOrderNetwork
from .utils.separator import separator
from . import Node, Path, Network, Edge

# create logger for the Higher Order Network class
log = logger(__name__)


class HigherOrderNetwork(BaseHigherOrderNetwork, Network):
    """Base class for a Higher Order Network (HON)."""

    def __init__(self, network: Optional[Network] = None, order: int = 1,
                 directed: bool = True, **kwargs: Any) -> None:
        """Initialize the network object."""

        # initialize the base class
        super().__init__(directed=directed, **kwargs)

        self.separator: dict = separator(mode='hon', **kwargs)

        # order of this HigherOrderNetwork
        self._order: int = order

        # network objects used to generate this instance
        self.network = network

        # add paths form the provide network
        if self.network is not None and self.order > 0:
            self.add_subpaths_from(self.network)
        elif self.network is not None and self.order == 0:
            self.add_zero_order_from(self.network)

    # import external functions
    try:
        from ..algorithms.statistics.likelihoods import likelihood
    except ImportError:
        log.debug('pathpy.likelihood faild to be import')

    def _node_class(self) -> None:
        """Internal function to assign different Node classes."""
        self.NodeClass: Any = HigherOrderNode

    @property
    def order(self) -> int:
        """Return the order of the network."""
        return self._order

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
            degrees_of_freedom = max(0, self.number_of_nodes()-2)

        elif mode == 'old':
            # TODO : Remove this part after proper testing
            A = self.network.adjacency_matrix()

            degrees_of_freedom = int(
                (A ** self.order).sum()
                - np.count_nonzero((A ** self.order).sum(axis=0)))

        elif mode == 'ngram':
            number_of_nodes = self.network.number_of_nodes()
            degrees_of_freedom = (number_of_nodes ** self.order) * \
                (number_of_nodes - 1)

        elif mode == 'path':
            # iterate over all nodes and count outdegree
            # TODO : This should be only done with a null model
            log.debug('DoF only valide if it comes from a null model')
            for node in self.nodes.values():
                degrees_of_freedom += max(0, len(node.outgoing)-1)

        # return degree of freedom
        return degrees_of_freedom

    def add_subpaths_from(self, network: Network) -> None:
        """Add sub-paths from a given network."""

        # get all paths of length = order-1
        paths = network.subpaths.expand(order=self.order-1,
                                        include_path=True)

        # iterate over all paths
        for path in paths:

            # initialize temporary path
            _path = []

            # get frequency of the observed path
            frequency = path[0].attributes.frequency

            for v_path, w_path in zip(path[:-1], path[1:]):

                # generate higher order objects
                v = HigherOrderNode(v_path)
                w = HigherOrderNode(w_path)
                e = HigherOrderEdge(v, w)

                # check if hon edge is observed as path in the network
                if e.to_path_uid() in network.paths:
                    e['observed'] = network.paths.counter()[e.to_path_uid()]

                # add edge to temporary path
                _path.append(e)

            if len(_path) > 0:
                # generate path of higher order edges
                _hon_path = Path.from_edges(_path, frequency=frequency)

            elif len(_path) == 0 and len(path) == 1:
                # generate path of higher order nodes
                _hon_path = Path.from_nodes([HigherOrderNode(path[0])],
                                            frequency=frequency)

            # Add path to the hon
            self.add_path(_hon_path)

    def add_zero_order_from(self, network: Network) -> None:
        """Add sub-paths from a given network."""

        # get all paths of length = order-1
        paths = network.subpaths.expand(order=self.order,
                                        include_path=True)

        # generate a "dummy" start node
        start = HigherOrderNode(uid='start')

        for path in paths:

            # get frequency of the observed path
            frequency = path[0].attributes.frequency

            for w_path in path:

                # generate higher order node
                w = HigherOrderNode(w_path)

                # check if hon node is observed as path in the network
                if w.uid in network.paths:
                    w['observed'] = network.paths.counter()[w.uid]

                _hon_path = Path.from_nodes(
                    [start, w], frequency=frequency,
                    edge_separator=self.separator['hon'])

                # Add path to the hon
                self.add_path(_hon_path)

    @classmethod
    def from_network(cls, network: Network,
                     order: int = 1) -> HigherOrderNetwork:
        return cls(network, order=order)

    def _check_class(self):
        """Check which is the appropriated network class."""
        pass


class HigherOrderEdge(Edge):
    """Base class of a higher order edge."""

    def __init__(self, v: HigherOrderNode, w: HigherOrderNode, uid: str = None,
                 directed: bool = True, **kwargs: Any) -> None:
        # initializing the parent classes
        # _separator = kwargs.get(
        #     'separator', separator(mode='hon', **kwargs)['hon'])
        self.separator = separator(mode='hon', **kwargs)

        super().__init__(v=v, w=w, uid=uid, directed=directed,
                         separator=self.separator['hon'], **kwargs)

        self.separator = separator(mode='hon', **kwargs)
        self.order = v.order

    def to_path_uid(self):
        """Returns the path uid of the higher order edge."""

        if self.order > 1:
            edges = self.v.as_edges + [self.w.as_edges[-1]]
            return self.separator['path'].join(edges)
        elif self.order == 1:
            nodes = self.v.as_nodes + self.w.as_nodes
            return self.separator['edge'].join(nodes)
        else:
            log.warning('Hihger order edge has no path!')
            return None


class HigherOrderNode(Node, Path):
    """Base class of a higher order node which is also a path."""

    def __init__(self, *args: Path, uid: str = '',
                 directed: bool = True, **kwargs: Any) -> None:

        # set unique identifier of the higher oder node
        self._uid: str = uid

        # initializing the parent classes
        # TODO: Make it work with super()
        Node.__init__(self, uid, **kwargs)
        Path.__init__(self, uid=uid, directed=directed)

        # self.check = True
        # check if a path object is given
        # if not isinstance(path, Path) and self.check:
        #     path = self._check_path(path, **kwargs)

        # inherit properties for the path
        if args:
            self._inherit_from_path(args[0])

    def _check_path(self, path: Any, **kwargs: Any) -> Path:
        """Helperfunction to check if the edge is in the right format."""
        raise NotImplementedError

    def _inherit_from_path(self, path: Path, copy: bool = False) -> None:
        """Inherit attributes and properties from an other path object
        Parameters
        ----------
        path : :py:class:`Path` object
            The :py:class:`Path` object which bequest their attributes and
            properties.

        copy : Boole, optional (default = True)
            If enabled the attributes and properties are copied.

        """
        if copy:
            for k, v in path.__dict__.items():
                if k not in ['_uid']:
                    self.__dict__[k] = deepcopy(v)

        else:
            for k, v in path.__dict__.items():
                if k not in ['_uid']:
                    self.__dict__[k] = v

    # TODO: inherit this property form parent class
    @property
    def uid(self) -> str:
        """Returns the unique id of the path.

        Id of the path. If no id is assigned the path is called after the
        assigned edges. e.g. if the path has edges 'a-b' and 'c-d', the id is
        'a-b|b-c'.

        Returns
        -------
        str
            Returns the uid of the path as a string.

        Examples
        --------
        Generate a simple path

        >>> from pathpy import Path
        >>> p = Path('a','b','c')
        >>> p.uid
        'a-b|b-c'

        """
        if self._uid != '':
            return self._uid
        elif self.number_of_edges() > 0:
            return self.separator['path'].join(self.as_edges)
        elif self.number_of_nodes() > 0:
            return self.as_nodes[0]
        else:
            return str(id(self))

    @property
    def order(self) -> int:
        """Returns the order of the Node."""
        return self.number_of_nodes(unique=False)

    def summary(self) -> str:
        """Returns a summary of the path.

        The summary contains the name, the used path class, if it is directed
        or not, the number of unique nodes and unique edges, and the number of
        nodes in the path.

        Since a path can multiple times pass the same node and edge objects,
        the length of the path (i.e. the consecutive nodes) might be larger
        then the number of unique nodes.

        If logging is enabled (see config), the summary is written to the log
        file and showed as information on in the terminal. If logging is not
        enabled, the function will return a string with the information, which
        can be printed to the console.

        """
        summary = [
            'Name:\t\t\t{}\n'.format(self.name),
            'Type:\t\t\t{}\n'.format(self.__class__.__name__),
            'Directed:\t\t{}\n'.format(str(self.directed)),
            'Order:\t\t\t{}\n'.format(self.order),
            'Number of unique nodes:\t{}\n'.format(self.number_of_nodes()),
            'Number of unique edges:\t{}'.format(self.number_of_edges()),
            # 'Path length (# edges):\t{}'.format(len(self))
        ]

        # TODO: Move this code to a helper function
        if config['logging']['verbose']:
            for line in summary:
                log.info(line.rstrip())
            return ''
        else:
            return ''.join(summary)

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
