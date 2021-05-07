"""Edge class"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : edge.py -- Base class for an edge
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Wed 2021-05-05 16:58 juergen>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
from typing import Any, Optional, Union

from singledispatchmethod import singledispatchmethod  # NOTE: not needed at 3.9

from pathpy import logger
from pathpy.core.core import PathPyTuple, PathPyObject, PathPyPath, PathPyCollection
from pathpy.core.node import Node, NodeCollection

# create logger for the Path class
LOG = logger(__name__)


class Edge(PathPyPath):
    """Base class for an edge.

    An edge is (together with nodes) one of the two basic units out of which
    networks are constructed. Each edge has two nodes to which it is attached,
    called its endpoints. Edges may be directed or undirected; undirected edges
    are also called lines and directed edges are also called arcs or arrows. In
    an undirected network, an edge may be represented as the set of its nodes,
    and in a directed network it may be represented as an ordered pair of its
    vertices.

    In ``pathpy`` the edge is referenced by its unique identifier (``uid``),
    connects two :py:class:`PathPyObjects` and can store any arbitrary python
    objects as attributes.

    .. note::

       To generate an edge, only two nodes have to be defined. ``pathpy`` will
       automatically create a unique identifier (``uid``) for the edge.

    Parameters
    ----------

    v : str or PathPyObject

        This parameter defines the source of the edge (if directed),
        i.e. v->w. Beside a py:class:`PathPyObject` object also a ``str`` node
        uid can be entered.

    w : str or PathPyObject

        This parameter defines the source of the edge (if directed),
        i.e. v->w. Beside a py:class:`PathPyObject` object also a ``str`` node
        uid can be entered.

    uid : str, optional (default = None)

        The parameter ``uid`` is the unique identifier for the edge. Every edge
        should have an uid. The uid is converted to a string value and is used
        as a key value for all dict which saving edge objects. If no edge uid
        is specified the edge ``uid`` will be defined by pathpy based on the
        internal object id.

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

    >>> ab = Edge('a', 'b', uid = 'a-b')
    >>> ab.uid
    a-b

    Show the associated node objects

    >>> ab.objects
    {'a': Node a, 'b': Node b}

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

    def __init__(self, v: Union[str, PathPyObject],
                 w: Union[str, PathPyObject],
                 uid: Optional[str] = None,
                 directed: bool = True,
                 **kwargs: Any) -> None:
        """Initialize the node object."""

        # initialize the parent class
        super().__init__(v, w, uid=uid, directed=directed, **kwargs)

    @property
    def v(self) -> PathPyObject:
        """Return the uid of the source node v. """
        # pylint: disable=invalid-name
        return self.objects[self.relations[0]]

    @property
    def w(self) -> PathPyObject:
        """Return the uid of the target node w. """
        # pylint: disable=invalid-name
        return self.objects[self.relations[-1]]

    @property
    def nodes(self) -> dict:
        """Return the nodes of the edge."""
        return self.objects

    def summary(self) -> str:
        """Returns a summary of the edge. """
        summary = [
            'Uid:\t\t{}\n'.format(self.uid),
            'Type:\t\t{}\n'.format(self.__class__.__name__),
            'Directed:\t{}\n'.format(self.directed),
            'Nodes:\t\t{}\n'.format(self.relations),
        ]

        return ''.join(summary)


