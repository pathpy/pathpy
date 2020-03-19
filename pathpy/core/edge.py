#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : edge.py -- Base class for an single edge
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2020-03-19 11:20 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, List

from .. import logger
from .base import BaseClass
from .base import NodeDict
from .utils.separator import separator
from .utils._check_node import _check_node
from . import Node

# create logger for the Edge class
log = logger(__name__)


class Edge(BaseClass):
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
        :ref:`config_file`.

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

    def __init__(self, v: Node, w: Node, uid: str = None,
                 directed: bool = True, **kwargs: Any) -> None:
        """Initialize the edge object."""

        # initialize the base class
        super().__init__(**kwargs)

        # set unique identifier of the edge
        self._uid: str

        # inidcator whether the edge is directed or undirected
        self._directed: bool = directed

        # a dictionary containing node objects
        self._nodes: NodeDict = NodeDict(dict)

        # use separator if given otherwise use config default value
        self.separator: dict = separator(mode='edge', **kwargs)

        # add attributes to the edge
        self.attributes.update(**kwargs)

        # add nodes
        self.add_nodes_from([v, w])

        # set source and target nodes
        self._v: str = list(self.nodes.values())[0].uid
        self._w: str = list(self.nodes.values())[-1].uid

        # set uid of the edge
        if uid is None:
            self._uid = self.v.uid + self.separator['edge'] + self.w.uid
        else:
            self._uid = uid

        # update associated nodes
        self.v.outgoing.add(self.uid)
        self.w.incoming.add(self.uid)
        if not self.directed:
            self.w.outgoing.add(self.uid)
            self.v.incoming.add(self.uid)

    def __repr__(self) -> str:
        """Return the description of the edge.

        Returns
        -------
        str

            Returns the description of the edge with the class and assigned
            edge uid.

        Examples
        --------
        Generate new edge without dedicated uid

        >>> from pathpy import Node, Edge
        >>> vw = Edge('v', 'w')
        >>> vw
        Edge v-w

        """
        return '{} {}'.format(self._desc(), self.uid)

    def _desc(self) -> str:
        """Return a string *Edge()*."""
        return '{}'.format(self.__class__.__name__)

    def __hash__(self) -> Any:
        """Returns the unique hash of the edge.

        Here the hash value is defined by the unique edge id!

        """
        return hash(self.uid)

    def __del__(self) -> None:
        """Delete the edge."""
        # update associated nodes
        try:
            self.v.outgoing.remove(self.uid)
        except Exception:
            pass
        try:
            self.w.incoming.remove(self.uid)
        except Exception:
            pass

        if not self.directed:
            try:
                self.v.incoming.remove(self.uid)
            except Exception:
                pass
            try:
                self.w.outgoing.remove(self.uid)
            except Exception:
                pass

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
        return self._uid

    @property
    def nodes(self) -> NodeDict:
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

            Retun the source :py:class:`Node` of the edge.

        Examples
        --------
        Generate an single edge and return the source node.

        >>> from pathpy import Edge
        >>> vw = Edge('v','w')
        >>> vw.v
        Node v

        """
        return self.nodes[self._v]

    @property
    def w(self) -> Node:
        """Return the target node w of the edge.

        Returns
        -------
        :py:class:`Node`

            Retun the target :py:class:`Node` of the edge.

        Examples
        --------
        Generate an single edge and return the target node.

        >>> from pathpy import Edge
        >>> vw = Edge('v','w')
        >>> vw.w
        Node w

        """
        return self.nodes[self._w]

    @property
    def directed(self) -> bool:
        """Return if the edge is directed (True) or undirected (False).

        Returns
        -------
        bool

            Retun ``True`` if the edge is directed or ``False`` if the edge is
            undirected.

        Examples
        --------
        Generate an undirected edge.

        >>> from pathpy import Edge
        >>> vw = Edge('v', 'w', directed=False)
        >>> vw.directed
        False

        """
        return self._directed

    def add_node(self, node: Node, **kwargs: Any) -> None:
        """Add a single node to the edge.

        Parameters
        ----------
        node : Node

            The :py:class:`Node` object, which will be added to the edge.

        kwargs : Any, optional (default = {})

            Attributes assigned to the node as key=value pairs.

        .. note::

            This function is only used internally. It can be used to consider
            hyperedges in a futher version of pathpy.

        """
        # check if the right object is provided.
        if self.check:
            node = _check_node(self, node, **kwargs)

        # add node to the edge
        self.nodes[node.uid] = node

        # update node counter
        self.nodes.increase_counter(node.uid, self.attributes.frequency)

    def add_nodes_from(self, nodes: List[Node], **kwargs: Any) -> None:
        """Add multiple nodes from a list.

        Parameters
        ----------
        nodes : List[Node]

            Nodes from a list of :py:class:`Node` objects are added to the
            edge.

        kwargs : Any, optional (default = {})

            Attributes assigned to all nodes in the list as key=value pairs.

       .. note::

            This function is only used internally. It can be used to consider
            hyperedges in a futher version of pathpy.

        """
        # iterate over a list of nodes
        # TODO: parallelize this function
        for node in nodes:
            self.add_node(node, **kwargs)

    def update(self, other: Edge = None, attributes: bool = True,
               **kwargs: Any) -> None:
        """Update of the edge object.

        Update the edge with new kwargs or based on an other given
        :py:class:`Edge` object. If an other object is given, the other
        attributes can be used or not.

        Parameters
        ----------
        other : Edge, optional (default = None)

            An other :py:class:`Edge` object, which is used to update the edge
            attributes and properties.

        attributes : bool, optional (default = True)

            If ``True`` the attributes from the other edge are written to the
            initial edge. If ``False`` only the information about the
            associated nodes is updated.

        kwargs : Any

            Keyword arguments stored as edges attributes. Attributes are added
            to the edge as ``key=value`` pairs.

        Examples
        --------
        Create an :py:class:`Edge` object with an assigned attribute.

        >>> from pathpy import Edge
        >>> ab = Edge('a','b', length=10)
        >>> ab['length']
        10

        Update attributes (and add new).

        >>> ab.update(length = 2, capacity = 3, speed = 10)
        >>> ab.attributes
        {'length': 2, 'capacity': 3, 'speed': 10}

        Create a new edge.

        >>> cd = Edge('c', 'd', length=4, speed=30)
        >>> ab.update(cd)
        >>> ab.attributes
        {'length': 4, 'capacity': 3, 'speed': 30}

        """
        if other:
            # get relations with the associated nodes
            self.v.update(other.v, attributes=False)
            self.w.update(other.w, attributes=False)

            # get the attributes
            if attributes:
                self.attributes.update(
                    **other.attributes.to_dict(history=False))

        self.attributes.update(**kwargs)


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
