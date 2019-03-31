"""
Configuration module.

GitHub issue #17.

A few of our tools need to have config files to read from and write to (hotkey manager, shelf and menus)

There are many places to store and read data from in Maya.

- A Maya node
- The Maya scene file.
- The Maya preferences
- The user's home directory (by-passing the Maya preferences)
- Configuration options in the install Maya module (configured for everyone).

This module needs to handle a number of use cases:

- Module to read/write config values.
- Store data in the scene file.
- Store data on a Maya node.
- Store data in the user's home directory.
- Store data in the Maya preferences.
- Read data from the config directory "MM_SOLVER_CONFIG"
"""

import json

import maya.cmds
import mmSolver.logger


LOG = mmSolver.logger.get_logger()


class Config(object):
    pass


def get_config_directories():
    """
    Get a list of directories to look in for config files.

    :return:
    """
    pass


def find_config_path(file_name):
    """
    Search though a list of defined paths for the config file name given.

    If an absolute file path is given, it is verified and returned.

    :param file_name: File name to find.
    :type file_name: str

    :return: Full config file name, or None.
    :rtype: str
    """
    pass


def read_config(file_name):
    """
    Read configuration file.

    :param file_name: The name of the config file, or an absolute file
                      path.
    :type file_name: str

    :return:
    """
    pass


def get_config(file_name):
    """
    Read a config file.

    :param file_name: The name of the config file, or an absolute file
                      path.
    :type file_name: str

    :return:
    :rtype:
    """
    pass


def get_config_value(file_name, default_value=None, *args):
    """
    Get a value from the config file.

    If the config file does not exist, or one of the argument (keys)
    does not exist, 'default_value' is returned.

    >>> x = get_config_value('config.json', 'key')
    >>> y = get_config_value('config.json', 'key', 'subkey')
    >>> z = get_config_value('config.json', 'key', 'subkey', 'subsubkey')

    :param file_name: The name of the config file, or an absolute file
                      path.
    :type file_name: str

    :param args: Hierarchy of keys to search for in the config.
                 For example 'config_data[arg1][arg2][arg3]'.
    :type args: str

    :param default_value: The value returned when the config file or
                          key doesn't exist.
    :type default_value: any type

    :return:
    :rtype
    """
    pass


def set_config_value():
    pass


def get_data_on_node_attr(node_name, attr_name):
    """
    Get data from an node attribute.

    :param node_name: Node to get data from.
    :type node_name: str

    :param attr_name: The name of the attribute to get data from.
    :type attr_name: str

    :return: Arbitrary Plain-Old-Data data structures.
    :rtype: list of dict
    """
    ret = []
    attr_data = get_value_on_node_attr(node_name, attr_name)
    if attr_data is None:
        return ret
    data = json.loads(attr_data)
    if isinstance(data, list):
        ret = data
    return ret


def set_data_on_node_attr(node_name, attr_name, data):
    """
    Set arbitrary Plain-Old-Data onto a node.attr path.

    :param node_name: Node to store data on.
    :type node_name: str

    :param attr_name: Attribute name to store data with.
    :type attr_name: str

    :param data: The data to store.
    :type data: list or dict
    """
    assert isinstance(attr_name, (str, unicode))
    assert isinstance(data, (list, dict))
    node_attr = node_name + '.' + attr_name

    new_attr_data = json.dumps(data)
    old_attr_data = maya.cmds.getAttr(node_attr)
    if old_attr_data == new_attr_data:
        return  # no change is needed.

    maya.cmds.setAttr(node_attr, lock=False)
    maya.cmds.setAttr(node_attr, new_attr_data, type='string')
    maya.cmds.setAttr(node_attr, lock=True)
    return


def get_value_on_node_attr(node_name, attr_name):
    """
    Get numeric value from an node attribute.

    :param node_name: Node to get value from.
    :type node_name: str

    :param attr_name: The name of the attribute to get value from.
    :type attr_name: str

    :return: A numeric value.
    :rtype: bool or float or int
    """
    attrs = maya.cmds.listAttr(node_name)
    if attr_name not in attrs:
        msg = 'attr_name not found on node: '
        msg += 'attr_name={name} node={node}'
        msg = msg.format(name=attr_name, node=node_name)
        raise ValueError(msg)
    node_attr = node_name + '.' + attr_name
    ret = maya.cmds.getAttr(node_attr)
    return ret


def set_value_on_node_attr(node_name, attr_name, data):
    """
    Set value onto a node.attr path.

    :param node_name: Node to store value on.
    :type node_name: str

    :param attr_name: Attribute name to store value with.
    :type attr_name: str

    :param data: The numeric value to store.
    :type data: bool or float or int

    ;return: Nothing.
    :rtype: None
    """
    assert isinstance(attr_name, (str, unicode))
    assert isinstance(data, (bool, float, int))
    node_attr = node_name + '.' + attr_name
    maya.cmds.setAttr(node_attr, lock=False)
    maya.cmds.setAttr(node_attr, data)
    maya.cmds.setAttr(node_attr, lock=True)
    return
