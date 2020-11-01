# Copyright (C) 2020 Patcha Saheb Binginapalli.
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




import sys
import math

import maya.api.OpenMaya as om
import maya.OpenMaya as OpenMaya
import maya.api.OpenMayaRender as omr
import maya.OpenMayaRender as OpenMayaRender
import maya.api.OpenMayaUI as omui
import pymel.core as pm
import maya.mel as mel
import maya.cmds as cmds
import mmSolver.api as mmapi
import mmSolver.utils.configmaya as configmaya
import mmSolver.utils.constant as utils_const
import mmSolver.logger
LOG = mmSolver.logger.get_logger()

__author__ = 'patchasaheb'
__version__ = '0.1.0'

maya_useNewAPI = True
mmSolverRenderOverrideInstance = None 
kPluginName = "mmSolver Renderer"

utils_const.SCENE_DATA_NODE = "MM_SOLVER_RENDERER_DATA"
utils_const.SCENE_DATA_ATTR = "Renderer"
scene_data_node = utils_const.SCENE_DATA_NODE

callback_ids = []
mmSolverRendererChangedCB = 0
mmSolverModelEditorChangedCB = 0
mmSolverSceneDataUpdateCB = 0

#callback functions
def onRendererChanged(model_panel, *args):
    if not cmds.modelEditor(model_panel, q=True, qpo="mmsolvershapes"):
        cmds.modelEditor(model_panel, e=True, po=("mmsolvershapes",True))
    if not cmds.objExists(scene_data_node):
        createSceneDataNode()
    sceneDataMarkerBundleLocatorUpdate()


def onModelEditorChanged(client_data):
    panels = cmds.getPanel(type="modelPanel")
    for p in panels:    
        name = cmds.modelEditor(p, q=True, rendererOverrideName=True)
        if name != "mmSolverRenderer":
            if cmds.modelEditor(p, q=True, qpo="mmsolvershapes"):
                cmds.modelEditor(p, e=True, po=("mmsolvershapes",False))
                msg = "mmSolverRenderer is not actived in the viewport"
                LOG.warning(msg)

def createSceneDataNode():
    nodes = cmds.ls(long=True,type="locator")
    markers = []
    bundles = []
    locators = []
    for node in nodes:
        if "MKR" in node and not "markerBundle" in node:
            markers.append(node)
        if "BND" in node and not "markerBundle" in node:
            bundles.append(node)
        if not "MKR" in node:
            if not "BND" in node:
                if not "markerBundle" in node:
                    locators.append(node)
    #set node options
    configmaya.set_scene_option("", "mmSolverRenderer", add_attr=True)
    configmaya.set_node_option(scene_data_node, "UpdateRequire", "True", True)
    configmaya.set_node_option_structure(scene_data_node, "Locators", locators, True)
    configmaya.set_node_option_structure(scene_data_node, "Markers", markers, True)
    configmaya.set_node_option_structure(scene_data_node, "Bundles", bundles, True)
    configmaya.set_node_option(scene_data_node, "Shapes", 0, True)




def sceneDataMarkerBundleLocatorUpdate():
    nodes = cmds.ls(long=True,type="locator")
    markers = []
    bundles = []
    locators = []
    for node in nodes:
        if "MKR" in node and not "markerBundle" in node:
            markers.append(node)
        if "BND" in node and not "markerBundle" in node:
            bundles.append(node)
        if not "MKR" in node:
            if not "BND" in node:
                if not "markerBundle" in node:
                    locators.append(node)     
    #set node options
    configmaya.set_node_option(scene_data_node, "UpdateRequire", "True")    
    configmaya.set_node_option_structure(scene_data_node, "Locators", locators)
    configmaya.set_node_option_structure(scene_data_node, "Markers", markers)
    configmaya.set_node_option_structure(scene_data_node, "Bundles", bundles)
    configmaya.set_node_option(scene_data_node, "UpdateRequire", "True")    


