"""Functions to read graphml files."""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : graphml.py -- Read graphml data files
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Sat 2020-08-22 17:21 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================

import xml.etree.ElementTree as ET

from pathpy import logger
from pathpy.core.edge import Edge, EdgeCollection
from pathpy.core.node import Node, NodeCollection
from pathpy.core.network import Network


# create logger
LOG = logger(__name__)


def read_network(filename: str):
    """Reads a pathyp.Network from a graphml file.

    This function supports typed Node and Edge attributes including default
    values.

    Warnings are issued if the type of Node or Edge attributes are undeclared,
    in which case the attribute type will fall back to string.

    Parameters
    ----------

    filename: str
        The graphml file to read the graph from

    """
    root = ET.parse(filename).getroot()

    graph = root.find('{http://graphml.graphdrawing.org/xmlns}graph')
    directed = graph.attrib['edgedefault'] != 'undirected'
    uid = graph.attrib['id']
    n = Network(directed=directed, uid=uid)

    node_attributes = {}
    edge_attributes = {}

    # read attribute types and default values
    for a in root.findall('{http://graphml.graphdrawing.org/xmlns}key'):
        a_id = a.attrib['id']
        a_name = a.attrib['attr.name']
        a_type = a.attrib['attr.type']
        a_for = a.attrib['for']

        # store attribute info and assign data types
        a_data = {'name': a_name}
        if a_type == 'string':
            a_data['type'] = str
        elif a_type == 'float':
            a_data['type'] = float
        elif a_type == 'double':
            a_data['type'] = float
        elif a_type == 'int':
            a_data['type'] = int
        elif a_type == 'long':
            a_data['type'] = int
        elif a_type == 'boolean':
            a_data['type'] = bool
        else:
            a_data['type'] = str

        d = a.find('{http://graphml.graphdrawing.org/xmlns}default')
        if d is not None:
            a_data['default'] = a_data['type'](d.text)

        if a_for == 'node':
            node_attributes[a_name] = a_data
        if a_for == 'edge':
            edge_attributes[a_name] = a_data

    # add nodes with uids and attributes
    for node in graph.findall('{http://graphml.graphdrawing.org/xmlns}node'):
        # create node
        uid = node.attrib['id']
        v = Node(uid=uid)

        # set attribute values
        for a in node.findall('{http://graphml.graphdrawing.org/xmlns}data'):
            key = a.attrib['key']
            val = a.text
            if key not in node_attributes:
                LOG.warning(
                    'Undeclared Node attribute "{}". Defaulting to string type.'.format(key))
                v.attributes[key] = val
            else:
                v.attributes[key] = node_attributes[key]['type'](val)

        # set default values
        for a_name in node_attributes:
            if 'default' in node_attributes[a_name] and v.attributes[a_name] is None:
                v.attributes[a_name] = node_attributes[a_name]['default']
        n.add_node(v)

    # add edges with uids and attributes
    for edge in graph.findall('{http://graphml.graphdrawing.org/xmlns}edge'):
        # create edge
        source = edge.attrib['source']
        target = edge.attrib['target']
        uid = edge.attrib['id']
        e = Edge(n.nodes[source], n.nodes[target], uid=uid)

        # set attribute values
        for a in edge.findall('{http://graphml.graphdrawing.org/xmlns}data'):
            key = a.attrib['key']
            val = a.text
            if key not in edge_attributes:
                LOG.warning(
                    'Warning: Undeclared Edge attribute "{}". Defaulting to string type.'.format(key))
                e.attributes[key] = val
            else:
                e.attributes[key] = edge_attributes[key]['type'](val)
        # set default values
        for a_name in edge_attributes:
            if 'default' in edge_attributes[a_name] and e.attributes[a_name] is None:
                e.attributes[a_name] = edge_attributes[a_name]['default']
        n.add_edge(e)
    return n


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
