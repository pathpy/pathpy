"""Edge class"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : edge.py -- Base class for an single edge
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Tue 2020-07-14 09:00 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, Optional, Union, cast
from collections import defaultdict

from pathpy import logger
from pathpy.core.base import BaseEdge, BaseCollection
from pathpy.core.node import Node, NodeCollection

# create logger for the Edge class
LOG = logger(__name__)


class Edge(BaseEdge):
    """Base class for an single edge.

    An edge is (together with nodes) one of the two basic units out of which
    networks are constructed. Each edge has two nodes to which it is attached,
    called its endpoints. Edges may be directed or undirected; undirected edges
    are also called lines and directed edges are also called arcs or arrows. In
    an undirected network, an edge may be represented as the set of its nodes,
    and in a directed network it may be represented as an ordered pair of its
    vertices.

    The two nodes forming an :py:class:`Edge` are said to be the endpoints of
    this edge, and the edge is said to be incident to the nodes.

    In ``pathpy`` the edge is referenced by its unique identifier (``uid``),
    connects two :py:class:`Node` objects and can store any arbitrary python
    objects as attributes.

    .. note::

       To generate an edge, only two nodes have to be defined. ``pathpy`` will
       automatically create a unique identifier (``uid``) for the edge based on
       the node uids. In this case, the edge ``uid`` is defined as a
       combination of the node uids separated by ``-``. The separation sign can
       be changed in the config file.

    Parameters
    ----------

    v : Node

        This parameter defines the source of the edge (if directed),
        i.e. v->w. Beside a py:class:`Node` object also a ``str`` node uid can
        be entered, in this case, a new :py:class:`Node` will be created.

    w : Node

        This parameter defines the target of the edge (if directed)
        i.e. u->v. Beside a py:class:`Node` object also a ``str`` node uid can
        be entered, in this case, a new :py:class:`Node` will be created.

    uid : str, optional (default = None)

        The parameter ``uid`` is the unique identifier for the edge. Every edge
        should have an uid. The uid is converted to a string value and is used
        as a key value for all dict which saving edge objects. If no edge uid
        is specified the edge ``uid`` will be defined as a combination of the
        node uids separated by ``-``. The separation sign can be changed in the
        config file.

    directed : bool, optional (default = True)

        If ``True`` the edge is directed, i.e. quantities can only transmited
        from the source node ``v`` to the traget node ``w``. If ``False`` the
        edge is undirected, i.e. quantities can be transmited in both
        directions. Per default edges in ``pathpy`` are directed.

    kwargs : Any

        Keyword arguments to store edge attributes. Attributes are added to the
        edge as ``key=value`` pairs.

    Examples
    --------
    From the ``pathpy`` import the :py:class:`Node` and :py:class:`Edge` classes.

    >>> from pathpy import Node, Edge

    Create an edge ``e`` with given nodes.

    >>> v = Node('w')
    >>> w = Node('v')
    >>> e = Edge(v, w, uid='e')
    >>> e.uid
    e

    Create an edge with given node uids and no edge uid.

    >>> ab = Edge('a', 'b')
    >>> ab.uid
    a-b

    Show the associated node objects

    >>> ab.nodes
    NodeDict(<class 'dict'>, {'a': Node a, 'b': Node b})

    Create an edge with attached attribute.

    >>> ab = Edge('a','b', length=10)

    Add attribute to the edge.

    >>> ab['capacity'] = 5.5

    Show attached attributes

    >>> ab.attributes
    {'length': 10, 'capacity': 5}

    Change attribute.

    >>> ab['length'] = 5

    Update attributes (and add new).

    >>> ab.update(length = 2, capacity = 3, speed = 10)
    >>> ab.attributes
    {'length': 2, 'capacity': 3, 'speed': 10}

    Get the weight of the edge. Per default the attribute with the key 'weight'
    is used as weight. Should there be no such attribute, a new one will be
    crated with weight = 1.0.

    >>> ab.weight()
    1.0

    If an other attribute should be used as weight, the option weight has to be
    changed.

    >>> ab.weight('length')
    2

    If a weight is assigned but for calculation a weight of 1.0 is needed, the
    weight can be disabled with ``False`` or None.

    >>> ab['weight'] = 4
    >>> ab.weight()
    4.0
    >>> ab.weight(False)
    1.0

    Make copy of the edge.

    >>> ef = ab.copy()
    >>> ef.uid
    'a-b'

    Make a plot element and plot the edge as a png image.

    .. todo::

        Make a single plot command for plotting edges.
        The code below is not working yet!

    >>> plt = ab.plot()
    >>> plt.show('png')

    .. plot::

       import pathpy as pp
       ab = pp.Edge('a','b')
       net = pp.Network()
       net.add_edge(ab)
       plt = net.plot()
       plt.show('png')

    Create an undirected edge.

    >>> cd = Edge('c', 'd', directed=False)
    >>> plt = ab.plot()
    >>> plt.show('png')

    .. plot::

       import pathpy as pp
       cd = pp.Edge('c','d',directed=False)
       net = pp.Network(directed=False)
       net.add_edge(cd)
       plt = net.plot()
       plt.show('png')


    See Also
    --------
    Node

    """

    def __init__(self, v: Node, w: Node, uid: Optional[str] = None,
                 **kwargs: Any) -> None:
        """Initialize the edge object."""

        # initialize the base class
        super().__init__(uid=uid, **kwargs)

        # a set containing node objects
        self._nodes: set = set()

        # add attributes to the edge
        self.attributes.update(**kwargs)

        # check nodes
        if not isinstance(v, Node) or not isinstance(w, Node):
            LOG.error('v and w have to be Node objects!')
            raise TypeError

        # add nodes
        self._v: Node = v
        self._w: Node = w

        self._nodes.add(v)
        self._nodes.add(w)

    def __str__(self) -> str:
        """Print a summary of the edge.

        The summary contains the uid, the associated nodes, and if it is
        directed or not.

        If logging is enabled (see config), the summary is written to the log
        file and showed as information on in the terminal. If logging is not
        enabled, the function will return a string with the information, which
        can be printed to the console.

        """
        return self.summary()

    @property
    def uid(self) -> str:
        """Return the unique identifier (uid) of the edge.

        Returns
        -------
        str

            Return the edge identifier as a string.

        Examples
        --------
        Generate a single edge and print the id.

        >>> from pathpy import Edge
        >>> vw = Edge('v','w')
        >>> vw.uid
        'v-w'

        """
        return super().uid

    @property
    def nodes(self) -> set:
        """Return the associated nodes of the edge.

        Returns
        -------
        :py:class:`NodeDict`

            Return a dictionary with the :py:class:`Node` uids as key and the
            :py:class:`Node` objects as values, associated with the edge.

        Examples
        --------
        Generate a single edge with a color attribute.

        >>> from pathpy import Edge
        >>> vw = Edge('v','w', color='red')

        Get the nodes of the edge

        >>> vw.nodes
        {'v': Node v, 'w': Node w}

        """
        return self._nodes

    @property
    def v(self) -> Node:
        """Return the source node v of the edge.

        Returns
        -------
        :py:class:`Node`

            Return the source :py:class:`Node` of the edge.

        Examples
        --------
        Generate an single edge and return the source node.

        >>> from pathpy import Edge
        >>> vw = Edge('v','w')
        >>> vw.v
        Node v

        """
        return self._v

    @property
    def w(self) -> Node:
        """Return the target node w of the edge.

        Returns
        -------
        :py:class:`Node`

            Return the target :py:class:`Node` of the edge.

        Examples
        --------
        Generate an single edge and return the target node.

        >>> from pathpy import Edge
        >>> vw = Edge('v','w')
        >>> vw.w
        Node w

        """
        return self._w

    def summary(self) -> str:
        """Returns a summary of the edge.

        The summary contains the uid, the associated nodes, and if it is
        directed or not.

        If logging is enabled (see config), the summary is written to the log
        file and showed as information on in the terminal. If logging is not
        enabled, the function will return a string with the information, which
        can be printed to the console.

        Returns
        -------
        str

            Return a summary of the edge.

        """
        summary = [
            'Uid:\t\t{}\n'.format(self.uid),
            'Type:\t\t{}\n'.format(self.__class__.__name__),
            'Source node:\t{}\n'.format(self.v.__repr__()),
            'Target node:\t{}'.format(self.w.__repr__()),
        ]

        return ''.join(summary)


class EdgeSet(BaseCollection):
    """A set of edges"""

    def add(self, edge: Edge) -> None:
        """Add a node to the set of nodes."""
        # pylint: disable=unused-argument
        self._map[edge.uid] = edge

    def discard(self, edge: Edge) -> None:
        """Removes the specified item from the set."""
        self.pop(edge.uid, None)

    def __getitem__(self, key: Union[int, str, Edge]) -> Edge:
        """Returns a node object."""
        edge: Edge
        if isinstance(key, Edge) and key in self:
            edge = key
        elif isinstance(key, (int, slice)):
            edge = list(self._map.values())[key]
        else:
            edge = self._map[key]
        return edge

    def __setitem__(self, key: Any, value: Any) -> None:
        """set a object"""
        for edge in self.values():
            edge[key] = value


class EdgeCollection(BaseCollection):
    """A collection of edges"""

    def __init__(self, directed: bool = True, multiedges: bool = False,
                 nodes: Optional[NodeCollection] = None) -> None:
        """Initialize the network object."""

        # initialize the base class
        super().__init__()

        # inidcator whether the network is directed or undirected
        self._directed: bool = directed

        # indicator whether the network has multi-edges
        self._multiedges: bool = multiedges

        # collection of nodes
        self._nodes: NodeCollection = NodeCollection()
        if nodes is not None:
            self._nodes = nodes

        # map node tuples to edges
        self._nodes_map: defaultdict = defaultdict(EdgeSet)

        # map single node to edges
        self._node_map: defaultdict = defaultdict(set)

    def __contains__(self, item) -> bool:
        """Returns if item is in edges."""
        _contain: bool = False
        if isinstance(item, Edge) and item in self._map.values():
            _contain = True
        elif isinstance(item, (tuple, list)):
            try:
                if tuple(self.nodes[i].uid for i in item) in self._nodes_map:
                    _contain = True
            except KeyError:
                pass

        elif isinstance(item, str) and item in self._map:
            _contain = True
        return _contain

    def __getitem__(self, key: Union[str, tuple, Edge]) -> Union[Edge, EdgeSet, EdgeCollection]:
        """Returns a node object."""
        edge: Edge
        if isinstance(key, tuple):
            _node = tuple(self.nodes[i].uid for i in key)
            if self.multiedges:
                edge = self._nodes_map[_node]
            else:
                edge = self._nodes_map[_node][-1]
        elif isinstance(key, Edge) and key in self:
            edge = key
        else:
            edge = self._map[key]
        return edge

    @property
    def nodes(self) -> NodeCollection:
        """Return the associated nodes. """
        return self._nodes

    @property
    def directed(self) -> bool:
        """Return if edges are directed. """
        return self._directed

    @property
    def multiedges(self) -> bool:
        """Return if edges are directed. """
        return self._multiedges

    def add(self, *edges: Union[str, tuple, list, Node, Edge],
            **kwargs: Any) -> None:
        """Add multiple edges. """

        uid: Optional[str] = kwargs.pop('uid', None)
        nodes: bool = kwargs.pop('nodes', True)

        if all(isinstance(arg, (str, Node)) for arg in edges) and nodes:
            edges = tuple(cast(Union[str, Node], edge)
                          for edge in zip(edges[:-1], edges[1:]))

        if isinstance(edges[0], list) and len(edges) == 1:
            edges = tuple(edges[0])

        if not edges:
            LOG.warning('No edge was added!')

        for edge in edges:
            self._add_edge(edge, uid=uid, nodes=nodes, **kwargs)

    def _add_edge(self, *edge: Union[str, tuple, list, Node, Edge],
                  uid: Optional[str] = None, nodes: bool = True,
                  **kwargs: Any) -> None:
        """Add a single edge to the network."""
        # check if the right object is provided.
        # if edge obect is given
        if len(edge) == 1 and isinstance(edge[0], Edge):
            _edge = edge[0]
            _edge.update(**kwargs)
            # check if edge exists already
            if not self.contain(_edge):

                # check if node exists already
                if _edge.v not in self.nodes:
                    self.nodes.add(_edge.v)
                if _edge.w not in self.nodes:
                    self.nodes.add(_edge.w)

                # add edge to the network
                self._add(_edge)
            else:
                # raise error if edge already exists
                self._if_edge_exists(_edge.uid, **kwargs)
                # LOG.error('The edge "%s" already exists.', _edge.uid)
                # raise KeyError

        elif len(edge) == 1 and isinstance(edge[0], (list, tuple)):
            self._add_edge(*edge[0], uid=uid, **kwargs)

        elif all(isinstance(arg, (str, Node)) for arg in edge) and nodes:
            _nodes = [cast(Union[str, Node], node) for node in edge]
            self._add_edge_from_nodes(*_nodes, uid=uid, **kwargs)

        elif len(edge) == 1 and isinstance(edge[0], str) and not nodes:
            _uid = cast(str, edge[0])
            self._add_edge_from_str(_uid, **kwargs)

        # otherwise raise error
        else:
            LOG.error('The provided edge "%s" is of the wrong type!', edge)
            raise TypeError

    def _add_edge_from_nodes(self, *nodes: Union[str, Node],
                             uid: Optional[str] = None, **kwargs: Any) -> None:
        """Helper function to add an edge from nodes."""

        _nodes: list = []
        for node in nodes:
            if node not in self.nodes:
                self.nodes.add(node)
            _nodes.append(self.nodes[node])

        if (_nodes[0], _nodes[1]) not in self or self.multiedges:
            # create new edge object and add it to the network
            self._add_edge(Edge(_nodes[0], _nodes[1], uid=uid, **kwargs))
        else:
            # raise error if node already exists
            self._if_edge_exists(_nodes, **kwargs)
            # LOG.error('The edge "%s" already exists in the Network', _nodes)
            # raise KeyError

    def _add_edge_from_str(self, edge: str, **kwargs: Any) -> None:
        """Helper function to add an edge from nodes."""
        # check if edge with given uid str exists already
        if edge not in self:
            # if not add new node with provided uid str
            self._add_edge(Edge(Node(), Node(), uid=edge, **kwargs))
        else:
            # raise error if node already exists
            self._if_edge_exists(edge, **kwargs)
            # LOG.error('The node "%s" already exists in the Network', edge)
            # raise KeyError

    def _if_edge_exists(self, edge: Any, **kwargs: Any) -> None:
        LOG.error('The node "%s" already exists in the Network', edge)
        raise KeyError

    def _add(self, edge: Edge) -> None:
        """Add an edge to the set of edges."""
        self[edge.uid] = edge

        _v: str = edge.v.uid
        _w: str = edge.w.uid

        self._nodes_map[(_v, _w)].add(edge)
        if not self.directed:
            self._nodes_map[(_w, _v)].add(edge)

        self._node_map[_v].add(edge)
        self._node_map[_w].add(edge)

    def remove(self, *edges: Union[str, tuple, list, Node, Edge],
               **kwargs: Any) -> None:
        """Remove multiple edges. """

        uid: Optional[str] = kwargs.pop('uid', None)
        nodes: bool = kwargs.pop('nodes', True)

        if (all(isinstance(arg, (str, Node)) for arg in edges)
                and nodes and len(edges) > 1):
            edges = tuple(cast(Union[str, Node], edge)
                          for edge in zip(edges[:-1], edges[1:]))

        if not edges:
            LOG.warning('No edge was removed!')

        for edge in edges:
            self._remove_edge(edge, uid=uid)

    def _remove_edge(self, *edge: Union[str, tuple, list, Node, Edge],
                     uid: Optional[str] = None) -> None:
        """Remove a single edge."""
        # check if the right object is provided.
        # if edge obect is given
        if len(edge) == 1 and isinstance(edge[0], Edge) and edge[0] in self:
            self._remove(edge[0])

        elif len(edge) == 1 and isinstance(edge[0], str) and edge[0] in self:
            _edge = cast(Edge, self[edge[0]])
            self._remove(_edge)

        elif len(edge) == 1 and isinstance(edge[0], (tuple, list)):
            self._remove_edge(*edge[0], uid=uid)

        elif all(isinstance(arg, (str, Node)) for arg in edge):

            if all(arg in self for arg in edge):
                _edges = [cast(Edge, self[cast(str, _edge)]) for _edge in edge]
            elif self.multiedges:
                _edges = [cast(Edge, _edge) for _edge in cast(
                    EdgeSet, self[edge[0], edge[1]]).values()]
            else:
                _edges = [cast(Edge, self[edge[0], edge[1]])]

            # iterate over all edges between the nodes
            for _edge in list(_edges):
                # if dedicated uid is given
                if uid is not None:
                    if _edge.uid == uid:
                        self._remove_edge(_edge)
                else:
                    # remove all edges between the nodes
                    self._remove_edge(_edge)

    def _remove_node(self, node: Union[str, Node]) -> None:
        """Remove a single node."""
        if node in self.nodes:

            # remove incident edges
            for _edge in list(self._node_map[self.nodes[node].uid]):
                self._remove_edge(_edge)

            # remove node
            self.nodes.remove(self.nodes[node])

    def _remove(self, edge: Edge) -> None:
        """Remove an edge from the set of edges."""
        self.pop(edge.uid, None)

        _v: str = edge.v.uid
        _w: str = edge.w.uid

        self._nodes_map[(_v, _w)].discard(edge)

        if not self.directed:
            self._nodes_map[(_w, _v)].discard(edge)

        self._node_map[_v].discard(edge)
        self._node_map[_w].discard(edge)

        for _a, _b in [(_v, _w), (_w, _v)]:
            if len(self._nodes_map[(_a, _b)]) == 0:
                self._nodes_map.pop((_a, _b), None)

            if len(self._node_map[_a]) == 0:
                self._node_map.pop(_a, None)

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
