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

RIG_SUFFIX_NAME = "_screenSpaceRig"
FREEZE_RIG_SUFFIX_NAME = "_freezeRig"
FREEZE_RIG_ANIM_LAYER = "_freezeRigLayer"
ATTRIBUTE_IDENTIFIER_NAME = "screenzrigidentifier"
ATTRIBUTE_IDENTIFIER_NICE_NAME = "ScreenZRigIdentifier"
SCREEN_Z_DEPTH_ATTR_NAME = "screenzdepth"
TRANSFORM_ATTR_LIST = ["tx", "ty", "tz",
                       "rx", "ry", "rz",
                       "sx", "sy", "sz"]


def transform_has_constraints(tfm_node):
    constraints = cmds.listRelatives(
        tfm_node, children=True, type="pointConstraint") or []
    constraints += cmds.listRelatives(
        tfm_node, children=True, type="parentConstraint") or []
    has_constraints = len(constraints) > 0
    return has_constraints


def _display_warning_ui(msg):
    assert isinstance(msg, basestring)
    msg = "warning, " + msg
    cmds.confirmDialog(
        title="Warning",
        message=msg)
    return


def setZDepthKeyframes(node,
                          start_frame, end_frame,
                          values,
                          anim_layer_name=None):    
    kwargs = {}
    if anim_layer_name is not None:
        kwargs = {'animLayer': anim_layer_name}
    
    frames = range(start_frame, end_frame+1)
    for i, frame in enumerate(frames):
        oma.MAnimControl.setCurrentTime(om.MTime(frame))
        cmds.setKeyframe(
            node,
            attribute=(SCREEN_Z_DEPTH_ATTR_NAME),
            value=values[i],
            **kwargs)
    return


class ScreenSpaceRigWindow(BaseWindow):

    def __init__(self, parent=None, name=None):
        super(ScreenSpaceRigWindow, self).__init__(parent,
                                                   name=name)
        self.setWindowTitle("Screen Space Rig Bake")
        self.setMinimumWidth(240)
        self.setMinimumHeight(380)
        self.setWindowFlags(QtCore.Qt.Tool)

        self.addSubForm(ScreenSpaceRigLayout)

        # Hide irrelevant stuff
        self.baseHideMenuBar()
        self.baseHideStandardButtons()
        self.baseHideProgressBar()


