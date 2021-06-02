#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_generators.py -- Test random graph generation
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Sat 2021-05-29 02:22 ingos>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================

import pytest

import pathpy as pp
import numpy as np


def test_Molloy_Reed():
    """Test the degree sequence of a network."""
    n = pp.generators.Molloy_Reed([2]*500)

    assert n.number_of_nodes() == 500
    assert set(n.degrees().values()) == set([2])

def test_ER_np():
    """Test Erdös-Renyi Model."""
    n = pp.generators.ER_np(n=500, p=0.002)

    assert n.number_of_nodes() == 500
    assert pytest.approx(pp.statistics.mean_degree(n), 0.1) == 1


def test_ER_nm():
    """Test Erdös-Renyi Model."""
    n = pp.generators.ER_nm(n=100, m=200)

    assert n.number_of_nodes() == 100
    assert n.number_of_edges() == 200


def test_k_regular():
    """Test k-regular network."""
    n = pp.generators.k_regular_random(k=2, n=100)

    assert n.number_of_nodes() == 100
    assert set(n.degrees().values()) == set([2])
    
def test_lattice():
    """Test lattice construction"""
    n = pp.generators.lattice_network(start=0, stop=10, dims=2)

    assert n.number_of_nodes() == 100
    assert set(n.degrees().values()) == set([2, 3, 4])


def test_Watts_Strogatz():
    """Test lattice construction"""
    n = pp.generators.Watts_Strogatz(n=100, s=3, p=0)

    assert n.number_of_nodes() == 100
    assert n.number_of_edges() == 300
    assert set(n.degrees().values()) == set([6])

    n = pp.generators.Watts_Strogatz(n=100, s=1, p=0)

    assert n.number_of_nodes() == 100
    assert n.number_of_edges() == 100
    assert set(n.degrees().values()) == set([2])

    n = pp.generators.Watts_Strogatz(n=100, s=2, p=0.1)

    assert n.number_of_nodes() == 100
    assert n.number_of_edges() == 200


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
