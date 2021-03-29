"""Path class"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : network.py -- Base class for a path
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Mon 2021-03-29 14:23 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, Optional, Union, cast
from collections import defaultdict
from singledispatchmethod import singledispatchmethod  # NOTE: not needed at 3.9

from pathpy import logger
from pathpy.core.classes import BasePath
from pathpy.core.collecions import BaseCollection
from pathpy.core.node import Node, NodeCollection
from pathpy.core.edge import Edge, EdgeCollection

# create logger for the Path class
LOG = logger(__name__)


class Path(BasePath):
    """Base class for a path."""

    def __init__(self, *args: Union[Node, Edge], uid: Optional[str] = None,
                 **kwargs: Any) -> None:
        """Initialize the path object."""

        # initialize the base class
        super().__init__(uid=uid, **kwargs)

        # a list containing sequence of edge objects
        self._path: list = []

        # start node of the path
        self._start: Node

        # only the start node is given
        if len(args) == 1 and isinstance(args[0], Node):
            self._start = args[0]

        else:
            # otherwise check edges
            for edge in args:

                # raise error when no edges are given
                if not isinstance(edge, Edge):
                    LOG.error('"%s" has to be an Edge object!', edge)
                    raise TypeError

                # add edge if it is the first
                if len(self._path) == 0:
                    self._path.append(edge)
                    self._start = edge.v

                # check if edges are consecutive
                elif self._path[-1].w == edge.v:
                    self._path.append(edge)
                else:
                    LOG.error('Path object needs consecutive edges!')
                    raise AttributeError

    def __str__(self) -> str:
        """Print a summary of the path.

        The summary contains the name, the used path class, if it is directed
        or not, the number of unique nodes and unique edges, and the number of
        nodes in the path.

        Since a path can multiple times pass the same node and edge objects,
        the length of the path(i.e. the consecutive nodes) might be larger
        then the number of unique nodes.

        If logging is enabled(see config), the summary is written to the log
        file and showed as information on in the terminal. If logging is not
        enabled, the function will return a string with the information, which
        can be printed to the console.

        """
        return self.summary()

    def __len__(self) -> int:
        """Returns the number of edges in the path."""
        return len(self._path)

    @property
    def uid(self) -> str:
        """Returns the unique identifier(uid) of the path.

        Returns
        -------
        str

        Returns the uid of the path as a string.

        Examples
        --------
        Generate a simple path

        """
        return super().uid

    @property
    def start(self) -> Node:
        """Return the start node of the path.

        Returns
        -------
        : py: class: `Node`

        Return the start: py: class: `Node` of the path.

        Examples
        --------

        """
        return self._start

    @property
    def end(self) -> Node:
        """Return the end node of the path.

        Returns
        -------
        : py: class: `Node`

        Return the end: py: class: `Node` of the path.

        Examples
        --------

        """
        if len(self) == 0:
            end = self._start
        else:
            end = self._path[-1].w
        return end

    @property
    def nodes(self) -> list:
        """Return the associated nodes of the path.

        Returns
        -------
        NodeDict

        Return a dictionary with the: py: class: `Node` uids as key and the
        : py: class: `Node` objects as values, associated with the path.

        Examples
        --------
        Generate a simple path.

        >> > from pathpy import Path
        >> > p = Path('a', 'b', 'c')

        Get the nodes of the path

        >> > p.nodes
        {'a': Node a, 'b': Node b, 'c': Node c}

        """
        return [self._start] + [e.w for e in self._path]

    @property
    def edges(self) -> list:
        """Return the associated edges of the path.

        Returns
        -------
        EdgeDict

        Return a dictionary with the: py: class: `Edge` uids as key and the
        : py: class: `Edge` objects as values, associated with the path.

        Examples
        --------
        Generate a simple path.

        >> > from pathpy import Path
        >> > p = Path('a', 'b', 'c')

        Get the edges of the path

        >> > p.edges
        {'a-b': Edge a-b, 'b-c': Edge b-c}

        """
        return self._path

    def summary(self) -> str:
        """Returns a summary of the path.

        The summary contains the name, the used path class, if it is directed
        or not, the number of unique nodes and unique edges, and the number of
        nodes in the path.

        Since a path can multiple times pass the same node and edge objects,
        the length of the path(i.e. the consecutive nodes) might be larger
        then the number of unique nodes.

        If logging is enabled(see config), the summary is written to the log
        file and showed as information on in the terminal. If logging is not
        enabled, the function will return a string with the information, which
        can be printed to the console.

        Returns
        -------
        str

        Return a summary of the path.

        """
        summary = [
            'Uid:\t\t\t{}\n'.format(self.uid),
            'Type:\t\t\t{}\n'.format(self.__class__.__name__),
            'Number of unique nodes:\t{}\n'.format(self.number_of_nodes()),
            'Number of unique edges:\t{}\n'.format(self.number_of_edges()),
            'Path length (# edges):\t{}'.format(len(self))
        ]
        return ''.join(summary)

    def number_of_nodes(self, unique: bool = True) -> int:
        """Return the number of nodes in the path.

        Parameters
        ----------
        unique: bool, optional(default=True)

        If unique is ``True`` only the number of unique nodes in the path
        is returnd.

        Returns
        -------
        int

        Returns the number of nodes in the path.

        Examples
        --------
        Generate a simple path.

        >> > from pathy import Path
        >> > p = Path('a', 'b', 'c', 'a', 'b',)

        Get the number of unique nodes:

        >> > p.number_of_nodes()
        3

        Get the number of all node visits in the path:

        >> > p.number_of_nodes(unique=False)
        5

        """
        if unique:
            non = len(set(self.nodes))
        else:
            non = len(self.nodes)
        return non

    def number_of_edges(self, unique: bool = True) -> int:
        """Return the number of edges in the path.

        Parameters
        ----------
        unique: bool, optional(default=True)

        If unique is ``True`` only the number of unique edges in the path
        is returnd.

        Returns
        -------
        int

        Returns the number of edges in the path.

        Examples
        --------
        Generate a simple path.

        >> > from pathy import Path
        >> > p = Path('a', 'b', 'c', 'a', 'b')

        Get the number of unique edges:

        >> > p.number_of_edges()
        3

        Get the number of all observed edges in the path:

        >> > p.number_of_nodes(unique=False)
        4

        """
        if unique:
            noe = len(set(self.edges))
        else:
            noe = len(self.edges)
        return noe


class PathSet(BaseCollection):
    """A set of paths"""

    def add(self, path: Path) -> None:
        """Add a node to the set of nodes."""
        # pylint: disable=unused-argument
        self._map[path.uid] = path

    def discard(self, path: Path) -> None:
        """Removes the specified item from the set."""
        self.pop(path.uid, None)

    def __getitem__(self, key: Union[int, str, Path]) -> Path:
        """Returns a node object."""
        path: Path
        if isinstance(key, Path) and key in self:
            path = key
        elif isinstance(key, (int, slice)):
            path = list(self._map.values())[key]
        else:
            path = self._map[key]
        return path

    def __setitem__(self, key: Any, value: Any) -> None:
        """set a object"""
        for path in self.values():
            path[key] = value


class PathCollection(BaseCollection):
    """A collection of paths"""
    # pylint: disable=too-many-instance-attributes

    # read_csv = pathpy.io.read_pathcollection_csv

    def __init__(self, directed: bool = True,
                 multiedges: bool = False,
                 multipaths: bool = False,
                 nodes: Optional[NodeCollection] = None,
                 edges: Optional[EdgeCollection] = None) -> None:
        """Initialize the network object."""
        # pylint: disable=too-many-arguments

        # initialize the base class
        super().__init__()

        # inidcator whether the network is directed or undirected
        self._directed: bool = directed

        # indicator whether the network has multi-edges
        self._multiedges: bool = multiedges

        # indicator whether the network has multi-edges
        self._multipaths: bool = multipaths

        # collection of nodes
        self._nodes: NodeCollection = NodeCollection()

        if nodes is not None:
            self._nodes = nodes
        elif nodes is None and edges is not None:
            self._nodes = edges.nodes

        # collection of edges
        self._edges: EdgeCollection = EdgeCollection(
            directed=directed,
            multiedges=multiedges,
            nodes=self._nodes
        )
        if edges is not None:
            self._edges = edges

        # map node tuples to paths
        self._nodes_map: defaultdict = defaultdict(PathSet)

        # map single node to paths
        self._node_map: defaultdict = defaultdict(set)

        # map edge tuples to paths
        self._edges_map: defaultdict = defaultdict(PathSet)

        # map single node to paths
        self._edge_map: defaultdict = defaultdict(set)

        # class of objects
        self._path_class: Any = Path

        self._added: set = set()
        self._removed: set = set()

    def __contains__(self, item) -> bool:
        """Returns if item is in path."""
        _contain: bool = False
        if isinstance(item, self._path_class) and item in self._map.values():
            _contain = True
        elif isinstance(item, str) and item in self._map:
            _contain = True
        elif isinstance(item, (tuple, list)):

            _contain_nodes: bool = False
            _contain_edges: bool = False
            try:
                if tuple(self.nodes[i].uid for i in item) in self._nodes_map:
                    _contain_nodes = _contain = True
            except KeyError:
                pass

            try:
                if (tuple(cast(Edge, self.edges[i]).uid for i in item)
                        in self._edges_map):
                    _contain_edges = _contain = True
            except KeyError:
                pass

            if _contain_nodes and _contain_edges:
                LOG.warning('Matching node sequence as well as '
                            'edge sequence was found!')
        return _contain

    def __getitem__(self, key: Union[str, tuple, Path]) -> Path:
        """Returns a node object."""
        path: Path
        if isinstance(key, (tuple, list)):

            try:
                paths = self._nodes_map[tuple(self.nodes[i].uid for i in key)]

            except KeyError:
                try:
                    paths = self._edges_map[
                        tuple(cast(Edge, self.edges[i]).uid for i in key)]
                except KeyError as edges_not_exist:
                    LOG.error('No path with the given sequence available!')
                    raise KeyError from edges_not_exist

            if self.multipaths:
                path = paths
            else:
                path = paths[-1]

        elif isinstance(key, self._path_class) and key in self:
            path = key
        else:
            path = self._map[key]
        return path

    def __lshift__(self, path: Path) -> None:
        """Quick assigment of a path"""
        self[path.uid] = path
        self._added.add(path)

    def __rshift__(self, path: Path) -> None:
        """Quick removal of an edge"""
        self.pop(path.uid, None)
        self._removed.add(path)

    @property
    def nodes(self) -> NodeCollection:
        """Return the associated nodes. """
        return self._nodes

    @property
    def edges(self) -> EdgeCollection:
        """Return the associated nodes. """
        return self._edges

    @property
    def directed(self) -> bool:
        """Return if edges are directed. """
        return self._directed

    @property
    def multiedges(self) -> bool:
        """Return if edges are directed. """
        return self._multiedges

    @property
    def multipaths(self) -> bool:
        """Return if edges are directed. """
        return self._multipaths

    @singledispatchmethod
    def add(self, *path, **kwargs: Any) -> None:
        """Add multiple paths."""
        raise NotImplementedError

    @add.register(Path)  # type: ignore
    def _(self, *path: Path, **kwargs: Any) -> None:

        # if checking is disabed add path directly to the collection
        if not kwargs.pop('checking', True):
            self._add(path[0], indexing=kwargs.pop('indexing', True))
            return

        # check if more then one path is given raise an AttributeError
        if len(path) != 1:
            for _path in path:
                self.add(_path)
            return

        # get path object
        _path = path[0]

        # update path attributes
        _path.update(**kwargs)

        # check if path already exists
        if _path not in self and _path.uid not in self.keys():

            # if path has len zero add single node
            if len(_path) == 0 and _path.start not in self.nodes:
                self.nodes.add(_path.start)

            # check if edges exists already
            for edge in _path.edges:
                if edge not in self.edges:
                    self.edges.add(edge)

            # add path to the paths
            self._add(_path)
        else:
            # raise error if path already exists
            self._if_exist(_path, **kwargs)

    @add.register(Edge)  # type: ignore
    def _(self, *path: Edge, **kwargs: Any) -> None:

        # get additional parameters
        uid: Optional[str] = kwargs.pop('uid', None)

        # check if all objects are edges
        if not all(isinstance(arg, (Edge, str)) for arg in path):
            LOG.error('All objects have to be Edge objects!')
            raise TypeError

        # generate edge list
        _edges: list = []

        # get edges
        for edge in path:
            if edge not in self.edges or self.multiedges:
                self.edges.add(edge, nodes=False)
            _edges.append(self.edges[edge])

        # create path based on single objects
        _path = _edges
        if _path not in self or self.multipaths:
            self.add(self._path_class(*_path, uid=uid, **kwargs))
        else:
            # raise error if path already exists
            self._if_exist(_path, **kwargs)

    @add.register(Node)  # type: ignore
    def _(self, *path: Node, **kwargs: Any) -> None:

        # get additional parameters
        uid: Optional[str] = kwargs.pop('uid', None)

        # check if all objects are nodes
        if not all(isinstance(arg, Node) for arg in path):
            LOG.error('All objects have to be Node objects!')
            raise TypeError

        # initialize temporal lists
        _nodes: list = []
        _edges: list = []
        _path: list = []

        # get nodes
        for node in path:
            if node not in self.nodes:
                self.nodes.add(node)
            _nodes.append(self.nodes[node])

        # get edges
        for edge in zip(_nodes[:-1], _nodes[1:]):
            if edge not in self.edges or self.multiedges:
                self.edges.add(edge)
            _edges.append(self.edges[edge])

        # create path based on single objects
        if len(_edges) == 0:
            _path.append(_nodes[0])
        else:
            _path = _edges

        if _path not in self or self.multipaths:
            self._add(self._path_class(*_path, uid=uid, **kwargs))
        else:
            # raise error if node already exists
            self._if_exist(_path, **kwargs)

    @add.register(str)  # type: ignore
    def _(self, *path: str, **kwargs: Any) -> None:

        # get additional parameters
        uid: Optional[str] = kwargs.pop('uid', None)
        nodes: bool = kwargs.pop('nodes', True)

        # check if all objects are str
        if not all(isinstance(arg, str) for arg in path):
            LOG.error('All objects have to be str objects!')
            raise TypeError

        _path = []
        if nodes:
            for node in path:
                if node not in self.nodes:
                    self.nodes.add(node)
                _path.append(self.nodes[node])

        else:
            for edge in path:
                if edge not in self.edges or self.multiedges:
                    if len(_path) > 0:
                        self.edges.add(_path[-1].w, Node(), uid=edge)
                    else:
                        self.edges.add(edge, nodes=False)
                _path.append(self.edges[edge])

        if _path not in self or self.multipaths:
            self.add(*_path, uid=uid, **kwargs)
        else:
            # raise error if path already exists
            self._if_exist(_path, **kwargs)

    @add.register(tuple)  # type: ignore
    @add.register(list)  # type: ignore
    def _(self, *path: Union[tuple, list], **kwargs: Any) -> None:
        for _path in path:
            self.add(*_path, **kwargs)

    def _add(self, path: Path, indexing: bool = True) -> None:
        """Add a node to the set of nodes."""
        # add path to the dict
        self[path.uid] = path

        # store new added path
        self._added.add(path)

        # update the index structure
        if indexing:
            self.update_index()

    def _if_exist(self, path: Any, **kwargs: Any) -> None:
        """Helper function if the path does already exsist."""
        # pylint: disable=no-self-use
        # pylint: disable=unused-argument
        LOG.error('The path "%s" already exists in the Network', path.uid)
        raise KeyError

    def update_index(self) -> None:
        """Update the index structure of the PathCollection."""
        for path in list(self._added):
            _nodes = tuple(_n.uid for _n in path.nodes)
            _edges = tuple(_e.uid for _e in path.edges)
            self._nodes_map[_nodes].add(path)
            self._edges_map[_edges].add(path)

            self._added.discard(path)

        for path in list(self._removed):

            _nodes = tuple(_n.uid for _n in path.nodes)
            _edges = tuple(_e.uid for _e in path.edges)
            self._nodes_map[_nodes].discard(path)
            self._edges_map[_edges].discard(path)

            if len(self._nodes_map[_nodes]) == 0:
                self._nodes_map.pop(_nodes, None)

            if len(self._edges_map[_edges]) == 0:
                self._edges_map.pop(_edges, None)

            self._removed.discard(path)

    @singledispatchmethod
    def remove(self, *edge, **kwargs: Any) -> None:
        """Remove path. """
        raise NotImplementedError

    @remove.register(Path)  # type: ignore
    def _(self, *path: Path, **kwargs: Any) -> None:
        # pylint: disable=unused-argument
        for _path in path:
            self._remove(_path)

    @remove.register(Edge)  # type: ignore
    def _(self, *path: Edge, **kwargs: Any) -> None:
        # pylint: disable=unused-argument
        self._remove(self[path])

    @remove.register(Node)  # type: ignore
    def _(self, *path: Node, **kwargs: Any) -> None:
        # pylint: disable=unused-argument
        self._remove(self[path])

    @remove.register(str)  # type: ignore
    def _(self, *path: str, **kwargs: Any) -> None:
        # pylint: disable=unused-argument
        if len(path) == 1:
            self._remove(self[path[0]])
        else:
            self._remove(self[path])

    @remove.register(tuple)  # type: ignore
    @remove.register(list)  # type: ignore
    def _(self, *path: Union[tuple, list], **kwargs: Any) -> None:
        for _path in path:
            self.remove(*_path, **kwargs)

    def _remove(self, path: Path, indexing: bool = True) -> None:
        """Remove a path from the path collection."""

        # remove edge from the dict
        self.pop(path.uid, None)

        # store removed path
        self._removed.add(path)

        # update the index structure
        if indexing:
            self.update_index()

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
