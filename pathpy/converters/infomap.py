"""Converter to read paths and higher-order models in infomap"""
#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : infomap.py -- Converter classes to infomap
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Mon 2021-04-19 15:55 ingo>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
from typing import Optional

from pathpy import logger
from pathpy.core.api import PathCollection

def to_state_file(paths: PathCollection, file: str, weight: Optional[str]=None) -> None:
    """
    Writes path statistics into a state file that can be read by InfoMap

    Parameters
    ----------
        paths : PathCollection
            the PathCollection instance that will be used to generate the state file

        file : str
            Path where the state file will be saved

        weight : Optional[str]=None
            if not None (default), the given path attribute will be used to set link weights in the state file

    Examples
    --------
    Create a state file from a PathCollection with three paths

    >>> pc = pp.PathCollection()
    >>> a = pp.Node('a')
    >>> b = pp.Node('b')
    >>> c = pp.Node('c')
    >>> d = pp.Node('d')

    >>> e1 = pp.Edge(a, b, uid='a-b')
    >>> e2 = pp.Edge(b, c, uid='b-c')
    >>> e3 = pp.Edge(c, d, uid='c-d')

    >>> pc.add(pp.Path(e1, frequency=15))
    >>> pc.add(pp.Path(e1, e2, frequency=42))
    >>> pc.add(pp.Path(e1, e2, e3, frequency=41))

    >>> pp.converters.to_state_file(pc, 'paths.state', weight='frequency')
    >>> with open('test.state', 'r') as f:
    >>> print(f.read())

    >>> *Vertices 4
    >>> 1 "b"
    >>> 2 "d"
    >>> 3 "a"
    >>> 4 "c"
    >>> *States
    >>> 1 1 "a b"
    >>> 2 4 "b c"
    >>> 3 4 "a b c"
    >>> 4 2 "b c d"
    >>> *Links
    >>> 1 2 42
    >>> 3 4 41
    """
    state_file = []
    with open(file, mode='w') as f:        
        # total number of nodes traversed by paths
        n = len(paths.nodes)

        # generate list of nodes with 1-based index
        state_file.append('*Vertices {0}'.format(n))
        nodes_to_index = { i[0]: i[1] for i in zip(paths.nodes.uids, range(1, n+1)) }
        for v in paths.nodes.uids:
            state_file.append('{0} "{1}"'.format(nodes_to_index[v], v))

        # use paths to generate list of state nodes (with 1-based index) as well as links
        state_file.append('*States')
        states_by_index = {}
        states_to_index = {}
        links = []
        i = 1
        for p in paths:
            if len(p.edges)>1:
                # extract pairs of connected state nodes as well as associated nodes
                node = p.nodes[-2].uid
                state = '{' + '-'.join([v.uid for v in p.nodes[:-2]]) + '}_' + node
                next_node = p.nodes[-1].uid
                next_state = '{' + '-'.join([v.uid for v in p.nodes[1:-1]]) + '}_' + next_node

                # add state nodes with indices
                if state not in states_to_index:
                    states_by_index[i] = (node, state)
                    states_to_index[state] = i
                    i += 1
                if next_state not in states_to_index:
                    states_by_index[i] = (next_node, next_state)
                    states_to_index[next_state] = i
                    i += 1
                if weight:
                    links.append((state, next_state, paths[p][weight]))
                else:
                    links.append((state, next_state))

        for index, item in states_by_index.items():
            state_file.append('{0} {1} "{2}"'.format(index, nodes_to_index[item[0]], item[1]))

        # write links to file
        state_file.append('*Links')
        for l in links:
            if weight:
                state_file.append('{0} {1} {2}'.format(states_to_index[l[0]], states_to_index[l[1]], l[2]))
            else:
                state_file.append('{0} {1}'.format(states_to_index[l[0]], states_to_index[l[1]]))
        f.write('\n'.join(state_file))


def from_state_file(file: str) -> PathCollection:
    """
    Reads path statistics from a state file
    """ 
    raise NotImplementedError()

