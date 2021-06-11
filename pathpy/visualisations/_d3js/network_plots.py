"""Network plots with d3js"""
#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : network_plots.py -- Network plots with d3js
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Fri 2021-06-11 18:05 juergen>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
from __future__ import annotations

import webbrowser
import tempfile
import json
import os
import uuid

from typing import TYPE_CHECKING, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict

from pathpy import logger, config
from pathpy.visualisations.new_plot import PathPyPlot

# pseudo load class for type checking
if TYPE_CHECKING:
    from pathpy.models.network import Network

# create logger
LOG = logger(__name__)


def network_plot(network: Network, **kwargs: Any):
    """Plot a static network with d3js"""
    result = NetworkPlot(network, **kwargs)
    result.generate()
    return result


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

        # initialize variables
        data: defaultdict = defaultdict(list)

        # convert data to json format
        for key, objects in self.data.items():
            for obj in objects.values():
                data[key].append(
                    {k: v for k, v in asdict(obj).items() if v is not None})

        self.config['selector'] = network_id

        # generate html file
        html = '<style>\n' + css_template + '\n</style>\n'

        # div environment for the plot object
        html += f'\n<div id = "{network_id[1:]}"> </div>\n'

        # add setup code
        html += setup_template

        # add JavaScript
        html += '<script charset="utf-8">\n'

        # add data and config
        html += f'const data = {json.dumps(data)}\n'
        html += f'const config = {json.dumps(self.config)}\n'

        # add JavaScript
        html += js_template
        html += '\n</script>'

        return html


@dataclass
class NodeData:
    """Class to store nodes for plotting"""
    uid: str
    size: Optional[float] = None
    color: Optional[str] = None
    opacity: Optional[float] = None
    x: Optional[float] = None
    y: Optional[float] = None


@dataclass
class EdgeData:
    """Class to store nodes for plotting"""
    uid: str
    source: str
    target: str
    size: Optional[float] = None
    color: Optional[str] = None
    opacity: Optional[float] = None
    weight: float = 1.0
    # directed: bool = True
    # curved: bool = True


class NetworkPlot(D3jsPlot):
    """Network plot class for a static network."""

    _kind = 'network'

    def __init__(self, network: Network, **kwargs: Any):
        """Initialize network plot class"""
        super().__init__(**kwargs)
        self.network = network

    def generate(self):
        """Function to generate the plot"""
        self._compute_edge_data()
        self._compute_node_data()

    def _compute_node_data(self):
        """Generate the data structure for the nodes"""
        nodes: dict = {}
        for uid, node in self.network.nodes.items():
            nodes[uid] = NodeData(
                uid,
                size=node['size'],
                color=node['color'],
                opacity=node['opacity'],
                x=node['x'],
                y=node['y'],
            )
        self.data['nodes'] = nodes

    def _compute_edge_data(self):
        """Generate the data structure for the edges"""
        edges: dict = {}
        for uid, edge in self.network.edges.items():
            edges[uid] = EdgeData(
                uid,
                edge.v.uid,
                edge.w.uid,
                size=edge['size'],
                color=edge['color'],
                opacity=edge['opacity'],
                weight=edge.weight('weight'),
            )
        self.data['edges'] = edges

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
