#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : io.py -- Module for data import/export
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Mon 2020-05-22 15:53 ingo>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, Optional, cast

import sqlite3
import bz2
import tarfile
import io
import urllib
import xml.etree.ElementTree as ET

import pandas as pd  # pylint: disable=import-error

from pathpy import config, logger
from pathpy.core.edge import Edge
from pathpy.core.node import Node
from pathpy.core.network import Network

# create logger
LOG = logger(__name__)


def read_csv(filename: str, directed: bool = True, loops: bool = True, sep: str = ',',
             header: bool = True, names: Optional[list] = None,
             **kwargs: Any) -> Network:
    """Read network from a csv file,"""

    if header:
        df = pd.read_csv(filename, sep=sep)
    else:
        df = pd.read_csv(filename, header=0, names=names, sep=sep)

    return from_dataframe(df, directed=directed, loops=loops, **kwargs)


def from_dataframe(df: pd.DataFrame, directed: bool = True, loops: bool = True, multiedges: bool= False,
                   **kwargs: Any) -> Network:
    """Reads a network from a pandas dataframe.

    By default, columns `v` and `w` will be used as source and target of
    edges. If no column 'v' or 'w' exists, the list of synonyms for `v` and
    `w`` in the config file will be used to remap columns, choosing the first
    matching entries. Any columns not used to create edges will be used as edge
    attributes, e.g. if a column 'v' is present and an additional column
    `source`is given, `source` will be assigned as an edge property.

    In addition, an optional column `uid` will be used to assign node uids. If
    this column is not present, default edge uids will be created.  Any other
    columns (e.g. weight, type, time, etc.) will be assigned as edge
    attributes. kwargs will be assigned as network attributes.

    Parameters
    ----------

    directed: bool

        Whether to generate a directed or undirected network.

    **kwargs: Any

        List of key-value pairs that will be assigned as network attributes

    Examples
    --------

    """

    # if no v/w columns are included, pick first synonym
    if 'v' not in df.columns:
        LOG.info('No column v, searching for synonyms')
        for col in df.columns:
            if col in config['edge']['v_synonyms']:
                LOG.info('Remapping column \'%s\' to \'v\'', col)
                df.rename(columns={col: "v"}, inplace=True)
                continue

    if 'w' not in df.columns:
        LOG.info('No column w, searching for synonyms')
        for col in df.columns:
            if col in config['edge']['w_synonyms']:
                LOG.info('Remapping column \'%s\' to \'w\'', col)
                df.rename(columns={col: "w"}, inplace=True)
                continue

            LOG.debug('Creating %s network', directed)

    net = Network(directed=directed, multiedges=multiedges, **kwargs)
    for row in df.to_dict(orient='records'):

        # get edge
        v = row.get('v', None)
        w = row.get('w', None)
        uid = row.get('uid', None)
        if v is None or w is None:
            LOG.error('DataFrame minimally needs columns \'v\' and \'w\'')
            raise IOError
        else:
            v = str(v)
            w = str(w)
        if v not in net.nodes.uids:
            net.add_node(v)
        if w not in net.nodes.uids:
            net.add_node(w)
        if uid is None:
            edge = Edge(net.nodes[v], net.nodes[w])
        else:
            edge = Edge(net.nodes[v], net.nodes[w], uid=uid)
        if loops or edge.v != edge.w:
            net.add_edge(edge)

        reserved_columns = set(['v', 'w', 'uid'])
        for k in row:
            if k not in reserved_columns:
                edge[k] = row[k]
    return net


def read_sql(filename: Optional[str] = None, directed: bool = True, loops: bool = True,
                con: Optional[sqlite3.Connection] = None,
                sql: Optional[str] = None, table: Optional[str] = None,
                **kwargs: Any) -> Network:
    """Read network from an sqlite database."""

    LOG.debug('Load sql file as pandas data frame.')

    if con is None and filename is None:
        LOG.error('Either an SQL connection or a filename is required')
        raise IOError

    con_close = False
    # connect to database if not given
    if con is None and filename is not None:
        con_close = True
        con = sqlite3.connect(filename)

    # if sql query is not given check availabe tables
    if sql is None:

        # create cursor and get all tables availabe
        cursor = cast(sqlite3.Connection, con).cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = list(sum(cursor.fetchall(), ()))

        # check if table is given
        if table is None:
            table = tables[0]
        elif table not in tables:
            LOG.error('Given table "%s" not in database!', table)
            raise IOError

        # generate sql query
        sql = 'SELECT * from {}'.format(table)

    # read to pandas data frame
    df = pd.read_sql(sql, con)

    # close connection to the database
    if con_close:
        _con = cast(sqlite3.Connection, con)
        _con.close()

    # construct network from pandas data frame
    return from_dataframe(df, directed=directed, loops=loops, **kwargs)


