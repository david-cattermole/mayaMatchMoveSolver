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
import maya.api.OpenMaya as om
import maya.api.OpenMayaUI as omui
import maya.api.OpenMayaRender as omr


def maya_useNewAPI():
   pass


# shape2 Data
s2_center_left = [[-0.33, 0.0, 0.0],
                  [-0.66, 0.0, 0.0]]

s2_center_right = [[0.33, 0.0, 0.0],
                   [0.66, 0.0, 0.0]]

s2_center_top = [[0.0, 0.33, 0.0],
                 [0.0, 0.66, 0.0]]

s2_center_bottom = [[0.0, -0.33, 0.0],
                    [0.0, -0.66, 0.0]]

s2_top_left = [[-0.495, 0.99, 0.0],
               [-0.99, 0.99, 0.0],
               [-0.99, 0.495, 0.0]]

s2_top_right = [[0.495, 0.99, 0.0],
                [0.99, 0.99, 0.0],
                [0.99, 0.495, 0.0]]

s2_bottom_left = [[-0.495, -0.99, 0.0],
                  [-0.99, -0.99, 0.0],
                  [-0.99, -0.495, 0.0]]

s2_bottom_right = [[0.495, -0.99, 0.0],
                   [0.99, -0.99, 0.0],
                   [0.99, -0.495, 0.0]]

s2_center_left_count = 2
s2_center_right_count = 2
s2_center_bottom_count = 2
s2_center_top_count = 2
s2_top_left_count = 3
s2_top_right_count = 3
s2_bottom_left_count = 3
s2_bottom_right_count = 3

#############################################################################

# shape3 Data
s3_center_left = [[-0.33, 0.0, 0.0],
                  [-1.0, 0.0, 0.0]]

s3_center_right = [[0.33, 0.0, 0.0],
                   [1.0, 0.0, 0.0]]

s3_center_top = [[0.0, 0.33, 0.0],
                 [0.0, 1.0, 0.0]]

s3_center_bottom = [[0.0, -0.33, 0.0],
                    [0.0, -1.0, 0.0]]

s3_center_left_count = 2
s3_center_right_count = 2
s3_center_bottom_count = 2
s3_center_top_count = 2

#############################################################################

# shape4 Data
s4_horizontal = [[1.0, 0.0, 0.0],
                 [-1.0, 0.0, 0.0]]

s4_vertical = [[0.0, 1.0, 0.0],
               [0.0, -1.0, 0.0]]

s4_horizontal_count = 2
s4_vertical_count = 2

#############################################################################

# shape5 Data
s5_box = [[-0.5, 0.5, 0.0],
          [-0.5, -0.5, 0.0],
          [0.5, -0.5, 0.0],
          [0.5, 0.5, 0.0],
          [-0.5, 0.5, 0.0]]

s5_left = [[-0.5, 0.0, 0.0],
           [-1.0, 0.0, 0.0]]

s5_right = [[0.5, 0.0, 0.0],
            [1.0, 0.0, 0.0]]

s5_top = [[0.0, 0.5, 0.0],
          [0.0, 1.0, 0.0]]

s5_bottom = [[0.0, -0.5, 0.0],
             [0.0, -1.0, 0.0]]

s5_box_count = 5
s5_left_count = 2
s5_right_count = 2
s5_top_count = 2
s5_bottom_count = 2

#############################################################################

# shape6 Data
s6_box = [[-0.5, 0.5, 0.0],
          [-0.5, -0.5, 0.0],
          [0.5, -0.5, 0.0],
          [0.5, 0.5, 0.0],
          [-0.5, 0.5, 0.0]]

s6_box_count = 5

#############################################################################

# shape7 Data
s7_box = [[0.0, 1.0, 0.0],
          [-1.0, 0.0, 0.0],
          [0.0, -1.0, 0.0],
          [1.0, 0.0, 0.0],
          [0.0, 1.0, 0.0]]

s7_box_count = 5


