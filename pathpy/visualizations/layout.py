#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : layout.py -- Module to layout the network
# Author    : Juergen Hackl <hackl@ibi.baug.ethz.ch>
# Creation  : 2018-07-26
# Time-stamp: <Mon 2019-12-16 13:15 juergen>
#
# Copyright (c) 2018 Juergen Hackl <hackl@ibi.baug.ethz.ch>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# =============================================================================
import numpy as np
from .. import logger

log = logger(__name__)


def layout(network, **kwds):
    """Function to generate a layout for the network.

    This function genearates a layout configuration for the nodes in the
    network. Thereby, different layouts and options can be chosen. The layout
    function is directly included in the plot function or can be separately
    called.

    The layout function supports different network types and layout algorithm.
    Currently supported networks are:

    * 'cnet',
    * 'networkx',
    * 'igraph',
    * 'pathpy'
    * node/edge list

    Currently supported algorithms are:

    * Fruchterman-Reingold force-directed algorithm
    * Uniformly at random node positions

    The appearance of the layout can be modified by keyword arguments which will
    be explained in more detail below.

    Parameters
    ----------

    network : network object
        Network to be drawn. The network can be a 'cnet', 'networkx', 'igraph',
        'pathpy' object, or a tuple of a node list and edge list.

    kwds : keyword arguments, optional (default= no attributes)
        Attributes used to modify the appearance of the layout.
        For details see below.


    Keyword arguments used for the layout:

    **Layout:**

    NOTE: All layout arguments can be entered with or without 'layout_' at the
    beginning, e.g. 'layout_iterations' is equal to 'iterations'

    - ``layout`` : dict or string , optional (default = None)
      A dictionary with the node positions on a 2-dimensional plane. The
      key value of the dict represents the node id while the value
      represents a tuple of coordinates (e.g. n = (x,y)). The initial
      layout can be placed anywhere on the 2-dimensional plane.

      Instead of a dictionary, the algorithm used for the layout can be defined
      via a string value. Currently, supported are:

      * Random layout, where the nodes are uniformly at random placed in the
        unit square. This algorithm can be enabled with the keywords: 'Random',
        'random', 'rand', or None

      * Fruchterman-Reingold force-directed algorithm. In this algorithm, the
        nodes are represented by steel rings and the edges are springs between
        them. The attractive force is analogous to the spring force and the
        repulsive force is analogous to the electrical force. The basic idea is
        to minimize the energy of the system by moving the nodes and changing
        the forces between them. This algorithm can be enabled with the
        keywords: 'Fruchterman-Reingold', 'fruchterman_reingold', 'fr',
        'spring_layout', 'spring layout', 'FR'

        ==================== ==================================================
        Algorithms           Keywords
        ==================== ==================================================
        Random               Random, random, rand, None
        Fruchterman-Reingold Fruchterman-Reingold, fruchterman_reingold, fr
                             spring_layout, spring layout, FR
        ==================== ==================================================

    - ``force`` : float, optional (default = None)
      Optimal distance between nodes.  If None the distance is set to
      1/sqrt(n) where n is the number of nodes.  Increase this value to move
      nodes farther apart.

    - ``positions`` : dict or None  optional (default = None)
      Initial positions for nodes as a dictionary with node as keys and values
      as a coordinate list or tuple.  If None, then use random initial
      positions.

    - ``fixed`` : list or None, optional (default = None)
      Nodes to keep fixed at initial position.

    - ``iterations`` : int, optional (default = 50)
      Maximum number of iterations taken

    - ``threshold``: float, optional (default = 1e-4)
      Threshold for relative error in node position changes.  The iteration
      stops if the error is below this threshold.

    - ``weight`` : string or None, optional (default = None)
      The edge attribute that holds the numerical value used for the edge
      weight.  If None, then all edge weights are 1.

    - ``dimension`` : int, optional (default = 2)
      Dimension of layout. Currently, only plots in 2 dimension are supported.

    - ``seed`` : int or None, optional (default = None)
      Set the random state for deterministic node layouts. If int, `seed` is
      the seed used by the random number generator, if None, the a random seed
      by created by the numpy random number generator is used.

    In the layout style dictionary multiple keywords can be used to address
    attributes. These keywords will be converted to an unique key word,
    used in the remaining code.

    ========= =================================
    keys      other valid keys
    ========= =================================
    fixed     fixed_nodes, fixed_vertices,
              fixed_n, fixed_v
    positions initial_positions, node_positions
              vertex_positions, n_positions,
              v_positions
    ========= =================================

    Examples
    --------

    For illustration purpose a similar network as in the python-igrap tutorial
    is used. Instead of igraph, the cnet module is used for creating the
    network.

    Create an empty network object, and add some edges.

    >>> net = Network(name = 'my tikz test network',directed=True)
    >>> net.add_edges_from([('ab','a','b'), ('ac','a','c'), ('cd','c','d'),
    >>>                     ('de','d','e'), ('ec','e','c'), ('cf','c','f'),
    >>>                     ('fa','f','a'), ('fg','f','g'),('gg','g','g'),
    >>>                     ('gd','g','d')])

    Now a layout can be generated:

    >>> layout(net)
    {'b': array([0.88878309, 0.15685131]), 'd': array([0.4659341 , 0.79839535]),
    'c': array([0.60386662, 0.40727962]), 'e': array([0.71073353, 0.65608203]),
    'g': array([0.42663927, 0.47412449]), 'f': array([0.48759769, 0.86787594]),
    'a': array([0.84154488, 0.1633732 ])}

    Per default, the node positions are assigned uniform random. In order to
    create a layout, the layout methods of the packages can be used, or the
    position of the nodes can be directly assigned, in form of a dictionary,
    where the key is the node id and the value is a tuple of the node position
    in x and y.

    Let us generate a force directed layout (e.g. Fruchterman-Reingold):

    >>> layout(net, layout='fr')
    {'g': array([-0.77646408,  1.71291126]), 'c': array([-0.18639655,0.96232326]),
    'f': array([0.33394308, 0.93778681]), 'e': array([0.09740098, 1.28511973]),
    'a': array([1.37933158, 0.23171857]), 'b': array([ 2.93561876,-0.46183461]),
    'd': array([-0.29329793,  1.48971303])}

    Note, instead of the command ``fr`` also the command
    ``Fruchterman-Reingold`` or any other command mentioned above can be
    used. For more information see table above.

    In order to keep the properties of the layout for your network separate from
    the network itself, you can simply set up a Python dictionary containing the
    keyword arguments you would pass to :py:meth:`layout` and then use the
    double asterisk (**) operator to pass your specific layout attributes to
    :py:meth:`layout`:

    >>> layout_style = {}
    >>> layout_style['layout'] = 'Fruchterman-Reingold'
    >>> layout_style['seed'] = 1
    >>> layout_style['iterations'] = 100
    >>> layout(net,**layout_style)
    {'d': array([-0.31778276, 1.78246882]), 'f': array([-0.8603259, 0.82328291]),
    'c': array([-0.4423771 , 1.21203895]), 'e': array([-0.79934355, 1.49000119]),
    'g': array([0.43694799, 1.51428788]), 'a': array([-2.15517293, 0.23948823]),
    'b': array([-3.84803812, -0.71628417])}

    """
    # initialize variables
    _weight = kwds.get('weight', None)
    if _weight is None:
        _weight = kwds.get('layout_weight', None)

    # check type of network
    if 'cnet' in str(type(network)):
        # log.debug('The network is of type "cnet".')
        nodes = list(network.nodes)
        adjacency_matrix = network.adjacency_matrix(weight=_weight)

    elif 'networkx' in str(type(network)):
        # log.debug('The network is of type "networkx".')
        nodes = list(network.nodes())
        import networkx as nx
        adjacency_matrix = nx.adjacency_matrix(network, weight=_weight)
    elif 'igraph' in str(type(network)):
        # log.debug('The network is of type "igraph".')
        nodes = list(range(len(network.vs)))
        from scipy.sparse import coo_matrix
        A = np.array(network.get_adjacency(attribute=_weight).data)
        adjacency_matrix = coo_matrix(A)
    elif 'pathpy' in str(type(network)):
        # log.debug('The network is of type "pathpy".')
        nodes = list(network.nodes)
        if _weight is not None:
            _w = True
        else:
            _w = False
        adjacency_matrix = network.adjacency_matrix(weighted=_w)
    # elif isinstance(network, tuple):
    #     # log.debug('The network is of type "list".')
    #     nodes = network[0]
    #     from collections import OrderedDict
    #     edges = OrderedDict()
    #     for e in network[1]:
    #         edges[e] = e

    else:
        log.error('Type of the network could not be determined.'
                  ' Currently only "cnet", "networkx","igraph", "pathpy"'
                  ' and "node/edge list" is supported!')
        raise NotImplementedError

    # create layout class
    layout = Layout(nodes, adjacency_matrix, **kwds)
    # return the layout
    return layout.generate_layout()


