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

import mmSolver.ui.Qt.QtWidgets as QtWidgets

import maya.cmds as cmds

import mmSolver.logger
import mmSolver.utils.time as time_utils
import mmSolver.utils.viewport as viewport_utils
import mmSolver.tools.userpreferences.constant as userprefs_const
import mmSolver.tools.userpreferences.lib as userprefs_lib
import mmSolver.tools.createcontroller2.constant as const
import mmSolver.tools.createcontroller2.ui.ui_createcontroller_layout as ui_layout
import mmSolver.tools.createcontroller2.lib as lib


LOG = mmSolver.logger.get_logger()


def _transform_has_constraints(tfm_node):
    constraints = (
        cmds.listRelatives(tfm_node, children=True, type='pointConstraint') or []
    )
    constraints += (
        cmds.listRelatives(tfm_node, children=True, type='parentConstraint') or []
    )
    has_constraints = len(constraints) > 0
    return has_constraints


def _get_viewport_camera():
    """Get the Camera transform node in the active viewport."""
    model_editor = viewport_utils.get_active_model_editor()
    if model_editor is None:
        return None
    cam_tfm, cam_shp = viewport_utils.get_viewport_camera(model_editor)
    return cam_tfm


class CreateControllerLayout(QtWidgets.QWidget, ui_layout.Ui_Form):
    def __init__(self, parent=None, *args, **kwargs):
        super(CreateControllerLayout, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # Create Button Groups (because we get compile errors if
        # trying to create these in the .ui file).
        self.pivot_type_btnGrp = QtWidgets.QButtonGroup()
        self.pivot_type_btnGrp.addButton(self.pivot_static_rdo_btn)
        self.pivot_type_btnGrp.addButton(self.pivot_dynamic_rdo_btn)

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
        self.smart_bake_rdo_btn.clicked.connect(self.smart_bake_radio_button_clicked)
        self.full_bake_rdo_btn.clicked.connect(self.fullbake_space_radio_button_clicked)
        self.current_frame_rdo_btn.clicked.connect(
            self.fullbake_space_radio_button_clicked
        )

        self.reset_options()

    def get_pivot_object(self):
        """Set the pivot object widget as current selection."""
        selection = cmds.ls(selection=True, long=True) or []
        if not len(selection) == 1:
            LOG.warn('Please select exactly one object.')
            return
        self.pivot_object_text.setText(str(selection[0]))

    def get_main_object(self):
        """Set the main object widget as current selected transform."""
        selection = cmds.ls(selection=True, long=True, transforms=True) or []
        if not len(selection) == 1:
            LOG.warn('Please select exactly one transform object.')
            return
        self.main_object_text.setText(str(selection[0]))

    def smart_bake_radio_button_clicked(self):
        self.world_space_rdo_btn.setEnabled(False)
        if self.world_space_rdo_btn.isChecked():
            self.object_space_rdo_btn.setChecked(True)

    def fullbake_space_radio_button_clicked(self):
        self.world_space_rdo_btn.setEnabled(True)

    def create_locator_group(self):
        pivot_text = self.pivot_object_text.text()
        main_text = self.main_object_text.text()
        if pivot_text == '' or main_text == '':
            LOG.warn('Please get both pivot and main objects.')
            return
        if not cmds.objExists(pivot_text):
            LOG.warn('Could not find pivot object: %r', pivot_text)
            return
        if not cmds.objExists(main_text):
            LOG.warn('Could not find main object: %r', main_text)
            return

        loc_grp_name = str(self.locator_group_text.text())
        if not loc_grp_name:
            LOG.warn('Please type controller name.')
            return

        # The user preferences are used so that the user only has to
        # change this value once, for all Maya scenes. It is assumed
        # that users won't often want to change this value.
        config = userprefs_lib.get_config()
        key = userprefs_const.CREATE_CONTROLLER_SHAPE_KEY
        ctrl_type = userprefs_lib.get_value(config, key)
        if ctrl_type == userprefs_const.CREATE_CONTROLLER_SHAPE_LOCATOR_VALUE:
            loc_grp_node = cmds.spaceLocator(name=loc_grp_name)
        elif ctrl_type == userprefs_const.CREATE_CONTROLLER_SHAPE_GROUP_VALUE:
            loc_grp_node = cmds.group(empty=True, name=loc_grp_name)
            loc_grp_node = [loc_grp_node]
        else:
            raise NotImplementedError

        return loc_grp_node

    def create_controller_button_clicked(self):
        loc_grp_node = self.create_locator_group()
        if loc_grp_node is None or len(loc_grp_node) == 0:
            LOG.warn('Locator Group node is invalid, exiting: %r', loc_grp_node)
            return

        # Set time
        start_frame, end_frame = time_utils.get_maya_timeline_range_inner()
        if self.current_frame_rdo_btn.isChecked():
            start_frame = int(cmds.currentTime(query=True))
            end_frame = start_frame

        # Get widgets data
        controller_name = self.locator_group_text.text()
        pivot_node = self.pivot_object_text.text()
        main_node = self.main_object_text.text()
        if not controller_name or not pivot_node or not main_node:
            LOG.error(
                'Invalid nodes given: controller_name=%r pivot_node=%r main_node=%r',
                controller_name,
                pivot_node,
                main_node,
            )
            cmds.delete(loc_grp_node)
            return
        camera = _get_viewport_camera()
        smart_bake = self.smart_bake_rdo_btn.isChecked() is True
        dynamic_pivot = self.pivot_dynamic_rdo_btn.isChecked() is True
        if self.world_space_rdo_btn.isChecked():
            space = const.CONTROLLER_SPACE_WORLD
        elif self.object_space_rdo_btn.isChecked():
            space = const.CONTROLLER_SPACE_OBJECT
        elif self.screen_space_rdo_btn.isChecked():
            space = const.CONTROLLER_SPACE_SCREEN
        else:
            LOG.error('Create Controller: Invalid space value.')
            return
        if self.screen_space_rdo_btn.isChecked():
            if not camera:
                LOG.warn('Please select camera viewport.')
                cmds.delete(loc_grp_node)
                return

        # Check if main node has constraints already
        has_constraints = _transform_has_constraints(main_node)
        if has_constraints is True:
            LOG.warn('Main object has constraints already.')
            cmds.delete(loc_grp_node)
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
            camera,
            dynamic_pivot,
        )
        cmds.select(controller_nodes, replace=True)

    def reset_options(self):
        # reset widgets to default
        self.pivot_object_text.clear()
        self.main_object_text.clear()
        self.pivot_static_rdo_btn.setChecked(True)
        self.full_bake_rdo_btn.setChecked(True)
        self.world_space_rdo_btn.setEnabled(True)
        self.object_space_rdo_btn.setChecked(True)
        self.locator_group_text.clear()
