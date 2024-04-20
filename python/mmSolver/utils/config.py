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
Configuration for querying and setting configuration values and files.

Tools may need to have config files to read from and write. This
module is a unified module for working with these configuration files.

All configuration files are expected to be JSON formatted.

By default, without any keyword arguments, configuration files are
searched for in the 'MMSOLVER_CONFIG_PATH' environment variable, but
this may be overridden using "get_dirs", or "get_config" function arguments.

By default the following paths are searched (in order, top-down):

 - `${HOME}/.mmSolver` (Linux)

 - `%APPDATA%/mmSolver` (Windows)

 - `${MMSOLVER_LOCATION}/config` (Linux and Windows)

This allows both a default fallback, and a user specified path.
Additionally, studios may modify the '.mod' file to provide an
intermediate studio or project location.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json
import os
import platform

import mmSolver.logger
import mmSolver.utils.constant as const
import mmSolver.utils.python_compat as pycompat

LOG = mmSolver.logger.get_logger()


def get_dirs(envvar):
    """
    Get a list of directories to look in for config files.

    :param envvar: The environment variable to query for a list
                        of directories.
    :type envvar: str or None

    :return: List of config directories.
    """
    value = os.environ.get(envvar, None)
    if value is None:
        msg = 'Env Var does not exist; %r'
        LOG.warning(msg, envvar)
        value = ''
    result = value.split(os.pathsep)
    result = [v for v in result if len(v) > 0]
    result = [os.path.abspath(os.path.expandvars(v)) for v in result]
    return result


def _split_key(key):
    """
    Split a key into separate name hierarchy, with a '/' character.

    :rtype: [str, ..]
    """
    args = key.split('/')
    args = [k for k in args if len(k) > 0]
    return args


def find_path(file_name, search_paths):
    """
    Search though a list of defined paths for the config file name given.

    If an absolute file path is given, it is verified and returned.

    :param file_name: File name to find.
    :type file_name: str

    :param search_paths: The directories to search for the file.
    :type search_paths: list of str

    :return: Full config file name, or None.
    :rtype: str or None
    """
    assert isinstance(search_paths, (list, tuple))
    if os.path.isabs(file_name) and os.path.isfile(file_name):
        return file_name
    file_path = None
    for path in search_paths:
        p = os.path.join(path, file_name)
        p = os.path.abspath(p)
        if os.path.isfile(p) is True:
            file_path = p
            break
    return file_path


def read_data(file_path):
    """
    Read configuration file and return the data embedded.

    :param file_path: The absolute file path to a config file.
    :type file_path: str

    :return: Dictionary, list or None, depending what the given file
             contains.
    :rtype: dict, list or None
    """
    LOG.debug('Read Configuration: %r', file_path)
    data = None
    if not os.path.isfile(file_path):
        return data
    with open(file_path, 'rb') as f:
        try:
            text = f.read()
            data = json.loads(text)
        except BaseException:
            raise
    return data


def write_data(data, file_path, human_readable=True):
    """
    Write the given configuration data to a file.

    :param data: Configuration data to write. The data should be
                 plain-old-(Python)data types, like lists, float, int,
                 string and dict.
    :type data: dict or list

    :param file_path: A valid absolute file path.
    :type file_path: str
    """
    LOG.debug('Write Configuration: %r', file_path)
    kwargs = {
        'sort_keys': True,
        'indent': 2,
        'separators': None,
    }
    if human_readable is False:
        kwargs = {
            'sort_keys': False,
            'indent': None,
            'separators': (',', ':'),
        }
    text = json.dumps(data, **kwargs)
    with open(file_path, 'w') as f:
        f.write(text)
    return


