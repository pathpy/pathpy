"""Higher-order network class"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : higher_order_network.py -- Basic class for a HON
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Wed 2020-06-10 09:48 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================

from __future__ import annotations
from typing import Any, Optional

from pathpy import logger
from pathpy.core.network import Network

# create logger for the Network class
LOG = logger(__name__)


class HigherOrderNetwork(Network):
    """Base class for a Higher Order Network (HON)."""

    def __init__(self, uid: Optional[str] = None, order: int = 1,
                 **kwargs: Any) -> None:
        """Initialize the higer-order network object."""

        # initialize the base class
        super().__init__(uid=uid, directed=True, temporal=False,
                         multiedges=False, **kwargs)

        # order of the higher-order network
        self._order: int = order

    @property
    def order(self) -> int:
        """Return the order of the higher-order network."""
        return self._order

    def degrees_of_freedom(self, mode: str = 'path') -> int:
        """Returns the degrees of freedom of the higher-order network.

        Since probabilities must sum to one, the effective degree of freedom is
        one less than the number of nodes

        .. math::

           \\text{dof} = \\sum_{n \\in N} \\max(0,\\text{outdeg}(n)-1)

        """
        # initialize degree of freedom
        degrees_of_freedom: int = 0
        return degrees_of_freedom

    def summary(self) -> str:
        """Returns a summary of the higher-order network.

        The summary contains the name, the used network class, the order, the
        number of nodes and edges.

        If logging is enabled (see config), the summary is written to the log
        file and showed as information on in the terminal. If logging is not
        enabled, the function will return a string with the information, which
        can be printed to the console.

        Returns
        -------
        str
            Returns a summary of important higher-order network properties.

        """
        summary = [
            'Uid:\t\t\t{}\n'.format(self.uid),
            'Type:\t\t\t{}\n'.format(self.__class__.__name__),
            # 'Directed:\t\t{}\n'.format(str(self.directed)),
            # 'Multi-Edges:\t\t{}\n'.format(str(self.multiedges)),
            'Order:\t\t\t{}\n'.format(self.order),
            'Number of nodes:\t{}\n'.format(self.number_of_nodes()),
            'Number of edges:\t{}'.format(self.number_of_edges()),
        ]
        attr = self.attributes.to_dict()
        if len(attr) > 0:
            summary.append('\n\nNetwork attributes\n')
            summary.append('------------------\n')
        for k, v in attr.items():
            summary.append('{}:\t{}\n'.format(k, v))

        return ''.join(summary)


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
