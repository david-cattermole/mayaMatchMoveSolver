# Copyright (C) 2022 Patcha Saheb Binginapalli.
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
Window for the Create Controller tool.

Usage::

   import mmSolver.tools.createcontroller3beta.ui.createcontroller_window as createcontroller_window
   createcontroller_window.main()

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mmSolver.ui.qtpyutils as qtpyutils

qtpyutils.override_binding_order()

import mmSolver.ui.Qt.QtCore as QtCore
import mmSolver.ui.Qt.QtWidgets as QtWidgets

import maya.cmds as cmds

import mmSolver.logger
import mmSolver.ui.uiutils as uiutils
import mmSolver.tools.createcontroller3beta.constant as const
import mmSolver.tools.createcontroller3beta.ui.constant as ui_const
import mmSolver.tools.createcontroller3beta.ui.createcontroller_layout as ui_layout

import mmSolver.tools.loadmarker.lib.utils as cam_lib

LOG = mmSolver.logger.get_logger()
baseModule, BaseWindow = uiutils.getBaseWindow()
WINDOW_TITLE = "Create Controller"


def _transform_has_constraints(tfm_node):
    constraints = (
        cmds.listRelatives(tfm_node, children=True, type='pointConstraint') or []
    )
    constraints += (
        cmds.listRelatives(tfm_node, children=True, type='parentConstraint') or []
    )
    return len(constraints) > 0


class ComboBox(QtWidgets.QComboBox):
    def __init__(self, row, column, item_list, table_widget=None):
        super(ComboBox, self).__init__()
        self.table_widget = table_widget
        for count, item in enumerate(item_list):
            self.addItem(item)
            self.setItemData(count, [row, column])
        self.currentIndexChanged.connect(self.index_changed)

    def wheelEvent(self, event):
        event.ignore()

    def index_changed(self):
        idx = self.currentIndex()
        row, column = self.itemData(idx)
        if (
            column == ui_const.COLUMN_BAKE_INDEX
            and self.currentText() == const.BAKE_ITEM_SMART_BAKE
        ):
            cell_widget = self.table_widget.cellWidget(row, ui_const.COLUMN_SPACE_INDEX)
            item_text = cell_widget.currentText()
            if item_text == const.SPACE_ITEM_WORLD_SPACE:
                cell_widget.setCurrentIndex(1)
        elif column == ui_const.COLUMN_SPACE_INDEX:
            camera_cell_widget = self.table_widget.cellWidget(
                row, ui_const.COLUMN_CAMERA_INDEX
            )
            if self.currentText() == const.SPACE_ITEM_WORLD_SPACE:
                camera_cell_widget.setEnabled(False)
                camera_cell_widget.setCurrentIndex(0)
                cell_widget = self.table_widget.cellWidget(
                    row, ui_const.COLUMN_BAKE_INDEX
                )
                item_text = cell_widget.currentText()
                if item_text == const.BAKE_ITEM_SMART_BAKE:
                    cell_widget.setCurrentIndex(0)
            elif self.currentText() == const.SPACE_ITEM_OBJECT_SPACE:
                camera_cell_widget.setEnabled(False)
                camera_cell_widget.setCurrentIndex(0)
            elif self.currentText() == const.SPACE_ITEM_SCREEN_SPACE:
                camera_cell_widget.setEnabled(True)
                camera_cell_widget.setCurrentIndex(1)
        return


