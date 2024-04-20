# Copyright (C) 2020 David Cattermole.
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
Help query and set user preferences.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

import mmSolver.logger
import mmSolver.utils.config as config_utils
import mmSolver.utils.python_compat as pycompat
import mmSolver.tools.userpreferences.constant as const


LOG = mmSolver.logger.get_logger()


# Intialised without a file path, because we only look up the file in
# the functions below.
#
# Users are not allowed to touch this variable.
#
# Note we never re-assign this variable. The Config object instance is
# always reused.
__CONFIG_PATH = config_utils.get_home_dir_path(const.CONFIG_FILE_NAME)
__CONFIG = config_utils.Config(__CONFIG_PATH)
__CONFIG.autoread = True
__CONFIG.autowrite = False


def get_config():
    return __CONFIG


def force_reload_from_file():
    if os.path.isfile(__CONFIG.file_path):
        __CONFIG.read()
    return


def get_value(config, key):
    assert isinstance(config, config_utils.Config)
    assert key in const.VALID_KEYS
    default_value = const.DEFAULT_VALUE_MAP[key]
    value = config.get_value(key, default_value=default_value)
    return value


def set_value(config, key, value):
    assert isinstance(config, config_utils.Config)
    assert key in const.VALID_KEYS
    assert key in const.VALUE_TYPE_MAP
    expected_value_type = const.VALUE_TYPE_MAP[key]
    if expected_value_type == const.TYPE_ENUMERATION_INT:
        assert value in const.VALUES_MAP[key]
    elif expected_value_type == const.TYPE_STRING:
        assert isinstance(value, pycompat.TEXT_TYPE)
    else:
        msg = (
            'The type ({value_type}) of the value given ({value})'
            'does not match the expected type ({expected_type}) '
            'for the user preference key {key}.'
        )
        msg = msg.format(
            key=key,
            value=repr(value),
            value_type=repr(type(value)),
            expected_type=repr(expected_value_type),
        )
        raise ValueError(msg)
    return config.set_value(key, value)


def get_value_type(config, key):
    assert isinstance(config, config_utils.Config)
    assert key in const.VALID_KEYS
    expected_value_type = const.VALUE_TYPE_MAP[key]
    return expected_value_type


def get_label_from_value(key, value):
    assert key in const.VALID_KEYS
    labels = const.LABELS_MAP[key]
    values = const.VALUES_MAP[key]
    idx = values.index(value)
    label = labels[idx]
    return label


def get_labels(key):
    assert key in const.VALID_KEYS
    labels = const.LABELS_MAP[key]
    return labels


def get_values(key):
    assert key in const.VALID_KEYS
    values = const.VALUES_MAP[key]
    return values


def get_value_from_label(key, label):
    assert key in const.VALID_KEYS
    labels = const.LABELS_MAP[key]
    values = const.VALUES_MAP[key]
    idx = labels.index(label)
    value = values[idx]
    return value
