#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : graphtool.py -- Module for data import/export from graphtool binary format
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Wed 2021-04-21 09:06 ingo>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Union


from pathpy import config, logger

from pathpy.models.network import Network
from numpy import array

import struct
import pickle

# create logger
LOG = logger(__name__)


def _parse_property_value(data, ptr, type_index, endianness):
    """
    Parses a property value and returns the value along with the number of processed bytes
    """
    if type_index == 0:
        return (bool(data[ptr]), 1)
    elif type_index == 1:
        return (struct.unpack(endianness + 'h', data[ptr:ptr+2])[0], 2)
    elif type_index == 2:
        return (struct.unpack(endianness + 'i', data[ptr:ptr+4])[0], 4)
    elif type_index == 3:
        return (struct.unpack(endianness + 'q', data[ptr:ptr+8])[0], 8)
    elif type_index == 4:
        return (struct.unpack(endianness + 'd', data[ptr:ptr+8])[0], 8)
    elif type_index == 5:
        LOG.warning('pathpy does not support properties with type long double. Properties have been dropped.')
    elif type_index == 6:
        str_len = struct.unpack(endianness + 'Q', data[ptr:ptr+8])[0]
        str = data[ptr+8:ptr+8+str_len].decode('utf-8')
        return (str, 8 + str_len)
    elif type_index == 7:
        num_values = struct.unpack(endianness + 'Q', data[ptr:ptr+8])[0]
        offset = 8
        vals = []
        for i in range(num_values):
            vals.append(bool(data[ptr+offset:ptr+offset+1]))
            offset += 1
        return (array(vals), 8 + num_values)
    elif type_index == 8:
        num_values = struct.unpack(endianness + 'Q', data[ptr:ptr+8])[0]
        offset = 8
        vals = []
        for i in range(num_values):
            vals.append(struct.unpack(endianness + 'h', data[ptr+offset:ptr+offset+2])[0])
            offset += 4
        return (array(vals), 8 + 2*num_values)
    elif type_index == 9:
        num_values = struct.unpack(endianness + 'Q', data[ptr:ptr+8])[0]
        offset = 8
        vals = []
        for i in range(num_values):
            vals.append(struct.unpack(endianness + 'i', data[ptr+offset:ptr+offset+4])[0])
            offset += 4
        return (array(vals), 8 + 4*num_values)
    elif type_index == 10:
        num_values = struct.unpack(endianness + 'Q', data[ptr:ptr+8])[0]
        offset = 8
        vals = []
        for i in range(num_values):
            vals.append(struct.unpack(endianness + 'Q', data[ptr+offset:ptr+offset+8])[0])
            offset += 8
        return (None, 8 + 8*num_values)
    elif type_index == 11:
        num_values = struct.unpack(endianness + 'Q', data[ptr:ptr+8])[0]
        offset = 8
        vals = []
        for i in range(num_values):
            vals.append(struct.unpack(endianness + 'd', data[ptr+offset:ptr+offset+8])[0])
            offset += 8
        return (array(vals), 8 + 8*num_values)
    elif type_index == 12:
        val_len = struct.unpack(endianness + 'Q', data[ptr:ptr+8])[0]
        LOG.warning('pathpy does not support properties with type vector<long double>. Properties have been dropped.')
        return (None, 8 + 16*val_len)
    elif type_index == 13:
        num_strings = struct.unpack(endianness + 'Q', data[ptr:ptr+8])[0]
        offset = 8
        strs = []
        for i in range(num_strings):
            str_len = struct.unpack(endianness + 'Q', data[ptr+offset:ptr+offset+8])[0]
            offset += 8
            strs.append(data[ptr+offset:ptr+offset+str_len].decode('utf-8'))
            offset += str_len

        return (strs, offset)
    elif type_index == 14:
        val_len = struct.unpack(endianness + 'Q', data[ptr:ptr+8])[0]
        return (pickle.loads(data[ptr+8:ptr+8+val_len]), 8 + val_len)
    else:
        LOG.error('Unknown type index {0}'.format(type_index))

