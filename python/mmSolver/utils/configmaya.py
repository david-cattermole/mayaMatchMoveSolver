# Copyright (C) 2019 David Cattermole.
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
Configuration module for getting/setting config data inside Maya.

There are many places to store and read data from in Maya.

- A Maya node
- The Maya scene file.
- The Python shared variables.
- The Maya preferences.

Each type of storage can be considered to have a different life-time.

The levels are (in ascending order):

- Maya Node
- Maya Scene
- Maya Session
- Maya Preferences
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json

import maya.cmds
import mmSolver.logger
import mmSolver.utils.constant as const
import mmSolver.utils.python_compat as pycompat

LOG = mmSolver.logger.get_logger()


def __add_node_option_attr(node_name, attr_name, value):
    """
    Create an attribute on a node, with the type of the given value.

    .. note: The attribute is assumed not to already exist.

    :rtype: None
    """
    if isinstance(value, bool):
        maya.cmds.addAttr(node_name, longName=attr_name, attributeType='bool')
    elif isinstance(value, int):
        maya.cmds.addAttr(node_name, longName=attr_name, attributeType='long')
    elif isinstance(value, float):
        maya.cmds.addAttr(node_name, longName=attr_name, attributeType='float')
    elif isinstance(value, pycompat.TEXT_TYPE):
        maya.cmds.addAttr(node_name, longName=attr_name, dataType='string')
    else:
        msg = "Type of 'value' is not supported."
        raise TypeError(msg)
    return


def get_node_option(node_name, attr_name, default=None):
    """
    Get value from an node attribute.

    :param node_name: Node to get value from. Node must exist before
                      running function!
    :type node_name: str

    :param attr_name: The name of the attribute to get value from.
    :type attr_name: str

    :param default: Value to be returned if the value does not exist.
    :type default: any

    :return: A value from the node.
    :rtype: bool, float, int or str
    """
    attrs = maya.cmds.listAttr(node_name)
    if attr_name not in attrs:
        msg = 'attr_name not found on node: attr=%r node=%r'
        LOG.debug(msg, attr_name, node_name)
        return default
    node_attr = node_name + '.' + attr_name
    ret = maya.cmds.getAttr(node_attr)
    return ret


def set_node_option(node_name, attr_name, value, add_attr=None):
    """
    Set value onto a node.attr path.

    .. note: If you use use add_attr, be aware that the first value
        type will determine the attribute automatically created.
        Once created the attribute type cannot be changed.

    :param node_name: Node to store value on.
    :type node_name: str

    :param attr_name: Attribute name to store value with.
    :type attr_name: str

    :param value: The value to store.
    :type value: bool, float, int or str

    :param add_attr: Add attribute to the given node, if the attribute
                     does not already exist.
    :type add_attr: bool

    :rtype: None
    """
    assert isinstance(attr_name, pycompat.TEXT_TYPE)
    assert isinstance(value, (bool, float, int, pycompat.TEXT_TYPE))
    if add_attr is None:
        add_attr = False
    assert isinstance(add_attr, bool)
    node_attr = node_name + '.' + attr_name

    attrs = maya.cmds.listAttr(node_name)
    if attr_name not in attrs:
        if add_attr is False:
            msg = 'attr_name not found on node: attr=%r node=%r'
            LOG.debug(msg, attr_name, node_name)
        else:
            __add_node_option_attr(node_name, attr_name, value)

    # Set value
    maya.cmds.setAttr(node_attr, lock=False)
    if isinstance(value, (bool, float, int)):
        maya.cmds.setAttr(node_attr, value)
    elif isinstance(value, pycompat.TEXT_TYPE):
        maya.cmds.setAttr(node_attr, value, type='string')
    maya.cmds.setAttr(node_attr, lock=True)
    return


def get_node_option_structure(node_name, attr_name):
    """
    Get data structure from a node attribute.

    :param node_name: Node to get data from.
    :type node_name: str

    :param attr_name: The name of the attribute to get data from.
    :type attr_name: str

    :return: Arbitrary Plain-Old-Data data structures, can be a list or
             dictionary.
    :rtype: dict or list or None
    """
    ret = None
    attr_data = get_node_option(node_name, attr_name)
    if attr_data is None:
        return ret
    ret = json.loads(attr_data)
    return ret


