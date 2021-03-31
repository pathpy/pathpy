"""Functions to read and write csv tables."""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : sql.py -- Read and write sql database tables
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Mon 2021-03-29 17:35 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================

from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional, Union

import pandas as pd  # pylint: disable=import-error

from pathpy import logger
from pathpy.io.io import to_network, to_temporal_network, to_dataframe

from pathpy.core.node import Node, NodeCollection
from pathpy.core.edge import Edge, EdgeCollection
# from pathpy.core.path import Path, PathCollection

# pseudo load class for type checking
if TYPE_CHECKING:
    from pathpy.models.network import Network
    from pathpy.models.temporal_network import TemporalNetwork
    from pathpy.core.path import PathCollection

# create logger
LOG = logger(__name__)


def read_dataframe(filename: Optional[str] = None,
                   sep: str = ',',
                   header: bool = True,
                   names: Optional[list] = None) -> pd.DataFrame:
    """Read csv database as a pandas data frame."""

    if header:
        frame = pd.read_csv(filename, sep=sep)
    else:
        frame = pd.read_csv(filename, header=0, names=names, sep=sep)

    # return pandas data frame
    return frame


def read_network(filename: Optional[str] = None,
                 loops: bool = True,
                 directed: bool = True,
                 multiedges: bool = False,
                 sep: str = ',',
                 header: bool = True,
                 names: Optional[list] = None,
                 **kwargs: Any) -> Network:
    """Read network from a csv database."""
    # pylint: disable=too-many-arguments

    frame = read_dataframe(filename=filename, sep=sep,
                           header=header, names=names)

    net = to_network(frame, loops=loops, directed=directed,
                     multiedges=multiedges, **kwargs)

    return net


def read_temporal_network(filename: Optional[str] = None,
                          loops: bool = True,
                          directed: bool = True,
                          multiedges: bool = False,
                          sep: str = ',',
                          header: bool = True,
                          names: Optional[list] = None,
                          **kwargs: Any) -> TemporalNetwork:
    """Read temporal network from a csv database."""
    # pylint: disable=too-many-arguments

    frame = read_dataframe(filename=filename, sep=sep,
                           header=header, names=names)

    net = to_temporal_network(frame, loops=loops, directed=directed,
                              multiedges=multiedges, **kwargs)

    return net


def read_pathcollection(filename: str, separator: str = ',',
                        frequency: bool = False, directed: bool = True,
                        maxlines: int = None) -> PathCollection:
    """Read path in edgelist format

    Reads data from a file containing multiple lines of *edges* of the form
    "v,w,frequency,X" (where frequency is optional and X are arbitrary
    additional columns). The default separating character ',' can be changed.

    Parameters
    ----------
    filename : str
        path to edgelist file
    separator : str
        character separating the nodes
    frequency : bool
        is a frequency given? if ``True`` it is the last element in the
        edge (i.e. ``a,b,2``)
    directed : bool
        are the edges directed or undirected
    maxlines : int
        number of lines to read (useful to test large files).
        None means the entire file is read

    """

    from pathpy.core.path import Path, PathCollection

    nodes: dict = {}
    edges: dict = {}
    paths: dict = {}

    with open(filename, 'r') as csv:
        for n, line in enumerate(csv):
            fields = line.rstrip().split(separator)
            assert len(fields) >= 1, 'Error: empty line: {0}'.format(line)

            if frequency:
                path = tuple(fields[:-1])
                freq = float(fields[-1])
            else:
                path = tuple(fields)
                freq = 1.0

            for node in path:
                if node not in nodes:
                    nodes[node] = Node(node)

            if len(path) == 1 and path not in paths:
                paths[path] = Path(nodes[path[0]], frequency=freq)

            else:
                edge_list = []
                for u, v in zip(path[:-1], path[1:]):
                    if (u, v) not in edges:
                        edges[(u, v)] = Edge(nodes[u], nodes[v])
                    edge_list.append(edges[(u, v)])

                if path not in paths:
                    paths[path] = Path(*edge_list, frequency=freq)

            if maxlines is not None and n >= maxlines:
                break

    ncoll = NodeCollection()
    for node in nodes.values():
        ncoll.add(node)

    ecoll = EdgeCollection(nodes=ncoll)
    for edge in edges.values():
        ecoll._add(edge)

    _paths = PathCollection(directed=directed, nodes=ncoll, edges=ecoll)

    for _path in paths.values():
        _paths._add(_path)

    return _paths


def write_dataframe(frame: pd.DataFrame, path_or_buf: Any = None,
                    **pdargs: Any) -> None:
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

        Whether to exclude edge uids in the exported csv file or not
        (default). If this is set to True, each edge between nodes with uids v
        and w will be exported to a line w,v. If this is set to False
        (default), the uid of the edge will be additionally included,
        i.e. exporting v,w,e_uid. The latter ensures that both nodes and edges
        will retain their uids when writing and reading a network with
        pathpy. Excluding edge_uids can be necessary to export edge lists for
        use in third-party packages.

    export_indices: bool

        Whether or not to replace node uids by integer node indices. If False
        (default), string node uids in pp.Network instance will be used. If
        True, node integer indices are exported instead, which may be necessary
        to export edge lists that can be used by third-party packages such as
        node2vec.

    **pdargs:

        Keyword args that will be passed to pandas.DataFrame.to_csv. This
        allows full control of the csv export.

    """
    return frame.to_csv(path_or_buf=path_or_buf, index=False, **pdargs)


def write(network: Union[Network, TemporalNetwork],
          path_or_buf: Any = None,
          exclude_edge_uid: bool = False,
          export_indices: bool = False,
          **pdargs: Any) -> None:
    """Stores all edges including edge attributes in a csv file."""
    frame = to_dataframe(network=network, exclude_edge_uid=exclude_edge_uid,
                         export_indices=export_indices)

    return write_dataframe(frame, path_or_buf=path_or_buf, **pdargs)

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
