"""Methods to calculate edge reciprocity"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : clustering.py -- Module to calculate edge reciprocity
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Sun 2021-05-02 03:09 ingo>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import TYPE_CHECKING, Set

from pathpy.core.api import Node, Edge
from pathpy.models.api import Network

def edge_reciprocity(network: Network) -> float:
    """
    """

    if network.directed == False:
        return 1.0 
    else:
        reciproc = 0
        for e in network.edges:
            if (e.w, e.v) in network.edges:
                reciproc += 1.0
        return reciproc / network.number_of_edges()
