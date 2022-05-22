# Copyright (C) 2020 Kazuma Tonegawa.
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
The main component of the user interface for the remove solver
nodes window.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import mmSolver.ui.Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.utils.config as config_utils
import mmSolver.tools.removesolvernodes.constants as const
import mmSolver.tools.removesolvernodes.ui.ui_removesolvernodes_layout as ui_removesolvernodes_layout

LOG = mmSolver.logger.get_logger()


def get_config():
    """Get the Remove Solver Nodes config object or None."""
    file_name = const.CONFIG_FILE_NAME
    config_path = config_utils.get_home_dir_path(file_name)
    config = config_utils.Config(config_path)
    config.set_autoread(False)
    config.set_autowrite(False)
    if os.path.isfile(config.file_path):
        config.read()
    return config


def get_config_value(config, key, fallback):
    """Query the attribute from the user's home directory. If the user's
    option is saved, use that value instead.
    """
    value = fallback
    if config is not None:
        value = config.get_value(key, fallback)
    return value


class RemoveSolverNodesLayout(QtWidgets.QWidget, ui_removesolvernodes_layout.Ui_Form):
    def __init__(self, parent=None, *args, **kwargs):
        super(RemoveSolverNodesLayout, self).__init__(*args, **kwargs)
        self.setupUi(self)

    def reset_options(self):
        # Read these values from the config file.
        config = get_config()
        save_scene = get_config_value(
            config, 'data/save_scene',
            const.SAVE_SCENE_DEFAULT_VALUE)
        markers = get_config_value(
            config, 'data/delete_markers',
            const.DELETE_MARKERS_DEFAULT_VALUE)
        bundles = get_config_value(
            config, 'data/delete_bundles',
            const.DELETE_BUNDLES_DEFAULT_VALUE)
        marker_groups = get_config_value(
            config, 'data/delete_marker_groups',
            const.DELETE_MARKER_GROUPS_DEFAULT_VALUE)
        lenses = get_config_value(
            config, 'data/delete_lenses',
            const.DELETE_LENSES_DEFAULT_VALUE)
        lines = get_config_value(
            config, 'data/delete_lines',
            const.DELETE_LINES_DEFAULT_VALUE)
        imageplanes = get_config_value(
            config, 'data/delete_imageplanes',
            const.DELETE_IMAGE_PLANES_DEFAULT_VALUE)
        collections = get_config_value(
            config, 'data/delete_collections',
            const.DELETE_COLLECTIONS_DEFAULT_VALUE)
        display_nodes = get_config_value(
            config, 'data/delete_display_nodes',
            const.DELETE_DISPLAY_NODES_DEFAULT_VALUE)
        others = get_config_value(
            config, 'data/delete_others',
            const.DELETE_OTHERS_DEFAULT_VALUE)

        self.saveSceneBefore_checkBox.setChecked(save_scene)
        self.markers_checkBox.setChecked(markers)
        self.bundles_checkBox.setChecked(bundles)
        self.markerGroup_checkBox.setChecked(marker_groups)
        self.lenses_checkBox.setChecked(lenses)
        self.lines_checkBox.setChecked(lines)
        self.imagePlanes_checkBox.setChecked(imageplanes)
        self.collections_checkBox.setChecked(collections)
        self.displayNodes_checkBox.setChecked(display_nodes)
        self.otherNodes_checkBox.setChecked(others)

    def save_options(self):
        # Update config file with widget values.
        save_scene = self.saveSceneBefore_checkBox.isChecked()
        markers = self.markers_checkBox.isChecked()
        bundles = self.bundles_checkBox.isChecked()
        marker_groups = self.markerGroup_checkBox.isChecked()
        lenses = self.lenses_checkBox.isChecked()
        lines = self.lines_checkBox.isChecked()
        imageplanes = self.imagePlanes_checkBox.isChecked()
        collections = self.collections_checkBox.isChecked()
        display_nodes = self.displayNodes_checkBox.isChecked()
        others = self.otherNodes_checkBox.isChecked()

        config = get_config()
        if config is not None:
            config.set_value("data/save_scene", save_scene)
            config.set_value("data/delete_markers", markers)
            config.set_value("data/delete_bundles", bundles)
            config.set_value("data/delete_marker_groups", marker_groups)
            config.set_value("data/delete_lenses", lenses)
            config.set_value("data/delete_lines", lines)
            config.set_value("data/delete_imageplanes", imageplanes)
            config.set_value("data/delete_collections", collections)
            config.set_value("data/delete_display_nodes", display_nodes)
            config.set_value("data/delete_others", others)
            config.write()
        return
