#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : network.py -- Base class for a network
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Wed 2019-09-25 14:10 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, TypeVar, List, Dict, Tuple
# from copy import deepcopy
from collections import defaultdict

from .. import logger, config
from . import Node
from . import Edge
from .base import DefaultNetwork

# create logger for the Edge class
log = logger(__name__)

# create multi type for Nodes
NodeType = TypeVar('NodeType', Node, str)
EdgeType = TypeVar('EdgeType', Edge, str)


class Network(DefaultNetwork):
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

        # a dictionary containing tuple of node ids and edges
        self._node_to_edges_map = defaultdict(list)

        # a dictionary containing edge ids and node ids
        self._edge_to_nodes_map = defaultdict(tuple)

        # Classes of the Node and Edge objects
        # TODO: Probably there is a better solution to have different Node and
        # Edge classes for different Network sub classes
        self._node_class()
        self._edge_class()

        pass

    # import external functions
    from ..algorithms.adjacency_matrix import adjacency_matrix

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

        Examples
        --------
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
        pass

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

    @property
    def node_to_edges_map(self) -> Dict(List(str)):
        """Returns a a dictionary which maps the nodes to associated edges.

        Returns
        -------
        Dict(List(str))
            Returns a dict where the key is a tuple of node ids and the values
            are lists of edges which are associated with these nodes.

        Examples
        --------
        Generate simple network.

        >>> from pathpy import Network
        >>> net = Network()
        >>> net.add_edges_from([('ab1','a','b'),
        >>>                     ('ab2','a','b'),
        >>>                     ('bc','b','c')])
        >>> net.node_to_edges_map


        """
        return self._node_to_edges_map

    @property
    def edge_to_nodes_map(self) -> Dict(Tuple(str, str)):
        """Returns a a dictionary which maps the edges to associated nodes.

        Returns
        -------
        Dict(Tuple(str,str))
           Returns a dict where the key is the edge id and the values
           are tuples of associated node ids.

        Examples
        --------
        Generate simple network

        >>> from pathpy import Network
        >>> net = Network()
        >>> net.add_edges_from([('ab','a','b'),('bc','b','c')])
        >>> net.edge_to_nodes_map

        """
        return self._edge_to_nodes_map

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

        Examples
        --------

        TODO: Make example

        """
        return len(self.nodes)

    def number_of_edges(self) -> int:
        """Return the number of edges in the network.

        Returns
        -------
        int
            Returns the number of edges in the network.

        Examples
        --------

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

        Examples
        --------
        Adding a singe new node to the network.

        >>> from pathpy import Node, Network
        >>> net = Network()
        >>> net.add_node('v',color='red')

        Adding an existing node object to the network.

        >>> w = Node('w',color='green')
        >>> net.add_node(w)

        Notes
        -----
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

        Examples
        --------
        Adding a multiple nodes to the network.

        >>> from pathpy import Node, Network
        >>> net = Network()
        >>> u = Node('u')
        >>> net.add_nodes_from([u,'v','w'],shape='circle')

        Notes
        -----
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

        Examples
        --------

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
            for e in _edges:
                self.remove_edge(e)

            # remove node
            del self.nodes[n]

    def remove_nodes_from(self, nodes: List[str]) -> None:
        """Remove multiple nodes given in a list of nodes.

        Parameters
        ----------
        nodes : list of node ids as str
            The parameter nodes must be a list with node ids as strings.

        Examples
        --------

        Generate a simple network.

        >>> from pathpy import Network
        >>> net = Network()
        >>> net.add_edge('ab','a','b')
        >>> net.add_edge('bc','b','c')
        >>> net.add_edge('ac','a','c')

        Remove nodes form the network

        >>> net.remove_nodes_from(['a', 'b'])

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

        Examples
        --------

        Generate a simple network.

        >>> from pathpy import Network
        >>> net = Network()
        >>> net.add_nodes_from(['a','b','c'])

        Check if network has specific nodes

        >>> net.has_node('a')

        >>> net.has_node('u')

        """
        return n in self.nodes

    def _check_edge(self, *args: Any, **kwargs: Any) -> Tuple(Dict):
        """Helper function to check if edge is in the right format.

        Returns
        -------
        Tuple(Dict)
            Returns a tuple of dictionaries. A dictionary correspond to either
            a edge or a node, and contain the node id (key: `id`) the
            :py:class:`Edge` or :py:class:`Node` object (key: `object`) and if
            the object is already in the network (key: `given`).

        """

        # initializing variables
        e: EdgeType = None
        v: NodeType = None
        w: NodeType = None

        _e = {'id': None, 'object': None, 'given': False}
        _v = {'id': None, 'object': None, 'given': False}
        _w = {'id': None, 'object': None, 'given': False}

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
            log.error('Edge parameters are not correct defined!')
            raise AttributeError

        # check if edge e is given
        if e is not None:

            # check the type of the edge
            if isinstance(e, self.EdgeClass):

                # if edge is an Edge object use the id value
                _e['id'] = e.id

                # assigne the Edge object
                _e['object'] = e

            else:
                # otherwise use the given id
                _e['id'] = str(e)

        # check if node v is given
        if v is not None:

            # check the type of the node
            if isinstance(v, self.NodeClass):

                # if node is a Node object use the id value
                _v['id'] = v.id

                # assigne the Node object
                _v['object'] = v

            else:
                # otherwise use the given id
                _v['id'] = str(v)

        # check if node w is given
        if w is not None:

            # check the type of the node
            if isinstance(w, self.NodeClass):

                # if node is a Node object use the id value
                _w['id'] = w.id

                # assigne the Node object
                _w['object'] = w

            else:
                # otherwise use the given id
                _w['id'] = str(w)

        # check if the Edge object is already in the network
        if _e['id'] in self.edges:
            _e['given'] = True

        # check if the Node object is already in the network
        if _v['id'] in self.nodes:
            _v['given'] = True

        # check if the Node object is already in the network
        if _w['id'] in self.nodes:
            _w['given'] = True

        # if edge is give does it have the same nodes?
        if _e['given'] and _v['id'] is None and _w['id'] is None:
            _v['id'] = self.edges[_e['id']].v.id
            _w['id'] = self.edges[_e['id']].w.id
            _v['given'] = True
            _w['given'] = True
        # if no edge is given but two nodes
        elif _e['id'] is None and _v['given'] and _w['given']:

            # check if edge is associated with the nodes
            _edges = self.node_to_edges_map[(_v['id'], _w['id'])]

            # TODO: find solution for multiedges
            if len(_edges) > 1:
                _e['given'] = True
            elif len(_edges) == 1:
                _e['given'] = True
                _e['id'] = _edges[0]

        # TODO: Make some additional sanity checks
        # - if edge is give does it have the same nodes?
        # - if objects are given is there any diffencse between them?
        return _e, _v, _w

    def add_edge(self, *args: Any, **kwargs: Any) -> None:
        """Add an edge e between node v and node w.

        With the :py:meth:`add_edge` an :py:class:`Edge` object is added to the
        network. Thereby, mutliple input options are available.

        1. `add_edge(e, v, w)`:
            The first way to add an edge is via the triplet edge `e`, source
            node `v` and target node `w`. Thereby, the `e` is the string value
            of the edge id and `v` and `w` are either the string values of the
            node ids or :py:class:`Node` objects.

        2. `add_edge(v, w)`:
            The second way to add an edge is via a tuple of source node `v` and
            target node `w`. Thereby, `v` and `w` are either the string values
            of the node ids or :py:class:`Node` objects. Thereby the edge id is
            the combination of the node ids separated via the
            `separator`. e.g. an edge between nodes 'v' and 'w' is generated,
            with edge id 'v-w'.

        3. `add_edge(e)`:
            The thrid way to add an edge is directly add an :py:class:`Edge`
            object. Thereby, all properties of the edge object
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

        separator : str, optional, config (default = '-')
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

        Examples
        --------
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

        Notes
        -----

        Altough an edge can be defined only by its nodes, it is highly
        recommended to use unique identifier for the edge id!

        If the edge is already defined in the network. The new edge will not
        be added to the network, instead a warning will be printed.

        """
        # use separator if given otherwise use config default value
        separator: str = kwargs.get('separator', config.network.separator)

        # check the inputs
        # returns a dict with
        # variable = {'id':str, 'object':class, 'given':bool}
        e, v, w = self._check_edge(*args, **kwargs)

        # if edge is an object
        if e['object'] is not None:

            # check if direction of edge and network is not given
            if e['object'].directed != self.directed:
                _msg = {True: 'directed', False: 'undirected'}
                log.error('The {} edge "{}" cannot be added to the '
                          '{} network!'.format(_msg[e['object'].directed],
                                               e['id'],
                                               _msg[self.directed]))
                raise ValueError

            # create temporal edge
            _edge = e['object']

            # update attributes with new given attributes
            _edge.update(**kwargs)

        # if edge is not an object but nodes are given:
        elif (e['object'] is None and v['id'] is not None
                and v['id'] is not None):

            # generate edge id based on nodes if no id is given
            if e['id'] is None:
                e['id'] = '{}{}{}'.format(v['id'], separator, w['id'])

            # if node is already defined use this node
            if v['given']:
                _v = self.nodes[v['id']]

            # otherwise if an object is given use this
            elif v['object'] is not None:
                _v = v['object']

            # otherwise use the id and create a new node
            else:
                _v = v['id']

            # if node is already defined use this node
            if w['given']:
                _w = self.nodes[w['id']]

            # otherwise if an object is given use this
            elif w['object'] is not None:
                _w = w['object']

            # otherwise use the id and create a new node
            else:
                _w = w['id']

            # create temporal edge
            _edge = self.EdgeClass(e['id'], _v, _w,
                                   directed=self.directed,
                                   **kwargs)

        # Raise error if no proper edge definition is given
        else:
            # TODO: make error more spesific.
            log.error('Edge parameters are not correct defined!')
            raise AttributeError

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

            # update maps
            self._edge_to_nodes_map[_edge.id] = (_edge.v.id, _edge.w.id)
            self._node_to_edges_map[(_edge.v.id, _edge.w.id)].append(_edge.id)

        else:
            log.warn('The edge with id: {} is already part of the'
                     'network. Please, check network consistency. The edge id'
                     ' must be unique.'.format(_edge.id))

    def add_edges_from(self, edges: list, **kwargs):
        """Add multiple edges from a list.

        Parameters
        ----------
        edges : list of edge ids or Edges
            The parameter edges must be a list with edge ids or edge
            objects. Every edge within the list should have a unique id. The
            id is converted to a string value and is used as a key value for
            all dict which saving node objects.

        separator : str, optional, config (default = '-')
            If no edge id is provide, an edge id is generated based on the node
            ids, Thereby the edge id is the combination of the node ids
            separated via the `separator`. e.g. an edge between nodes 'v' and
            'w' is generated, with edge id 'v-w'.

        attr : keyword arguments, optional (default= no attributes)
            Attributes to add to all edges in the list as key=value pairs.

        Examples
        --------
        Adding a multiple edges to the network.

        >>> from pathpy import Edge, Network
        >>> net = Network()
        >>> ab = Edge('ab','a','b')
        >>> net.add_edges_from([ab,('bc',b','c')],length=10)

        Notes
        -----
        If an edge id is added without nodes, an error will be raised and stop
        the code.

        If the edge is already defined in the network. The new edge will not
        be added to the network, instead a warning will be printed.

        See Also
        --------
        add_edge

        """
        # use separator if given otherwise use config default value
        separator: str = kwargs.get('separator', config.network.separator)

        for _edge in edges:
            if not isinstance(_edge, self.EdgeClass):
                self.add_edge(*_edge, separator=separator, **kwargs)
            else:
                self.add_edge(_edge, separator=separator, **kwargs)

    def remove_edge(self, *args: Any) -> None:
        """Remove the edge e between v and w.

        With the :py:meth:`remove_edge` an :py:class:`Edge` object is removed
        from the network. Thereby, mutliple input options are available.

        1. `remove_edge(e, v, w)`:
            The first way to remove an edge is via the triplet edge `e`, source
            node `v` and target node `w`. Thereby, the `e` is the string value
            of the edge id and `v` and `w` are either the string values of the
            node ids or :py:class:`Node` objects.

        2. `remove_edge(v, w)`:
            The second way to remove an edge is via a tuple of source node `v`
            and target node `w`. Thereby, `v` and `w` are either the string
            values of the node ids or :py:class:`Node` objects.

        3. `remove_edge(e)`:
            The thrid way to remove an edge is directly add an :py:class:`Edge`
            object or edge id.

        Parameters
        ----------
        e : str or py:class:`Edge`
            The parameter `e` describes the edge which schould be removed from
            the network. The parameter `e` can either be a string value, a
            :py:class:`Edge` object, or not defined. If the edge is not defined
            but two node parameter are given, an edge based on the nodes is
            removed.

        v : str or :py:class:`Node`
            The parameter `v` is the source node of the edge, which should be
            removed from the network. The parameter `v` can either be string
            value, a :py:class:`Node` object or not defined. If the node is not
            defined an :py:class:`Edge` object has to be given.

        w : str or :py:class:`Node`
            The parameter `w` is the target node of the edge, which should be
            removed from the network. The parameter `w` can either be string
            value, a :py:class:`Node` object or not defined. If the node is not
            defined an :py:class:`Edge` object has to be given.

        Notes
        -----
        If the tuple of node ids is used to remove edges, it is possible that
        multiple edges might be effected. In this situation an error will be
        raised and instead of the tuple the actual edge id should be used.

        """
        # initializing variables
        _edge: EdgeType = None

        # check the inputs
        # returns a dict with
        # variable = {'id':str, 'object':class, 'given':bool}
        e, v, w = self._check_edge(*args)

        # check if the edge is in the network
        if not e['given'] and not v['given'] and not w['given']:
            if e['id'] is not None:
                _edge = e['id']
            else:
                _edge = '({},{})'.format(v['id'], w['id'])
            log.warning('The edge "{}" could not be removed, because '
                        'this does not exist in the network.'.format(_edge))
            return

        # check if e exists in the network
        elif e['given'] and e['id'] is not None:
            _edge = self.edges[e['id']]

        # check if edge is given in terms of (v,w):
        elif v['given'] and w['given']:
            _edges = self.node_to_edges_map[(v['id'], w['id'])]

            # raise error if multiple edges are defined between v and w
            if len(_edges) > 1:
                log.error('From node "{}" to node "{}", {} edges exist with'
                          ' ids: {}! Please, us the correct edge id instead of'
                          ' the node ids!'.format(v['id'], w['id'],
                                                  len(_edges),
                                                  ', '.join(_edges)))
                raise ValueError

            # otherwise take the edge id
            else:
                _edge = self.edges[_edges[0]]

        # raise error if edge is not properly defined
        else:
            log.error('Parameters are not correct defined!')
            raise AttributeError

        # if edge is in the network, start removing it
        if _edge.id in self.edges:

            # remove edge from heads and tails counter of the nodes
            self.nodes[_edge.v.id].outgoing.remove(_edge.id)
            self.nodes[_edge.w.id].incoming.remove(_edge.id)

            # TODO: This is probabily not needed.
            if not self.directed:
                self.nodes[_edge.v.id].incoming.remove(_edge.id)
                self.nodes[_edge.w.id].outgoing.remove(_edge.id)

            # update maps
            del self._edge_to_nodes_map[_edge.id]
            self._node_to_edges_map[(_edge.v.id, _edge.w.id)].remove(_edge.id)

            # delete the edge
            del self.edges[_edge.id]

    def remove_edges_from(self, edges: List[str]) -> None:
        """Remove multiple edges given in a list of edges/nodes.

        Parameters
        ----------
        edges : list of edge ids or node tuples as str
            The parameter edges must be a list with edge ids or tuples of node
            ids as strings.

        Examples
        --------

        Generate a simple network.

        >>> from pathpy import Network
        >>> net = Network()
        >>> net.add_edge('ab','a','b')
        >>> net.add_edge('bc','b','c')
        >>> net.add_edge('ac','a','c')

        Remove mutliple edges form the network

        >>> net.remove_edges_from('ab', ('b', 'c'))

        """
        for e in edges:
            if isinstance(e, tuple):
                self.remove_edge(*e)
            else:
                self.remove_edge(e)

    def has_edge(self, *args: Any) -> bool:
        """Return True if an edge e between node v and node w exists.

        Mutliple input options are available.

        1. `has_edge(v, w)`: The first way to check if an edge exists, is via a
            tuple of source node `v` and target node `w`. Thereby, `v` and `w`
            are either the string values of the node ids or :py:class:`Node`
            objects.

        2. `has_edge(e)`: The thrid way to chekc if and edge exist, is directly
           via using an :py:class:`Edge` object or edge id.

        Parameters
        ----------
        e : str or py:class:`Edge`
            The parameter `e` describes the edge which schould be checked to be
            in the network. The parameter `e` can either be a string value, a
            :py:class:`Edge` object, or not defined. If the edge is not defined
            but two node parameter are given, an edge based on the nodes is
            checked.

        v : str or :py:class:`Node`

            The parameter `v` is the source node of the edge, which should be
            checked. The parameter `v` can either be string value, a
            :py:class:`Node` object or not defined. If the node is not defined
            an :py:class:`Edge` object or edge id has to be given.

        w : str or :py:class:`Node`
            The parameter `w` is the target node of the edge, which should be
            checked. The parameter `w` can either be string value, a
            :py:class:`Node` object or not defined. If the node is not defined
            an :py:class:`Edge` object or edge id has to be given.


        Returns
        -------
        bool
            Returns True if the network has an edge e otherwise False.

        Examples
        --------

        Generate a simple network.

        >>> from pathpy import Network
        >>> net = Network()
        >>> net.add_edge('ab','a','b')
        >>> net.add_edge('bc','b','c')

        Check if edge exists

        >>> net.has_edge('ab')
        True

        >>> net.has_edge('b','c')
        True

        """
        # check the inputs
        # returns a dict with
        # variable = {'id':str, 'object':class, 'given':bool}
        e, v, w = self._check_edge(*args)
        return e['given']

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
