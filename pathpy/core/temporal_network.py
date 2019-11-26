#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : temporal_network.py • core -- Base class for a temporal network
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Tue 2019-11-26 09:30 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any

from .. import logger, config
from .base import BaseTemporalNetwork
from . import Node, Edge, Path, Network

# create logger for the Network class
log = logger(__name__)


class TemporalNetwork(BaseTemporalNetwork, Network):
    """Base class for a temporal network."""

    def __init__(self, **kwargs: Any) -> None:

        # initialize the base class
        super().__init__(directed=True, **kwargs)


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
