/*
 * Copyright (C) 2025 David Cattermole.
 *
 * This file is part of mmSolver.
 *
 * mmSolver is free software: you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * mmSolver is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
 * ====================================================================
 *
 * Get a 3D point from the members (objects and components) of an
 * object set node.
 *
 * The following object components are supported:
 * - Mesh Vertex
 * - Mesh Edge
 * - Mesh Face
 */

#include "MMPointFromObjectSetNode.h"

// STL
#include <cmath>
#include <cstring>

// Maya
#include <maya/MDagPath.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MFnCompoundAttribute.h>
#include <maya/MFnMatrixAttribute.h>
#include <maya/MFnMatrixData.h>
#include <maya/MFnMesh.h>
#include <maya/MFnMessageAttribute.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnNumericData.h>
#include <maya/MFnSet.h>
#include <maya/MFnSingleIndexedComponent.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MIntArray.h>
#include <maya/MItMeshEdge.h>
#include <maya/MItMeshPolygon.h>
#include <maya/MItMeshVertex.h>
#include <maya/MItSelectionList.h>
#include <maya/MPlug.h>
#include <maya/MSelectionList.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MTypes.h>

// MM Solver
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/nodeTypeIds.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/number_utils.h"

namespace mmsolver {

// Resolve destination plug into MSelectionList of members
// connected to the plug.
MStatus resolve_destination_plug_into_set_members(const MPlug &plug,
                                                  MSelectionList &outMembers) {
    // When 'true', verbose will print out additional details for
    // debugging.
    const bool verbose = false;

    MStatus status = MS::kSuccess;

    // Reset members if there are any.
    outMembers.clear();

    const bool plugValid = !plug.isNull(&status);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    if (plugValid) {
        MPlug sourcePlug = plug.source(&status);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        const bool sourcePlugValid = !sourcePlug.isNull(&status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        if (sourcePlugValid) {
            MObject node = sourcePlug.node(&status);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            if (!node.isNull()) {
                MFnSet fnSet(node, &status);
                CHECK_MSTATUS_AND_RETURN_IT(status);

                // 'flatten=true' means that all sets that exist
                // inside this set will be expanded into a list of
                // their contents.
                const bool flatten = false;

                status = fnSet.getMembers(outMembers, flatten);
                CHECK_MSTATUS_AND_RETURN_IT(status);

                MMSOLVER_MAYA_VRB(
                    "mmPointFromObjectSet: "
                    "resolve_destination_plug_into_set_members: got "
                    << outMembers.length() << " objects in selection set.");
            }
        }
    }

    if (verbose && !outMembers.isEmpty()) {
        MStringArray selectionArray;
        status = outMembers.getSelectionStrings(selectionArray);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        for (auto i = 0; i < selectionArray.length(); i++) {
            MMSOLVER_MAYA_VRB(
                "mmPointFromObjectSet: "
                "resolve_destination_plug_into_set_members: "
                "selection object=\""
                << selectionArray[i].asChar() << "\"");
        }
    }

    return status;
}

MStatus get_average_point(const MSelectionList &members, double &outPointX,
                          double &outPointY, double &outPointZ) {
    // When 'true', verbose will print out additional details for
    // debugging.
    const bool verbose = false;

    MStatus status = MS::kSuccess;

    // The "grabUVMain.cpp" file is reference here:
    // https://help.autodesk.com/view/MAYAUL/2022/ENU/?guid=Maya_SDK_cpp_ref_grab_u_v_main_8cpp_example_html

    const MSpace::Space space = MSpace::kWorld;

    uint32_t pointCount = 0;

    MDagPath dagPath;
    MObject components;

    for (auto i = 0; i < members.length(); i++) {
        status = members.getDagPath(i, dagPath, components);
        if (!components.isNull()) {
            // If a DAG object has components, that means we should
            // use the positions of the components, not the overall
            // transform.
            continue;
        }

        MMatrix worldMatrix = dagPath.inclusiveMatrix();
        outPointX += worldMatrix(3, 0);  // position X
        outPointY += worldMatrix(3, 1);  // position Y
        outPointZ += worldMatrix(3, 2);  // position Z
        pointCount++;
    }

    // Vertices
    for (MItSelectionList componentIter(members, MFn::kMeshVertComponent);
         !componentIter.isDone(); componentIter.next()) {
        status = componentIter.getDagPath(dagPath, components);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        if (components.isNull()) {
            continue;
        }

        uint32_t count = 0;
        MPoint averagePoint;
        for (MItMeshVertex vertIter(dagPath, components); !vertIter.isDone();
             vertIter.next()) {
            MPoint vertPos = vertIter.position(space, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            averagePoint += vertPos;
            count++;
        }

        if (count > 0) {
            outPointX += averagePoint.x / count;
            outPointY += averagePoint.y / count;
            outPointZ += averagePoint.z / count;
            pointCount++;
        }
    }

    // Faces
    for (MItSelectionList componentIter(members, MFn::kMeshPolygonComponent);
         !componentIter.isDone(); componentIter.next()) {
        status = componentIter.getDagPath(dagPath, components);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        if (components.isNull()) {
            continue;
        }

        uint32_t count = 0;
        MPoint averagePoint;
        for (MItMeshPolygon faceIter(dagPath, components); !faceIter.isDone();
             faceIter.next()) {
            MPoint facePos = faceIter.center(space, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            averagePoint += facePos;
            count++;
        }

        if (count > 0) {
            outPointX += averagePoint.x / count;
            outPointY += averagePoint.y / count;
            outPointZ += averagePoint.z / count;
            pointCount++;
        }
    }

    // Edges
    for (MItSelectionList componentIter(members, MFn::kMeshEdgeComponent);
         !componentIter.isDone(); componentIter.next()) {
        componentIter.getDagPath(dagPath, components);
        if (components.isNull()) {
            continue;
        }

        uint32_t count = 0;
        MPoint averagePoint;
        for (MItMeshEdge edgeIter(dagPath, components); !edgeIter.isDone();
             edgeIter.next()) {
            MPoint edgePos = edgeIter.center(space, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            averagePoint += edgePos;
            count++;
        }

        if (count > 0) {
            outPointX += averagePoint.x / count;
            outPointY += averagePoint.y / count;
            outPointZ += averagePoint.z / count;
            pointCount++;
        }
    }

    MMSOLVER_MAYA_VRB(
        "mmPointFromObjectSet: get_average_point: pointCount=" << pointCount);
    if (pointCount > 0) {
        outPointX = outPointX / pointCount;
        outPointY = outPointY / pointCount;
        outPointZ = outPointZ / pointCount;
    }

    return status;
}

MTypeId MMPointFromObjectSetNode::m_id(MM_POINT_FROM_OBJECT_SET_TYPE_ID);

// Input Attributes
MObject MMPointFromObjectSetNode::a_setNode;
MObject MMPointFromObjectSetNode::a_matrixArray;
MObject MMPointFromObjectSetNode::a_meshArray;

// Output Attributes
MObject MMPointFromObjectSetNode::a_outPoint;
MObject MMPointFromObjectSetNode::a_outPointX;
MObject MMPointFromObjectSetNode::a_outPointY;
MObject MMPointFromObjectSetNode::a_outPointZ;
MObject MMPointFromObjectSetNode::a_outMatrix;

MMPointFromObjectSetNode::MMPointFromObjectSetNode() {}

MMPointFromObjectSetNode::~MMPointFromObjectSetNode() {}

MString MMPointFromObjectSetNode::nodeName() {
    return MString(MM_POINT_FROM_OBJECT_SET_TYPE_NAME);
}

MStatus MMPointFromObjectSetNode::setDependentsDirty(const MPlug &plug,
                                                     MPlugArray &plugArray) {
    MStatus status = MS::kSuccess;

    // Check if any matrix array element changed.
    if (plug.isElement() && plug.array() == a_matrixArray) {
        MPlug outMatrixPlug(thisMObject(), a_outMatrix);
        plugArray.append(outMatrixPlug);
        MPlug outPointPlug(thisMObject(), a_outPoint);
        plugArray.append(outPointPlug);
    }

    // Check if any mesh array element changed.
    if (plug.isElement() && plug.array() == a_meshArray) {
        MPlug outMatrixPlug(thisMObject(), a_outMatrix);
        plugArray.append(outMatrixPlug);
        MPlug outPointPlug(thisMObject(), a_outPoint);
        plugArray.append(outPointPlug);
    }

    // Check if the set node connection changed.
    if (plug == a_setNode) {
        MPlug outMatrixPlug(thisMObject(), a_outMatrix);
        plugArray.append(outMatrixPlug);
        MPlug outPointPlug(thisMObject(), a_outPoint);
        plugArray.append(outPointPlug);
    }

    return MS::kSuccess;
}

MStatus MMPointFromObjectSetNode::compute(const MPlug &plug, MDataBlock &data) {
    // When 'true', verbose will print out additional details for
    // debugging.
    const bool verbose = false;
    MStatus status = MS::kUnknownParameter;

    if ((plug == a_outPoint) || (plug == a_outPointX) ||
        (plug == a_outPointY) || (plug == a_outPointZ) ||
        (plug == a_outPoint) || (plug == a_outPointX) ||
        (plug == a_outPointY) || (plug == a_outPointZ) ||
        (plug == a_outMatrix)) {
        // Query the set node to ensure dirty propagation.
        MDataHandle setNodeHandle = data.inputValue(a_setNode, &status);

        // Query the matrix array to ensure dirty propagation.
        MArrayDataHandle matrixArrayHandle =
            data.inputArrayValue(a_matrixArray, &status);
        if (status == MS::kSuccess) {
            unsigned int matrixCount = matrixArrayHandle.elementCount();
            for (unsigned int i = 0; i < matrixCount; ++i) {
                status = matrixArrayHandle.jumpToArrayElement(i);
                if (status == MS::kSuccess) {
                    MDataHandle matrixHandle =
                        matrixArrayHandle.inputValue(&status);
                    if (status == MS::kSuccess) {
                        MMatrix mat = matrixHandle.asMatrix();
                    }
                }
            }
        }

        // Query the mesh array to ensure dirty propagation.
        MArrayDataHandle meshArrayHandle =
            data.inputArrayValue(a_meshArray, &status);
        if (status == MS::kSuccess) {
            unsigned int meshCount = meshArrayHandle.elementCount();
            for (unsigned int i = 0; i < meshCount; ++i) {
                status = meshArrayHandle.jumpToArrayElement(i);
                if (status == MS::kSuccess) {
                    MDataHandle meshHandle =
                        meshArrayHandle.inputValue(&status);
                    if (status == MS::kSuccess) {
                        MObject meshObj = meshHandle.asMesh();
                    }
                }
            }
        }

        // Outputs
        double outPointX = 0.0;
        double outPointY = 0.0;
        double outPointZ = 0.0;

        MObject thisNode = MPxNode::thisMObject();
        MPlug plug = MPlug(thisNode, a_setNode);

        // Resolve Set attribute into members.
        MSelectionList members;
        status = resolve_destination_plug_into_set_members(plug, members);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        if (!members.isEmpty()) {
            status =
                get_average_point(members, outPointX, outPointY, outPointZ);
            CHECK_MSTATUS_AND_RETURN_IT(status);
        }

        MMSOLVER_MAYA_VRB("mmPointFromObjectSet: pointX=" << outPointX);
        MMSOLVER_MAYA_VRB("mmPointFromObjectSet: pointY=" << outPointY);
        MMSOLVER_MAYA_VRB("mmPointFromObjectSet: pointZ=" << outPointZ);

        // Row-major matrix layout.
        const double outMatrixRaw[4][4] = {
            {1.0, 0.0, 0.0, 0.0},
            {0.0, 1.0, 0.0, 0.0},
            {0.0, 0.0, 1.0, 0.0},
            {outPointX, outPointY, outPointZ, 1.0}};
        MMatrix outMatrix(outMatrixRaw);

        // Output Point
        MDataHandle outPointXHandle = data.outputValue(a_outPointX);
        MDataHandle outPointYHandle = data.outputValue(a_outPointY);
        MDataHandle outPointZHandle = data.outputValue(a_outPointZ);
        outPointXHandle.setDouble(outPointX);
        outPointYHandle.setDouble(outPointY);
        outPointZHandle.setDouble(outPointZ);
        outPointXHandle.setClean();
        outPointYHandle.setClean();
        outPointZHandle.setClean();

        // Output Matrix
        MDataHandle outMatrixHandle = data.outputValue(a_outMatrix);
        outMatrixHandle.setMMatrix(outMatrix);
        outMatrixHandle.setClean();

        status = MS::kSuccess;
    }

    return status;
}

void *MMPointFromObjectSetNode::creator() {
    return (new MMPointFromObjectSetNode());
}

MStatus MMPointFromObjectSetNode::initialize() {
    MStatus status;
    MFnNumericAttribute numericAttr;
    MFnMatrixAttribute matrixAttr;
    MFnCompoundAttribute compoundAttr;
    MFnMessageAttribute msgAttr;
    MFnTypedAttribute typedAttr;

    {
        // Set node.
        //
        // The Set message attribute is expected to be connected to a
        // valid set node. The members of the set node are used to
        // evaluate the transform output of this node.
        a_setNode = msgAttr.create("set", "set", &status);
        CHECK_MSTATUS(status);
        CHECK_MSTATUS(msgAttr.setStorable(true));
        CHECK_MSTATUS(msgAttr.setConnectable(true));
        CHECK_MSTATUS(addAttribute(a_setNode));

        // The "matrix" and "mesh" attributes are intended to allow
        // the Maya DAG to automatically update for changes to the
        // input objects in the Set.
        //
        // This means that the objects in the Set, need to be
        // connected do the mmPointFromObjectSet node in two different
        // ways. This is unfortunate, but seems to be necessary, if we
        // want to have "real-time" updates, and we want to avoid
        // installing/uninstalling callbacks.

        // Matrices.
        //
        // These are used to enable dirty-propagation, so the node
        // updates when matrices of input objects are changed.
        a_matrixArray = matrixAttr.create("matrix", "mat",
                                          MFnMatrixAttribute::kDouble, &status);
        CHECK_MSTATUS(status);
        CHECK_MSTATUS(matrixAttr.setReadable(true));
        CHECK_MSTATUS(matrixAttr.setConnectable(true));
        CHECK_MSTATUS(matrixAttr.setArray(true));
        CHECK_MSTATUS(addAttribute(a_matrixArray));

        // Meshes.
        //
        // These are used to enable dirty-propagation, so the node
        // updates when mesh of input objects are changed.
        a_meshArray = typedAttr.create("mesh", "msh", MFnData::kMesh,
                                       MObject::kNullObj, &status);
        CHECK_MSTATUS(status);
        CHECK_MSTATUS(typedAttr.setReadable(true));
        CHECK_MSTATUS(typedAttr.setConnectable(true));
        CHECK_MSTATUS(typedAttr.setArray(true));
        CHECK_MSTATUS(addAttribute(a_meshArray));
    }

    /////////////////////////////////////////////////////////////////////////

    {
        // Out Point X
        a_outPointX = numericAttr.create("outPointX", "opx",
                                         MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(false));
        CHECK_MSTATUS(numericAttr.setKeyable(false));
        CHECK_MSTATUS(numericAttr.setReadable(true));
        CHECK_MSTATUS(numericAttr.setWritable(false));

        // Out Point Y
        a_outPointY = numericAttr.create("outPointY", "opy",
                                         MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(false));
        CHECK_MSTATUS(numericAttr.setKeyable(false));
        CHECK_MSTATUS(numericAttr.setReadable(true));
        CHECK_MSTATUS(numericAttr.setWritable(false));

        // Out Point Z
        a_outPointZ = numericAttr.create("outPointZ", "opz",
                                         MFnNumericData::kDouble, 0.0, &status);
        CHECK_MSTATUS(status);
        CHECK_MSTATUS(numericAttr.setStorable(false));
        CHECK_MSTATUS(numericAttr.setKeyable(false));
        CHECK_MSTATUS(numericAttr.setReadable(true));
        CHECK_MSTATUS(numericAttr.setWritable(false));

        // Out Point (parent of outPoint* attributes)
        a_outPoint = compoundAttr.create("outPoint", "op", &status);
        CHECK_MSTATUS(status);
        compoundAttr.addChild(a_outPointX);
        compoundAttr.addChild(a_outPointY);
        compoundAttr.addChild(a_outPointZ);
        CHECK_MSTATUS(addAttribute(a_outPoint));
    }

    //////////////////////////////////////////////////////////////////////////

    {
        // Out Matrix (camera-space)
        a_outMatrix = matrixAttr.create("outMatrix", "omt",
                                        MFnMatrixAttribute::kDouble, &status);
        CHECK_MSTATUS(status);
        CHECK_MSTATUS(matrixAttr.setStorable(false));
        CHECK_MSTATUS(matrixAttr.setKeyable(false));
        CHECK_MSTATUS(matrixAttr.setReadable(true));
        CHECK_MSTATUS(matrixAttr.setWritable(false));
        CHECK_MSTATUS(addAttribute(a_outMatrix));
    }

    //////////////////////////////////////////////////////////////////////////

    // Attribute Affects
    MObjectArray inputAttrs;
    inputAttrs.append(a_setNode);
    inputAttrs.append(a_matrixArray);
    inputAttrs.append(a_meshArray);

    MObjectArray outputAttrs;
    outputAttrs.append(a_outPoint);
    outputAttrs.append(a_outPointX);
    outputAttrs.append(a_outPointY);
    outputAttrs.append(a_outPointZ);
    outputAttrs.append(a_outMatrix);

    CHECK_MSTATUS(
        MMNodeInitUtils::attributeAffectsMulti(inputAttrs, outputAttrs));

    return MS::kSuccess;
}

}  // namespace mmsolver
