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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.utils.node as node_utils
import mmSolver.utils.animcurve as anim_utils
import mmSolver.tools.loadlens.constant as const


LOG = mmSolver.logger.get_logger()


LensObject = collections.namedtuple(
    'LensObject',
    [
        'name',
        'node_type',
        'camera_parameters',
        'fov_parameters',
        'lens_parameters',
    ],
)


def parse_file(file_path):
    LOG.info('Reading file path: %r', file_path)
    lines = []
    with open(file_path, 'r') as f:
        lines = f.readlines()
    nuke_node_type = None
    node_name = None
    cam_parameters = {}
    fov_parameters = {}
    lens_parameters = {}
    for line in lines:
        # Comments in Nuke scripts start with '#' and comments will be
        # ignored.
        line = line.partition('#')[0].strip()

        if (
            line.startswith('LD_3DE_') or line.startswith('LD_3DE4_')
        ) and line.endswith(' {'):
            nuke_node_type = line.partition('{')[0].strip()
            continue

        if nuke_node_type is not None:
            split = line.split(' ')

            name = None
            times = None  # None means a static parameter.
            values = None
            param_anim_type = None
            if len(split) > 1 and '{{curve' in split[1] and '}}' in split[-1]:
                name = split[0]

                # Remove '{{curve' and '}}'.
                times_and_values = split[2:-1]

                # Times start with 'x', such as 'x42' or 'x1'.
                times = [int(t.strip('x')) for t in times_and_values[0::2]]

                # Values are expected to be floating point (but Nuke
                # allows other data types such as integer values).
                values = [float(v) for v in times_and_values[1::2]]
                assert len(times) == len(values)

            elif len(split) == 2:
                name = split[0]
                values = split[1]
            else:
                # Unknown line type, it will be ignored.
                continue

            if name == 'name' and times is None:
                node_name = values
            else:
                if times is None:
                    clean_string = values.replace('.', '').replace('-', '')
                    is_digit = clean_string.isdigit()
                    if is_digit:
                        values = float(values)
                    else:
                        # Skip parameters with unsupported types.
                        continue

                if name.startswith('tde4_'):
                    cam_parameters[name] = (times, values)
                elif name.startswith('field_of_view_'):
                    fov_parameters[name] = (times, values)
                else:
                    lens_parameters[name] = (times, values)

    # Check for invalid data.
    if nuke_node_type is None:
        return None
    if node_name is None:
        return None

    lens_object = LensObject(
        name=node_name,
        node_type=nuke_node_type,
        camera_parameters=cam_parameters,
        fov_parameters=fov_parameters,
        lens_parameters=lens_parameters,
    )
    return lens_object


def _remove_keyframes(node, attr_name):
    node_attr = '{}.{}'.format(node, attr_name)
    anim_curves = (
        maya.cmds.listConnections(node_attr, type='animCurve', source=True) or []
    )
    if len(anim_curves) > 0:
        # TODO: This will delete the node along with the keyframes.
        #  This is caused by Maya's behavior to automatically delete
        #  nodes that do not have incoming connections.
        maya.cmds.cutKey(node, clear=True, time=(), float=(), attribute=attr_name)
    return


def _set_static_attr(node, attr_name, value):
    node_attr = '{}.{}'.format(node, attr_name)

    locked = maya.cmds.getAttr(node_attr)
    if locked is True:
        LOG.info('Skipping locked attribute: %r', node_attr)
        return False

    _remove_keyframes(node, attr_name)

    connection_nodes = maya.cmds.listConnections(node_attr, source=True) or []
    if len(connection_nodes) > 0:
        LOG.info('Skipping connected attribute: %r', node_attr)
        return False

    maya.cmds.setAttr(node_attr, value)
    return True


def _set_animated_attr(node, attr_name, times, values):
    assert len(times) == len(values)
    assert len(times) > 0
    node_attr = node + '.' + attr_name

    _remove_keyframes(node, attr_name)

    connection_nodes = maya.cmds.listConnections(node_attr, source=True) or []
    if len(connection_nodes) > 0:
        LOG.info('Skipping connected attribute: %r', node_attr)
        return False

    anim_utils.create_anim_curve_node_apione(times, values, node_attr)
    return True


def _set_lens_model(node, value):
    maya_node_type = maya.cmds.nodeType(node)
    if maya_node_type != const.MAYA_MM_LENS_MODEL_3DE:
        # Only 'mmLensModel3de' is supported for now.
        return False

    attr_name = 'lensModel'
    node_attr = '{}.{}'.format(node, attr_name)

    locked = maya.cmds.getAttr(node_attr)
    if locked is True:
        LOG.info('Skipping locked attribute: %r', node_attr)
        return False

    _remove_keyframes(node, attr_name)

    connection_nodes = maya.cmds.listConnections(node_attr, source=True) or []
    if len(connection_nodes) > 0:
        LOG.info('Skipping connected attribute: %r', node_attr)
        return False

    lookup = const.NUKE_NODE_TYPE_TO_NODE_TYPE_TO_LENS_MODEL_VALUE
    node_type_to_lens_model_value = lookup.get(value, {})
    value = node_type_to_lens_model_value.get(maya_node_type)
    if value is None:
        return False

    maya.cmds.setAttr(node_attr, value)
    return True


def apply_to_lens(lens_object, lens):
    assert isinstance(lens_object, LensObject)
    LOG.info('Apply lens object to lens: %r', lens)

    object_node_type = lens_object.node_type
    if object_node_type is None:
        msg = 'Lens values do not have a valid node type, skipping apply.'
        LOG.warn(msg)
        return False

    lens_parameters = lens_object.lens_parameters
    if len(lens_parameters) == 0:
        msg = 'Lens values do not have any lens parameters, skipping apply.'
        LOG.warn(msg)
        return False

    lens_node = lens.get_node()
    if lens_node is None:
        msg = 'Could not get Lens node, Lens is not valid: %r'
        LOG.error(msg, lens)
        return False

    _set_lens_model(lens_node, object_node_type)

    set_attributes_count = 0
    for param_name, value in lens_parameters.items():
        key = (object_node_type, param_name)
        attr_map = const.NODE_TYPE_PARAMETER_NAME_TO_ATTRIBUTE_NAMES
        attr_names = attr_map.get(key, [])
        if len(attr_names) == 0:
            continue

        for attr_name in attr_names:
            exists = node_utils.attribute_exists(attr_name, lens_node)
            if exists is False:
                msg = 'Attribute %r does not exist on node %r'
                LOG.warn(msg, attr_name, lens_node)
                continue
            times, values = value
            if times is None:
                result = _set_static_attr(lens_node, attr_name, values)
                set_attributes_count += int(bool(result))
            else:
                result = _set_animated_attr(lens_node, attr_name, times, values)
                set_attributes_count += int(bool(result))

    # Rename node.
    new_name = lens_object.name
    if new_name:
        maya.cmds.rename(lens_node, new_name)

    success = set_attributes_count > 0
    return success