class EdgeCollection(PathPyCollection):
    """A collection of edges"""
    # pylint: disable=too-many-ancestors

    def __init__(self, directed: bool = True,
                 multiedges: bool = False,
                 nodes: Optional[NodeCollection] = None) -> None:
        """Initialize the EdgeCollection object."""

        # initialize the base class
        super().__init__(directed=directed)

        # collection of nodes
        self._nodes: Any = NodeCollection()
        if nodes is not None:
            self._nodes = nodes

        # indicator whether the network has multi-edges
        self._multiedges: bool = multiedges

        # class of objects
        self._node_class: Any = Node
        self._edge_class: Any = Edge

    @singledispatchmethod
    def __getitem__(self, key):
        return super().__getitem__(key)

    @__getitem__.register(tuple)  # type: ignore
    def _(self, key):
        if any((isinstance(i, (self._node_class)) for i in key)):
            key = tuple(self.nodes[i].uid for i in key)

        edge = super().__getitem__(key)
        if not self.multiedges and isinstance(edge, set):
            edge = next(iter(edge))
        return edge

    @singledispatchmethod
    def __contains__(self, item) -> bool:
        """Returns if item is in edges."""
        return super().__contains__(item)

    @__contains__.register(tuple)  # type: ignore
    def _(self, item: tuple) -> bool:
        return PathPyTuple((self.nodes[i].uid for i in item),
                           directed=self.directed) in self._relations \
            if any((isinstance(i, (self._node_class)) for i in item)) \
            else super().__contains__(item)

    @property
    def multiedges(self) -> bool:
        """Return if edges are multiedges. """
        return self._multiedges

    @property
    def nodes(self) -> NodeCollection:
        """Return the associated nodes. """
        return self._nodes

    @singledispatchmethod
    def add(self, *edge, **kwargs: Any) -> None:
        """Add multiple nodes. """
        raise NotImplementedError

    @add.register(Edge)  # type: ignore
    def _(self, *edge: Edge, **kwargs: Any) -> None:

        if not kwargs.pop('checking', True):
            super().add(edge[0], **kwargs)
            return

        _edge = edge[0]

        if _edge.directed != self.directed:
            _text = {True: 'directed', False: 'undirected'}
            LOG.warning('An %s edge was added to an %s edge collection!',
                        _text[_edge.directed], _text[self.directed])

        # check if node exists already
        for node in _edge.nodes.values():
            if node not in self.nodes.values():
                self.nodes.add(node)

        # check if other edge exists between v and w
        if _edge.relations not in self or self.multiedges:
            super().add(edge[0], **kwargs)
        else:
            self._if_exist(_edge, **kwargs)

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

            _node_uids = tuple((n.uid for n in _nodes))
            # create new edge object and add it to the network
            if _node_uids not in self._relations or self.multiedges:
                self.add(self._edge_class(*_nodes, uid=uid,
                         directed=self.directed, **kwargs))
            # raise error if edge already exists
            else:
                self._if_exist(_nodes, **kwargs)

        # add edge with unknown nodes
        else:
            self.add(self._edge_class(self._node_class(), self._node_class(),
                                      uid=edge[0], directed=self.directed, **kwargs))

    @add.register(tuple)  # type: ignore
    @add.register(list)  # type: ignore
    def _(self, *edge: Union[tuple, list], **kwargs: Any) -> None:

        # check length of the input
        if len(edge) == 1:
            self.add(*edge[0], **kwargs)
        # convert to set and add hyperedge
        elif len(edge) > 1:
            for _edge in edge:
                self.add(_edge, **kwargs)
        else:
            LOG.error('The provided edge "%s" is of the wrong format!', edge)
            raise AttributeError

    @singledispatchmethod
    def remove(self, *edge, **kwargs):
        """Remove objects"""
        super().remove(*edge, **kwargs)

    @remove.register(str)  # type: ignore
    @remove.register(Node)  # type: ignore
    def _(self, *edge: Union[str, Node], **kwargs: Any) -> None:

        # get additional parameters
        uid: Optional[str] = kwargs.pop('uid', None)

        if len(edge) == 1 and edge[0] in self:
            self.remove(self[edge[0]])
        elif uid is not None:
            self.remove(uid)
        elif edge in self._relations:
            for uid in list(self._relations[edge]):
                self.remove(self[uid])
            # self.remove(_edge)
            # if isinstance(_edge, self._edge_class):
            #     self._remove(_edge)
            # elif isinstance(_edge, EdgeSet):
            #     for _e in list(_edge):
            #         self._remove(_e)
            # else:
            #     raise NotImplementedError
        else:
            LOG.warning('No edge was removed!')

    @remove.register(tuple)  # type: ignore
    @remove.register(list)  # type: ignore
    def _(self, *edge: Union[tuple, list], **kwargs: Any) -> None:

        # check length of the input
        if len(edge) == 1:
            self.remove(*edge[0], **kwargs)
        # convert to set and add hyperedge
        # elif len(edge) == 2 and self.hyperedges:
        #     self.remove(set(edge[0]), set(edge[1]), **kwargs)
        else:
            LOG.warning('No edge was removed!')


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
