#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : _check_edge.py -- Helper function to check the edge format
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2019-10-31 14:15 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, Optional

from ... import logger
from .. import Edge
from ._check_node import _check_node

# create a logger
log = logger(__name__)


def _check_edge(self, edge: Any, *args: Any, **kwargs: Any) -> Edge:
    """Helper function to check if the edge is in the right format."""

    _e: dict = {'uid': None, 'object': None}
    _v: dict = {'uid': None, 'object': None}
    _w: dict = {'uid': None, 'object': None}

    # check if edge is an Edge object
    if isinstance(edge, self.EdgeClass):

        _e['uid'] = edge.uid
        _e['object'] = edge

    # check if edge is a single string
    elif isinstance(edge, str) and not args:

        try:
            v_uid, w_uid = edge.split(self.separator['edge'])
            _v['uid'] = v_uid
            _w['uid'] = w_uid
        except Exception:
            log.error('The definition of the edge "{}" is incorrect! '
                      'Please use an Edge object!'.format(edge))
            raise AttributeError

    # check if node objects are given
    elif (isinstance(edge, self.NodeClass) and
          isinstance(args[0], self.NodeClass)):

        try:
            _e['uid'] = args[1]
        except Exception:
            pass

        _v['uid'] = edge.uid
        _v['object'] = edge
        _w['uid'] = args[0].uid
        _w['object'] = args[0]

    # check if edge is definde buy strings
    elif (isinstance(edge, str) and
          isinstance(args[0], str)):

        try:
            _e['uid'] = args[1]
        except Exception:
            pass

        _v['uid'] = edge
        _w['uid'] = args[0]

    # raise error if nothing works.
    else:
        log.error('The definition of the edge "{}" is incorrect! '
                  'Please use an Edge object!'.format(edge))
        raise AttributeError

    # check nodes and generate virtual edge
    if _e['object']:
        v = _check_node(self, _e['object'].v)
        w = _check_node(self, _e['object'].w)
        _edge = _e['object']
        _edge.nodes.update({v.uid: v, w.uid: w})

    elif _v['object'] and _w['object']:
        v = _check_node(self, _v['object'])
        w = _check_node(self, _w['object'])

        _edge = self.EdgeClass(v, w, uid=_e['uid'], **kwargs)

    elif _v['uid'] and _w['uid']:
        v = _check_node(self, _v['uid'])
        w = _check_node(self, _w['uid'])
        _edge = self.EdgeClass(v, w, uid=_e['uid'], **kwargs)

    else:
        log.error('The definition of the edge "{}" is incorrect! '
                  'Please use an Edge object!'.format(edge))
        raise AttributeError

    # check if the edge objet is already recorded
    if _edge.uid in self.edges:

        # check if edges are different (e.g. have different attributes)
        if _edge == self.edges[_edge.uid]:

            # if edges are similar use the recorded edge
            _edge = self.edges[_edge.uid]

        else:

            # otherwise get previous edge properties and add the new ones
            _copy = self.edges[_edge.uid].copy()
            _copy.inherit(_edge)
            _edge = _copy

    # otherwise check if attributes have to be overwritten
    else:
        if kwargs and kwargs != _edge.attributes.to_dict(history=False):
            _edge.update(**kwargs)

    return _edge


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
