#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : network.py -- Base class for a network
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Tue 2019-09-10 16:55 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, TypeVar, List
# from copy import deepcopy
from collections import defaultdict

from .. import logger  # , config
from . import Node
from . import Edge

# create logger for the Edge class
log = logger(__name__)

# create multi type for Nodes
NodeType = TypeVar('NodeType', Node, str)
EdgeType = TypeVar('EdgeType', Edge, str)
WeightType = TypeVar('WeightType', str, None, float, int)


class Network(object):
    """Base class for a network."""

    def __init__(self, directed: bool = True, **kwargs: Any) -> None:
        """Initialize the network object."""

        # inidcator whether the network is directed or undirected
        self._directed = directed

        # dictionary for network attributes
        self.attributes: dict = {}

        # add attributes to the network
        self.attributes.update(kwargs)

        # a dictionary containing node objects
        self.nodes = defaultdict(dict)

        # a dictionary containing edge objects
        self.edges = defaultdict(dict)

        # Classes of the Node and Edge objects
        # TODO: Probably there is a better solution to have different Node and
        # Edge classes for different Network sub classes
        self._node_class()
        self._edge_class()

        pass

    def _node_class(self) -> None:
        """Internal function to assign different Node classes."""
        self.NodeClass = Node

    def _edge_class(self) -> None:
        """Internal function to assign different Edge classes."""
        self.EdgeClass = Edge

    def __repr__(self) -> str:
        """Return the description of the network.

        Returns
        -------
        str
            Returns the description of the network with the class, the name (if
            deffined) and the assigned system id.

        Example
        -------
        Genarate new network

        >>> from pathpy import Network
        >>> n = Node()
        >>> print(n)

        """
        return '<{} object {} at 0x{}x>'.format(self._desc(),
                                                self.name, id(self))

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

        Example
        -------
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

        Example
        -------
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
        pass

    @property
    def name(self) -> str:
        """Return the name of the network if defined, else an empty space.

        The name of the network is an attribute of the network, in order to
        make the classification and identification easier. However the name of
        the network do not have to be unique like an id. Therefore, the name of
        the network can be changed.

        Retuns
        ------
        str
            Returns the name of the network (if defined), otherwise an empty
            string is returnd.

        Example
        -------
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
        _name = self.attributes.get('name', '')
        if _name is None:
            _name = ''
        return _name

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
    def shape(self):
        """Return the size of the Network as tuple of number of nodes and number
        of edges"""
        return self.number_of_nodes(), self.number_of_edges()

    @property
    def directed(self):
        """Return if the network is directed (True) or undirected (False)."""
        return self._directed

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
        >>> net.update(city='Vienna',year='1850')

        """
        self.attributes.update(kwargs)

    def number_of_nodes(self) -> int:
        """Return the number of nodes in the network.

        Returns
        -------
        int
            Returns the number of nodes in the network.

        Example
        -------

        TODO: Make example

        """
        return len(self.nodes)

    def number_of_edges(self) -> int:
        """Return the number of edges in the network.

        Returns
        -------
        int
            Returns the number of edges in the network.

        Example
        -------

        TODO: Make example

        """
        return len(self.edges)

    def add_node(self, n: NodeType, **kwargs: Any) -> None:
        """Add a single node n and update node attributes.

        Parameters
        ----------
        u : str or :py:class:`Node`
            The parameter `n` is the node which should be added to the
            network. The parameter `n` can either be string value or a
            :py:class:`Node` object. If the parameter is a string value, a new
            node object is created where the node identifier (id) is the given
            value `n`. If the parameter is already a :py:class:`Node` object,
            it will be added to the network.

        kwargs : Any, optional (default = {})
            Attributes assigned to the node as key=value pairs.

        Example
        -------
        Adding a singe new node to the network.

        >>> from pathpy import Node, Network
        >>> net = Network()
        >>> net.add_node('v',color='red')

        Adding an existing node object to the network.

        >>> w = Node('w',color='green')
        >>> net.add_node(w)

        Note
        ----
        If the node is already defined in the network. The new node will not
        be added to the network, instead a warning will be printed.

        """
        # check if u is not a Node object
        if not isinstance(n, self.NodeClass):
            _node = self.NodeClass(n, **kwargs)
        else:
            _node = n
            _node.update(**kwargs)

        # check if node is already in the network
        if _node.id not in self.nodes:
            self.nodes[_node.id] = _node
        else:
            log.warn('The node with id: {} is already part of the'
                     'network. Please, check network consistency. The node id'
                     ' must be unique.'.format(_node.id))

    def add_nodes_from(self, nodes: List[NodeType], **kwargs: Any) -> None:
        """Add multiple nodes from a list.

        Parameters
        ----------
        nodes : list of str or :py:class:`Node`
            The parameter nodes must be a list with node ids as strings or
            :py:class:`Node` objects. Every node within the list should have a
            unique id.  If the list entry is a string value, a new node object
            is created where the node identifier (id) is the given string
            value. If the list entry is already a :py:class:`Node` object, it
            will be added to the network.

        kwargs : Any, optional (default = {})
            Attributes assigned to all nodes in the list as key=value pairs.

        Example
        -------
        Adding a multiple nodes to the network.

        >>> from pathpy import Node, Network
        >>> net = Network()
        >>> u = Node('u')
        >>> net.add_nodes_from([u,'v','w'],shape='circle')

        Note
        ----
        If the node is already defined in the network. The new node will not
        be added to the network, instead a warning will be printed.

        """
        for n in nodes:
            self.add_node(n, **kwargs)

    def remove_node(self, n: str) -> None:
        """Remove node n and all adjacent edges.

        Parameters
        ----------
        n : str
            The parameter `n` is the node identifier (id) as string for the
             node.

        Example
        -------

        Generate a simple network.

        >>> from pathpy import Network
        >>> net = Network()
        >>> net.add_edge('ab','a','b')
        >>> net.add_edge('bc','b','c')
        >>> net.add_edge('ac','a','c')

        Remove node form the network

        >>> net.remove_node('b')
        """
        if n in self.nodes:
            # get list of adjacent edges
            _edges = self.nodes[n].adjacent_edges
            # remove edges
            # BUG when multiple nodes are removed
            # TODO exchange del self.edges[e] with self.remove_edge(e)
            for e in _edges:
                del self.edges[e]
            # remove node
            del self.nodes[n]

    def remove_nodes_from(self, nodes: List[str]) -> None:
        """Remove multiple nodes given in a list of nodes.

        Parameters
        ----------
        nodes : list of node ids as str
            The parameter nodes must be a list with node ids as strings.

        """
        for n in nodes:
            self.remove_node(n)

    def has_node(self, n: str) -> bool:
        """Return True if the network contains the node n.

        Parameters
        ----------
        n : node id as str
            The parameter `n` is the identifier (id) for the node.

        Returns
        -------
        bool
            Returns True if the network has a node `n` otherwise False.

        """
        return n in self.nodes

    def add_edge(self, *args: Any,
                 separator: str = '-',
                 **kwargs: Any) -> None:
        """Add an edge e between node v and node w.

        With the :py:meth:`add_edge` an :py:class:`Edge` object is added to the
        network. Thereby, mutliple input options are available.

        1. `add_edge(e, v, w)`: The first way to add an edge is via the triplet
            edge `e`, source node `v` and target node `w`. Thereby, the `e` is
            the string value of the edge id and `v` and `w` are either the
            string values of the node ids or :py:class:`Node` objects.

        2. `add_edge(v, w)`: The second way to add an edge is via a tuple of
            source node `v` and target node `w`. Thereby, `v` and `w` are
            either the string values of the node ids or :py:class:`Node`
            objects. Thereby the edge id is the combination of the node ids
            separated via the `separator`. e.g. an edge between nodes 'v' and
            'w' is generated, with edge id 'v-w'.

        3. `add_edge(e)`: The thrid way to add an edge is directly add an
           :py:class:`Edge` object. Thereby, all properties of the edge object
           (e.g. corresponding nodes) are taken from the object.

        Parameters
        ----------
        e : str or py:class:`Edge`
            The parameter `e` describes the edge which schould be added to the
            network. The parameter `e` can either be a string value, a
            :py:class:`Edge` object, or not defined. If the parameter is a
            string value, a new edge object is created given that also node
            parameters are given. Thereby, the edge identifier (id) is the
            string value. If the parameter is already a :py:class:`Edge`
            object, it will be added to the network. If the edge is not defined
            but two node parameter are given, an edge based on the nodes is
            generated, i.e. the edge id is created based on the node ids.

        v : str or :py:class:`Node`
            The parameter `v` is the source node of the edge, which should be
            added to the network. The parameter `v` can either be string value,
            a :py:class:`Node` object or not defined. If the parameter is a
            string value, a new node object is created where the node
            identifier (id) is the given value `v`. If the parameter is already
            a :py:class:`Node` object, it will be added to the network. If the
            node is not defined an :py:class:`Edge` object has to be given.

        w : str or :py:class:`Node`
            The parameter `w` is the target node of the edge, which should be
            added to the network. The parameter `w` can either be string value,
            a :py:class:`Node` object or not defined. If the parameter is a
            string value, a new node object is created where the node
            identifier (id) is the given value `w`. If the parameter is already
            a :py:class:`Node` object, it will be added to the network. If the
            node is not defined an :py:class:`Edge` object has to be given.

        separator : str, optional (default = '-')
            If no edge id is provide, an edge id is generated based on the node
            ids, Thereby the edge id is the combination of the node ids
            separated via the `separator`. e.g. an edge between nodes 'v' and
            'w' is generated, with edge id 'v-w'.

        kwargs : Any, optional (default = {})
            Attributes assigned to the edge as key=value pairs.

        Raises
        ------
        AttributeError
            If the arguments are not correct enterd.

        AttributeError
            If the edge id is given as string but no nodes are definde.

        ValueError
            If and directed edge is added to an undirected network or vice
            versa.

        Example
        -------
        Adding a singe new edge to the network.

        >>> from pathpy import Node, Edge, Network
        >>> net = Network()
        >>> net.add_edge('a-b', 'a', 'b', length = 10)

        Adding an existing edge object to the network.

        >>> e = Edge('b-c','b', 'c', length = 5)
        >>> net.add_edge(e)

        Adding an edge only based on nodes.

        >>> net.add_edge('c', 'd')

        Changing the separator.

        >>> net.add_edge('a', 'd', separator='=')

        Note
        ----

        Altough an edge can be defined only by its nodes, it is highly
        recommended to use unique identifier for the edge id!

        If the edge is already defined in the network. The new edge will not
        be added to the network, instead a warning will be printed.

        """
        # initializing variables
        e: EdgeType = None
        v: NodeType = None
        w: NodeType = None

        # get the right variables
        if len(args) == 3:
            e, v, w = args

        # check if only nodes are given
        elif (len(args) == 2
              and not isinstance(args[0], self.EdgeClass)
              and not isinstance(args[1], self.EdgeClass)):
            v, w = args

        # if only on variable is given
        elif len(args) == 1:
            e = args[0]

        # if otherwise an error will be raised
        else:
            log.error('Parameters are not correct defined!')
            raise AttributeError

        # check if e is not an Edge object
        if not isinstance(e, self.EdgeClass):

            # check if nodes are given
            if v is not None and w is not None:

                # create temporal list of nodes
                _n: List[List[str, NodeType]] = []

                # iterate trough the nodes
                for n in [v, w]:

                    # check the type of the node
                    if isinstance(n, self.NodeClass):

                        # if node is a Node object use the id value
                        _id = n.id
                    else:
                        # otherwise use the given id
                        _id = n

                    # if node is already defined use this node
                    if _id in self.nodes:
                        _n.append([_id, self.nodes[_id]])
                    else:
                        _n.append([_id, n])

                # generate edge id based on nodes if no id is given
                if e is None:
                    e = '{}{}{}'.format(_n[0][0], separator, _n[1][0])
                # create temporal edge
                _edge = self.EdgeClass(e, _n[0][1], _n[1][1],
                                       directed=self.directed,
                                       **kwargs)
            else:
                log.error('No nodes are defined '
                          'for the new edge "{}!"'.format(e))
                raise AttributeError

        # if edge is an Edge object
        else:
            # check if direction of edge and network is not given
            if e.directed != self.directed:
                _msg = {True: 'directed', False: 'undirected'}
                log.error('The {} edge "{}" cannot be added to the '
                          '{} network!'.format(_msg[e.directed], e.id,
                                               _msg[self.directed]))
                raise ValueError
            # create temporal edge
            _edge = e

            # update attributes with new given attributes
            _edge.update(**kwargs)

        # check if node v is already in the network
        if _edge.v.id not in self.nodes:
            self.nodes[_edge.v.id] = _edge.v

        # check if node w is already in the network
        if _edge.w.id not in self.nodes:
            self.nodes[_edge.w.id] = _edge.w

        # check if edge is already in the network
        if _edge.id not in self.edges:

            # add edge to the network
            self.edges[_edge.id] = _edge

            # update in- and out-degree of the nodes
            self.nodes[_edge.v.id].outgoing.add(_edge.id)
            self.nodes[_edge.w.id].incoming.add(_edge.id)

            # TODO: This is probabily not needed.
            if not self.directed:
                self.nodes[_edge.v.id].incoming.add(_edge.id)
                self.nodes[_edge.w.id].outgoing.add(_edge.id)

        else:
            log.warn('The edge with id: {} is already part of the'
                     'network. Please, check network consistency. The edge id'
                     ' must be unique.'.format(_edge.id))

    def add_edges_from(self, edges: list, separator: str = '-', **kwargs):
        """Add multiple edges from a list.

        Parameters
        ----------
        edges : list of edge ids or Edges
            The parameter edges must be a list with edge ids or edge
            objects. Every edge within the list should have a unique id.
            The id is converted to a string value and is used as a key value for
            all dict which saving node objects.

        attr : keyword arguments, optional (default= no attributes)
            Attributes to add to all edges in the list as key=value pairs.

        Example
        -------
        Adding a multiple edges to the network.

        >>> net = cn.Network()
        >>> ab = cn.Edge'ab','a','b')
        >>> net.add_edges_from([ab,('bc',b','c')],length=10)

        Note
        ----
        If an edge id is added without nodes, an error will be raised and stop
        the code.

        If the edge is already defined in the network. The new edge will not
        be added to the network, instead a warning will be printed.

        """
        for _edge in edges:
            if not isinstance(_edge, self.EdgeClass):
                self.add_edge(*_edge, separator=separator, **kwargs)
            else:
                self.add_edge(_edge, separator=separator, **kwargs)
# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
