#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : network.py -- Base class for a network
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Tue 2020-03-31 16:29 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, List, Tuple, Optional, Sequence, Set

from .. import logger, config
from .base import BaseNetwork
from .base import BaseDirectedNetwork, BaseUndirectedNetwork
from .base import BaseDirectedTemporalNetwork, BaseUndirectedTemporalNetwork
from .base import NodeDict, EdgeDict, PathDict
from .utils.separator import separator
from .utils._check_node import _check_node
from .utils._check_edge import _check_edge
from .utils._check_path import _check_path
from .utils._check_str import _check_str
from . import Node, Edge, Path

# create logger for the Network class
log = logger(__name__)


class Network(BaseNetwork):
    """Base class for a network.

    A network is a structure amounting to a set of objects in which some of the
    objects are related to each other. The objects correspond to mathematical
    abstractions called nodes (or vertices) and each of the related pairs of
    nodes is called an edge (or link). Furthermore, related edges form
    paths. Thereby, the edges and paths may be directed or undirected.

    In ``pathpy`` a :py:class:`Network` stores :py:class:`Node`,
    :py:class:`Edge` and :py:class:`Path` objects with optional data or
    attributes. Instances of this class capture a network that can be directed,
    undirected, unweighted or weighted as well as static or temporal. Self
    loops and multiple (parallel) edges are allowed.

    Parameters
    ----------

    uid : str, optional (default = None)

        The parameter ``uid`` is the unique identifier for the network. This
        option can late be used for multi-layer networks. Currently the ``uid``
        of the network is not in use.

    directed : bool, optional  (default = True)

        Specifies if a network contains directed edges and paths, i.e u->v->w
        or undirected edges and paths i.d. u-v-w.  If ``True`` the all
        subsequent objects are directed, i.e. quantities can only transmited
        from the source node ``v`` to the traget node ``w``. If ``False`` the
        al subsequent obects are undirected, i.e. quantities can be transmited
        in both directions. Per default networks in ``pathpy`` are directed.

    temporal : bool, optional (default = False)

        A :py:class:`Network` can be static or temporal. If ``True`` the
        network is temporal; i.e. properties of nodes, edges or paths can
        change over time. If ``False`` the network is static, i.e. no changes
        over time. Per default the network is assumed to be static.

    args : Path

        :py:class:`Path` objects can be used as arguments to build a
        network. While the default options is using paths, `pathpy` also
        supports :py:class:`Node`, :py:class:`Edge` objects and ``str`` uids to
        generate networks.

    kwargs : Any

        Keyword arguments to store network attributes. Attributes are added to
        the network as ``key=value`` pairs.

    See Also
    --------
    Node, Edge, Path

    Examples
    --------
    Examples
    --------
    Create an empty network structure with no nodes, edges or paths.

    >>> form pathpy import Node, Edge, Path, Network
    >>> net = Network()

    Some properties of the network are: the name, if directed or if temporal

    >>> net.name = 'my test network'
    >>> net.name
    my test network

    Per default the network is directed and static

    >>> net.directed
    True
    >>> net.temporal
    False

    The network can be grown in several ways.

    **Nodes:**

    Add single node to the network.

    >>> net.add_node('a')

    Also a node object can be added to the network.

    >>> b = Node('b')
    >>> net.add_node(b)

    In addition to single nodes, also nodes from a list can added to the
    network at once. Attributes are assigned to all nodes.

    >>> net.add_nodes_from(['c','d','e'], color='green')
    >>> net.nodes['c']['color']
    'green'

    Single nodes can be removed.

    >>> net.remove_node('c')

    While multiple nodes can be removed from a list of nodes.

    >>> net.remove_nodes_from(['a','b'])

    **Edges**

    Adding a singe new edge to the network.

    >>> net = Network()
    >>> net.add_edge('a-b', length = 10)

    Adding an existing edge object to the network.

    >>> e = Edge('b', 'c', length = 5)
    >>> net.add_edge(e)
    >>> net.number_of_edges()
    2

    **Path**

    Adding a single path to the network.

    >>> net = Network()
    >>> p = Path('a-b-c')
    >>> net.add_path(p)
    >>> net.number_of_nodes()
    3
    >>> net.number_of_edges()
    2
    >>> net.number_of_paths()
    1

    **str uids**

    String uids can be used to add objects to the network.

    >>> net = Network('a','b-c','c-d-e')
    >>> net.number_of_nodes()
    5
    >>> net.number_of_edges()
    3
    >>> net.number_of_paths()
    1

    Plot a network.

    >>> net = Network('a-b-c-d','b-e-f-c')
    >>> plt = net.plot()
    >>> plt.show('png')

    .. plot::

       import pathpy as pp
       net = pp.Network('a-b-c-d','b-e-f-c')
       plt = net.plot()
       plt.show('png')

    """

    def __init__(self, *args: Path, uid: str = '',
                 directed: bool = True, temporal: bool = False,
                 **kwargs: Any) -> None:
        """Initialize the network object."""

        # initialize the base class
        super().__init__(**kwargs)

        # set unique identifier of the network
        self._uid: str = uid

        # inidcator whether the network is directed or undirected
        self._directed: bool = directed

        # indicator whether the network is temporal or static
        self._temporal: bool = temporal

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

        # add objects from args if given
        if args:
            self._add_args(*args)
        # self.add_paths_from(list(args))

        # check the network class
        self._check_class()

    try:
        # import sub paths object
        from ..algorithms.statistics.subpaths import SubPaths as _SubPathsConstructor

        # initialize a local variable to store sub paths
        # NOTE: this will be only created if the module is loaded
        _subpaths = None

        # add property to the network
        @property
        def subpaths(self):
            """Returns a SubPath object."""

            # check if alread a sub path object is initialzed
            if self._subpaths is None:

                # if not generate initialize new object
                self._subpaths = self._SubPathsConstructor(self)

            # return sub path object
            return self._subpaths

    except ImportError:
        # if library could not be loaded raise a warning
        log.warning('pathpy.subpaths failed to be imported')

    try:
        from ..algorithms.matrices import adjacency_matrix, transition_matrix
    except ImportError:
        log.debug('pathpy.matrices failed to be imported')

    try:
        from ..visualizations.plot import plot
    except ImportError:
        log.debug('pathpy.plot failed to be imported')

    try:
        from ..io.edgelist import read_edgelist
    except ImportError:
        log.debug('pathpy.io.edgelist failed to be imported')

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
        <DirectedNetwork object  at 0x139942320561264x>

        """
        return '<{} object {} at 0x{}x>'.format(self._desc(),
                                                self.name, id(self))

    def _desc(self) -> str:
        """Return a string *Network*."""
        return '{}'.format(self.__class__.__name__)

    def __str__(self) -> str:
        """Print the summary of the network.

        The summary contains the name, the used network class, if it is
        directed or not, the number of nodes and edges.

        If logging is enabled (see config), the summary is written to the log
        file and showed as information on in the terminal. If logging is not
        enabled, the function will return a string with the information, which
        can be printed to the console.

        """
        return self.summary()

    def __add__(self):
        """Add two networks together."""
        raise NotImplementedError

    @property
    def uid(self) -> str:
        """Returns the unique id of the network.

        Uid of the network. If no uid is assigned the network is called after the
        system id.

        Returns
        -------
        str

            Returns the uid of the network as a string.

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
        """Return the name of the network if defined, else an empty string.

        The name of the network is an attribute of the network, in order to
        make the classification and identification easier. However the name of
        the network do not have to be unique like an uid. Therefore, the name of
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
        >>> net.name
        'my test network'

        Create a new network with a name.

        >>> net = Network(name='an other network')
        >>> net.name
        'an other network'

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
    def shape(self) -> Tuple[int, int, int]:
        """Return the size of the Network as tuple of number of nodes, edges and paths.

        Returns
        -------
        Tuple[int, int, int]

            Size of the network as tuple: (number of nodes, number of edges,
            number of paths)

        Examples
        --------
        Genarate a simple network

        >>> form pathpy import Network
        >>> net = Network('a-b-c-d','b-e-f-c')
        >>> net.shape
        (6, 6, 2)

        """
        return self.number_of_nodes(), self.number_of_edges(), self.number_of_paths()

    @property
    def directed(self) -> bool:
        """Return if the network is directed (True) or undirected (False).

        Returns
        -------
        bool

            Retun ``True`` if the network is directed or ``False`` if the
            network is undirected.

        Examples
        --------
        Generate an undirected network.

        >>> from pathpy import Network
        >>> net = Network('a-b', directed=False)
        >>> net.directed
        False
        >>> net.edges['a-b'].directed
        False

        """
        return self._directed

    @property
    def temporal(self) -> bool:
        """Return if the network is temproal (True) or static (False).

        Returns
        -------
        bool

            Retun ``True`` if the network is temporal or ``False`` if the
            network is static.

        """
        return self._temporal

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

        >>> from pathpy import Network
        >>> net = Network('a-b-c')

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

        >>> from pathpy import Network
        >>> net = Network('a-b-c')

        Get the edges of the network

        >>> net.edges
        {'a-b': Edge a-b, 'b-c': Edge b-c}

        """
        return self._edges

    @property
    def paths(self) -> PathDict:
        """Return the associated paths of the network.

        Returns
        -------
        PathDict

            Return a dictionary with the :py:class:`Path` uids as key and the
            :py:class:`Path` objects as values, associated with the network.

        Examples
        --------
        Generate a simple network.

        >>> from pathpy import Path, Network
        >>> net = Network('a-b-c')

        Get the paths of the network

        >>> net.paths
        {'a-b|b-c': Path a-b|b-c}

        """
        return self._paths

    @property
    def node_index(self) -> dict:
        """Returns a dictionary that maps node uids to 
        integer indices. 
        
        The indices of nodes correspond to the row/column 
        ordering of nodes in any list/array/matrix representation
        generated by pathpy, e.g. for degrees.sequence or 
        adjacency_matrix.

        Returns
        -------
        dict
            maps node uids to zero-based integer index

        """
        return dict(zip(self.nodes, range(self.number_of_nodes())))

    def summary(self) -> str:
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
            Returns a summary of important network properties.

        """
        summary = [
            'Name:\t\t\t{}\n'.format(self.name),
            'Type:\t\t\t{}\n'.format(self.__class__.__name__),
            # 'Directed:\t\t{}\n'.format(str(self.directed)),
            'Number of unique nodes:\t{}\n'.format(self.number_of_nodes()),
            'Number of unique edges:\t{}\n'.format(self.number_of_edges()),
            'Number of unique paths:\t{}\n'.format(self.number_of_paths()),
            'Number of total paths:\t{}'.format(
                self.number_of_paths(unique=False)),
        ]

        # TODO: Move this code to a helper function
        if config['logging']['verbose']:
            for line in summary:
                log.info(line.rstrip())
            return ''
        else:
            return ''.join(summary)

    def number_of_nodes(self, unique: bool = True) -> int:
        """Return the number of nodes in the network.

        Parameters
        ----------
        unique : bool, optional (default = True)

            If unique is ``True`` only the number of unique nodes in the
            network is returnd.

        Returns
        -------
        int

            Returns the number of nodes in the network.

        Examples
        --------
        Generate a simple network.

        >>> from pathy import Path, Network
        >>> net = Network('a-b-c-a-b')

        Get the number of unique nodes:

        >>> net.number_of_nodes()
        3

        Get the number of all observed node visits in the network:

        >>> net.number_of_nodes(unique=False)
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

            If unique is ``True`` only the number of unique edges in the
            network is returnd.

        Returns
        -------
        int

            Returns the number of edges in the network.

        Examples
        --------
        Generate a simple network.

        >>> from pathy import Path, Network
        >>> net = Network('a-b-c-a-b')

        Get the number of unique edges:

        >>> net.number_of_edges()
        3

        Get the number of all observed edges in the path:

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

            If unique is ``True`` only the number of unique paths in the
            network is returnd.

        Returns
        -------
        int

            Returns the number of paths in the network.

        Examples
        --------
        Generate a simple network.

        >>> from pathy import Network
        >>> net = Network('a-b-c', 'd-b-e', 'a-b-c')

        Get the number of unique paths:

        >>> net.number_of_paths()
        2

        Get the number of all observed paths in the path:

        >>> net.number_of_paths(unique=False)
        3

        """
        if unique:
            return len(self.paths)
        else:
            return sum(self.paths.counter().values())

    def add_nodes_from(self, nodes: List[Node], **kwargs: Any) -> None:
        """Add multiple nodes from a list to the network.

        Parameters
        ----------
        nodes : List[Node]

            Nodes from a list of :py:class:`Node` objects are added to the
            networ.

        kwargs: Any, optional(default={})

            Attributes assigned to all nodes in the list as ``key=value`` pairs.

        Examples
        --------
        Generate some nodes and add them to the network

        >>> from pathpy import Node, Network
        >>> a = Node('a')
        >>> b = Node('b')
        >>> c = Node('c')
        >>> net = Network()
        >>> net.add_nodes_from([a, b, c])
        >>> net.number_of_nodes()
        3

        """
        # iterate over a list of nodes
        # TODO: parallelize this function
        for node in nodes:
            self.add_node(node, **kwargs)

    def add_edges_from(self, edges: Sequence[Edge], **kwargs: Any) -> None:
        """Add multiple edges from a list to the network.

        Parameters
        ----------
        nodes : List[Edge]

            Edges from a list of :py:class:`Edge` objects are added to the
            network.

        kwargs : Any, optional(default={})

            Attributes assigned to all edges in the list as ``key=value``
            pairs.

        Examples
        --------
        Generate some edges and add them to the network.

        >>> from pathpy import Edge, Network
        >>> e1 = Edge('a', 'b')
        >>> e2 = Edge('b', 'c')
        >>> net = Network()
        >>> net.add_edges_from([e1, e2])
        >>> net.number_of_edges()
        2

        """

        # iterate over a list of nodes
        # TODO: parallelize this function
        for edge in edges:
            self.add_edge(edge, **kwargs)

    def add_paths_from(self, paths: Sequence[Path], **kwargs: Any) -> None:
        """Add multiple paths from a list to the network.

        Parameters
        ----------
        paths: List[Path]

            Paths from a list of :py:class:`Path` objects are added to the
            network.

        Examples
        --------
        Generate some paths and add them to the network,

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
        node : Node

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

        Generate new node from string uid.

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

        # check the network class
        self._check_class()

    def add_edge(self, edge: Edge, *args, **kwargs: Any) -> None:
        """Add a single edge to the network.

        Parameters
        ----------
        edge : Edge

            The :py:class:`Edge` object, which will be added to the network.

        kwargs : Any, optional(default={})

            Attributes assigned to the edge as ``key=value`` pairs.

        Examples
        --------
        Generate an edge and add it to the network.

        >>> from pathpy import Edge, Network
        >>> e = Edge('a', 'b')
        >>> net = Network()
        >>> net.add_edge(e)
        >>> net.number_of_edges()
        1

        Add an other edge.

        >>> net.add_edge('b-c')
        >>> net.number_of_edges()
        2

        """

        # check if the right object is provided
        if self.check:
            edge = _check_edge(self, edge, *args,
                               directed=self.directed, **kwargs)

        # add new edge to the network or update modified edge
        if (edge.uid not in self.edges or
                (edge.uid in self.edges and edge != self.edges[edge.uid])):
            self.nodes.add_edge(edge)
            self.edges.add_edge(edge)

        # add related object to the edge dictionary
        # TODO make function to do this
        # self.edges.related[edge.uid].nodes[edge.v.uid] = edge.v
        # self.edges.related[edge.uid].nodes[edge.w.uid] = edge.w

        # update counters
        # TODO find better way to do this
        self.edges.increase_counter(edge.uid, edge.attributes.frequency)
        self.nodes.increase_counter(edge.nodes, edge.attributes.frequency)

        # check the network class
        self._check_class()

    def add_path(self, path: Path, *args: Any, **kwargs: Any) -> None:
        """Add a single path to the network.

        Parameters
        ----------
        path : Path

            The :py:class:`Path` object, which will be added to the network.

        kwargs : Any, optional(default={})

            Attributes assigned to the path as ``key=value`` pairs.

        Examples
        --------
        Generate a path and add it to the network.

        >>> from pathpy import Path, Network
        >>> p = Path('a', 'b', 'c')
        >>> net = Network()
        >>> net.add_path(p)
        >>> net.number_of_paths()
        1

        Add an other edge.

        >>> net.add_path('e-f-g')
        >>> net.number_of_paths()
        2

        """
        # check if the right object is provided
        if self.check:
            path = _check_path(self, path, *args, **kwargs)

        # add new path to the network or update modified path
        if (path.uid not in self.paths or
                (path.uid in self.paths and path != self.paths[path.uid])):
            # self.nodes.add(path.nodes)
            self.nodes.add_edges(path.edges)
            self.edges.add_edges(path.edges)
            self.paths.add_path(path)
            #self.paths[path.uid] = path

        # increas the counters
        self.nodes.increase_counter(path.as_nodes, path.attributes.frequency)
        self.edges.increase_counter(path.as_edges, path.attributes.frequency)
        self.paths.increase_counter(path.uid, path.attributes.frequency)

        # check the network class
        self._check_class()

    def _add_args(self, *args: Any) -> None:
        """Add args to the network."""

        # iterate over all given arguments
        for arg in args:

            # if arg is a Path add the path
            if isinstance(arg, Path):
                self.add_path(arg)

            # if arg is an Edge add the edge
            elif isinstance(arg, Edge):
                self.add_edge(arg)

            # if arg is a Node add the node
            elif isinstance(arg, Node):
                self.add_node(arg)

            # if arg is a string, check the string and add accordingly
            elif isinstance(arg, str) and self.check:

                # check the given string
                objects = _check_str(self, arg, expected='path')

                # iterate over the cleand string and append objects
                for string, mode in objects:
                    if mode == 'path':
                        self.add_paths_from(string)
                    elif mode == 'edge':
                        self.add_edges_from(string)
                    elif mode == 'node':
                        self.add_nodes_from(string)
            else:
                log.error('Invalide argument "{}"!'.format(arg))
                raise AttributeError

    def remove_node(self, uid: str) -> None:
        """Remove a single node from the network.

        .. note::

            If an node is removed from the network, all associated edges and
            paths are deleted.

        Parameters
        ----------

        uid : str

            The parameter ``uid`` is the unique identifier for the node which
            should be removed.

        Examples
        --------
        Generate a simple network.

        >>> from pathpy import Network
        >>> net = Network('a-b', 'b-c', 'c-d', 'a-b-c-d')
        >>> net.shape
        (4, 3, 1)

        Remove a node.

        >>> net.remove_node('b')
        >>> net.shape
        (3, 1, 0)

        """
        # initializing varialbes
        node: str = uid

        # check if the node node exists in the network
        if node in self.nodes:

            # get associated paths
            _paths: dict = self.nodes.related[node].paths

            # get set of adjacent edges
            _edges: dict = self.nodes.related[node].edges

            # remove paths
            for path in list(_paths):
                self.remove_path(path.uid)

            # remove edges
            for edge in list(_edges):
                self.remove_edge(edge)

            # remove node
            self.nodes.delete(node)

    def remove_edge(self, uid: str, *args: str) -> None:
        """Remove a single edge from the network.

        .. note::

            If an edge is removed from the network, all associated paths are
            deleted. Nodes are not removed from the network. Edge and Node
            counter are adjusted accordingly.

        Parameters
        ----------

        uid : str

            The parameter ``uid`` is the unique identifier for the edge which
            should be removed.

        Examples
        --------
        Generate a network with some edges.

        >>> from pathpy import Network
        >>> net = Network('a-b', 'b-c', 'c-d')
        >>> net.number_of_edges()
        3

        Remove an edge.

        >>> net.remove_edge('b-c')
        >>> net.number_of_edges()
        2

        """
        # initializing varialbes
        edge: str = uid

        # check if the right object is provided
        if self.check:
            edge = _check_edge(self, edge, *args).uid

        # check if the edge is in the network
        if edge in self.edges:

            # get associated paths
            _paths: Set = self.edges.related[edge].paths

            # remove paths
            for path in list(_paths):
                self.remove_path(path.uid)

            # decrease node counter
            self.nodes.decrease_counter(
                list(self.edges[edge].nodes), self.edges.counter()[edge])

            # remove associated nodes
            self.nodes.remove_edge(self.edges[edge])

            # remove the edge from the network
            self.edges.delete(edge)

    def remove_path(self, uid: str, frequency: int = None) -> None:
        """Remove a single path from the network.

        .. note::

            If a path is removed from the network, the underlying nodes and
            edges remain in the network. I.e. only the :py:class:`Path` object
            is removed. Edge and Node counter are adjusted accordingly.

        Parameters
        ----------

        uid : str

            The parameter ``uid`` is the unique identifier for the path which
            should be removed.

        frequency : int, optional (default = None)

            Number of path observations which should be removed from the
            network. Per default all path observation are removed.

        Examples
        --------
        Generate a network and add paths with a frequency.

        >>> from pathpy import Network
        >>> net = Network()
        >>> net.add_paths_from(['a-b-c-d', 'b-c-d'], frequency=10)
        >>> net.paths.counter()
        Counter({'a-b|b-c|c-d': 10, 'b-c|c-d': 10})

        Remove some path observations.

        >>> net.remove_path('b-c-d', frequency=3)
        >>> net.paths.counter()
        Counter({'a-b|b-c|c-d': 10, 'b-c|c-d': 7})

        Remove the path.

        >>> net.remove_path('b-c|c-d')
        >>> net.paths.counter()
        Counter({'a-b|b-c|c-d': 10})

        """
        # initializing varialbes
        path: str = uid

        # check if the right object is provided
        if self.check:
            # check the given string
            string, mode = _check_str(self, path, expected='path')[0]

            # if string represents a path
            if mode == 'path':
                # get the path uid
                path = _check_path(self, string[0]).uid
            else:
                log.warning('Invalide path uid "{}"!'.format(string[0]))

        # check if the path is in the network
        if path in self.paths:
            # get the path object and the frequency
            _path = self.paths[path]
            _frequency = self.paths.counter()[path]

            # check if frequency is given and smaller than observed
            if frequency is not None and frequency < _frequency:
                _frequency = frequency
            else:
                frequency = None

            # decrease the counters
            self.nodes.decrease_counter(_path.as_nodes, _frequency)
            self.edges.decrease_counter(_path.as_edges, _frequency)
            self.paths.decrease_counter(_path.uid, _frequency)

            # remove path from the network
            # if frequency is equal to the observations
            if frequency is None:
                # remove associated nodes and edges
                self.nodes.remove_path(self.paths[path])
                self.edges.remove_path(self.paths[path])

                # remove path from the network
                self.paths.delete(path)

    def _check_class(self):
        """Check which is the appropriated network class."""

        if not self.edges:
            _directed = self.directed
        else:
            _directed = self.edges.directed

        if _directed is None:
            log.error('Edges must either be directed or undirected!')
            raise AttributeError

        # TODO: Consider also temporal paths
        _temporal = self.nodes.temporal or self.edges.temporal

        if _directed and not _temporal:
            self.__class__ = DirectedNetwork
        elif not _directed and not _temporal:
            self.__class__ = UndirectedNetwork
        elif _directed and _temporal:
            self.__class__ = DirectedTemporalNetwork
        elif not _directed and _temporal:
            self.__class__ = UndirectedTemporalNetwork