class ScreenSpaceRigLayout(QtWidgets.QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super(ScreenSpaceRigLayout, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.createConnections()
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

        self.refreshRigsList()

    def setupUi(self, parent):
        self.transform_icon = QtGui.QIcon(":transform.svg")

        # main layout
        self.gridLayout = QtWidgets.QGridLayout(parent)

        # menu bar
        self.menu_bar = QtWidgets.QMenuBar()

        # menus
        self.options_menu = self.menu_bar.addMenu("Freeze")
        self.refresh_menu = self.menu_bar.addMenu("Refresh")

        # freeze options actions
        self.animlayer_action = QtWidgets.QAction("Add to AnimLayer", self)
        self.animlayer_action.setCheckable(True)
        self.options_menu.addAction(self.animlayer_action)

        self.options_menu.addSeparator()

        self.freeze_action_group = QtWidgets.QActionGroup(self)

        self.camera_space_action = QtWidgets.QAction("Freeze in Camera Space", self)
        self.camera_space_action.setCheckable(True)
        self.options_menu.addAction(self.camera_space_action)
        self.camera_space_action.setActionGroup(self.freeze_action_group)

        self.world_space_action = QtWidgets.QAction("Freeze in World Space", self)
        self.world_space_action.setCheckable(True)
        self.world_space_action.setChecked(True)
        self.options_menu.addAction(self.world_space_action)
        self.world_space_action.setActionGroup(self.freeze_action_group)

        #refresh action
        self.refresh_action = QtWidgets.QAction("Refresh Rigs list", self)
        self.refresh_menu.addAction(self.refresh_action)

        self.gridLayout.setMenuBar(self.menu_bar)

        spacerItem = QtWidgets.QSpacerItem(
            5, 17,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 0, 1, 1)

        #full bake radio button
        self.full_bake_rdo_btn = QtWidgets.QRadioButton()
        self.gridLayout.addWidget(self.full_bake_rdo_btn, 0, 1, 1, 1)

        spacerItem1 = QtWidgets.QSpacerItem(
            5, 17,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 2, 1, 1)

        #smart bake radio button
        self.smart_bake_rdo_btn = QtWidgets.QRadioButton()
        self.smart_bake_rdo_btn.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.smart_bake_rdo_btn.setAutoFillBackground(False)
        self.smart_bake_rdo_btn.setChecked(True)
        self.gridLayout.addWidget(self.smart_bake_rdo_btn, 0, 3, 1, 1)

        spacerItem2 = QtWidgets.QSpacerItem(
            5, 10,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 0, 4, 1, 1)

        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()

        #rigs label
        self.rigs_label = QtWidgets.QLabel()
        self.horizontalLayout_2.addWidget(self.rigs_label)

        #rigs list
        self.rigs_list = QtWidgets.QTreeWidget()
        self.rigs_list.setFocusPolicy(QtCore.Qt.NoFocus)
        self.rigs_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.rigs_list.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.rigs_list.setIndentation(15)
        self.rigs_list.setHeaderHidden(True)
        self.horizontalLayout_2.addWidget(self.rigs_list)
        self.gridLayout.addLayout(self.horizontalLayout_2, 2, 0, 1, 5)

        self.horizontalLayout = QtWidgets.QHBoxLayout()

        #name label
        self.name_label = QtWidgets.QLabel()
        self.horizontalLayout.addWidget(self.name_label)

        #name line edit
        self.name_text = QtWidgets.QLineEdit()
        self.name_text.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.horizontalLayout.addWidget(self.name_text)

        self.gridLayout.addLayout(self.horizontalLayout, 3, 0, 1, 5)

        #widget labels
        self.full_bake_rdo_btn.setText("Full bake")
        self.smart_bake_rdo_btn.setText("Smart bake")
        self.rigs_label.setText("Rigs")
        self.name_label.setText("Name")

        self.context_menu = QtWidgets.QMenu()

        self.create_rig_action = QtWidgets.QAction("Create Screen Space Rig", self)
        self.context_menu.addAction(self.create_rig_action)

        self.create_freeze_rig_action = QtWidgets.QAction("Create Freeze Rig", self)
        self.context_menu.addAction(self.create_freeze_rig_action)

        self.context_menu.addSeparator()

        self.match_rig_action = QtWidgets.QAction("Match Screen Z Depth", self)
        self.context_menu.addAction(self.match_rig_action)

        self.context_menu.addSeparator()

        self.bake_rig_action = QtWidgets.QAction("Bake Rig", self)
        self.context_menu.addAction(self.bake_rig_action)

        self.delete_rig_action = QtWidgets.QAction("Delete Rig", self)
        self.context_menu.addAction(self.delete_rig_action)

        return

    def createConnections(self):
        self.create_rig_action.triggered.connect(self.createRigBtn)
        self.match_rig_action.triggered.connect(self.Match)
        self.create_freeze_rig_action.triggered.connect(self.createFreezeRigBtn)
        self.bake_rig_action.triggered.connect(self.bakeRigBtn)
        self.delete_rig_action.triggered.connect(self.deleteRigBtn)
        self.refresh_action.triggered.connect(self.refreshRigsList)
        self.animlayer_action.triggered.connect(self.freezeOptionsUpdate)
        self.world_space_action.triggered.connect(self.freezeOptionsUpdate)
        self.camera_space_action.triggered.connect(self.freezeOptionsUpdate)
        self.name_text.editingFinished.connect(self.clearFocus)

    def showContextMenu(self, point):
        self.context_menu.exec_(self.mapToGlobal(point))

    def refreshRigsList(self):
        self.rigs_list.clear()
        mItDag = om.MItDag(om.MItDag.kDepthFirst, om.MFn.kTransform)
        while not mItDag.isDone():
            depNode = om.MFnDependencyNode(mItDag.currentItem())
            if depNode.hasAttribute(ATTRIBUTE_IDENTIFIER_NAME):
                name = depNode.name()
                item = self.createItem(name)
                self.rigs_list.addTopLevelItem(item)
                mItDag.prune()
            mItDag.next()

        top_level_item_count = self.rigs_list.topLevelItemCount()
        for i in range(top_level_item_count+1):
            top_level_item = self.rigs_list.topLevelItem(i)
            self.rigs_list.setItemExpanded(top_level_item, True)

    def createItem(self, name):
        item = QtWidgets.QTreeWidgetItem([name])
        self.addChildren(item)
        item.setIcon(0, self.transform_icon)
        return item

    def addChildren(self, item):
        children = cmds.listRelatives(item.text(0), c=True) or []
        for child in children:
            if ATTRIBUTE_IDENTIFIER_NAME in cmds.listAttr(child):
                child_item = self.createItem(child)
                item.addChild(child_item)

    def freezeOptionsUpdate(self):
        if self.world_space_action.isChecked():
            self.animlayer_action.setEnabled(True)
        else:
            self.animlayer_action.setEnabled(False)
            self.animlayer_action.setChecked(False)

    def clearFocus(self):
        self.name_text.clearFocus()

    def bakeOptions(self):
        bake_options = None
        if self.full_bake_rdo_btn.isChecked():
            bake_options = "full_bake"
        else:
            bake_options = "smart_bake"
        return bake_options

    def getViewportCamera(self):
        """Get the Camera transform node in the active viewport."""
        model_editor = viewport_utils.get_active_model_editor()
        if model_editor is None:
            return None
        cam_tfm, cam_shp = viewport_utils.get_viewport_camera(model_editor)
        return cam_tfm

    def getPreBakeFramesListFromNode(self, node):
        frames_list = []
        start_frame, end_frame = time_utils.get_maya_timeline_range_inner()
        keys_list = cmds.keyframe(node, q=True, time=(start_frame, end_frame))
        if keys_list == None:
            frames_list = [start_frame, end_frame]
        bake_options = self.bakeOptions()
        if bake_options == "full_bake":
            for frame in range(start_frame, end_frame + 1):
                if frame not in frames_list:
                    frames_list.append(frame)
        if bake_options == "smart_bake":
            keys_list = cmds.keyframe(node, q=True, time=(start_frame, end_frame)) or []
            for frame in keys_list:
                 if frame not in frames_list:
                    frames_list.append(frame)
        return sorted(frames_list)

    def offsetVector(self, a, b):
        assert isinstance(a, basestring)
        assert isinstance(b, basestring)
        assert cmds.objExists(a) and cmds.objExists(b)
        a_pos = cmds.xform(a, q=True, ws=True, t=True)
        b_pos = cmds.xform(b, q=True, ws=True, t=True)
        a_vector = om.MVector(a_pos[0], a_pos[1], a_pos[2])
        b_vector = om.MVector(b_pos[0], b_pos[1], b_pos[2])
        length = (b_vector - a_vector).length()
        return length

    def calcDistance(self, cam_tfm, tfm_node, offset):
        """
        Calculate the distance between cam_tfm and tfm_node.

        .. note::
           'offset' is not yet used, but may be implemented in future.
        """
        depth_list = []
        frames_list = self.getPreBakeFramesListFromNode(tfm_node)
        if len(frames_list) > 0:
            current_time = cmds.currentTime(query=True)
            for frame in frames_list:
                oma.MAnimControl.setCurrentTime(om.MTime(float(frame)))
                vector = self.offsetVector(cam_tfm, tfm_node)
                depth_list.append(vector + offset)
            oma.MAnimControl.setCurrentTime(om.MTime(float(current_time)))
        return depth_list

    def createRig(self, camera, object, dlist, name, rigName):
        start_frame, end_frame = time_utils.get_maya_timeline_range_inner()
        
        # Create main group
        main_grp = cmds.group(empty=True, n=name + rigName)
        # Delete all transform attributes
        attr_list = TRANSFORM_ATTR_LIST + ["visibility"]
        for attr in attr_list:
            cmds.setAttr(main_grp+"."+attr, k=0, l=1)

        # Add custom attributes
        cmds.addAttr(main_grp, ln="screenx", nn="Screen X", at="float", k=True)
        cmds.addAttr(main_grp, ln="screeny", nn="Screen Y", at="float", k=True)
        cmds.addAttr(main_grp, ln="screenzdepth", nn="Screen Z depth", at="float", k=True)
        cmds.addAttr(main_grp, ln=ATTRIBUTE_IDENTIFIER_NAME, nn=ATTRIBUTE_IDENTIFIER_NICE_NAME, dt="string", k=False)
        cmds.setAttr(main_grp+"."+ATTRIBUTE_IDENTIFIER_NAME, str(object), type="string")

        # Set keyframes on screezdepth attribute
        frames_list = self.getPreBakeFramesListFromNode(object)            
        for i, frame in enumerate(frames_list):
            cmds.setKeyframe(main_grp, at="screenzdepth", t=frame, v=dlist[i])

        # Clear name text
        self.name_text.clear()
        self.name_text.clearFocus()

        # Create screez master group
        screenz_master_grp = cmds.group(em=True, n=name + "_screenZMaster")
        cmds.setAttr(screenz_master_grp+".visibility", 0)
        # Add screen x,y copy attributes
        cmds.addAttr(screenz_master_grp, ln="screenxcopy", nn="Screen X copy", at="float")
        cmds.addAttr(screenz_master_grp, ln="screenycopy", nn="Screen Y copy", at="float")
        cmds.setAttr(screenz_master_grp+".screenxcopy", cb=False)
        cmds.setAttr(screenz_master_grp+".screenycopy", cb=False)

        cmds.parent(screenz_master_grp, main_grp)
        con = cmds.parentConstraint(self.getViewportCamera(), screenz_master_grp)
        cmds.bakeResults(screenz_master_grp, t=(start_frame, end_frame), sm=True)
        cmds.delete(con)

        # Create screenz depth connections
        cmds.connectAttr(main_grp+".screenzdepth", screenz_master_grp+".scaleX", f=True)
        cmds.connectAttr(main_grp+".screenzdepth", screenz_master_grp+".scaleY", f=True)
        cmds.connectAttr(main_grp+".screenzdepth", screenz_master_grp+".scaleZ", f=True)

        # Create screen xy master group
        screen_xy_master_grp = cmds.group(em=True, n=name + "_screenXYMaster")
        cmds.setAttr(screen_xy_master_grp+".visibility", 0)
        attr_list = ["rx", "ry", "rz", "sx","sy","sz","visibility"]
        for attr in attr_list:
            cmds.setAttr(screen_xy_master_grp+"."+attr, k=0, l=1)
        cmds.parent(screen_xy_master_grp, screenz_master_grp, r=True)
        con = cmds.pointConstraint(object, screen_xy_master_grp)
        cmds.bakeResults(screen_xy_master_grp, t=(start_frame, end_frame), sm=True)
        cmds.delete(con)
        cmds.setAttr(screen_xy_master_grp+".translateZ", l=1)

        # Create screenxy connections
        cmds.connectAttr(screen_xy_master_grp+".translateX", main_grp+".screenx", f=True)
        cmds.connectAttr(screen_xy_master_grp+".translateY", main_grp+".screeny", f=True)
        cmds.connectAttr(screen_xy_master_grp+".translateX", screenz_master_grp+".screenxcopy", f=True)
        cmds.connectAttr(screen_xy_master_grp+".translateY", screenz_master_grp+".screenycopy", f=True)
        cmds.bakeResults(main_grp, at=["screenx","screeny"], t=(start_frame, end_frame), sm=True)
        cmds.bakeResults(screenz_master_grp, at=["screenxcopy","screenycopy"], t=(start_frame, end_frame), sm=True)
        cmds.connectAttr(main_grp+".screenx", screen_xy_master_grp+".translateX", f=True)
        cmds.connectAttr(main_grp+".screeny", screen_xy_master_grp+".translateY", f=True)

        # Create condition node network
        screenx_condition_node = cmds.shadingNode("condition", au=True, n=name+"_screenx_condition")
        screeny_condition_node = cmds.shadingNode("condition", au=True, n=name+"_screeny_condition")

        cmds.connectAttr(main_grp+".screenx", screenx_condition_node+".firstTerm", f=True)
        cmds.connectAttr(screenz_master_grp+".screenxcopy", screenx_condition_node+".secondTerm", f=True)
        cmds.connectAttr(main_grp+".screeny", screeny_condition_node+".firstTerm", f=True)
        cmds.connectAttr(screenz_master_grp+".screenycopy", screeny_condition_node+".secondTerm", f=True)

        attr_list = TRANSFORM_ATTR_LIST + ["visibility"]
        for attr in attr_list:
            cmds.setAttr(screenz_master_grp+"."+attr, l=1)

        cmds.pointConstraint(screen_xy_master_grp, object)
        # Clear selection in the end
        cmds.select(cl=True)
        self.refreshRigsList()

    def checkNameExists(self, rigName, name, rigs_list):
        valid_name_list = False
        same_name_used = False
        sel = cmds.ls(transforms=True, os=True) or []
        if len(sel) == 0:
            _display_warning_ui(
                "atleast one Transform "
                "node type object must be selected.")
            return valid_name_list, same_name_used

        if len(name) == 0:
            _display_warning_ui("please type name first.")
            return valid_name_list, same_name_used

        names = name.split(",")
        if len(names) != len(sel):
            _display_warning_ui("selection and name count not matching.")
            return valid_name_list, same_name_used

        valid_name_list = True
        for name_item in names:
            #check if name already exists
            iterator = QtWidgets.QTreeWidgetItemIterator(rigs_list)
            while iterator.value():
                item = iterator.value()
                item_name = item.text(0)
                item_name = item_name.replace(rigName, "")
                if item_name == name_item:
                    same_name_used = True
                iterator += 1

        if same_name_used == True:
            _display_warning_ui("same name exists already "
                                "please type different name.")
        return valid_name_list, same_name_used

    def createRigBtn(self):
        name = self.name_text.text()
        rigs_list = self.rigs_list
        cam_tfm = self.getViewportCamera()
        if cam_tfm is None:
            _display_warning_ui("Please select a viewport.")
            return
        sel = cmds.ls(transforms=True, os=True)
        check_name = self.checkNameExists(RIG_SUFFIX_NAME,  name, rigs_list)
        valid_name_list, same_name_used = check_name

        names = name.split(",")
        if valid_name_list is False or same_name_used is True:
            return
        assert len(names) == len(sel)

        node_screen_depths = []
        for sel_item, name_item in zip(sel, names):
            #check if object has existing point constraint already
            has_constraints = transform_has_constraints(sel_item)
            if has_constraints == False:
                depth_list = self.calcDistance(cam_tfm, sel_item, 0)
                node_screen_depths.append((sel_item, name_item, depth_list))
            else:
                _display_warning_ui(
                    "selected object(s) already have constraints.")
                return

        ctx = tools_utils.tool_context(
            use_undo_chunk=True,
            restore_current_frame=True,
            use_dg_evaluation_mode=True,
            disable_viewport=True)
        with ctx:
            for sel_item, name_item, depth_list in node_screen_depths:
                self.createRig(
                    cam_tfm, sel_item,
                    depth_list,
                    name_item,
                    RIG_SUFFIX_NAME)
        return

    def createFreezeRigBtn(self):
        name_text = self.name_text.text()
        rigs_list = self.rigs_list
        cam_tfm = self.getViewportCamera()
        if cam_tfm is None:
            _display_warning_ui("Please select a viewport.")
            return
        
        check_name = self.checkNameExists(FREEZE_RIG_SUFFIX_NAME, name_text, rigs_list)
        valid_name_list, same_name_used = check_name

        if valid_name_list is not True or same_name_used is not False:
            _display_warning_ui("Invalid freeze rig name.")
            return

        do_camera_space = self.camera_space_action.isChecked()
        do_world_space = self.world_space_action.isChecked()
        use_anim_layer = self.animlayer_action.isChecked()

        # When making a freeze rig we always assume the full frame
        # range will be baked - NO smart bake.
        LOG.warn("Force full bake for Freeze Rig.")
        self.full_bake_rdo_btn.setChecked(True)

        start_frame, end_frame = time_utils.get_maya_timeline_range_inner()
        sel = cmds.ls(orderedSelection=True, transforms=True) or []
        names = name_text.split(",")

        ctx = tools_utils.tool_context(
            use_undo_chunk=True,
            restore_current_frame=True,
            use_dg_evaluation_mode=True,
            disable_viewport=True)
        with ctx:

            for sel_item, name_item in zip(sel, names):
                freeze_rig_name = name_item + FREEZE_RIG_SUFFIX_NAME
                animLayerName = name_item + FREEZE_RIG_ANIM_LAYER

                # Check if object has existing point constraint already.
                has_constraints = transform_has_constraints(sel_item)
                if has_constraints is True:
                    LOG.warn(
                        "Selected object(s) already have constraints: %r.",
                        sel_item)
                    continue

                # Get the selected item's depth, if we don't have
                # anything, we cannot continue.
                dlist = self.calcDistance(cam_tfm, sel_item, 0)
                if len(dlist) == 0:
                    continue

                if do_camera_space:
                    # Camera space bake
                    self.createRig(
                        cam_tfm, sel_item, dlist, name_item,
                        FREEZE_RIG_SUFFIX_NAME)
                    cmds.cutKey(
                        name_item + FREEZE_RIG_SUFFIX_NAME, clear=True,
                        at=SCREEN_Z_DEPTH_ATTR_NAME)
                else:
                    # World space bake
                    
                    # Create a static temp group
                    temp_grp = cmds.group(empty=True)
                    con = cmds.parentConstraint(
                        sel_item, temp_grp,
                        maintainOffset=False)
                    cmds.delete(con)
                    cmds.bakeResults(
                        temp_grp,
                        time=(start_frame, end_frame),
                        simulation=True)
                    self.createRig(
                        cam_tfm, sel_item, dlist, name_item,
                        FREEZE_RIG_SUFFIX_NAME)
                    
                    # Calc full freeze list
                    dlist = self.calcDistance(cam_tfm, temp_grp, 0)
                    if use_anim_layer == False:
                        # Set keyframes on screenzdepth attribute,
                        # with no anim layer.
                        setZDepthKeyframes(
                            freeze_rig_name,
                            start_frame, end_frame, dlist)
                    else:
                        # Make the anim layer, and add our freeze rig
                        # node to the layer.
                        cmds.select(freeze_rig_name, replace=True)
                        cmds.animLayer(
                            animLayerName,
                            addSelectedObjects=True)
                        cmds.select(clear=True)

                        setZDepthKeyframes(
                            freeze_rig_name,
                            start_frame, end_frame, dlist,
                            anim_layer_name=animLayerName)

                    # Delete temp group
                    cmds.delete(temp_grp)
        return
                    
    def bakeRigBtn(self):
        bake_options = self.bakeOptions()
        selected_items = self.rigs_list.selectedItems()
        start_frame, end_frame = time_utils.get_maya_timeline_range_inner()
        if len(selected_items) == 0:
            _display_warning_ui("at least one rig must be selected from Rigs list.")
            return

        ctx = tools_utils.tool_context(
            use_undo_chunk=True,
            restore_current_frame=True,
            use_dg_evaluation_mode=True,
            disable_viewport=True)
        with ctx:
            cmds.select(clear=True)
            for sel_item in selected_items:
                children = self.getAllChildren(sel_item)
                for j in children:
                    rigName = j.text(0)
                    object = cmds.getAttr(rigName+"."+ATTRIBUTE_IDENTIFIER_NAME)
                    if FREEZE_RIG_SUFFIX_NAME in rigName:
                        self.full_bake_rdo_btn.setChecked(True)

                    if RIG_SUFFIX_NAME in rigName:
                        name = rigName.split(RIG_SUFFIX_NAME)[0]
                    if FREEZE_RIG_SUFFIX_NAME in rigName:
                        name = rigName.split(FREEZE_RIG_SUFFIX_NAME )[0]

                    if bake_options == "full_bake":
                        cmds.bakeResults(
                            object,
                            time=(start_frame, end_frame),
                            simulation=True)
                    if bake_options == "smart_bake":
                        nodes_list = cmds.listConnections(name+"_screenZMaster")
                        for node in nodes_list:
                            if "screenx_condition" in node:
                                x_node = node
                            if "screeny_condition" in node:
                                y_node = node

                        cmds.select(object)
                        attrs = ["tx", "ty", "tz"]
                        # First key on objects existing key frames
                        for frame in self.getPreBakeFramesListFromNode(object):
                            oma.MAnimControl.setCurrentTime(om.MTime(frame))
                            cmds.setKeyframe(attribute=attrs)

                        # Key screen z depth attribute frames
                        keys_list = cmds.keyframe(rigName+".screenzdepth",query=True)
                        if keys_list:
                            for frame in keys_list:
                                oma.MAnimControl.setCurrentTime(om.MTime(frame))
                                cmds.setKeyframe(attribute=attrs)

                        # Check condition result node and set keyframe
                        for i in range(start_frame, end_frame+1):
                            oma.MAnimControl.setCurrentTime(om.MTime(i))
                            x_changed = cmds.getAttr(x_node+".outColor")[0][0]
                            y_changed = cmds.getAttr(y_node+".outColor")[0][0]
                            if x_changed or y_changed:
                                cmds.setKeyframe(attribute=attrs)
                        cmds.select(clear=True)

            self.deleteRigBtn()
            self.refreshRigsList()
        return

    def getAllChildren(self, tree_widget_item):
        nodes = [tree_widget_item]
        for i in range(tree_widget_item.childCount()):
            nodes.extend(self.getAllChildren(tree_widget_item.child(i)))
        return nodes

    def deleteRigBtn(self):
        selected_items = self.rigs_list.selectedItems()
        if len(selected_items) == 0:
            _display_warning_ui("at least one rig must be selected from Rigs list.")
            return

        nodes_to_delete = []
        for sel_item in selected_items:
            children = self.getAllChildren(sel_item)
            for j in children:
                rigName = j.text(0)
                if RIG_SUFFIX_NAME in rigName:
                    name = rigName.split(RIG_SUFFIX_NAME)[0]
                elif FREEZE_RIG_SUFFIX_NAME in rigName:
                    name = rigName.split(FREEZE_RIG_SUFFIX_NAME)[0]
                else:
                    LOG.warn("No valid rig name: %r", rigName)
                    continue
                nodes_to_delete.append(rigName)
                nodes_to_delete.append(name + "_screenZMaster")
                nodes_to_delete.append(name + "_screenXYMaster")

                nodes_list = cmds.listConnections(name + "_screenZMaster")
                for node in nodes_list:
                    if "screenx_condition" in node:
                        nodes_to_delete.append(node)
                    if "screeny_condition" in node:
                        nodes_to_delete.append(node)

                animLayer = rigName + "Layer"
                if cmds.animLayer(animLayer, query=True, exists=True):
                    nodes_to_delete.append(animLayer)

        # Delete selected nodes
        nodes_to_delete = [n for n in nodes_to_delete if cmds.objExists(n)]
        cmds.delete(nodes_to_delete)
        self.refreshRigsList()
        return

    def lockUnlockAttributes(self, tfm_node, lock=True):
        attr_list = TRANSFORM_ATTR_LIST
        for attr in attr_list:
            cmds.setAttr(tfm_node + "." + attr, lock=lock)

    def Match(self):
        selected_items = self.rigs_list.selectedItems()
        if len(selected_items) < 2:
            _display_warning_ui("at least two rigs must"
                                " be selected from Rigs list.")
            return

        # Get parent
        selected_parent = selected_items[0]
        parent_main = selected_parent.text(0)
        parent_base_name = parent_main.split("_screenSpaceRig")[0]
        parent = parent_base_name + "_screenZMaster"

        try:
            self.lockUnlockAttributes(parent, lock=False)

            selected_children = selected_items[1:]
            for selected_child in selected_children:
                child_main = selected_child.text(0)

                child_base_name = child_main.split("_screenSpaceRig")[0]
                child = child_base_name + "_screenZMaster"

                self.lockUnlockAttributes(child, lock=False)

                attr_list = TRANSFORM_ATTR_LIST
                for attr in attr_list:
                    plug = child + '.' + attr
                    cmd = ('source channelBoxCommand; '
                           'CBdeleteConnection "%s";')
                    mel.eval(cmd % plug)

                cmds.parent(child, parent)
                cmds.parent(child_main, parent_main)
                cmds.cutKey(child_main, cl=True, at=SCREEN_Z_DEPTH_ATTR_NAME)

                child_scale = cmds.getAttr(child + ".sx")
                cmds.setAttr(child_main + ".screenzdepth", child_scale)

                src = child_main + "." + SCREEN_Z_DEPTH_ATTR_NAME
                cmds.connectAttr(src, child + ".scaleX", f=True)
                cmds.connectAttr(src, child + ".scaleY", f=True)
                cmds.connectAttr(src, child + ".scaleZ", f=True)

                self.lockUnlockAttributes(child, lock=True)
            self.lockUnlockAttributes(parent, lock=True)
        except:
            _display_warning_ui("freeze rig can not be matched.")
        self.refreshRigsList()


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
    win = ScreenSpaceRigWindow.open_window(
        show=show,
        auto_raise=auto_raise,
        delete=delete
    )
    return win
