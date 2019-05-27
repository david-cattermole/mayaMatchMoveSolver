"""
Configuration for querying and setting configuration values and files.

Tools may need to have config files to read from and write. This
module is a unified module for working with these configuration files.

All configuration files are expected to be JSON formatted.

By default, without any keyword arguments, configuration files are
searched for in the 'MMSOLVER_CONFIG_PATH' environment variable, but
this may be overridden using "get_dirs", or "get_config" function arguments.

By default the following paths are searched (in order, top-down):

 - ${MMSOLVER_LOCATION}/config (Linux and Windows)
 - ${HOME}/.mmSolver (Linux)
 - %APPDATA%\mmSolver (Windows)

This allows both a default fallback, and a user specified path.
Additionally, studios may modify the '.mod' file to provide an
intermediate studio or project location.
"""

import collections
import json
import os

import mmSolver.logger
import mmSolver.utils.constant as const

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
    with open(file_path, 'rb') as f:
        try:
            text = f.read()
            data = json.loads(text)
        except:
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
    with open(file_path, 'wb') as f:
        f.write(text)
    return


def exists(data, key):
    """
    Does the key exist in data?

    :param data: The name of the config file, or an absolute file
                      path.
    :type data: dict

    :param key: Hierarchy of keys separated by forward slash to search
                for in the config.
                For example 'data[arg1][arg2][arg3]'.
    :type key: str

    :return:
    :rtype
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

    :return:
    :rtype
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
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
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
    def __init__(self, file_path):
        self.file_path = file_path
        self._values = dict()
        self._changed = False
        self._auto_read = True
        self._auto_write = False

    def get_autoread(self):
        return self._auto_read

    def set_autoread(self, value):
        assert isinstance(value, bool)
        self._auto_read = value

    def get_autowrite(self):
        return self._auto_write

    def set_autowrite(self, value):
        assert isinstance(value, bool)
        self._auto_write = value

    def __del__(self):
        if self._auto_write is True and self._changed is True:
            self.write()

    def read(self):
        data = read_data(self.file_path)
        self._values = data
        self._changed = False
        return

    def write(self, human_readable=True):
        write_data(self._values, self.file_path, human_readable)
        self._changed = False

    def exists(self, key):
        data = self._values
        return exists(data, key)

    def get_value(self, key, default_value=None):
        if self._auto_read is True and len(self._values) == 0:
            self.read()
        data = self._values
        if data is None:
            return default_value
        value = get_value(data, key, default_value=default_value)
        return value

    def set_value(self, key, value):
        data = {}
        if isinstance(self._values, dict):
            data = self._values.copy()
        data = set_value(data, key, value)
        self._values = data
        self._changed = True
        return


def get_config(file_name, search=None):
    """
    Read a config file as a Config class object.

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
