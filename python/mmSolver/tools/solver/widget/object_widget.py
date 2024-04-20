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
Object Browser widget.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import time

import mmSolver.ui.qtpyutils as qtpyutils

qtpyutils.override_binding_order()

import mmSolver.ui.Qt as Qt
import mmSolver.ui.Qt.QtCore as QtCore
import mmSolver.ui.Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.ui.uiutils as uiutils
import mmSolver.api as mmapi
import mmSolver.tools.solver.maya_callbacks as maya_callbacks
import mmSolver.tools.solver.lib.collection as lib_col
import mmSolver.tools.solver.lib.state as lib_state
import mmSolver.tools.solver.lib.uiquery as lib_uiquery
import mmSolver.tools.solver.lib.marker as lib_marker
import mmSolver.tools.solver.lib.line as lib_line
import mmSolver.tools.solver.lib.maya_utils as lib_maya_utils
import mmSolver.tools.solver.ui.object_nodes as object_nodes
import mmSolver.tools.solver.ui.convert_to_ui as convert_to_ui
import mmSolver.tools.solver.widget.nodebrowser_widget as nodebrowser_widget
import mmSolver.tools.solver.widget.nodebrowser_utils as nodebrowser_utils
import mmSolver.tools.solver.widget.object_treeview as object_treeview
import mmSolver.tools.solver.constant as const


LOG = mmSolver.logger.get_logger()


def _lookupUINodesFromIndexes(indexes, model):
    """
    Find the UI nodes, from the list of Qt indexes.
    """
    maya_nodes = []
    for idx in indexes:
        ui_node = lib_uiquery.get_ui_node_from_index(idx, model)
        if ui_node is None:
            continue

        typeInfo = ui_node.typeInfo
        assert typeInfo in const.OBJECT_NODE_TYPE_INFO_LIST

        nodes = lib_uiquery.convert_ui_nodes_to_nodes([ui_node], typeInfo)
        if typeInfo == const.OBJECT_NODE_TYPE_INFO_CAMERA_VALUE:
            maya_nodes += [x.get_transform_node() for x in nodes]
        else:
            # For bundles and markers
            maya_nodes += [x.get_node() for x in nodes]
    return maya_nodes


