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
The main component of the user interface for the mesh from locators window.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mmSolver.ui.qtpyutils as qtpyutils

qtpyutils.override_binding_order()

import mmSolver.ui.Qt.QtWidgets as QtWidgets

import mmSolver.tools.meshfromlocators.ui.ui_meshfromlocators_layout as ui_meshfromlocators_layout
import mmSolver.tools.meshfromlocators.lib as lib


class MeshFromLocatorsLayout(QtWidgets.QWidget,
                             ui_meshfromlocators_layout.Ui_Form):
    def __init__(self, parent=None, *args, **kwargs):
        super(MeshFromLocatorsLayout, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.create_connections()

    def create_connections(self):
        self.createFullMeshBtn.clicked.connect(self.full_mesh_btn_clicked)
        self.createBorderMeshBtn.clicked.connect(self.border_mesh_btn_clicked)
        self.createEdgeStripMeshBtn.clicked.connect(
            self.border_edge_strip_mesh_btn_clicked)

    def full_mesh_btn_clicked(self):
        lib.create_mesh_from_locators('fullMesh')

    def border_mesh_btn_clicked(self):
        lib.create_mesh_from_locators('borderMesh')

    def border_edge_strip_mesh_btn_clicked(self):
        offset = self.stripWidthSpinBox.value()
        lib.create_mesh_from_locators('borderEdgeStripMesh', offset)
