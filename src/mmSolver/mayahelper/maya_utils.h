/*
 * Copyright (C) 2018, 2019, 2021 David Cattermole.
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
 * Miscellaneous Maya utilities, related to objects and selection, etc.
 */


#ifndef MAYA_UTILS_H
#define MAYA_UTILS_H

// STL
#include <vector>

// Maya
#include <maya/MStatus.h>
#include <maya/MColor.h>
#include <maya/MDistance.h>
#include <maya/MPoint.h>
#include <maya/MVector.h>
#include <maya/MMatrix.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MObject.h>
#include <maya/MObjectArray.h>
#include <maya/MDagPath.h>
#include <maya/MPlug.h>
#include <maya/MDataHandle.h>
#include <maya/MSelectionList.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MPxNode.h>

// MM Solver
#include "mmSolver/utilities/debug_utils.h"

#define MMSOLVER_OBJECT_TYPE_UNKNOWN      (0)
#define MMSOLVER_OBJECT_TYPE_ATTRIBUTE    (1)
#define MMSOLVER_OBJECT_TYPE_MARKER       (2)
#define MMSOLVER_OBJECT_TYPE_BUNDLE       (3)
#define MMSOLVER_OBJECT_TYPE_CAMERA       (4)
#define MMSOLVER_OBJECT_TYPE_IMAGE_PLANE  (5)
#define MMSOLVER_OBJECT_TYPE_MARKER_GROUP (6)
#define MMSOLVER_OBJECT_TYPE_COLLECTION   (7)
#define MMSOLVER_OBJECT_TYPE_LINE         (8)
#define MMSOLVER_OBJECT_TYPE_LENS         (9)


enum class ObjectType
{
    kUnknown = MMSOLVER_OBJECT_TYPE_UNKNOWN,
    kAttribute = MMSOLVER_OBJECT_TYPE_ATTRIBUTE,
    kMarker = MMSOLVER_OBJECT_TYPE_MARKER,
    kBundle = MMSOLVER_OBJECT_TYPE_BUNDLE,
    kCamera = MMSOLVER_OBJECT_TYPE_CAMERA,
    kImagePlane = MMSOLVER_OBJECT_TYPE_IMAGE_PLANE,
    kMarkerGroup = MMSOLVER_OBJECT_TYPE_MARKER_GROUP,
    kCollection = MMSOLVER_OBJECT_TYPE_COLLECTION,
    kLine = MMSOLVER_OBJECT_TYPE_LINE,
    kLens = MMSOLVER_OBJECT_TYPE_LENS,
};


MStatus getAsSelectionList(
    const MStringArray &nodeNames,
    MSelectionList &selList);


MStatus getAsSelectionList(
    const MString nodeName,
    MSelectionList &selList);


MStatus nodeExistsAndIsType(
    const MString &nodeName,
    const MFn::Type nodeType);


MStatus getAsObject(
    const MString &nodeName,
    MObject &object);


MStatus getAsDagPath(
    const MString &nodeName,
    MDagPath &nodeDagPath);


bool hasAttrName(
    MFnDependencyNode &dependFn,
    const MString &attrName);


// Analogous to the Python function "mmSolver.api.get_object_type()"
ObjectType computeObjectType(
    const MObject &node_obj,
    // If 'nodeDagPath' given, assumed to be the node's MDagPath.
    MDagPath &nodeDagPath);
ObjectType computeObjectType(const MObject &node_obj);

// Generate attribute name used to set and look up 'attribute affects'
// on nodes.
MStatus constructAttrAffectsName(
    const MString attrName,
    const MString attrUuidStr,
    MString &outAttrName);


