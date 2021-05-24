"""HyperEdge class"""
#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : hyperedge.py -- Base class for a hyperedge
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Mon 2021-05-24 11:03 juergen>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================

from typing import Any, Optional, Union

from singledispatchmethod import singledispatchmethod  # NOTE: not needed at 3.9

from pathpy import logger
from pathpy.core.core import PathPyObject, PathPyPath, PathPyCollection

# create logger for the Path class
LOG = logger(__name__)


class HyperEdge(PathPyPath):
    """Base class for a hyperedge.  """

    def __init__(self, *nodes: Union[str, PathPyObject],
                 uid: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize the node object."""
        _ = kwargs.pop('directed', None)
        _ = kwargs.pop('ordered', None)
        # initialize the parent class
        super().__init__(*nodes, uid=uid, directed=False, ordered=False, **kwargs)

    @property
    def nodes(self) -> dict:
        """Return the nodes of the edge."""
        return self.objects

    def summary(self) -> str:
        """Returns a summary of the edge. """
        summary = [
            'Uid:\t\t{}\n'.format(self.uid),
            'Type:\t\t{}\n'.format(self.__class__.__name__),
            'Nodes:\t\t{}\n'.format(self.relations),
        ]

        return ''.join(summary)


class HyperEdgeCollection(PathPyCollection):
    """A collection of edges"""
    # pylint: disable=too-many-ancestors

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the EdgeCollection object."""

        # initialize the base class
        super().__init__(*args, directed=False, ordered=False, **kwargs)

        # indicator whether the network has multi-edges
        self._multiple: bool = kwargs.pop('multiedges', False)

        # class of objects
        self._default_class: Any = HyperEdge

    @property
    def multiedges(self) -> bool:
        """Return if edges are multiedges. """
        return self._multiple

    @singledispatchmethod
    def add(self, *args, **kwargs: Any) -> None:
        """Add multiple nodes. """
        raise NotImplementedError

    @add.register(HyperEdge)  # type: ignore
    def _(self, *args: HyperEdge, **kwargs: Any) -> None:
        super().add(args[0], **kwargs)

    @add.register(str)  # type: ignore
    @add.register(int)  # type: ignore
    @add.register(PathPyObject)  # type: ignore
    def _(self, *args: Union[int, str, PathPyObject], **kwargs: Any) -> None:

        # get additional parameters
        uid: Optional[str] = kwargs.pop('uid', None)

        obj = self._default_class(
            *args, uid=uid, directed=self.directed, **kwargs)
        super().add(obj, **kwargs)

    @add.register(tuple)  # type: ignore
    @add.register(list)  # type: ignore
    def _(self, *args: Union[tuple, list], **kwargs: Any) -> None:
        for arg in args:
            self.add(*arg, **kwargs)

    @singledispatchmethod
    def remove(self, *args, **kwargs):
        """Remove objects"""
        super().remove(*args, **kwargs)

    @remove.register(HyperEdge)  # type: ignore
    def _(self, *args: HyperEdge, **kwargs: Any) -> None:
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
        elif args in self and self.multiedges:
            for obj in list(self[args]):
                super().remove(obj)
        elif args in self and not self.multiedges:
            super().remove(self[args])
        else:
            LOG.warning('No hyperedge was removed!')

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
