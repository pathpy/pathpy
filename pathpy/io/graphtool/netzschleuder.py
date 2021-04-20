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
from pathpy.io.graphtool.graphtool import parse_graphtool_format
from typing import TYPE_CHECKING, Optional, Union


from pathpy import config, logger

from pathpy.models.network import Network

import urllib
import json

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

    # retrieve network properties
    url = '/api/net/{0}'.format(name)
    properties = json.loads(urllib.request.urlopen(base_url + url).read())

    # retrieve data
    if not net:
        net = name
    url = '/net/{0}/files/{1}.gt.zst'.format(name, net)
    try:
        f = urllib.request.urlopen(base_url + url).read()
    except urllib.error.HTTPError:
        LOG.error('HTTP 404 Error. Did you specify the network to load from this data set?')
        return None

    # decompress data
    dctx = zstd.ZstdDecompressor()
    decompressed = dctx.decompress(f, max_output_size=1048576)

    # parse graphtool binary format
    n = parse_graphtool_format(bytes(decompressed))
    if n:
        # store network attributes
        for k, v in properties.items():
            n[k] = v

    return n
