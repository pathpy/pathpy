#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : higher_order_network.py -- Basic class for a HON
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Fri 2019-11-08 16:24 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================

from __future__ import annotations
from copy import deepcopy
from typing import Any, List, Optional

from .. import logger, config
from .base import BaseHigherOrderNetwork
from .utils.separator import separator
from . import Node, Path, Network

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
        if self.network is not None:
            for path in self.network.paths.values():
                self.add_subpaths_from(path)

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
            return max(0, self.number_of_nodes()-1)

        else:
            # iterate over all nodes and count outdegree
            for node in self.nodes.values():
                degrees_of_freedom += max(0, len(node.outgoing)-1)

        # return degree of freedom
        return degrees_of_freedom

    def add_subpaths_from(self, path: Path) -> None:
        """Add sub-paths from a given path."""

        # check if the right object is provided.
        if not isinstance(path, self.PathClass) and self.check:
            path = self._check_path(path)

        _nodes: List[HigherOrderNode] = []
        for uid, subpath in path.subpaths(
                min_length=self.order-1,
                max_length=self.order-1,
                include_path=False).items():

            if subpath.uid not in self.nodes:
                node = HigherOrderNode(subpath)
            else:
                # TODO : Fix typing (self.nodes)
                node = self._nodes[subpath.uid]

            _nodes.append(node)

        if len(_nodes) > 0:
            # Get the uid for the first and hon path
            # TODO : Generate a mapping function net->hon and hon->net
            if _nodes[0].number_of_edges() == 0:
                nodes = [n.as_nodes[0] for n in _nodes]
                # TODO: fix edge separator
                edges = [v+'-'+w for v, w in list(zip(nodes[:-1], nodes[1:]))]
                net_uid = path.separator['path'].join(edges)
                hon_uid = self.separator['hon'].join(list(zip(*nodes))[0])
            else:
                edges = [n.as_edges for n in _nodes]
                net_uid = path.separator['path'].join(list(zip(*edges))[0])
                hon_uid = self.separator['hon'].join(list(zip(*edges))[0])

            _path = Path.from_nodes(
                _nodes, edge_separator=self.separator['hon'],
                **path.attributes.to_dict())

            # Check if the HON path is observed in the network
            if (net_uid in self.network.paths and hon_uid in _path.edges):
                _path.edges[hon_uid]['observed'] = \
                    self.network.paths.counter()[net_uid]

            # Add path to the hon
            self.add_path(_path)  # , frequency=path['frequency'])
        pass


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

    def summary(self) -> Optional[str]:
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
        if config['logging']['enabled']:
            for line in summary:
                log.info(line.rstrip())
            return None
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
