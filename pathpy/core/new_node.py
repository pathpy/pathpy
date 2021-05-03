"""Node Class"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : node.py -- Base class for a node
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Mon 2021-05-03 17:36 juergen>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
from typing import Any, Optional, Union

from singledispatchmethod import singledispatchmethod  # NOTE: not needed at 3.9

from pathpy import logger
from pathpy.core.core import PathPyObject, BasePath, BasePathCollection

# create logger for the Path class
LOG = logger(__name__)


class Node(BasePath):
    """Base class for a node."""

    def __init__(self, *n: Union[str, PathPyObject],
                 uid: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize the node object."""

        # Node Assumption:
        # ----------------
        # If only one string argument is given and no uid is defined
        # use the string argument as uid
        uid = n[0] if n and isinstance(n[0], str) and uid is None else uid

        # initialize the parent class
        super().__init__(*n, uid=uid, **kwargs)


class NodeCollection(BasePathCollection):
    """A collection of nodes"""
    # pylint: disable=too-many-ancestors

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the NodeCollection object."""

        # initialize the base class
        super().__init__(*args, **kwargs)

        # class of objects
        self._node_class: Any = Node

    @singledispatchmethod
    def add(self, *node, **kwargs: Any) -> None:
        """Add multiple nodes. """
        raise NotImplementedError

    @add.register(Node)  # type: ignore
    def _(self, *node: Node, **kwargs: Any) -> None:
        super().add(node[0], **kwargs)

    @add.register(str)  # type: ignore
    def _(self, *node: Node, **kwargs: Any) -> None:

        # get node uid
        _uid: str = str(node[0])

        # check if node with given uid str exists already
        if _uid not in self:
            # if not add new node with provided uid str
            super().add(self._node_class(_uid, uid=_uid, **kwargs))
        else:
            # raise error if node already exists
            super()._if_exist(_uid, **kwargs)

    @add.register(int)  # type: ignore
    def _(self, *node: int, **kwargs: Any) -> None:
        self.add(str(node[0]), **kwargs)

    @add.register(tuple)  # type: ignore
    @add.register(list)  # type: ignore
    def _(self, *node: tuple, **kwargs: Any) -> None:
        for _n in node[0]:
            self.add(_n, **kwargs)

    @singledispatchmethod
    def remove(self, *node, **kwargs):
        """Remove objects"""
        super().remove(*node, **kwargs)

    @remove.register(tuple)  # type: ignore
    @remove.register(list)  # type: ignore
    def _(self, *node: tuple, **kwargs: Any) -> None:
        for _n in node[0]:
            self.remove(_n, **kwargs)

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
