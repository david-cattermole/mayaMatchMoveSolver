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
The main component of the user interface for the create controller
window.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mmSolver.ui.qtpyutils as qtpyutils

qtpyutils.override_binding_order()

import mmSolver.ui.Qt.QtWidgets as QtWidgets

import maya.cmds

import mmSolver.logger
import mmSolver.utils.time as time_utils
import mmSolver.utils.tools as tools_utils
import mmSolver.utils.constant as const_utils
import mmSolver.utils.configmaya as configmaya
import mmSolver.ui.helputils as helputils
import mmSolver.ui.commonmenus as commonmenus
import mmSolver.tools.createcontroller2.constant as const
import mmSolver.tools.createcontroller2.lib as lib
import mmSolver.tools.createcontroller3beta.ui.constant as ui_const
import mmSolver.tools.createcontroller3beta.ui.ui_createcontroller_layout as ui_layout

LOG = mmSolver.logger.get_logger()


# TODO: Move this into another file.
def _transform_has_constraints(tfm_node):
    constraints = (
        maya.cmds.listRelatives(tfm_node, children=True, type='pointConstraint') or []
    )
    constraints += (
        maya.cmds.listRelatives(tfm_node, children=True, type='parentConstraint') or []
    )
    return len(constraints) > 0


# TODO: Move this into another file.
def _is_world_space_node(node, start_frame, end_frame):
    """
    Find out if a node is effectively in world-space or not.

    :returns:
        True if object is in global space, or False if object is in
        local space.
    :rtype: bool
    """
    if len(node) == 0 or not maya.cmds.objExists(node):
        return False

    # Create node network to check if object is in world space.
    maya.cmds.loadPlugin('matrixNodes', quiet=True)
    worldspace_check_matrix_node = None
    result_decomp_node = None
    worldspace_check_matrix_node = maya.cmds.createNode('multMatrix', skipSelect=True)
    result_decomp_node = maya.cmds.createNode('decomposeMatrix', skipSelect=True)
    maya.cmds.connectAttr(
        node + '.parentMatrix[0]',
        worldspace_check_matrix_node + '.matrixIn[1]',
        force=True,
    )
    maya.cmds.connectAttr(
        node + '.xformMatrix', worldspace_check_matrix_node + '.matrixIn[2]', force=True
    )
    maya.cmds.connectAttr(
        worldspace_check_matrix_node + '.matrixSum',
        result_decomp_node + '.inputMatrix',
        force=True,
    )

    # Get single frame pos and rotation sum
    pos = maya.cmds.getAttr(
        result_decomp_node + '.outputTranslate', time=int(start_frame)
    )[0]
    rot = maya.cmds.getAttr(result_decomp_node + '.outputRotate', time=int(end_frame))[
        0
    ]
    stored_sum = sum(pos) + sum(rot)
    # Check stored sum in all frames.
    #
    # True = object is in global space
    # False = object is in local space
    world_space_state = True
    for frame in range(start_frame, end_frame + 1):
        pos = maya.cmds.getAttr(result_decomp_node + '.outputTranslate', time=frame)[0]
        rot = maya.cmds.getAttr(result_decomp_node + '.outputRotate', time=frame)[0]
        pos_rot_sum = sum(pos) + sum(rot)
        if pos_rot_sum != stored_sum:
            world_space_state = False
            break
    if worldspace_check_matrix_node and maya.cmds.objExists(
        worldspace_check_matrix_node
    ):
        maya.cmds.delete(worldspace_check_matrix_node)
    if result_decomp_node and maya.cmds.objExists(result_decomp_node):
        maya.cmds.delete(result_decomp_node)
    return world_space_state


def _open_help():
    src = helputils.get_help_source()
    page = 'tools_generaltools.html#create-controller'
    helputils.open_help_in_browser(page=page, help_source=src)
    return


