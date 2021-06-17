#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : core.py -- Plots with d3js
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2021-06-17 16:39 juergen>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
from __future__ import annotations

import os
import json
import uuid
import tempfile
import webbrowser

from typing import Any

from pathpy import logger, config
from pathpy.visualisations.new_plot import PathPyPlot

# create logger
LOG = logger(__name__)


class D3jsPlot(PathPyPlot):
    """Base class for plotting d3js objects"""

    def __init__(self, **kwargs: Any):
        """Initialize plot class"""
        super().__init__()
        if kwargs:
            self.config = kwargs

    def generate(self):
        """Function to generate the plot"""
        raise NotImplementedError

    def save(self, filename: str) -> None:
        """Function to save the plot"""
        with open(filename, 'w+') as new:
            new.write(self.to_html())

    def show(self) -> None:
        """Function to show the plot"""

        if config['environment']['interactive']:
            from IPython.core.display import display, HTML
            display(HTML(self.to_html()))
        else:
            # create temporal file
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                # save html
                self.save(temp_file.name)
                # open the file
                webbrowser.open(r'file:///'+temp_file.name)

    def to_json(self) -> str:
        """Convert data to json"""
        raise NotImplementedError

    def to_html(self) -> str:
        """Convert data to html"""

        # generate unique dom uids
        network_id = "#x"+uuid.uuid4().hex

        # get path to the pathpy templates
        template_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            os.path.normpath('_d3js/templates'))

        # get template files
        with open(os.path.join(template_dir, "network.js")) as template:
            js_template = template.read()

        with open(os.path.join(template_dir, "setup.html")) as template:
            setup_template = template.read()

        with open(os.path.join(template_dir, "styles.css")) as template:
            css_template = template.read()

        # update config
        self.config['selector'] = network_id

        data = self.to_json()

        # generate html file
        html = '<style>\n' + css_template + '\n</style>\n'

        # div environment for the plot object
        html += f'\n<div id = "{network_id[1:]}"> </div>\n'

        # add setup code
        html += setup_template

        # add JavaScript
        html += '<script charset="utf-8">\n'

        # add data and config
        html += f'const data = {data}\n'
        html += f'const config = {json.dumps(self.config)}\n'

        # add JavaScript
        html += js_template
        html += '\n</script>'

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