def to_dataframe(network: Network, exclude_edge_uid: bool = False, export_indices: bool=False) -> pd.DataFrame:
    """Returns a pandas dataframe of the network.

    Returns a pandas dataframe data that contains all edges including all edge
    attributes. Node and network-level attributes are not included.

    """
    df = pd.DataFrame()

    for edge in network.edges:
        v = edge.v.uid
        w = edge.w.uid
        if export_indices:
            v = network.nodes.index[v]
            w = network.nodes.index[w]
        if exclude_edge_uid:
            edge_df = pd.DataFrame(columns=['v', 'w'])           
            edge_df.loc[0] = [v, w]
        else:
            edge_df = pd.DataFrame(columns=['v', 'w', 'uid'])            
            edge_df.loc[0] = [v, w, edge.uid]            
        edge_df = pd.concat([edge_df, edge.attributes.to_frame()], axis=1)
        df = pd.concat([edge_df, df], ignore_index=True)
    return df


def write_csv(network: Network, path_or_buf: Any = None, exclude_edge_uid: bool=False, export_indices: bool=False, **pdargs: Any):
    """Stores all edges including edge attributes in a csv file.

    Node and network-level attributes are not included.

    Parameters
    ----------

    network: Network

        The network to save as csv file

    path_or_buf: Any

        This can be a string, a file buffer, or None (default). Follows
        pandas.DataFrame.to_csv semantics.  If a string filename is given, the
        network will be saved in a file. If None, the csv file contents is
        returned as a string. If a file buffer is given, the csv file will be
        saved to the file.

    exclude_edge_uid: bool

        Whether to exclude edge uids in the exported csv file or not (default). If this is set to 
        True, each edge between nodes with uids v and w will be exported to a line w,v. If this is 
        set to False (default), the uid of the edge will be additionally included, i.e. exporting 
        v,w,e_uid. The latter ensures that both nodes and edges will retain their uids when writing 
        and reading a network with pathpy. Excluding edge_uids can be necessary to export edge lists 
        for use in third-party packages.

    export_indices: bool 

        Whether or not to replace node uids by integer node indices. If False (default), string node uids 
        in pp.Network instance will be used. If True, node integer indices are exported instead, which may be 
        necessary to export edge lists that can be used by third-party packages such as node2vec.

    **pdargs:

        Keyword args that will be passed to pandas.DataFrame.to_csv. This
        allows full control of the csv export.

    """

    df = to_dataframe(network, exclude_edge_uid = exclude_edge_uid, export_indices = export_indices)
    return df.to_csv(path_or_buf=path_or_buf, index=False, **pdargs)


def write_sql(network: Network,  table: str,
              filename: Optional[str] = None,
              con: Optional[sqlite3.Connection] = None, **pdargs: Any) -> None:
    """Stores all edges including edge attributes in an sqlite database table.

    Node and network-level attributes are not included.

    Parameters
    ----------

    network: Network

        The network to store in the sqlite database

    filename: str

        The name of the SQLite database in which the network will be stored

    con: sqlite3.Connection

        The SQLite3 connection in which the network will be stored

    table: str

        Name of the table in the database in which the network will be stored.

    **pdargs:

        Keyword args that will be passed to pandas.DataFrame.to_sql.

    """

    df = to_dataframe(network)

    LOG.debug('Store network as sql database.')

    if con is None and filename is None:
        LOG.error('Either an SQL connection or a filename is required')
        raise IOError

    con_close = False
    # connect to database if not given
    if con is None:
        con = sqlite3.connect(cast(str, filename))
        con_close = True

    df.to_sql(table, con, **pdargs)

    if con_close:
        _con = cast(sqlite3.Connection, con)
        _con.close()


