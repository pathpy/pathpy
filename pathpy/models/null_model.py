""" Null Model class """
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : null_models.py -- Null models for pathpy
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Fri 2021-05-28 14:56 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from typing import Optional, Any
from singledispatchmethod import singledispatchmethod

from pathpy import logger  # , tqdm
from pathpy.models.higher_order_network import HigherOrderNetwork
from pathpy.core.path import PathCollection
# from pathpy.core.node import NodeCollection
# from pathpy.core.edge import EdgeCollection
# from pathpy.models.network import Network

# from pathpy.statistics.subpaths import SubPathCollection

# create logger
LOG = logger(__name__)


class NullModel(HigherOrderNetwork):
    """A null model for higher order networks."""

    def __init__(self, uid: Optional[str] = None, order: int = 2,
                 **kwargs: Any) -> None:
        """Initialize the null model"""

        # initialize the base class
        super().__init__(uid=uid, order=order, **kwargs)

    @singledispatchmethod
    def fit(self, data, order: Optional[int] = None,
            subpaths: bool = True) -> None:
        """Fit data to a HigherOrderNetwork"""
        raise NotImplementedError

    @fit.register(PathCollection)  # type: ignore
    def _(self, data: PathCollection, order: Optional[int] = None,
          subpaths: bool = True) -> None:

        # Check order
        if order is not None:
            self._order = order

    @classmethod
    def from_paths(cls, paths: PathCollection, **kwargs: Any):
        """Create higher oder network from paths."""

        order: int = kwargs.get('order', 2)

        null = cls(order=order)
        null.fit(paths)

        return null


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
