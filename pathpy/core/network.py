"""Network class"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : network.py -- Base class for a network
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Mon 2020-06-15 14:33 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, Tuple, Optional, Union, Dict, Set
from collections import defaultdict

from pathpy import logger
from pathpy.core.base import BaseModel
from pathpy.core.node import Node, NodeCollection
from pathpy.core.edge import Edge, EdgeCollection

from pathpy.algorithms import (matrices,
                               centralities,
                               shortest_paths,
                               components)

from pathpy.statistics import degrees as degree_statistics
from pathpy.statistics import clustering
from pathpy.visualisations.plot import plot as network_plot

# create custom types
Weight = Union[str, bool, None]

# create logger for the Network class
LOG = logger(__name__)


class Network(BaseModel):
    """Class for a network.

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
    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-many-public-methods

    # load external functions to the network
    adjacency_matrix = matrices.adjacency_matrix  # type: ignore
    transition_matrix = matrices.transition_matrix  # type: ignore
    distance_matrix = shortest_paths.distance_matrix  # type: ignore
    diameter = shortest_paths.diameter  # type: ignore
    avg_path_length = shortest_paths.avg_path_length

    betweenness_centrality = centralities.betweenness_centrality  # type: ignore
    closeness_centrality = centralities.closeness_centrality  # type: ignore

    find_connected_components = components.find_connected_components  # type: ignore
    largest_connected_component = components.largest_connected_component  # type: ignore
    largest_component_size = components.largest_component_size  # type: ignore
    is_connected = components.is_connected

    mean_degree = degree_statistics.mean_degree
    mean_neighbor_degree = degree_statistics.mean_neighbor_degree
    degree_sequence = degree_statistics.degree_sequence
    degree_assortativity = degree_statistics.degree_assortativity
    degree_central_moment = degree_statistics.degree_central_moment
    degree_distribution = degree_statistics.degree_distribution
    degree_generating_function = degree_statistics.degree_generating_function
    degree_raw_moment = degree_statistics.degree_raw_moment
    molloy_reed_fraction = degree_statistics.molloy_reed_fraction

    avg_clustering_coefficient = clustering.avg_clustering_coefficient
    local_clustering_coefficient = clustering.local_clustering_coefficient

    plot = network_plot

    def __init__(self, uid: Optional[str] = None,
                 directed: bool = True, temporal: bool = False,
                 multiedges: bool = False, **kwargs: Any) -> None:
        """Initialize the network object."""

        # initialize the base class
        super().__init__(uid=uid, **kwargs)

        # inidcator whether the network is directed or undirected
        self._directed: bool = directed

        # indicator whether the network is temporal or static
        self._temporal: bool = temporal

        # indicator whether the network has multi-edges
        self._multiedges: bool = multiedges

        # # a container for the network properties
        self._properties: defaultdict = defaultdict()

        # a container for node objects
        self._nodes: NodeCollection = NodeCollection()

        # a container for edge objects
        self._edges: EdgeCollection = EdgeCollection(directed=directed,
                                                     multiedges=multiedges,
                                                     nodes=self._nodes)

        # add attributes to the network
        self.attributes.update(**kwargs)

        # add network properties
        self._properties['edges'] = set()
        self._properties['successors'] = defaultdict(set)
        self._properties['predecessors'] = defaultdict(set)
        self._properties['outgoing'] = defaultdict(set)
        self._properties['incoming'] = defaultdict(set)
        self._properties['neighbors'] = defaultdict(set)
        self._properties['incident_edges'] = defaultdict(set)
        self._properties['indegrees'] = defaultdict(float)
        self._properties['outdegrees'] = defaultdict(float)
        self._properties['degrees'] = defaultdict(float)

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

    def _repr_html_(self):
        """Plot the network in an interactive environment."""
        self.plot()

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
        return super().uid

    def __add__(self, other: Network) -> Network:
        """Add a network to a network."""
        network = Network(directed=self.directed, temporal=self.temporal,
                          multiedges=self.multiedges, **self.attributes.to_dict())

        # TODO: add warnings if two networks have different properties
        # TODO: update also netork properties

        # add nodes and edges of self to the new network
        network.add_nodes(*self.nodes)
        network.add_edges(*self.edges)

        # add nodes and edges of the other to the new network
        # iterate over all other nodes
        for node in other.nodes:
            # check if the node object already exists
            if node not in network.nodes.values():
                # add node to the network
                network.add_node(node)

        # iterate over all other edges
        for edge in other.edges:
            # check if the edge object already exists
            if edge not in network.edges.values():
                # add node to the network
                network.add_edge(edge)

        # return the new network
        return network

    def __sub__(self, other: Network) -> Network:
        """Remove a network from a network."""

        network = Network(directed=self.directed, temporal=self.temporal,
                          multiedges=self.multiedges, **self.attributes.to_dict())

        # add nodes and edges of self to a new network
        network.add_nodes(*self.nodes)
        network.add_edges(*self.edges)

        # remove nodes and edges of the other network
        network.remove_edges(*other.edges)
        network.remove_nodes(*other.nodes)

        # return the new network
        return network

    def __iadd__(self, other: Network) -> Network:
        """Add a network to it self."""

        # TODO: add warnings if two networks have different properties
        # TODO: update also netork properties

        # add nodes and edges of the other to the network
        # iterate over all other nodes
        for node in other.nodes:
            # check if the node object already exists
            if node not in self.nodes.values():
                # add node to the network
                self.add_node(node)

        # iterate over all other edges
        for edge in other.edges:
            # check if the edge object already exists
            if edge not in self.edges.values():
                # add node to the network
                self.add_edge(edge)

        return self

    def __isub__(self, other: Network) -> Network:
        """Remove a network."""

        # remove nodes and edges of the other network
        self.remove_edges(*other.edges)
        self.remove_nodes(*other.nodes)

        return self

    @property
    def shape(self) -> Tuple[int, int]:
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
        return self.number_of_nodes(), self.number_of_edges()

    @property
    def directed(self) -> bool:
        """Return if the network is directed (True) or undirected (False).

        Returns
        -------
        bool

            Return ``True`` if the network is directed or ``False`` if the
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
    def multiedges(self) -> bool:
        """Return if edges are directed. """
        return self._multiedges

    @property
    def temporal(self) -> bool:
        """Return if the network is temproal (True) or static (False).

        Returns
        -------
        bool

            Return ``True`` if the network is temporal or ``False`` if the
            network is static.

        """
        return self._temporal

    @property
    def nodes(self) -> NodeCollection:
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
    def edges(self) -> EdgeCollection:
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
    def successors(self) -> Dict[str, Set[Node]]:
        """Returns a dict of set of all successor nodes for a given node.

        Returns
        -------

        Dict[str, Set[Node]]

            Return the Node objects of all successor nodes.

        Examples
        --------
        Generate network with two nodes and a (directed) edge.

        >>> import pathpy as pp
        >>> n = pp.Network(directed=True)
        >>> n.add_edge('v', 'w')

        Print the successors nodes.

        >>> n.successors
        {'v': {Node w}, 'w':{}}

        """
        _d = self._properties['successors']
        return {node.uid: _d[node] for node in self.nodes}

    @property
    def predecessors(self) -> Dict[str, Set[Node]]:
        """Returns a dict of sets of all predecessor nodes for a given node.

        Returns
        -------

        Dict[str, Set[Node]]

            Return the Node objects of all predecessor nodes.

        Examples
        --------
        Generate network with two nodes and a (directed) edge.

        >>> import pathpy as pp
        >>> n = pp.Network(directed=True)
        >>> n.add_edge('v', 'w')

        Print the predecessor nodes.

        >>> n.predecessors
        {'v':{}, 'w': {Node v}}

        """
        _d = self._properties['predecessors']
        return {node.uid: _d[node] for node in self.nodes}

    @property
    def outgoing(self) -> Dict[str, Set[Edge]]:
        """Retuns a dict with sets of outgoing edges."""
        _d = self._properties['outgoing']
        return {node.uid: _d[node] for node in self.nodes}

    @property
    def incoming(self) -> Dict[str, Set[Edge]]:
        """Retuns a dict with sets of incoming edges."""
        _d = self._properties['incoming']
        return {node.uid: _d[node] for node in self.nodes}

    @property
    def neighbors(self) -> Dict[str, Set[Node]]:
        """Retuns a dict with sets of adjacent nodes."""
        _d = self._properties['neighbors']
        return {node.uid: _d[node] for node in self.nodes}

    @property
    def incident_edges(self) -> Dict[str, Set[Edge]]:
        """Retuns a dict with sets of adjacent edges."""
        _d = self._properties['incident_edges']
        return {node.uid: _d[node] for node in self.nodes}

    def _degrees(self, _dict: defaultdict,
                 weight: Weight = None) -> Dict[str, float]:
        """Helper function to calculate the degrees."""
        _degrees: dict = {}
        if weight is None:
            _degrees = {node.uid: _dict[node] for node in self.nodes.values()}
        else:
            for node in self.nodes.values():
                _degrees[node.uid] = sum([e.weight(weight)
                                          for e in _dict[node]])
        return _degrees

    def indegrees(self, weight: Weight = None) -> Dict[str, float]:
        """Retuns a dict with indegrees of the nodes."""
        if weight is None:
            _d = self._degrees(self._properties['indegrees'], weight)
        else:
            _d = self._degrees(self._properties['incoming'], weight)
        return _d

    def outdegrees(self, weight: Weight = None) -> Dict[str, float]:
        """Retuns a dict with outdegrees of the nodes."""
        if weight is None:
            _d = self._degrees(self._properties['outdegrees'], weight)
        else:
            _d = self._degrees(self._properties['outgoing'], weight)
        return _d

    def degrees(self, weight: Weight = None) -> Dict[str, float]:
        """Retuns a dict with degrees of the nodes."""
        if weight is None:
            _d = self._degrees(self._properties['degrees'], weight)
        else:
            _d = self._degrees(self._properties['incident_edges'], weight)
        return _d

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
            'Uid:\t\t\t{}\n'.format(self.uid),
            'Type:\t\t\t{}\n'.format(self.__class__.__name__),
            'Directed:\t\t{}\n'.format(str(self.directed)),
            'Multi-Edges:\t\t{}\n'.format(str(self.multiedges)),
            'Number of nodes:\t{}\n'.format(self.number_of_nodes()),
            'Number of edges:\t{}'.format(self.number_of_edges()),
        ]
        attr = self.attributes.to_dict()
        if len(attr) > 0:
            summary.append('\n\nNetwork attributes\n')
            summary.append('------------------\n')
        for k, v in attr.items():
            summary.append('{}:\t{}\n'.format(k, v))

        return ''.join(summary)

    def number_of_nodes(self) -> int:
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
        # if unique:
        return len(self.nodes)

    def number_of_edges(self) -> int:
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
        # if unique:
        return len(self.edges)

    def add_node(self, *node: Union[str, Node], **kwargs: Any) -> None:
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
        self.nodes.add(*node, **kwargs)

    def add_edge(self, *edge: Union[str, tuple, list, Node, Edge],
                 uid: Optional[str] = None, **kwargs: Any) -> None:
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
        self.edges.add(*edge, uid=uid, **kwargs)
        self._add_properties()

    def add_nodes(self, *nodes: Union[str, Node],
                  **kwargs: Any) -> None:
        """Add multiple nodes from a list to the network.

        Parameters
        ----------
        nodes : List[Node]

            Nodes from a list of :py:class:`Node` objects are added to the
            network.

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
        self.nodes.add(*nodes, **kwargs)

    def add_edges(self, *edges: Union[str, tuple, list, Node, Edge],
                  **kwargs: Any) -> None:
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
        self.edges.add(*edges, **kwargs)
        self._add_properties()

    def remove_node(self, node: Union[str, Node]) -> None:
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
        if node in self.nodes:
            for _edge in list(self.incident_edges[self.nodes[node].uid]):
                self.remove_edge(_edge)
        self.nodes.remove(node)

    def remove_edge(self, *edge: Union[str, tuple, Node, Edge],
                    uid: Optional[str] = None) -> None:
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
        # check if the right object is provided.
        # if edge obect is given
        self.edges.remove(*edge, uid=uid)
        self._remove_properties()

    def remove_edges(self, *edges: Union[str, tuple, list, Node, Edge]) -> None:
        """Remove multiple edges from the network."""
        self.edges.remove(*edges)
        self._remove_properties()

    def remove_nodes(self, *nodes: Union[str, Node]) -> None:
        """Remove multiple nodes from the network."""
        for node in nodes:
            self.remove_node(node)

    def _add_properties(self):
        """Helper function to update network properties."""

        edges = set(self.edges).difference(self._properties['edges'])

        for edge in edges:
            _nodes: list = [(edge.v, edge.w), (edge.w, edge.v)]

            for _v, _w in _nodes:
                self._properties['successors'][_v].add(_w)
                self._properties['outgoing'][_v].add(edge)
                self._properties['predecessors'][_w].add(_v)
                self._properties['incoming'][_w].add(edge)

                if self.directed:
                    break

            for _v, _w in _nodes:
                self._properties['neighbors'][_v].add(_w)
                self._properties['incident_edges'][_v].add(edge)

                self._properties['indegrees'][_v] = len(
                    self._properties['incoming'][_v])
                self._properties['outdegrees'][_v] = len(
                    self._properties['outgoing'][_v])
                self._properties['degrees'][_v] = len(
                    self._properties['incident_edges'][_v])

            self._properties['edges'].add(edge)

    def _remove_properties(self):
        """Helper function to update network properties."""

        edges = self._properties['edges'].difference(set(self.edges))

        for edge in edges:
            _nodes: list = [(edge.v, edge.w), (edge.w, edge.v)]

            for _v, _w in _nodes:
                self._properties['successors'][_v].discard(_w)
                self._properties['outgoing'][_v].discard(edge)
                self._properties['predecessors'][_w].discard(_v)
                self._properties['incoming'][_w].discard(edge)

                if self.directed:
                    break

            for _v, _w in _nodes:
                self._properties['neighbors'][_v].discard(_w)
                self._properties['incident_edges'][_v].discard(edge)

                self._properties['indegrees'][_v] = len(
                    self._properties['incoming'][_v])
                self._properties['outdegrees'][_v] = len(
                    self._properties['outgoing'][_v])
                self._properties['degrees'][_v] = len(
                    self._properties['incident_edges'][_v])

            self._properties['edges'].discard(edge)


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