def onNodeAdded(*args):
    sceneDataMarkerBundleLocatorUpdate()


# main MRenderOverride
class ViewmmSolverRenderOverride(omr.MRenderOverride):
    # constructor
    def __init__(self, name):
        #omr.MRenderOverride.__init__(self, name)
        super(ViewmmSolverRenderOverride, self).__init__(name)
        # name in the renderer dropdown menu
        self.mUIName = kPluginName

        # render operations list
        self.mRenderOperations = []

        #MSAA 4x
        sampleCount = 4
        colorFormat = omr.MRenderer.kR32G32B32A32_FLOAT;
        depthFormat = omr.MRenderer.kD24S8
        self.colorDesc = omr.MRenderTargetDescription("__color_mmsolver_renderer__", 256, 256, sampleCount, colorFormat, 0, False)
        self.depthDesc = omr.MRenderTargetDescription("__depth_mmsolver_renderer__", 256, 256, sampleCount, depthFormat, 0, False)
        
        self.colorTarget = None
        self.depthTarget = None

        #standard pass
        self.mStandardPass = ViewmmSolverSceneRender("standardPass", omr.MClearOperation.kClearAll, False)
        #self.mStandardPass.setSceneFilter(omr.MSceneRender.kRenderShadedItems | omr.MSceneRender.kRenderUIItems)
        self.mStandardPass.setExcludeType(omr.MSceneRender.kExcludeLocators)        
        self.mRenderOperations.append(self.mStandardPass)

        #locator pass
        self.mLocatorPass = ViewmmSolverSceneRender("locatorPass", omr.MClearOperation.kClearNone, True)
        #self.mLocatorPass.setSceneFilter(omr.MSceneRender.kRenderNonShadedItems)
        self.mRenderOperations.append(self.mLocatorPass)

        #user pass
        self.mUserPass = ViewmmSolverUserOperation("userPass" )
        self.mRenderOperations.append(self.mUserPass) 

        #HUD pass
        self.mHUDPass = ViewmmSolverHudRender()        
        self.mRenderOperations.append(self.mHUDPass)

        #Present pass
        self.mPresentPass = ViewmmSolverPresentRender("PresentPass")
        self.mRenderOperations.append(self.mPresentPass)

        self.mPanelName = ""


       

        """#get marker,bundle,locator nodes           
        nodes = cmds.ls(long=True,type="locator")
        nodes = [cmds.listRelatives(node, fullPath=True, parent=True) for node in nodes]                
        flat_list = [item for sublist in nodes for item in sublist]
        markers = mmapi.filter_marker_nodes(flat_list) or [] 
        bundles = mmapi.get_bundle_nodes_from_marker_nodes(markers) or []

        locators = list(set(flat_list) - set(markers))
        locators = list(set(locators) - set(bundles))
        locators = cmds.listRelatives(locators, fullPath=True, shapes=True) or []"""





    # destructor
    def __del__(self):      
        targetManager = omr.MRenderer.getRenderTargetManager()
        if self.colorTarget is not None:
            targetManager.releaseRenderTarget(self.colorTarget)
            self.colorTarget = None

        if self.depthTarget is not None:
            targetManager.releaseRenderTarget(self.depthTarget)
            self.depthTarget = None

        #callbacks cleanup
        global callback_ids
        om.MMessage.removeCallbacks(callback_ids)
        callback_ids = []
        mmSolverRendererChangedCB = 0
        mmSolverModelEditorChangedCB = 0
        mmSolverSceneDataUpdateCB = 0





    def supportedDrawAPIs(self):
        return omr.MRenderer.kAllDevices

    # called by maya to start iterating through passes
    def startOperationIterator(self):
        self.mOperation = 0
        return True

    # called by maya to define which pass to calculate
    # the order specified here defines the draw order
    def renderOperation(self):
        return self.mRenderOperations[self.mOperation]

    # advance to the next pass or return false if
    # all are calculated
    def nextRenderOperation(self):
        self.mOperation = self.mOperation + 1
        return self.mOperation < len(self.mRenderOperations)

    def setup(self, destination):
        global callback_ids, mmSolverModelEditorChangedCB, mmSolverRendererChangedCB
        global mmSolverSceneDataUpdateCB

        self.mPanelName = destination

        #create callbacks
        if len(self.mPanelName) > 0:
            view = omui.M3dView.getM3dViewFromModelPanel(self.mPanelName)
            if mmSolverRendererChangedCB == 0:
                mmSolverRendererChangedCB = omui.MUiMessage.add3dViewRenderOverrideChangedCallback(self.mPanelName, onRendererChanged)
                callback_ids.append(mmSolverRendererChangedCB)

        if mmSolverModelEditorChangedCB == 0:
            mmSolverModelEditorChangedCB = om.MEventMessage.addEventCallback("modelEditorChanged", onModelEditorChanged)
            callback_ids.append(mmSolverModelEditorChangedCB)

        if mmSolverSceneDataUpdateCB == 0:
            mmSolverSceneDataUpdateCB = om.MEventMessage.addEventCallback("DagObjectCreated", onNodeAdded)
            callback_ids.append(mmSolverSceneDataUpdateCB)


        if not cmds.objExists(scene_data_node):
            createSceneDataNode()
            sceneDataMarkerBundleLocatorUpdate()









        
        # set the size of the target, so when the viewport scales,
        # the targets remain a 1:1 pixel size
        targetManager = omr.MRenderer.getRenderTargetManager()
        width, height = omr.MRenderer.outputTargetSize()
        self.colorDesc.setWidth(width)
        self.colorDesc.setHeight(height)

        self.depthDesc.setWidth(width)
        self.depthDesc.setHeight(height)
        
        if self.colorTarget is None:
            self.colorTarget = targetManager.acquireRenderTarget(self.colorDesc)
        else:
            self.colorTarget.updateDescription(self.colorDesc)
        
        if self.depthTarget is None:
            self.depthTarget = targetManager.acquireRenderTarget(self.depthDesc)
        else:
            self.depthTarget.updateDescription(self.depthDesc)

        #Setting Render targets
        self.mStandardPass.setRenderTarget([self.colorTarget, self.depthTarget])                                     
        self.mLocatorPass.setRenderTarget([self.colorTarget, self.depthTarget])
        self.mUserPass.setPanelName(self.mPanelName)                                   
        self.mUserPass.setRenderTarget([self.colorTarget, self.depthTarget])
        self.mHUDPass.setRenderTarget([self.colorTarget, self.depthTarget])
        self.mPresentPass.setRenderTarget([self.colorTarget, self.depthTarget])

    def panelName(self):
        return self.mPanelName      

    # called by maya. Sets the name in the "Renderers" dropdown
    def uiName(self):
        return self.mUIName