def read_konect_file(file):
    """Reads a KONECT data file and returns a pp.Network instance.

    The unified KONECT data format is a compressed .tar.bz2 file containing 
    two files meta.* and out.*. The key-value attributes in the meta file
    (typically containing data descriptions and link to original data source)
    are stored as attributes in the returned instance of pp.Network. 

    Depending on the data file, the generated network will be a single -or multi-edge 
    network with directed or undirected edges. The type of the network will be automatically 
    determined based on the data file. Weight and Time attributes are stored as edge attributes.

    Parameters
    ----------

    file: str, Bytes

        Filename or byte stream from which data should be loaded

    """

    tsv_columns = ['v', 'w', 'weight', 'time']

    if isinstance(file, str):
        tar = tarfile.open(file, mode='r:bz2')
    elif isinstance(file, bytes):
        tar = tarfile.open(fileobj=io.BytesIO(file), mode='r:bz2')
    attributes = {}
    directed = False
    multiedges = False
    network_data = None
    for tarinfo in tar:
        if tarinfo.isfile():
            f = tarinfo.path.split('/')[-1]

            # read meta-data into attributes
            if f.startswith('meta.'):
                with io.TextIOWrapper(tar.extractfile(tarinfo)) as buffer:
                    for line in buffer.readlines():                        
                        s = line.split(': ', 1)
                        # ignore empty lines
                        if len(s) == 2:
                            attributes[s[0].strip()] = s[1].strip()
            
            # read network data
            elif f.startswith('out.'):
                with io.TextIOWrapper(tar.extractfile(tarinfo)) as buffer:
                    directed = 'asym' in buffer.readline()
                    network_data = pd.read_csv(buffer, sep=' ', header=None, comment='%')
                    network_data = network_data.dropna(axis=1, how='all')
                    
                    # print(network_data.head())                    
                    network_data.columns = [tsv_columns[i] for i in range(len(network_data.columns))]
                    duplicates = len(network_data[network_data.duplicated(['v', 'w'], keep=False)])
                    if duplicates>0:
                        print('Found {} duplicate edges'.format(duplicates))
                        multiedges = True
                    print('Detected columns: ', [c for c in network_data.columns])
    if 'timeiso' in attributes:
        attributes['time'] = attributes['timeiso']
    return from_dataframe(network_data, directed=directed, multiedges=multiedges, **attributes)


def read_konect_name(name, base_url="http://konect.uni-koblenz.de/downloads/tsv/"):
    """Retrieves a KONECT data set with a given name and returns a corresponding 
    instance of pp.Network.

    The unified KONECT data format is a compressed .tar.bz2 file containing 
    two files meta.* and out.*. The key-value attributes in the meta file
    (typically containing data descriptions and link to original data source)
    are stored as attributes in the returned instance of pp.Network. 

    Depending on the data file, the generated network will be a single -or multi-edge 
    network with directed or undirected edges. The type of the network will be automatically 
    determined based on the data file. Weight and Time attributes are stored as edge attributes.

    Parameters
    ----------

    name: str

        Name of the data set to retrieve from the KONECT database, e.g. 'moreno_bison'

    base_url: str

        Base url of the KONECT service that will be used to retrieve data set. Default is 
        "http://konect.uni-koblenz.de/downloads/tsv/". This method assumes that the KONECT data file 
        with name X can be retrieved via HTTP under the URL "http://konect.uni-koblenz.de/downloads/tsv/X.tar.bz2"
    """
    f = urllib.request.urlopen(base_url + name + ".tar.bz2").read()
    return read_konect_file(f)


def read_graphml(filename: str):
    """Reads a pathyp.Network from a graphml file. This function supports typed Node and Edge attributes 
    including default values. 
    
    Warnings are issued if the type of Node or Edge attributes are undeclared,  in which case the attribute type will fall back to string.

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
                print('Warning: Undeclared Node attribute "{}". Defaulting to string type.'.format(key))
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
                print('Warning: Undeclared Edge attribute "{}". Defaulting to string type.'.format(key))
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
