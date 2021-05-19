"""Path class"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : network.py -- Base class for a path
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Wed 2021-05-19 10:15 juergen>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
from typing import Any, Optional, Union
from singledispatchmethod import singledispatchmethod  # NOTE: not needed at 3.9

from pathpy import logger
from pathpy.core.core import PathPyObject, PathPyTuple, PathPyPath, PathPyCollection

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

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the EdgeCollection object."""

        # initialize the base class
        super().__init__(*args, **kwargs)

        # indicator whether the network has multi-edges
        self._multiple: bool = kwargs.pop('multipaths', False)

        # class of objects
        self._default_class: Any = Path

    @property
    def multipaths(self) -> bool:
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

    @add.register(Path)  # type: ignore
    def _(self, *args: Path, **kwargs: Any) -> None:
        super().add(args[0], **kwargs)

    @add.register(int)  # type: ignore
    @add.register(str)  # type: ignore
    @add.register(PathPyObject)  # type: ignore
    def _(self, *args: Union[int, str, PathPyObject], **kwargs: Any) -> None:

        # get additional parameters
        uid: Optional[str] = kwargs.pop('uid', None)

        obj = self._default_class(
            *args, uid=uid, directed=self.directed, **kwargs)
        super().add(obj)

    @singledispatchmethod
    def remove(self, *args, **kwargs):
        """Remove objects"""
        super().remove(*args, **kwargs)

    @remove.register(Path)  # type: ignore
    def _(self, *args: Path, **kwargs: Any) -> None:
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
        elif args in self and self.multipaths:
            for obj in list(self[args]):
                super().remove(obj)
        elif args in self and not self.multipaths:
            super().remove(self[args])
        else:
            LOG.warning('No path was removed!')

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
