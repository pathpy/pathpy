"""Backend for d3js."""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : d3js.py -- Module to draw a d3js-network
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Fri 2020-05-22 15:29 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from __future__ import annotations  # remove for python 3.8
import os
import uuid
import json

from string import Template

from pathpy import logger, config

# create logger for the Network class
LOG = logger(__name__)


class D3js:
    """Class to draw d3js objects."""

    def __init__(self) -> None:
        """Initialize d3js drawer"""

    @staticmethod
    def to_html(figure) -> str:
        """Convert figure to a single html document."""
        LOG.debug('Generate single html document.')

        # generate unique dom uids
        widgets_id = 'x'+uuid.uuid4().hex
        network_id = 'x'+uuid.uuid4().hex

        # template directory
        temp_dir = str(os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            os.path.normpath('templates/network')))

        # clean config
        _config = figure['config']
        _config.pop('node')
        _config.pop('edge')

        if _config['coordinates']:
            _config['layout'] = 'euclidean'
            _config['euclidean'] = True
            _config['widgets']['layout']['enabled'] = True

        # clean data
        data = figure['data']
        data['links'] = data.pop('edges')

        # mirrow y axis
        if _config['coordinates']:
            for node in data['nodes']:
                _x, _y = node['coordinates']
                node['coordinates'] = (_x, _config['height']-_y)

        # load js template
        temp_name = 'template.html'
        if config['environment']['IDE'] == 'vs code':
            temp_name = 'template_vscode.html'

        with open(os.path.join(temp_dir, temp_name)) as temp:
            js_template = temp.read()

        # load css template
        # TODO: Load user css template if given
        with open(os.path.join(temp_dir, 'css/style.css')) as temp:
            css_template = temp.read()

        # Substitute parameters in the template
        js = Template(js_template).substitute(divId=widgets_id,
                                              svgId=network_id,
                                              config=json.dumps(_config),
                                              data=json.dumps(data))

        # generate html file with css styles
        html = '<style>\n' + css_template + '\n</style>\n'

        # if config['environment']['IDE'] != 'vs code':
        #     html = html + '<script charset="utf-8" src="https://d3js.org/d3.v5.min.js"></script>\n <script charset="utf-8" src="https://requirejs.org/docs/release/2.3.6/minified/require.js"></script>'
        # div environment for the widgets and network
        html = html + \
            '<div id="{}"></div>\n<div id="{}"></div>\n'.format(
                widgets_id, network_id)

        # add js code
        html = html+js

        # return the html file
        return html

    @staticmethod
    def to_json(figure) -> tuple:
        """Convert figure to a tuple of json files."""
        raise NotImplementedError

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
