"""
To run, type:

import create_controller as tool
reload(tool)
tool.main()

"""
import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets

import maya.OpenMaya as om
import maya.OpenMayaUI as omui
import maya.OpenMayaAnim as oma
import maya.cmds as cmds
import maya.mel as mel

import mmSolver.logger
import mmSolver.ui.uiutils as uiutils
import mmSolver.utils.viewport as viewport_utils
import mmSolver.utils.time as time_utils
import mmSolver.utils.tools as tools_utils

LOG = mmSolver.logger.get_logger()
baseModule, BaseWindow = uiutils.getBaseWindow()


def transform_has_constraints(tfm_node):
    constraints = cmds.listRelatives(
        tfm_node, children=True, type="pointConstraint") or []
    constraints += cmds.listRelatives(
        tfm_node, children=True, type="parentConstraint") or []
    has_constraints = len(constraints) > 0
    return has_constraints


class CreateControllerWindow(BaseWindow):

    def __init__(self, parent=None, name=None):
        super(CreateControllerWindow, self).__init__(parent,
                                                     name=name)
        self.setWindowTitle("Create Controller")
        self.setMinimumWidth(480)
        self.setMinimumHeight(210)
        self.setMaximumWidth(480)
        self.setMaximumHeight(210)
        self.setWindowFlags(QtCore.Qt.Tool)

        self.addSubForm(CreateControllerLayout)

        # Hide irrelevant stuff
        self.baseHideMenuBar()
        self.baseHideStandardButtons()
        self.baseHideProgressBar()


