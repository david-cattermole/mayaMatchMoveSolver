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
Object Browser widget.
"""

import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import mmSolver.ui.Qt as Qt
import mmSolver.ui.Qt.QtCore as QtCore
import mmSolver.ui.Qt.QtGui as QtGui
import mmSolver.ui.Qt.QtWidgets as QtWidgets

import mmSolver.logger

import mmSolver.api as mmapi
import mmSolver.tools.solver.ui.attr_nodes as attr_nodes
import mmSolver.tools.solver.lib.attr as lib_attr
import mmSolver.tools.solver.lib.maya_utils as lib_maya_utils
import mmSolver.tools.solver.lib.state as lib_state
import mmSolver.tools.solver.lib.uiquery as lib_uiquery


LOG = mmSolver.logger.get_logger()


def _get_selected_attrs(cls_obj):
    tree_view = cls_obj
    filter_model = cls_obj.model()
    ui_nodes = lib_uiquery.get_selected_ui_nodes(
        tree_view,
        filter_model,
    )
    attr_ui_nodes = [x for x in ui_nodes if isinstance(x, attr_nodes.AttrNode)]
    attr_list = lib_uiquery.convert_ui_nodes_to_nodes(attr_ui_nodes, 'data')
    # maya_ui_nodes = [x for x in ui_nodes if isinstance(x, attr_nodes.MayaNode)]
    # for maya_ui_node in maya_ui_nodes:
    #     # Maya nodes will contain all the attributes added into the UI
    #     # in the 'data' key name on the data of the MayaNode.
    #     attr_list += maya_ui_node.data().get('data')
    return attr_list


class AttributeTreeView(QtWidgets.QTreeView):

    def __init__(self, parent=None, *args, **kwargs):
        super(AttributeTreeView, self).__init__(parent, *args, **kwargs)
        return

    def set_details_selected_attributes(self):
        try:
            # Disable selection callback.
            mmapi.set_solver_running(True)
            col = lib_state.get_active_collection()
            attr_list = _get_selected_attrs(self)
            lib_attr.set_details_selected_attributes(attr_list, col)
        finally:
            # Enable selection callback
            mmapi.set_solver_running(False)
            # TODO: Force the changed data model to update the UI.
        return

    def lock_selected_attributes(self):
        attr_list = _get_selected_attrs(self)
        lib_attr.lock_selected_attributes(attr_list)
        return

    def unlock_selected_attributes(self):
        attr_list = _get_selected_attrs(self)
        lib_attr.unlock_selected_attributes(attr_list)
        return

    def set_keyframe_on_selected_attributes(self):
        attr_list = _get_selected_attrs(self)
        lib_attr.set_keyframe_on_selected_attributes(attr_list)
        return

    def delete_keyframe_current_frame_on_selected_attributes(self):
        attr_list = _get_selected_attrs(self)
        lib_attr.delete_keyframe_current_frame_on_selected_attributes(attr_list)
        return

    def delete_static_channel_on_selected_attributes(self):
        attr_list = _get_selected_attrs(self)
        lib_attr.delete_static_channel_on_selected_attributes(attr_list)
        return

    def delete_keyframe_all_frames_on_selected_attributes(self):
        attr_list = _get_selected_attrs(self)
        lib_attr.delete_keyframe_all_frames_on_selected_attributes(attr_list)
        return

    def break_connections_on_selected_attributes(self):
        attr_list = _get_selected_attrs(self)
        lib_attr.break_connections_on_selected_attributes(attr_list)
        return

    def bake_selected_attributes(self):
        attr_list = _get_selected_attrs(self)
        lib_attr.bake_selected_attributes(attr_list)
        return

    def reset_values_on_selected_attributes(self):
        attr_list = _get_selected_attrs(self)
        lib_attr.reset_values_on_selected_attributes(attr_list)
        return

    def contextMenuEvent(self, event):
        LOG.debug('Attribute TreeView Context Menu Event: %r', event)
        menu = QtWidgets.QMenu(self)

        label = 'Edit Details...'
        edit_act = QtWidgets.QAction(label, self)
        edit_act.triggered.connect(
            self.set_details_selected_attributes)

        label = 'Lock Attributes'
        lock_act = QtWidgets.QAction(label, self)
        lock_act.triggered.connect(
            self.lock_selected_attributes)

        label = 'Unlock Attributes'
        unlock_act = QtWidgets.QAction(label, self)
        unlock_act.triggered.connect(
            self.unlock_selected_attributes)

        label = 'Set Keyframe'
        set_key_act = QtWidgets.QAction(label, self)
        set_key_act.triggered.connect(
            self.set_keyframe_on_selected_attributes)

        label = 'Delete Keyframe'
        delete_key_current_frame_act = QtWidgets.QAction(label, self)
        delete_key_current_frame_act.triggered.connect(
            self.delete_keyframe_current_frame_on_selected_attributes)

        label = 'Delete Keyframes (Timeline)'
        delete_key_all_frames_act = QtWidgets.QAction(label, self)
        delete_key_all_frames_act.triggered.connect(
            self.delete_keyframe_all_frames_on_selected_attributes)

        label = 'Delete Static Channels'
        delete_static_keys_act = QtWidgets.QAction(label, self)
        delete_static_keys_act.triggered.connect(
            self.delete_static_channel_on_selected_attributes)

        label = 'Break Connections'
        break_conn_act = QtWidgets.QAction(label, self)
        break_conn_act.triggered.connect(
            self.break_connections_on_selected_attributes)

        label = 'Bake Attributes'
        bake_attr_act = QtWidgets.QAction(label, self)
        bake_attr_act.triggered.connect(
            self.bake_selected_attributes)

        label = 'Reset Values'
        reset_values_act = QtWidgets.QAction(label, self)
        reset_values_act.triggered.connect(
            self.reset_values_on_selected_attributes)

        menu.addAction(edit_act)
        menu.addSeparator()
        menu.addAction(set_key_act)
        menu.addSeparator()
        menu.addAction(delete_key_current_frame_act)
        menu.addAction(delete_key_all_frames_act)
        menu.addAction(delete_static_keys_act)
        menu.addSeparator()
        menu.addAction(break_conn_act)
        menu.addAction(bake_attr_act)
        menu.addAction(reset_values_act)
        menu.addSeparator()
        menu.addAction(lock_act)
        menu.addAction(unlock_act)
        menu.exec_(event.globalPos())
        return
