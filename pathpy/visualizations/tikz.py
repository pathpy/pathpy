#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : tikz.py -- Module to draw a tikz-network
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Fri 2020-02-28 12:17 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
import numpy as np
#from functools import singledispatchmethod
from singledispatchmethod import singledispatchmethod
from collections import OrderedDict
from .. import logger
from ..core.base import BaseStaticNetwork, BaseTemporalNetwork
from .painter import Painter, Painting
from .units import UnitConverter
from .canvas import Canvas
from .layout import Layout

log = logger(__name__)

# TODO: move this to the config file
DIGITS = 3


class TikzNetworkPainter(Painter):

    def __init__(self):
        """Initialize the network drawer.

        """
        log.debug('Draw tikz-network')

        # initialize the base class
        super().__init__()

        self.digits = DIGITS

    def convert_units(self):
        _units = self.config['general'].get('units', ('cm', 'pt'))
        if isinstance(_units, tuple):
            self.unit2cm = UnitConverter(_units[0], 'cm')
            self.unit2pt = UnitConverter(_units[1], 'pt')
        else:
            self.unit2cm = UnitConverter(_units, 'cm')
            self.unit2pt = UnitConverter(_units, 'pt')

        def formater(converter, divided=1, digits=3, unit=None):
            if unit is None:
                return lambda x: round(converter(x)/divided, digits)
            else:
                return lambda x: str(round(converter(x)/divided, digits))+unit

        def u2cm(a): return a if isinstance(a, str) \
            else formater(self.unit2cm)(a)

        def u2pt(a): return a if isinstance(a, str) \
            else formater(self.unit2pt)(a)

        def u2str(a): return a if isinstance(a, str) \
            else formater(self.unit2cm, unit='cm')(a)

        def u2div(a): return a if isinstance(a, str) \
            else formater(self.unit2pt, divided=7)(a)

        _commands = {'size': u2cm, 'label_distance': u2cm, 'label_size': u2div,
                     'arrow_size': u2cm, 'arrow_width': u2cm, 'width': u2pt,
                     'loop_size': u2str}

        for elements in self.data.values():
            for k, v in _commands.items():
                if k in list(elements.columns):
                    elements[k] = elements[k].apply(lambda x: v(x))

        # TODO: Find better way to do this
        if 'canvas' in self.config['general']:
            w, h = self.config['general']['canvas']
            self.config['general']['canvas'] = (
                self.unit2cm(w), self.unit2cm(h))

        if 'margins' in self.config['general']:
            _margins = self.config['general']['margins']
            if isinstance(_margins, int) or isinstance(_margins, float):
                value = self.unit2cm(_margins)
            else:
                value = {'top': self.unit2cm(_margins.get('top', 0)),
                         'left': self.unit2cm(_margins.get('left', 0)),
                         'bottom': self.unit2cm(_margins.get('bottom', 0)),
                         'right': self.unit2cm(_margins.get('right', 0))}
            self.config['general']['margins'] = value

        for key in ['xshift', 'yshift']:
            if key in self.config['general']:
                v = self.self.config['general'][key]
                self.config['general'][key] = str(self.unit2cm(v))+'cm'

    @singledispatchmethod
    def draw(self, network):
        raise NotImplementedError

    @draw.register(BaseStaticNetwork)
    def _draw_static(self, network, mode='tex', **kwargs):
        log.debug('Drawing a static tikz-network')

        # create new painting
        painting = Painting()

        # get data and config from the original network
        self.data, self.config = self.parse(network, **kwargs)

        # convert units
        self.convert_units()

        # get data in a nicer format
        nodes = self.data['nodes']
        edges = self.data['edges']

        # create canvas
        _canvas = self.config['general'].get('canvas', (None, None))
        _margins = self.config['general'].get('margins', None)

        # get max node size
        _max_node_size = None
        if 'size' in nodes.columns:
            _max_node_size = nodes['size'].max()

        # create canvas
        self.canvas = Canvas(_canvas[0], _canvas[1], _margins, _max_node_size)

        # configure the layout
        # check if a layout is defined
        _layout = self.config['general'].get('layout', None)

        # if layout is a command or None create the layout
        if isinstance(_layout, str) or _layout is None:
            if isinstance(_layout, str) and _layout in nodes.columns:
                layout = dict(zip(nodes['uid'], nodes[_layout]))
            elif _layout is None and 'euclidean' in nodes.columns:
                layout = dict(zip(nodes['uid'], nodes['euclidean']))
            else:
                _weight = self.config['general'].get('weight', None)
                layout = Layout(
                    nodes=list(network.nodes),
                    adjacency_matrix=network.adjacency_matrix(weight=_weight),
                    **self.config['general']).generate_layout()
        else:
            layout = _layout

        # fit the node position to the chosen canvas
        k_a_r = self.config['general'].get('keep_aspect_ratio', True)
        layout = self.canvas.fit(layout, keep_aspect_ratio=k_a_r)

        # assign layout to the nodes
        nodes['layout'] = nodes['uid'].map(layout)

        # bend the edges if enabled
        if 'curved' in edges.columns:
            edges['curved'] = edges['curved'].apply(
                lambda x: self.bend_factor(x))
            # self.edge_attributes['edge_curved'] = self.curve()

        # initialize data
        painting.data['nodes'] = []
        painting.data['edges'] = []

        # if csv is needed generate headings first
        if mode == 'csv':
            painting.data['nodes'].append(TikzNodePainter(
                **nodes.to_dict(orient='records')[0]).head())
            painting.data['edges'].append(TikzEdgePainter(
                **edges.to_dict(orient='records')[0]).head())

        # draw nodes
        for node in nodes.to_dict(orient='records'):
            painting.data['nodes'].append(
                TikzNodePainter(**node).draw(mode=mode))

        # draw edges
        for edge in edges.to_dict(orient='records'):
            painting.data['edges'].append(
                TikzEdgePainter(**edge).draw(mode=mode))

        # update config
        painting.config['width'] = self.canvas.width
        painting.config['height'] = self.canvas.height
        painting.config['standalone'] = self.config['general'].get(
            'standalone', True)

        _latex = {
            'clean': self.config['general'].get('clean', True),
            'clean_tex': self.config['general'].get('clean_tex', True),
            'compiler': self.config['general'].get('compiler', None),
            'compiler_args': self.config['general'].get('compiler_args', None),
            'silent': self.config['general'].get('silent', True)
        }

        painting.config.update(**_latex)

        return painting

    def bend_factor(self, curved):
        """Calculate the bend factor for curved edges."""
        bend = 0

        if curved != 0:
            v1 = np.array([0, 0])
            v2 = np.array([1, 1])
            v3 = np.array([(2*v1[0]+v2[0]) / 3.0 - curved * 0.5 * (v2[1]-v1[1]),
                           (2*v1[1]+v2[1]) / 3.0 +
                           curved * 0.5 * (v2[0]-v1[0])
                           ])
            vec1 = v2-v1
            vec2 = v3 - v1
            angle = np.rad2deg(np.arccos(
                np.dot(vec1, vec2) / np.sqrt((vec1*vec1).sum()) / np.sqrt((vec2*vec2).sum())))
            bend = np.round(
                np.sign(curved) * angle * -1, self.digits)
        return bend


class TikzNodePainter(object):
    """Class which handles the drawing of the nodes

    Parameters
    ----------
    id : node id
        This parameter is the identifier (id) for the node. Every node should
        have a unique id.

    attr : keyword arguments, optional (default = no attributes)
        Attributes to add to node as key=value pairs.
        See also :py:meth:`plot`

    See Also
    --------
    plot

    """

    def __init__(self, **kwargs):
        """Initialize the node drawer.

        Parameters
        ----------
        id : node id
            This parameter is the identifier (id) for the node. Every node
            should have a unique id.

        attr : keyword arguments, optional (default = no attributes)
            Attributes to add to node as key=value pairs.
            See also :py:meth:`plot`

        """
        self.uid = kwargs.get('uid', 'NaN')
        self.x = kwargs.get('layout', (0, 0))[0]
        self.y = kwargs.get('layout', (0, 0))[1]
        self.attributes = kwargs
        self.digits = DIGITS
        # all options from the tikz-network library
        self.tikz_kwds = OrderedDict()
        self.tikz_kwds['size'] = 'size'
        self.tikz_kwds['color'] = 'color'
        self.tikz_kwds["r"] = 'R'
        self.tikz_kwds["g"] = 'G'
        self.tikz_kwds["b"] = 'B'
        self.tikz_kwds['opacity'] = 'opacity'
        self.tikz_kwds['label'] = 'label'
        self.tikz_kwds['label_position'] = 'position'
        self.tikz_kwds['label_distance'] = 'distance'
        self.tikz_kwds['label_color'] = 'fontcolor'
        self.tikz_kwds['label_size'] = 'fontscale'
        self.tikz_kwds['shape'] = 'shape'
        self.tikz_kwds['style'] = 'style'
        self.tikz_kwds['layer'] = 'layer'

        self.tikz_args = OrderedDict()
        self.tikz_args['label_off'] = 'NoLabel'
        self.tikz_args['label_as_id'] = 'IdAsLabel'
        self.tikz_args['math_mode'] = 'Math'
        self.tikz_args['rgb'] = 'RGB'
        self.tikz_args['pseudo'] = 'Pseudo'

        for key, value in self.attributes.items():
            if value is None or (isinstance(value, float) and np.isnan(value)):
                self.attributes[key] = None

    def _check_color(self, mode='tex'):
        """Check if RGB colors are used and return this option."""
        _color = self.attributes.get('color', None)
        if (isinstance(_color, tuple) and mode == 'tex'):
            self.attributes['color'] = '{{{},{},{}}}'.format(
                _color[0], _color[1], _color[2])
            self.attributes['rgb'] = True
        elif (isinstance(_color, tuple) and mode == 'csv' and
              self.attributes.get('rgb', False)):
            self.attributes['color'] = None
            self.attributes['r'] = _color[0]
            self.attributes['g'] = _color[1]
            self.attributes['b'] = _color[2]
        elif (not isinstance(_color, tuple) and mode == 'csv' and
                self.attributes.get('node_rgb', False)):
            self.attributes['r'] = self.attributes.get('r', 0)
            self.attributes['g'] = self.attributes.get('g', 0)
            self.attributes['b'] = self.attributes.get('b', 0)
        elif (isinstance(_color, tuple) and mode == 'csv' and
                self.attributes.get('rgb', False) is False):
            self.attributes['color'] = None

    def draw(self, mode='tex'):
        """Function to draw a virtual node.

        Parameters
        ----------
        mode : str, optional (default = 'tex')
            The mode defines which kind of result should be returned. Currently
            a string for a tex file or a string for a csv file can be returned.

        Returns
        -------
        string : str
            Returns a string defining the node. If 'tex' mode is enabled, a
            tikz-network code is returned. If 'csv' mode is enabled, a row
            element for the node list is returned.

        """
        if mode == 'tex':
            self._check_color()
            string = '\\Vertex[x={x:.{n}f},y={y:.{n}f},IdAsLabel,' \
                ''.format(x=self.x, y=self.y, n=self.digits)

            for k in self.tikz_kwds:
                if (k in self.attributes and
                        self.attributes.get(k, None) is not None):
                    string += ',{}={}'.format(self.tikz_kwds[k],
                                              self.attributes[k])
            for k in self.tikz_args:
                if k in self.attributes:
                    if self.attributes[k]:
                        string += ',{}'.format(self.tikz_args[k])

            string += ']{{{}}}'.format(self.uid)

        elif mode == 'csv':
            self._check_color(mode='csv')
            string = '{uid},{x:.{n}f},{y:.{n}f}'\
                ''.format(uid=self.uid, x=self.x,
                          y=self.y, n=self.digits)

            for k in self.tikz_kwds:
                if k in self.attributes:
                    if self.attributes[k] is not None:
                        string += ',{}'.format(self.attributes[k])
                    else:
                        string += ', '

            for k in self.tikz_args:
                if k in self.attributes:
                    if self.attributes[k]:
                        string += ',true'
                    else:
                        string += ',false'

        return string + '\n'

    def head(self):
        """Function to draw the header of a virtual node.

        Returns
        -------
        string : str
            Returns a string with the attributes defined for the node. This
            string can be used as header for the 'csv' file.

        """
        self._check_color(mode='csv')
        string = 'id,x,y'
        for k in self.tikz_kwds:
            if k in self.attributes:
                string += ',{}'.format(self.tikz_kwds[k])
        for k in self.tikz_args:
            if k in self.attributes:
                string += ',{}'.format(self.tikz_args[k])

        return string + '\n'


class TikzEdgePainter(object):
    """Class which handles the drawing of the edges.

    Parameters
    ----------
    id : edge id
        This parameter is the identifier (id) for the edge. Every edge should
        have a unique id.

    u : node id
        This parameter defines the origin of the edge (if directed), i.e. u->v.

    v : node id
        This parameter defines the destination of the edge (if directed)
        i.e. u->v.

    attr : keyword arguments, optional (default = no attributes)
        Attributes to add to edge as key=value pairs.
        See also :py:meth:`plot`

    See Also
    --------
    plot

    """

    def __init__(self, **kwargs):
        """Initialize the edge drawer.

        Parameters
        ----------
        id : edge id
            This parameter is the identifier (id) for the edge. Every edge
            should have a unique id.

        u : node id
            This parameter defines the origin of the edge (if directed).

        v : node id
            This parameter defines the destination of the edge (if directed).

        attr : keyword arguments, optional (default = no attributes)
            Attributes to add to edge as key=value pairs.
            See also :py:meth:`plot`
        """
        self.uid = kwargs.get('uid')
        self.u = kwargs.get('source')
        self.v = kwargs.get('target')
        self.attributes = kwargs
        self.digits = DIGITS
        # all options from the tikz-network library
        self.tikz_kwds = OrderedDict()
        self.tikz_kwds["width"] = 'lw'
        self.tikz_kwds["color"] = 'color'
        self.tikz_kwds["r"] = 'R'
        self.tikz_kwds["g"] = 'G'
        self.tikz_kwds["b"] = 'B'
        self.tikz_kwds["opacity"] = 'opacity'
        self.tikz_kwds["curved"] = 'bend'
        self.tikz_kwds["label"] = 'label'
        self.tikz_kwds["label_position"] = 'position'
        self.tikz_kwds["label_distance"] = 'distance'
        self.tikz_kwds["label_color"] = 'fontcolor'
        self.tikz_kwds["label_size"] = 'fontscale'
        self.tikz_kwds["style"] = 'style'
        # self.tikz_kwds["edge_arrow_size"] = 'length'
        # self.tikz_kwds["edge_arrow_width"] = 'width'
        # self.tikz_kwds["edge_path"] = 'path'
        self.tikz_kwds["loop_size"] = 'loopsize'
        self.tikz_kwds["loop_position"] = 'loopposition'
        self.tikz_kwds["loop_shape"] = 'loopshape'

        self.tikz_args = OrderedDict()
        self.tikz_args['directed'] = 'Direct'
        self.tikz_args['math_mode'] = 'Math'
        self.tikz_args['rgb'] = 'RGB'
        self.tikz_args['not_in_bg'] = 'NotInBG'

        for key, value in self.attributes.items():
            if value is None or (isinstance(value, float) and np.isnan(value)):
                self.attributes[key] = None

    def _check_color(self, mode='tex'):
        """Check if RGB colors are used and return this option."""
        _color = self.attributes.get('color', None)
        if isinstance(_color, tuple) and mode == 'tex':
            self.attributes['color'] = '{{{},{},{}}}'.format(
                _color[0], _color[1], _color[2])
            self.attributes['rgb'] = True
        elif (isinstance(_color, tuple) and mode == 'csv' and
                self.attributes.get('rgb', False)):
            self.attributes['color'] = None
            self.attributes['r'] = _color[0]
            self.attributes['g'] = _color[1]
            self.attributes['b'] = _color[2]
        elif (not isinstance(_color, tuple) and mode == 'csv' and
                self.attributes.get('rgb', False)):
            self.attributes['r'] = self.attributes.get('r', 0)
            self.attributes['g'] = self.attributes.get('g', 0)
            self.attributes['b'] = self.attributes.get('b', 0)
        elif (isinstance(_color, tuple) and mode == 'csv' and
                self.attributes.get('rgb', False) is False):
            self.attributes['color'] = None

    def _format_style(self):
        """Format the style attribute for the edge.

        In order to change the arrow shape, the style attribute of the edge has
        to be changed. This option is only available for 'pdf' and 'tex'
        files. 'csv' files do not have this option.

        """
        if 'arrow_size' in self.attributes:
            arrow_size = 'length=' + str(15*self.attributes['arrow_size'])+'cm,'
        else:
            arrow_size = ''

        if 'arrow_size' in self.attributes:
            arrow_width = 'width=' + str(10*self.attributes['arrow_width'])+'cm'
        else:
            arrow_width = ''

        if ((arrow_size != '' or arrow_width != '') and
                self.attributes.get('directed', False)):
            self.attributes['style'] = '{{-{{Latex[{}{}]}}, {} }}'.format(
                arrow_size, arrow_width, self.attributes.get('style', ''))

    def draw(self, mode='tex'):
        """Function to draw an virtual edge.

        Parameters
        ----------
        mode : str, optional (default = 'tex')
            The mode defines which kind of result should be returned. Currently
            a string for a tex file or a string for a csv file can be returned.

        Returns
        -------
        string : str
            Returns a string defining the edge. If 'tex' mode is enabled, a
            tikz-network code is returned. If 'csv' mode is enabled, a row
            element for the edge list is returned.

        """
        if mode == 'tex':
            self._format_style()
            self._check_color()

            string = '\\Edge['

            for k in self.tikz_kwds:
                if (k in self.attributes and
                        self.attributes.get(k, None) is not None):
                    string += ',{}={}'.format(self.tikz_kwds[k],
                                              self.attributes[k])
            for k in self.tikz_args:
                if k in self.attributes:
                    if self.attributes[k]:
                        string += ',{}'.format(self.tikz_args[k])

            string += ']({})({})'.format(self.u, self.v)

        elif mode == 'csv':
            self._check_color(mode='csv')
            string = '{},{}'.format(self.u, self.v)

            for k in self.tikz_kwds:
                if k in self.attributes:
                    if self.attributes[k] is not None:
                        string += ',{}'.format(self.attributes[k])
                    else:
                        string += ', '
            for k in self.tikz_args:
                if k in self.attributes:
                    if self.attributes[k] == True:
                        string += ',true'
                    else:
                        string += ',false'

        return string + '\n'

    def head(self):
        """Function to draw the header of an virtual edge.

        Returns
        -------
        string : str
            Returns a string with the attributes defined for the edge. This
            string can be used as header for the 'csv' file.

        """
        self._check_color(mode='csv')
        string = 'u,v'
        for k in self.tikz_kwds:
            if k in self.attributes:
                string += ',{}'.format(self.tikz_kwds[k])
        for k in self.tikz_args:
            if k in self.attributes:
                string += ',{}'.format(self.tikz_args[k])

        return string + '\n'


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
