# Copyright (C) 2021 Patcha Saheb Binginapalli.
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

import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import Qt.QtWidgets as QtWidgets

import maya.cmds as cmds

import mmSolver.logger
import mmSolver.utils.time as time_utils
import mmSolver.utils.viewport as viewport_utils
import mmSolver.tools.createcontroller2.constant as const
import mmSolver.tools.createcontroller2.ui.ui_createcontroller_layout as ui_layout
import mmSolver.tools.createcontroller2.lib as lib


LOG = mmSolver.logger.get_logger()


def _transform_has_constraints(tfm_node):
    constraints = cmds.listRelatives(
        tfm_node, children=True, type="pointConstraint") or []
    constraints += cmds.listRelatives(
        tfm_node, children=True, type="parentConstraint") or []
    has_constraints = len(constraints) > 0
    return has_constraints


def _get_viewport_camera():
    """Get the Camera transform node in the active viewport."""
    model_editor = viewport_utils.get_active_model_editor()
    if model_editor is None:
        return None
    cam_tfm, cam_shp = viewport_utils.get_viewport_camera(model_editor)
    return cam_tfm


def _is_world_space_node(node, start_frame, end_frame):
    """
    Find out if a node is effectively in world-space or not.

    :returns:
        True if object is in global space, or False if object is in
        local space.
    :rtype: bool
    """
    if len(node) == 0 or not cmds.objExists(node):
        return False

    # Create node network to check if object is in world space.
    cmds.loadPlugin("matrixNodes", quiet=True)
    worldspace_check_matrix_node = None
    result_decomp_node = None
    # try:
    worldspace_check_matrix_node = cmds.createNode(
        "multMatrix",
        # name="mmSolver_cc_worldspace_check_node",
        skipSelect=True)
    result_decomp_node = cmds.createNode(
        "decomposeMatrix",
        # name="mmSolver_cc_worldspace_result_node",
        skipSelect=True)
    cmds.connectAttr(
        node + ".parentMatrix[0]",
        worldspace_check_matrix_node + ".matrixIn[1]",
        force=True)
    cmds.connectAttr(
        node + ".xformMatrix",
        worldspace_check_matrix_node + ".matrixIn[2]",
        force=True)
    cmds.connectAttr(
        worldspace_check_matrix_node + ".matrixSum",
        result_decomp_node + ".inputMatrix",
        force=True)

    # Get single frame pos and rotation sum
    pos = cmds.getAttr(
        result_decomp_node + ".outputTranslate",
        time=int(start_frame))[0]
    rot = cmds.getAttr(
        result_decomp_node + ".outputRotate",
        time=int(end_frame))[0]
    stored_sum = sum(pos) + sum(rot)

    # Check stored sum in all frames.
    #
    # True = object is in global space
    # False = object is in local space
    world_space_state = True
    for frame in range(start_frame, end_frame + 1):
        pos = cmds.getAttr(
            result_decomp_node + ".outputTranslate",
            time=frame)[0]
        rot = cmds.getAttr(
            result_decomp_node + ".outputRotate",
            time=frame)[0]
        pos_rot_sum = sum(pos) + sum(rot)
        if not pos_rot_sum == stored_sum:
            world_space_state = False
            break
    # finally:
    if worldspace_check_matrix_node and cmds.objExists(worldspace_check_matrix_node):
        cmds.delete(worldspace_check_matrix_node)
    if result_decomp_node and cmds.objExists(result_decomp_node):
        cmds.delete(result_decomp_node)

    return world_space_state


