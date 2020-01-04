# Copyright (C) 2018, 2019 David Cattermole.
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
Querying and setting of state information on Collection nodes.
"""

import maya.cmds

import mmSolver.logger

import mmSolver.utils.configmaya as configmaya
import mmSolver.tools.solver.constant as const


LOG = mmSolver.logger.get_logger()


def ensure_attr_exists(node, attr_name,
                       attr_type=None,
                       default_value=None):
    """
    Ensure an attribute exists on the given node, or we create it.
    """
    attrs = maya.cmds.listAttr(node)
    if attr_name in attrs:
        return
    node_attr = node + '.' + attr_name
    numeric_attr_types = [
        'bool',
        'long', 'short', 'byte', 'char',
        'float', 'double',
        'doubleAngle', 'doubleLinear',
    ]
    if attr_type in numeric_attr_types:
        maya.cmds.addAttr(
            node,
            defaultValue=default_value,
            longName=attr_name,
            attributeType=attr_type,
        )
    elif attr_type in ['string']:
        maya.cmds.addAttr(
            node,
            longName=attr_name,
            dataType='string'
        )
        if isinstance(default_value, basestring):
            maya.cmds.setAttr(
                node_attr,
                default_value,
                type='string')
    else:
        raise TypeError('attr_type is not supported: %r' % attr_type)
    maya.cmds.setAttr(node_attr, lock=True)
    return


def __get_value_from_node(node, attr_name,
                          get_value_func,
                          attr_type, default_value):
    """
    Get a value from a node.

    .. note:: First create the attribute if it does not exist.

    """
    assert isinstance(node, basestring)
    assert isinstance(attr_name, basestring)
    ensure_attr_exists(
        node, attr_name,
        attr_type=attr_type,
        default_value=default_value
    )
    value = get_value_func(node, attr_name)
    integer_attr_types = [
        'long', 'short', 'byte', 'char'
    ]
    float_attr_types = [
        'float', 'double',
        'doubleAngle',
        'doubleLinear'
    ]
    if attr_type == 'bool':
        if not isinstance(value, bool):
            msg = 'Value queried is not bool: %r'
            msg = msg % type(value)
            raise TypeError(msg)
    elif attr_type in integer_attr_types:
        valid_types = (int, long)
        if not isinstance(value, valid_types):
            msg = 'Value queried is not int: %r'
            msg = msg % type(value)
            raise TypeError(msg)
    elif attr_type in float_attr_types:
        if not isinstance(value, float):
            msg = 'Value queried is not floating-point: %r'
            msg = msg % type(value)
            raise TypeError(msg)
    elif attr_type == 'string':
        # Note: An initialized string attribute will return None,
        # not '' (empty string), as one would expect at first glance.
        # valid_types = (basestring, unicode, dict, list)
        pass
        # if value is not None and isinstance(value, valid_types) is False:
        #     msg = 'Value queried is not string: %r'
        #     msg = msg % type(value)
        #     raise TypeError(msg)
    else:
        msg = 'Value queried is not valid type: attr_type=%r value_type=%r'
        msg = msg % (attr_type, type(value))
        raise TypeError(msg)

    return value


def __set_value_on_node(node, attr_name, value,
                        set_value_func,
                        attr_type, default_value):
    """
    Set a value on a node.

    .. note:: First create the attribute if it does not exist.

    """
    assert isinstance(node, basestring)
    assert isinstance(attr_name, basestring)
    integer_attr_types = [
        'long', 'short', 'byte', 'char'
    ]
    float_attr_types = [
        'float', 'double',
        'doubleAngle',
        'doubleLinear'
    ]
    if attr_type in ['bool']:
        if not isinstance(value, bool):
            msg = 'Value queried is not bool: %r' % type(value)
            raise TypeError(msg)
    elif attr_type in integer_attr_types:
        valid_types = (int, long)
        if not isinstance(value, valid_types):
            msg = 'Value queried is not integer: %r' % type(value)
            raise TypeError(msg)
    elif attr_type in float_attr_types:
        if not isinstance(value, float):
            msg = 'Value queried is not floating-point: %r' % type(value)
            raise TypeError(msg)
    elif attr_type in ['string']:
        valid_types = (basestring, unicode, list, dict)
        if not isinstance(value, valid_types):
            msg = 'Value queried is not string: %r' % type(value)
            raise TypeError(msg)
    else:
        msg = 'Value queried is not valid type: attr_type=%r value_type=%r'
        msg = msg % (attr_type, type(value))
        raise TypeError(msg)
    ensure_attr_exists(node, attr_name, attr_type, default_value)
    set_value_func(node, attr_name, value)
    return


def get_value_from_node(node, attr_name,
                        attr_type=None,
                        default_value=None):
    """
    Get a value from a node.

    .. note:: First create the attribute if it does not exist.

    """
    func = configmaya.get_node_option
    value = __get_value_from_node(
        node, attr_name,
        func,
        attr_type, default_value)
    return value


def set_value_on_node(node, attr_name, value,
                      attr_type=None,
                      default_value=None):
    """
    Set a value on a node.

    .. note:: First create the attribute if it does not exist.

    """
    func = configmaya.set_node_option
    __set_value_on_node(
        node, attr_name, value,
        func,
        attr_type, default_value)
    return


def get_value_structure_from_node(node, attr_name,
                        attr_type=None,
                        default_value=None):
    """
    Get a value from a node.

    .. note:: First create the attribute if it does not exist.

    """
    func = configmaya.get_node_option_structure
    value = __get_value_from_node(
        node, attr_name,
        func,
        attr_type, default_value)
    return value


def set_value_structure_on_node(node, attr_name, value,
                      attr_type=None,
                      default_value=None):
    """
    Set a value on a node.

    .. note:: First create the attribute if it does not exist.

    """
    func = configmaya.set_node_option_structure
    __set_value_on_node(
        node, attr_name, value,
        func,
        attr_type, default_value)
    return


#######################################################################


def get_override_current_frame_from_collection(col):
    """
    Get the value of 'Override Current Frame', from a Collection.

    :param col: The Collection to query.
    :type col: Collection

    :returns: True or False.
    :rtype: bool
    """
    value = get_value_from_node(
        col.get_node(),
        const.OVERRIDE_CURRENT_FRAME_ATTR,
        attr_type=const.OVERRIDE_CURRENT_FRAME_ATTR_TYPE,
        default_value=const.OVERRIDE_CURRENT_FRAME_DEFAULT_VALUE,
    )
    return value


def set_override_current_frame_on_collection(col, value):
    """
    Set the value of 'Override Current Frame' on a Collection.

    :param col: The Collection to change.
    :type col: Collection

    :param value: Value to set to.
    :type value: bool
    """
    set_value_on_node(
        col.get_node(),
        const.OVERRIDE_CURRENT_FRAME_ATTR,
        value,
        attr_type=const.OVERRIDE_CURRENT_FRAME_ATTR_TYPE,
        default_value=const.OVERRIDE_CURRENT_FRAME_DEFAULT_VALUE,
    )
    return


#######################################################################


def get_attribute_toggle_animated_from_collection(col):
    """
    Get the value of 'Attributes Toggle Animated', from a Collection.

    :param col: The Collection to query.
    :type col: Collection

    :returns: True or False.
    :rtype: bool
    """
    value = get_value_from_node(
        col.get_node(),
        const.ATTRIBUTE_TOGGLE_ANIMATED_ATTR,
        attr_type=const.ATTRIBUTE_TOGGLE_ANIMATED_ATTR_TYPE,
        default_value=const.ATTRIBUTE_TOGGLE_ANIMATED_DEFAULT_VALUE
    )
    return value


def set_attribute_toggle_animated_on_collection(col, value):
    """
    Set the value of 'Attributes Toggle Animated' on a Collection.

    :param col: The Collection to change.
    :type col: Collection

    :param value: Value to set to.
    :type value: bool
    """
    set_value_on_node(
        col.get_node(),
        const.ATTRIBUTE_TOGGLE_ANIMATED_ATTR,
        value,
        attr_type=const.ATTRIBUTE_TOGGLE_ANIMATED_ATTR_TYPE,
        default_value=const.ATTRIBUTE_TOGGLE_ANIMATED_DEFAULT_VALUE
    )
    return


#######################################################################


def get_attribute_toggle_static_from_collection(col):
    """
    Get the value of 'Attributes Toggle Static', from a Collection.

    :param col: The Collection to query.
    :type col: Collection

    :returns: True or False.
    :rtype: bool
    """
    value = get_value_from_node(
        col.get_node(),
        const.ATTRIBUTE_TOGGLE_STATIC_ATTR,
        attr_type=const.ATTRIBUTE_TOGGLE_STATIC_ATTR_TYPE,
        default_value=const.ATTRIBUTE_TOGGLE_STATIC_DEFAULT_VALUE
    )
    return value


def set_attribute_toggle_static_on_collection(col, value):
    """
    Set the value of 'Attributes Toggle Static' on a Collection.

    :param col: The Collection to change.
    :type col: Collection

    :param value: Value to set to.
    :type value: bool
    """
    set_value_on_node(
        col.get_node(),
        const.ATTRIBUTE_TOGGLE_STATIC_ATTR,
        value,
        attr_type=const.ATTRIBUTE_TOGGLE_STATIC_ATTR_TYPE,
        default_value=const.ATTRIBUTE_TOGGLE_STATIC_DEFAULT_VALUE
    )
    return


#######################################################################


def get_attribute_toggle_locked_from_collection(col):
    """
    Get the value of 'Attributes Toggle Locked', from a Collection.

    :param col: The Collection to query.
    :type col: Collection

    :returns: True or False.
    :rtype: bool
    """
    value = get_value_from_node(
        col.get_node(),
        const.ATTRIBUTE_TOGGLE_LOCKED_ATTR,
        attr_type=const.ATTRIBUTE_TOGGLE_LOCKED_ATTR_TYPE,
        default_value=const.ATTRIBUTE_TOGGLE_LOCKED_DEFAULT_VALUE
    )
    return value


def set_attribute_toggle_locked_on_collection(col, value):
    """
    Set the value of 'Attributes Toggle Locked' on a Collection.

    :param col: The Collection to change.
    :type col: Collection

    :param value: Value to set to.
    :type value: bool
    """
    set_value_on_node(
        col.get_node(),
        const.ATTRIBUTE_TOGGLE_LOCKED_ATTR,
        value,
        attr_type=const.ATTRIBUTE_TOGGLE_LOCKED_ATTR_TYPE,
        default_value=const.ATTRIBUTE_TOGGLE_LOCKED_DEFAULT_VALUE
    )
    return


#######################################################################


def get_object_toggle_camera_from_collection(col):
    """
    Get the value of 'Objects Toggle Camera', from a Collection.

    :param col: The Collection to query.
    :type col: Collection

    :returns: True or False.
    :rtype: bool
    """
    value = get_value_from_node(
        col.get_node(),
        const.OBJECT_TOGGLE_CAMERA_ATTR,
        attr_type=const.OBJECT_TOGGLE_CAMERA_ATTR_TYPE,
        default_value=const.OBJECT_TOGGLE_CAMERA_DEFAULT_VALUE,
    )
    return value


def set_object_toggle_camera_on_collection(col, value):
    """
    Set the value of 'Objects Toggle Camera' on a Collection.

    :param col: The Collection to change.
    :type col: Collection

    :param value: Value to set to.
    :type value: bool
    """
    set_value_on_node(
        col.get_node(),
        const.OBJECT_TOGGLE_CAMERA_ATTR,
        value,
        attr_type=const.OBJECT_TOGGLE_CAMERA_ATTR_TYPE,
        default_value=const.OBJECT_TOGGLE_CAMERA_DEFAULT_VALUE,
    )
    return


#######################################################################


def get_object_toggle_marker_from_collection(col):
    """
    Get the value of 'Objects Toggle Marker', from a Collection.

    :param col: The Collection to query.
    :type col: Collection

    :returns: True or False.
    :rtype: bool
    """
    value = get_value_from_node(
        col.get_node(),
        const.OBJECT_TOGGLE_MARKER_ATTR,
        attr_type=const.OBJECT_TOGGLE_MARKER_ATTR_TYPE,
        default_value=const.OBJECT_TOGGLE_MARKER_DEFAULT_VALUE,
    )
    return value


def set_object_toggle_marker_on_collection(col, value):
    """
    Set the value of 'Objects Toggle Marker' on a Collection.

    :param col: The Collection to change.
    :type col: Collection

    :param value: Value to set to.
    :type value: bool
    """
    set_value_on_node(
        col.get_node(),
        const.OBJECT_TOGGLE_MARKER_ATTR,
        value,
        attr_type=const.OBJECT_TOGGLE_MARKER_ATTR_TYPE,
        default_value=const.OBJECT_TOGGLE_MARKER_DEFAULT_VALUE,
    )
    return


#######################################################################


def get_object_toggle_bundle_from_collection(col):
    """
    Get the value of 'Objects Toggle Bundle', from a Collection.

    :param col: The Collection to query.
    :type col: Collection

    :returns: True or False.
    :rtype: bool
    """
    value = get_value_from_node(
        col.get_node(),
        const.OBJECT_TOGGLE_BUNDLE_ATTR,
        attr_type=const.OBJECT_TOGGLE_BUNDLE_ATTR_TYPE,
        default_value=const.OBJECT_TOGGLE_BUNDLE_DEFAULT_VALUE,
    )
    return value


def set_object_toggle_bundle_on_collection(col, value):
    """
    Set the value of 'Objects Toggle Bundle' on a Collection.

    :param col: The Collection to change.
    :type col: Collection

    :param value: Value to set to.
    :type value: bool
    """
    set_value_on_node(
        col.get_node(),
        const.OBJECT_TOGGLE_BUNDLE_ATTR,
        value,
        attr_type=const.OBJECT_TOGGLE_BUNDLE_ATTR_TYPE,
        default_value=const.OBJECT_TOGGLE_BUNDLE_DEFAULT_VALUE,
    )
    return


#######################################################################


def get_solver_tab_from_collection(col):
    """
    Get the value of solver 'tab', from a Collection.

    :param col: The Collection to query.
    :type col: Collection

    :returns: The tab name.
    :rtype: str
    """
    value = get_value_from_node(
        col.get_node(),
        const.SOLVER_TAB_ATTR,
        attr_type=const.SOLVER_TAB_ATTR_TYPE,
        default_value=const.SOLVER_TAB_DEFAULT_VALUE,
    )
    return value


def set_solver_tab_on_collection(col, value):
    """
    Set the value of solver 'tab' on a Collection.

    :param col: The Collection to change.
    :type col: Collection

    :param value: Value to set to.
    :type value: str
    """
    set_value_on_node(
        col.get_node(),
        const.SOLVER_TAB_ATTR,
        value,
        attr_type=const.SOLVER_TAB_ATTR_TYPE,
        default_value=const.SOLVER_TAB_DEFAULT_VALUE,
    )
    return


#######################################################################


def get_solver_range_type_from_collection(col):
    """
    Get the value of solver 'Range Type', from a Collection.

    :param col: The Collection to query.
    :type col: Collection

    :returns: An integer value in const.RANGE_TYPE_VALUE_LIST.
    :rtype: bool
    """
    value = get_value_from_node(
        col.get_node(),
        const.SOLVER_RANGE_TYPE_ATTR,
        attr_type=const.SOLVER_RANGE_TYPE_ATTR_TYPE,
        default_value=const.SOLVER_RANGE_TYPE_DEFAULT_VALUE,
    )
    return value


def set_solver_range_type_on_collection(col, value):
    """
    Set the value of solver 'Range Type' on a Collection.

    :param col: The Collection to change.
    :type col: Collection

    :param value: Value to set to.
    :type value: int
    """
    set_value_on_node(
        col.get_node(),
        const.SOLVER_RANGE_TYPE_ATTR,
        value,
        attr_type=const.SOLVER_RANGE_TYPE_ATTR_TYPE,
        default_value=const.SOLVER_RANGE_TYPE_DEFAULT_VALUE,
    )
    return


#######################################################################


def get_solver_frames_from_collection(col):
    """
    Get the value of solver 'Frames', from a Collection.

    :param col: The Collection to query.
    :type col: Collection

    :returns: The string representation of the frames.
    :rtype: str
    """
    value = get_value_from_node(
        col.get_node(),
        const.SOLVER_FRAMES_ATTR,
        attr_type=const.SOLVER_FRAMES_ATTR_TYPE,
        default_value=const.SOLVER_FRAMES_DEFAULT_VALUE,
    )
    return value


def set_solver_frames_on_collection(col, value):
    """
    Set the value of solver 'Frames' on a Collection.

    :param col: The Collection to change.
    :type col: Collection

    :param value: Value to set to.
    :type value: str
    """
    set_value_on_node(
        col.get_node(),
        const.SOLVER_FRAMES_ATTR,
        value,
        attr_type=const.SOLVER_FRAMES_ATTR_TYPE,
        default_value=const.SOLVER_FRAMES_DEFAULT_VALUE,
    )
    return


#######################################################################


def get_solver_increment_by_frame_from_collection(col):
    """
    Get the value of solver 'Increment By Frame', from a Collection.

    :param col: The Collection to query.
    :type col: Collection

    :returns: The frame number value.
    :rtype: int
    """
    value = get_value_from_node(
        col.get_node(),
        const.SOLVER_INCREMENT_BY_FRAME_ATTR,
        attr_type=const.SOLVER_INCREMENT_BY_FRAME_ATTR_TYPE,
        default_value=const.SOLVER_INCREMENT_BY_FRAME_DEFAULT_VALUE,
    )
    return value


def set_solver_increment_by_frame_on_collection(col, value):
    """
    Set the value of solver 'Increment By Frame' on a Collection.

    :param col: The Collection to change.
    :type col: Collection

    :param value: Value to set to.
    :type value: int
    """
    set_value_on_node(
        col.get_node(),
        const.SOLVER_INCREMENT_BY_FRAME_ATTR,
        value,
        attr_type=const.SOLVER_INCREMENT_BY_FRAME_ATTR_TYPE,
        default_value=const.SOLVER_INCREMENT_BY_FRAME_DEFAULT_VALUE,
    )
    return


#######################################################################


def get_solver_root_frames_from_collection(col):
    """
    Get the value of solver 'Root Frames', from a Collection.

    :param col: The Collection to query.
    :type col: Collection

    :returns: The string representation of the frames.
    :rtype: str
    """
    value = get_value_from_node(
        col.get_node(),
        const.SOLVER_ROOT_FRAMES_ATTR,
        attr_type=const.SOLVER_ROOT_FRAMES_ATTR_TYPE,
        default_value=const.SOLVER_ROOT_FRAMES_DEFAULT_VALUE,
    )
    return value


def set_solver_root_frames_on_collection(col, value):
    """
    Set the value of solver 'Root Frames' on a Collection.

    :param col: The Collection to change.
    :type col: Collection

    :param value: Value to set to.
    :type value: str
    """
    set_value_on_node(
        col.get_node(),
        const.SOLVER_ROOT_FRAMES_ATTR,
        value,
        attr_type=const.SOLVER_ROOT_FRAMES_ATTR_TYPE,
        default_value=const.SOLVER_ROOT_FRAMES_DEFAULT_VALUE,
    )
    return


#######################################################################


def get_solver_only_root_frames_from_collection(col):
    """
    Get the value of solver 'Only Root Frames', from a Collection.

    :param col: The Collection to query.
    :type col: Collection

    :returns: A boolean, do we solve only root frames, or not?
    :rtype: bool
    """
    value = get_value_from_node(
        col.get_node(),
        const.SOLVER_ONLY_ROOT_FRAMES_ATTR,
        attr_type=const.SOLVER_ONLY_ROOT_FRAMES_ATTR_TYPE,
        default_value=const.SOLVER_ONLY_ROOT_FRAMES_DEFAULT_VALUE,
    )
    return value


def set_solver_only_root_frames_on_collection(col, value):
    """
    Set the value of solver 'Only Root Frames' on a Collection.

    :param col: The Collection to change.
    :type col: Collection

    :param value: Value to set to.
    :type value: bool
    """
    set_value_on_node(
        col.get_node(),
        const.SOLVER_ONLY_ROOT_FRAMES_ATTR,
        value,
        attr_type=const.SOLVER_ONLY_ROOT_FRAMES_ATTR_TYPE,
        default_value=const.SOLVER_ONLY_ROOT_FRAMES_DEFAULT_VALUE,
    )
    return


#######################################################################


def get_solver_global_solve_from_collection(col):
    """
    Get the value of solver 'Global Solve', from a Collection.

    :param col: The Collection to query.
    :type col: Collection

    :returns: A boolean, do we solve all frames and attributes together, or not?
    :rtype: bool
    """
    value = get_value_from_node(
        col.get_node(),
        const.SOLVER_GLOBAL_SOLVE_ATTR,
        attr_type=const.SOLVER_GLOBAL_SOLVE_ATTR_TYPE,
        default_value=const.SOLVER_GLOBAL_SOLVE_DEFAULT_VALUE,
    )
    return value


def set_solver_global_solve_on_collection(col, value):
    """
    Set the value of solver 'Global Solve' on a Collection.

    :param col: The Collection to change.
    :type col: Collection

    :param value: Value to set to.
    :type value: bool
    """
    set_value_on_node(
        col.get_node(),
        const.SOLVER_GLOBAL_SOLVE_ATTR,
        value,
        attr_type=const.SOLVER_GLOBAL_SOLVE_ATTR_TYPE,
        default_value=const.SOLVER_GLOBAL_SOLVE_DEFAULT_VALUE,
    )
    return
