#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : plot.py -- Module to plot pathpy objects
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Mon 2019-09-30 10:07 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
import os
import json
import random
from string import ascii_letters, Template
from .. import logger, config
# create logger for the Edge class
log = logger(__name__)


class Plot:
    """Class to visulize pathpy objects."""

    def __init_(self):
        """Initialize the Plot class."""
        pass

    def __call__(self, network, **kwargs):
        """Call the plot function and plot or show the results."""
        # TODO: Make a dedicated class to generate html files
        html = self._generate_html(network, **kwargs)

        from IPython.core.display import display, HTML
        display(HTML(html))

    def _generate_html(self, network, **kwargs):
        # Initialize dictionaries
        network_data = {}
        params = {}

        # Get network data
        network_data['nodes'] = []
        network_data['links'] = []

        for id, node in network.nodes.items():
            _data = {'id': id,
                     'text': 'mytext',
                     'color': '#99ccff',
                     'size': 5.0}
            network_data['nodes'].append(_data)

        for id, edge in network.edges.items():
            _data = {'source': edge.v.id,
                     'target': edge.w.id,
                     'color': '#999999',
                     'width': 0.5,
                     'weight': 1.0}
            network_data['links'].append(_data)

        # get parameters
        # DIV params
        params['height'] = 400
        params['width'] = 400
        params['label_size'] = '8px'
        params['label_offset'] = [0, -10]
        params['label_color'] = '#999999'
        params['label_opacity'] = 1.0
        params['edge_opacity'] = 1.0
        # layout params
        params['force_repel'] = -200
        params['force_charge'] = -20
        params['force_alpha'] = 0.0

        # arrows
        params['edge_arrows'] = 'true'
        if not network.directed:
            params['edge_arrows'] = 'false'

        # Create a random DIV ID to avoid conflicts within the same notebook
        div_id = "".join(random.choice(ascii_letters) for x in range(8))

        module_dir = os.path.dirname(os.path.realpath(__file__))
        html_dir = os.path.join(module_dir, 'templates')

        params['d3js_path'] = 'https://d3js.org/d3.v4.min.js'

        d3js_params = {
            'network_data': json.dumps(network_data),
            'div_id': div_id,
        }

        template_file = os.path.abspath(
            os.path.join(html_dir, 'network.html'))

        # Read template file ...
        with open(template_file) as f:
            html_str = f.read()

        # substitute variables in template file
        html = Template(html_str).substitute({**d3js_params, **params})

        return html


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