class DirectedNetwork(BaseDirectedNetwork, Network):
    def __init__(self, *args: Path, uid: str = '',
                 directed: bool = True, temporal: bool = None,
                 **kwargs: Any) -> None:
        """Initialize the network object."""
        # initialize the base class
        super().__init__(*args, directed=directed, temporal=temporal ** kwargs)


class UndirectedNetwork(BaseUndirectedNetwork, Network):
    def __init__(self, *args: Path, uid: str = '',
                 directed: bool = False, temporal: bool = None,
                 **kwargs: Any) -> None:
        """Initialize the network object."""
        # initialize the base class
        super().__init__(*args, directed=directed, temporal=temporal ** kwargs)


class DirectedTemporalNetwork(BaseDirectedTemporalNetwork, Network):
    def __init__(self, *args: Path, uid: str = '',
                 directed: bool = True, temporal: bool = True,
                 **kwargs: Any) -> None:
        """Initialize the network object."""
        # initialize the base class
        super().__init__(*args, directed=directed, temporal=temporal ** kwargs)


class UndirectedTemporalNetwork(BaseUndirectedTemporalNetwork, Network):
    def __init__(self, *args: Path, uid: str = '',
                 directed: bool = False, temporal: bool = True,
                 **kwargs: Any) -> None:
        """Initialize the network object."""
        # initialize the base class
        super().__init__(*args, directed=directed, temporal=temporal ** kwargs)


class DirectedAcyclicGraph(Network):
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
