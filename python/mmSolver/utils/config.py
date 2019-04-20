"""
Configuration module.

GitHub issue #17.

A few of our tools need to have config files to read from and write to
(hotkey manager, shelf and menus).

There are many places to store and read data within Maya.

- The user's home directory (by-passing the Maya preferences)
- Configuration options in the install Maya module (configured for everyone).

This module needs to handle a number of use cases:

- Module to read/write config values.
- Store data in the user's home directory.
- Read data from the config directory "MMSOLVER_CONFIG_PATH"

"""

import os
import json

import mmSolver.logger
import mmSolver.utils.constant as const

LOG = mmSolver.logger.get_logger()


def get_dirs(envvar_name=None):
    """
    Get a list of directories to look in for config files.

    :param envvar_name: The environment variable to query for a list 
                        of directories.
    :type envvar_name: str or None

    :return: List of config directories.
    """
    if envvar_name is None:
        envvar_name = const.CONFIG_PATH_VAR_NAME
    result = []
    return result


def find_path(file_name, search_paths):
    """
    Search though a list of defined paths for the config file name given.

    If an absolute file path is given, it is verified and returned.

    :param file_name: File name to find.
    :type file_name: str

    :return: Full config file name, or None.
    :rtype: str
    """
    pass


def read_data(file_path):
    """
    Read configuration file and return the data embedded.

    :param file_path: The absolute file path to a config file.
    :type file_path: str

    :return: Dictionary, list or None, depending what the given file 
             contains.
    :rtype: dict, list or None
    """
    pass


def write_data(data, file_path):
    """
    Write the given configuration data to a file.

    :param data: Configuration data to write. The data should be 
                 plain-old-(Python)data types, like lists, float, int, 
                 string and dict.
    :type data: dict or list

    :param file_path: A valid absolute file path.
    :type file_path: str
    """
    pass


def exists(data, key):
    """
    Does the key exist in data?

    :param data: The name of the config file, or an absolute file
                      path.
    :type data: str

    :param key: Hierarchy of keys separated by forward slash to search 
                for in the config. 
                For example 'data[arg1][arg2][arg3]'.
    :type key: str

    :return:
    :rtype
    """
    pass


def get_value(data, key, default_value=None):
    """
    Get a value from the config data.

    If the config data value does not exist, or one of the argument (keys)
    does not exist, 'default_value' is returned.

    >>> data = read_data('/path/to/config.json')
    >>> x = get_value(data, 'key')
    >>> y = get_value(data, 'key/subkey')
    >>> z = get_value(data, 'key/subkey/subsubkey')

    :param data: The configuration data, as a Python dict (plain-old-data).
    :type data: dict

    :param key: Hierarchy of keys separated by forward slash to search 
                for in the config. 
                For example 'data[arg1][arg2][arg3]'.
    :type key: str

    :param default_value: The value returned when the config file or
                          key doesn't exist.
    :type default_value: any type

    :return:
    :rtype
    """
    pass


def set_value(data, key, value):
    """
    Set a value in the given configuration data.

    :returns: A copy of the configuration data with the modification 
              made.
    :rtype: dict or list
    """
    pass


class Config(object):
    def __init__(self, file_path):
        self.file_path = file_path
        self._values = {}
        self._autoread = True
        self._autowrite = True

    def read(self):
        pass

    def write(self):
        pass

    def exists(self, key):
        pass
    
    def get_value(self, key, default_value=None):
        pass

    def set_value(self, key, value):
        pass

    def get_autoread(self):
        pass

    def set_autoread(self, value):
        pass

    def get_autowrite(self):
        pass

    def set_autowrite(self, value):
        pass


def get_config(file_name, envvar=None):
    """
    Read a config file as a Config class object.

    :param file_name: The name of the config file, or an absolute file
                      path.
    :type file_name: str

    :return: Config object.
    :rtype: Config
    """
    pass
