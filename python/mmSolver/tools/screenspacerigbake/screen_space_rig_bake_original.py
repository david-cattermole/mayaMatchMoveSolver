from PySide2 import QtCore, QtGui, QtWidgets
from shiboken2 import wrapInstance
import maya.OpenMaya as om
import maya.OpenMayaUI as omui
import maya.OpenMayaAnim as oma
import maya.cmds as cmds
import maya.mel as mel



#import screen_space_rig_bake
#reload(screen_space_rig_bake) 

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class screenSpaceRigTools(QtWidgets.QDialog):    
    def __init__(self, parent=maya_main_window()):
        super(screenSpaceRigTools, self).__init__(parent)
        
        self.setWindowTitle("Screen Space Rig Bake")
        self.setMinimumWidth(240)
        self.setMinimumHeight(380)
        #self.setMaximumWidth(290)
        #self.setMaximumHeight(380)
        

        self.initUI()
        self.createConnections()
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)
        self.start_frame = int(oma.MAnimControl.minTime().value())
        self.end_frame = int(oma.MAnimControl.maxTime().value())
        self.refreshRigsList()


    def initUI(self): 

        self.transform_icon = QtGui.QIcon(":transform.svg")

        #main layout       
        self.gridLayout = QtWidgets.QGridLayout(self)

        #menu bar
        self.menu_bar = QtWidgets.QMenuBar()

        #menus
        #self.create_rig_menu = self.menu_bar.addMenu("Create Rig")
        self.options_menu = self.menu_bar.addMenu("Freeze")
        self.refresh_menu = self.menu_bar.addMenu("Refresh")

        #freeze options actions
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


        spacerItem = QtWidgets.QSpacerItem(5, 17, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 0, 1, 1)

        #full bake radio button
        self.full_bake_rdo_btn = QtWidgets.QRadioButton()
        self.gridLayout.addWidget(self.full_bake_rdo_btn, 0, 1, 1, 1)

        spacerItem1 = QtWidgets.QSpacerItem(5, 17, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 2, 1, 1)

        #smart bake radio button
        self.smart_bake_rdo_btn = QtWidgets.QRadioButton()
        self.smart_bake_rdo_btn.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.smart_bake_rdo_btn.setAutoFillBackground(False)
        self.smart_bake_rdo_btn.setChecked(True)
        self.gridLayout.addWidget(self.smart_bake_rdo_btn, 0, 3, 1, 1)

        spacerItem2 = QtWidgets.QSpacerItem(5, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 0, 4, 1, 1)

        #separator line
        """self.line = QtWidgets.QFrame()
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.gridLayout.addWidget(self.line, 1, 0, 1, 5)"""

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

        """self.horizontalLayout_3 = QtWidgets.QHBoxLayout()

        #create rig button
        self.create_rig_btn = QtWidgets.QPushButton()
        self.horizontalLayout_3.addWidget(self.create_rig_btn)

        #remove rig button
        self.remove_rig_btn = QtWidgets.QPushButton()
        self.horizontalLayout_3.addWidget(self.remove_rig_btn)

        self.gridLayout.addLayout(self.horizontalLayout_3, 4, 0, 1, 5)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()

        #match rigs button
        self.match_btn = QtWidgets.QPushButton()
        self.horizontalLayout_4.addWidget(self.match_btn)

        #freeze rig button
        self.freeze_btn = QtWidgets.QPushButton()
        self.horizontalLayout_4.addWidget(self.freeze_btn)

        self.gridLayout.addLayout(self.horizontalLayout_4, 5, 0, 1, 5)"""

        #widget labels
        self.full_bake_rdo_btn.setText("Full bake")
        self.smart_bake_rdo_btn.setText("Smart bake")
        self.rigs_label.setText("Rigs")
        self.name_label.setText("Name")

        """self.create_rig_btn.setText("Create Screen Space Rig")
        self.remove_rig_btn.setText("Bake Rig")
        self.match_btn.setText("Match Rigs Screen Z")
        self.freeze_btn.setText("Create Freeze Rig")"""

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


    def createConnections(self):
        """self.create_rig_btn.clicked.connect(self.createRigBtn)
        self.remove_rig_btn.clicked.connect(self.removeRigBtn)
        self.match_btn.clicked.connect(self.Match)
        self.freeze_btn.clicked.connect(self.Freeze)"""
        self.create_rig_action.triggered.connect(self.createRigBtn)
        self.match_rig_action.triggered.connect(self.Match)
        self.create_freeze_rig_action.triggered.connect(self.createFreezeRigBtn)
        self.bake_rig_action.triggered.connect(self.bakeRigBtn)
        self.delete_rig_action.triggered.connect(self.deleteRigBtn)
        self.refresh_action.triggered.connect(self.refreshRigsList)
        self.animlayer_action.triggered.connect(self.freezeOptionsUpdate)
        self.world_space_action.triggered.connect(self.freezeOptionsUpdate)
        self.camera_space_action.triggered.connect(self.freezeOptionsUpdate)
        QtCore.QObject.connect(self.name_text, QtCore.SIGNAL("editingFinished()"), self.clearFocus)

    def showContextMenu(self, point):
        self.context_menu.exec_(self.mapToGlobal(point))


    def refreshRigsList(self):
        self.rigs_list.clear()
        mItDag = om.MItDag(om.MItDag.kDepthFirst, om.MFn.kTransform)      
        while not mItDag.isDone():
            depNode = om.MFnDependencyNode(mItDag.currentItem())
            if depNode.hasAttribute('screenzrigidentifier'):
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
        children = cmds.listRelatives(item.text(0), c=True)
        if children:
            for child in children:
                if "screenzrigidentifier" in cmds.listAttr(child):
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
        self.bake_options = []
        if self.full_bake_rdo_btn.isChecked():
            self.bake_options.append("full_bake")
        else:
            self.bake_options.append("smart_bake")
        self.bake_options = self.bake_options[0]
        return self.bake_options        


    def getViewportCamera(self):
        view = omui.M3dView.active3dView()
        camera = om.MDagPath()
        view.getCamera(camera)
        self.vp_camera = om.MFnDagNode(camera.transform()).name()
        return self.vp_camera


    def preBakeFramesList(self, object):
        self.frames_list = []
        self.start_frame = int(oma.MAnimControl.minTime().value())
        self.end_frame = int(oma.MAnimControl.maxTime().value())
        keys_list = cmds.keyframe(object, q=True, time=(self.start_frame, self.end_frame))
        if keys_list == None:
            self.frames_list = [self.start_frame, self.end_frame]
        if self.bakeOptions() == "full_bake":
            for frame in range(self.start_frame, self.end_frame + 1):
                if frame not in self.frames_list:
                    self.frames_list.append(frame)
        if self.bakeOptions() == "smart_bake":
            keys_list = cmds.keyframe(object, q=True, time=(self.start_frame, self.end_frame))
            if keys_list:
                for frame in keys_list:
                     if frame not in self.frames_list:
                        self.frames_list.append(frame)
        self.frames_list.sort()
        return self.frames_list


    def offsetVector(self, a, b):
        a_pos = cmds.xform(a, q=True, ws=True, t=True)
        b_pos = cmds.xform(b, q=True, ws=True, t=True)
        a_vector = om.MVector(a_pos[0], a_pos[1], a_pos[2])
        b_vector = om.MVector(b_pos[0], b_pos[1], b_pos[2])
        length = (b_vector - a_vector).length()
        return length


    def calcDistance(self, camera, object, offset):
        try:
            cmds.refresh(suspend=True)
            mel.eval('paneLayout -e -manage false $gMainPane')
            self.d_list = []
            if self.preBakeFramesList(object):
                parked_frame = cmds.currentTime(q=True)
                for frame in self.frames_list:
                    oma.MAnimControl.setCurrentTime(om.MTime(float(frame)))
                    self.d_list.append(self.offsetVector(camera, object) + offset) 
                cmds.currentTime(parked_frame, e=True)
            cmds.refresh(suspend=False)
            mel.eval('paneLayout -e -manage true $gMainPane')             
        except:
            cmds.refresh(suspend=False)
            mel.eval('paneLayout -e -manage true $gMainPane')
        return self.d_list


    def createRig(self, camera, object, dlist, name, rigName):
        try:
            cmds.refresh(suspend=True)
            mel.eval('paneLayout -e -manage false $gMainPane')

            #create main group
            main_grp = cmds.group(empty=True, n=name + rigName)
            #delete all transform attributes
            attr_list = ["tx","ty","tz","rx","ry","rz","sx","sy","sz","visibility"]
            for attr in attr_list:
                cmds.setAttr(main_grp+"."+attr, k=0, l=1)

            #add custom attributes
            cmds.addAttr(main_grp, ln="screenx", nn="Screen X", at="float", k=True)
            cmds.addAttr(main_grp, ln="screeny", nn="Screen Y", at="float", k=True)
            cmds.addAttr(main_grp, ln="screenzdepth", nn="Screen Z depth", at="float", k=True)        
            cmds.addAttr(main_grp, ln="screenzrigidentifier", nn="ScreenZRigIdentifier", dt="string", k=False) 
            cmds.setAttr(main_grp+".screenzrigidentifier", str(object), type="string")

            #set keyframes on screezdepth attribute
            frames_list = self.preBakeFramesList(object)
            for i in range(len(frames_list)):
                cmds.setKeyframe(main_grp, at="screenzdepth", t=frames_list[i], v=dlist[i])

            #clear name text
            self.name_text.clear()
            self.name_text.clearFocus()

            #create screez master group
            screenz_master_grp = cmds.group(em=True, n=name + "_screenZMaster")
            cmds.setAttr(screenz_master_grp+".visibility", 0)
            #add screen x,y copy attributes
            cmds.addAttr(screenz_master_grp, ln="screenxcopy", nn="Screen X copy", at="float")
            cmds.addAttr(screenz_master_grp, ln="screenycopy", nn="Screen Y copy", at="float")
            cmds.setAttr(screenz_master_grp+".screenxcopy", cb=False)
            cmds.setAttr(screenz_master_grp+".screenycopy", cb=False)

            cmds.parent(screenz_master_grp, main_grp)
            con = cmds.parentConstraint(self.getViewportCamera(), screenz_master_grp)
            cmds.bakeResults(screenz_master_grp, t=(self.start_frame, self.end_frame), sm=True)
            cmds.delete(con)

            #create screenz depth connections
            cmds.connectAttr(main_grp+".screenzdepth", screenz_master_grp+".scaleX", f=True)
            cmds.connectAttr(main_grp+".screenzdepth", screenz_master_grp+".scaleY", f=True)
            cmds.connectAttr(main_grp+".screenzdepth", screenz_master_grp+".scaleZ", f=True)

            #create screen xy master group
            screen_xy_master_grp = cmds.group(em=True, n=name + "_screenXYMaster")
            cmds.setAttr(screen_xy_master_grp+".visibility", 0)
            attr_list = ["rx","ry","rz","sx","sy","sz","visibility"]
            for attr in attr_list:
                cmds.setAttr(screen_xy_master_grp+"."+attr, k=0, l=1)
            cmds.parent(screen_xy_master_grp, screenz_master_grp, r=True)
            con = cmds.pointConstraint(object, screen_xy_master_grp)
            cmds.bakeResults(screen_xy_master_grp, t=(self.start_frame, self.end_frame), sm=True)
            cmds.delete(con)
            cmds.setAttr(screen_xy_master_grp+".translateZ", l=1)

            #create screenxy connections
            cmds.connectAttr(screen_xy_master_grp+".translateX", main_grp+".screenx", f=True)
            cmds.connectAttr(screen_xy_master_grp+".translateY", main_grp+".screeny", f=True)
            cmds.connectAttr(screen_xy_master_grp+".translateX", screenz_master_grp+".screenxcopy", f=True)
            cmds.connectAttr(screen_xy_master_grp+".translateY", screenz_master_grp+".screenycopy", f=True)
            cmds.bakeResults(main_grp, at=["screenx","screeny"], t=(self.start_frame, self.end_frame), sm=True)
            cmds.bakeResults(screenz_master_grp, at=["screenxcopy","screenycopy"], t=(self.start_frame, self.end_frame), sm=True)
            cmds.connectAttr(main_grp+".screenx", screen_xy_master_grp+".translateX", f=True)
            cmds.connectAttr(main_grp+".screeny", screen_xy_master_grp+".translateY", f=True)

            #create condition node network
            screenx_condition_node = cmds.shadingNode("condition", au=True, n=name+"_screenx_condition")
            screeny_condition_node = cmds.shadingNode("condition", au=True, n=name+"_screeny_condition")

            cmds.connectAttr(main_grp+".screenx", screenx_condition_node+".firstTerm", f=True)
            cmds.connectAttr(screenz_master_grp+".screenxcopy", screenx_condition_node+".secondTerm", f=True)
            cmds.connectAttr(main_grp+".screeny", screeny_condition_node+".firstTerm", f=True)
            cmds.connectAttr(screenz_master_grp+".screenycopy", screeny_condition_node+".secondTerm", f=True)

            attr_list = ["tx","ty","tz","rx","ry","rz","visibility"]
            for attr in attr_list:
                cmds.setAttr(screenz_master_grp+"."+attr, l=1)

            cmds.pointConstraint(screen_xy_master_grp, object)
            #clear selection in the end
            cmds.select(cl=True)                           
            self.refreshRigsList()
            cmds.refresh(suspend=False)
            mel.eval('paneLayout -e -manage true $gMainPane')          
        except:
            cmds.refresh(suspend=False)
            mel.eval('paneLayout -e -manage true $gMainPane')


    def checkNameExists(self, rigName):
        boolean = [False, False]          
        sel = cmds.ls(transforms=True, os=True)
        if sel and len(sel) > 0:
            name = self.name_text.text()
            if name != "":
                name = name.split(",")
                if len(name) == len(sel):
                    boolean[0] = True
                    for i in range(len(sel)):
                        #sel_item = sel[i]
                        name_item = name[i]                          
                        #check if name already exists
                        iterator = QtWidgets.QTreeWidgetItemIterator(self.rigs_list)
                        while iterator.value():
                            item = iterator.value()
                            item_name = item.text(0)
                            item_name = item_name.replace(rigName, "")
                            if item_name == name_item:
                                boolean[1] = True
                            iterator += 1
                    if boolean[1] == True:
                        cmds.confirmDialog(title="Warning",message="warning, same name exists already please type different name.")
                else:
                    cmds.confirmDialog(title="Warning",message="warning, selection and name count not matching.")                                 
            else:
                cmds.confirmDialog(title="Warning",message="warning, please type name first.")                                
        else:
            cmds.confirmDialog(title="Warning",message="warning, atleast one Transform node type object must be selected.")
        return boolean



    def createRigBtn(self):
        if self.checkNameExists("_screenSpaceRig") == [True, False]:
            sel = cmds.ls(transforms=True, os=True)
            name = self.name_text.text()
            name = name.split(",")
            for i in range(len(sel)):
                sel_item = sel[i]
                name_item = name[i]                        
                #check if object has existing point constraint already
                null = 0
                k = cmds.listRelatives(sel_item, type="constraint")
                if k != None:
                    if "pointConstraint" in k or "parentConstraint":
                        null = 1
                if null == 0:
                    dlist = self.calcDistance(self.getViewportCamera(), sel_item, 0)
                    if dlist:
                        self.createRig(self.getViewportCamera(), sel_item, dlist, name_item, "_screenSpaceRig")
                else:
                    cmds.confirmDialog(title="Warning",message="warning, selected object(s) already have constraints.")
                    break


    def createFreezeRigBtn(self):
        if self.checkNameExists("_freezeRig") == [True, False]:
            sel = cmds.ls(transforms=True, os=True)
            name = self.name_text.text()
            name = name.split(",")
            for i in range(len(sel)):
                sel_item = sel[i]
                name_item = name[i]                        
                #check if object has existing point constraint already
                null = 0
                k = cmds.listRelatives(sel_item, type="constraint")
                if k != None:
                    if "pointConstraint" in k or "parentConstraint":
                        null = 1
                if null == 0:
                    try:
                        cmds.refresh(suspend=True)
                        mel.eval('paneLayout -e -manage false $gMainPane')                    
                        if self.camera_space_action.isChecked():
                            dlist = self.calcDistance(self.getViewportCamera(), sel_item, 0)
                            if dlist:
                                self.createRig(self.getViewportCamera(), sel_item, dlist, name_item, "_freezeRig")
                                cmds.cutKey(name_item+"_freezeRig", cl=True, at="screenzdepth")
                        if self.world_space_action.isChecked():
                            self.full_bake_rdo_btn.setChecked(True)
                            #create a static temp group  
                            temp_grp = cmds.group(em=True)
                            con = cmds.parentConstraint(sel_item, temp_grp, mo=False)
                            cmds.delete(con)
                            cmds.bakeResults(temp_grp, t=(self.start_frame, self.end_frame), sm=True)
                            dlist = self.calcDistance(self.getViewportCamera(), sel_item, 0)
                            if dlist:
                                self.createRig(self.getViewportCamera(), sel_item, dlist, name_item, "_freezeRig")
                                #calc full freeze list
                                dlist = self.calcDistance(self.getViewportCamera(), temp_grp, 0)
                                parked_frame = cmds.currentTime(q=True)
                                if self.animlayer_action.isChecked() == False:
                                    #set keyframes on screezdepth attribute
                                    count = -1
                                    for i in range(self.start_frame, self.end_frame+1):
                                        count += 1
                                        oma.MAnimControl.setCurrentTime(om.MTime(i))
                                        cmds.setKeyframe(name_item+"_freezeRig", at="screenzdepth", v=dlist[count])
                                if self.animlayer_action.isChecked():
                                    cmds.select(name_item+"_freezeRig", replace=True)
                                    anim_layer = cmds.animLayer(name_item+"_freezeRigLayer", aso=True)
                                    cmds.select(clear=True)
                                    count = -1
                                    for i in range(self.start_frame, self.end_frame+1):
                                        count += 1
                                        oma.MAnimControl.setCurrentTime(om.MTime(i))
                                        cmds.setKeyframe(name_item+"_freezeRig", al=name_item+"_freezeRigLayer", at=("screenzdepth"), v=dlist[count])
                                cmds.currentTime(parked_frame, e=True)
                                #delete temp group
                                cmds.delete(temp_grp)

                        cmds.refresh(suspend=False)
                        mel.eval('paneLayout -e -manage true $gMainPane')                                                        
                    except:
                        cmds.refresh(suspend=False)
                        mel.eval('paneLayout -e -manage true $gMainPane')                    
                else:
                    cmds.confirmDialog(title="Warning",message="warning, selected object(s) already have constraints.")
                    break


    def bakeRigBtn(self):
        selected_items = self.rigs_list.selectedItems()
        if len(selected_items) > 0:
            try:
                cmds.refresh(suspend=True)
                mel.eval('paneLayout -e -manage false $gMainPane')            
                cmds.select(clear=True)
                for i in range(len(selected_items)):
                    children = self.getAllChildren(selected_items[i])
                    for j in children:
                        rigName = j.text(0)
                        object = cmds.getAttr(rigName+".screenzrigidentifier")
                        if "_freezeRig" in rigName:
                            self.full_bake_rdo_btn.setChecked(True)

                        if "_screenSpaceRig" in rigName:
                            name = rigName.split("_screenSpaceRig")[0]
                        if "_freezeRig" in rigName:
                            name = rigName.split("_freezeRig")[0]

                        self.bakeOptions()
                        if self.bake_options == "full_bake":
                            cmds.bakeResults(object, t=(self.start_frame, self.end_frame), sm=True)
                        if self.bake_options == "smart_bake":
                            nodes_list = cmds.listConnections(name+"_screenZMaster")
                            for node in nodes_list:
                                if "screenx_condition" in node:
                                    x_node = node
                                if "screeny_condition" in node:
                                    y_node = node

                            parked_frame = cmds.currentTime(q=True)                        
                            cmds.select(object)
                            #first key on objects existing key frames
                            for frame in self.preBakeFramesList(object):
                                oma.MAnimControl.setCurrentTime(om.MTime(frame))
                                cmds.setKeyframe(at=["tx","ty","tz"])

                            #key screen z depth attribute frames                           
                            keys_list = cmds.keyframe(rigName+".screenzdepth",q=True)
                            if keys_list:
                                for frame in keys_list:
                                    oma.MAnimControl.setCurrentTime(om.MTime(frame))
                                    cmds.setKeyframe(at=["tx","ty","tz"])                        

                            #check condition result node and set keyframe
                            for i in range(self.start_frame, self.end_frame+1):
                                oma.MAnimControl.setCurrentTime(om.MTime(i))
                                if cmds.getAttr(x_node+".outColor")[0][0] == 1 or cmds.getAttr(y_node+".outColor")[0][0] == 1:
                                    cmds.setKeyframe(at=["tx","ty","tz"])
                            cmds.currentTime(parked_frame, e=True)
                            cmds.select(clear=True)

                self.deleteRigBtn()
                self.refreshRigsList()
                cmds.refresh(suspend=False)
                mel.eval('paneLayout -e -manage true $gMainPane')            
            except:
                cmds.refresh(suspend=False)
                mel.eval('paneLayout -e -manage true $gMainPane')                          
        else:
            cmds.confirmDialog(title="Warning",message="warning, at least one rig must be selected from Rigs list.")



    def getAllChildren(self, tree_widget_item):
        nodes = []
        nodes.append(tree_widget_item)
        for i in range(tree_widget_item.childCount()):
            nodes.extend(self.getAllChildren(tree_widget_item.child(i)))
        return nodes 


    def deleteRigBtn(self):
        selected_items = self.rigs_list.selectedItems()
        if len(selected_items) > 0:
            cmds.select(clear=True)
            for i in range(len(selected_items)):
                children = self.getAllChildren(selected_items[i])
                for j in children:
                    rigName = j.text(0)
                    if "_screenSpaceRig" in rigName:
                        name = rigName.split("_screenSpaceRig")[0]
                    if "_freezeRig" in rigName:
                        name = rigName.split("_freezeRig")[0]
                    nodes_list = cmds.listConnections(name+"_screenZMaster")
                    for node in nodes_list:
                        if "screenx_condition" in node:
                            x_node = node
                        if "screeny_condition" in node:
                            y_node = node                        
                    cmds.select(rigName, name+"_screenZMaster", name+"_screenXYMaster", x_node, y_node, add=True)                 
                    try:
                        cmds.delete(rigName+"Layer")
                    except:
                        pass
            cmds.delete()
            self.refreshRigsList()
        else:
            cmds.confirmDialog(title="Warning",message="warning, at least one rig must be selected from Rigs list.")                


    def lockUnlockAttributes(self, object, lock=True):
        if lock == False:
            attr_list = ["tx","ty","tz","rx","ry","rz","sx","sy","sz"]
            for attr in attr_list:
                cmds.setAttr(object+"."+attr, l=0)        
        if lock == True:
            attr_list = ["tx","ty","tz","rx","ry","rz","sx","sy","sz"]
            for attr in attr_list:
                cmds.setAttr(object+"."+attr, l=1)


    def Match(self):
        selected_items = self.rigs_list.selectedItems()
        if len(selected_items) > 1:
            parent_main = selected_items[0].text(0)
            #parent = cmds.pickWalk(parent_main, d="down")
            try:
                parent = parent_main.split("_screenSpaceRig")[0] + "_screenZMaster"
                self.lockUnlockAttributes(parent, lock=False)
                for i in range(len(selected_items)-1):
                    i += 1
                    child_main = selected_items[i].text(0)
                    #child = cmds.pickWalk(child_main, d="down")
                    child = child_main.split("_screenSpaceRig")[0] + "_screenZMaster"
                    self.lockUnlockAttributes(child, lock=False)
                    attr_list = [child+".tx",child+".ty",child+".tz",child+".rx",child+".ry",child+".rz",child+".sx", child+".sy", child+".sz"]
                    for attr in attr_list:
                        mel.eval("source channelBoxCommand; CBdeleteConnection \"%s\""%attr)                
                    cmds.parent(child, parent)
                    cmds.parent(child_main, parent_main)
                    cmds.cutKey(child_main, cl=True, at="screenzdepth")
                    cmds.setAttr(child_main+".screenzdepth",cmds.getAttr(child+".sx"))
                    cmds.connectAttr(child_main+".screenzdepth", child+".scaleX", f=True)
                    cmds.connectAttr(child_main+".screenzdepth", child+".scaleY", f=True)
                    cmds.connectAttr(child_main+".screenzdepth", child+".scaleZ", f=True)
                    self.lockUnlockAttributes(child, lock=True)
                self.lockUnlockAttributes(parent, lock=True)
            except:
                cmds.confirmDialog(title="Warning",message="warning, freeze rig can not be matched.")
            self.refreshRigsList()
        else:
            cmds.confirmDialog(title="Warning",message="warning, at least two rigs must be selected from Rigs list.")
        
try:
    screenSpace_rig_tools_win.close()
    screenSpace_rig_tools_win.deleteLater()
except:
    pass

screenSpace_rig_tools_win = screenSpaceRigTools()
screenSpace_rig_tools_win.show()