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
Object Browser tree view.
"""

import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import Qt
import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets

import mmSolver.tools.solver.ui.object_nodes as object_nodes
import mmSolver.tools.solver.lib.maya_utils as lib_maya_utils
import mmSolver.tools.solver.lib.attr as lib_attr
import mmSolver.tools.solver.lib.state as lib_state
import mmSolver.tools.solver.lib.uiquery as lib_uiquery

import mmSolver.logger


LOG = mmSolver.logger.get_logger()


def _get_selected_maya_nodes(cls_obj):
    tree_view = cls_obj
    filter_model = cls_obj.model()
    ui_nodes = lib_uiquery.get_selected_ui_nodes(
        tree_view,
        filter_model,
    )
    uuid_list = lib_uiquery.convert_ui_nodes_to_nodes(ui_nodes, 'uuid')
    nodes = lib_maya_utils.get_node_names_from_uuids(uuid_list)
    return nodes


class ObjectTreeView(QtWidgets.QTreeView):

    def __init__(self, parent=None, *args, **kwargs):
        super(ObjectTreeView, self).__init__(parent, *args, **kwargs)
        return

    def selection_swap(self):
        node_list = _get_selected_maya_nodes(self)
        LOG.debug("Swap Marker/Bundle Selection: %r", node_list)
        import mmSolver.tools.selection.tools as tools
        lib_maya_utils.set_scene_selection(node_list)
        tools.swap_between_selected_markers_and_bundles()
        return

    def selection_both_markers_bundles(self):
        node_list = _get_selected_maya_nodes(self)
        LOG.debug("Select Both Markers and Bundles: %r", node_list)
        import mmSolver.tools.selection.tools as tools
        lib_maya_utils.set_scene_selection(node_list)
        tools.select_both_markers_and_bundles()
        return

    def rename_marker_bundles():
        node_list = _get_selected_maya_nodes(self)
        LOG.debug("Rename Markers and Bundles: %r", node_list)
        import mmSolver.tools.markerbundlerename.tool as tool
        lib_maya_utils.set_scene_selection(node_list)
        tool.main()
        return

    def contextMenuEvent(self, event):
        LOG.debug('Object TreeView Context Menu Event: %r', event)
        menu = QtWidgets.QMenu(self)

        label = 'Select Marker / Bundle'
        swap_sel_act = QtWidgets.QAction(label, self)
        swap_sel_act.triggered.connect(
            self.selection_swap)

        label = 'Select Marker + Bundle'
        both_sel_act = QtWidgets.QAction(label, self)
        both_sel_act.triggered.connect(
            self.selection_both_markers_bundles)

        label = 'Marker Bundle Rename...'
        rename_act = QtWidgets.QAction(label, self)
        rename_act.triggered.connect(
            self.rename_marker_bundles)

        menu.addAction(swap_sel_act)
        menu.addAction(both_sel_act)
        menu.addSeparator()
        menu.addAction(rename_act)
        menu.exec_(event.globalPos())
        return