class MMMarkerBundleShape(omui.MPxLocatorNode):
    id = om.MTypeId(0x0012F18C)
    drawDbClassification = "drawdb/geometry/MMMarkerBundleShape"
    drawRegistrantId = "MarkerBundleShapeNodePlugin"

    shapes = 0
    line_width = 1.0
    scale = 1.0
    alpha = 1.0

    @staticmethod
    def creator():
        return MMMarkerBundleShape()

    @staticmethod
    def initialize():
        nAttr = om.MFnNumericAttribute()

        # shapes attribute
        MMMarkerBundleShape.shapes = nAttr.create(
            "Shapes", "shapes", om.MFnNumericData.kInt, 1)
        nAttr.setMin(0)
        nAttr.readable = True
        nAttr.writable = True
        nAttr.keyable = False
        nAttr.storable = True
        nAttr.channelBox = True
        MMMarkerBundleShape.addAttribute(MMMarkerBundleShape.shapes)

        # scale attribute
        MMMarkerBundleShape.scale = nAttr.create(
            "Scale", "scale", om.MFnNumericData.kFloat, 1.0)
        nAttr.setMin(0.0)
        nAttr.readable = True
        nAttr.writable = True
        nAttr.keyable = False
        nAttr.storable = True
        nAttr.channelBox = True
        MMMarkerBundleShape.addAttribute(MMMarkerBundleShape.scale)

        # line width attribute
        MMMarkerBundleShape.line_width = nAttr.create(
            "LineWidth", "lw", om.MFnNumericData.kFloat, 1.0)
        nAttr.setMin(1.0)
        nAttr.setMax(10.0)
        nAttr.readable = True
        nAttr.writable = True
        nAttr.keyable = False
        nAttr.storable = True
        nAttr.channelBox = True
        MMMarkerBundleShape.addAttribute(MMMarkerBundleShape.line_width)

        # alpha attribute
        MMMarkerBundleShape.alpha = nAttr.create(
            "Alpha", "alpha", om.MFnNumericData.kFloat, 1.0)
        nAttr.setMin(0.0)
        nAttr.setMax(1.0)
        nAttr.readable = True
        nAttr.writable = True
        nAttr.keyable = False
        nAttr.storable = True
        nAttr.channelBox = True
        MMMarkerBundleShape.addAttribute(MMMarkerBundleShape.alpha)

    def __init__(self):
        omui.MPxLocatorNode.__init__(self)

    def excludeAsLocator(self):
        return False


class MarkerBundleShapeData(om.MUserData):
    def __init__(self):
        # False == don't delete after draw
        do_not_delete_after_draw = False
        om.MUserData.__init__(self, do_not_delete_after_draw)

        self.fColor = om.MColor()

        self.s2_center_left_linesList = om.MPointArray()
        self.s2_center_right_linesList = om.MPointArray()
        self.s2_center_top_linesList = om.MPointArray()
        self.s2_center_bottom_linesList = om.MPointArray()
        self.s2_top_left_linesList = om.MPointArray()
        self.s2_top_right_linesList = om.MPointArray()
        self.s2_bottom_left_linesList = om.MPointArray()
        self.s2_bottom_right_linesList = om.MPointArray()

        self.s3_center_left_linesList = om.MPointArray()
        self.s3_center_right_linesList = om.MPointArray()
        self.s3_center_top_linesList = om.MPointArray()
        self.s3_center_bottom_linesList = om.MPointArray()

        self.s4_horizontal_linesList = om.MPointArray()
        self.s4_vertical_linesList = om.MPointArray()

        self.s5_box_linesList = om.MPointArray()
        self.s5_left_linesList = om.MPointArray()
        self.s5_right_linesList = om.MPointArray()
        self.s5_top_linesList = om.MPointArray()
        self.s5_bottom_linesList = om.MPointArray()

        self.s6_box_linesList = om.MPointArray()

        self.s7_box_linesList = om.MPointArray()


