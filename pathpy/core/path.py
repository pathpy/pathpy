#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : network.py -- Base class for a path
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2020-03-19 15:58 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, List, Dict, Optional, Sequence
import sys

from .. import logger, config
from .base import BaseClass
from .base import NodeDict
from .base import EdgeDict
from .base import PathDict
from .utils.separator import separator
from .utils._check_node import _check_node
from .utils._check_edge import _check_edge
from .utils._check_str import _check_str
from . import Node, Edge

# create logger for the Path class
log = logger(__name__)


class Path(BaseClass):
    """Base class for a path.

    Paths are fundamental parts of networks. A path in a network is a finite or
    infinite sequence of edges which joins a sequence of nodes. In a directed
    path edges are all directed in the same direction.

    In ``pathpy`` the path is constructed based on consecutive edges. Per
    default the path is directed. A :py:class:`Path` object can store any
    arbitrary python objects as attributes. A path is referenced by its unique
    identifier (``uid``). A path can have various lengths, i.e. number of
    associated edges. Paths with length 0 consists only of one node and no
    edges.

    .. note::

       To generate a path, a sequence of edges is needed. ``pathpy`` will
       automatically create a unique identifier (``uid``) for the path based on
       the edge uids. In this case, the path ``uid`` is defined as a
       combination of the edge uids separated by ``|``. The separation sign can
       be changed in the config file.

    Parameters
    ----------

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

    args : Edge

        :py:class:`Edge` objects can be used as arguments to build a
        path. While the default options is using edges. `pathpy` also supports
        :py:class:`Node` objects and ``str`` uid to generate a path.

    kwargs : Any

        Keyword arguments to store path attributes. Attributes are added to the
        path as ``key=value`` pairs.

    See Also
    --------
    Node, Edge

    Examples
    --------

    From the ``pathpy`` import the :py:class:`Node`, :py:class:`Edge` and
    :py:class:`Path` classes.

    >>> from pathpy import Node, Edge, Path

    Create an empty path

    >>> p = Path()
    >>> len(p)
    0

    Create some edges and add them to the path.

    >>> e1 = Edge('a','b')
    >>> e2 = Edge('b','c')
    >>> p.add_edges_from([e1,e2])
    >>> len(p)
    2

    Print the uid of the path.

    >>> p.uid
    'a-b|b-c'

    Get the associated nodes and edges

    >>> p.nodes
    NodeDict(<class 'dict'>, {'a': Node a, 'b': Node b, 'c': Node c})
    >>> p.edges
    EdgeDict(<class 'dict'>, {'a-b': Edge a-b, 'b-c': Edge b-c})

    Get the path as a sequence of node and edge uids

    >>> p.as_nodes
    ['a', 'b', 'c']
    >>> p.as_edges
    ['a-b', 'b-c']

    Extend path with a new node.

    >>> p.add_node('d')
    >>> p.uid
    'a-b|b-c|c-d'

    Plot the path.

    .. todo::

        Make a single plot command for plotting paths.
        The code below is not working yet!

    >>> plt = p.plot()
    >>> plt.show('png')

    .. plot::

       import pathpy as pp
       p = pp.Path('a','b','c','d')
       net = pp.Network()
       net.add_path(p)
       plt = net.plot()
       plt.show('png')


    Create paths from string uids.

    >>> p1 = Path('a', 'b', 'c')
    >>> p2 = Path('a-b', 'b-c')
    >>> p3 = Path('a,b,c')
    >>> p4 = Path('a-b,b-c')
    >>> p5 = Path('a-b-c')
    >>> p6 = Path('a-b|b-c')

    """

    def __init__(self, *args: Edge, uid: str = '', directed: bool = True,
                 **kwargs: Any) -> None:
        """Initialize the path object."""

        # initialize the base class
        super().__init__(**kwargs)

        # set unique identifier of the path
        self._uid: str = uid

        # inidcator whether the edge is directed or undirected
        self._directed: bool = directed

        # use separator if given otherwise use config default value
        self.separator: dict = separator(mode='path', **kwargs)

        # get the max display name length
        self.max_name_length: int = kwargs.get(
            'max_name_length', config['path']['max_name_length'])

        # a dictionary containing node objects
        self._nodes: NodeDict = NodeDict(dict)

        # a dictionary containing edge objects
        self._edges: EdgeDict = EdgeDict(dict)

        # TODO : Make a unique path object instead of two lists
        # E.g. path = [(e_uid,v_uid,w_uid),(e_uid,v_uid,w_uid),...]
        # a list containing the edge uids of the path
        self._as_edges: List[str] = []

        # a list containing the node uids of the path
        self._as_nodes: List[str] = []

        # add attributes to the edge
        self.attributes.update(**kwargs)

        # add objects from args if given
        if args:
            self._add_args(*args)

    def __repr__(self) -> str:
        """Return the description of the path.

        Returns
        -------
        str

            Returns the description of the path with the class, the name (if
            deffined) and the assigned path uid.

        Examples
        --------
        Generate new path

        >>> from pathpy import Path
        >>> p = Path()
        >>> p
        Path object  at 0x140458648250512x

        """
        return '<{} object {} at 0x{}x>'.format(self._desc(),
                                                self.name,
                                                id(self))

    def _desc(self) -> str:
        """Return a string *Path()*."""
        return '{}'.format(self.__class__.__name__)

    def __len__(self) -> int:
        """Returns the number of edges in the path."""
        return len(self.as_edges)

    def __hash__(self) -> Any:
        """Returns the unique hash of the path.

        Here the hash value is defined by the unique path id!

        """
        return hash(self.uid)

    @property
    def uid(self) -> str:
        """Returns the unique identifier (uid) of the path.

        If no uid is assigned the path is labled after the assigned
        edges. e.g. if the path has edges 'a-b' and 'c-d', the uid is
        'a-b|b-c'.

        Returns
        -------
        str

            Returns the uid of the path as a string.

        Examples
        --------
        Generate a simple path

        >>> from pathpy import Path
        >>> p = Path('a','b','c')
        >>> p.uid
        'a-b|b-c'

        """
        # if uid is defined us this uid
        if self._uid != '':
            return self._uid
        # if edges are given use a combined edge uid
        elif self.number_of_edges() > 0:
            return self.separator['path'].join(self.as_edges)
        elif self.number_of_nodes() > 0:
            return self.as_nodes[0]
        else:
            return str(id(self))

    @property
    def directed(self) -> bool:
        """Return if the path is directed (True) or undirected (False).

        Returns
        -------
        bool

            Retun ``True`` if the path is directed or ``False`` if the path is
            undirected.

        Examples
        --------
        Generate an undirected path.
        >>> from pathpy import Path
        >>> p = Path('a', 'b', 'c', directed=False)
        >>> p.directed
        False

        """
        return self._directed

    @property
    def name(self) -> str:
        """Returns the name of the path.

        Name of the path. If no name is assigned the network is called after
        the assigned edge. e.g. if the path has edges 'a-b' and 'b-c', the path
        is named 'a-b|b-c'. The maximum length of the name is defined in the

        config file and is per default 5. E.g. if the path has 6 edges
        (a-b,b-c,c-d,d-e,e-f,f-g) the name of the path is
        'a-b|b-c|c-d|d-e|...|f-g'. Please, note the name of a path is NOT an
        unique identifier!

        Returns
        -------
        str

            Returns the name of the path as a string.

        Examples
        --------

        Generate simple path:

        >>> from pathpy import Path
        >>> p = Path('a', 'b', 'c')
        >>> p.name
        'a-b|b-c'

        Generate longer path:

        >>> p = Path('a', 'b', 'c', 'd', 'e', 'f', 'g')
        >>> p.name
        'a-b|b-c|c-d|d-e|...|f-g'

        """

        # if path is longer then useful, shorten name
        if len(self) > self.max_name_length:
            _name = self.separator['path'].join(
                self.as_edges[0:-2][0:self.max_name_length]) \
                + self.separator['path'] + '...' + self.separator['path'] \
                + self.as_edges[-1]
        else:
            _name = self.separator['path'].join(self.as_edges)

        return self.attributes.get('name', _name)

    @property
    def nodes(self) -> NodeDict:
        """Return the associated nodes of the path.

        Returns
        -------
        NodeDict

            Return a dictionary with the :py:class:`Node` uids as key and the
            :py:class:`Node` objects as values, associated with the path.

        Examples
        --------
        Generate a simple path.

        >>> from pathpy import Path
        >>> p = Path('a','b','c')

        Get the nodes of the path

        >>> p.nodes
        {'a': Node a, 'b': Node b, 'c': Node c}

        """
        return self._nodes

    @property
    def edges(self) -> EdgeDict:
        """Return the associated edges of the path.

        Returns
        -------
        EdgeDict

            Return a dictionary with the :py:class:`Edge` uids as key and the
            :py:class:`Edge` objects as values, associated with the path.

        Examples
        --------
        Generate a simple path.

        >>> from pathpy import Path
        >>> p = Path('a','b','c')

        Get the edges of the path

        >>> p.edges
        {'a-b': Edge a-b, 'b-c': Edge b-c}

        """
        return self._edges

    @property
    def as_nodes(self) -> List[str]:
        """Return the adjacend node uids in the path.

        Returns
        -------
        List[str]

            Return a list the :py:class:`Node` uids.

        Examples
        --------
        Generate a simple path.

        >>> from pathpy import Path
        >>> p = Path('a','b','c','a','b',)

        Get the path as a list of nodes

        >>> p.as_nodes
        ['a', 'b', 'c', 'a', 'b']

        """
        return self._as_nodes

    @property
    def as_edges(self) -> List[str]:
        """Return the adjacend edge uids in the path.

        Returns
        -------
        List[str]

            Return a list the :py:class:`Edge` uids.

        Examples
        --------
        Generate a simple path.

        >>> from pathpy import Path
        >>> p = Path('a','b','c','a','b',)

        Get the edges of the path

        >>> p.as_edges
        ['a-b', 'b-c', 'c-a', 'a-b']

        """
        return self._as_edges

    def summary(self) -> Optional[str]:
        """Returns a summary of the path.

        The summary contains the name, the used path class, if it is directed
        or not, the number of unique nodes and unique edges, and the number of
        nodes in the path.

        Since a path can multiple times pass the same node and edge objects,
        the length of the path (i.e. the consecutive nodes) might be larger
        then the number of unique nodes.

        If logging is enabled (see config), the summary is written to the log
        file and showed as information on in the terminal. If logging is not
        enabled, the function will return a string with the information, which
        can be printed to the console.

        Returns
        -------
        str

            Return a summary of the path.

        """
        summary = [
            'Name:\t\t\t{}\n'.format(self.name),
            'Type:\t\t\t{}\n'.format(self.__class__.__name__),
            'Directed:\t\t{}\n'.format(str(self.directed)),
            'Number of unique nodes:\t{}\n'.format(self.number_of_nodes()),
            'Number of unique edges:\t{}'.format(self.number_of_edges()),
            'Path length (# edges):\t{}'.format(len(self))
        ]
        if config['logging']['enabled']:
            for line in summary:
                log.info(line.rstrip())
            return None
        else:
            return ''.join(summary)

    def number_of_nodes(self, unique: bool = True) -> int:
        """Return the number of nodes in the path.

        Parameters
        ----------
        unique : bool, optional (default = True)

            If unique is ``True`` only the number of unique nodes in the path
            is returnd.

        Returns
        -------
        int

            Returns the number of nodes in the path.

        Examples
        --------
        Generate a simple path.

        >>> from pathy import Path
        >>> p = Path('a', 'b', 'c', 'a', 'b',)

        Get the number of unique nodes:

        >>> p.number_of_nodes()
        3

        Get the number of all node visits in the path:

        >>> p.number_of_nodes(unique=False)
        5

        """
        if unique:
            return len(self.nodes)
        else:
            return len(self.as_nodes)

    def number_of_edges(self, unique: bool = True) -> int:
        """Return the number of edges in the path.

        Parameters
        ----------
        unique : bool, optional (default = True)

            If unique is ``True`` only the number of unique edges in the path
            is returnd.

        Returns
        -------
        int

            Returns the number of edges in the path.

        Examples
        --------
        Generate a simple path.

        >>> from pathy import Path
        >>> p = Path('a', 'b', 'c', 'a', 'b')

        Get the number of unique edges:

        >>> p.number_of_edges()
        3

        Get the number of all observed edges in the path:

        >>> p.number_of_nodes(unique=False)
        4

        """
        if unique:
            return len(self.edges)
        else:
            return len(self.as_edges)

    def add_edges_from(self, edges: Sequence[Edge], **kwargs: Any) -> None:
        """Add multiple edges from a list to the path.

        Parameters
        ----------
        nodes : List[Edge]

            Edges from a list of :py:class:`Edge` objects are added to the
            path.

        kwargs : Any, optional(default={})

            Attributes assigned to all edges in the list as ``key=value``
            pairs.

        Examples
        --------
        Generate some edges and add them to a path

        >>> from pathpy import Edge, Path
        >>> e1 = Edge('a', 'b')
        >>> e2 = Edge('b', 'c')
        >>> p = Path()
        >>> p.add_edges_from([e1, e2])
        >>> p.uid
        'a-b|b-c'

        """

        # iterate over a list of nodes
        # TODO: parallelize this function
        for edge in edges:
            self.add_edge(edge, **kwargs)

    def add_edge(self, edge: Edge, *args: Any, **kwargs: Any) -> None:
        """Add a single edge to the path.

        Parameters
        ----------
        edge : Edge

            The :py:class:`Edge` object, which will be added to the path.

        kwargs : Any, optional(default={})

            Attributes assigned to the edge as ``key=value`` pairs.

        Examples
        --------
        Generate an edge and add it to a path.

        >>> from pathpy import Edge, Path
        >>> e = Edge('a', 'b')
        >>> p = Path()
        >>> p.add_edge(e)
        >>> p.uid
        'a-b'

        Add an other edge.

        >>> p.add_edge('b-c')
        >>> p.uid
        'a-b|b-c'

        """

        # check if the right object is provided
        if self.check:
            edge = _check_edge(self, edge, *args, **kwargs)

        # check if edge is adjacent
        if len(self.as_nodes) > 0 and self.as_nodes[-1] != edge.v.uid:
            log.error('The edge {} is not adjacent to the previous'
                      ' edge {}'.format(edge.uid, self.as_edges[-1]))
            raise AttributeError

        # add new edge to the path or update modified edge
        if (edge.uid not in self.edges or
                (edge.uid in self.edges and edge != self.edges[edge.uid])):
            self.nodes.update(edge.nodes)
            self.edges[edge.uid] = edge

        # append edge to the path and update counter
        self.as_edges.append(edge.uid)
        self.edges.increase_counter(edge.uid, self.attributes.frequency)

        # append nodes to path
        # add first node if path is empty
        if len(self.as_nodes) == 0:
            self.as_nodes.append(edge.v.uid)
            self.nodes.increase_counter(edge.v.uid, self.attributes.frequency)

        # add node to the path and update counter
        self.as_nodes.append(edge.w.uid)
        self.nodes.increase_counter(edge.w.uid, self.attributes.frequency)

    def add_node(self, node: Node, **kwargs: Any) -> None:
        """Add a single node to the path.

        Parameters
        ----------

        node : Node

            The :py:class:`Node` object, which will be added to the path.

        kwargs : Any, optional(default={})

            Attributes assigned to the node as key = value pairs.

        Examples
        --------
        Generate a node and add it to a path.

        >>> from pathpy import Edge, Path
        >>> a = Node('a')
        >>> p = Path()
        >>> p.add_node(a)
        >>> p.uid
        'a'

        Add other nodes.

        >>> p.add_node('b')
        >>> p.add_node('c')
        >>> p.uid
        'a-b|b-c'

        """

        # check if the right object is provided.
        if self.check:
            node = _check_node(self, node, **kwargs)

        # get predecessor node
        try:
            v_uid = self.as_nodes[-1]
        except Exception:
            v_uid = ''

        # add new node to the path or update modified node
        if (node.uid not in self.nodes or
                (node.uid in self.nodes and node != self.nodes[node.uid])):
            self.nodes[node.uid] = node

        # append node to path
        if len(self.as_nodes) == 0:
            self.as_nodes.append(node.uid)
            self.nodes.increase_counter(node.uid, self.attributes.frequency)

        # assigne edge from the last added node to the new node
        if v_uid != '':
            # add edge
            edge_uid = v_uid+self.separator['edge']+node.uid
            if edge_uid not in self.edges:
                self.add_edge(
                    Edge(self.nodes[v_uid], node,
                         separator=self.separator['edge']))
            else:
                self.add_edge(self.edges[edge_uid])

    def add_nodes_from(self, nodes: Sequence[Node], **kwargs: Any) -> None:
        """Add multiple nodes from a list to the path.

        Parameters
        ----------
        nodes: List[Node]

            Nodes from a list of :py:class:`Node` objects are added to the
            path.

        kwargs: Any, optional(default={})

            Attributes assigned to all nodes in the list as key = value pairs.

        Examples
        --------
        Generate some nodes and add them to a path

        >>> from pathpy import Node, Path
        >>> a = Node('a')
        >>> b = Node('b')
        >>> c = Node('c')
        >>> p = Path()
        >>> p.add_nodes_from([a, b, c])
        >>> p.uid
        'a-b|b-c'

        """
        # iterate over a list of nodes
        # TODO: parallelize this function
        for node in nodes:
            self.add_node(node, **kwargs)

    def _add_args(self, *args: Any) -> None:
        """Add args to the path."""

        # iterate over all given arguments
        for arg in args:

            # if arg is an Edge add the edge
            if isinstance(arg, Edge):
                self.add_edge(arg)

            # if arg is a Node add the node
            elif isinstance(arg, Node):
                self.add_node(arg)

            # if arg is a string, check the string and add accordingly
            elif isinstance(arg, str) and self.check:

                # check the given string
                objects = _check_str(self, arg, expected='edge')

                # iterate over the cleand string and append objects
                for string, mode in objects:
                    if mode == 'edge':
                        self.add_edges_from(string)
                    elif mode == 'node':
                        self.add_nodes_from(string)
            else:
                log.error('Invalide argument "{}"!'.format(arg))
                raise AttributeError

    def subpaths(self, min_length: int = 0,
                 max_length: int = sys.maxsize,
                 include_path: bool = False) -> Dict[str, Path]:
        """Returns a list of subpaths.

        .. warning::

            This function will be removed soon!  Functionality regarding
            sub-path statistics will be provide by the submodule subpaths!

        Parameters
        ----------
        min_length: int, optional(default=0)

            Parameter which defines the minimum length of the sub-paths. This
            parameter has to be smaller then the maximum length parameter.

        max_length: int, optional(default=sys.maxsize)

            Parameter which defines the maximum length of the sub-paths. This
            parameter has to be greater then the minimum length parameter. If
            the parameter is also greater then the maximum length of the path,
            the maximum path length is used instead.

        include_path: bool, optional(default=Flase)

            If this option is enabled also the current path is added as a
            sub-path of it self.

        Returns
        -------
        Dict[str, Paths]

            Return a dictionary with the: py: class: `Paht` uids as key and the
            : py: class: `Path` objects as values.

        Examples
        --------
        >> > from pathpy import Path
        >> > p = Path('a', 'b', 'c', 'd', 'e')
        >> > for k in p.subpaths():
        ... print(k)
        a
        b
        c
        d
        e
        a-b
        b-c
        c-d
        d-e
        a-b | b-c
        b-c | c-d
        c-d | d-e
        a-b | b-c | c-d
        b-c | c-d | d-e

        >> > for k in p.subpaths(min_length=2, max_length=2)
        ... print(k)
        a-b | b-c
        b-c | c-d
        c-d | d-e

        """

        # initializing the subpaths dictionary
        subpaths: dict = PathDict(dict)

        # get the default max and min path lengths
        _min_length: int = min_length
        _max_length: int = max_length

        # TODO: FIX DICT -> LIST
        # if min_length is zero, account also for nodes
        if _min_length <= 0:
            for node in self.as_nodes:
                # generate empty path with one node
                subpaths[node] = Path.from_nodes(
                    [self.nodes[node]], **self.attributes.to_dict())

        # find the right path lengths
        min_length = max(_min_length, 1)
        max_length = min(len(self)-1, _max_length)

        # get subpaths
        for i in range(min_length-1, max_length):
            for j in range(len(self)-i):
                # get the edge uids
                edges = [self.edges[edge] for edge in self.as_edges[j:j+i+1]]
                # assign a new path based  on the given edges
                subpaths[self.separator['path'].join(
                    self.as_edges[j:j+i+1])] = Path(
                        *edges, **self.attributes.to_dict())

        # include the path
        if include_path and _min_length <= len(self) <= _max_length:
            subpaths[self.uid] = self

        # return the dict of subpaths
        return subpaths

    # def has_subpath(self, subpath: Path) -> bool:
    #     """Return True if the path has a sub-path."""
    #     raise NotImplementedError

    # def subpath(self, *args: str) -> Path:
    #     """Returns a sup-path of the path."""
    #     raise NotImplementedError

    def update(self, other: Path = None, attributes: bool = True,
               **kwargs: Any) -> None:
        """Update of the path object.

        Update the path with new kwargs or based on an other given
        :py:class:`Path` object. If an other object is given, the other
        attributes can be used or not.

        Parameters
        ----------
        other : Path, optional (default = None)

            An other :py:class:`Path` object, which is used to update the edge
            attributes and properties.

        attributes : bool, optional (default = True)

            If ``True`` the attributes from the other path are written to the
            initial path. If ``False`` only the information about the
            associated edges and nodes is updated.

        kwargs : Any

            Keyword arguments stored as path attributes. Attributes are added
            to the path as ``key=value`` pairs.

        Examples
        --------
        Create an :py:class:`Path` object with an assigned attribute.

        >>> from pathpy import Path
        >>> p = path('a','b', 'c', length=10)
        >>> p['length']
        10

        Update attributes (and add new).

        >>> p.update(length = 2, capacity = 3, speed = 10)
        >>> p.attributes
        {'length': 2, 'capacity': 3, 'speed': 10}

        Create a new path.

        >>> q = Path('v', 'w', length=4, speed=30)
        >>> p.update(q)
        >>> p.attributes
        {'length': 4, 'capacity': 3, 'speed': 30}

        """
        if other:
            # get relations with the associated nodes
            for v in self.nodes.values():
                v.update(other.nodes[v.uid], attributes=False)

            # get the attributes
            if attributes:
                self.attributes.update(
                    **other.attributes.to_dict(history=False))

        self.attributes.update(**kwargs)

    @classmethod
    def from_nodes(cls, nodes: Sequence[Node], **kwargs: Any) -> Path:
        """Generate a Path object from a list of nodes.

        Parameters
        ----------
        nodes : List[Node]

            Nodes from a list of :py:class:`Node` objects are added to the
            path.

        kwargs : Any, optional(default={})

            Attributes assigned to the path as key = value pairs.

        Returns
        -------
        :py:class:`Path`

            Returns a :py:class:`Path` object with nodes and edges according to
            the given list of :py:class:`Node` objects.

        Examples
        --------
        Generate a simple path.

        >>> from pathpy import Path
        >>> p = Path.from_nodes(['a', 'b'])
        >>> p.nodes
        {'a': Node a, 'b': Node b}

        """
        path: Path = cls(**kwargs)
        path.add_nodes_from(nodes)
        return path

    @classmethod
    def from_edges(cls, edges: Sequence[Edge], **kwargs: Any) -> Path:
        """Generate a Path object from a list of edges.

        Parameters
        ----------
        edges : List[Edge]

            Edges from a list of :py:class:`Edge` objects are added to the
            path.

        kwargs : Any, optional(default={})

            Attributes assigned to the path as key = value pairs.

        Returns
        -------
        :py:class:`Path`

            Returns a :py:class:`Path` object with nodes and edges according to
            the given list of :py:class:`Edge` objects.

        Examples
        --------
        Generate a simple path.

        >>> from pathpy import Path
        >>> p = Path.from_edges(['a-b', 'b-c'])
        >>> p.nodes
        {'a': Node a, 'b': Node b, 'c': Node c}

        """
        path: Path = cls(**kwargs)
        path.add_edges_from(edges)
        return path


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
