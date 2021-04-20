#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : netzschleuder.py -- Module for data import/export from netzschleuder repository
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Wed 2021-04-20 12:29 ingo>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Union


from pathpy import config, logger

from pathpy.models.network import Network

import urllib
import json
import struct

# create logger
LOG = logger(__name__)


def list_netzschleuder(properties=False, base_url='https://networks.skewed.de') -> Union[list, dict]:
    """
    Reads a list of data sets from the netzschleuder repository
    """ 
    url = '/api/nets'
    if properties:
        url = url + '?full=True'
    f = urllib.request.urlopen(base_url + url).read()
    return json.loads(f)


def read_netzschleuder(name: str, net: Optional[str]=None, base_url='https://networks.skewed.de') -> Network:
    """
    Reads a network from the netzschleuder repository
    """
    import zstandard as zstd 

    url = '/api/net/{0}'.format(name)
    properties = json.loads(urllib.request.urlopen(base_url + url).read())

    if not net:
        net = name
    url = '/net/{0}/files/{1}.gt.zst'.format(name, net)
    try:
        f = urllib.request.urlopen(base_url + url).read()
    except urllib.error.HTTPError:
        LOG.error('Did you specify the network to load from this data set?')
        return None

    # decompress data
    dctx = zstd.ZstdDecompressor()
    decompressed = dctx.decompress(f, max_output_size=1048576)
    # see doc at https://graph-tool.skewed.de/static/doc/gt_format.html

    # six magic bytes in decompressed[0:6]
    ptr = 6

    version = int(decompressed[ptr])
    ptr += 1

    if bool(decompressed[ptr]):
        endianness = '>'
    else:
        endianness = '<'
    ptr += 1

    str_len = struct.unpack(endianness + 'Q', decompressed[ptr:ptr+8])[0]
    ptr += 8


    comment = decompressed[ptr:ptr+str_len].decode('utf-8')
    ptr += str_len

    directed = bool(decompressed[ptr])
    ptr += 1

    n_nodes = struct.unpack(endianness + 'Q', decompressed[ptr:ptr+8])[0]
    ptr += 8

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
    
    n = Network(directed = directed, multiedges=True)

    # lists of out neighbors for all n nodes
    for v in range(n_nodes):
        # read number of neighbors
        num_neighbors = struct.unpack(endianness + 'Q', decompressed[ptr:ptr+8])[0]
        ptr += 8

        for j in range(num_neighbors):
            w = struct.unpack(endianness + fmt, decompressed[ptr:ptr+d])[0]
            ptr += d
            n.add_edge(str(v), str(w))

    # store network attributes
    for k, v in properties.items():
        n[k] = v    

    LOG.info('Version \t= ', version)
    LOG.info('Endianness \t= ', endianness)
    LOG.info('comment size \t= ', str_len)
    LOG.info('comment \t= ', comment)
    LOG.info('directed \t= ', directed)
    LOG.info('nodes \t\t= ', n_nodes)
    
    return n
