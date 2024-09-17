# Copyright (C) 2024 Patcha Saheb Binginapalli.
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
The main component of the user interface for the mesh from points window.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import maya.cmds

import mmSolver.ui.qtpyutils as qtpyutils

qtpyutils.override_binding_order()

import mmSolver.ui.Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.utils.configmaya as configmaya
import mmSolver.tools.meshfrompoints.ui.ui_meshfrompoints_layout as ui_meshfrompoints_layout
import mmSolver.tools.meshfrompoints.lib as lib
import mmSolver.tools.meshfrompoints.constant as const


LOG = mmSolver.logger.get_logger()


def _get_selection():
    transform_nodes = maya.cmds.ls(selection=True, transforms=True) or []
    if len(transform_nodes) < 3:
        LOG.warn('Please select least three transform nodes.')
        return None
    return transform_nodes


class MeshFromPointsLayout(QtWidgets.QWidget, ui_meshfrompoints_layout.Ui_Form):
    def __init__(self, parent=None, *args, **kwargs):
        super(MeshFromPointsLayout, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.create_connections()

        # TODO: Should the mesh node name be exposed to the user to set?

        # Populate the UI with data
        self.populateUi()

    def create_connections(self):
        self.createFullMeshBtn.clicked.connect(self.full_mesh_btn_clicked)
        self.createBorderMeshBtn.clicked.connect(self.border_mesh_btn_clicked)
        self.createEdgeStripMeshBtn.clicked.connect(
            self.border_edge_strip_mesh_btn_clicked
        )

    def reset_options(self):
        name = const.CONFIG_STRIP_WIDTH_KEY
        value = const.DEFAULT_STRIP_WIDTH
        configmaya.set_scene_option(name, value)
        LOG.debug('key=%r value=%r', name, value)

        self.populateUi()
        return

    def populateUi(self):
        """
        Update the UI for the first time the class is created.
        """
        name = const.CONFIG_STRIP_WIDTH_KEY
        value = configmaya.get_scene_option(name, default=const.DEFAULT_STRIP_WIDTH)
        LOG.debug('key=%r value=%r', name, value)
        self.stripWidthSpinBox.setValue(value)

    def full_mesh_btn_clicked(self):
        transform_nodes = _get_selection()
        if transform_nodes is None:
            return

        lib.create_mesh_from_transform_nodes(
            const.MESH_TYPE_FULL_MESH_VALUE, transform_nodes
        )

    def border_mesh_btn_clicked(self):
        transform_nodes = _get_selection()
        if transform_nodes is None:
            return

        lib.create_mesh_from_transform_nodes(
            const.MESH_TYPE_BORDER_MESH_VALUE, transform_nodes
        )

    def border_edge_strip_mesh_btn_clicked(self):
        transform_nodes = _get_selection()
        if transform_nodes is None:
            return

        offset = self.stripWidthSpinBox.value()
        lib.create_mesh_from_transform_nodes(
            const.MESH_TYPE_BORDER_EDGE_STRIP_MESH_VALUE,
            transform_nodes,
            offset_value=offset,
        )
