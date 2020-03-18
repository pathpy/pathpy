#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : _check_node.py -- Helper function to check the node format
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Wed 2020-03-18 09:00 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any

from ... import logger
from .. import Node

# create a logger
log = logger(__name__)


def _check_node(self, node: Any, **kwargs: Any) -> Node:
    """Helper function to check if the node is in the right format."""

    # check if node is a Node object
    if isinstance(node, Node):
        _node = node

    # check if node is defined as string
    elif isinstance(node, str):

        # check if node is already recorded
        if node in self.nodes:
            _node = self.nodes[node]

        # otherwise generate new node object
        else:
            _node = Node(node, **kwargs)

    # raise error if not defined in the right format
    else:
        log.error('The definition of the node "{}" is incorrect!'
                  'Please use a Node object or a unique str!'.format(node))
        raise AttributeError

    # check if the node objet is already recorded
    if _node.uid in self.nodes:

        # check if nodes are different (e.g. have different attributes)
        if _node == self.nodes[_node.uid]:

            # if nodes are similar use the recorded node
            _node = self.nodes[_node.uid]

        else:

            # update existing node
            self.nodes[_node.uid].update(_node)

            # make a shallow copy of the updated node
            _node = self.nodes[_node.uid]

    # otherwise check if attributes have to be overwritten
    else:
        if kwargs and kwargs != _node.attributes.to_dict(history=False):
            _node.update(**kwargs)

    return _node


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