#user render operation
class ViewmmSolverUserOperation(omr.MUserRenderOperation):
    def __init__(self, name):
        omr.MUserRenderOperation.__init__(self, name)

        # 3D viewport panel name, if any
        self.mPanelName = ""

        # Available targets
        self.mTargets = None

        self.mSel = om.MSelectionList() 

    def hasUIDrawables(self):
        return True

    def addUIDrawables(self, drawManager, frameContext):
        pass
        return True


    def execute(self, drawContext):
        pass





    def panelName(self):
        return self.mPanelName

    def setPanelName(self, name):
        self.mPanelName = name            

    def targetOverrideList(self):        
        return self.mTargets

    def setRenderTarget(self, target):
        self.mTargets = target

    def __del__(self):
        self.mTargets = None 


class ViewmmSolverSceneRender(omr.MSceneRender):
    def __init__(self, name, clearMask, doLocators=False):
        omr.MSceneRender.__init__(self, name)

        self.doLocators = doLocators

        # 3D viewport panel name, if available
        self.mPanelName = name

        # Available render targets
        self.mTargets = None

        # Mask for clear override
        self.mClearMask = clearMask

        #selection list
        self.objectList = om.MSelectionList()

        self.mSceneFilter = omr.MSceneRender.kNoSceneFilterOverride        

        #exlude type
        self.excludeType = omr.MSceneRender.kExcludeNone 

    def __del__(self):
        self.mTargets = None

    def setExcludeType(self, excludeType):
        self.excludeType = excludeType

    # sets the clear mask
    def clearOperation(self):
        # setOverridesColors(False) doesn't work in 2016
        #bg = pm.general.displayRGBColor('background', q=True)
        self.mClearOperation.setOverridesColors(False)
        self.mClearOperation.setMask(self.mClearMask)
        return self.mClearOperation

    def setRenderTarget(self, target):
        self.mTargets = target

    def objectSetOverride(self):
        if self.doLocators:
            if cmds.objExists(scene_data_node):
                if configmaya.get_node_option(scene_data_node, "UpdateRequire") == "True":
                    self.objectList.clear()
                    locator_nodes = configmaya.get_node_option_structure(scene_data_node,"Locators") or []
                    [self.objectList.add(loc) for loc in locator_nodes]
                    configmaya.set_node_option(scene_data_node, "UpdateRequire", "False")
                return self.objectList
        return None

    def setSceneFilter(self, filter):
        self.mSceneFilter = filter

    def renderFilterOverride(self):
        return self.mSceneFilter

    def targetOverrideList(self):        
        return self.mTargets

    def getObjectTypeExclusions(self):
        return self.excludeType


