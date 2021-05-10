"""Edge class"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : edge.py -- Base class for an edge
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Mon 2021-05-10 14:45 juergen>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
from typing import Any, Optional, Union

from singledispatchmethod import singledispatchmethod  # NOTE: not needed at 3.9

from pathpy import logger
from pathpy.core.core import PathPyObject, PathPyPath, PathPyCollection

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
    def v(self) -> str:
        """Return the uid of the source node v. """
        # pylint: disable=invalid-name
        return self.relations[0]

    @property
    def w(self) -> str:
        """Return the uid of the target node w. """
        # pylint: disable=invalid-name
        return self.relations[-1]

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

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the EdgeCollection object."""

        # initialize the base class
        super().__init__(*args, **kwargs)

        # indicator whether the network has multi-edges
        self._multiple: bool = kwargs.pop('multiedges', False)

        # collection of nodes
        self._nodes: PathPyCollection = kwargs.pop('nodes', PathPyCollection())

        # class of objects
        self._default_class: Any = Edge

    @property
    def multiedges(self) -> bool:
        """Return if edges are multiedges. """
        return self._multiple

    @property
    def nodes(self) -> dict:
        """Return the associated nodes. """
        return self._objects

    @singledispatchmethod
    def add(self, *args, **kwargs: Any) -> None:
        """Add multiple nodes. """
        raise NotImplementedError

    @add.register(Edge)  # type: ignore
    def _(self, *args: Edge, **kwargs: Any) -> None:
        super().add(args[0], **kwargs)

    @add.register(str)  # type: ignore
    @add.register(int)  # type: ignore
    @add.register(PathPyObject)  # type: ignore
    def _(self, *args: str, **kwargs: Any) -> None:

        # get additional parameters
        uid: Optional[str] = kwargs.pop('uid', None)

        if len(args) == 2:
            obj = self._default_class(
                *args, uid=uid, directed=self.directed, **kwargs)
            super().add(obj)
        else:
            LOG.error('Only two objects can be linked with an edge')
            raise KeyError

    @add.register(tuple)  # type: ignore
    @add.register(list)  # type: ignore
    def _(self, *args: tuple, **kwargs: Any) -> None:
        for arg in args:
            if len(arg) == 2:
                self.add(*arg, **kwargs)
            else:
                LOG.error('The provided edge "%s" is of the wrong format!', arg)
                raise AttributeError

    def _add(self, obj: Any) -> None:
        """Add an edge to the set of edges."""
        super()._add(obj)
        # update shared collection of nodes
        for uid, node in self._objects.items():
            # if Node not linked update edge objects
            if node is None and uid in self._nodes:
                self._objects[uid] = self._nodes[uid]

            # add new nodes to the shared node colection
            if uid not in self._nodes and node is None:
                self._nodes.add(uid)
            elif uid not in self._nodes and node is not None:
                self._nodes.add(node)

    @singledispatchmethod
    def remove(self, *args, **kwargs):
        """Remove objects"""
        super().remove(*args, **kwargs)

    @remove.register(Edge)  # type: ignore
    def _(self, *args: Edge, **kwargs: Any) -> None:
        super().remove(*args, **kwargs)

    @remove.register(str)  # type: ignore
    @remove.register(int)  # type: ignore
    @remove.register(PathPyObject)  # type: ignore
    def _(self, *args: Union[int, str, PathPyObject], **kwargs: Any) -> None:

        # get additional parameters
        uid: Optional[str] = kwargs.pop('uid', None)

        if len(args) == 1 and args[0] in self:
            self.remove(self[args[0]])
        elif uid is not None:
            self.remove(uid)
        elif args in self:
            for obj in list(self[args]):
                super().remove(obj)
        else:
            LOG.warning('No edge was removed!')

    @remove.register(tuple)  # type: ignore
    @remove.register(list)  # type: ignore
    def _(self, *args: Union[tuple, list], **kwargs: Any) -> None:
        for arg in args:
            self.remove(*arg, **kwargs)

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
