"""Path class"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : network.py -- Base class for a path
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Wed 2021-05-05 17:37 juergen>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
from typing import Any, Optional, Union
from singledispatchmethod import singledispatchmethod  # NOTE: not needed at 3.9

from pathpy import logger
from pathpy.core.core import PathPyTuple, PathPyPath, PathPyCollection
from pathpy.core.node import Node, NodeCollection

# create logger for the Path class
LOG = logger(__name__)


class Path(PathPyPath):
    """Base class for a path."""

    def summary(self) -> str:
        """Returns a summary of the path. """
        summary = [
            'Uid:\t\t{}\n'.format(self.uid),
            'Type:\t\t{}\n'.format(self.__class__.__name__),
            'Directed:\t{}\n'.format(self.directed),
            'Nodes:\t\t{}\n'.format(self.relations),
        ]

        return ''.join(summary)

    @property
    def nodes(self) -> dict:
        """Return the nodes of the path."""
        return self.objects


class PathCollection(PathPyCollection):
    """A collection of edges"""
    # pylint: disable=too-many-ancestors

    def __init__(self, directed: bool = True,
                 multipaths: bool = False,
                 nodes: Optional[NodeCollection] = None) -> None:
        """Initialize the PathCollection object."""

        # initialize the base class
        super().__init__(directed=directed)

        # collection of nodes
        self._nodes: Any = NodeCollection()
        if nodes is not None:
            self._nodes = nodes

        # indicator whether the network has multi-edges
        self._multipaths: bool = multipaths

        # class of objects
        self._node_class: Any = Node
        self._path_class: Any = Path

    @singledispatchmethod
    def __getitem__(self, key):
        return super().__getitem__(key)

    @__getitem__.register(tuple)  # type: ignore
    def _(self, key):
        if any((isinstance(i, (self._node_class)) for i in key)):
            key = tuple(self.nodes[i].uid for i in key)

        path = super().__getitem__(key)
        if not self.multipaths and isinstance(path, set):
            path = next(iter(path))
        return path

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
    def multipaths(self) -> bool:
        """Return if edges are multiedges. """
        return self._multipaths

    @property
    def nodes(self) -> NodeCollection:
        """Return the associated nodes. """
        return self._nodes

    @singledispatchmethod
    def add(self, *path, **kwargs: Any) -> None:
        """Add multiple nodes. """
        raise NotImplementedError

    @add.register(Path)  # type: ignore
    def _(self, *path: Path, **kwargs: Any) -> None:

        if not kwargs.pop('checking', True):
            super().add(path[0], **kwargs)
            return

        _path = path[0]

        if _path.directed != self.directed:
            _text = {True: 'directed', False: 'undirected'}
            LOG.warning('A %s path was added to a %s path collection!',
                        _text[_path.directed], _text[self.directed])

        # check if node exists already
        for node in _path.nodes.values():
            if node not in self.nodes.values():
                self.nodes.add(node)

        # check if other edge exists between v and w
        if _path.relations not in self or self.multipaths:
            super().add(path[0], **kwargs)
        else:
            self._if_exist(_path, **kwargs)

    @add.register(str)  # type: ignore
    @add.register(Node)  # type: ignore
    def _(self, *path: Union[str, Node], **kwargs: Any) -> None:

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


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
