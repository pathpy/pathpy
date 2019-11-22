#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : _check_path.py -- Helper function to check the path format
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Fri 2019-11-22 12:20 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any

from ... import logger
from .. import Path
from ._check_node import _check_node
from ._check_edge import _check_edge
from ._check_str import _check_str

# create a logger
log = logger(__name__)


def _check_path(self, path: Any, *args: Any, **kwargs: Any) -> Path:
    """Helper function to check if the edge is in the right format."""

    _p = None
    _e: dict = {'uids': [], 'objects': []}
    _n: dict = {'uids': [], 'objects': []}

    # check if path is a Path object
    if isinstance(path, self.PathClass):
        _p = path

    # check if edge objects are given
    elif (isinstance(path, self.EdgeClass) and
          all([isinstance(x, self.EdgeClass) for x in args])):
        _e['uids'] = [path.uid] + [e.uid for e in args]
        _e['objects'] = [path] + [e for e in args]

    # check if node objects are given
    elif (isinstance(path, self.NodeClass) and
          all([isinstance(x, self.NodeClass) for x in args])):
        _n['uids'] = [path.uid] + [n.uid for n in args]
        _n['objects'] = [path] + [n for n in args]

    # check if path is definde by strings
    elif (isinstance(path, str) and
          all([isinstance(x, str) for x in args])):
        strings = [path] + [s for s in args]

        # convert strings to possible objects
        objects = _check_str(self, *strings, expected='edge')

        # check if all the strings are the same objects
        if len({x[1] for x in objects}) != 1:
            log.error('Path objects have to be from the same type!')
            raise AttributeError

        # get list of uids
        for uid, mode in objects:
            if mode == 'edge':
                _e['uids'].extend(uid)
            elif mode == 'node':
                _n['uids'].extend(uid)

    # raise error if nothing works.
    else:
        log.error('The definition of the path "{}" is incorrect! '
                  'Please use an Path object!'.format(path))
        raise AttributeError

    # generate virtual path

    # check given path
    if _p is not None:
        e = {k: _check_edge(self, v) for k, v in _p.edges.items()}
        n = {k: _check_node(self, v) for k, v in _p.nodes.items()}
        _path = _p
        _path.edges.update(e)
        _path.nodes.update(n)

    elif _e['objects']:
        e = [_check_edge(self, v) for v in _e['objects']]
        _path = self.PathClass(*e, **kwargs)

    elif _e['uids']:
        e = [_check_edge(self, v) for v in _e['uids']]
        _path = self.PathClass(*e, **kwargs)

    elif _n['objects']:
        n = [_check_node(self, v) for v in _n['objects']]
        _path = self.PathClass(*n, **kwargs)

    elif _n['uids']:
        n = [_check_node(self, v) for v in _n['uids']]
        _path = self.PathClass(*n, **kwargs)

    else:
        log.error('The definition of the path "{}" is incorrect! '
                  'Please use an Path object!'.format(path))
        raise AttributeError

    # check if the path objet is already recorded
    if _path.uid in self.paths:

        # check if paths are different (e.g. have different attributes)
        if _path == self.paths[_path.uid]:

            # if paths are similar use the recorded path
            _path = self.paths[_path.uid]

        else:

            # update existing path
            self.paths[_path.uid].update(_path)

            # make a shallow copy of the updated path
            _path = self.paths[_path.uid]

    # otherwise check if attributes have to be overwritten
    else:
        if kwargs and kwargs != _path.attributes.to_dict(history=False):
            _path.update(**kwargs)

    return _path

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
