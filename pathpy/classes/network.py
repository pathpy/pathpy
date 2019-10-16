#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : network.py -- Base class for a network
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Wed 2019-10-16 15:08 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, List, Dict, Tuple, Optional
from collections import defaultdict, Counter
# import datetime
# import sys
# from copy import deepcopy

from .. import logger, config
from . import Node, Edge, Path

# create logger for the Network class
log = logger(__name__)


class Network:
    """Base class for a network."""

    def __init__(self, *args: Path, uid: str = '',
                 directed: bool = True, **kwargs: Any) -> None:
        """Initialize the network object."""

        # check code
        self.check: bool = kwargs.get(
            'check_code', config['computation']['check_code'])

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

        # dictionary for network attributes
        self.attributes: dict = {}

        # add attributes to the network
        self.attributes.update(kwargs)

        # a dictionary containing node objects
        self._nodes: dict = defaultdict(dict)

        # a dictionary containing edge objects
        self._edges: dict = defaultdict(dict)

        # a dictionary containing path objects
        self._paths: dict = defaultdict(dict)

        # a counter fo the nodes
        self._node_counter: Counter = Counter()

        # a counter fo the edges
        self._edge_counter: Counter = Counter()

        # a counter fo the edges
        self._path_counter: Counter = Counter()

        # add paths
        self.add_paths_from(list(args))

        # # a dictionary containing tuple of node ids and edges
        # self._node_to_edges_map = defaultdict(list)

        # # a dictionary containing edge ids and node ids
        # self._edge_to_nodes_map = defaultdict(tuple)

        # pass

    # import external functions
    try:
        from ..io.csv import read_csv
    except ImportError:
        log.debug('pathpy.io faild to be imported')

    try:
        from ..subpaths.subpaths import subpath_counter, subpath_statistics
    except ImportError:
        log.debug('pathpy.subpaths faild to be imported')

    try:
        from ..algorithms.adjacency_matrix import adjacency_matrix
    except ImportError:
        log.debug('pathpy.algorithms faild to be import')

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
    #     """Display an interactive d3js visualisation of the network in jupyter.

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

    def __setitem__(self, key: Any, value: Any) -> None:
        """Add a specific attribute to the network.

        An attribute has a key and the corresponding value expressed as a pair,
        key: value.

        Parameters
        ----------
        key: Any
            Unique identifier for a corresponding value.

        value: Any
            A value i.e. attribute which is associated with the node.

        Examples
        --------
        Generate new network.

        >>> from pathpy import Network
        >>> net = Network()

        Add atribute to the network.

        >>> net[city] = 'Zurich'

        """
        self.attributes[key] = value

    def __getitem__(self, key: Any) -> Any:
        """Returns a specific attribute of the network.

        Parameters
        ----------
        key: any
            Key value for the attribute of the node.

        Returns
        -------
        any
            Returns the attribute of the node associated with the given key
            value.

        Raises
        ------
        KeyError
            If no attribute with the assiciated key is defined.

        Examples
        --------
        Generate new network.

        >>> from pathpy import Network
        >>> net = Node(city='London')

        Get the node attribute.

        >>> print(net['London'])
        """
        try:
            return self.attributes[key]
        except KeyError as error:
            log.error(
                'No attribute with key {} is defined!'.format(error))
            raise

    def __add__(self):
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

    @property
    def shape(self) -> Tuple[int, int]:
        """Return the size of the Network as tuple of number of nodes and number
        of edges"""
        return self.number_of_nodes(), self.number_of_edges()

    @property
    def directed(self) -> bool:
        """Return if the network is directed (True) or undirected (False)."""
        return self._directed

    # @property
    # def node_to_edges_map(self) -> Dict(List(str)):
    #     """Returns a a dictionary which maps the nodes to associated edges.

    #     Returns
    #     -------
    #     Dict(List(str))
    #         Returns a dict where the key is a tuple of node ids and the values
    #         are lists of edges which are associated with these nodes.

    #     Examples
    #     --------
    #     Generate simple network.

    #     >>> from pathpy import Network
    #     >>> net = Network()
    #     >>> net.add_edges_from([('ab1','a','b'),
    #     >>>                     ('ab2','a','b'),
    #     >>>                     ('bc','b','c')])
    #     >>> net.node_to_edges_map

    #     """
    #     return self._node_to_edges_map

    # @property
    # def edge_to_nodes_map(self) -> Dict(Tuple(str, str)):
    #     """Returns a a dictionary which maps the edges to associated nodes.

    #     Returns
    #     -------
    #     Dict(Tuple(str,str))
    #        Returns a dict where the key is the edge id and the values
    #        are tuples of associated node ids.

    #     Examples
    #     --------
    #     Generate simple network

    #     >>> from pathpy import Network
    #     >>> net = Network()
    #     >>> net.add_edges_from([('ab','a','b'),('bc','b','c')])
    #     >>> net.edge_to_nodes_map

    #     """
    #     return self._edge_to_nodes_map

    @property
    def nodes(self) -> Dict[str, Node]:
        return self._nodes

    @property
    def edges(self) -> Dict[str, Edge]:
        return self._edges

    @property
    def paths(self) -> Dict[str, Path]:
        return self._paths

    @property
    def node_counter(self) -> Counter:
        return self._node_counter

    @property
    def edge_counter(self) -> Counter:
        return self._edge_counter

    @property
    def path_counter(self) -> Counter:
        return self._path_counter

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

    def update(self, **kwargs: Any) -> None:
        """Update the attributes of the network.

        Parameters
        ----------
        kwargs : Any
            Attributes to add or update for the network as key=value pairs.

        Examples
        --------
        Update attributes.

        >>> from pathpy import network
        >>> net = Network(city='London')
        >>> net.attributes
        {'city': 'London'}

        Update the attributes.

        >>> net.update(city='Vienna', year=1850)
        >>> net.attributes
        {'city': 'Vienna', 'year': 1850)

        """
        self.attributes.update(kwargs)

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
            return sum(self.node_counter.values())

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
            return sum(self.edge_counter.values())

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
            return sum(self.path_counter.values())

    def add_paths_from(self, paths: List[Path]) -> None:
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
            self.add_path(path)

    def add_path(self, path: Path) -> None:
        """Add a single path to the network.

        Parameters
        ----------
        path: :py:class:`Path`
            The: py: class: `Edge` object, which will be added to the path.

        """

        if not isinstance(path, self.PathClass) and self.check:
            path = self._check_path(path)

        if path.uid not in self.paths:
            self.nodes.update(path.nodes)
            self.edges.update(path.edges)
            self.paths[path.uid] = path

            # update the edge and node count
            # NOTE: using a for loop is much faster
            # than using the default function Counter.update()!
            for edge in path.as_edges:
                self.edge_counter[edge] += 1
            for node in path.as_nodes:
                self.node_counter[node] += 1

            self.path_counter[path.uid] = 1
        else:
            # update the edge and node count
            # NOTE: using a for loop is much faster
            # than using the default function Counter.update()!
            for edge in path.as_edges:
                self.edge_counter[edge] += 1
            for node in path.as_nodes:
                self.node_counter[node] += 1

            self.path_counter[path.uid] += 1

        pass

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