def exists(data, key):
    """
    Does the key exist in data?

    :param data: The name of the config file, or an absolute file path.
    :type data: dict

    :param key: Hierarchy of keys separated by forward slash to search
                for in the config.
                For example 'data[arg1][arg2][arg3]'.
    :type key: str

    :return: Boolean, does the 'key' exist in the 'data'?
    :rtype: bool
    """
    key_list = _split_key(key)
    d = data
    ok = True
    for i, k in enumerate(key_list):
        if k not in d:
            ok = False
            break
        d = d[k]
    return ok


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

    :return: The value type in the key - it could be any type..
    """
    if exists(data, key) is False:
        return default_value

    key_list = _split_key(key)
    d = data
    for i, k in enumerate(key_list):
        if k not in d:
            break
        else:
            d = d[k]
    return d


def _recursive_update(d, u):
    """
    Merge one dictionary with another, while keeping the nested state.

    This is copied from:
    https://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth

    :param d: Base dictionary.
    :type d: dict

    :param u: Update value.
    :type u: dict or any

    :returns: A dictionary with both d and u merged together.
    :rtype: dict
    """
    for k, v in u.items():
        if isinstance(v, pycompat.COLLECTIONS_ABC_MAPPING):
            d[k] = _recursive_update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


def set_value(data, key, value):
    """
    Set a value in the given configuration data.

    :param data: The data to set the value on to.
    :type data: dict

    :param key: Where to set the value in data
    :type key: str

    :param value: The value to set.
    :type value: any

    :returns: A copy of the configuration data with the modification
              made.
    :rtype: dict or list
    """
    assert isinstance(data, dict)
    key_list = _split_key(key)
    data_value = dict()
    for i, k in enumerate(reversed(key_list)):
        last = i == 0
        if last is True:
            data_value[k] = value
        else:
            tmp = data_value.copy()
            data_value = dict()
            data_value[k] = tmp
    result = data.copy()
    result = _recursive_update(result, data_value)
    return result


class Config(object):
    """
    A configuration file in mmSolver, to read, write, query and edit
    configuration files.

    `Config` will save a new file, if the given file_name is valid.

    This is an example use::

        >>> file_path = "/absolute/path/to/file.json"
        >>> config = Config(file_path)
        >>> config.file_path
        /absolute/path/to/file.json
        >>> config.read()  # Read the file, fails if the file does not exist.
        >>> config.exists("my_option_name")
        False
        >>> config.get_value("my_option_name")
        None
        >>> config.set_value("my_option_name", 42)
        >>> config.exists("my_option_name")
        True
        >>> config.get_value("my_option_name")
        42
        >>> config.write()

    """

    def __init__(self, file_path):
        self._file_path = file_path
        self._values = dict()
        self._changed = False
        self._auto_read = True
        self._auto_write = False

    def get_autoread(self):
        return self._auto_read

    def set_autoread(self, value):
        """
        Set auto-read value.

        By default, auto-read is True.

        If auto-read is True, `Config` will read a config file
        automatically, without the need to call "read()" explicitly.

        :param value: The value to set.
        :type value: bool
        """
        assert isinstance(value, bool)
        self._auto_read = value

    def get_autowrite(self):
        return self._auto_write

    def set_autowrite(self, value):
        """Set auto-write value.

        By default, auto-write is False.

        If auto-write is True, `Config` will write a config file
        automatically, when the Config object is destructed by Python.
        Otherwise, the user must call "write()" (which is generally
        recommended anyway).

        :param value: The value to set.
        :type value: bool
        """
        assert isinstance(value, bool)
        self._auto_write = value

    def get_file_path(self):
        return self._file_path

    def set_file_path(self, value):
        """Set the file path for the Config.

        Setting the file path will automatically invalidate the Config
        and force a re-read of the config file when a value is next requested.

        .. note:: If the new file path is the same as the old file
            path, the Config will not be invalidated. Only if the file
            path changes will the Config be invalidated. To re-read
            the file, use the Config.read() method.

        :param value: The value to set.
        :type value: str
        """
        assert isinstance(value, pycompat.TEXT_TYPE)
        if value == self._file_path:
            # No change to the file path.
            return
        self._file_path = value
        self._values = dict()
        self._changed = False

    def __del__(self):
        if self._auto_write is True and self._changed is True:
            self.write()

    def read(self):
        """Read the `file_path` contents."""
        data = read_data(self.file_path)
        self._values = data
        self._changed = False
        return

    def write(self, human_readable=True):
        """Write the contents of this object to the `file_path`."""
        write_data(self._values, self.file_path, human_readable)
        self._changed = False

    def exists(self, key):
        """Does the key exist in this config file?"""
        data = self._values
        return exists(data, key)

    def get_value(self, key, default_value=None):
        """
        Get a value from the Config file.

        If no key exists, returns the default_value.
        """
        if self._auto_read is True and (self._values is None or len(self._values) == 0):
            self.read()
        data = self._values
        if data is None or len(data) == 0:
            return default_value
        value = get_value(data, key, default_value=default_value)
        return value

    def set_value(self, key, value):
        """Set the key/value in the Config file."""
        data = {}
        if isinstance(self._values, dict):
            data = self._values.copy()
        data = set_value(data, key, value)
        self._values = data
        self._changed = True
        return

    autoread = property(get_autoread, set_autoread)
    autowrite = property(get_autowrite, set_autowrite)
    file_path = property(get_file_path, set_file_path)


def get_config(file_name, search=None):
    """
    Read a config file as a Config class object.

    >>> get_config("myConfigFile.json")
    <mmSolver.utils.config.Config object at 0x0000016993BF5160>
    >>> get_config("/path/to/config/file.json")
    <mmSolver.utils.config.Config object at 0x0000016993BF5748>
    >>> get_config("non_existant_file.json")
    None

    :param file_name: The name of the config file, or an absolute file
                      path.
    :type file_name: str

    :param search: An environment variable to parse for search paths,
                   or a list of given search directory paths, or if set
                   to None, use the default environment variable for
                   mmSolver.
    :type search: str or [str, ..] or None

    :return: Config object, or None if the file is not found.
    :rtype: Config or None
    """
    if search is None:
        search = const.CONFIG_PATH_VAR_NAME
    if isinstance(search, list):
        dir_list = search
    else:
        dir_list = get_dirs(search)

    file_path = find_path(file_name, dir_list)
    if file_path is None:
        return None

    config = Config(file_path)
    return config


def get_home_dir_path(*args):
    """
    Get the default home directory configuration directory.

    The path returned will be operating system dependent.

    .. note:: The path returned may not exist! It is up to the user to
              check and create files/directories as needed.

    :param args: A list of string arguments to be joined to the
                 returned path.
    :type args: [str, ..]

    :returns: An absolute path to a config directory that may or may not exist.
    :rtype: str
    """
    os_name = platform.system()
    path = const.CONFIG_HOME_DIR_PATH.get(os_name)
    if len(args) > 0:
        path = os.path.join(path, *args)
    path = os.path.expandvars(path)
    path = os.path.abspath(path)
    LOG.debug('Config Path: %r', path)
    return path