class CreateControllerLayout(QtWidgets.QWidget, ui_layout.Ui_Form):
    def __init__(self, parent=None, *args, **kwargs):
        super(CreateControllerLayout, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # Create Button Groups (because we get compile errors if
        # trying to create these in the .ui file).
        self.node_type_btnGrp = QtWidgets.QButtonGroup()
        self.node_type_btnGrp.addButton(self.group_rdo_btn)
        self.node_type_btnGrp.addButton(self.locator_rdo_btn)

        self.bake_mode_btnGrp = QtWidgets.QButtonGroup()
        self.bake_mode_btnGrp.addButton(self.full_bake_rdo_btn)
        self.bake_mode_btnGrp.addButton(self.smart_bake_rdo_btn)
        self.bake_mode_btnGrp.addButton(self.current_frame_rdo_btn)

        self.space_btnGrp = QtWidgets.QButtonGroup()
        self.space_btnGrp.addButton(self.world_space_rdo_btn)
        self.space_btnGrp.addButton(self.object_space_rdo_btn)
        self.space_btnGrp.addButton(self.screen_space_rdo_btn)

        # Create Connections
        self.main_object_btn.clicked.connect(self.get_main_object)
        self.pivot_object_btn.clicked.connect(self.get_pivot_object)
        self.node_type_btnGrp.buttonClicked.connect(self.radio_button_group_clicked)
        self.bake_mode_btnGrp.buttonClicked.connect(self.radio_button_group_clicked)
        self.space_btnGrp.buttonClicked.connect(self.radio_button_group_clicked)
        self.smart_bake_rdo_btn.clicked.connect(self.smart_bake_radio_button_clicked)
        self.world_space_rdo_btn.clicked.connect(self.world_space_radio_button_clicked)

        self.loc_grp_node = None
        self.reset_options()

    def set_option_widgets_enabled(self, value):
        """Set the enabled widget status for all options."""
        widgets = [
            self.type_label,
            self.group_rdo_btn,
            self.locator_rdo_btn,
            #
            self.bake_label,
            self.full_bake_rdo_btn,
            self.smart_bake_rdo_btn,
            self.current_frame_rdo_btn,
            #
            self.space_label,
            self.world_space_rdo_btn,
            self.object_space_rdo_btn,
            self.screen_space_rdo_btn,
        ]
        for widget in widgets:
            widget.setEnabled(value)
        return

    def get_pivot_object(self):
        """Set the pivot object widget as current selection."""
        selection = cmds.ls(selection=True, long=True) or []
        if not len(selection) == 1:
            LOG.warn("Please select exactly one object.")
            return
        self.pivot_object_text.setText(str(selection[0]))

    def get_main_object(self):
        """Set the main object widget as current selected transform."""
        selection = cmds.ls(selection=True, long=True, transforms=True) or []
        if not len(selection) == 1:
            LOG.warn("Please select exactly one transform object.")
            return
        self.main_object_text.setText(str(selection[0]))
        self.full_bake_rdo_btn.setChecked(True)
        self.object_space_rdo_btn.setChecked(True)
        self.set_option_widgets_enabled(True)

    def radio_button_group_clicked(self):
        # check if main object is selected already
        text = self.main_object_text.text()
        if not text:
            self.full_bake_rdo_btn.setChecked(True)
            self.object_space_rdo_btn.setChecked(True)
            self.locator_rdo_btn.setChecked(True)
            LOG.warn("Please get main object.")

    def smart_bake_radio_button_clicked(self):
        main_object_node = str(self.main_object_text.text())
        start_frame, end_frame = time_utils.get_maya_timeline_range_inner()
        is_world = _is_world_space_node(main_object_node, start_frame, end_frame)
        if is_world is False:
            if (self.smart_bake_rdo_btn.isChecked()
                    and self.world_space_rdo_btn.isChecked()):
                self.object_space_rdo_btn.setChecked(True)

    def world_space_radio_button_clicked(self):
        main_object_node = str(self.main_object_text.text())
        start_frame, end_frame = time_utils.get_maya_timeline_range_inner()
        is_world = _is_world_space_node(main_object_node, start_frame, end_frame)
        if is_world is False:
            if (self.world_space_rdo_btn.isChecked()
                    and self.smart_bake_rdo_btn.isChecked()):
                self.full_bake_rdo_btn.setChecked(True)
        return

    def create_locator_group(self):
        pivot_text = self.pivot_object_text.text()
        main_text = self.main_object_text.text()
        if pivot_text == "" or main_text == "":
            LOG.warn("Please get both pivot and main objects.")
            return
        if not cmds.objExists(pivot_text):
            LOG.warn("Could not find pivot object: %r", pivot_text)
            return
        if not cmds.objExists(main_text):
            LOG.warn("Could not find main object: %r", main_text)
            return

        loc_grp_name = str(self.locator_group_text.text())
        if not loc_grp_name:
            LOG.warn("Please type locator/group name.")
            return
        if self.group_rdo_btn.isChecked():
            self.loc_grp_node = cmds.group(empty=True, name=loc_grp_name)
        else:
            self.loc_grp_node = cmds.spaceLocator(name=loc_grp_name)

        # Move the loc_grp_node to the pivot object.
        pivot_matrix = cmds.xform(
            pivot_text, query=True, worldSpace=True, matrix=True)
        cmds.xform(self.loc_grp_node, worldSpace=True, matrix=pivot_matrix)

        # TODO: Should we de-select?
        cmds.select(clear=True)

    def create_controller_button_clicked(self):
        # Set time
        start_frame, end_frame = time_utils.get_maya_timeline_range_inner()
        if self.current_frame_rdo_btn.isChecked():
            start_frame = cmds.currentTime(query=True)
            end_frame = start_frame

        # Get widgets data
        controller_name = self.locator_group_text.text()
        pivot_node = self.pivot_object_text.text()
        main_node = self.main_object_text.text()
        loc_grp_node = self.loc_grp_node
        camera = _get_viewport_camera()
        space = None
        if self.world_space_rdo_btn.isChecked():
            space = const.CONTROLLER_TYPE_WORLD_SPACE
        elif self.object_space_rdo_btn.isChecked():
            space = const.CONTROLLER_TYPE_OBJECT_SPACE
        elif self.screen_space_rdo_btn.isChecked():
            space = const.CONTROLLER_TYPE_SCREEN_SPACE
        else:
            LOG.error("Invalid space.")
            return
        smart_bake = self.smart_bake_rdo_btn.isChecked()
        if not pivot_node:
            LOG.warn("Please get pivot object.")
            return
        if not main_node:
            LOG.warn("Please get main object.")
            return
        if not cmds.listRelatives(loc_grp_node, shapes=True):
            loc_grp_node = [loc_grp_node]
        if not cmds.objExists(loc_grp_node[0]):
            LOG.warn("Please create locator/group.")
            return
        if self.screen_space_rdo_btn.isChecked():
            if not camera:
                LOG.warn("Please select camera viewport.")
                return

        # Check if main node has constraints already
        has_constraints = _transform_has_constraints(main_node)
        if has_constraints is True:
            LOG.warn("Main object has constraints already.")
            cmds.delete(self.loc_grp_node)
            return

        controller_nodes = lib.create_controller(
            controller_name,
            pivot_node,
            main_node,
            loc_grp_node,
            start_frame,
            end_frame,
            space,
            smart_bake,
            camera)
        LOG.warn("Success: Create Controller.")

    def reset_options(self):
        # reset widgets to default
        self.pivot_object_text.clear()
        self.main_object_text.clear()
        self.locator_rdo_btn.setChecked(True)
        self.full_bake_rdo_btn.setChecked(True)
        self.object_space_rdo_btn.setChecked(True)
        self.locator_group_text.clear()
        self.set_option_widgets_enabled(False)