class CreateControllerWindow(BaseWindow):
    name = 'CreateController3Window'

    def __init__(self, parent=None, name=None):
        super(CreateControllerWindow, self).__init__(parent, name=name)
        self.setupUi(self)
        self.addSubForm(ui_layout.CreateControllerLayout)
        self.form = self.getSubForm()

        self.setWindowTitle(WINDOW_TITLE)
        self.setWindowType(qtpyutils.WINDOW_TYPE_DIALOG)

        # Hide irrelevant stuff
        self.baseHideStandardButtons()
        self.baseHideProgressBar()

        # Set menubar
        self.setMenuBar(self.form.menu_bar)

        # Create Connections
        self.form.addButton.clicked.connect(self.add_objects_clicked)
        self.form.deleteButton.clicked.connect(self.delete_objects_clicked)
        self.form.closeButton.clicked.connect(self.close_clicked)

    def close_clicked(self):
        self.close()

    def resizeEvent(self, event):
        win_width = self.width()
        self.resize_columns(win_width)
        QtWidgets.QMainWindow.resizeEvent(self, event)

    def insert_item(self, row, column, name):
        item = QtWidgets.QTableWidgetItem(name)
        self.form.mainTableWidget.setItem(row, column, item)

    def insert_combo_box(self, row, column, item_list, enable_flag=True):
        combo_widget = ComboBox(row, column, item_list, self.form.mainTableWidget)
        combo_widget.setEnabled(enable_flag)
        self.form.mainTableWidget.setCellWidget(row, column, combo_widget)

    def add_objects_clicked(self):
        selection = cmds.ls(selection=True, long=True, transforms=True) or []
        if not selection:
            LOG.warn('Please select transform type object(s).')
            return
        main_names = self.form.get_existing_names_from_ui(
            ui_const.COLUMN_MAIN_OBJECT_INDEX
        )
        current_row_count = self.form.mainTableWidget.rowCount()
        cam_tfm_list = ['']
        all_camera_nodes = cam_lib.get_cameras()
        for cam in all_camera_nodes:
            cam_tfm = cam.get_transform_node()
            cam_tfm_list.append(cam_tfm)
        for node in selection:
            has_constraints = _transform_has_constraints(node)
            if has_constraints is True:
                LOG.warn('Main object(s) have constraints already.')
                break
        if not has_constraints:
            for node in selection:
                if node not in main_names:
                    self.form.mainTableWidget.insertRow(current_row_count)
                    object_indices = [
                        ui_const.COLUMN_CONTROLLER_NAME_INDEX,
                        ui_const.COLUMN_MAIN_OBJECT_INDEX,
                        ui_const.COLUMN_PIVOT_OBJECT_INDEX,
                    ]
                    for count, idx in enumerate(object_indices):
                        self.insert_item(current_row_count, object_indices[count], node)
                    combo_indices = [
                        ui_const.COLUMN_PIVOT_TYPE_INDEX,
                        ui_const.COLUMN_BAKE_INDEX,
                        ui_const.COLUMN_SPACE_INDEX,
                    ]
                    combo_items = [
                        const.PIVOT_TYPE_ITEM_LIST,
                        const.BAKE_ITEM_LIST,
                        const.SPACE_ITEM_LIST,
                    ]
                    for count, idx in enumerate(combo_indices):
                        self.insert_combo_box(
                            current_row_count,
                            combo_indices[count],
                            combo_items[count],
                            True,
                        )
                        self.insert_combo_box(
                            current_row_count,
                            ui_const.COLUMN_CAMERA_INDEX,
                            cam_tfm_list,
                            False,
                        )
                    current_row_count += 1
        # Column resize
        win_width = self.width()
        self.resize_columns(win_width)

    def resize_columns(self, win_width):
        win_width = self.width() - 30
        if win_width % 2 != 0:
            win_width = win_width - 1
        win_width = win_width - (
            ui_const.COLUMN_PIVOT_TYPE_INDEX_SIZE
            + ui_const.COLUMN_BAKE_INDEX_SIZE
            + ui_const.COLUMN_SPACE_INDEX_SIZE
        )
        each_column_width = win_width / 4
        index_list = ui_const.COLUMN_INDICES_LIST
        column_size_list = [
            each_column_width,
            each_column_width,
            each_column_width,
            each_column_width,
            ui_const.COLUMN_PIVOT_TYPE_INDEX_SIZE,
            ui_const.COLUMN_BAKE_INDEX_SIZE,
            ui_const.COLUMN_SPACE_INDEX_SIZE,
        ]
        for count, idx in enumerate(column_size_list):
            self.form.mainTableWidget.horizontalHeader().resizeSection(
                index_list[count], column_size_list[count]
            )

    def delete_objects_clicked(self):
        selected_items = self.form.mainTableWidget.selectedItems()
        rows = []
        for item in selected_items:
            row = self.form.mainTableWidget.row(item) + 1
            if row not in rows:
                rows.append(row)
        rows.sort()
        rows.reverse()
        if not rows:
            LOG.warn('Please select row(s) to delete.')
            return
        for i in rows:
            self.form.mainTableWidget.removeRow(i - 1)


def main(show=True, auto_raise=True, delete=False):
    win = CreateControllerWindow.open_window(
        show=show, auto_raise=auto_raise, delete=delete
    )
    return win
