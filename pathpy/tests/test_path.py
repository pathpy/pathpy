# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_path.py -- Test environment for the Path class
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2020-05-14 12:09 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================

import pytest

from pathpy import Edge, Node, Path
from pathpy.core.path import PathCollection


def test_path():
    """Test basic path"""
    a = Node('a')
    b = Node('b')
    c = Node('c')
    e = Edge(a, b)
    f = Edge(b, c)

    p = Path(e, f)


def test_PathCollection():
    """Test the paths object"""
    a = Node('a')
    b = Node('b')
    c = Node('c')
    e = Edge(a, b, uid='e')
    f = Edge(b, c, uid='f')

    p1 = Path(e, f, uid='p1')
    p2 = Path(e, uid='p2')
    p3 = Path(a, uid='p3')

    paths = PathCollection()
    paths.add(p1)
    paths.add(p2)
    paths.add(p3)

    with pytest.raises(Exception):
        paths.add(p1)

    assert len(paths.nodes) == 3
    assert len(paths.edges) == 2
    assert len(paths) == 3
    assert p1 in paths
    assert p2 in paths
    assert p3 in paths

    assert 'p1' in paths
    assert 'p2' in paths
    assert 'p3' in paths

    assert (e, f) in paths
    assert ('e', 'f') in paths
    assert [e] in paths
    assert ['e'] in paths

    assert(a, b, c) in paths
    assert('a', 'b', 'c') in paths
    assert(a, b) in paths
    assert('a', 'b') in paths

    assert (a,) in paths
    assert ('a', ) in paths
    assert [a] in paths
    assert ['a'] in paths

    # print(paths['p1'] == p1)
    #print(paths[p1] == p1)

    assert paths['a', 'b', 'c'] == p1
    assert paths['e', 'f'] == p1

    with pytest.raises(Exception):
        p = paths['x', 'y']

    g = Edge(b, c, uid='a')
    p4 = Path(g, uid='p4')
    paths.add(p4)

    # issue warning
    assert ['a'] in paths

    paths = PathCollection()
    paths.add(a, b)

    with pytest.raises(Exception):
        paths.add(a, b)

    paths = PathCollection()
    paths.add('a', 'b', 'c', uid='a-b-c')

    assert len(paths) == 1
    assert 'a-b-c' in paths
    assert 'a' and 'b' and 'c' in paths.nodes
    assert ('a', 'b') and ('b', 'c') in paths.edges

    paths = PathCollection()
    paths.add(p1, p2)

    assert len(paths) == 2

    paths = PathCollection()
    paths.add(('a', 'b', 'c'), ('a', 'b'))

    assert len(paths.nodes) == 3
    assert len(paths.edges) == 2
    assert len(paths) == 2

    paths = PathCollection()
    paths.add(e, f, uid='p1')

    assert len(paths) == 1
    assert len(paths.edges) == 2
    assert len(paths.nodes) == 3

    assert (e, f) in paths
    assert ('a', 'b', 'c') in paths

    with pytest.raises(Exception):
        paths.add(f, e, uid='p2')

    paths = PathCollection()
    paths.add('e1', uid='p1', nodes=False)

    assert len(paths) == 1
    assert len(paths.edges) == 1
    assert len(paths.nodes) == 2
    assert 'p1' in paths
    assert 'e1' in paths.edges

    paths = PathCollection()
    paths.add('e1', 'e2', uid='p1', nodes=False)

    assert len(paths) == 1
    assert len(paths.edges) == 2
    assert len(paths.nodes) == 3
    assert 'p1' in paths
    assert 'e1' and 'e2' in paths.edges

    assert paths.edges['e1'].w == paths.edges['e2'].v

    paths = PathCollection()
    paths.add(('e1', 'e2'), ('e3', 'e4'), nodes=False)

    assert len(paths.nodes) == 6
    assert len(paths.edges) == 4
    assert len(paths) == 2

    paths = PathCollection()
    paths.add(p1, p2, p3)

    assert len(paths.nodes) == 3
    assert len(paths.edges) == 2
    assert len(paths) == 3

    paths.remove(p3)
    assert len(paths.nodes) == 3
    assert len(paths.edges) == 2
    assert len(paths) == 2
    assert p3 not in paths

    paths.remove('p1')
    assert len(paths.nodes) == 3
    assert len(paths.edges) == 2
    assert len(paths) == 1
    assert p1 not in paths

    paths = PathCollection()
    paths.add(('a', 'b', 'c'), ('a', 'b'))

    assert len(paths) == 2

    paths.remove('a', 'b')

    assert len(paths) == 1

    paths = PathCollection()
    paths.add(('a', 'b'), ('b', 'c'), ('c', 'd'))
    paths.remove(('a', 'b'), ('b', 'c'))

    assert len(paths) == 1
    assert ('a', 'b') not in paths
    assert ('b', 'c') not in paths
    assert ('c', 'd') in paths

    paths = PathCollection()
    paths.add(('e1', 'e2'), ('e2', 'e3'), ('e3', 'e4'), nodes=False)

    assert len(paths) == 3
    assert len(paths.edges) == 4

    paths.remove('e1', 'e2')
    assert len(paths) == 2

    paths.remove(('e2', 'e3'), ('e3', 'e4'))
    assert len(paths) == 0

    paths = PathCollection()
    paths.add('a', 'b', uid='p1')
    paths.add('b', 'c', uid='p2')
    paths.add('c', 'd', uid='p3')
    paths.add('d', 'e', uid='p4')

    assert len(paths) == 4

    paths.remove('p1')

    assert len(paths) == 3

    paths.remove('p2', 'p3')

    assert len(paths) == 1


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