class MarkerBundleShapeDrawOverride(omr.MPxDrawOverride):
    """Viewport 2.0 override implementation"""

    @staticmethod
    def creator(obj):
        return MarkerBundleShapeDrawOverride(obj)

    @staticmethod
    def draw(context, data):
        return

    # By setting isAlwaysDirty to false in MPxDrawOverride constructor, the
    # draw override will be updated (via prepareForDraw()) only when the node
    # is marked dirty via DG evaluation or dirty propagation. Additional
    # callback is also added to explicitly mark the node as being dirty (via
    # MRenderer::setGeometryDrawDirty()) for certain circumstances.
    def __init__(self, obj):
        omr.MPxDrawOverride.__init__(self, obj, None, False)

    def supportedDrawAPIs(self):
        # this plugin supports both GL and DX
        return omr.MRenderer.kAllDevices

    def isBounded(self, obj_path, camera_path):
        return True

    def disableInternalBoundingBoxDraw(self):
        return True

    def prepareForDraw(self, obj_path, camera_path, frameContext, old_data):
        # Get dag node
        global dag_node
        dag_node = obj_path.node()

        self.shapes = om.MPlug(dag_node, MMMarkerBundleShape.shapes).asInt()
        self.scale = om.MPlug(dag_node, MMMarkerBundleShape.scale).asFloat()
        self.line_width = om.MPlug(dag_node, MMMarkerBundleShape.line_width).asFloat()
        self.alpha = om.MPlug(dag_node, MMMarkerBundleShape.alpha).asFloat()

        # Retrieve data cache (create if does not exist)
        data = old_data
        if not isinstance(data, MarkerBundleShapeData):
            data = MarkerBundleShapeData()

        fMultiplier = 0.01 * self.scale
        data.fColor = omr.MGeometryUtilities.wireframeColor(obj_path)

        if self.shapes == 2:
            # Compute data and cache it
            global s2_center_left_count, s2_center_left
            global s2_center_right_count, s2_center_right
            global s2_center_top_count, s2_center_top
            global s2_center_bottom_count, s2_center_bottom
            global s2_top_left_count, s2_top_left
            global s2_top_right_count, s2_top_right
            global s2_bottom_left_count, s2_bottom_left
            global s2_bottom_right_count, s2_bottom_right

            data.s2_center_left_linesList.clear()
            for i in range(s2_center_left_count):
                data.s2_center_left_linesList.append( om.MPoint(s2_center_left[i][0] * fMultiplier, s2_center_left[i][1] * fMultiplier, s2_center_left[i][2] * fMultiplier) )

            data.s2_center_right_linesList.clear()
            for i in range(s2_center_right_count):
                data.s2_center_right_linesList.append( om.MPoint(s2_center_right[i][0] * fMultiplier, s2_center_right[i][1] * fMultiplier, s2_center_right[i][2] * fMultiplier) )

            data.s2_center_top_linesList.clear()
            for i in range(s2_center_top_count):
                data.s2_center_top_linesList.append( om.MPoint(s2_center_top[i][0] * fMultiplier, s2_center_top[i][1] * fMultiplier, s2_center_top[i][2] * fMultiplier) )

            data.s2_center_bottom_linesList.clear()
            for i in range(s2_center_bottom_count):
                data.s2_center_bottom_linesList.append( om.MPoint(s2_center_bottom[i][0] * fMultiplier, s2_center_bottom[i][1] * fMultiplier, s2_center_bottom[i][2] * fMultiplier) )

            data.s2_top_left_linesList.clear()
            for i in range(s2_top_left_count):
                data.s2_top_left_linesList.append( om.MPoint(s2_top_left[i][0] * fMultiplier, s2_top_left[i][1] * fMultiplier, s2_top_left[i][2] * fMultiplier) )

            data.s2_top_right_linesList.clear()
            for i in range(s2_top_right_count):
                data.s2_top_right_linesList.append( om.MPoint(s2_top_right[i][0] * fMultiplier, s2_top_right[i][1] * fMultiplier, s2_top_right[i][2] * fMultiplier) )

            data.s2_bottom_left_linesList.clear()
            for i in range(s2_bottom_left_count):
                data.s2_bottom_left_linesList.append( om.MPoint(s2_bottom_left[i][0] * fMultiplier, s2_bottom_left[i][1] * fMultiplier, s2_bottom_left[i][2] * fMultiplier) )

            data.s2_bottom_right_linesList.clear()
            for i in range(s2_bottom_right_count):
                data.s2_bottom_right_linesList.append( om.MPoint(s2_bottom_right[i][0] * fMultiplier, s2_bottom_right[i][1] * fMultiplier, s2_bottom_right[i][2] * fMultiplier) )

        if self.shapes == 3:
            global s3_center_left_count, s3_center_left
            global s3_center_right_count, s3_center_right
            global s3_center_top_count, s3_center_top
            global s3_center_bottom_count, s3_center_bottom

            data.s3_center_left_linesList.clear()
            for i in range(s3_center_left_count):
                data.s3_center_left_linesList.append( om.MPoint(s3_center_left[i][0] * fMultiplier, s3_center_left[i][1] * fMultiplier, s3_center_left[i][2] * fMultiplier) )

            data.s3_center_right_linesList.clear()
            for i in range(s3_center_right_count):
                data.s3_center_right_linesList.append( om.MPoint(s3_center_right[i][0] * fMultiplier, s3_center_right[i][1] * fMultiplier, s3_center_right[i][2] * fMultiplier) )

            data.s3_center_top_linesList.clear()
            for i in range(s3_center_top_count):
                data.s3_center_top_linesList.append( om.MPoint(s3_center_top[i][0] * fMultiplier, s3_center_top[i][1] * fMultiplier, s3_center_top[i][2] * fMultiplier) )

            data.s3_center_bottom_linesList.clear()
            for i in range(s3_center_bottom_count):
                data.s3_center_bottom_linesList.append( om.MPoint(s3_center_bottom[i][0] * fMultiplier, s3_center_bottom[i][1] * fMultiplier, s3_center_bottom[i][2] * fMultiplier) )

        if self.shapes == 4:
            global s4_horizontal, s4_vertical
            data.s4_horizontal_linesList.clear()
            for i in range(s4_horizontal_count):
                data.s4_horizontal_linesList.append(om.MPoint(s4_horizontal[i][0] * fMultiplier, s4_horizontal[i][1] * fMultiplier, s4_horizontal[i][2] * fMultiplier))

            data.s4_vertical_linesList.clear()
            for i in range(s4_vertical_count):
                data.s4_vertical_linesList.append( om.MPoint(s4_vertical[i][0] * fMultiplier, s4_vertical[i][1] * fMultiplier, s4_vertical[i][2] * fMultiplier) )

        if self.shapes == 5:
            global s5_box, s5_box_count
            global s5_left, s5_left_count
            global s5_right, s5_right_count
            global s5_top, s5_top_count
            global s5_bottom, s5_bottom_count

            data.s5_box_linesList.clear()
            for i in range(s5_box_count):
                data.s5_box_linesList.append( om.MPoint(s5_box[i][0] * fMultiplier, s5_box[i][1] * fMultiplier, s5_box[i][2] * fMultiplier) )

            data.s5_left_linesList.clear()
            for i in range(s5_left_count):
                data.s5_left_linesList.append( om.MPoint(s5_left[i][0] * fMultiplier, s5_left[i][1] * fMultiplier, s5_left[i][2] * fMultiplier) )

            data.s5_right_linesList.clear()
            for i in range(s5_right_count):
                data.s5_right_linesList.append( om.MPoint(s5_right[i][0] * fMultiplier, s5_right[i][1] * fMultiplier, s5_right[i][2] * fMultiplier) )

            data.s5_top_linesList.clear()
            for i in range(s5_top_count):
                data.s5_top_linesList.append( om.MPoint(s5_top[i][0] * fMultiplier, s5_top[i][1] * fMultiplier, s5_top[i][2] * fMultiplier) )

            data.s5_bottom_linesList.clear()
            for i in range(s5_bottom_count):
                data.s5_bottom_linesList.append( om.MPoint(s5_bottom[i][0] * fMultiplier, s5_bottom[i][1] * fMultiplier, s5_bottom[i][2] * fMultiplier) )

        if self.shapes == 6:
            global s6_box, s6_box_count

            data.s6_box_linesList.clear()
            for i in range(s6_box_count):
                data.s6_box_linesList.append( om.MPoint(s6_box[i][0] * fMultiplier, s6_box[i][1] * fMultiplier, s6_box[i][2] * fMultiplier) )

        if self.shapes == 7:
            global s7_box, s7_box_count

            data.s7_box_linesList.clear()
            for i in range(s7_box_count):
                data.s7_box_linesList.append( om.MPoint(s7_box[i][0] * fMultiplier, s7_box[i][1] * fMultiplier, s7_box[i][2] * fMultiplier) )

        return data

    def hasUIDrawables(self):
        return True

    def addUIDrawables(self, obj_path, draw_manager, frame_context, data):
        locatordata = data
        if not isinstance(locatordata, MarkerBundleShapeData):
            return

        draw_manager.beginDrawable()
        color = om.MColor((locatordata.fColor[0],
                           locatordata.fColor[1],
                           locatordata.fColor[2],
                           self.alpha))
        draw_manager.setColor(color)
        draw_manager.setDepthPriority(5)
        draw_manager.setLineWidth(self.line_width)

        if self.shapes == 1:
            draw_manager.setPointSize(2.0 * self.scale)
            draw_manager.point(om.MPoint(0.0, 0.0, 0.0))

        if self.shapes == 2:
            draw_manager.setPointSize(2.5 * self.line_width)
            draw_manager.point(om.MPoint(0.0, 0.0, 0.0))
            draw_manager.mesh(omr.MUIDrawManager.kLineStrip, locatordata.s2_center_left_linesList)
            draw_manager.mesh(omr.MUIDrawManager.kLineStrip, locatordata.s2_center_right_linesList)
            draw_manager.mesh(omr.MUIDrawManager.kLineStrip, locatordata.s2_center_top_linesList)
            draw_manager.mesh(omr.MUIDrawManager.kLineStrip, locatordata.s2_center_bottom_linesList)
            draw_manager.mesh(omr.MUIDrawManager.kLineStrip, locatordata.s2_top_left_linesList)
            draw_manager.mesh(omr.MUIDrawManager.kLineStrip, locatordata.s2_top_right_linesList)
            draw_manager.mesh(omr.MUIDrawManager.kLineStrip, locatordata.s2_bottom_left_linesList)
            draw_manager.mesh(omr.MUIDrawManager.kLineStrip, locatordata.s2_bottom_right_linesList)

        if self.shapes == 3:
            draw_manager.setPointSize(2.5 * self.line_width)
            draw_manager.point(om.MPoint(0.0, 0.0, 0.0))
            draw_manager.mesh(omr.MUIDrawManager.kLineStrip, locatordata.s3_center_left_linesList)
            draw_manager.mesh(omr.MUIDrawManager.kLineStrip, locatordata.s3_center_right_linesList)
            draw_manager.mesh(omr.MUIDrawManager.kLineStrip, locatordata.s3_center_top_linesList)
            draw_manager.mesh(omr.MUIDrawManager.kLineStrip, locatordata.s3_center_bottom_linesList)

        if self.shapes == 4:
            draw_manager.mesh(omr.MUIDrawManager.kLineStrip, locatordata.s4_horizontal_linesList)
            draw_manager.mesh(omr.MUIDrawManager.kLineStrip, locatordata.s4_vertical_linesList)

        if self.shapes == 5:
            draw_manager.setPointSize(2.5 * self.line_width)
            draw_manager.point(om.MPoint(0.0, 0.0, 0.0))
            draw_manager.mesh(omr.MUIDrawManager.kLineStrip, locatordata.s5_box_linesList)
            draw_manager.mesh(omr.MUIDrawManager.kLineStrip, locatordata.s5_left_linesList)
            draw_manager.mesh(omr.MUIDrawManager.kLineStrip, locatordata.s5_right_linesList)
            draw_manager.mesh(omr.MUIDrawManager.kLineStrip, locatordata.s5_top_linesList)
            draw_manager.mesh(omr.MUIDrawManager.kLineStrip, locatordata.s5_bottom_linesList)

        if self.shapes == 6:
            draw_manager.setPointSize(2.5 * self.line_width)
            draw_manager.point(om.MPoint(0.0, 0.0, 0.0))
            draw_manager.setLineStyle(omr.MUIDrawManager.kDashed)
            draw_manager.mesh(omr.MUIDrawManager.kLineStrip, locatordata.s6_box_linesList)

        if self.shapes == 7:
            draw_manager.setPointSize(2.5 * self.line_width)
            draw_manager.point(om.MPoint(0.0, 0.0, 0.0))
            draw_manager.mesh(omr.MUIDrawManager.kLineStrip, locatordata.s7_box_linesList)

        draw_manager.endDrawable()


