#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_netzschleuder.py -- Test consistency of network metrics against netzschleuder repo
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Sun 2021-05-02 02:20 ingo>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================

import pytest
import pathpy as pp

datasets = [ 
    ('7th_graders', None, True), 
    ('adjnoun', None, False),
    ('ecoli_transcription', 'v1.1', False),
    ('karate', '78', False),
    ('game_thrones', None, False),
    ('cattle', None, False),
    ('student_cooperation', None, True)
    #('facebook_friends', None, True)
    ]

consistency_checks = [ 
    'num_vertices', 
    'num_edges', 
    'largest_component_fraction', 
    'average_degree',
    'degree_assortativity',
    'edge_reciprocity',
    'global_clustering',
    'diameter']

def get_metric(network: pp.Network, metric: str):
    switcher = {
        'num_vertices': network.number_of_nodes(),
        'num_edges': network.number_of_edges(),
        'is_directed': network.directed,
        'average_degree': pp.statistics.mean_degree(network),
        'degree_assortativity': pp.statistics.degree_assortativity(network),
        'global_clustering_coefficient': pp.statistics.avg_clustering_coefficient(network),
        'diameter': pp.algorithms.diameter(network),        
        'edge_reciprocity': pp.statistics.edge_reciprocity(network),
        'largest_component_fraction': pp.algorithms.largest_component_size(network)/network.number_of_nodes()
    }
    return switcher.get(metric, None)

@pytest.mark.slow
def test_netzschleuder_consistency():
    for data, net, multi in datasets:
        print('Running metric tests for network {0}/{1} ...'.format(data, net))

        record = pp.io.graphtool.read_netzschleuder_record(data)
        network = pp.io.graphtool.read_netzschleuder_network(data, net, multiedges=multi)

        if net is None:
            netzschleuder_analysis = record['analyses']
        else:
            netzschleuder_analysis = record['analyses'][net]

        for metric in consistency_checks:
            val = get_metric(network, metric)
            if val is None or netzschleuder_analysis[metric] != pytest.approx(val):
                print('Consistency check failed for network {0} and metric {1}: {2} != {3}'.format(data, metric, netzschleuder_analysis[metric], val))


def test_facebook_friends():

    network = pp.io.graphtool.read_netzschleuder_network('facebook_friends')

    assert network.number_of_nodes() == 362
    assert network.number_of_edges() == 1988