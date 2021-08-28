#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_konect.py -- Test functions to read konect networks
# Author    : Ingo Scholtes <ingo.scholtes@uni-wuerzburg.de>
# Time-stamp: <Sat 2021-08-28 23:51>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================

import pytest
import pathpy as pp


def test_karate_club():

    network = pp.io.konect.read_konect_name('ucidata-zachary')

    assert network.number_of_nodes() == 34
    assert network.number_of_edges() == 78