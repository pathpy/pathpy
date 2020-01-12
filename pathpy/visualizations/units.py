#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : unit.py
# Creation  : 08 May 2018
# Time-stamp: <Wed 2019-12-18 12:37 juergen>
#
# Copyright (c) 2018 Jürgen Hackl <hackl@ibi.baug.ethz.ch>
#               http://www.ibi.ethz.ch
# $Id$
#
# Description : Module to convert measurement units
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


class UnitConverter(object):
    """Convert units.

    Parameters
    ----------
    input_unit : str, optional (default = 'cm')
        Unit which should be converted. The abbreviation of the unit is entered
        as string value. Currently supported are: Pixel 'px', Points 'pt',
        Millimeters 'mm', and Centimeters 'cm'.

    output_unit : str, optional (default = 'cm')
        Unit to which should be converted. The abbreviation of the unit is
        entered as string value. Currently supported are: Pixel 'px', Points
        'pt', Millimeters 'mm', and Centimeters 'cm'.

    digits : int, optional (default = 4)
        Number of digits to round the returning measure. Per default the
        measures are rounded to 4 digits.

    Examples
    --------
    >>> mm2cm = cn.UnitConverter('mm','cm')
    >>> mm2cm(10)
    1

    """

    def __init__(self, input_unit='cm', output_unit='cm', digits=4):
        """Initialize the unit converter.

        Parameters
        ----------
        input_unit : str, optional (default = 'cm')
            Unit which should be converted. The abbreviation of the unit is
            entered as string value. Currently supported are: Pixel 'px', Points
            'pt', Millimeters 'mm', and Centimeters 'cm'.

        output_unit : str, optional (default = 'cm')
            Unit to which should be converted. The abbreviation of the unit is
            entered as string value. Currently supported are: Pixel 'px', Points
            'pt', Millimeters 'mm', and Centimeters 'cm'.

        digits : int, optional (default = 4)
            Number of digits to round the returning measure. Per default the
            measures are rounded to 4 digits.
        """
        self.input_unit = input_unit
        self.output_unit = output_unit
        self.digits = digits

    def __call__(self, value):
        """Returns the converted measure.

        Returns
        -------
        measure : float
            Returns the converted measure.

        Examples
        --------
        >>> mm2cm = cn.UnitConverter('mm','cm')
        >>> mm2cm(10)
        1

        """
        return self.convert(value)

    @staticmethod
    def px_to_mm(measure):
        """Convert pixel to millimeters."""
        return measure * 0.26458333333719

    @staticmethod
    def px_to_pt(measure):
        """Convert pixel to points."""
        return measure * 0.75

    @staticmethod
    def pt_to_mm(measure):
        """Convert points to millimeters."""
        return measure * 0.352778

    @staticmethod
    def mm_to_px(measure):
        """Convert millimeters to pixel."""
        return measure * 3.779527559

    @staticmethod
    def mm_to_pt(measure):
        """Convert millimeters to points."""
        return measure * 2.83465

    def convert(self, value):
        """Returns the converted measure.

        Returns
        -------
        measure : float
            Returns the converted measure.

        Examples
        --------
        >>> mm2cm = cn.UnitConverter('mm','cm')
        >>> mm2cm.convert(10)
        1

        """
        try:
            measure = float(value)
        except:
            log.error('Value "{}" is not a number, and therefor can not'
                      ' converted to an other unit!.'.format(value))
            raise ValueError

        # to cm
        if self.input_unit == 'mm' and self.output_unit == 'cm':
            value = measure/10
        elif self.input_unit == 'pt' and self.output_unit == 'cm':
            value = self.pt_to_mm(measure)/10
        elif self.input_unit == 'px' and self.output_unit == 'cm':
            value = self.px_to_mm(measure)/10
        elif self.input_unit == 'cm' and self.output_unit == 'cm':
            value = measure
        # to pt
        elif self.input_unit == 'px' and self.output_unit == 'pt':
            value = self.px_to_pt(measure)
        elif self.input_unit == 'mm' and self.output_unit == 'pt':
            value = self.mm_to_pt(measure)
        elif self.input_unit == 'cm' and self.output_unit == 'pt':
            value = self.mm_to_pt(measure)*10
        elif self.input_unit == 'pt' and self.output_unit == 'pt':
            value = measure
        # to px
        elif self.input_unit == 'mm' and self.output_unit == 'px':
            value = self.mm_to_px(measure)
        elif self.input_unit == 'cm' and self.output_unit == 'px':
            value = self.mm_to_px(10*measure)
        elif self.input_unit == 'pt' and self.output_unit == 'px':
            value = measure*4/3
        elif self.input_unit == 'px' and self.output_unit == 'px':
            value = measure
        else:
            log.error('The conversion from "{}" to "{}" is currently not '
                      'supported!'.format(self.input_unit,
                                          self.output_unit))
            raise NotImplementedError

        # return the converted measure
        return round(value, self.digits)

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:
