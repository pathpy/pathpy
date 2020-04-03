#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_io_edgelist.py -- Test environment for input/output of edges
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Fri 2020-04-03 09:51 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
import pytest
import sqlite3
import pandas as pd
from pathpy import Network


def test_read_edgelist_from_csv():
    """Test to read edges from a file."""
    net = Network()
    net.read_edgelist('./data/tube.csv', separator=';')
    assert net.shape == (308, 370, 0)


def test_read_edgelist_from_sql():
    """Test to read edges from a sql database."""

    net = Network()
    net.read_edgelist('./data/networks.db', table='kde')
    assert net.shape == (1039, 1232, 0)


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
