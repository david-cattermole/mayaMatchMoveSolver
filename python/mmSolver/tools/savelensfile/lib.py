# Copyright (C) 2022 David Cattermole.
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
The Save Lens File library functions.

Write out a mmSolver Lens node as a .nk file, readable in The Foundry
Nuke.
"""

import os
import tempfile

import maya.cmds

import mmSolver.logger
import mmSolver.utils.python_compat as pycompat
import mmSolver.tools.loadlens.constant as const_load
import mmSolver.tools.savelensfile.constant as const
import mmSolver.constant as const_proj
import mmSolver.api as mmapi


LOG = mmSolver.logger.get_logger()


def _get_lens_model(node):
    assert isinstance(node, pycompat.TEXT_TYPE)
    assert maya.cmds.nodeType(node) == const_load.MAYA_MM_LENS_MODEL_3DE
    attr_name = 'lensModel'
    node_attr = '{}.{}'.format(node, attr_name)
    return maya.cmds.getAttr(node_attr)


def _generate_attr_data(node, attr_name, frames, modify_value_func=None):
    assert isinstance(node, pycompat.TEXT_TYPE)
    assert isinstance(attr_name, pycompat.TEXT_TYPE)
    assert isinstance(frames, list) and len(frames) > 0
    assert modify_value_func is None or callable(modify_value_func)

    data = const.DEFAULT_ATTRIBUTE_DATA.copy()
    data['name'] = attr_name

    node_attr = '{}.{}'.format(node, attr_name)
    attr = mmapi.Attribute(node=node, attr=attr_name)
    if attr.is_animated() is True:
        values = [maya.cmds.getAttr(node_attr, time=f) for f in frames]
        if callable(modify_value_func) is True:
            values = [modify_value_func(v) for v in values]

        data['frames'] = frames
        data['values'] = values
        assert len(data['frames']) == len(data['values'])
    else:
        value = maya.cmds.getAttr(node_attr)
        if callable(modify_value_func) is True:
            value = modify_value_func(value)

        data['frames'] = []
        data['values'] = [value]
        assert len(data['frames']) == 0
        assert len(data['values']) == 1
    return data


def generate(cam, lens, frame_range):
    """
    Convert camera-lens pair to data that can be written to a file.

    :returns: Data structure containing the data from the lens, ready to be written.
    :rtype: dict
    """
    assert isinstance(cam, mmapi.Camera)
    assert isinstance(lens, mmapi.Lens)

    frames = range(frame_range.start, frame_range.end + 1)
    assert len(frames) > 0

    lens_node = lens.get_node()
    # The lens node is a DG node, so the name will be a valid name by
    # default.
    node_name = lens_node
    maya_node_type = const_load.MAYA_MM_LENS_MODEL_3DE
    lens_model = _get_lens_model(lens_node)

    data = const.DEFAULT_LENS_NODE_DATA.copy()

    data['node_type'] = maya_node_type
    data['lens_model_type'] = lens_model
    data['node_name'] = node_name
    data['attributes'] = []

    # 3DEqualizer uses centimeters for all units, so we might as well
    # convert the data into the same units that it will probably be
    # used as.
    def _inches_to_centimeters(value):
        return value * 2.54

    def _millimeters_to_centimeters(value):
        return value * 0.1

    # Camera shape node values
    cam_shp = cam.get_shape_node()
    attr_focal = _generate_attr_data(
        cam_shp, 'focalLength', frames, modify_value_func=_millimeters_to_centimeters
    )
    attr_focus = _generate_attr_data(cam_shp, 'focusDistance', frames)
    attr_hfa = _generate_attr_data(
        cam_shp,
        'horizontalFilmAperture',
        frames,
        modify_value_func=_inches_to_centimeters,
    )
    attr_vfa = _generate_attr_data(
        cam_shp,
        'verticalFilmAperture',
        frames,
        modify_value_func=_inches_to_centimeters,
    )
    attr_hfo = _generate_attr_data(
        cam_shp,
        'horizontalFilmOffset',
        frames,
        modify_value_func=_inches_to_centimeters,
    )
    attr_vfo = _generate_attr_data(
        cam_shp, 'verticalFilmOffset', frames, modify_value_func=_inches_to_centimeters
    )

    data['attributes'].append(attr_focal)
    data['attributes'].append(attr_focus)
    data['attributes'].append(attr_hfa)
    data['attributes'].append(attr_vfa)
    data['attributes'].append(attr_hfo)
    data['attributes'].append(attr_vfo)
    # TODO: How can we get the pixel aspect ratio?
    # 'tde4_pixel_aspect'

    # Add lens distortion values
    lookup = const_load.NODE_TYPE_TO_MODEL_TYPE_TO_ATTRIBUTE_NAMES
    attr_names = lookup[maya_node_type][lens_model]
    for attr_name in attr_names:
        attr = _generate_attr_data(lens_node, attr_name, frames)
        data['attributes'].append(attr)

    return data


def _format_attributes_data_for_nuke_knobs(attributes, nuke_node_type, node_name):
    assert isinstance(attributes, list)
    assert isinstance(node_name, pycompat.TEXT_TYPE)

    # Add default attributes that are not in the 'attributes'.
    attr_direction = const.DEFAULT_ATTRIBUTE_DATA.copy()
    attr_fov_xa = const.DEFAULT_ATTRIBUTE_DATA.copy()
    attr_fov_xb = const.DEFAULT_ATTRIBUTE_DATA.copy()
    attr_fov_ya = const.DEFAULT_ATTRIBUTE_DATA.copy()
    attr_fov_yb = const.DEFAULT_ATTRIBUTE_DATA.copy()
    attr_name = const.DEFAULT_ATTRIBUTE_DATA.copy()

    attr_direction['name'] = 'direction'
    attr_fov_xa['name'] = 'field_of_view_xa_unit'
    attr_fov_xb['name'] = 'field_of_view_xb_unit'
    attr_fov_ya['name'] = 'field_of_view_ya_unit'
    attr_fov_yb['name'] = 'field_of_view_yb_unit'
    attr_name['name'] = 'name'

    attr_direction['values'] = ['undistort']
    attr_fov_xa['values'] = [0.0]
    attr_fov_xb['values'] = [1.0]
    attr_fov_ya['values'] = [0.0]
    attr_fov_yb['values'] = [1.0]
    attr_name['values'] = [node_name]

    attributes.append(attr_direction)
    attributes.append(attr_fov_xa)
    attributes.append(attr_fov_xb)
    attributes.append(attr_fov_ya)
    attributes.append(attr_fov_yb)
    attributes.append(attr_name)

    lookup = const_load.ATTR_NAME_TO_NUKE_NODE_TYPE_AND_KNOB_NAME

    knobs_text = ''
    for attr in attributes:
        attr_name = attr['name']

        nuke_names = lookup.get(attr_name, None)
        assert nuke_names is None or isinstance(nuke_names, dict)
        if nuke_names is not None:
            attr_name = nuke_names[nuke_node_type]

        attr_frames = attr['frames']
        attr_values = attr['values']

        attr_value_str = ''
        if len(attr_frames) == 0:
            # Static attribute.
            assert len(attr_values) == 1
            attr_value_str = str(attr_values[0])
        else:
            # Animated attribute.
            assert len(attr_frames) == len(attr_values)
            attr_value_str = const.NUKE_FILE_SPEC_CURVE_START
            for frame, value in zip(attr_frames, attr_values):
                assert isinstance(frame, int)
                assert isinstance(value, float)
                attr_value_str += 'x%d %f ' % (frame, value)
            attr_value_str += const.NUKE_FILE_SPEC_CURVE_END

        attr_str = str(const.NUKE_FORMAT_SPEC_KNOB)
        attr_str = attr_str.format(name=attr_name, value=attr_value_str)
        knobs_text += attr_str

    knobs_text = knobs_text.strip('\n')
    return knobs_text


def _format_data_as_nuke_file(data_list):
    assert len(data_list) > 0
    data_str = str(const.NUKE_FILE_HEADER_COMMENT)
    data_str = data_str.format(
        module_version_name=const_proj.MODULE_FULL_NAME,
        project_homepage_url=const_proj.PROJECT_HOMEPAGE_URL,
    )
    for data in data_list:
        maya_node_type = data['node_type']
        lens_model_type = data['lens_model_type']
        node_name = data['node_name']

        lookup = const_load.NODE_TYPE_TO_LENS_MODEL_VALUE_TO_NUKE_NODE_TYPE
        nuke_node_type = lookup[maya_node_type][lens_model_type]

        attributes = data['attributes']
        knobs_text = _format_attributes_data_for_nuke_knobs(
            attributes, nuke_node_type, node_name
        )

        node_text = const.NUKE_FORMAT_SPEC_NODE.format(
            node_type=nuke_node_type, knobs=knobs_text, left_brace='{', right_brace='}'
        )
        data_str += node_text

    data_str = data_str.strip('\n')
    return data_str


def write_nuke_file(file_path, data_list):
    """
    Write data_list to a Nuke file.

    :returns: True or False, indicating success or not.
    :rtype: bool
    """
    data_str = _format_data_as_nuke_file(data_list)
    with open(file_path, 'w') as f:
        f.write(data_str)
    result = os.path.isfile(file_path)
    return result


def write_nuke_temp_file(data_list):
    """
    Write data_list to temporary Nuke file.

    :returns: String of the written file path, or None if writing failed.
    :rtype: str or None
    """
    data_str = _format_data_as_nuke_file(data_list)
    assert isinstance(data_str, pycompat.TEXT_TYPE)
    file_ext = const.EXT
    f = tempfile.NamedTemporaryFile(mode='w', suffix=file_ext, delete=False)
    if f.closed:
        LOG.error("Error: Couldn't open file.\n%r", f.name)
        return None
    f.write(data_str)
    f.close()
    return f.name
