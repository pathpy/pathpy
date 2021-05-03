"""Path class"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : network.py -- Base class for a path
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Mon 2021-05-03 15:36 juergen>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, Optional, Union, cast
from collections import defaultdict
from collections.abc import MutableMapping

from singledispatchmethod import singledispatchmethod  # NOTE: not needed at 3.9

from pathpy import logger
from pathpy.core.classes import PathPyObject, PathPyCollection

# create logger for the Path class
LOG = logger(__name__)


class PathTuple(tuple):
    """Class to store directed and undirected relationships of path components."""
    def __new__(cls, args, **kwargs):
        """Create a new PathTuple object."""
        # pylint: disable=unused-argument
        return super(PathTuple, cls).__new__(cls, args)

    def __init__(self, _, directed=False):
        """ Initialize the new tuple class."""
        # pylint: disable=super-init-not-called
        # self._reversed = self[::-1]
        self.directed = directed

    def __hash__(self):
        return super().__hash__() if self.directed else super().__hash__() \
            + hash(self[::-1])

    def __eq__(self, other):
        return super().__eq__(other) if self.directed else super().__eq__(other) \
            or self[::-1] == other

    def __repr__(self):
        return super().__repr__() if self.directed else '|'+super().__repr__()[1:-1]+'|'


class BasePath(PathPyObject):
    """Base class for a path."""

    def __init__(self, *args: Union[str, PathPyObject],
                 uid: Optional[str] = None,
                 directed: bool = True,
                 **kwargs: Any) -> None:
        """Initialize the path object."""

        # initialize the parent class
        super().__init__(uid=uid, **kwargs)

        # variable to indicate if path is directed or not
        self._directed: bool = directed

        # a storage containing structure of the objects
        self._relations: PathTuple

        # map to the associated objects
        self._objects: dict = dict()

        # if checking is disabled create path directly from args of str
        if not kwargs.pop('checking', True):
            self._relations = PathTuple(args, directed=directed)
            self._objects = {uid: None for uid in args}
            return

        # helper variable for path assignment
        _uids = []

        # iterate over args and create structure and map
        for arg in args:
            # check if arg is a str (i.e. an uid)
            if isinstance(arg, str):
                _uid = arg
                _obj = None

            # check if arg is already a pathpy opject
            elif isinstance(arg, PathPyObject):
                _uid = arg.uid
                _obj = arg

            # if not applicable raise an error
            else:
                LOG.error('All objects must be str or PathPyObject s!')
                raise TypeError

            # temporal storage of the uids
            _uids.append(_uid)

            # create object mapping
            if _uid not in self._objects and _uid != self.uid:
                self._objects[_uid] = _obj

            # if arg uid and self.uid is equal make a self reference
            elif _uid not in self._objects and _uid == self.uid:
                self._objects[_uid] = self

        # save relationships
        self._relations = PathTuple(_uids, directed=directed)

    def __len__(self) -> int:
        """Lenght of the object."""
        return len(self.relations) - 1 if self.relations else 0

    def __str__(self) -> str:
        """Print a summary of the object. """
        return self.summary()

    def __contains__(self, item) -> bool:
        """Returns if suppath is in path"""
        return NotImplementedError

    @property
    def objects(self) -> dict:
        """Return the associated objects. """
        return self._objects

    @property
    def relations(self) -> PathTuple:
        """Return the associated relations of the path. """
        return self._relations

    @property
    def depth(self) -> int:
        """Depth of the object."""
        return self.max_depth(self)

    @property
    def directed(self) -> bool:
        """Returns if the object is directed or not."""
        return self._directed

    @directed.setter
    def directed(self, directed: bool) -> None:
        """Set the direction of the path"""
        self._directed = directed
        self._relations.directed = directed

    @staticmethod
    def max_depth(item) -> int:
        """Calculate the max depth of the object."""
        # Filter valid objects
        objects = _get_valid_objects(item)
        # if no valid objects are given return 1
        if not objects:
            return 1
        # recursive function  to get the depth
        return 1 + max(BasePath.max_depth(child) for child in objects)

    def subobjects(self, depth=None) -> list:
        """Returns the sub objects at a certain depth."""
        objects = _get_valid_objects(self)
        result = [[self.relations]]
        queue = objects

        while queue:
            result.append([node.nodes for node in queue])
            if len(result) == depth and depth:
                break

            level = []
            for node in queue:
                level.extend(_get_valid_objects(node))

            queue = level

        if depth:
            if depth <= len(result):
                result = result[depth-1]
            else:
                result = []
        return result

    def summary(self) -> str:
        """Returns a summary of the object. """

        summary = [
            'Uid:\t\t{}\n'.format(self.uid),
            'Type:\t\t{}\n'.format(self.__class__.__name__),
        ]

        return ''.join(summary)


class BasePathCollection(PathPyCollection):
    """Base collection for BasePathObjects"""

    def __init__(self, *args, **kwargs):
        """Initialize the BasePathCollection object."""

        # dict to store child objects {child.uid:child.PathPyObject}
        self._objects: dict = dict()

        # mapping between the child and the parten {child.uid: {parten.uids}}
        self._mapping: defaultdict = defaultdict(set)

        # enable indexing of the structures
        self._indexed: bool = kwargs.pop('indexed', True)

        # inidcator whether the network is directed or undirected
        self._directed: bool = kwargs.pop('directed', True)

        # dict to store the relationships between objects
        # IMPORTANT key has to be hashable
        # i.e. if the structure changes the mapping has to be updated
        self._relations: defaultdict = defaultdict(set)

        # initialize the base class
        super().__init__(*args, **kwargs)

    @singledispatchmethod
    def __getitem__(self, key):
        return super().__getitem__(key)

    @__getitem__.register(tuple)  # type: ignore
    def _(self, key):
        return {self._store[uid] for uid in self._relations[PathTuple(key, directed=self.directed)]}

    @singledispatchmethod
    def __contains__(self, item) -> bool:
        """Returns if item is in edges."""
        return super().__contains__(item)

    @__contains__.register(tuple)  # type: ignore
    def _(self, item: tuple) -> bool:
        return PathTuple(item, directed=self.directed) in self._relations

    @property
    def directed(self) -> bool:
        """Return if the collection is directed. """
        return self._directed

    def _add(self, obj: BasePath) -> None:
        """Add an edge to the set of edges."""
        super()._add(obj)
        self._objects.update(obj.objects)

        for uid in obj.objects:
            self._mapping[uid].add(obj.uid)

        if self._indexed:
            self._relations[obj.relations].add(obj.uid)

    @singledispatchmethod
    def remove(self, *args, **kwargs):
        """Remove objects"""
        super().remove(*args, **kwargs)

    @remove.register(str)  # type: ignore
    def _(self, *args: str, **kwargs: Any):
        """Remove object from the collection"""
        for uid in args:
            if uid in self.keys():
                self._remove(self[uid], **kwargs)

    def _remove(self, obj: BasePath) -> None:
        """Add an edge to the set of edges."""
        super()._remove(obj)

        for uid in obj.objects:
            self._mapping[uid].discard(obj.uid)
            if len(self._mapping[uid]) == 0:
                self._mapping.pop(uid, None)
                self._objects.pop(uid, None)

        if self._indexed:
            self._relations[obj.relations].discard(obj.uid)
            if len(self._relations[obj.relations]) == 0:
                self._relations.pop(obj.relations, None)


def _get_valid_objects(item) -> list:
    """Helper function to return a list with valid objects"""
    return [obj for obj in item.objects.values()
            if (isinstance(obj, BasePath) and obj.uid != item.uid)]


class Path(BasePath):
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


class PathCollection(BasePathCollection):
    """A collection of edges"""


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
