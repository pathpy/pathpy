"""Functions to export paths and higher-order models to state files used by InfoMap"""
#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : infomap.py -- Converter classes to infomap
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Tue 2021-04-27 11:12 ingo>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
from typing import Optional
from collections import Counter, OrderedDict

from pathpy import logger

def to_state_file(paths: Counter, file: str, max_memory: int=1) -> None:
    """
    Writes paths from a PathCollection instance into a state file that can be read by InfoMap [1].

    .. [1] M. Rosvall, Daniel Axelsson, Carl T. Bergstrom, "The map equation" The European Physical Journal Special Topics 178.1 (2009): 13-23.

    Parameters
    ----------
    paths : PathCollection
        the PathCollection instance that will be used to generate the state file

    file : str
        Path where the state file will be saved

    max_memory : int=1
        maximum length of memory in state nodes. For default value 1, the maximum memory state node will
        look like "{u}_w". For max_memory=2 we can have "{u-v}_w".

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
    *Vertices 4
    1 "b"
    2 "d"
    3 "a"
    4 "c"
    *States
    1 1 "{a}_b"
    2 4 "{b}_c"
    3 4 "{a-b}_c"
    4 2 "{b-c}_d"
    5 1  "{}_a"
    *Links
    1 2 42
    3 4 41
    5 1 15
    """
    # node set
    nodes = set()    
    for p in paths:
        nodes.update(p)

    state_file = []
    with open(file, mode='w') as f:        
        # total number of nodes traversed by paths
        n = len(nodes)

        # generate list of nodes with 1-based index
        state_file.append('*Vertices {0}'.format(n))

        # sorting is only important that the same state file node indices are generated every time (since dictionaries do not preserve the order). This is only important for unit testing.
        nodes_to_index = OrderedDict( { i[0]: i[1] for i in zip(sorted(nodes), range(1, n+1)) })
        for v in nodes:
            state_file.append('{0} "{1}"'.format(nodes_to_index[v], v))

        # use paths to generate list of state nodes (with 1-based index) as well as links
        state_file.append('*States')
        
        # sorting is only important that the same state file node indices are generated every time (since dictionaries do not preserve the order). This is only important for unit testing.
        states_by_index = OrderedDict()
        states_to_index = OrderedDict()
        links = Counter()
        i = 1
        for p in paths:
            # print(' -> '.join(v for v in p))

            for k in range(len(p)-1):
                current_node = p[k]
                next_node = p[k+1]

                # memory of predecessor = last up to max_order nodes (or empty if first node)
                memory_pred = []
                for j in range(max(0, k-max_memory), k):
                    memory_pred.append(p[j])

                # memory of successor = last up to max_order nodes (or empty if last node)
                memory_succ = []
                if k+1<len(p)-1:
                    for j in range(max(0, k-max_memory+1), k+1):
                        memory_succ.append(p[j])
                
                current_state = '{' + '-'.join(memory_pred) + '}_' + current_node
                next_state = '{' + '-'.join(memory_succ) + '}_' + next_node

                # add state nodes with indices
                if current_state not in states_to_index:
                    states_by_index[i] = (current_node, current_state)
                    states_to_index[current_state] = i
                    i += 1
                if next_state not in states_to_index:
                    states_by_index[i] = (next_node, next_state)
                    states_to_index[next_state] = i
                    i += 1
                links[(current_state, next_state)] += paths[p]
            # for i in range(1, len(p.nodes)):
            #     # extract pair of connected state nodes and associated nodes
            #     node = p.nodes[-2].uid
            #     state = '{' + '-'.join([v.uid for v in p.nodes[:-2]]) + '}_' + node
            #     next_node = p.nodes[-1].uid
            #     next_state = '{' + '-'.join([v.uid for v in p.nodes[i:-1]]) + '}_' + next_node

            #     # add state nodes with indices
            #     if state not in states_to_index:
            #         states_by_index[i] = (node, state)
            #         states_to_index[state] = i
            #         i += 1
            #     if next_state not in states_to_index:
            #         states_by_index[i] = (next_node, next_state)
            #         states_to_index[next_state] = i
            #         i += 1
            #     if weight:
            #         links.append((state, next_state, paths[p][weight]))
            #     else:
            #         links.append((state, next_state))

        for index, item in states_by_index.items():
            state_file.append('{0} {1} "{2}"'.format(index, nodes_to_index[item[0]], item[1]))

        # write links to file
        state_file.append('*Links')
        for l in links:
            state_file.append('{0} {1} {2}'.format(states_to_index[l[0]], states_to_index[l[1]], links[l]))
        f.write('\n'.join(state_file))


def from_state_file(file: str) -> Counter:
    """
    Reads path statistics from a state file
    """ 
    raise NotImplementedError()

