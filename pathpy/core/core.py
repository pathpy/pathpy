"""Module for core classes of pathpy."""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : core.py -- Core classes of pathpy
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Mon 2021-05-24 09:51 juergen>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
from typing import Any, Optional, Union, Dict
from copy import deepcopy
from collections import defaultdict, Counter
from singledispatchmethod import singledispatchmethod  # NOTE: not needed at 3.9

from pathpy import logger, config

# create logger for the Path class
LOG = logger(__name__)


class PathPyObject:
    """Base class for all pathpy core objects."""

    def __init__(self, uid: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize the base class."""

        # declare variable
        self._uid: str
        self._is_python_uid: bool
        self._attributes: Any

        # assign node identifier
        if uid is not None:
            self._uid = uid
            self._is_python_uid = False
        else:
            self._uid = hex(id(self))
            self._is_python_uid = True

        # update attributes
        self._attributes = kwargs

    def __setitem__(self, key: Any, value: Any) -> None:
        """Add a specific attribute to the object.

        An attribute has a key and the corresponding value expressed as a pair,
        key: value.

        Parameters
        ----------
        key: Any
            Unique identifier for a corrisponding value.

        value: Any
            A value i.e. attribute which is associated with the object.

        Examples
        --------

        Generate new node.

        >>> from pathpy import Node
        >>> u = Node('u')

        Add atribute to the node.

        >>> u['color'] = 'blue'

        """

        self._attributes[key] = value

    def __getitem__(self, key: Any) -> Any:
        """Returns a specific attribute of the object.

        Parameters
        ----------
        key: any
            Key value for the attribute of the object.

        Returns
        -------
        any
            Returns the attribute of the node associated with the given key
            value.

        Raises
        ------
        KeyError
            If no attribute with the assiciated key is defined.

        Examples
        --------

        Generate new node with blue color

        >>> from pathpy import Node
        >>> u = Node('u', color='blue')

        Get the node attribute.

        >>> u['color']
        'blue'

        """
        return self._attributes.get(key, None)

    def __repr__(self) -> str:
        """Return the description of the object.

        Returns
        -------
        str

            Returns the description of the object with the class and assigned
            node uid.

        Examples
        --------
        Genarate new node.

        >>> from pathpy import Node
        >>> u = Node('u')
        >>> print(u)
        Node u

        """
        # declare variable
        string: str

        # check if python id is used as uid or not
        if self._is_python_uid:
            # if python id is used dont show in the object description
            string = super().__repr__()
        else:
            # if user uid is used show in the object description
            string = '{} {}'.format(self.__class__.__name__, self.uid)

        return string

    @property
    def uid(self) -> str:
        """Return the unique identifier (uid) of the object.

        Returns
        -------
        str

            Return the node identifier (uid) as a string.

        Examples
        --------
        Generate a single node and print the uid.

        >>> from pathpy import Node
        >>> u = Node('u')
        >>> u.uid
        u

        """
        return self._uid

    @property
    def attributes(self) -> dict:
        """Return the attributes of the object as a dict.

        Returns
        -------
        dict

            Return the attributes as a dict.

        Examples
        --------
        Generate a single node and print the attribute.

        >>> from pathpy import Node
        >>> u = Node('u', color='red')
        >>> u.attributes['color']
        'red'

        """
        return self._attributes

    def update(self, **kwargs: Any) -> None:
        """Update the attributes of the object.

        Parameters
        ----------
        kwargs : Any
            Attributes to add or update for the object as key=value pairs.

        Examples
        --------

        Generate simple node with attribute.

        >>> from pathpy import Node
        >>> u = Node('u',color='red')
        >>> u.attributes
        {'color': 'red'}

        Update attributes.

        >>> u.update(color='green',shape='rectangle')
        >>> u.attributes
        {'color': 'green', 'shape': 'rectangle'}

        """

        self._attributes.update(**kwargs)

    def copy(self):
        """Return a copy of the node.

        Returns
        -------
        :py:class:`Node`
            A copy of the node.

        Examples
        --------
        >>> from pathpy import Node
        >>> u = Node('u')
        >>> v = u.copy()
        >>> v.uid
        u
        """
        return deepcopy(self)

    def weight(self, weight: str = 'weight', default: float = 1.0) -> float:
        """Returns the weight of the object.

        Per default the attribute with the key 'weight' is used as
        weight. Should there be no such attribute, a new one will be crated
        with weight = 1.0.

        If an other attribute should be used as weight, the option weight has
        to be changed.

        If a weight is assigned but for calculation a weight of 1.0 is needed,
        the weight can be disabled with False or None.

        Parameters
        ----------
        weight : str, optional (default = 'weight')
            The weight parameter defines which attribute is used as weight. Per
            default the attribute 'weight' is used. If `None` or `False` is
            chosen, the weight will be 1.0. Also any other attribute of the
            edge can be used as a weight

        Returns
        -------
        float
            Returns the attribute value associated with the keyword.

        Examples
        --------

        Create new edge and get the weight.

        >>> form pathpy import Edge
        >>> vw = Edge('v','w')
        >>> vw.weight()
        1.0

        Change the weight.

        >>> vw['weight'] = 4
        >>> vw.weight()
        4.0

        >>> vw.weight(False)
        1.0

        Add an attribute and use this as weight.

        >>> vw['length'] = 5
        >>> vw.weight('length')
        5.0

        Create new path and get the weight.

        >>> form pathpy import Path
        >>> p = Path('a','b','c')
        >>> p.weight()
        1.0

        Change the weight.

        >>> p['weight'] = 4
        >>> p.weight()
        4.0

        >>> p.weight(False)
        1.0

        Add an attribute and use this as weight.

        >>> p['length'] = 5
        >>> p.weight('length')
        5.0

        """
        value: float
        weight = False if weight is None else weight

        if not weight:
            value = default
        elif isinstance(weight, str) and weight != 'weight':
            value = float(self.attributes.get(weight, 0.0))
        else:
            value = float(self.attributes.get('weight', default))
        return value


class PathPySet(frozenset):
    """Class to store unordered relationships between objects."""
    def __new__(cls, args):
        """Create a new PathPySet object."""
        # pylint: disable=unused-argument
        return super(PathPySet, cls).__new__(cls, args)


class PathPyTuple(tuple):
    """Class to store un/directed and ordered relationships between objects."""
    def __new__(cls, args, **kwargs):
        """Create a new PathPyTuple object."""
        # pylint: disable=unused-argument
        return super(PathPyTuple, cls).__new__(cls, args)

    def __init__(self, _, directed=False):
        """ Initialize the new tuple class."""
        # pylint: disable=super-init-not-called
        # self._reversed = self[::-1]
        self.directed = directed

    def __hash__(self):
        return super().__hash__() if self.directed else super().__hash__() \
            + hash(self[::-1])

    def __eq__(self, other):
        return super().__eq__(other) if self.directed else super().__eq__(other) \
            or self[::-1] == other

    def __repr__(self):
        return super().__repr__() if self.directed else '|'+super().__repr__()[1:-1]+'|'


class PathPyPath(PathPyObject):
    """Base class for a path."""

    def __init__(self, *args: Union[str, PathPyObject],
                 uid: Optional[str] = None,
                 directed: bool = True,
                 **kwargs: Any) -> None:
        """Initialize the path object."""

        # initialize the parent class
        super().__init__(uid=uid, **kwargs)

        # variable to indicate if path is directed or not
        self._directed: bool = directed

        # a storage containing structure of the objects
        self._relations: PathPyTuple

        # map to the associated objects
        self._objects: dict = dict()

        # if checking is disabled create path directly from args of str
        if not kwargs.pop('checking', True):
            self._relations = PathPyTuple(args, directed=directed)
            self._objects = {uid: None for uid in args}
            return

        # helper variable for path assignment
        _uids = []

        # iterate over args and create structure and map
        for arg in args:
            # check if arg is a str (i.e. an uid)
            if isinstance(arg, (int, str)):
                _uid = arg
                _obj = None

            # check if arg is already a pathpy opject
            elif isinstance(arg, PathPyObject):
                _uid = arg.uid
                _obj = arg

            # if not applicable raise an error
            else:
                LOG.error('All objects must be str or PathPyObject s!')
                raise TypeError

            # temporal storage of the uids
            _uids.append(_uid)

            # create object mapping
            if _uid not in self._objects and _uid != self.uid:
                self._objects[_uid] = _obj

            # if arg uid and self.uid is equal make a self reference
            elif _uid not in self._objects and _uid == self.uid:
                self._objects[_uid] = self

        # save relationships
        self._relations = PathPyTuple(_uids, directed=directed)

    def __len__(self) -> int:
        """Lenght of the object."""
        return len(self.relations) - 1 if self.relations else 0

    def __str__(self) -> str:
        """Print a summary of the object. """
        return self.summary()

    def __contains__(self, item) -> bool:
        """Returns if suppath is in path"""
        return False

    def __iter__(self):
        """Iterates of the Relations"""
        return iter(self._relations)  # PathPyIter(self)

    @property
    def objects(self) -> dict:
        """Return the associated objects. """
        return self._objects

    @property
    def relations(self) -> PathPyTuple:
        """Return the associated relations of the path. """
        return self._relations

    @property
    def depth(self) -> int:
        """Depth of the object."""
        return self.max_depth(self)

    @property
    def directed(self) -> bool:
        """Returns if the object is directed or not."""
        return self._directed

    @directed.setter
    def directed(self, directed: bool) -> None:
        """Set the direction of the path"""
        self._directed = directed
        self._relations.directed = directed

    def items(self):
        """Return a new view of the container’s items ((key, value) pairs)."""
        for key in self.relations:
            yield key, self.objects[key]

    def keys(self):
        """Return a new view of the container’s keys. """
        for key in self.relations:
            yield key

    def values(self):
        """Return a new view of the container’s values."""
        for key in self.relations:
            yield self.objects[key]

    @staticmethod
    def max_depth(item) -> int:
        """Calculate the max depth of the object."""
        # Filter valid objects
        objects = _get_valid_objects(item)
        # if no valid objects are given return 1
        if not objects:
            return 1
        # recursive function  to get the depth
        return 1 + max(PathPyPath.max_depth(child) for child in objects)

    def subobjects(self, depth=None) -> list:
        """Returns the sub objects at a certain depth."""
        objects = _get_valid_objects(self)
        result = [[self.relations]]
        queue = objects

        while queue:
            result.append([node.nodes for node in queue])
            if len(result) == depth and depth:
                break

            level = []
            for node in queue:
                level.extend(_get_valid_objects(node))

            queue = level

        if depth:
            if depth <= len(result):
                result = result[depth-1]
            else:
                result = []
        return result

    def summary(self) -> str:
        """Returns a summary of the object. """

        summary = [
            'Uid:\t\t{}\n'.format(self.uid),
            'Type:\t\t{}\n'.format(self.__class__.__name__),
        ]

        return ''.join(summary)


class PathPyCollection():
    """Base collection for PathPyObjects"""

    def __init__(self, *args, **kwargs):

        # dict to store the PathPyObjects {uid:PathPyObject}
        self._store: dict = dict()

        # dict to store child objects {child.uid:child.PathPyObject}
        self._objects: dict = dict()

        # mapping between the child and the parten {child.uid: {parten.uids}}
        self._mapping: defaultdict = defaultdict(set)

        # initialize object counter
        self._counter: Counter = Counter()

        # enable indexing of the structures
        self._indexed: bool = kwargs.pop('indexed', True)

        # inidcator whether the network is directed or undirected
        self._directed: bool = kwargs.pop('directed', True)

        # indicator if multipaths/edges are allowed
        self._multiple: bool = kwargs.pop('multiple', False)

        # dict to store the relationships between objects
        # IMPORTANT key has to be hashable
        # i.e. if the structure changes the mapping has to be updated
        self._relations: defaultdict = defaultdict(set)

        # class of objects to be stored
        self._default_class: Any = PathPyPath

    @singledispatchmethod
    def __getitem__(self, key):
        return None

    @__getitem__.register(str)  # type: ignore
    def _(self, key):
        return self._store[key]

    @__getitem__.register(PathPyObject)  # type: ignore
    def _(self, key):
        return self._store[key.uid]

    @__getitem__.register(tuple)  # type: ignore
    def _(self, key):
        new = tuple(k.uid if isinstance(k, PathPyObject) else k for k in key)
        values = {self._store[uid] for uid in self._relations[
            PathPyTuple(new, directed=self.directed)]}
        return values if self._multiple else next(iter(values))

    def __setitem__(self, key, value):
        self._store[key] = value

    def __delitem__(self, key):
        del self._store[key]

    def __iter__(self):
        return self._store.values().__iter__()

    def __len__(self):
        return len(self._store)

    def __repr__(self):
        return set(self._store.values()).__repr__()

    def __str__(self) -> str:
        return set(self._store.values()).__str__()

    def __eq__(self, other) -> bool:
        """Return if two collections are equal"""
        return self._store == other._store

    @singledispatchmethod
    def __contains__(self, item) -> bool:
        """Returns if item is in edges."""
        return False

    @__contains__.register(PathPyObject)  # type: ignore
    def _(self, item: PathPyObject) -> bool:
        return item in self._store.values()

    @__contains__.register(str)  # type: ignore
    def _(self, item: str) -> bool:
        return item in self._store.keys()

    @__contains__.register(tuple)  # type: ignore
    def _(self, item: tuple) -> bool:
        new = tuple(k.uid if isinstance(k, PathPyObject) else k for k in item)
        return PathPyTuple(new, directed=self.directed) in self._relations

    def items(self):
        """Return a new view of the container’s items ((key, value) pairs)."""
        return self._store.items()

    def keys(self):
        """Return a new view of the container’s keys. """
        return self._store.keys()

    def values(self):
        """Return a new view of the container’s values."""
        return self._store.values()

    def pop(self, key, default: Any = KeyError) -> Any:
        """Pop item form dict"""
        self._store.pop(key, default)

    @property
    def uids(self) -> set:
        """Return the associated uids. """
        return set(self.keys())

    @property
    def directed(self) -> bool:
        """Return if the collection is directed. """
        return self._directed

    @property
    def counter(self) -> Counter:
        """Return a counter of the objects. """
        return self._counter

    @property
    def index(self) -> Dict[str, int]:
        """Returns a dictionary that maps object uids to  integer indices.

        The indices of nodes correspond to the row/column ordering of objects
        in any list/array/matrix representation generated by pathpy, e.g. for
        degrees.sequence or adjacency_matrix.

        Returns
        -------
        dict
            maps node uids to zero-based integer index

        """
        return dict(zip(self._store, range(len(self))))

    @property
    def nodes(self) -> dict:
        """Return the associated objects (i.e. nodes). """
        return self._objects

    @singledispatchmethod
    def add(self, *args, **kwargs) -> None:
        """Add objects"""
        # pylint: disable=no-self-use
        # pylint: disable=unused-argument
        raise NotImplementedError

    @add.register(PathPyObject)  # type: ignore
    def _(self, *args: PathPyObject, **kwargs: Any) -> None:
        """Add object to collection"""

        for obj in args:

            # check if object exists already
            if obj not in self.values() and obj.uid not in self.keys():

                # update attributes
                if kwargs:
                    obj.update(**kwargs)

                # add edge to the collection
                self._add(obj, **kwargs)
            else:
                self._if_exist(obj, **kwargs)

    @add.register(PathPyPath)  # type: ignore
    def _(self, *args: PathPyPath, **kwargs: Any) -> None:
        for obj in args:

            # check if object exists already
            if obj not in self.values() and obj.uid not in self.keys():
                if obj.relations not in self or self._multiple:
                    if kwargs:
                        obj.update(**kwargs)

                    self._add(obj, **kwargs)
                else:
                    self._if_exist(obj, **kwargs)
            else:
                self._if_exist(obj, **kwargs)

    @add.register(str)  # type: ignore
    @add.register(int)  # type: ignore
    def _(self, *args: Union[str, int], **kwargs: Any) -> None:

        # get additional parameters
        uid: Optional[str] = kwargs.pop('uid', None)

        # check if all objects are str
        if not all(isinstance(arg, (str, int)) for arg in args):
            LOG.error('All objects have to be str objects!')
            raise TypeError

        obj = self._default_class(
            *args, uid=uid, directed=self.directed, **kwargs)
        self.add(obj, **kwargs)

    @singledispatchmethod
    def _add(self, obj: Any, **kwargs: Any) -> None:
        """Add an edge to the set of edges."""
        raise NotImplementedError

    @_add.register(PathPyObject)  # type: ignore
    def _(self, obj: PathPyObject, **kwargs: Any) -> None:
        self[obj.uid] = obj
        self.counter[obj.uid] += kwargs.get(
            config['attributes']['frequency'], 1)

    @_add.register(PathPyPath)  # type: ignore
    def _(self, obj: PathPyObject, **kwargs: Any) -> None:
        self[obj.uid] = obj

        self.counter[obj.uid] += kwargs.get(
            config['attributes']['frequency'], 1)

        for key, value in obj.objects.items():
            if key not in self._objects or \
                    (self._objects[key] is None and value is not None):
                self._objects[key] = value

        if self._indexed:
            for uid in obj.objects:
                self._mapping[uid].add(obj.uid)

            self._relations[obj.relations].add(obj.uid)

    def _if_exist(self, obj: Any, **kwargs: Any) -> None:
        """Helper function if the edge does already exsist."""
        # pylint: disable=no-self-use
        # pylint: disable=unused-argument
        uid = self[obj.relations].uid
        self.counter[uid] += kwargs.get(config['attributes']['frequency'], 1)
        # LOG.error('The object "%s" already exists in the Collection', obj)
        # raise KeyError

    @singledispatchmethod
    def remove(self, *args, **kwargs) -> None:
        """Remove objects"""
        # pylint: disable=no-self-use
        # pylint: disable=unused-argument
        raise NotImplementedError

    @remove.register(PathPyObject)  # type: ignore
    def _(self, *args: PathPyObject, **kwargs: Any) -> None:
        """Remove object from the collection"""
        # pylint: disable=unused-argument
        for obj in args:

            # check if object exists already
            if obj in self.values() and obj.uid in self.keys():
                self._remove(obj)

    @remove.register(str)  # type: ignore
    def _(self, *args: str, **kwargs: Any) -> None:
        """Remove object from the collection"""

        # check if more then one object is given raise an AttributeError
        if len(args) == 1:
            # check if object exists already
            if args[0] in self.keys():
                self._remove(self[args[0]], **kwargs)
        elif len(args) > 1 and args in self:
            for obj in list(self[args]):
                self.remove(obj)
        else:
            LOG.warning('No edge was removed!')

    @singledispatchmethod
    def _remove(self, obj) -> None:
        """Add an edge to the set of edges."""
        raise NotImplementedError

    @_remove.register(PathPyObject)  # type: ignore
    def _(self, obj: PathPyObject) -> None:
        """Add an edge to the set of edges."""
        self.pop(obj.uid, None)
        self.counter.pop(obj.uid, None)

    @_remove.register(PathPyPath)  # type: ignore
    def _(self, obj: PathPyPath) -> None:
        """Add an edge to the set of edges."""
        self.pop(obj.uid, None)
        self.counter.pop(obj.uid, None)

        if self._indexed:
            for uid in obj.objects:
                self._mapping[uid].discard(obj.uid)
                if len(self._mapping[uid]) == 0:
                    self._mapping.pop(uid, None)
                    self._objects.pop(uid, None)

            self._relations[obj.relations].discard(obj.uid)
            if len(self._relations[obj.relations]) == 0:
                self._relations.pop(obj.relations, None)


def _get_valid_objects(item) -> list:
    """Helper function to return a list with valid objects"""
    return [obj for obj in item.objects.values()
            if (isinstance(obj, PathPyPath) and obj.uid != item.uid)]


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
