"""Node Class"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : node.py -- Base class for a node
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Mon 2021-05-03 15:41 juergen>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
from typing import Any, Optional, Union, cast

from singledispatchmethod import singledispatchmethod  # NOTE: not needed at 3.9

from pathpy import logger
from pathpy.core.classes import PathPyObject
from pathpy.core.path import BasePath, BasePathCollection

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


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