class ObjectBrowserWidget(nodebrowser_widget.NodeBrowserWidget):
    def __init__(self, parent=None, *args, **kwargs):
        s = time.time()
        super(ObjectBrowserWidget, self).__init__(parent=parent, *args, **kwargs)
        self.callback_manager = maya_callbacks.CallbackManager()

        self.ui.title_label.setText('Input Objects')

        self.createToolButtons()
        self.createTreeView()

        e = time.time()
        LOG.debug('ObjectWidget init: %r seconds', e - s)
        return

    def __del__(self):
        """
        Release all resources held by the class.
        """
        del self.callback_manager

    def createToolButtons(self):
        """
        Create the 'toggle' buttons for the Object browser.
        """
        self.toggleCamera_toolButton = QtWidgets.QToolButton(self)
        self.toggleCamera_toolButton.setText('CAM')
        self.toggleCamera_toolButton.setCheckable(True)
        self.ui.toggleButtons_layout.addWidget(self.toggleCamera_toolButton)

        self.toggleLine_toolButton = QtWidgets.QToolButton(self)
        self.toggleLine_toolButton.setText('LN')
        self.toggleLine_toolButton.setCheckable(True)
        self.ui.toggleButtons_layout.addWidget(self.toggleLine_toolButton)

        self.toggleMarker_toolButton = QtWidgets.QToolButton(self)
        self.toggleMarker_toolButton.setText('MKR')
        self.toggleMarker_toolButton.setCheckable(True)
        self.ui.toggleButtons_layout.addWidget(self.toggleMarker_toolButton)

        self.toggleBundle_toolButton = QtWidgets.QToolButton(self)
        self.toggleBundle_toolButton.setText('BND')
        self.toggleBundle_toolButton.setCheckable(True)
        self.ui.toggleButtons_layout.addWidget(self.toggleBundle_toolButton)

        self.toggleCamera_toolButton.clicked.connect(self.toggleCameraClicked)
        self.toggleLine_toolButton.clicked.connect(self.toggleLineClicked)
        self.toggleMarker_toolButton.clicked.connect(self.toggleMarkerClicked)
        self.toggleBundle_toolButton.clicked.connect(self.toggleBundleClicked)
        return

    def createTreeView(self):
        """
        Set up the tree view.
        """
        self.treeView = object_treeview.ObjectTreeView()
        self.ui.treeViewLayout.addWidget(self.treeView)

        root = object_nodes.ObjectNode('root')
        self.model = object_nodes.ObjectModel(root, font=self.font)
        self.filterModel = QtCore.QSortFilterProxyModel()
        self.filterModel.setSourceModel(self.model)
        self.filterModel.setDynamicSortFilter(False)
        self.header = QtWidgets.QHeaderView(QtCore.Qt.Horizontal, parent=self.treeView)
        Qt.QtCompat.QHeaderView.setSectionResizeMode(
            self.header, QtWidgets.QHeaderView.ResizeToContents
        )
        self.treeView.setHeader(self.header)
        self.treeView.setModel(self.filterModel)
        self.treeView.setSortingEnabled(True)
        self.treeView.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.treeView.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.selModel = self.treeView.selectionModel()
        self.selModel.selectionChanged.connect(self.selectionChanged)

        # Always hide the UUID Column - it's used for selection of
        # ModelIndexes with Maya node UUIDs only.
        hidden = True
        column = self.model.getColumnIndexFromColumnName(const.OBJECT_COLUMN_NAME_UUID)
        self.treeView.setColumnHidden(column, hidden)
        return

    def populateModel(self, model, col):
        valid = uiutils.isValidQtObject(model)
        if valid is False:
            return
        mkr_list = []
        line_list = []
        show_cam = const.OBJECT_TOGGLE_CAMERA_DEFAULT_VALUE
        show_line = const.OBJECT_TOGGLE_LINE_DEFAULT_VALUE
        show_mkr = const.OBJECT_TOGGLE_MARKER_DEFAULT_VALUE
        show_bnd = const.OBJECT_TOGGLE_BUNDLE_DEFAULT_VALUE
        if col is not None:
            mkr_list = lib_marker.get_markers_from_collection(col)
            line_list = lib_line.get_lines_from_collection(col)
            show_cam = lib_col.get_object_toggle_camera_from_collection(col)
            show_line = lib_col.get_object_toggle_line_from_collection(col)
            show_mkr = lib_col.get_object_toggle_marker_from_collection(col)
            show_bnd = lib_col.get_object_toggle_bundle_from_collection(col)
        root_node = convert_to_ui.solverObjectsToUINodes(
            mkr_list, line_list, show_cam, show_mkr, show_bnd, show_line
        )
        model.setRootNode(root_node)
        return

    def updateInfo(self):
        is_running = mmapi.is_solver_running()
        if is_running is True:
            return
        cam_list = set()
        line_list = set()
        mkr_list = set()
        bnd_list = set()

        col = lib_state.get_active_collection()
        if col is not None:
            marker_list = col.get_marker_list()
            for mkr in marker_list:
                mkr_node = mkr.get_node()
                mkr_list.add(mkr_node)

                cam = mkr.get_camera()
                cam_shp_node = cam.get_shape_node()
                cam_list.add(cam_shp_node)

                bnd = mkr.get_bundle()
                if bnd is not None:
                    bnd_node = bnd.get_node()
                    bnd_list.add(bnd_node)

            line_list = set([x.get_node() for x in col.get_line_list()])

        text = ('Camera {cam} | Lines {line} | Markers {mkr} | Bundles {bnd}').format(
            cam=len(cam_list),
            line=len(line_list),
            mkr=len(mkr_list),
            bnd=len(bnd_list),
        )
        self.ui.info_label.setText(text)
        return

    def updateToggleButtons(self):
        is_running = mmapi.is_solver_running()
        if is_running is True:
            return
        col = lib_state.get_active_collection()
        if col is None:
            return
        show_cam = lib_col.get_object_toggle_camera_from_collection(col)
        show_line = lib_col.get_object_toggle_line_from_collection(col)
        show_mkr = lib_col.get_object_toggle_marker_from_collection(col)
        show_bnd = lib_col.get_object_toggle_bundle_from_collection(col)
        self.toggleCamera_toolButton.setChecked(show_cam)
        self.toggleLine_toolButton.setChecked(show_line)
        self.toggleMarker_toolButton.setChecked(show_mkr)
        self.toggleBundle_toolButton.setChecked(show_bnd)
        return

    def updateColumnVisibility(self):
        is_running = mmapi.is_solver_running()
        if is_running is True:
            return
        show_weight = lib_state.get_display_object_weight_state()
        show_frm_dev = lib_state.get_display_object_frame_deviation_state()
        show_avg_dev = lib_state.get_display_object_average_deviation_state()
        show_max_dev = lib_state.get_display_object_maximum_deviation_state()
        self.displayWeightColumnChanged(show_weight)
        self.displayFrameDeviationColumnChanged(show_frm_dev)
        self.displayAverageDeviationColumnChanged(show_avg_dev)
        self.displayMaximumDeviationColumnChanged(show_max_dev)
        return

    def updateModel(self):
        is_running = mmapi.is_solver_running()
        if is_running is True:
            return

        col = lib_state.get_active_collection()
        if col is None:
            return

        self.populateModel(self.model, col)
        nodebrowser_utils._expand_node(
            self.treeView,
            self.treeView.model(),
            self.treeView.rootIndex(),
            expand=True,
            recurse=True,
        )

        widgets = [self]
        nodebrowser_utils._populateWidgetsEnabled(col, widgets)

        block = self.blockSignals(True)
        self.viewUpdated.emit()
        self.blockSignals(block)
        return

    def addClicked(self):
        col = lib_state.get_active_collection()
        if col is None:
            msg = 'Cannot add markers, active collection is not defined.'
            LOG.warning(msg)
            return

        sel = lib_maya_utils.get_scene_selection()
        mkr_list = lib_maya_utils.get_markers_from_selection()
        line_list = lib_maya_utils.get_lines_from_selection()
        if len(mkr_list) == 0 and len(line_list) == 0:
            msg = 'Please select objects; no markers or lines found.'
            LOG.warning(msg)
            return

        if len(mkr_list) > 0:
            lib_marker.add_markers_to_collection(mkr_list, col)
        if len(line_list) > 0:
            lib_line.add_lines_to_collection(line_list, col)

        # Add Callbacks
        callback_manager = self.callback_manager
        if callback_manager is not None:
            lib_marker.add_callbacks_to_markers(mkr_list, callback_manager)
            lib_line.add_callbacks_to_lines(line_list, callback_manager)

        # Restore selection.
        lib_maya_utils.set_scene_selection(sel)
        return

    def removeClicked(self):
        col = lib_state.get_active_collection()
        if col is None:
            return

        sel = lib_maya_utils.get_scene_selection()
        ui_nodes = lib_uiquery.get_selected_ui_nodes(self.treeView, self.filterModel)
        mkr_nodes = lib_uiquery.convert_ui_nodes_to_nodes(
            ui_nodes, mmapi.OBJECT_TYPE_MARKER
        )
        line_nodes = lib_uiquery.convert_ui_nodes_to_nodes(
            ui_nodes, mmapi.OBJECT_TYPE_LINE
        )
        lib_marker.remove_markers_from_collection(mkr_nodes, col)
        lib_line.remove_lines_from_collection(line_nodes, col)

        # Remove Callbacks
        callback_manager = self.callback_manager
        if callback_manager is not None:
            lib_marker.remove_callbacks_from_markers(mkr_nodes, callback_manager)
            lib_line.remove_callbacks_from_lines(line_nodes, callback_manager)

        self.dataChanged.emit()
        self.viewUpdated.emit()

        # Restore selection.
        lib_maya_utils.set_scene_selection(sel)
        return

    def toggleCameraClicked(self):
        col = lib_state.get_active_collection()
        if col is None:
            LOG.warning('No active collection to set.')
            return
        value = lib_col.get_object_toggle_camera_from_collection(col)
        value = not value
        lib_col.set_object_toggle_camera_on_collection(col, value)
        self.dataChanged.emit()
        return

    def toggleLineClicked(self):
        col = lib_state.get_active_collection()
        if col is None:
            LOG.warning('No active collection to set.')
            return
        value = lib_col.get_object_toggle_line_from_collection(col)
        value = not value
        lib_col.set_object_toggle_line_on_collection(col, value)
        self.dataChanged.emit()
        return

    def toggleMarkerClicked(self):
        col = lib_state.get_active_collection()
        if col is None:
            LOG.warning('No active collection to set.')
            return
        value = lib_col.get_object_toggle_marker_from_collection(col)
        value = not value
        lib_col.set_object_toggle_marker_on_collection(col, value)
        self.dataChanged.emit()
        return

    def toggleBundleClicked(self):
        col = lib_state.get_active_collection()
        if col is None:
            LOG.warning('No active collection to set.')
            return
        value = lib_col.get_object_toggle_bundle_from_collection(col)
        value = not value
        lib_col.set_object_toggle_bundle_on_collection(col, value)
        self.dataChanged.emit()
        return

    @QtCore.Slot(list)
    def setNodeSelection(self, values):
        """
        Override the tree view selection based on Maya Node UUIDs.
        """
        nodebrowser_utils.setNodeSelectionWithUUID(
            self.treeView,
            self.model,
            self.filterModel,
            self.selModel,
            const.OBJECT_COLUMN_NAME_UUID,
            values,
        )
        return

    @QtCore.Slot(QtCore.QItemSelection, QtCore.QItemSelection)
    def selectionChanged(self, selected, deselected):
        """
        Look up the Maya node from the 'selected' nodes, and add them
        to the Maya selection.
        """
        select_indexes = [idx for idx in selected.indexes()]
        deselect_indexes = [idx for idx in deselected.indexes()]
        select_nodes = _lookupUINodesFromIndexes(select_indexes, self.filterModel)
        deselect_nodes = _lookupUINodesFromIndexes(deselect_indexes, self.filterModel)
        if self.isActiveWindow() is True:
            # Only allow Maya selection changes when the user has the
            # UI focused. This breaks the Maya and Qt selection
            # callback cycle.
            try:
                mmapi.set_solver_running(True)  # disable selection callback.
                lib_maya_utils.add_scene_selection(select_nodes)
                lib_maya_utils.remove_scene_selection(deselect_nodes)
            finally:
                mmapi.set_solver_running(False)  # enable selection callback
        return

    @QtCore.Slot(bool)
    def displayWeightColumnChanged(self, value):
        lib_state.set_display_object_weight_state(value)
        idx = self.model.getColumnIndexFromColumnName(const.OBJECT_COLUMN_NAME_WEIGHT)
        self.treeView.setColumnHidden(idx, not value)
        return

    @QtCore.Slot(bool)
    def displayFrameDeviationColumnChanged(self, value):
        lib_state.set_display_object_frame_deviation_state(value)
        idx = self.model.getColumnIndexFromColumnName(
            const.OBJECT_COLUMN_NAME_DEVIATION_FRAME
        )
        self.treeView.setColumnHidden(idx, not value)
        return

    @QtCore.Slot(bool)
    def displayAverageDeviationColumnChanged(self, value):
        lib_state.set_display_object_average_deviation_state(value)
        idx = self.model.getColumnIndexFromColumnName(
            const.OBJECT_COLUMN_NAME_DEVIATION_AVERAGE
        )
        self.treeView.setColumnHidden(idx, not value)
        return

    @QtCore.Slot(bool)
    def displayMaximumDeviationColumnChanged(self, value):
        lib_state.set_display_object_maximum_deviation_state(value)
        idx = self.model.getColumnIndexFromColumnName(
            const.OBJECT_COLUMN_NAME_DEVIATION_MAXIMUM
        )
        self.treeView.setColumnHidden(idx, not value)
        return
