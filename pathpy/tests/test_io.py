#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_io.py -- Test environment for input/output files
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Sat 2020-08-22 18:12 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================

import pytest
from pathpy import Network,  TemporalNetwork
import pathpy as pp


def test_sql_read_network():
    """Read a static network from a sql database."""
    net = pp.io.sql.read_network(filename='./data/networks.db',
                                 table='gentoo', directed=True, multiedges=False)

    assert isinstance(net, Network)
    assert net.number_of_nodes() == 403
    assert net.number_of_edges() == 513


def test_sql_read_temporal_network():
    """Read a temporal network from a sql database."""
    net = pp.io.sql.read_temporal_network(filename='./data/networks.db',
                                          table='lotr',
                                          directed=True,
                                          multiedges=False)

    assert isinstance(net, TemporalNetwork)
    assert net.number_of_nodes() == 139
    assert net.number_of_edges() == 701


def test_sql_write_network():
    """Write network to sql database."""
    net = Network()
    net.add_edges(('a', 'b'), ('a', 'c'))
    pp.io.sql.write(net, filename='./data/network.db',
                    table='test', if_exists='replace')

    net = pp.io.sql.read_network(filename='./data/network.db', table='test')

    assert isinstance(net, Network)
    assert net.number_of_nodes() == 3
    assert net.number_of_edges() == 2


def test_csv_write_network():
    """Write network to csv."""
    net = Network()
    net.add_edges(('a', 'b'), ('a', 'c'))
    pp.io.csv.write(net, './data/network.csv')


def test_csv_read_network():
    """Read network from csv."""
    net = pp.io.csv.read_network('./data/network.csv')

    assert isinstance(net, Network)
    assert net.number_of_nodes() == 3
    assert net.number_of_edges() == 2

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
