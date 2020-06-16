"""Higher-order network class"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : higher_order_network.py -- Basic class for a HON
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Wed 2020-06-10 14:56 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================

from __future__ import annotations
from typing import Any, Optional, Union

from pathpy import logger
from pathpy.core.node import Node
from pathpy.core.edge import Edge
from pathpy.core.path import Path
from pathpy.core.network import Network

# create logger for the Network class
LOG = logger(__name__)

"""Questions about HONs

How to deal with the 0-order start node?

How is the order of a node determined?
Can this be done on a node level or
must it be done on the network level?

How to get nodes and edges?

Forced uids like in pathpy2 ? a and b -> ('a,b')

Nodes
hon.nodes[abc] # hon-node object
hon.nodes['abc'] # hon-node uid
hon.nodes[a,b,c] # node objects
hon.nodes['a','b','c'] # node uids
hon.nodes[ab,bc] # edge objects
hon.nodes['a-b','b-c'] # edge uids

Edges
hon.edges[abcd] # hon-edge object
hon.edges['abcd'] # hon-edge uid
hon.edges[abc,bcd] # hon-node objects
hon.edges['abc','bcd'] # hon-node uids
hon.edges[('a','b','c'),('b','c','d')] # node uids
hon.edges[('a-b','b-c'),('b-c','c-d')] # edge uids
hon.edges['a','b','c','d'] # path node uids
hon.edges['a-b','b-c','c-d'] # path edge uids
hon.edges[a,b,c,d] # node objects
hon.edges[ab,bc,cd] # edge objects

Methods

How to implement:

estimator = estimator.fit(data, targets)
estimator = estimator.fit(data)

prediction = predictor.predict(data)
probability = predictor.predict_proba(data)

new_data = transformer.transform(data)
new_data = transformer.fit_transform(data)

score = model.score(data)



Model.from_samples(data)

"""


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


class HigherOrderNode(Node, Path):
    """Base class of a higher order node."""

    def __init__(self, *args: Union[Node, Edge], uid: Optional[str] = None,
                 **kwargs: Any) -> None:

        # initializing the parent classes
        Node.__init__(self, uid, **kwargs)
        Path.__init__(self, *args, uid=uid, **kwargs)

    @property
    def order(self) -> int:
        """Returns the order of the higher-order node."""
        return self.number_of_nodes(unique=False)

    def summary(self) -> str:
        """Returns a summary of the higher-order node.

        The summary contains the name, the used node class, the order, the
        number of nodes and the number of edges.

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
            'Order:\t\t\t{}\n'.format(self.order),
            'Number of unique nodes:\t{}\n'.format(self.number_of_nodes()),
            'Number of unique edges:\t{}'.format(self.number_of_edges()),
        ]
        return ''.join(summary)


class HigherOrderEdge(Edge):
    """Base class of a higher order edge."""

    def __init__(self, v: HigherOrderNode, w: HigherOrderNode,
                 uid: Optional[str] = None, **kwargs: Any) -> None:
        # initializing the parent classes
        super().__init__(v=v, w=w, uid=uid, **kwargs)


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
