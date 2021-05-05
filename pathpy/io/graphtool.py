"""Functions to read networks from graphtool binary format and to retrieve network data from the netzschleuder repository"""
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

import json
from pathpy.utils.errors import FileFormatError, NetworkError
import pickle
import struct
from collections import defaultdict
from typing import TYPE_CHECKING, Any, List, Optional, Tuple, Union
from urllib import request
from urllib.error import HTTPError

from numpy import array

from pathpy import logger
from pathpy.io.pandas import to_network, to_temporal_network
from pathpy.models.network import Network
from pathpy.models.temporal_network import TemporalNetwork
from pathpy import FileFormatError, NetworkError, MissingModuleError

import pandas as pd

# create logger
LOG = logger(__name__)


def _parse_property_value(data: bytes, ptr: int, type_index: int, endianness: str) -> Tuple[Optional[Any], int]:
    """
    Parses a property value as well as the number of processed bytes.

    Parameters
    ----------

    data: bytes

        byte array containing the data to be decoded

    ptr: int

        index of the first byte to be parsed

    type_index: int

        integer representing the type of the property value to be parsed

    endianness: str

        String representation of endianness, where '>' represents Big Endian 
        and '<' represents Little Endian

    Returns
    -------

    Tuple (v, n) consisting of the property value v and the number of bytes n processed
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
        return (None, 16)
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
        msg = 'Unknown type index {0} while parsing graphtool file'.format(type_index)
        LOG.error(msg)
        raise FileFormatError(msg)


def parse_graphtool_format(data: bytes, ignore_temporal: bool=False, multiedges: bool=False) -> Union[Network, TemporalNetwork]:
    """
    Decodes data in graphtool binary format and returns a pathpy network. For a documentation of 
    hte graphtool binary format, see see doc at https://graph-tool.skewed.de/static/doc/gt_format.html

    Parameters
    ----------

    data: bytes
        Array of bys to be decoded

    ignore_temporal: bool=False
        If False, this function will return a static or temporal network depending 
        on whether edges contain a time attribute. If True, pathpy will not interpret
        time attributes and thus always return a static network.

    Returns
    -------
    Network or TemporalNetwork
        a static or temporal network object
    """

    # check magic bytes
    if data[0:6] != b'\xe2\x9b\xbe\x20\x67\x74':
        LOG.error('Invalid graphtool file. Wrong magic bytes.')
        raise FileFormatError('Invalid graphtool file. Wrong magic bytes.')
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
    comment = data[ptr:ptr+str_len].decode('ascii')
    ptr += str_len

    # read network directedness
    directed = bool(data[ptr])
    ptr += 1

    # read number of nodes
    n_nodes = struct.unpack(graphtool_endianness + 'Q', data[ptr:ptr+8])[0]
    ptr += 8

    # create pandas dataframe
    network_dict = {}
    # n = Network(directed = directed, multiedges=True)

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

    n_edges = 0
    # parse lists of out-neighbors for all n nodes
    for v in range(n_nodes):
        # read number of neighbors
        num_neighbors = struct.unpack(graphtool_endianness + 'Q', data[ptr:ptr+8])[0]
        ptr += 8

        # add edges to record
        for j in range(num_neighbors):
            w = struct.unpack(graphtool_endianness + fmt, data[ptr:ptr+d])[0]
            ptr += d
            network_dict[n_edges] = [str(v), str(w)]
            n_edges += 1
    
    network_data = pd.DataFrame.from_dict(network_dict, orient='index', columns=['v', 'w'])

    # collect all attributes from property maps
    network_attributes = {}
    edge_attribute_names = set()
    node_attributes = defaultdict(lambda: dict())
    edge_attributes = defaultdict(lambda: defaultdict(lambda: pd.NA))
    
    # parse property maps
    property_maps = struct.unpack(graphtool_endianness + 'Q', data[ptr:ptr+8])[0]
    ptr += 8

    for i in range(property_maps):
        key_type = struct.unpack(graphtool_endianness + 'B', data[ptr:ptr+1])[0]
        ptr += 1

        property_len  = struct.unpack(graphtool_endianness + 'Q', data[ptr:ptr+8])[0]
        ptr += 8

        property_name = data[ptr:ptr+property_len].decode('ascii')
        ptr += property_len

        property_type = struct.unpack(graphtool_endianness + 'B', data[ptr:ptr+1])[0]
        ptr += 1

        if key_type == 0: # network property
            res = _parse_property_value(data, ptr, property_type, graphtool_endianness)
            network_attributes[property_name] = res[0]
            ptr += res[1]
        elif key_type == 1: # vertex property
            for v in range(n_nodes):
                res = _parse_property_value(data, ptr, property_type, graphtool_endianness)
                node_attributes[str(v)][property_name] = res[0]
                ptr += res[1]
        elif key_type == 2: # edge property
            for e in range(n_edges):
                res = _parse_property_value(data, ptr, property_type, graphtool_endianness)
                edge_attributes[e][property_name] = res[0]
                edge_attribute_names.add(property_name)
                ptr += res[1]
        else:
            LOG.error('Unknown key type {0}'.format(key_type))

    LOG.info('Version \t= {0}'.format(graphtool_version))
    LOG.info('Endianness \t= {0}'.format(graphtool_endianness))
    LOG.info('comment size \t= {0}'.format(str_len))
    LOG.info('comment \t= {0}'.format(comment))
    LOG.info('directed \t= {0}'.format(directed))
    LOG.info('nodes \t\t= {0}'.format(n_nodes))

    # add edge properties to data frame
    for p in edge_attribute_names:
        # due to use of default_dict, this will add NA values ot edges which are missing properties
        network_data[p] = [ edge_attributes[e][p] for e in range(n_edges) ]

    # create network from pandas dataframe
    n: Optional[Union[Network, TemporalNetwork]] = None
    if 'time' in edge_attribute_names and not ignore_temporal:
        n = to_temporal_network(network_data, directed=directed, **network_attributes)
    else:
        n = to_network(network_data, directed=directed, multiedges=multiedges, **network_attributes)
    
    for v in node_attributes:        
        for p in node_attributes[v]:
            # for now we remove _pos for temporal networks due to type being incompatible with plotting
            if p != '_pos' or ('time' not in edge_attribute_names or ignore_temporal):
                n.nodes[v][p] = node_attributes[v][p]
    return n


def read_graphtool(file: str, ignore_temporal: bool=False, multiedges: bool=False) -> Optional[Union[Network, TemporalNetwork]]: 
    """
    Reads a file in graphtool binary format

    Parameters
    ----------

    file: str
        Path to graphtool file to be read
    """
    with open(file, 'rb') as f:
        if '.zst' in file:
            try: 
                import zstandard as zstd 
                dctx = zstd.ZstdDecompressor()
                data = f.read()
                return parse_graphtool_format(dctx.decompress(data, max_output_size=len(data)))
            except ModuleNotFoundError:
                msg = 'Package zstandard is required to decompress graphtool files. Please install module, e.g., using "pip install zstandard".'
                LOG.error(msg)                
                raise MissingModuleError(msg)
        else:    
            return parse_graphtool_format(f.read(), ignore_temporal, multiedges)


def write_graphtool(network: Network, file: str):
    """
    Writes a network to graphtool binary format
    """ 
    raise NotImplementedError()


def list_netzschleuder_records(base_url: str='https://networks.skewed.de', **kwargs) -> Union[list, dict]:
    """Reads a list of data sets available at the netzschleuder repository.

    Parameters
    ----------
    
    base_url: str='https://networks.skewed.de'

        Base URL of netzschleuder repository
    
    **kwargs

        Keyword arguments that will be passed to the netzschleuder repository as HTTP GET parameters. 
        For supported parameters see https://networks.skewed.de/api


    Examples
    --------
    Return a list of all data sets

    >>> import pathpy as pp
    >>> pp.io.graphtool.list_netzschleuder_records()
    ['karate', 'reality_mining', 'sp_hypertext', ...]

    Return a list of all data sets with a given tag

    >>> pp.io.graphtool.list_netzschleuder_records(tags='temporal')
    ['reality_mining', 'sp_hypertext', ...]

    Return a dictionary containing all data set names (keys) as well as all network attributes
    
    >>> pp.io.graphtool.list_netzschleuder_records(full=True)
    { 'reality_mining': [...], 'karate': [...] }


    Returns
    -------

    Either a list of data set names or a dictionary containing all data set names and network attributes.

    """ 
    url = '/api/nets'
    for k, v in kwargs.items():
        url += '?{0}={1}'.format(k, v)
    try:
        f = request.urlopen(base_url + url).read()
        return json.loads(f)
    except HTTPError:
        msg = 'Could not connect to netzschleuder repository at {0}'.format(base_url)
        LOG.error(msg)
        raise NetworkError(msg)



def read_netzschleuder_record(name: str, base_url: str='https://networks.skewed.de') -> dict:
    """
    Reads metadata of a single data record with given name from the netzschleuder repository

    Parameters
    ----------

    name: str

        Name of the data set for which to retrieve the metadata

    base_url: str='https://networks.skewed.de'

        Base URL of netzschleuder repository

    Examples
    --------

    Retrieve metadata of karate club network
    >>> import pathpy as pp
    >>> metdata = pp.io.graphtool.read_netzschleuder_record('karate')
    >>> print(metadata)
    { 
        'analyses': {'77': {'average_degree': 4.52... } }
    }

    Returns
    -------

    Dictionary containing key-value pairs of metadata
    """ 
    url = '/api/net/{0}'.format(name)
    try:
        return json.loads(request.urlopen(base_url + url).read())
    except HTTPError:
        msg = 'Could not connect to netzschleuder repository at {0}'.format(base_url)
        LOG.error(msg)
        raise NetworkError(msg)


def read_netzschleuder_network(name: str, net: Optional[str]=None, 
        ignore_temporal: bool=False, multiedges: bool=False,
        base_url: str='https://networks.skewed.de') -> Optional[Union[Network, TemporalNetwork]]:
    """Reads a pathpy network record from the netzschleuder repository.

    Parameters
    ----------
    name: str

        Name of the network data sets to read from

    net: Optional[str]=None

        Identifier of the network within the data set to read. For data sets 
        containing a single network only, this can be set to None.

    ignore_temporal: bool=False

        If False, this function will return a static or temporal network depending 
        on whether edges contain a time attribute. If True, pathpy will not interpret
        time attributes and thus always return a static network.

    base_url: str=https://networks.skewed.de

        Base URL of netzschleuder repository

    Examples
    --------

    Read network '77' from karate club data set

    >>> import pathpy as pp
    >>> n = pp.io.graphtool.read_netzschleuder_network('karate', '77')
    >>> print(type(n))
    >>> pp.plot(n)
    pp.Network

    Read a temporal network from a data set containing a single network only
    (i.e. net can be omitted):

    >>> n = pp.io.graphtool.read_netzschleuder_network('reality_mining')
    >>> print(type(n))
    >>> pp.plot(n)
    pp.TemporalNetwork

    Read temporal network but ignore time attribute of edges:

    >>> n = pp.io.graphtool.read_netzschleuder_network('reality_mining', ignore_temporal=True)
    >>> print(type(n))
    >>> pp.plot(n)
    pp.Network


    Returns
    -------

    Depending on whether the network data set contains an edge attribute
    'time' (and whether ignore_temporal is set to True), this function 
    returns an instance of Network or TemporalNetwork

    """
    try:
        import zstandard as zstd

        # retrieve network properties
        url = '/api/net/{0}'.format(name)
        properties = json.loads(request.urlopen(base_url + url).read())

        # retrieve data
        if not net:
            net = name
        url = '/net/{0}/files/{1}.gt.zst'.format(name, net)
        try:
            f = request.urlopen(base_url + url)
        except HTTPError:
            msg = 'Could not connect to netzschleuder repository at {0}'.format(base_url)
            LOG.error(msg)
            raise NetworkError(msg)

        # decompress data
        dctx = zstd.ZstdDecompressor()
        reader = dctx.stream_reader(f)
        decompressed = reader.readall()

        # parse graphtool binary format
        n = parse_graphtool_format(bytes(decompressed), ignore_temporal=ignore_temporal, multiedges=multiedges)
        if n:
            # store network attributes
            for k, v in properties.items():
                n[k] = v

        return n
    except ModuleNotFoundError:
        msg = 'Package zstandard is required to decompress graphtool files. Please install module, e.g., using "pip install zstandard.'
        LOG.error(msg)
        raise MissingModuleError(msg)
