"""Functions to read and write sql database tables."""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : sql.py -- Read and write sql database tables
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Mon 2021-03-29 17:04 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================

from __future__ import annotations
from pathpy.utils.errors import ParameterError
from typing import TYPE_CHECKING, Any, Optional, Union, cast
import sqlite3
import tempfile
import os
import urllib.request
import shutil

from pathpy import logger
from pathpy.io.pandas import to_dataframe, to_network, to_temporal_network

import pandas as pd  # pylint: disable=import-error

# pseudo load class for type checking
if TYPE_CHECKING:
    from pathpy.models.api import Network, TemporalNetwork


# create logger
LOG = logger(__name__)


def read_dataframe(db_file: Optional[str] = None,
                   con: Optional[sqlite3.Connection] = None,
                   uri: Optional[bool] = False,
                   sql: Optional[str] = None,
                   table: Optional[str] = None) -> pd.DataFrame:
    """Read sql database as a pandas data frame. The Database can exists locally or be read from an online ressource.
    
    Parameters
    ----------
    db_file : Optional[str] = ``None``

        The path to the databse file

    con : Optional[sqlite3.Connection] = ``None`` 

        The SQLite3 connection in which the network will be stored

    uri : Optional[bool] = ``False``

        Uniform Resource Identifier for the databse

    sql : Optional[str] = ``None``

        Executable SQL query specify the datas

    table : Optional[str] = ``None``

        Database table to read the data from 
    """

    LOG.debug('Load sql file as pandas data frame.')

    if con is None and db_file is None:
        msg = 'Either an SQL connection or a filename is required'
        LOG.error(msg)
        raise ParameterError(msg)

    con_close = False

    # temporary file for download of DB files
    path = tempfile.mkdtemp()

    # connect to database if not given
    if con is None and db_file is not None:
        con_close = True

        # download Web resources to temporary file
        if db_file.startswith('http://') or db_file.startswith('https://'):

            with urllib.request.urlopen(db_file) as f:
                data = f.read()
                
                file_name = os.path.join(path, 'sqlite.db')
                with open(file_name, 'wb') as dbfile:
                    dbfile.write(data)
            con = sqlite3.connect(file_name)
        else:
            con = sqlite3.connect(db_file, uri=uri)

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
    frame = pd.read_sql(sql, con)

    # close connection to the database
    if con_close:
        _con = cast(sqlite3.Connection, con)
        _con.close()
        try:
            shutil.rmtree(path)
        except IOError:
            pass

    # return pandas data frame
    return frame


def read_network(db_file: Optional[str] = None,
                 loops: bool = True,
                 directed: bool = True,
                 multiedges: bool = False,
                 con: Optional[sqlite3.Connection] = None,
                 sql: Optional[str] = None,
                 table: Optional[str] = None,
                 uri: Optional[bool] = False,
                 **kwargs: Any) -> Network:
    """Read network from a sqlite database.
    
    Parameters
    ----------
    db_file : Optional[str] = ``None``

        The path to the databse file
    
    loops : bool = ``True``

        Does the network have loops

    directed : bool = ``True``

        Is the network directed

    multiedges : bool = ``True``

        Does the network have multiedges

    con : Optional[sqlite3.Connection] = ``None`` 

        The SQLite3 connection in which the network will be stored

    uri : Optional[bool] = ``False``

        Uniform Resource Identifier for the databse

    sql : Optional[str] = ``None``

        Executable SQL query specify the datas

    table : Optional[str] = ``None``

        Database table to read the data from

    """
    # pylint: disable=too-many-arguments

    frame = read_dataframe(db_file=db_file, con=con, sql=sql, table=table, uri=uri)

    net = to_network(frame, loops=loops, directed=directed,
                     multiedges=multiedges, **kwargs)

    return net


def read_temporal_network(db_file: Optional[str] = None,
                          loops: bool = True,
                          directed: bool = True,
                          multiedges: bool = False,
                          con: Optional[sqlite3.Connection] = None,
                          sql: Optional[str] = None,
                          table: Optional[str] = None,
                          **kwargs: Any) -> TemporalNetwork:
    """Read temporal network from a sqlite database."""
    # pylint: disable=too-many-arguments

    frame = read_dataframe(db_file=db_file, con=con, sql=sql, table=table)

    net = to_temporal_network(frame, loops=loops, directed=directed,
                              multiedges=multiedges, **kwargs)

    return net


def write_dataframe(frame: pd.DataFrame,
                    table: str,
                    filename: Optional[str] = None,
                    con: Optional[sqlite3.Connection] = None,
                    **pdargs: Any) -> None:
    """Stores all edges including edge attributes in an sqlite database table.

    Node and network-level attributes are not included.

    Parameters
    ----------
    frame : pd.DataFrame
   
        Source pandas Data Frame to write into SQL

    table: str

        Name of the table in the database in which the network will be stored.

    filename: Optional[str] = ``None``

        The name of the SQLite database in which the network will be stored

    con : Optional[sqlite3.Connection] = ``None``

        The SQLite3 connection in which the network will be stored

    **pdargs:

        Keyword args that will be passed to pandas.DataFrame.to_sql.

    """

    LOG.debug('Store network as sql database.')

    if con is None and filename is None:
        LOG.error('Either an SQL connection or a filename is required')
        raise IOError

    con_close = False

    # connect to database if not given
    if con is None:
        con = sqlite3.connect(cast(str, filename))
        con_close = True

    frame.to_sql(table, con, **pdargs)

    if con_close:
        _con = cast(sqlite3.Connection, con)
        _con.close()


def write(network: Union[Network, TemporalNetwork],
          table: str,
          filename: Optional[str] = None,
          con: Optional[sqlite3.Connection] = None,
          include_edge_uid: bool = False,
          export_indices: bool = False,
          **pdargs: Any) -> None:
    """Stores all edges including edge attributes in a sql file. It stores regular as well as temporal networks.
    
     Parameters
    ----------

    network: Union[Network, TemporalNetwork]

        The network to store in the sqlite database

    table: str

        Name of the table in the database in which the network will be stored.

    filename: str

        The name of the SQLite database in which the network will be stored

    con: sqlite3.Connection

        The SQLite3 connection in which the network will be stored

    include_edge_ui : bool = ``False``

        Whether or not to include a column that stores the uids of the edge objects

    export_indices : bool = ``False``

        Whether or not to use node indices rather than node uids. This is useful to import network data in tools that only support integer node identifiers.

    **pdargs:

        Keyword args that will be passed to pandas.DataFrame.to_sql.
    """
    frame = to_dataframe(network=network, include_edge_uid=include_edge_uid,
                         export_indices=export_indices)

    return write_dataframe(frame, table=table, filename=filename,
                           con=con, **pdargs)
# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
