"""Edge class"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : edge.py -- Base class for an single edge
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Wed 2021-04-21 20:27 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, Optional, Union, Set
from collections import defaultdict
from singledispatchmethod import singledispatchmethod

from pathpy import logger
from pathpy.core.classes import BaseEdge
from pathpy.core.collections import BaseCollection
from pathpy.core.node import Node, NodeSet, NodeCollection

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
        # pylint: disable=invalid-name
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
        # pylint: disable=invalid-name
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


class HyperEdge(BaseEdge):
    """Base class for an single edge.


    See Also
    --------
    Node

    """

    def __init__(self, v: Set[Node], w: Optional[Set[Node]] = None,
                 uid: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize the edge object."""

        # initialize the base class
        super().__init__(uid=uid, **kwargs)

        # a set containing node objects
        self._nodes: set = set()

        # add attributes to the edge
        self.attributes.update(**kwargs)

        # check nodes
        if isinstance(v, Node):
            v = {v}
        if isinstance(w, Node):
            w = {w}
        elif w is None:
            w = v

        if not isinstance(v, set) or not isinstance(w, set):
            LOG.error('Nodes must be a set of Node objects!')
            raise TypeError

        if not all((isinstance(n, Node) for n in v | w)):
            LOG.error('All nodes must be Node objects!')
            raise TypeError

        # add nodes
        self._v: NodeSet = NodeSet()
        self._w: NodeSet = NodeSet()

        for node in v:
            self._v.add(node)
        for node in w:
            self._w.add(node)

        self._nodes = v.union(w)

    def __str__(self) -> str:
        """Print a summary of the edge.
        """
        return self.summary()

    @property
    def uid(self) -> str:
        """Return the unique identifier (uid) of the edge.
        """
        return super().uid

    @property
    def nodes(self) -> Set[Node]:
        """Return the associated nodes of the edge.
        """
        return self._nodes

    @property
    def v(self) -> NodeSet:
        """Return the source node v of the edge.
        """
        # pylint: disable=invalid-name
        return self._v

    @property
    def w(self) -> NodeSet:
        """Return the target node w of the edge.
        """
        # pylint: disable=invalid-name
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
        ]

        if self.v == self.w:
            summary += ['Nodes: \t\t{}'.format(self.v.__repr__())]
        else:
            summary += [
                'Source node:\t{}\n'.format(self.v.__repr__()),
                'Target node:\t{}'.format(self.w.__repr__())]

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
    # pylint: disable=too-many-instance-attributes

    def __init__(self, directed: bool = True,
                 multiedges: bool = False,
                 hyperedges: bool = False,
                 nodes: Optional[NodeCollection] = None) -> None:
        """Initialize the network object."""

        # initialize the base class
        super().__init__()

        # inidcator whether the network is directed or undirected
        self._directed: bool = directed

        # indicator whether the network has multi-edges
        self._multiedges: bool = multiedges

        # indicator whether the network has hyper-edges
        self._hyperedges: bool = hyperedges

        # collection of nodes
        self._nodes: Any = NodeCollection()
        if nodes is not None:
            self._nodes = nodes

        # map node tuples to edges
        self._nodes_map: defaultdict = defaultdict(EdgeSet)

        # map single node to edges
        self._node_map: defaultdict = defaultdict(set)

        # class of objects
        self._node_class: Any = Node
        self._edge_class: Any = Edge
        if self._hyperedges:
            self._edge_class = HyperEdge

        self._added: set = set()
        self._removed: set = set()

    @singledispatchmethod
    def __contains__(self, item) -> bool:
        """Returns if item is in edges."""
        _contain: bool = False

        return _contain

    @__contains__.register(Edge)  # type: ignore
    @__contains__.register(HyperEdge)  # type: ignore
    def _(self, item: Edge) -> bool:
        """Returns if item is in edges."""
        _contain: bool = False
        if item in self.values():
            _contain = True
        return _contain

    @__contains__.register(str)  # type: ignore
    def _(self, item: str) -> bool:
        """Returns if item is in edges."""
        _contain: bool = False
        if item in self.keys():
            _contain = True
        return _contain

    @__contains__.register(tuple)  # type: ignore
    @__contains__.register(list)
    def _(self, item: Union[tuple, list]) -> bool:
        """Returns if item is in edges."""
        _contain: bool = False

        if all((isinstance(i, set) for i in item)):
            try:
                if tuple(map(lambda x: frozenset({self.nodes[i] for i in x}),
                             item)) in self._nodes_map:
                    _contain = True
            except KeyError:
                pass
        elif all((isinstance(i, (str, self._node_class)) for i in item)):
            try:
                if tuple(self.nodes[i] for i in item) in self._nodes_map:
                    _contain = True
            except KeyError:
                pass

        return _contain

    def __getitem__(self, key: Union[str, tuple, Edge]
                    ) -> Union[Edge, EdgeSet, EdgeCollection]:
        """Returns a node object."""

        if (isinstance(key, tuple)
                and all((isinstance(i, (str, Node)) for i in key))):
            _node = tuple(self.nodes[i] for i in key)
            if self.multiedges:
                edge = self._nodes_map[_node]
            else:
                edge = self._nodes_map[_node][-1]

        elif (isinstance(key, tuple)
              and all((isinstance(i, set) for i in key))):
            _nodes: list = []
            for i, nodes in enumerate(key):
                _nodes.append(set())
                for node in nodes:
                    _nodes[i].add(self.nodes[node])
            _nodes = (frozenset(_nodes[0]), frozenset(_nodes[1]))

            if self.multiedges:
                edge = self._nodes_map[_nodes]
            else:
                edge = self._nodes_map[_nodes][-1]

        elif isinstance(key, self._edge_class) and key in self:
            edge = key
        else:
            edge = self._map[key]
        return edge

    def __lshift__(self, edge: Edge) -> None:
        """Quick assigment of an edge"""
        self[edge.uid] = edge
        self._added.add(edge)

    def __rshift__(self, edge: Edge) -> None:
        """Quick removal of an edge"""
        self.pop(edge.uid, None)
        self._removed.add(edge)

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
        """Return if edges are multiedges. """
        return self._multiedges

    @property
    def hyperedges(self) -> bool:
        """Return if edges are hyperedges. """
        return self._hyperedges

    @singledispatchmethod
    def add(self, *edge, **kwargs: Any) -> None:
        """Add multiple edges. """

        raise NotImplementedError

    @add.register(Edge)  # type: ignore
    @add.register(HyperEdge)  # type: ignore
    def _(self, *edge: Edge, **kwargs: Any) -> None:

        # remove uid kwarg for edge objects
        kwargs.pop('uid', None)

        if not kwargs.pop('checking', True):
            self._add(edge[0], indexing=kwargs.pop('indexing', True))
            return

        # check if more then one edge is given raise an AttributeError
        if len(edge) != 1:
            LOG.error('More then one edge was given.')
            raise AttributeError

        # check if edge is an HyperEdge and hyper edges are enabled
        if isinstance(edge[0], HyperEdge) and not self.hyperedges:
            LOG.error('EdgeCollection cannot store HyperEdges! '
                      ' Please enable hyperedges!')
            raise AttributeError

        # get edge object
        _edge = edge[0]

        # check if edge exists already
        if _edge not in self and _edge.uid not in self.keys():

            # check if node exists already
            for node in _edge.nodes:
                if node not in self.nodes:
                    self.nodes.add(node)

            # check if single edge between node v and w
            if (_edge.v, _edge.w) not in self or self.multiedges:

                # update edge attributes
                if kwargs:
                    # print(kwargs)
                    _edge.update(**kwargs)

                # add edge to the network
                self._add(_edge)
            else:
                self._if_exist(_edge, **kwargs)
        else:
            # raise error if edge already exists
            self._if_exist(_edge.uid, **kwargs)

    @add.register(str)  # type: ignore
    @add.register(Node)  # type: ignore
    def _(self, *edge: Union[str, Node], **kwargs: Any) -> None:

        # get additional parameters
        uid: Optional[str] = kwargs.pop('uid', None)
        nodes: bool = kwargs.pop('nodes', True)

        # check if all objects are node or str
        if not all(isinstance(arg, (Node, str)) for arg in edge):
            LOG.error('All objects have to be Node objects or str uids!')
            raise TypeError

        # if nodes is true add nodes
        if nodes:
            _nodes: tuple = ()
            for node in edge:
                if node not in self.nodes:
                    self.nodes.add(node)
                _nodes += (self.nodes[node],)

            # create new edge object and add it to the network
            if _nodes not in self or self.multiedges:
                self.add(self._edge_class(*_nodes, uid=uid, **kwargs))
            # raise error if edge already exists
            else:
                self._if_exist(_nodes, **kwargs)

        # add edge with unknown nodes
        else:
            self.add(self._edge_class(self._node_class(), self._node_class(),
                                      uid=edge[0], **kwargs))

    @add.register(tuple)  # type: ignore
    @add.register(list)  # type: ignore
    def _(self, *edge: Union[tuple, list], **kwargs: Any) -> None:

        # check length of the input
        if len(edge) == 1:
            self.add(*edge[0], **kwargs)
        # convert to set and add hyperedge
        elif len(edge) == 2 and self.hyperedges:
            self.add(set(edge[0]), set(edge[1]), **kwargs)
        elif len(edge) > 1 and not self.hyperedges:
            for _edge in edge:
                self.add(_edge, **kwargs)
        else:
            LOG.error('The provided edge "%s" is of the wrong format!', edge)
            raise AttributeError

    @add.register(set)  # type: ignore
    def _(self, *edge: set, **kwargs: Any) -> None:

        # check if hyperedges are enabled:
        if not self.hyperedges:
            LOG.error('EdgeCollection cannot store HyperEdges! '
                      ' Please enable hyperedges!')
            raise AttributeError

        # get additional parameters
        uid: Optional[str] = kwargs.pop('uid', None)

        _nodes: list = []
        for i, nodes in enumerate(edge):
            _nodes.append(set())
            for node in nodes:
                if node not in self.nodes:
                    self.nodes.add(node)
                _nodes[i].add(self.nodes[node])
        if len(_nodes) == 1:
            _nodes.append(_nodes[0])

        if (_nodes[0], _nodes[1]) not in self or self.multiedges:
            self.add(self._edge_class(_nodes[0], _nodes[1], uid=uid, **kwargs))

        else:
            # raise error if node already exists
            self._if_exist(_nodes, **kwargs)

    def _if_exist(self, edge: Any, **kwargs: Any) -> None:
        """Helper function if the edge does already exsist."""
        # pylint: disable=no-self-use
        # pylint: disable=unused-argument
        LOG.error('The edge "%s" already exists in the Network', edge)
        raise KeyError

    def update_index(self) -> None:
        """Update the index structure of the EdgeCollection."""
        for edge in list(self._added):
            _v: Any = edge.v
            _w: Any = edge.w

            if isinstance(edge, HyperEdge):
                _v = frozenset(edge.v.values())
                _w = frozenset(edge.w.values())

            self._nodes_map[(_v, _w)].add(edge)
            if not self.directed:
                self._nodes_map[(_w, _v)].add(edge)

            self._node_map[_v].add(edge)
            self._node_map[_w].add(edge)

            self._added.discard(edge)

        for edge in list(self._removed):

            _v = edge.v
            _w = edge.w

            if isinstance(edge, HyperEdge):
                _v = frozenset(edge.v.values())
                _w = frozenset(edge.w.values())

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

            self._removed.discard(edge)

    def _add(self, edge: Edge, indexing: bool = True) -> None:
        """Add an edge to the set of edges."""
        # add edge to the dict
        self[edge.uid] = edge

        # store new added edge
        self._added.add(edge)

        # update the index structure
        if indexing:
            self.update_index()

    @singledispatchmethod
    def remove(self, *edge, **kwargs: Any) -> None:
        """Remove multiple edges. """
        raise NotImplementedError

    @remove.register(Edge)  # type: ignore
    @remove.register(HyperEdge)  # type: ignore
    def _(self, *edge: Edge, **kwargs: Any) -> None:
        # pylint: disable=unused-argument

        if not kwargs.pop('checking', True):
            self._remove(edge[0], indexing=kwargs.pop('indexing', True))
            return

        if edge[0] in self:
            self._remove(edge[0])

    @remove.register(str)  # type: ignore
    @remove.register(Node)  # type: ignore
    def _(self, *edge: Union[str, Node], **kwargs: Any) -> None:

        # get additional parameters
        uid: Optional[str] = kwargs.pop('uid', None)

        if len(edge) == 1 and edge[0] in self:
            self._remove(self[edge[0]])
        elif uid is not None:
            self.remove(uid)
        elif edge in self:
            _edge = self[edge]
            if isinstance(_edge, self._edge_class):
                self._remove(_edge)
            elif isinstance(_edge, EdgeSet):
                for _e in list(_edge):
                    self._remove(_e)
            else:
                raise NotImplementedError
        else:
            LOG.warning('No edge was removed!')

    @remove.register(tuple)  # type: ignore
    @remove.register(list)  # type: ignore
    def _(self, *edge: Union[tuple, list], **kwargs: Any) -> None:

        # check length of the input
        if len(edge) == 1:
            self.remove(*edge[0], **kwargs)
        # convert to set and add hyperedge
        elif len(edge) == 2 and self.hyperedges:
            self.remove(set(edge[0]), set(edge[1]), **kwargs)
        else:
            LOG.warning('No edge was removed!')

    @remove.register(set)  # type: ignore
    def _(self, *edge: set, **kwargs: Any) -> None:

        # check if hyperedges are enabled:
        if not self.hyperedges:
            LOG.error('EdgeCollection cannot remove HyperEdges! '
                      ' Please enable hyperedges!')
            raise AttributeError

        # get additional parameters
        uid: Optional[str] = kwargs.pop('uid', None)

        if len(edge) == 1:
            edge = (edge[0], edge[0])

        if uid is not None:
            self.remove(uid)
        elif edge in self:
            _edge = self[edge]
            if isinstance(_edge, self._edge_class):
                self._remove(_edge)
            elif isinstance(_edge, EdgeSet):
                for _e in list(_edge):
                    self._remove(_e)
            else:
                raise NotImplementedError
        else:
            LOG.warning('No edge was removed!')

    def _remove(self, edge: Edge, indexing: bool = True) -> None:
        """Remove an edge from the set of edges."""
        # remove edge from the dict
        self.pop(edge.uid, None)

        # store removed edge
        self._removed.add(edge)

        # update the index structure
        if indexing:
            self.update_index()

    def copy(self, nodes: Optional[NodeCollection] = None) -> EdgeCollection:
        """Return a new copy of the edge collection."""

        if nodes is None:
            nodes = self.nodes.copy()

        edges = EdgeCollection(directed=self.directed,
                               multiedges=self.multiedges,
                               hyperedges=self.hyperedges,
                               nodes=nodes)

        for edge in self.values():
            edges.add(edge)

        return edges


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
