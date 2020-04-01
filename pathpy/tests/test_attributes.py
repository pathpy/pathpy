#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_attributes.py -- Test environment for the attributes
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2019-11-14 15:52 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================

import pytest

from pathpy.core.base import Attributes
import pathpy as pp


def test_basic():
    """Test some basic functions."""
    a = Attributes()

    assert a.uid is None
    assert len(a.data[0]) == 0

    a = Attributes(uid='a')

    assert a.uid == 'a'

    a = Attributes(A='x')

    assert len(a.data[0]) == 1
    assert a.data[0]['A'] == 'x'


def test_update():
    """Test to update the attributes."""

    # empty attributes
    a = Attributes()

    # no update
    a.update()

    assert len(a.data) == 1
    assert len(a.data[0]) == 0

    # empty attributes
    a = Attributes()

    a.update(A='x', B='y')

    assert a.data[0]['A'] == 'x'
    assert a.data[0]['B'] == 'y'
    assert len(a.data) == 1
    assert len(a.data[0]) == 2

    # initial attributes
    a = Attributes(A='a')

    # no update
    a.update()

    assert a.data[0]['A'] == 'a'
    assert len(a.data) == 1
    assert len(a.data[0]) == 1

    # initial attributes
    a = Attributes(A='a')

    a.update(A='x', B='y')

    assert a.data[0]['A'] == 'a'
    assert a.data[1]['A'] == 'x'
    assert a.data[1]['B'] == 'y'
    assert len(a.data) == 2
    assert len(a.data[0]) == 1
    assert len(a.data[1]) == 2

    # empty attributes
    a = Attributes()

    # update uid
    a.update(uid='a')

    assert a.uid == 'a'
    assert len(a.data) == 1
    assert len(a.data[0]) == 0

    # initial uids and attributes
    a = Attributes(uid='a', A='a')

    # update uid
    a.update(uid='b')

    assert a.uid == 'b'
    assert len(a.data) == 1
    assert len(a.data[0]) == 1
    assert a.data[0]['A'] == 'a'


def test_set_single_value():
    """Test to set a singel value."""

    a = Attributes()

    a._set_single_value('A', 'a')

    assert len(a.data) == 1
    assert len(a.data[0]) == 1
    assert a.data[0]['A'] == 'a'

    # update single value with __setitem__
    a['A'] = 'x'

    assert len(a.data) == 2
    assert len(a.data[0]) == 1
    assert a.data[1]['A'] == 'x'

    # add new single value with __setitem__
    a['B'] = 'y'

    assert len(a.data) == 3
    assert len(a.data[2]) == 2
    assert a.data[2]['B'] == 'y'


def test_get_singel_value():
    """Test to get a single value."""

    a = Attributes(A='x')

    assert a['A'] == 'x'
    assert a['B'] is None

    a['B'] = 'y'

    assert a['A'] == 'x'
    assert a['B'] == 'y'


def test_get():
    """Test to get a value."""

    a = Attributes(A='x')
    assert a.get('A') == 'x'
    assert a.get('B') is None
    assert a.get('C', 1) == 1


def test_history():
    """Test the attribute history."""

    pp.config['attributes']['history'] = False

    a = Attributes(A=1)
    a['A'] = 2
    a['A'] = 3
    a['A'] = 4
    pp.config['attributes']['history'] = True

    assert len(a.data) == 1
    assert len(a.data[0]) == 1
    assert a.data[0]['A'] == 4

    a = Attributes(A=1, history=False)
    a['A'] = 2
    a['A'] = 3
    a['A'] = 4

    assert len(a.data) == 1
    assert len(a.data[0]) == 1
    assert a.data[0]['A'] == 4

    a = Attributes(A=1, history=True)
    a['A'] = 2
    a['A'] = 3
    a['A'] = 4

    assert len(a.data) == 4
    assert len(a.data[3]) == 1
    assert a.data[3]['A'] == 4


def test_repr():
    """Test the print function."""

    a = Attributes(A=1, multi_attributes=False)

    assert a.__repr__() == "{'A': 1}"


def test_eq():
    """Test if two attributes are equal."""

    # multi_attributes are disalbed

    a = Attributes(A=1)
    b = Attributes(A=1)

    assert a == b

    c = Attributes(C=1)

    assert a != c

    b['A'] = 2

    assert a != b

    a['A'] = 3
    a['A'] = 2

    assert a == b

    # multi_attributes are enabled

    a = Attributes(A=1, multi_attributes=True)
    b = Attributes(A=1, multi_attributes=True)

    assert a == b

    c = Attributes(C=1)

    assert a != c

    b['A'] = 2

    assert a != b

    a['A'] = 3
    a['A'] = 2

    assert a != b


def test_to_dict():
    """Test conversion to dict."""

    a = Attributes(A=1)
    a['B'] = 2

    d = a.to_dict()

    assert isinstance(d, dict)
    assert len(d) == 2
    assert 'A' and 'B' in d
    assert d['A'] == 1
    assert d['B'] == 2

    a = Attributes(A=1, multi_attributes=True)
    a['B'] = 2

    d = a.to_dict(transpose=True)

    assert isinstance(d, dict)
    assert len(d) == 2
    assert 'A' and 'B' in d
    assert isinstance(d['A'], dict)
    assert isinstance(d['B'], dict)
    assert d['A'] == {0: 1, 1: 1}
    assert d['A'][0] == 1
    assert d['B'] == {1: 2}

    a = Attributes(A=1, multi_attributes=True)
    a['B'] = 2

    d = a.to_dict(transpose=False)

    assert isinstance(d, dict)
    assert len(d) == 2
    assert len(d[0]) == 1
    assert len(d[1]) == 2
    assert isinstance(d[0], dict)
    assert isinstance(d[1], dict)
    assert d[0] == {'A': 1}
    assert d[1] == {'A': 1, 'B': 2}

    a = Attributes(A=1, multi_attributes=True)
    a['B'] = 2
    a['C'] = 2

    #d = a.to_dict('A', 'C', exclude=['C'], transpose=True)
    d = a.to_dict('A', 'C', exclude=['B'], transpose=False)

    print(d)


def test_data_frame():
    """Test export to data frame."""

    a = Attributes(A=1, multi_attributes=False)
    a['A'] = 2
    a['B'] = 'a'
    a['A'] = 3
    a['C'] = 2
    # a.update(A=4, B=4, C=4)
    # print(a.data)
    # print(a)
    # print(a.data_frame(history=True))


def test_frequency():
    """Test the frequency of the object."""
    pass

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
