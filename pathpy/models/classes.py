"""Module for base classes in the models module."""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : classes.py -- Base classes for pathpy
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Wed 2021-04-21 09:11 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from pathpy.core.classes import BaseClass


class BaseModel(BaseClass):
    """Base class for models."""


class BaseNetwork(BaseModel):
    """Base class for a network model."""


class BaseTemporalNetwork(BaseModel):
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