class CreateControllerLayout(QtWidgets.QWidget, ui_layout.Ui_Form):
    def __init__(self, parent=None, *args, **kwargs):
        super(CreateControllerLayout, self).__init__(*args, **kwargs)
        self.setupUi(self)
        # Add menus
        self.menu_bar = QtWidgets.QMenuBar(self)
        self.edit_menu = QtWidgets.QMenu('Edit', self.menu_bar)
        commonmenus.create_edit_menu_items(
            self.edit_menu, reset_settings_func=self.reset_options
        )
        self.menu_bar.addMenu(self.edit_menu)
        # Type menu
        self.type_menu = QtWidgets.QMenu('Controller Type', self.menu_bar)
        self.type_action_group = QtWidgets.QActionGroup(self.type_menu)
        self.group_action = QtWidgets.QAction('Group', self.type_menu)
        self.group_action.setCheckable(True)
        self.type_menu.addAction(self.group_action)
        self.group_action.setActionGroup(self.type_action_group)
        self.locator_action = QtWidgets.QAction('Locator', self.type_menu)
        self.locator_action.setCheckable(True)
        self.locator_action.setChecked(True)
        self.type_menu.addAction(self.locator_action)
        self.locator_action.setActionGroup(self.type_action_group)
        self.menu_bar.addMenu(self.type_menu)
        # Help menu
        help_menu = QtWidgets.QMenu('Help', self.menu_bar)
        commonmenus.create_help_menu_items(help_menu, tool_help_func=_open_help)
        self.menu_bar.addMenu(help_menu)

        # Create connections
        self.setMainObjectButton.clicked.connect(self.set_main_object_clicked)
        self.setPivotObjectButton.clicked.connect(self.set_pivot_object_clicked)
        self.createcontrollerButtton.clicked.connect(
            self.create_controller_button_clicked
        )
        self.selectInOutlinerButton.clicked.connect(self.select_in_outliner_clicked)
        self.locator_action.triggered.connect(self.type_locator_rdo_toggled)
        self.group_action.triggered.connect(self.type_group_rdo_toggled)

        self.populate_ui()

    def populate_ui(self):
        name = ui_const.CONFIG_CONTROLLER_TYPE
        default_value = ui_const.CONFIG_CONTROLLER_TYPE_LOCATOR
        ctrl_type = configmaya.get_scene_option(name, default_value)
        if ctrl_type == ui_const.CONFIG_CONTROLLER_TYPE_LOCATOR:
            self.locator_action.setChecked(True)
        elif ctrl_type == ui_const.CONFIG_CONTROLLER_TYPE_GROUP:
            self.group_action.setChecked(True)

    def type_locator_rdo_toggled(self):
        if self.locator_action.isChecked():
            name = ui_const.CONFIG_CONTROLLER_TYPE
            value = ui_const.CONFIG_CONTROLLER_TYPE_LOCATOR
            configmaya.set_scene_option(name, value, add_attr=True)

    def type_group_rdo_toggled(self):
        if self.group_action.isChecked():
            name = ui_const.CONFIG_CONTROLLER_TYPE
            value = ui_const.CONFIG_CONTROLLER_TYPE_GROUP
            configmaya.set_scene_option(name, value, add_attr=True)

    def get_existing_names_from_ui(self, column):
        names = []
        row_count = self.mainTableWidget.rowCount()
        for row in range(row_count):
            name = self.mainTableWidget.item(row, column).text()
            names.append(name)
        return names

    def set_object_helper(self, column, main=False, pivot=False):
        warn_msg_obj = ''
        if main:
            warn_msg_obj = 'Main object'
        elif pivot:
            warn_msg_obj = 'Pivot object'

        item_column = None
        selected_item = self.mainTableWidget.selectedItems() or []
        if selected_item:
            item_column = self.mainTableWidget.column(selected_item[0])
        if len(selected_item) != 1 or item_column != column:
            LOG.warn('Please select exactly one %s cell from UI.', warn_msg_obj.lower())
            return
        selection = maya.cmds.ls(selection=True, long=True) or []
        if len(selection) != 1:
            LOG.warn('Please select exactly one maya object.')
            return
        if main:
            existing_names = self.get_existing_names_from_ui(column)
            if selection[0] in existing_names:
                LOG.warn('%s already exists.', warn_msg_obj)
                return
            # Check if main node has constraints already
            has_constraints = _transform_has_constraints(selection[0])
            if has_constraints is True:
                LOG.warn('Main object has constraints already.')
                return
        selected_item[0].setText(str(selection[0]))

    def set_main_object_clicked(self):
        self.set_object_helper(ui_const.COLUMN_MAIN_OBJECT_INDEX, True, False)

    def set_pivot_object_clicked(self):
        self.set_object_helper(ui_const.COLUMN_PIVOT_OBJECT_INDEX, False, True)

    def create_locator_group(self, name, main_text, pivot_text):
        if pivot_text == '' or main_text == '':
            LOG.warn('Please get both pivot and main objects.')
            return
        if not maya.cmds.objExists(pivot_text):
            LOG.warn('Could not find pivot object: %r', pivot_text)
            return
        if not maya.cmds.objExists(main_text):
            LOG.warn('Could not find main object: %r', main_text)
            return
        if not name:
            LOG.warn('Controller name not found.')
            return
        if self.group_action.isChecked():
            return maya.cmds.group(empty=True, name=name)
        else:
            return maya.cmds.spaceLocator(name=name)

    def get_combo_box_value(self, row, column):
        return self.mainTableWidget.cellWidget(row, column).currentText()

    def get_selected_rows(self):
        selected_items = self.mainTableWidget.selectedItems()
        rows = []
        for item in selected_items:
            row = self.mainTableWidget.row(item)
            if row not in rows:
                rows.append(row)
        return rows

    def select_in_outliner_clicked(self):
        selected_items = self.mainTableWidget.selectedItems()
        for item in selected_items:
            column = self.mainTableWidget.column(item)
            if column not in [
                ui_const.COLUMN_MAIN_OBJECT_INDEX,
                ui_const.COLUMN_PIVOT_OBJECT_INDEX,
            ]:
                LOG.warn('Please select main object or pivot object cell.')
                return
            text = item.text()
            maya.cmds.select(text, replace=True)

    def create_controller_button_clicked(self):
        rows = self.mainTableWidget.rowCount()
        if not rows:
            LOG.warn('No rows found to create controller.')
            return

        for row in range(rows):
            # Set time
            start_frame, end_frame = time_utils.get_maya_timeline_range_inner()
            bake_value = self.get_combo_box_value(row, ui_const.COLUMN_BAKE_INDEX)
            if bake_value == const.BAKE_ITEM_CURRENT_FRAME_BAKE:
                start_frame = int(maya.cmds.currentTime(query=True))
                end_frame = start_frame

            # Get widgets data
            controller_name = self.mainTableWidget.item(
                row, ui_const.COLUMN_CONTROLLER_NAME_INDEX
            ).text()
            main_node = self.mainTableWidget.item(
                row, ui_const.COLUMN_MAIN_OBJECT_INDEX
            ).text()
            pivot_node = self.mainTableWidget.item(
                row, ui_const.COLUMN_PIVOT_OBJECT_INDEX
            ).text()
            camera = self.get_combo_box_value(row, ui_const.COLUMN_CAMERA_INDEX)

            pivot_type = self.get_combo_box_value(row, ui_const.COLUMN_PIVOT_TYPE_INDEX)
            dynamic_pivot = pivot_type == const.PIVOT_TYPE_ITEM_DYNAMIC

            loc_grp_node = self.create_locator_group(
                controller_name, main_node, pivot_node
            )

            # Space options
            space = None
            space_option = self.get_combo_box_value(row, ui_const.COLUMN_SPACE_INDEX)
            if space_option == const.SPACE_ITEM_WORLD_SPACE:
                space = const.CONTROLLER_TYPE_WORLD_SPACE
            elif space_option == const.SPACE_ITEM_OBJECT_SPACE:
                space = const.CONTROLLER_TYPE_OBJECT_SPACE
            elif space_option == const.SPACE_ITEM_SCREEN_SPACE:
                space = const.CONTROLLER_TYPE_SCREEN_SPACE
            else:
                LOG.error('Invalid space.')
                return
            if space_option == const.SPACE_ITEM_SCREEN_SPACE and not camera:
                LOG.warn('Please select camera from UI.')
                if maya.cmds.objExists(loc_grp_node[0]):
                    maya.cmds.delete(loc_grp_node[0])
                return

            # Bake options
            bake_option = self.get_combo_box_value(row, ui_const.COLUMN_BAKE_INDEX)
            smart_bake = bake_option == const.BAKE_ITEM_SMART_BAKE
            if not controller_name or not pivot_node or not main_node:
                return

            # Check if main node has constraints already
            has_constraints = _transform_has_constraints(main_node)
            if has_constraints is True:
                LOG.warn('Main object has constraints already.')
                maya.cmds.delete(loc_grp_node)
                return

            ctx = tools_utils.tool_context(
                use_undo_chunk=True,
                restore_current_frame=True,
                use_dg_evaluation_mode=True,
                disable_viewport=True,
                disable_viewport_mode=const_utils.DISABLE_VIEWPORT_MODE_VP1_VALUE,
            )
            with ctx:
                controller_nodes = lib.create_controller(
                    controller_name,
                    pivot_node,
                    main_node,
                    loc_grp_node,
                    start_frame,
                    end_frame,
                    space,
                    smart_bake,
                    camera,
                    dynamic_pivot,
                )
                maya.cmds.select(controller_nodes, replace=True)
                LOG.warn('Success: Create Controller(s).')
        self.reset_options()

    def reset_options(self):
        self.mainTableWidget.setRowCount(0)