def set_node_option_structure(node_name, attr_name, data_struct, add_attr=None):
    """
    Set arbitrary Plain-Old-Data onto a node.attr path.

    .. note: If you use add_attr, be aware that the first value
        type will determine the attribute automatically created.
        Once created the attribute type cannot be changed.

    :param node_name: Node to store data on.
    :type node_name: str

    :param attr_name: Attribute name to store data with.
    :type attr_name: str

    :param data_struct: The data to store.
    :type data_struct: dict or list

    :param add_attr: Add attribute to the given node, if the attribute
                     does not already exist.
    :type add_attr: bool

    :rtype: None
    """
    assert isinstance(attr_name, pycompat.TEXT_TYPE)
    assert isinstance(data_struct, (list, dict))

    new_attr_data = json.dumps(data_struct)
    old_attr_data = get_node_option(node_name, attr_name)
    if old_attr_data == new_attr_data:
        # No change is needed.
        return

    set_node_option(node_name, attr_name, new_attr_data, add_attr=add_attr)
    return


def get_scene_option(name, default=None):
    """
    Get a value from the scene.

    :param name: Get the option with this name.
    :type name: str

    :param default: Value to be returned if the value does not exist.
    :type default: any

    :return: The value of the scene option, or 'default' if the 'name'
             does not exist.
    :rtype: any
    """
    if not maya.cmds.objExists(const.SCENE_DATA_NODE):
        maya.cmds.createNode(
            const.SCENE_DATA_NODE_TYPE, name=const.SCENE_DATA_NODE, skipSelect=True
        )
    data = get_node_option_structure(const.SCENE_DATA_NODE, const.SCENE_DATA_ATTR)
    value = default
    if isinstance(data, dict):
        value = data.get(name, default)
    return value


def set_scene_option(name, value, add_attr=None):
    """
    Set a value in the scene.

    :param name: Set the option with this name.
    :type name: str

    :param value: Value to set.
    :type value: any

    :param add_attr: Add attribute to the scene, if the attribute
                     does not already exist.
    :type add_attr: bool

    :rtype: None
    """
    if not maya.cmds.objExists(const.SCENE_DATA_NODE):
        maya.cmds.createNode(
            const.SCENE_DATA_NODE_TYPE, name=const.SCENE_DATA_NODE, skipSelect=True
        )
    data = get_node_option_structure(const.SCENE_DATA_NODE, const.SCENE_DATA_ATTR)
    if data is None:
        data = dict()
    data[name] = value
    set_node_option_structure(
        const.SCENE_DATA_NODE,
        const.SCENE_DATA_ATTR,
        data,
        add_attr=add_attr,
    )
    return


def get_preference_option(name, default=None):
    """
    Get a Maya preference from Maya (optionVar).

    :param name: Name key to get from Maya preferences.
    :type name: str

    :param default: If the preference option is not found, return this value.
    :type default: any

    :return: The value found under 'name', or the 'default' value.
    :rtype: int, float or str
    """
    assert isinstance(name, pycompat.TEXT_TYPE)
    exists = maya.cmds.optionVar(exists=name)
    if exists is False:
        return default
    value = maya.cmds.optionVar(query=name)
    return value


def set_preference_option(name, value):
    """
    Set a Maya preference to Maya (optionVar).

    :param name: Name key to set to Maya preferences.
    :type name: str

    :param value: Value to set.
    :type value: int, float or str
    """
    assert isinstance(name, pycompat.TEXT_TYPE)
    if isinstance(value, int):
        maya.cmds.optionVar(intValue=(name, value))
    elif isinstance(value, float):
        maya.cmds.optionVar(floatValue=(name, value))
    elif isinstance(value, pycompat.TEXT_TYPE):
        maya.cmds.optionVar(stringValue=(name, value))
    else:
        msg = 'Invalid type for value argument. name=%r value=%r type=%r'
        raise TypeError(msg % (name, value, type(value)))
    return value


def save_preference_options():
    """
    Write all Maya preferences to disk.
    """
    cmd = 'SavePreferences;'
    maya.mel.eval(cmd)
    return