class Layout(object):
    """Default class to create layouts

    The :py:class:`Layout` class is used to generate node a layout drawer and
    return the calculated node positions as a dictionary, where the keywords
    represents the node ids and the values represents a two dimensional tuple
    with the x and y coordinates for the associated nodes.

    Parameters
    ----------
    nodes : list with node ids
        The list contain a list of unique node ids.

    attr : keyword arguments, optional (default = no attributes)
        Attributes to add to node as key=value pairs.
        See also :py:meth:`layout`

    See Also
    --------
    layout

    """

    def __init__(self, nodes, adjacency_matrix, **attr):
        """Initialize the Layout class

        The :py:class:`Layout` class is used to generate node a layout drawer
        and return the calculated node positions as a dictionary, where the
        keywords represents the node ids and the values represents a two
        dimensional tuple with the x and y coordinates for the associated nodes.

        Parameters
        ----------
        nodes : list with node ids
            The list contain a list of unique node ids.

        attr : keyword arguments, optional (default = no attributes)
            Attributes to add to node as key=value pairs.
            See also :py:meth:`layout`

        """

        # initialize variables
        self.nodes = nodes
        self.adjacency_matrix = adjacency_matrix

        # rename the attributes
        attr = self.rename_attributes(**attr)

        # options for the layouts
        self.layout_type = attr.get('layout', None)
        self.k = attr.get('force', None,)
        self.fixed = attr.get('fixed', None)
        self.iterations = attr.get('iterations', 50)
        self.threshold = attr.get('threshold', 1e-4)
        self.weight = attr.get('weight', None)
        self.dimension = attr.get('dimension', 2)
        self.seed = attr.get('seed', None)
        self.positions = attr.get('positions', None)

        # TODO: allow also higher dimensional layouts
        if self.dimension != 2:
            log.warning('Currently only plots with dimension 2 are supported!')
            self.dimension = 2

    @staticmethod
    def rename_attributes(**kwds):
        """Rename layout attributes.

        In the style dictionary multiple keywords can be used to address
        attributes. These keywords will be converted to an unique key word,
        used in the remaining code.

        ========= =================================
        keys      other valid keys
        ========= =================================
        fixed     fixed_nodes, fixed_vertices,
                  fixed_n, fixed_v
        positions initial_positions, node_positions
                  vertex_positions, n_positions,
                  v_positions
        ========= =================================

        """
        names = {'fixed': ['fixed_nodes', 'fixed_vertices',
                           'fixed_v', 'fixed_n'],
                 'positions': ['initial_positions', 'node_positions',
                               'vertex_positions', 'n_positions',
                               'v_positions'],
                 'layout_': ['layout_'],
                 }

        _kwds = {}
        del_keys = []
        for key, value in kwds.items():
            for attr, name_list in names.items():
                for name in name_list:
                    if name in key and name[0] == key[0]:
                        _kwds[key.replace(name, attr).replace(
                            'layout_', '')] = value
                        del_keys.append(key)
                        break
        # remove the replaced keys from the dict
        for key in del_keys:
            del kwds[key]

        return {**_kwds, **kwds}

    def generate_layout(self):
        """Function to pick and generate the right layout."""
        # method names
        names_rand = ['Random', 'random', 'rand', None]
        names_fr = ['Fruchterman-Reingold', 'fruchterman_reingold', 'fr',
                    'spring_layout', 'spring layout', 'FR']
        # check which layout should be plotted
        if self.layout_type in names_rand:
            self.layout = self.random()
        elif self.layout_type in names_fr:
            self.layout = self.fruchterman_reingold()

        # print(self.layout)
        return self.layout

    def random(self):
        """Position nodes uniformly at random in the unit square.

        For every node, a position is generated by choosing each of dimension
        coordinates uniformly at random on the interval [0.0, 1.0).

        This algorithm can be enabled with the keywords: 'Random',
        'random', 'rand', or None

        NumPy (http://scipy.org) is required for this function.

        **Keyword arguments used for the layout:**

        - ``dimension`` : int, optional (default = 2)
          Dimension of layout. Currently, only plots in 2 dimension are supported.

        - ``seed`` : int or None, optional (default = None)
          Set the random state for deterministic node layouts. If int, `seed` is
          the seed used by the random number generator, if None, the a random
          seed by created by the numpy random number generator is used.

        Returns
        -------
        layout : dict
            A dictionary of positions keyed by node

        """
        np.random.seed(self.seed)
        layout = np.random.rand(len(self.nodes), self.dimension)
        return dict(zip(self.nodes, layout))

    def fruchterman_reingold(self):
        """Position nodes using Fruchterman-Reingold force-directed algorithm.

        In this algorithm, the nodes are represented by steel rings and the
        edges are springs between them. The attractive force is analogous to the
        spring force and the repulsive force is analogous to the electrical
        force. The basic idea is to minimize the energy of the system by moving
        the nodes and changing the forces between them.

        This algorithm can be enabled with the keywords: 'Fruchterman-Reingold',
        'fruchterman_reingold', 'fr', 'spring_layout', 'spring layout', 'FR'

        **Keyword arguments used for the layout:**

        - ``force`` : float, optional (default = None)
          Optimal distance between nodes.  If None the distance is set to
          1/sqrt(n) where n is the number of nodes.  Increase this value to move
          nodes farther apart.

        - ``positions`` : dict or None  optional (default = None)
          Initial positions for nodes as a dictionary with node as keys and values
          as a coordinate list or tuple.  If None, then use random initial
          positions.

        - ``fixed`` : list or None, optional (default = None)
          Nodes to keep fixed at initial position.

        - ``iterations`` : int, optional (default = 50)
          Maximum number of iterations taken

        - ``threshold``: float, optional (default = 1e-4)
          Threshold for relative error in node position changes.  The iteration
          stops if the error is below this threshold.

        - ``weight`` : string or None, optional (default = None)
          The edge attribute that holds the numerical value used for the edge
          weight.  If None, then all edge weights are 1.

        - ``dimension`` : int, optional (default = 2)
          Dimension of layout. Currently, only plots in 2 dimension are supported.

        - ``seed`` : int or None, optional (default = None)
          Set the random state for deterministic node layouts. If int, `seed` is
          the seed used by the random number generator, if None, the a random seed
          by created by the numpy random number generator is used.

        Returns
        -------
        layout : dict
            A dictionary of positions keyed by node

        """

        # convert adjacency matrix
        self.adjacency_matrix = self.adjacency_matrix.astype(float)

        if self.fixed is not None:
            self.fixed = np.asarray([self.nodes.index(v) for v in self.fixed])

        if self.positions is not None:
            # Determine size of existing domain to adjust initial positions
            _size = max(coord for t in layout.values() for coord in t)
            if _size == 0:
                _size = 1
            np.random.seed(self.seed)
            self.layout = np.random.rand(
                len(self.nodes), self.dimension) * _size

            for i, n in enumerate(self.nodes):
                if n in self.positions:
                    self.layout[i] = np.asarray(self.positions[n])
        else:
            self.layout = None

        if self.k is None and self.fixed is not None:
            # We must adjust k by domain size for layouts not near 1x1
            self.k = _size / np.sqrt(len(self.nodes))

        try:
            # Sparse matrix
            if len(self.nodes) < 500:  # sparse solver for large graphs
                raise ValueError
            layout = self._sparse_fruchterman_reingold()
        except:
            layout = self._fruchterman_reingold()

        layout = dict(zip(self.nodes, layout))

        return layout

    def _fruchterman_reingold(self):
        """Fruchterman-Reingold algorithm for dense matrices.

        This algorithm is based on the Fruchterman-Reingold algorithm provided
        by networkx. (Copyright (C) 2004-2018 by Aric Hagberg <hagberg@lanl.gov>
        Dan Schult <dschult@colgate.edu> Pieter Swart <swart@lanl.gov> Richard
        Penney <rwpenney@users.sourceforge.net> All rights reserved. BSD
        license.)

        """
        A = self.adjacency_matrix.todense()
        k = self.k
        try:
            _n, _ = A.shape
        except AttributeError:
            log.error('Fruchterman-Reingold algorithm needs an adjacency '
                      'matrix as input')
            raise AttributeError

        # make sure we have an array instead of a matrix
        A = np.asarray(A)

        if self.layout is None:
            # random initial positions
            np.random.seed(self.seed)
            layout = np.asarray(np.random.rand(
                _n, self.dimension), dtype=A.dtype)
        else:
            # make sure positions are of same type as matrix
            layout = self.layout.astype(A.dtype)

        # optimal distance between nodes
        if k is None:
            k = np.sqrt(1.0 / _n)
        # the initial "temperature"  is about .1 of domain area (=1x1)
        # this is the largest step allowed in the dynamics.
        # We need to calculate this in case our fixed positions force our domain
        # to be much bigger than 1x1
        t = max(max(layout.T[0]) - min(layout.T[0]),
                max(layout.T[1]) - min(layout.T[1])) * 0.1
        # simple cooling scheme.
        # linearly step down by dt on each iteration so last iteration is size dt.
        dt = t / float(self.iterations + 1)
        delta = np.zeros(
            (layout.shape[0], layout.shape[0], layout.shape[1]), dtype=A.dtype)
        # the inscrutable (but fast) version
        # this is still O(V^2)
        # could use multilevel methods to speed this up significantly
        for iteration in range(self.iterations):
            # matrix of difference between points
            delta = layout[:, np.newaxis, :] - layout[np.newaxis, :, :]
            # distance between points
            distance = np.linalg.norm(delta, axis=-1)
            # enforce minimum distance of 0.01
            np.clip(distance, 0.01, None, out=distance)
            # displacement "force"
            displacement = np.einsum('ijk,ij->ik',
                                     delta,
                                     (k * k / distance**2 - A * distance / k))
            # update layoutitions
            length = np.linalg.norm(displacement, axis=-1)
            length = np.where(length < 0.01, 0.1, length)
            delta_layout = np.einsum('ij,i->ij', displacement, t / length)
            if self.fixed is not None:
                # don't change positions of fixed nodes
                delta_layout[self.fixed] = 0.0
            layout += delta_layout
            # cool temperature
            t -= dt
            error = np.linalg.norm(delta_layout) / _n
            if error < self.threshold:
                break
        return layout

    def _sparse_fruchterman_reingold(self):
        """Fruchterman-Reingold algorithm for sparse matrices.

        This algorithm is based on the Fruchterman-Reingold algorithm provided
        by networkx. (Copyright (C) 2004-2018 by Aric Hagberg <hagberg@lanl.gov>
        Dan Schult <dschult@colgate.edu> Pieter Swart <swart@lanl.gov> Richard
        Penney <rwpenney@users.sourceforge.net> All rights reserved. BSD
        license.)

        """
        A = self.adjacency_matrix
        k = self.k
        try:
            _n, _ = A.shape
        except AttributeError:
            log.error('Fruchterman-Reingold algorithm needs an adjacency '
                      'matrix as input')
            raise AttributeError
        try:
            from scipy.sparse import spdiags, coo_matrix
        except ImportError:
            log.error('The sparse Fruchterman-Reingold algorithm needs the '
                      'scipy package: http://scipy.org/')
            raise ImportError
        # make sure we have a LIst of Lists representation
        try:
            A = A.tolil()
        except:
            A = (coo_matrix(A)).tolil()

        if self.layout is None:
            # random initial positions
            np.random.seed(self.seed)
            layout = np.asarray(np.random.rand(
                _n, self.dimension), dtype=A.dtype)
        else:
            # make sure positions are of same type as matrix
            layout = layout.astype(A.dtype)

        # no fixed nodes
        if self.fixed is None:
            self.fixed = []

        # optimal distance between nodes
        if k is None:
            k = np.sqrt(1.0 / _n)
        # the initial "temperature"  is about .1 of domain area (=1x1)
        # this is the largest step allowed in the dynamics.
        t = max(max(layout.T[0]) - min(layout.T[0]),
                max(layout.T[1]) - min(layout.T[1])) * 0.1
        # simple cooling scheme.
        # linearly step down by dt on each iteration so last iteration is size dt.
        dt = t / float(self.iterations + 1)

        displacement = np.zeros((self.dimension, _n))
        for iteration in range(self.iterations):
            displacement *= 0
            # loop over rows
            for i in range(A.shape[0]):
                if i in self.fixed:
                    continue
                # difference between this row's node position and all others
                delta = (layout[i] - layout).T
                # distance between points
                distance = np.sqrt((delta**2).sum(axis=0))
                # enforce minimum distance of 0.01
                distance = np.where(distance < 0.01, 0.01, distance)
                # the adjacency matrix row
                Ai = np.asarray(A.getrowview(i).toarray())
                # displacement "force"
                displacement[:, i] +=\
                    (delta * (k * k / distance**2 - Ai * distance / k)).sum(axis=1)
            # update positions
            length = np.sqrt((displacement**2).sum(axis=0))
            length = np.where(length < 0.01, 0.1, length)
            delta_layout = (displacement * t / length).T
            layout += delta_layout
            # cool temperature
            t -= dt
            err = np.linalg.norm(delta_layout) / _n
            if err < self.threshold:
                break
        return layout


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:
