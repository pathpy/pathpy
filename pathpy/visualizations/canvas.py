#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : canvas.py
# Creation  : 19 May 2018
# Time-stamp: <Wed 2019-12-18 11:06 juergen>
#
# Copyright (c) 2018 Jürgen Hackl <hackl@ibi.baug.ethz.ch>
#               http://www.ibi.ethz.ch
# $Id$
#
# Description : Module to create a canvas for plotting
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
from .. import logger

log = logger(__name__)

# TODO: move to config file
CANVAS = (6, 6)


class Canvas(object):
    """A canvas object defining the size of the plot.

    Parameters
    ----------
    width : int or float, optional (default = 6)
        The parameter defines the width of the figure. The width is defined in
        cm units. If no width is defined the default value of 6 cm is used. The
        default can be changed in the config file.

    height : int or float, optional (default = 6)
        The parameter defines the height of the figure. The height is defined in
        cm units. If no height is defined the default value of 6 cm is used. The
        default can be changed in the config file.

    margins : None, int, float or dict, optional (default = None)
        The margins define the 'empty' space from the canvas border. If no
        margins are defined, the margin will be calculated based on the maximum
        node size, to avoid clipping of the nodes. If a single int or float is
        defined all margins using this distances. To define different the margin
        sizes for all size a dictionary with in the form of
        `{'top':2,'left':1,'bottom':2,'right':.5}` has to be used.

    max_node_size : dict, optional (default = None)
        If no specific margins are defined, the margins are based on the maximum
        node size, in order to avoid clipping at the boundary of the figure. If
        no max_node_size are defined, the default value of tikz-network will be
        used.

    Attributes
    ----------
    width : int or float
        Width of the figure. This property can be called, set and modified.

    height : int or float
        Height of the figure. This property can be called, set and modified.

    """

    def __init__(self, width=None, height=None, margins=None, max_node_size=None):
        """Initialize a canvas object.

        Parameters
        ----------
        width : int or float, optional (default = 6)
            The parameter defines the width of the figure. The width is defined
            in cm units. If no width is defined the default value of 6 cm is
            used. The default can be changed in the config file.

        height : int or float, optional (default = 6)
            The parameter defines the height of the figure. The height is
            defined in cm units. If no height is defined the default value of 6
            cm is used. The default can be changed in the config file.

        margins : None, int, float or dict, optional (default = None)
            The margins define the 'empty' space from the canvas border. If no
            margins are defined, the margin will be calculated based on the
            maximum node size, to avoid clipping of the nodes. If a single int
            or float is defined all margins using this distances. To define
            different the margin sizes for all size a dictionary with in the
            form of `{'top':2,'left':1,'bottom':2,'right':.5}` has to be used.

        max_node_size : dict, optional (default = None)
            If no specific margins are defined, the margins are based on the
            maximum node size, in order to avoid clipping at the boundary of the
            figure. If no max_node_size are defined, the default value of
            tikz-network will be used.

        """
        # apply default values if not defined
        if width is None:
            width = CANVAS[0]
        if height is None:
            height = CANVAS[1]

        # initialize variables
        self._width = width
        self._height = height
        self._margins = margins
        self._max_node_size = max_node_size

    @property
    def width(self):
        """Returns the width of the canvas."""
        return self._width

    @width.setter
    def width(self, width):
        """Set the width of the canvas."""
        self._width = width

    @property
    def height(self):
        """Returns the height of the canvas."""
        return self._height

    @height.setter
    def height(self, height):
        """Set the height of the canvas."""
        self._height = height

    def margins(self, margins=None, max_node_size=None):
        """Returns a dictionary of margins.

        Parameters
        ----------
        margins : None, int, float or dict, optional (default = None)
            The margins define the 'empty' space from the canvas border. If no
            margins are defined, the margin will be calculated based on the
            maximum node size, to avoid clipping of the nodes. If a single int
            or float is defined all margins using this distances. To define
            different the margin sizes for all size a dictionary with in the
            form of `{'top':2,'left':1,'bottom':2,'right':.5}` has to be used.

        max_node_size : dict, optional (default = None)
            If no specific margins are defined, the margins are based on the
            maximum node size, in order to avoid clipping at the boundary of the
            figure. If no max_node_size are defined, the default value of
            tikz-network will be used.

        Returns
        -------
        margins : dict
            Returns the margins of the :py:class:`Canvas` as a dictionary in
            from of `{'top':2,'left':1,'bottom':2,'right':.5}`. The values
            correspond to cm units.

        Examples
        --------
        Default margins if nothing is defined.

        >>> canvas = cn.Canvas()
        >>> canvas.margins()
        {'top':.35,'left':.35,'bottom':.35,'right':.35}

        Margins defined with one value

        >>> canvas.margins(1)
        {'top':1,'left':1,'bottom':1,'right':1}

        Margins as dictionary.

        >>> canvas.margins({'top':2,'left':1,'bottom':2,'right':.5})
        {'top':2,'left':1,'bottom':2,'right':.5}

        Margins defined via max node sizes:

        >>> canvas.margins(margins=None,max_node_size{'a':.3,'b':.5})
        {'top':.3,'left':.3,'bottom':.3,'right':.3}

        """

        # check if arguments are None
        if margins is None and self._margins is not None:
            margins = self._margins
        if max_node_size is None:
            max_node_size = self._max_node_size

        # if margins are not defined use max node size to avoid clipping.
        if margins is None:
            if max_node_size is not None:
                _margin = max_node_size.values()/2+.05
            else:
                _margin = 0.35
            _margins = {'top': _margin, 'bottom': _margin,
                        'left': _margin, 'right': _margin}

        # if only one number is specified, this will be applied to all margins.
        elif isinstance(margins, int) or isinstance(margins, float):
            _m = margins
            _margins = {'top': _m, 'left': _m, 'bottom': _m, 'right': _m}

        # if margins defined as dict, the dict values are used
        elif isinstance(margins, dict):
            _margins = {'top': margins.get('top', 0),
                        'left': margins.get('left', 0),
                        'bottom': margins.get('bottom', 0),
                        'right': margins.get('right', 0)}
        else:
            log.error('Margins are not proper defined!')
            raise AttributeError

        # check size of the margins
        if _margins['top'] + _margins['bottom'] >= self.height or \
           _margins['left'] + _margins['right'] >= self.width:
            log.error('Margins horizontal {} or vertical {} are larger than the'
                      ' canvas size ({},{})!'
                      ''.format(_margins['left'] + _margins['right'],
                                _margins['top'] + _margins['bottom'],
                                self.width, self.height))
            raise AttributeError

        # update class variables
        self._margins = _margins
        self._max_node_size = max_node_size

        # return a dict of margins
        return _margins

    def fit(self, layout, keep_aspect_ratio=True):
        """Fit the node positions to the canvas.

        Parameters
        ----------
        layout : dict
            A dictionary with the node positions on a 2-dimensional plane. The
            key value of the dict represents the node id while the value
            represents a tuple of coordinates (e.g. n = (x,y)). The initial
            layout can be placed anywhere on the 2-dimensional plane.

        keep_aspect_ratio : bool, optional (default = True)
            Defines whether to keep the aspect ratio of the current layout. If
            `False`, the layout will be rescaled to fit exactly into the
            available area in the canvas (i.e. removed margins). If `True`, the
            original aspect ratio of the layout will be kept and it will be
            centered within the canvas.

        Returns
        -------
        layout : dict
            Returns a dictionary with the new node positions. Key values
            represents the node ids and the values are the new coordinates. The
            new coordinates are shifted and transformed from its origins.

        Examples
        --------
        Create empty canvas with no margins and fit simple layout.

        >>> canvas = cn.Canvas(6,4,margins=0)
        >>> layout = {'a':(-1,-1),'b':(1,-1),'c':(1,1),'d':(-1,1)}
        >>> canvas.fit(layout)
        {'a':(1,0),'b':(5,0),'c':(5,4),'d':(1,4)}

        Without keeping the aspect ratio.

        >>> canvas = cn.Canvas(6,4,margins=0)
        >>> layout = {'a':(-1,-1),'b':(1,-1),'c':(1,1),'d':(-1,1)}
        >>> canvas.fit(layout, keep_aspect_ratio=False)
        {'a':(0,0),'b':(6,0),'c':(6,4),'d':(0,4)}

        """
        # get canvas size and margins
        width = self.width
        height = self.height
        margins = self.margins()

        # find min and max values of the points
        min_x = min(layout.items(), key=lambda item: item[1][0])[1][0]
        max_x = max(layout.items(), key=lambda item: item[1][0])[1][0]
        min_y = min(layout.items(), key=lambda item: item[1][1])[1][1]
        max_y = max(layout.items(), key=lambda item: item[1][1])[1][1]

        # calculate the scaling ratio
        ratio_x = float('inf')
        ratio_y = float('inf')

        if max_x-min_x > 0:
            ratio_x = (width-margins['left']-margins['right']) / (max_x-min_x)
        if max_y-min_y > 0:
            ratio_y = (height-margins['top']-margins['bottom']) / (max_y-min_y)

        if keep_aspect_ratio:
            scaling = (min(ratio_x, ratio_y), min(ratio_x, ratio_y))
        else:
            scaling = (ratio_x, ratio_y)

        if scaling[0] == float('inf'):
            scaling = (1, scaling[1])
        if scaling[1] == float('inf'):
            scaling = (scaling[0], 1)

        # apply scaling to the points
        _layout = {}
        for n, (x, y) in layout.items():
            _x = (x)*scaling[0]
            _y = (y)*scaling[1]
            _layout[n] = (_x, _y)

        # find min and max values of new the points
        min_x = min(_layout.items(), key=lambda item: item[1][0])[1][0]
        max_x = max(_layout.items(), key=lambda item: item[1][0])[1][0]
        min_y = min(_layout.items(), key=lambda item: item[1][1])[1][1]
        max_y = max(_layout.items(), key=lambda item: item[1][1])[1][1]

        # calculate the translation
        translation = (((width-margins['left']-margins['right'])/2
                        + margins['left']) - ((max_x-min_x)/2 + min_x),
                       ((height-margins['top']-margins['bottom'])/2
                        + margins['bottom']) - ((max_y-min_y)/2 + min_y))

        # apply translation to the points
        for n, (x, y) in _layout.items():
            _x = (x)+translation[0]
            _y = (y)+translation[1]
            _layout[n] = (_x, _y)

        return _layout

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:
