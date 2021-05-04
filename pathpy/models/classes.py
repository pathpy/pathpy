"""Module for base classes in the models module."""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : classes.py -- Base classes for pathpy
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Tue 2021-05-04 12:26 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from pathpy.core.core import PathPyObject


class BaseModel(PathPyObject):
    """Base class for models."""


class BaseNetwork(PathPyObject):
    """Base class for a network model."""


class BaseTemporalNetwork(PathPyObject):
    """Base class for a temporal network model."""

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
