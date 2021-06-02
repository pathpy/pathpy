"""Module for base classes in the models module."""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : classes.py -- Base classes for pathpy
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Tue 2021-06-01 13:38 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from pathpy.core.core import PathPyObject


class BaseModel(PathPyObject):
    """Base class for models."""


class BaseNetwork(BaseModel):
    """Base class for a network model."""


class BaseHyperGraph(BaseModel):
    """Base class for a hypergraph model."""


class BaseTemporalNetwork(BaseModel):
    """Base class for a temporal network model."""


class BaseHigherOrderNetwork(BaseModel):
    """Base class for a higher-order network model."""


class BaseMultiOrderModel(BaseModel):
    """Base class for a multi-order model."""

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