def parse_graphtool_format(data: bytes) -> Network:
    """
    Parses the graphtool binary format and returns a pathpy Network
    """
    # see doc at https://graph-tool.skewed.de/static/doc/gt_format.html

    # check magic bytes
    if data[0:6] != b'\xe2\x9b\xbe\x20\x67\x74':
        LOG.error('Invalid graphtool file. Wrong magic bytes.')
        return None
    ptr = 6

    # read graphtool version byte
    graphtool_version = int(data[ptr])
    ptr += 1

    # read endianness
    if bool(data[ptr]):
        graphtool_endianness = '>'
    else:
        graphtool_endianness = '<'
    ptr += 1

    # read length of comment
    str_len = struct.unpack(graphtool_endianness + 'Q', data[ptr:ptr+8])[0]
    ptr += 8

    # read string comment
    comment = data[ptr:ptr+str_len].decode('utf-8')
    ptr += str_len

    # read network directedness
    directed = bool(data[ptr])
    ptr += 1

    # read number of nodes
    n_nodes = struct.unpack(graphtool_endianness + 'Q', data[ptr:ptr+8])[0]
    ptr += 8

    # create pathpy network
    n = Network(directed = directed, multiedges=True)

    # determine binary representation of neighbour lists
    if n_nodes<2**8:
        fmt = 'B'
        d = 1
    elif n_nodes<2**16:
        fmt = 'H'
        d = 2
    elif n_nodes<2**32:
        fmt = 'I'
        d = 4
    else:
        fmt = 'Q'
        d = 8

    # parse lists of out-neighbors for all n nodes
    for v in range(n_nodes):
        # read number of neighbors
        num_neighbors = struct.unpack(graphtool_endianness + 'Q', data[ptr:ptr+8])[0]
        ptr += 8

        if num_neighbors == 0 and str(v) not in n.nodes.uids:
            n.add_node(str(v))
        for j in range(num_neighbors):
            w = struct.unpack(graphtool_endianness + fmt, data[ptr:ptr+d])[0]
            ptr += d
            n.add_edge(str(v), str(w))
        
    # read property maps
    property_maps = struct.unpack(graphtool_endianness + 'Q', data[ptr:ptr+8])[0]
    ptr += 8

    for i in range(property_maps):
        key_type = struct.unpack(graphtool_endianness + 'B', data[ptr:ptr+1])[0]
        ptr += 1

        property_len  = struct.unpack(graphtool_endianness + 'Q', data[ptr:ptr+8])[0]
        ptr += 8

        property_name = data[ptr:ptr+property_len].decode('utf-8')
        ptr += property_len

        property_type = struct.unpack(graphtool_endianness + 'B', data[ptr:ptr+1])[0]
        ptr += 1

        if key_type == 0: # network property
            res = _parse_property_value(data, ptr, property_type, graphtool_endianness)
            n[property_name] = res[0]
            ptr += res[1]
        elif key_type == 1: # vertex property
            for v in range(n_nodes):
                res = _parse_property_value(data, ptr, property_type, graphtool_endianness)
                n.nodes[str(v)][property_name] = res[0]
                ptr += res[1]
        elif key_type == 2: # edge property
            for e in n.edges:
                res = _parse_property_value(data, ptr, property_type, graphtool_endianness)
                n.edges[e.uid][property_name] = res[0]
                ptr += res[1]
        else:
            LOG.error('Unknown key type {0}'.format(key_type))

    LOG.info('Version \t= ', graphtool_version)
    LOG.info('Endianness \t= ', graphtool_endianness)
    LOG.info('comment size \t= ', str_len)
    LOG.info('comment \t= ', comment)
    LOG.info('directed \t= ', directed)
    LOG.info('nodes \t\t= ', n_nodes)
    return n


def read_graphtool(file: str) -> Network: 
    """
    Reads a file in graphtool binary format
    """
    with open(file, 'rb') as f:
        if '.zst' in file:
            import zstandard as zstd 
            dctx = zstd.ZstdDecompressor()
            return parse_graphtool_format(dctx.decompress(f.read(), max_output_size=1048576))
        else:    
            return parse_graphtool_format(f.read())


def write_graphtool(network: Network, file: str):
    """
    Writes a network to graphtool binary format
    """ 
    raise NotImplementedError()