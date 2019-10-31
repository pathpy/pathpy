#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : higher_order_network.py -- Basic class for a HON
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2019-10-31 12:21 juergen>
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

            # assign the frequency to the hon edges
            # for edge in _path.edges.values():
            #     edge.update_frequency(path.frequency)

            # Check if the HON path is observed in the network
            if (net_uid in self.network.paths and hon_uid in _path.edges):
                _path.edges[hon_uid]['observed'] = \
                    self.network.paths.counter()[net_uid]

            # Add path to the hon
            self.add_path(_path)
        pass


class HigherOrderNode(Node, Path):
    """Base class of a higher order node which is also a path."""

    def __init__(self, path: Path,
                 directed: bool = True, **kwargs: Any) -> None:

        self.check = True
        # check if a path object is given
        if not isinstance(path, Path) and self.check:
            path = self._check_path(path, **kwargs)

        # generate unique id for the higher order node
        uid = '{}'.format(path.uid)

        # initializing the parent classes
        # TODO: Make it work with super()
        Node.__init__(self, uid, **kwargs)
        Path.__init__(self, uid=uid, directed=directed)

        # inherit properties for the path
        self._inherit_from_path(path)

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