def initializePlugin(obj):
    plugin = om.MFnPlugin(obj, "mayaMatchMoveSolver", "0.4.0", "Any")
    try:
        plugin.registerNode(
            "mmMarkerBundleShape",
            MMMarkerBundleShape.id,
            MMMarkerBundleShape.creator,
            MMMarkerBundleShape.initialize,
            om.MPxNode.kLocatorNode,
            MMMarkerBundleShape.drawDbClassification)
    except RuntimeError:
        sys.stderr.write("Failed to register node\n")
        raise
    try:
        omr.MDrawRegistry.registerDrawOverrideCreator(
            MMMarkerBundleShape.drawDbClassification,
            MMMarkerBundleShape.drawRegistrantId,
            MarkerBundleShapeDrawOverride.creator)
    except RuntimeError:
        sys.stderr.write("Failed to register override\n")
        raise


def uninitializePlugin(obj):
    plugin = om.MFnPlugin(obj)
    try:
        plugin.deregisterNode(MMMarkerBundleShape.id)
    except RuntimeError:
        sys.stderr.write("Failed to deregister node\n")
        pass
    try:
        omr.MDrawRegistry.deregisterDrawOverrideCreator(
            MMMarkerBundleShape.drawDbClassification,
            MMMarkerBundleShape.drawRegistrantId)
    except RuntimeError:
        sys.stderr.write("Failed to deregister override\n")
        pass
