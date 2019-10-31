#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : network.py -- Base class for a network
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2019-10-31 14:07 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, List, Dict, Tuple, Optional, Sequence

from .. import logger, config
from .base import BaseNetwork
from .base import NodeDict, EdgeDict, PathDict
from .utils.separator import separator
from .utils._check_node import _check_node
from .utils._check_edge import _check_edge
from . import Node, Edge, Path

# create logger for the Network class
log = logger(__name__)


class Network(BaseNetwork):
    """Base class for a network."""

    def __init__(self, *args: Path, uid: str = '',
                 directed: bool = True, **kwargs: Any) -> None:
        """Initialize the network object."""

        # initialize the base class
        super().__init__(**kwargs)

        # Classes of the Node, Edge and Path objects
        # TODO: Probably there is a better solution to have different Node and
        # Edge classes for different Network sub classes
        self._node_class()
        self._edge_class()
        self._path_class()

        # set unique identifier of the network
        self._uid: str = uid

        # inidcator whether the network is directed or undirected
        self._directed: bool = directed

        # a dictionary containing node objects
        self._nodes: NodeDict = NodeDict(dict)

        # a dictionary containing edge objects
        self._edges: EdgeDict = EdgeDict(dict)

        # a dictionary containing path objects
        self._paths: PathDict = PathDict(dict)

        # use separator if given otherwise use config default value
        # TODO: Add a network mode
        self.separator: dict = separator()

        # add attributes to the network
        self.attributes.update(**kwargs)

        # add paths
        self.add_paths_from(list(args))

    # import external functions
    try:
        from ..io.csv import read_csv
    except ImportError:
        log.debug('pathpy.io faild to be imported')

    try:
        from ..algorithms.subpaths import subpath_info, subpath_counter
    except ImportError:
        log.debug('pathpy.sub faild to be imported')

    try:
        from ..algorithms.matrices import adjacency_matrix, transition_matrix
    except ImportError:
        log.debug('pathpy.adjacency_matrix faild to be import')

    def _node_class(self) -> None:
        """Internal function to assign different Node classes."""
        self.NodeClass = Node

    def _edge_class(self) -> None:
        """Internal function to assign different Edge classes."""
        self.EdgeClass = Edge

    def _path_class(self) -> None:
        """Internal function to assign different Path classes."""
        self.PathClass = Path

    def __repr__(self) -> str:
        """Return the description of the network.

        Returns
        -------
        str
            Returns the description of the network with the class, the name (if
            deffined) and the assigned system id.

        Examples
        --------
        Genarate new network

        >>> from pathpy import Network
        >>> net = Network()
        >>> print(net)

        """
        return '<{} object {} at 0x{}x>'.format(self._desc(),
                                                self.name, id(self))

    # def _repr_html_(self) -> str:
    #     """Display an interactive d3js visualisation
    # of the network in jupyter.

    #     Returns
    #     -------
    #     html
    #         Returns the html code for the d3js visualisation.

    #     Examples
    #     --------
    #     Genarate simple network

    #     >>> from pathpy import Network
    #     >>> net = Network()
    #     >>> net.add_edges_from([('a','b'),('b','c')]
    #     >>> net

    #     """
    #     from pathpy import plot
    #     return plot(self)

    def _desc(self) -> str:
        """Return a string *Network*."""
        return '{}'.format(self.__class__.__name__)

    def __add__(self):
        """Add two networks together."""
        raise NotImplementedError

    @property
    def uid(self) -> str:
        """Returns the unique id of the network.

        Id of the network. If no id is assigned the network is called after the
        system id.

        Returns
        -------
        str
            Returns the uid of the path as a string.

        Examples
        --------
        Generate a simple network

        >>> from pathpy import Network
        >>> p = Network(uid='testnet')
        >>> p.uid
        testnet

        Generate a simple network without uid.
        >>> p = Network()
        >>> p.uid
        139862868063504

        """
        if self._uid != '':
            return self._uid
        else:
            return str(id(self))

    @property
    def name(self) -> str:
        """Return the name of the network if defined, else an empty space.

        The name of the network is an attribute of the network, in order to
        make the classification and identification easier. However the name of
        the network do not have to be unique like an id. Therefore, the name of
        the network can be changed.

        Returns
        -------
        str
            Returns the name of the network (if defined), otherwise an empty
            string is returnd.

        Examples
        --------
        Create an empty network structure with no nodes and no edges.

        >>> from pathpy import Network
        >>> net = Network()

        Add a name of the network

        >>> net.name = 'my test network'
        >>> print(net.name)

        Create a new network with name.

        >>> net = Network(name='an other network')
        >>> print(net.name)

        """
        return self.attributes.get('name', '')

    @name.setter
    def name(self, name: str) -> None:
        """Set the name of the network.

        Parameters
        ----------
        name : str
            New name of the network.

        """
        self.attributes['name'] = name

    # TODO: Add also the paths as a shape inidcator
    @property
    def shape(self) -> Tuple[int, int]:
        """Return the size of the Network as tuple of number of nodes and number
        of edges"""
        return self.number_of_nodes(), self.number_of_edges()

    @property
    def directed(self) -> bool:
        """Return if the network is directed (True) or undirected (False)."""
        return self._directed

    @property
    def nodes(self) -> NodeDict:
        """Return the associated nodes of the network.

        Returns
        -------
        NodeDict
            Return a dictionary with the :py:class:`Node` uids as key and the
            :py:class:`Node` objects as values, associated with the network.

        Examples
        --------
        Generate a simple network.

        >>> from pathpy import Path, Network
        >>> p = Path('a','b','c')
        >>> net = Network(p)

        Get the nodes of the network

        >>> net.nodes
        {'a': Node a, 'b': Node b, 'c': Node c}
        """
        return self._nodes

    @property
    def edges(self) -> EdgeDict:
        """Return the associated edges of the network.

        Returns
        -------
        EdgeDict
            Return a dictionary with the :py:class:`Edge` uids as key and the
            :py:class:`Edge` objects as values, associated with the network.

        Examples
        --------
        Generate a simple network.

        >>> from pathpy import Path, Network
        >>> p = Path('a','b','c')
        >>> net = Network(p)

        Get the edges of the network

        >>> net.edges
        {'a-b': Edge a-b, 'b-c': Edge b-c}
        """
        return self._edges

    @property
    def paths(self) -> PathDict:
        """Return the associated pathss of the network.

        Returns
        -------
        PathDict
            Return a dictionary with the :py:class:`Path` uids as key and the
            :py:class:`Path` objects as values, associated with the network.

        Examples
        --------
        Generate a simple network.

        >>> from pathpy import Path, Network
        >>> p = Path('a','b','c')
        >>> net = Network(p)

        Get the paths of the network

        >>> net.paths
        {'a-b|b-c': Path a-b|b-c}
        """
        return self._paths

    def summary(self) -> Optional[str]:
        """Returns a summary of the network.

        The summary contains the name, the used network class, if it is
        directed or not, the number of nodes and edges.

        If logging is enabled (see config), the summary is written to the log
        file and showed as information on in the terminal. If logging is not
        enabled, the function will return a string with the information, which
        can be printed to the console.

        Returns
        -------
        str
            Retruns a summary of important network properties.

        """
        summary = [
            'Name:\t\t\t{}\n'.format(self.name),
            'Type:\t\t\t{}\n'.format(self.__class__.__name__),
            'Directed:\t\t{}\n'.format(str(self.directed)),
            'Number of unique nodes:\t{}\n'.format(self.number_of_nodes()),
            'Number of unique edges:\t{}'.format(self.number_of_edges()),
            'Number of unique paths:\t{}'.format(self.number_of_paths()),
            'Number of total paths:\t{}'.format(
                self.number_of_paths(unique=False)),
        ]
        if config['logging']['enabled']:
            for line in summary:
                log.info(line.rstrip())
            return None
        else:
            return ''.join(summary)

    def number_of_nodes(self, unique: bool = True) -> int:
        """Return the number of nodes in the network.

        Parameters
        ----------
        unique : bool, optional (default = True)
            If unique is True only the number of unique nodes in the network is
            returnd.

        Returns
        -------
        int
            Returns the number of nodes in the network.

        Examples
        --------
        Generate a simple network.

        >>> from pathy import Path, Network
        >>> net = Network(Path('a', 'b', 'c', 'a', 'b'))

        Get the number of unique nodes:

        >>> p.number_of_nodes()
        3

        Get the number of all nodes in the network:

        >>> p.number_of_nodes(unique=False)
        5

        """
        if unique:
            return len(self.nodes)
        else:
            return sum(self.nodes.counter().values())

    def number_of_edges(self, unique: bool = True) -> int:
        """Return the number of edges in the network.

        Parameters
        ----------
        unique : bool, optional (default = True)
            If unique is True only the number of unique edges in the network is
            returnd.

        Returns
        -------
        int
            Returns the number of edges in the network.

        Examples
        --------
        Generate a simple network.

        >>> from pathy import Path, Network
        >>> net = Network(Path('a', 'b', 'c', 'a', 'b'))

        Get the number of unique edges:

        >>> net.number_of_edges()
        3

        Get the number of all edges in the path:

        >>> net.number_of_edges(unique=False)
        4

        """
        if unique:
            return len(self.edges)
        else:
            return sum(self.edges.counter().values())

    def number_of_paths(self, unique: bool = True) -> int:
        """Return the number of paths in the network.

        Parameters
        ----------
        unique : bool, optional (default = True)
            If unique is True only the number of unique paths in the network is
            returnd.

        Returns
        -------
        int
            Returns the number of paths in the network.

        Examples
        --------
        Generate a simple network.

        >>> from pathy import Path, Network
        >>> p1 = Path('a', 'b', 'c')
        >>> p2 = Path('d', 'b', 'e')
        >>> net = Network(p1, p2 , p1)

        Get the number of unique paths:

        >>> net.number_of_paths()
        2

        Get the number of all paths in the path:

        >>> net.number_of_paths(unique=False)
        3

        """
        if unique:
            return len(self.paths)
        else:
            return sum(self.paths.counter().values())

    def add_nodes_from(self, nodes: List[Node], **kwargs: Any) -> None:
        """Add multiple nodes from a list.

        Parameters
        ----------
        nodes : List[Node]

            Nodes from a list of :py:class:`Node` objects are added to the
            network.

        kwargs : Any, optional (default = {})
            Attributes assigned to all nodes in the list as key=value pairs.

        """
        # iterate over a list of nodes
        # TODO: parallelize this function
        for node in nodes:
            self.add_node(node, **kwargs)

    def add_edges_from(self, edges: Sequence[Edge], **kwargs: Any) -> None:
        """Add multiple edges from a list.

        Parameters
        ----------
        nodes: List[Edge]

            Edges from a list of: py: class:`Edge` objects are added to the
            network.

        kwargs: Any, optional(default={})
            Attributes assigned to all nodes in the list as key = value pairs.

        """

        # iterate over a list of nodes
        # TODO: parallelize this function
        for edge in edges:
            self.add_edge(edge, **kwargs)

    def add_paths_from(self, paths: Sequence[Path], **kwargs: Any) -> None:
        """Add multiple paths from a list.

        Parameters
        ----------
        paths: List[Path]
            Paths from a list of: py: class:`path` objects are added to the
            network.

        Examples
        --------
        Generate a simple network generated by paths.

        >>> from pathpy import Path,Network
        >>> p1 = Path('a', 'c', 'd')
        >>> p2 = Path('b', 'c', 'e')
        >>> net = Network()
        >>> net.add_paths_from([p1, p2])
        net.number_of_paths()
        2

        """
        for path in paths:
            self.add_path(path, **kwargs)

    def add_node(self, node: Node, **kwargs: Any) -> None:
        """Add a single node to the network.

        Parameters
        ----------
        node : :py:class:`Node`
            The :py:class:`Node` object, which will be added to the network.

        kwargs : Any, optional (default = {})
            Attributes assigned to the node as key=value pairs.

        Examples
        --------
        Generate an empty network and add single nodes.

        >>> from pathpy import Node, Network
        >>> a = Node('a')
        >>> net = Network()
        >>> net.add_node(a, color='azur')
        >>> net.nodes
        {'a': Node a}

        Generate new node from string.

        >>> net.add_node('b', color='blue')
        >>> net.nodes
        {'a': Node a, 'b': Node b}

        """

        # check if the right object is provided.
        if self.check:
            node = _check_node(self, node, **kwargs)

        # add new node to the network or update modified node
        # TODO: Test the speed of the if statement
        if (node.uid not in self.nodes or
                (node.uid in self.nodes and node != self.nodes[node.uid])):
            self.nodes[node.uid] = node

        # update node counter
        self.nodes.increase_counter(node.uid, node.attributes.frequency)

    def add_edge(self, edge: Edge, *args, **kwargs: Any) -> None:
        """Add a single edge to the network."""

        # check if the right object is provided
        if self.check:
            edge = _check_edge(self, edge, *args, **kwargs)

        # add new edge to the path or update modified edge
        if (edge.uid not in self.edges or
                (edge.uid in self.edges and edge != self.edges[edge.uid])):
            self.nodes.update(edge.nodes)
            self.edges[edge.uid] = edge

        # update counters
        self.edges.increase_counter(edge.uid, edge.attributes.frequency)
        self.nodes.increase_counter(edge.nodes, edge.attributes.frequency)

    def add_path(self, path: Path, frequency: int = 1, **kwargs: Any) -> None:
        """Add a single path to the network.

        Parameters
        ----------
        path: :py:class:`Path`
            The: py: class: `Edge` object, which will be added to the path.

        """

        # check if the right object is provided
        if not isinstance(path, self.PathClass) and self.check:
            path = self._check_path(path, **kwargs)

        # update nodes, edges and the path
        if path.uid not in self.paths:
            self.nodes.update(path.nodes)
            self.edges.update(path.edges)
            self.paths[path.uid] = path

        # increas the counters
        self.nodes.increase_counter(path.as_nodes, path.attributes.frequency)
        self.edges.increase_counter(path.as_edges, path.attributes.frequency)
        self.paths.increase_counter(path.uid, path.attributes.frequency)

    def remove_node(self, node: str) -> None:
        """Remove a single node from the network."""
        raise NotImplementedError

    def remove_edge(self, path: str) -> None:
        """Remove a single edge from the network."""
        raise NotImplementedError

    def remove_path(self, path: str) -> None:
        """Remove a single path from the network."""
        raise NotImplementedError


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