class CreateControllerLayout(QtWidgets.QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super(CreateControllerLayout, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.createConnections()

    def setupUi(self, parent):
        #layout
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setContentsMargins(-1, -1, -1, 9)
        self.gridLayout.setHorizontalSpacing(6)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setContentsMargins(-1, 4, -1, 0)
        self.horizontalLayout_4.setSpacing(6)

        #spacer
        spacerItem = QtWidgets.QSpacerItem(38, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)

        #create locator/group button
        self.create_loc_grp_btn = QtWidgets.QPushButton()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.create_loc_grp_btn.sizePolicy().hasHeightForWidth())
        self.create_loc_grp_btn.setSizePolicy(sizePolicy)
        self.horizontalLayout_4.addWidget(self.create_loc_grp_btn)

        #spacer
        spacerItem1 = QtWidgets.QSpacerItem(74, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem1)

        #create controller button
        self.create_cntrl_btn = QtWidgets.QPushButton()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.create_cntrl_btn.sizePolicy().hasHeightForWidth())
        self.create_cntrl_btn.setSizePolicy(sizePolicy)
        self.horizontalLayout_4.addWidget(self.create_cntrl_btn)

        #spacer
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem2)

        self.gridLayout.addLayout(self.horizontalLayout_4, 4, 0, 1, 1)        
        self.horizontalLayout = QtWidgets.QHBoxLayout()

        self.pivot_obj_label = QtWidgets.QLabel()
        self.horizontalLayout.addWidget(self.pivot_obj_label)
        self.pivot_obj_text = QtWidgets.QLineEdit()
        self.pivot_obj_text.setEnabled(False)
        self.horizontalLayout.addWidget(self.pivot_obj_text)

        #get pivot object button
        self.get_pivot_obj_btn = QtWidgets.QPushButton()
        self.horizontalLayout.addWidget(self.get_pivot_obj_btn)

        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self)
        self.horizontalLayout_3.setContentsMargins(-1, 9, -1, -1)

        self.formLayout = QtWidgets.QFormLayout(self)
        self.formLayout.setContentsMargins(-1, -1, 0, -1)

        self.type_label = QtWidgets.QLabel()
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.type_label)

        self.verticalLayout = QtWidgets.QVBoxLayout()

        #type:locator radio button
        self.locator_rdo_btn = QtWidgets.QRadioButton()
        self.locator_rdo_btn.setChecked(True)

        self.buttonGroup = QtWidgets.QButtonGroup()

        self.buttonGroup.addButton(self.locator_rdo_btn)
        self.verticalLayout.addWidget(self.locator_rdo_btn)

        #type:group radio button
        self.group_rdo_tbn = QtWidgets.QRadioButton()
        self.buttonGroup.addButton(self.group_rdo_tbn)
        self.verticalLayout.addWidget(self.group_rdo_tbn)

        self.formLayout.setLayout(0, QtWidgets.QFormLayout.FieldRole, self.verticalLayout)
        self.horizontalLayout_3.addLayout(self.formLayout)
        self.formLayout_2 = QtWidgets.QFormLayout(self)
        self.formLayout_2.setContentsMargins(-1, -1, 0, -1)
        self.formLayout_2.setHorizontalSpacing(6)

        self.bake_label = QtWidgets.QLabel()
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.bake_label)

        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setContentsMargins(-1, -1, 0, -1)

        #bake:full bake radio button
        self.fullbake_rdo_btn = QtWidgets.QRadioButton()
        self.fullbake_rdo_btn.setChecked(True)
        self.buttonGroup_2 = QtWidgets.QButtonGroup()
        self.buttonGroup_2.addButton(self.fullbake_rdo_btn)
        self.verticalLayout_2.addWidget(self.fullbake_rdo_btn)

        #bake:current frame radio button
        self.cur_frame_rdo_btn = QtWidgets.QRadioButton()
        self.buttonGroup_2.addButton(self.cur_frame_rdo_btn)
        self.verticalLayout_2.addWidget(self.cur_frame_rdo_btn)

        self.formLayout_2.setLayout(0, QtWidgets.QFormLayout.FieldRole, self.verticalLayout_2)
        self.horizontalLayout_3.addLayout(self.formLayout_2)

        self.formLayout_3 = QtWidgets.QFormLayout()

        self.space_label = QtWidgets.QLabel()
        self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.space_label)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()

        #space:world space radio button
        self.world_spc_rdo_btn = QtWidgets.QRadioButton()
        self.buttonGroup_3 = QtWidgets.QButtonGroup()
        self.buttonGroup_3.addButton(self.world_spc_rdo_btn)
        self.verticalLayout_3.addWidget(self.world_spc_rdo_btn)

        #space:object space radio button
        self.object_spc_rdo_btn = QtWidgets.QRadioButton()
        self.object_spc_rdo_btn.setChecked(True)
        self.buttonGroup_3.addButton(self.object_spc_rdo_btn)
        self.verticalLayout_3.addWidget(self.object_spc_rdo_btn)

        #space:screen space radio button
        self.screen_spc_rdo_btn = QtWidgets.QRadioButton()
        self.buttonGroup_3.addButton(self.screen_spc_rdo_btn)
        self.verticalLayout_3.addWidget(self.screen_spc_rdo_btn)

        self.formLayout_3.setLayout(0, QtWidgets.QFormLayout.FieldRole, self.verticalLayout_3)
        self.horizontalLayout_3.addLayout(self.formLayout_3)
        self.gridLayout.addLayout(self.horizontalLayout_3, 2, 0, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()

        """spacerItem3 = QtWidgets.QSpacerItem(26, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem3)"""

        self.obj_label = QtWidgets.QLabel()
        self.horizontalLayout_2.addWidget(self.obj_label)

        #object text field
        self.obj_text = QtWidgets.QLineEdit()
        self.obj_text.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(35)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.obj_text.sizePolicy().hasHeightForWidth())
        self.obj_text.setSizePolicy(sizePolicy)
        self.obj_text.setMinimumSize(QtCore.QSize(2, 0))
        self.horizontalLayout_2.addWidget(self.obj_text)

        spacerItem4 = QtWidgets.QSpacerItem(3, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem4)

        #get object button
        self.get_obj_btn = QtWidgets.QPushButton()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.get_obj_btn.sizePolicy().hasHeightForWidth())
        self.get_obj_btn.setSizePolicy(sizePolicy)
        self.get_obj_btn.setMinimumSize(QtCore.QSize(86, 0))
        self.get_obj_btn.setCheckable(False)
        self.horizontalLayout_2.addWidget(self.get_obj_btn)

        self.gridLayout.addLayout(self.horizontalLayout_2, 1, 0, 1, 1)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setContentsMargins(-1, 0, -1, 3)

        self.loc_grp_label = QtWidgets.QLabel()
        self.horizontalLayout_5.addWidget(self.loc_grp_label)

        #locator/group name text field
        self.loc_grp_text = QtWidgets.QLineEdit() 
        self.loc_grp_text.setFocusPolicy(QtCore.Qt.ClickFocus)               
        self.horizontalLayout_5.addWidget(self.loc_grp_text)

        self.gridLayout.addLayout(self.horizontalLayout_5, 3, 0, 1, 1)       
        
        #set widget labels
        self.create_loc_grp_btn.setText( "Create Locator/Group")
        self.create_cntrl_btn.setText( "Create Controller")
        self.pivot_obj_label.setText( "Pivot Object")
        self.get_pivot_obj_btn.setText( "Get Pivot object")
        self.type_label.setText( "    Type:")
        self.locator_rdo_btn.setText( "Locator")
        self.group_rdo_tbn.setText( "Group")
        self.bake_label.setText( " Bake:")
        self.fullbake_rdo_btn.setText( "Full Bake")
        self.cur_frame_rdo_btn.setText( "Current Frame")
        self.space_label.setText( "   Space:")
        self.world_spc_rdo_btn.setText( "World Space")
        self.object_spc_rdo_btn.setText( "Object Space")
        self.screen_spc_rdo_btn.setText( "Screen Space")
        self.obj_label.setText("Main Object")
        self.get_obj_btn.setText( "Get Main object")
        self.loc_grp_label.setText( "Locator/Group name")

    #create connections
    def createConnections(self):
        self.create_loc_grp_btn.clicked.connect(self.createLocator_GroupBtn)
        self.get_pivot_obj_btn.clicked.connect(self.getPivotObjectBtn)
        self.get_obj_btn.clicked.connect(self.getObjectBtn)
        self.create_cntrl_btn.clicked.connect(self.createControllerBtn)

    #get pivot object
    def getPivotObjectBtn(self):
        sel = cmds.ls(sl=True)
        if sel != None and len(sel) == 1:
            self.pivot_obj_text.setText(str(sel[0]))
            self.create_loc_grp_btn.setEnabled(True)
        else:
            LOG.warn("Error, exactly one object must be selected.")
            self.pivot_obj_text.clear()


    #get main object
    def getObjectBtn(self):
        sel = cmds.ls(selection=True, transforms=True)
        if sel:
            if len(sel) == 1:
                self.obj_text.setText(str(sel[0]))
                self.create_loc_grp_btn.setEnabled(True)
            else:
                LOG.warn("Error, exactly one object must be selected.")
                self.obj_text.clear()
        else:
            LOG.warn("Error, please select Transform node type object")


    def createLocator_Group(self):
        if self.locator_rdo_btn.isChecked():
            if self.loc_grp_text.text() != "":
                new_name = str(self.loc_grp_text.text())
            else:
                new_name = "locator"             
            cmds.select(clear=True)
            self.loc_grp_id = cmds.spaceLocator(n=new_name)
        if self.group_rdo_tbn.isChecked():
            cmds.select(clear=True)
            if self.loc_grp_text.text() != "":
                new_name = str(self.loc_grp_text.text())
            else:
                new_name = "null"             
            self.loc_grp_id = cmds.group(empty=True,n=new_name)
        return self.loc_grp_id


    #create new locator/group and constrain it to object
    def createLocator_GroupBtn(self):
        cmds.select(clear=True)
        #get pivot object & object ids
        self.pivot_object = self.pivot_obj_text.text()
        self.object = self.obj_text.text()                    
        #check both pivotobject & object are picked already
        if self.pivot_obj_text.text() != "" and self.obj_text.text() != "":
            # Check if object has existing point constraint already.
            has_constraints = transform_has_constraints(self.object)
            if has_constraints is True:
                LOG.warn("Selected object already has constraints: %r.", self.object)
                return 
            #else:            
            #create locator/group
            self.createLocator_Group()
            #copy pivot object's positions in world space to locator/group
            cmds.xform(self.loc_grp_id, ws=True, t=(cmds.xform(self.pivot_object, q=True, ws=True, t=True)))
            #copy object's rotations in world space to locator/group
            cmds.xform(self.loc_grp_id, ws=True, ro=(cmds.xform(self.object, q=True, ws=True, ro=True)))
            cmds.filterCurve(self.loc_grp_id)
        else:
            LOG.warn("Error, please first get both Pivot object & Main object.")

    #skip attributes
    def skipAttributes(self, parent):
        attr_list = [["x","y","z"],["x","y","z"]]
        if cmds.getAttr(parent+".translateX", k=True) and cmds.getAttr(parent+".translateX", se=True):
            attr_list[0].remove("x")
        if cmds.getAttr(parent+".translateY", k=True) and cmds.getAttr(parent+".translateY", se=True):
            attr_list[0].remove("y")
        if cmds.getAttr(parent+".translateZ", k=True) and cmds.getAttr(parent+".translateZ", se=True):
            attr_list[0].remove("z")
        if cmds.getAttr(parent+".rotateX", k=True) and cmds.getAttr(parent+".rotateX", se=True):
            attr_list[1].remove("x")
        if cmds.getAttr(parent+".rotateY", k=True) and cmds.getAttr(parent+".rotateY", se=True):
            attr_list[1].remove("y")
        if cmds.getAttr(parent+".rotateZ", k=True) and cmds.getAttr(parent+".rotateZ", se=True):
            attr_list[1].remove("z")
        return attr_list

    #bake animation
    def bakeAnimation(self, parent, child):
        #get pivot object & object ids
        self.pivot_object = self.pivot_obj_text.text()
        self.object = self.obj_text.text()
        start_frame = cmds.playbackOptions(q=True, min=True)
        end_frame = cmds.playbackOptions(q=True, max=True)
        #parent = self.object, child = self.loc_grp_id      
        if self.fullbake_rdo_btn.isChecked():
            parent_con = cmds.parentConstraint(parent, child, mo=True)
            cmds.bakeResults(child, t=(start_frame,end_frame), sm=True) 
            cmds.delete(parent_con)
        if self.cur_frame_rdo_btn.isChecked():
            current_time = cmds.currentTime(q=True)
            parent_con = cmds.parentConstraint(parent, child, mo=True)
            cmds.delete(parent_con)
            cmds.setKeyframe(child)

    def getViewportCamera(self):
        """Get the Camera transform node in the active viewport."""
        model_editor = viewport_utils.get_active_model_editor()
        if model_editor is None:
            return None
        cam_tfm, cam_shp = viewport_utils.get_viewport_camera(model_editor)
        return cam_tfm          

    #create controller
    def createControllerBtn(self):
        #check both pivotobject & object are picked already
        if self.pivot_obj_text.text() != "" and self.obj_text.text() != "": 
            attr = self.skipAttributes(self.object)
            skip_translate_attr = attr[0]
            skip_rotate_attr = attr[1]
            start_frame = cmds.playbackOptions(q=True, min=True)
            end_frame = cmds.playbackOptions(q=True, max=True)
            if self.cur_frame_rdo_btn.isChecked():
                start_frame = cmds.currentTime(q=True) 
                end_frame = cmds.currentTime(q=True) + 1
            ctx = tools_utils.tool_context(
                use_undo_chunk=True,
                restore_current_frame=True,
                use_dg_evaluation_mode=True,
                disable_viewport=True)
            with ctx:
                # Check if object has existing point constraint already.
                has_constraints = transform_has_constraints(self.object)
                if has_constraints is True:
                    LOG.warn("Selected object already has constraints: %r.", self.object)
                    return                        
                #else:
                if self.world_spc_rdo_btn.isChecked():
                    #bake locator/group animation first
                    self.bakeAnimation(self.object, self.loc_grp_id)
                    #parent contraint, child = self.object, parent = self.loc_grp_id
                    cmds.parentConstraint(self.loc_grp_id, self.object, mo=True, st=skip_translate_attr, sr=skip_rotate_attr)
                    LOG.warn("Create Controller: SUCCESS")

                if self.object_spc_rdo_btn.isChecked():                
                    #bake locator/group animation first
                    self.bakeAnimation(self.object, self.loc_grp_id)                    
                    parent = cmds.ls(self.loc_grp_id)
                    #turn off LOD visibility
                    shape = cmds.listRelatives(parent, shapes=True)
                    cmds.setAttr(shape[0]+".lodVisibility",0)
                    #object space zero locator/group
                    self.createLocator_Group()
                    child = cmds.rename(str(parent[0])+"_"+"objectSpaceZero")
                    cmds.parent(child, parent,relative=True)
                    cmds.parentConstraint(child, self.object, mo=True, st=skip_translate_attr, sr=skip_rotate_attr)
                    LOG.warn("Create Controller: SUCCESS")

                if self.screen_spc_rdo_btn.isChecked():
                    if len(skip_translate_attr) == 0:
                        vp_camera = self.getViewportCamera()
                        #bake locator/group animation first
                        self.bakeAnimation(self.object, self.loc_grp_id)                        
                        parent = cmds.ls(self.loc_grp_id)
                        #turn off LOD visibility
                        shape = cmds.listRelatives(parent, shapes=True)
                        cmds.setAttr(shape[0]+".lodVisibility",0)                            
                        self.createLocator_Group()
                        child = cmds.rename(str(parent[0])+"_"+"screenSpace")
                        #turn off LOD visibility
                        shape = cmds.listRelatives(child, shapes=True)
                        cmds.setAttr(shape[0]+".lodVisibility",0)                            
                        cmds.parent(child, parent,relative=True)
                        if not self.cur_frame_rdo_btn.isChecked():
                            cmds.bakeResults(child, t=(start_frame, end_frame), sm=True) 
                        #aim constraint
                        aim_con = cmds.aimConstraint(vp_camera, child, mo=False)
                        if not self.cur_frame_rdo_btn.isChecked():
                            cmds.bakeResults(child, t=(start_frame, end_frame), sm=True)
                        cmds.delete(aim_con)
                        cmds.filterCurve(child)
                        #screen space zero locator/group
                        parent = child
                        self.createLocator_Group()
                        child = cmds.rename(str(parent)+"Zero")
                        cmds.parent(child, parent,relative=True)
                        cmds.pointConstraint(child, self.object, mo=True)
                        LOG.warn("Create Controller: SUCCESS")                   
                    else:
                        LOG.warn("Error, Main object all translation attributes(tx,ty,tz) are not available.")
                        #delete existing locator/group
                        cmds.delete(self.loc_grp_id)
        return 


def main(show=True, auto_raise=True, delete=False):
    """
    Open the Channel Sensitivity UI window.

    :param show: Show the UI.
    :type show: bool

    :param auto_raise: If the UI is open, raise it to the front?
    :type auto_raise: bool

    :param delete: Delete the existing UI and rebuild it? Helpful when
                   developing the UI in Maya script editor.
    :type delete: bool

    :returns: A new solver window, or None if the window cannot be
              opened.
    :rtype: SolverWindow or None.
    """
    win = CreateControllerWindow.open_window(
        show=show,
        auto_raise=auto_raise,
        delete=delete)
    return win