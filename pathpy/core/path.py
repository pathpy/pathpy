"""Path class"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : path.py -- Base class for a path
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Tue 2021-06-01 18:44 juergen>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
from typing import Any, Optional, Union
from singledispatchmethod import singledispatchmethod  # NOTE: not needed at 3.9

from pathpy import logger
from pathpy.core.core import PathPyObject, PathPyPath, PathPyCollection

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
            'Nodes:\t\t{}\n'.format(self.nodes),
            'Relations:\t{}\n'.format(self.relations),
        ]

        return ''.join(summary)

    @property
    def nodes(self) -> dict:
        """Return the nodes of the path."""
        return self.objects

    def subpaths(self, min_length: int = 0, max_length: int = None,
                 include_self: bool = False, paths: bool = True) -> list:
        """A list with all possible subpaths"""

        # get min and max length
        min_length = max(min_length, 0)
        max_length = min(len(self), max(max_length, 0)) if (
            max_length is not None) else len(self)

        relations: list = []

        # get subpaths
        for i in range(min_length, max_length+1):

            # do not include self if not given
            if i == len(self) and not include_self:
                break
            for j in range(len(self)-i+1):
                relations.append(self.relations[j:j+i+1])

        return [Path(*[self.objects[key] for key in obj],
                     directed=self.directed,
                     **self.attributes) for obj in relations] if paths else relations


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

    @singledispatchmethod
    def add(self, *args, **kwargs: Any) -> None:
        """Add multiple nodes. """
        raise NotImplementedError

    @add.register(Path)  # type: ignore
    def _(self, *args: Path, **kwargs: Any) -> None:
        super().add(*args, **kwargs)

    @add.register(int)  # type: ignore
    @add.register(str)  # type: ignore
    @add.register(PathPyObject)  # type: ignore
    def _(self, *args: Union[int, str, PathPyObject], **kwargs: Any) -> None:

        # get additional parameters
        uid: Optional[str] = kwargs.pop('uid', None)
        count: int = kwargs.pop('count', 1)
        obj = self._default_class(
            *args, uid=uid, directed=self.directed, **kwargs)

        super().add(obj, count=count, **kwargs)

    @add.register(type(None))  # type: ignore
    def _(self, *args: None, **kwargs: Any) -> None:

        # get additional parameters
        uid: Optional[str] = kwargs.pop('uid', None)
        count: int = kwargs.pop('count', 1)

        obj = self._default_class(
            uid, uid=uid, directed=self.directed, **kwargs)
        super().add(obj, count=count, **kwargs)

    @add.register(tuple)  # type: ignore
    @add.register(list)  # type: ignore
    def _(self, *args: Union[tuple, list], **kwargs: Any) -> None:
        for arg in args:
            self.add(*arg, **kwargs)

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