namespace mmsolver {

static inline
MStatus getNodeAttr(const MDagPath &objPath,
                    const MObject &attr,
                    MDistance &value) {
    MStatus status;
    MObject node = objPath.node(&status);
    if (status) {
        MPlug plug(node, attr);
        if (!plug.isNull()) {
            status = plug.getValue(value);
            return status;
        }
    }
    return status;
}

static inline
MStatus getNodeAttr(const MDagPath &objPath,
                    const MObject &attr,
                    bool &value) {
    MStatus status;
    MObject node = objPath.node(&status);
    if (status) {
        MPlug plug(node, attr);
        if (!plug.isNull()) {
            value = plug.asBool();
            return status;
        }
    }
    return status;
}

static inline
MStatus getNodeAttr(const MDagPath &objPath,
                    const MObject &attr,
                    int32_t &value) {
    MStatus status;
    MObject node = objPath.node(&status);
    if (status) {
        MPlug plug(node, attr);
        if (!plug.isNull()) {
            value = plug.asInt();
            return status;
        }
    }
    return status;
}

static inline
MStatus getNodeAttr(const MDagPath &objPath,
                    const MObject &attr,
                    uint32_t &value) {
    MStatus status;
    MObject node = objPath.node(&status);
    if (status) {
        MPlug plug(node, attr);
        if (!plug.isNull()) {
            value = static_cast<uint32_t>(plug.asInt());
            return status;
        }
    }
    return status;
}

static inline
MStatus getNodeAttr(const MDagPath &objPath,
                    const MObject &attr,
                    short &value) {
    MStatus status;
    MObject node = objPath.node(&status);
    if (status) {
        MPlug plug(node, attr);
        if (!plug.isNull()) {
            value = plug.asShort();
            return status;
        }
    }
    return status;
}

static inline
MStatus getNodeAttr(const MDagPath &objPath,
                    const MObject &attr,
                    float &value) {
    MStatus status;
    MObject node = objPath.node(&status);
    if (status) {
        MPlug plug(node, attr);
        if (!plug.isNull()) {
            value = plug.asFloat();
            return status;
        }
    }
    return status;
}

static inline
MStatus getNodeAttr(const MDagPath &objPath,
                    const MObject &attr,
                    double &value) {
    MStatus status;
    MObject node = objPath.node(&status);
    if (status) {
        MPlug plug(node, attr);
        if (!plug.isNull()) {
            value = plug.asDouble();
            return status;
        }
    }
    return status;
}

static inline
MStatus getNodeAttr(const MDagPath &objPath,
                    const MObject &attr,
                    MColor &value) {
    MStatus status;
    MObject node = objPath.node(&status);
    if (status) {
        MPlug plug(node, attr);
        if (!plug.isNull()) {
            MDataHandle data_handle = plug.asMDataHandle(&status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            auto data = data_handle.asFloat3();
            value.r = data[0];
            value.g = data[1];
            value.b = data[2];
            return status;
        }
    }
    return status;
}

static inline
MStatus getNodeAttr(const MDagPath &objPath,
                    const MObject &attr,
                    MMatrix &value) {
    MStatus status;
    MObject node = objPath.node(&status);
    if (status) {
        MPlug plug(node, attr);
        if (!plug.isNull()) {
            MDataHandle data_handle = plug.asMDataHandle(&status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            value = data_handle.asMatrix();
            return status;
        }
    }
    return status;
}

static inline
MStatus getNodeAttr(const MDagPath &objPath,
                    const MObject &attr,
                    MString &value) {
    MStatus status;
    MObject node = objPath.node(&status);
    if (status) {
        MPlug plug(node, attr);
        if (!plug.isNull()) {
            auto data = plug.asString(&status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            value = data;
            return status;
        }
    }
    return status;
}

} // namespace mmsolver

// Static attributes to help with Maya Node initialization.
class MMNodeInitUtils {
  public:

    // Create 'MPxNode::attributeAffects' relationships for nodes, using
    // lists of attributes, rather than each relationship taking up one
    // line.
    static MStatus attributeAffectsMulti(
            const MObjectArray &inputAttrs,
            const MObjectArray &outputAttrs);
};

#endif // MAYA_UTILS_H