class ViewmmSolverHudRender(omr.MHUDRender):
    def __init__(self):
        omr.MHUDRender.__init__(self)
        self.mTargets = None        

    def setRenderTarget(self, target):
        self.mTargets = target

    def targetOverrideList(self):        
        return self.mTargets

    def __del__(self):
        self.mTargets = None 


class ViewmmSolverPresentRender(omr.MPresentTarget):
    def __init__(self, name):
        omr.MPresentTarget.__init__(self, name)
        self.mTargets = None        

    def setRenderTarget(self, target):
        self.mTargets = target

    def targetOverrideList(self):        
        return self.mTargets

    def __del__(self):
        self.mTargets = None




def initializePlugin(mobj):
    plugin = om.MFnPlugin(mobj, __author__, __version__, 'Any')

    try:
        #register render override
        global mmSolverRenderOverrideInstance
        mmSolverRenderOverrideInstance = ViewmmSolverRenderOverride("mmSolverRenderer")
        omr.MRenderer.registerOverride(mmSolverRenderOverrideInstance)

        #register plugin display filter
        cmds.pluginDisplayFilter('mmsolvershapes', register=True, label='mmSolver Renderer Shapes', cls="drawdb/geometry/markerBundleShape")

    except Exception:
        sys.stderr.write("registerOverride\n")
        om.MGlobal.displayError("registerOverride")
        raise 


def uninitializePlugin(mobj):
    try:
        #deregister render override
        global mmSolverRenderOverrideInstance
        if mmSolverRenderOverrideInstance is not None:
            omr.MRenderer.deregisterOverride(mmSolverRenderOverrideInstance)
            mmSolverRenderOverrideInstance = None

        #deregister plugin display filter           
        if cmds.pluginDisplayFilter("mmsolvershapes", q=True, ex=True):
            cmds.pluginDisplayFilter('mmsolvershapes', deregister=True)

        #delete scene node
        if cmds.objExists(scene_data_node):
            cmds.delete(scene_data_node)

    except Exception:
        sys.stderr.write("deregisterOverride\n")
        om.MGlobal.displayError("deregisterOverride")
        raise 

#initally turn off plugin display filter
panels = cmds.getPanel(type="modelPanel")
for pk in panels:
    cmds.modelEditor(pk, e=True, po=("mmsolvershapes",False))

