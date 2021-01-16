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

import mmSolver.logger
import mmSolver.tools.createcontroller2.ui.ui_createcontroller_layout as ui_layout
import mmSolver.tools.createcontroller2.lib as lib
import mmSolver.tools.createcontroller2.tool as tool
import mmSolver.utils.tools as tools_utils
import mmSolver.utils.viewport as viewport_utils

LOG = mmSolver.logger.get_logger()

import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
import maya.cmds as cmds
import maya.mel as mel

start_frame = cmds.playbackOptions(q=True, min=True)
end_frame = cmds.playbackOptions(q=True, max=True)

def transform_has_constraints(tfm_node):
    constraints = cmds.listRelatives(
        tfm_node, children=True, type="pointConstraint") or []
    constraints += cmds.listRelatives(
        tfm_node, children=True, type="parentConstraint") or []
    has_constraints = len(constraints) > 0
    return has_constraints

def getViewportCamera():
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
        
        #create connections
        self.main_object_btn.clicked.connect(self.getMainObject)
        self.pivot_object_btn.clicked.connect(self.getPivotObject)
        self.buttonGroup.buttonClicked.connect(self.radioButtonGroupClicked)
        self.buttonGroup_2.buttonClicked.connect(self.radioButtonGroupClicked)
        self.buttonGroup_3.buttonClicked.connect(self.radioButtonGroupClicked)
        self.smart_bake_rdo_btn.clicked.connect(self.smartBakeRadioButtonClicked)
        self.world_space_rdo_btn.clicked.connect(self.worldSpaceRadioButtonClicked)
        self.locator_group_btn.clicked.connect(self.createLocatorGroup)
        self.create_controller_btn.clicked.connect(self.createControllerButtonClicked)
        self.reset_btn.clicked.connect(self.reset)

        self.loc_grp_node = None

    def getPivotObject(self):
        selection = cmds.ls(selection=True, long=True)
        if not len(selection) == 1:
            LOG.warn("Please select exactly one object.")
            return
        self.pivot_object_text.setText(str(selection[0]))                 

    def getMainObject(self):
        selection = cmds.ls(selection=True, long=True, transforms=True)
        if not len(selection) == 1:
            LOG.warn("Please select exactly one transform object.")
            return
        self.main_object_text.setText(str(selection[0]))
        self.full_bake_rdo_btn.setChecked(True)
        self.object_space_rdo_btn.setChecked(True)

    def deleteNodeNetwork(self):
        if cmds.objExists("mmSolver_cc*"):
            cmds.delete("mmSolver_cc*")    

    def worldSpaceCheck(self):
        node = str(self.main_object_text.text())
        if not node:
            return
        #create node network to check if object is in world space
        #delete existing nodes if any
        self.deleteNodeNetwork()
        #create nodes and connections
        worldspace_check_matrix_node = cmds.shadingNode("multMatrix", asUtility=True, n="mmSolver_cc_worldspace_check_node")
        result_decomp_node = cmds.shadingNode("decomposeMatrix", asUtility=True, n="mmSolver_cc_worldspace_result_node")
        cmds.connectAttr(node+".parentMatrix[0]", worldspace_check_matrix_node+".matrixIn[1]", force=True)
        cmds.connectAttr(node+".xformMatrix", worldspace_check_matrix_node+".matrixIn[2]", force=True)
        cmds.connectAttr(worldspace_check_matrix_node+".matrixSum", result_decomp_node+".inputMatrix", force=True)
        world_space_state = True
        #get single frame pos and rot sum
        pos = cmds.getAttr(result_decomp_node+".outputTranslate", time=int(start_frame))[0]
        rot = cmds.getAttr(result_decomp_node+".outputRotate", time=int(end_frame))[0]
        stored_sum = sum(pos) + sum(rot)   
        #check stored sum in all frames
        #True = object is in global space
        #False = object is in local space
        for frame in range(int(start_frame), int(end_frame)+1):         
            pos = cmds.getAttr(result_decomp_node+".outputTranslate", time=frame)[0]
            rot = cmds.getAttr(result_decomp_node+".outputRotate", time=frame)[0]
            pos_rot_sum = sum(pos) + sum(rot)
            if not pos_rot_sum == stored_sum:
                world_space_state = False
                break
        #delete nodes
        self.deleteNodeNetwork()
        return world_space_state

    def radioButtonGroupClicked(self):
        #check if main object is selected already
        text = self.main_object_text.text()
        if not text:
            self.full_bake_rdo_btn.setChecked(True)
            self.object_space_rdo_btn.setChecked(True)
            self.locator_rdo_btn.setChecked(True)
            LOG.warn("Please get main object.")

    def smartBakeRadioButtonClicked(self):      
        world = self.worldSpaceCheck()
        if world == False:
            if self.smart_bake_rdo_btn.isChecked() and self.world_space_rdo_btn.isChecked():
                self.object_space_rdo_btn.setChecked(True)

    def worldSpaceRadioButtonClicked(self):
        world = self.worldSpaceCheck()
        if world == False:
            if self.world_space_rdo_btn.isChecked() and self.smart_bake_rdo_btn.isChecked():
                self.full_bake_rdo_btn.setChecked(True)

    def createLocatorGroup(self):
        pivot_text = self.pivot_object_text.text()
        main_text = self.main_object_text.text()
        if pivot_text == "" or main_text == "" :
            LOG.warn("Please get both pivot and main objects.")
            return
        loc_grp_name = str(self.locator_group_text.text())
        if not loc_grp_name:
            LOG.warn("Please type locator/group name.")
            return
        if self.group_rdo_btn.isChecked():
            self.loc_grp_node = cmds.group(empty=True, name=loc_grp_name)
        else:
            self.loc_grp_node = cmds.spaceLocator(name=loc_grp_name)
        cmds.select(clear=True)

    def createControllerButtonClicked(self):
        #set time
        start_frame = cmds.playbackOptions(q=True, min=True)
        end_frame = cmds.playbackOptions(q=True, max=True) 
        if self.current_frame_rdo_btn.isChecked():
            start_frame = cmds.currentTime(query=True)
            end_frame = start_frame

        #get widgets data
        name = self.locator_group_text.text()
        pivot_node = self.pivot_object_text.text()
        main_node = self.main_object_text.text()
        loc_grp_node = self.loc_grp_node 
        camera = getViewportCamera() 
        if self.world_space_rdo_btn.isChecked():
            space = "worldSpace"
        elif self.object_space_rdo_btn.isChecked():
            space = "objectSpace"
        elif self.screen_space_rdo_btn.isChecked():
            space = "screenSpace"
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

        #check if main node has constraints already
        has_constraints = transform_has_constraints(main_node)
        if has_constraints is True:
            LOG.warn("Main object has constraints already.")
            cmds.delete(self.loc_grp_node)
            return

        #create controller
        lib.createController(name,
                             pivot_node,
                             main_node,
                             loc_grp_node,
                             start_frame,
                             end_frame,
                             space,
                             smart_bake,
                             camera)

        LOG.warn("Success: Create Controller.")

    def reset(self):
        #reset widgets to default
        self.pivot_object_text.clear()
        self.main_object_text.clear()
        self.locator_rdo_btn.setChecked(True)
        self.full_bake_rdo_btn.setChecked(True)
        self.object_space_rdo_btn.setChecked(True)
        self.locator_group_text.clear()
