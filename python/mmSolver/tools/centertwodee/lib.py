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
Functions to deal with range mappings to work between the UI sliders
and the offset/zoom nodes
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import maya.cmds

import mmSolver.logger
import mmSolver.utils.viewport as viewport_utils
import mmSolver.utils.reproject as reproject_utils
import mmSolver.tools.centertwodee.constant as const

LOG = mmSolver.logger.get_logger()


def _lerp(min_value, max_value, mix):
    """
    Return 'min_value' to 'max_value' linearly, for a 'mix' value
    between 0.0 and 1.0.

    :type min_value: float
    :type max_value: float
    :type mix: float

    :rtype: float
    """
    return (1.0 - mix) * min_value + mix * max_value


def _inverse_lerp(min_value, max_value, mix):
    """
    Return 0.0 to 1.0 linearly, for a 'mix' value between 'min_value'
    and 'max_value'.

    :type min_value: float
    :type max_value: float
    :type mix: float

    :rtype: float
    """
    return (mix - min_value) / (max_value - min_value)


def _remap(old_min, old_max, new_min, new_max, mix):
    """
    Remap from the 'old_*' values to 'new_*' values, using a 'mix'
    value between 0.0 and 1.0;

    :type old_min: float
    :type old_max: float
    :type new_min: float
    :type new_max: float
    :type mix: float

    :rtype: float
    """
    blend = _inverse_lerp(old_min, old_max, mix)
    return _lerp(new_min, new_max, blend)


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

    return (input_range_start, input_range_end, output_range_start, output_range_end)


def set_zoom_range(input_value=None, source=None):
    """
    Setting in/out zoom range. This one is a bit more complicated since a
    logarithmic mapping of range is not used.

    :rtype: (float, float, float, float)
    """
    if source == 'slider':
        input_range_start = const.SLIDER_MIN
        input_range_end = const.SLIDER_MAX
        output_range_start = const.ZOOM_MIN
        output_range_end = const.ZOOM_MAX
    elif source == 'node':
        input_range_start = const.ZOOM_MIN
        input_range_end = const.ZOOM_MAX
        output_range_start = const.SLIDER_MIN
        output_range_end = const.SLIDER_MAX

    return (input_range_start, input_range_end, output_range_start, output_range_end)


def get_offset_nodes():
    """
    Query for Center 2D nodes.

    :returns: Two offset nodes (plusMinusAverage and multiplyDivide)
    :rtype: string, string.
    """
    model_editor = viewport_utils.get_active_model_editor()
    cam_tfm, cam_shp = viewport_utils.get_viewport_camera(model_editor)
    reprojection_nodes = reproject_utils.find_reprojection_nodes(cam_tfm, cam_shp)
    offset_node = None
    for node in reprojection_nodes:
        if 'offset_plusMinusAverage' in node:
            offset_node = node
    return offset_node, cam_shp


def get_offset_node_values(offset_node):
    """
    Get attribute values for offset nodes.

    :rtype: (float, float, flaot)
    """
    offset_x_value = maya.cmds.getAttr(offset_node + '.input2D[1].input2Dx')
    offset_y_value = maya.cmds.getAttr(offset_node + '.input2D[1].input2Dy')
    return (offset_x_value, offset_y_value)


def get_camera_zoom(cam_shp):
    """
    Get attribute values for offset nodes.

    :rtype: (float, float, flaot)
    """
    zoom_value = maya.cmds.getAttr(cam_shp + '.zoom')
    return zoom_value


def process_value(input_value=None, source=None, zoom=None):
    assert isinstance(zoom, bool)
    if zoom is False:
        new_range = set_offset_range(source)
        zoom = False
    elif zoom is True:
        new_range = set_zoom_range(input_value=input_value, source=source)
        zoom = True
    input_range_start, input_range_end, output_range_start, output_range_end = new_range

    output = _remap(
        input_range_start,
        input_range_end,
        float(output_range_start),
        float(output_range_end),
        input_value,
    )
    return output


def set_horizontal_offset(cam_shp, offset_node, value):
    horizontal_aperture_value = maya.cmds.getAttr(cam_shp + '.horizontalFilmAperture')
    normalized_value = horizontal_aperture_value * value
    maya.cmds.setAttr(offset_node + '.input2D[1].input2Dx', normalized_value)


def set_vertical_offset(cam_shp, offset_node, value):
    vertical_aperture_value = maya.cmds.getAttr(cam_shp + '.verticalFilmAperture')
    normalized_value = vertical_aperture_value * value
    maya.cmds.setAttr(offset_node + '.input2D[1].input2Dy', normalized_value)


def set_zoom(cam_shp, value):
    assert maya.cmds.nodeType(cam_shp) == 'camera'
    maya.cmds.setAttr(cam_shp + '.zoom', value)
