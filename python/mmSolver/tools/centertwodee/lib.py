# Copyright (C) 2021 David Cattermole, Kazuma Tonegawa.
#
# This file is part of mmSolver.
#
# mmSolver is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# mmSolver is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
#
"""
Functions to support smoothing animation curve keyframes.
"""

import mmSolver.logger
import mmSolver.tools.centertwodee.constant as const

LOG = mmSolver.logger.get_logger()


def convert_range(**kwargs):
    """
    Converts the input range to maps it to desired range.

    :rtype: float
    """
    input_value = kwargs.get('input_value')
    LOG.info(('convertRange input_value:', input_value))
    input_range_start = kwargs.get('input_range_start')
    input_range_end = kwargs.get('input_range_end')
    output_range_start = kwargs.get('output_range_start')
    output_range_end = kwargs.get('output_range_end')
    is_zoom = kwargs.get('zoom')
    is_expected_node_default = (
        (input_value == const.PAN_DEFAULT and not is_zoom)\
        or (input_value == const.ZOOM_DEFAULT and is_zoom)
    )
    LOG.info(('convertRange is_expected_node_default:', is_expected_node_default))
    if input_value == float(const.DEFAULT_SLIDER_VALUE):
        if not is_zoom:
            output_value = const.PAN_DEFAULT
        else:
            output_value = const.ZOOM_DEFAULT
    elif is_expected_node_default:
        output_value = const.DEFAULT_SLIDER_VALUE
    else:
        input_diff = input_range_end - input_range_start
        output_diff = output_range_end - output_range_start
        output_value = (
           (output_diff / input_diff) *
           (input_value - input_range_start)
           ) + output_range_start
    return output_value


def set_offset_range(source='slider'):
    """
    Setting in/out ranges for pan offset values.

    :rtype: (float, float, float, float)
    """
    if source == 'slider':
        input_range_start = const.SLIDER_MIN
        input_range_end = const.SLIDER_MAX
        output_range_start = const.PAN_MIN
        output_range_end = const.PAN_MAX
    elif source == 'node':
        input_range_start = const.PAN_MIN
        input_range_end = const.PAN_MAX
        output_range_start = const.SLIDER_MIN
        output_range_end = const.SLIDER_MAX

    return (
        input_range_start,
        input_range_end,
        output_range_start,
        output_range_end
    )


def set_zoom_range(**kwargs):
    """
    Setting in/out zoom range. This one is a bit more complicated since a
    logarithmic mapping of range is not used.

    :rtype: (float, float, float, float)
    """
    if kwargs.get('source') == 'slider':
        input_range_start = const.SLIDER_MIN
        input_range_end = const.SLIDER_MAX
        output_range_start = const.ZOOM_MIN
        output_range_end = const.ZOOM_MAX
        if kwargs.get('input_value') > const.DEFAULT_SLIDER_VALUE:
            input_range_start = const.DEFAULT_SLIDER_VALUE
            output_range_start = const.ZOOM_DEFAULT
        elif kwargs.get('input_value') < const.DEFAULT_SLIDER_VALUE:
            input_range_end = const.DEFAULT_SLIDER_VALUE
            output_range_end = const.ZOOM_DEFAULT
    elif kwargs.get('source') == 'node':
        input_range_start = const.ZOOM_MIN
        input_range_end = const.ZOOM_MAX
        output_range_start = const.SLIDER_MIN
        output_range_end = const.SLIDER_MAX
        if kwargs.get('input_value') > const.ZOOM_DEFAULT:
            input_range_start = const.ZOOM_DEFAULT
            output_range_start = const.DEFAULT_SLIDER_VALUE
        elif kwargs.get('input_value') < const.ZOOM_DEFAULT:
            LOG.info(('should be decreasing zoom:', kwargs.get('input_value')))
            input_range_end = const.ZOOM_DEFAULT
            output_range_end = const.DEFAULT_SLIDER_VALUE

    return (
        input_range_start,
        input_range_end,
        output_range_start,
        output_range_end
    )