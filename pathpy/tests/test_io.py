#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_io.py -- Test environment for input/output files
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Sat 2020-08-22 18:43 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================

import pytest
from pathpy import Network, TemporalNetwork
import pathpy as pp


# def test_sql_read_network():
#     """Read a static network from a sql database."""
#     net = pp.io.sql.read_network(filename='networks.db',
#                                  table='gentoo', directed=True, multiedges=False)

#     assert isinstance(net, Network)
#     assert net.number_of_nodes() == 403
#     assert net.number_of_edges() == 513


# def test_sql_read_temporal_network():
#     """Read a temporal network from a sql database."""
#     net = pp.io.sql.read_temporal_network(filename='networks.db',
#                                           table='lotr',
#                                           directed=True,
#                                           multiedges=False)

#     assert isinstance(net, TemporalNetwork)
#     assert net.number_of_nodes() == 139
#     assert net.number_of_edges() == 701


def test_sql_write_network():
    """Write network to sql database."""
    net = Network()
    net.add_edges(('a', 'b'), ('a', 'c'))
    pp.io.sql.write(net, filename='network.db',
                    table='test', if_exists='replace')

    net = pp.io.sql.read_network(db_file='network.db', table='test')

    assert isinstance(net, Network)
    assert net.number_of_nodes() == 3
    assert net.number_of_edges() == 2


def test_csv_write_network():
    """Write network to csv."""
    net = Network()
    net.add_edges(('a', 'b'), ('a', 'c'))
    pp.io.csv.write(net, 'network.csv')


def test_csv_read_network():
    """Read network from csv."""
    net = pp.io.csv.read_network('network.csv')

    assert isinstance(net, Network)
    assert net.number_of_nodes() == 3
    assert net.number_of_edges() == 2


def test_pandas_temporal():
    """Read network from csv."""
    tn = TemporalNetwork(directed=True)
    tn.add_edge('a', 'b', timestamp=1)
    tn.add_edge('b', 'a', timestamp=3)
    tn.add_edge('b', 'c', timestamp=3)
    tn.add_edge('d', 'c', timestamp=4)
    tn.add_edge('c', 'd', timestamp=5)
    tn.add_edge('c', 'b', timestamp=6)
    tn.add_edge('a', 'b', timestamp=7)
    tn.add_edge('b', 'a', timestamp=8)

    df = pp.io.pandas.to_dataframe(tn)
    print(df)

    tn2 = pp.io.to_temporal_network(df, directed=True)

    n1 = tn.number_of_nodes()
    n2 = tn2.number_of_nodes()
    assert n1 == n2
    e1 = tn.number_of_edges()
    e2 = tn2.number_of_edges()
    assert e1 == e2
    te1 = len([e for e in tn.edges[:]])
    te2 = len([e for e in tn2.edges[:]])
    assert te1 == te2

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
