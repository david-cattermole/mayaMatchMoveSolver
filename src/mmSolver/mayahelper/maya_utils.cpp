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
 */

#include "maya_utils.h"

// Maya
#include <maya/MDagPath.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MObject.h>
#include <maya/MObjectArray.h>
#include <maya/MPlug.h>
#include <maya/MPlugArray.h>
#include <maya/MPxNode.h>
#include <maya/MSelectionList.h>
#include <maya/MStatus.h>
#include <maya/MStreamUtils.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>

MStatus MMNodeInitUtils::attributeAffectsMulti(
    const MObjectArray &inputAttrs, const MObjectArray &outputAttrs) {
    MStatus status = MS::kSuccess;
    for (unsigned int i = 0; i < inputAttrs.length(); i++) {
        for (unsigned int j = 0; j < outputAttrs.length(); j++) {
            MObject inputAttr = inputAttrs[i];
            MObject outputAttr = outputAttrs[j];
            status = MPxNode::attributeAffects(inputAttr, outputAttr);
            if (status != MS::kSuccess) {
                MMSOLVER_MAYA_ERR(
                    "MMNodeInitUtils::attributeAffects: Failed at "
                    << "input_index=" << i << " output_index=" << j);
                CHECK_MSTATUS(status);
            }
        }
    }
    return status;
}

MStatus getAsSelectionList(const MStringArray &nodeNames,
                           MSelectionList &selList, bool quiet) {
    MStatus status;
    for (unsigned int i = 0; i < nodeNames.length(); ++i) {
        status = selList.add(nodeNames[i]);
        if (!quiet) {
            CHECK_MSTATUS(status);
        }
        if (status != MS::kSuccess) {
            return status;
        }
    }
    if (selList.length() != nodeNames.length()) {
        status = MStatus::kFailure;
        status.perror("getAsSelectionList failed");
    }
    return status;
}

MStatus getAsSelectionList(const MString &nodeName, MSelectionList &selList,
                           bool quiet) {
    MStringArray nodeNames;
    nodeNames.append(nodeName);
    return getAsSelectionList(nodeNames, selList, quiet);
}

MStatus nodeExistsAndIsType(const MString &nodeName, const MFn::Type nodeType) {
    MStatus status;
    MSelectionList selList;
    selList.clear();

    status = getAsSelectionList(nodeName, selList);
    if (status != MS::kSuccess) {
        MMSOLVER_MAYA_ERR("Node does not exist; " << nodeName);
    }
    CHECK_MSTATUS_AND_RETURN_IT(status);

    MObject nodeObj;
    status = selList.getDependNode(0, nodeObj);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    if (nodeObj.apiType() != nodeType) {
        MMSOLVER_MAYA_ERR("Node type is not correct;"
                          << " node=" << nodeName << " type=" << nodeType);
        status = MS::kFailure;
        status.perror("Node Type is not correct");
        return status;
    }
    return status;
}

MStatus getAsObject(const MString &nodeName, MObject &object, bool quiet) {
    MStatus status;
    MSelectionList selList;
    status = getAsSelectionList(nodeName, selList, quiet);
    if (!quiet) {
        CHECK_MSTATUS(status);
    }
    if (status != MS::kSuccess) {
        return status;
    }

    if (selList.length() == 1) {
        status = selList.getDependNode(0, object);
        if (!quiet) {
            CHECK_MSTATUS(status);
        }
    }
    return status;
}

MStatus getAsDagPath(const MString &nodeName, MDagPath &nodeDagPath) {
    MStatus status;
    MSelectionList selList;
    status = getAsSelectionList(nodeName, selList);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    if (selList.length() == 1) {
        status = selList.getDagPath(0, nodeDagPath);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }
    return status;
}

MStatus getUniqueNodeName(MObject &node, MString &out_uniqueNodeName) {
    MDagPath dagPath;
    MStatus status = MDagPath::getAPathTo(node, dagPath);
    if (status == MS::kSuccess) {
        out_uniqueNodeName = dagPath.fullPathName();
    } else {
        MFnDependencyNode fnDependNode(node, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        out_uniqueNodeName = fnDependNode.name(&status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    return status;
}

bool hasAttrName(MFnDependencyNode &dependFn, const MString &attrName) {
    MStatus status = MStatus::kSuccess;
    auto network_plug = true;
    MPlug plug = dependFn.findPlug(attrName, network_plug, &status);
    CHECK_MSTATUS(status);
    return !plug.isNull();
}

ObjectType computeDgObjectType(const MObject &node_obj) {
    ObjectType objectType = ObjectType::kUnknown;

    MStatus status = MStatus::kSuccess;
    MFnDependencyNode dependFn(node_obj, &status);
    CHECK_MSTATUS(status);
    if (status != MS::kSuccess) {
        return objectType;
    }

    bool node_is_lens = false;
    const MString base_node_type_name("mmLensModel");
    const int char_index_start = 0;
    const int char_index_end = 10;
    const MString node_type = dependFn.typeName();
    if (node_type.length() >= char_index_end) {
        const MString start_string =
            node_type.substringW(char_index_start, char_index_end);
        node_is_lens = start_string == base_node_type_name;
    }

    if (node_is_lens) {
        objectType = ObjectType::kLens;
    }

    return objectType;
}

ObjectType computeDagObjectType(const MObject &node_obj,
                                MDagPath &nodeDagPath) {
    MStatus status = MStatus::kSuccess;
    ObjectType objectType = ObjectType::kUnknown;

    // TODO: Add support for detecting ObjectType::kLine objects.

    MFn::Type node_tid = nodeDagPath.apiType();
    bool hasTransformNode = (node_tid == MFn::kTransform) ||
                            (node_tid == MFn::kPluginTransformNode);

    bool hasLocatorShape = false;
    bool hasCameraShape = false;
    bool hasImagePlaneShape = false;
    auto childNodeDagPath = MDagPath();
    unsigned int num_children = nodeDagPath.childCount();
    for (unsigned int i = 0; i < num_children; ++i) {
        MObject child_obj = nodeDagPath.child(i);
        status = MDagPath::getAPathTo(child_obj, childNodeDagPath);
        CHECK_MSTATUS(status);
        if (status != MS::kSuccess) {
            return objectType;
        }

        MFn::Type shape_tid = childNodeDagPath.apiType();
        if (shape_tid == MFn::kLocator ||
            shape_tid == MFn::kPluginLocatorNode) {
            hasLocatorShape = true;
        } else if (shape_tid == MFn::kCamera) {
            hasCameraShape = true;
        } else if (shape_tid == MFn::kImagePlane) {
            hasImagePlaneShape = true;
        }
    }

    MFnDependencyNode dependFn(node_obj, &status);
    CHECK_MSTATUS(status);
    if (status != MS::kSuccess) {
        return objectType;
    }

    const auto attrNameEnable = MString("enable");
    const auto attrNameWeight = MString("weight");
    const auto attrNameBundle = MString("bundle");
    const auto attrNameDepth = MString("depth");
    const auto attrNameOverscanX = MString("overscanX");
    const auto attrNameOverscanY = MString("overscanY");
    const auto attrNameSolverList = MString("solverList");
    const bool hasAttrEnable = hasAttrName(dependFn, attrNameEnable);
    const bool hasAttrWeight = hasAttrName(dependFn, attrNameWeight);
    const bool hasAttrBundle = hasAttrName(dependFn, attrNameBundle);
    const bool hasAttrDepth = hasAttrName(dependFn, attrNameDepth);
    const bool hasAttrOverscanX = hasAttrName(dependFn, attrNameOverscanX);
    const bool hasAttrOverscanY = hasAttrName(dependFn, attrNameOverscanY);
    const bool hasAttrSolverList = hasAttrName(dependFn, attrNameSolverList);
    if (hasTransformNode && hasLocatorShape && hasAttrEnable && hasAttrWeight &&
        hasAttrBundle) {
        objectType = ObjectType::kMarker;
    } else if (hasTransformNode && hasAttrDepth && hasAttrOverscanX &&
               hasAttrOverscanY) {
        objectType = ObjectType::kMarkerGroup;
    } else if (hasTransformNode && hasLocatorShape) {
        objectType = ObjectType::kBundle;
    } else if (hasTransformNode && hasCameraShape) {
        objectType = ObjectType::kCamera;
    } else if (node_tid == MFn::kCamera) {
        objectType = ObjectType::kCamera;
    } else if (hasTransformNode && hasImagePlaneShape) {
        objectType = ObjectType::kImagePlane;
    } else if (hasImagePlaneShape) {
        objectType = ObjectType::kImagePlane;
    } else if (node_tid == MFn::kSet && hasAttrSolverList) {
        objectType = ObjectType::kCollection;
    }
    return objectType;
}

// Analogous to the Python function "mmSolver.api.get_object_type()"
ObjectType computeObjectType(
    const MObject &node_obj,
    MDagPath &nodeDagPath  // If given, assumed to be the node's MDagPath.
) {
    ObjectType objectType = ObjectType::kUnknown;

    if (node_obj.isNull() || !nodeDagPath.isValid()) {
        MMSOLVER_MAYA_ERR(
            "computeObjectType: Given node is null or not valid!");
        return objectType;
    }

    if (node_obj.hasFn(MFn::kDagNode)) {
        objectType = computeDagObjectType(node_obj, nodeDagPath);
    } else if (node_obj.hasFn(MFn::kDependencyNode)) {
        objectType = computeDgObjectType(node_obj);
    } else {
        MMSOLVER_MAYA_ERR(
            "computeObjectType: node_obj is not a DG or DAG compatible "
            "object.");
    }

    return objectType;
}

ObjectType computeObjectType(const MObject &node_obj) {
    ObjectType objectType = ObjectType::kUnknown;

    if (node_obj.isNull()) {
        MMSOLVER_MAYA_ERR("computeObjectType: Given node is null!");
        return objectType;
    }

    if (node_obj.hasFn(MFn::kDagNode)) {
        MDagPath nodeDagPath;
        MStatus status = MDagPath::getAPathTo(node_obj, nodeDagPath);
        if (status != MS::kSuccess) {
            MMSOLVER_MAYA_ERR(
                "computeObjectType: node_obj is not a DAG compatible object.");
            return objectType;
        }
        objectType = computeDagObjectType(node_obj, nodeDagPath);
    } else if (node_obj.hasFn(MFn::kDependencyNode)) {
        objectType = computeDgObjectType(node_obj);
    } else {
        MMSOLVER_MAYA_ERR(
            "computeObjectType: node_obj is not a DG or DAG compatible "
            "object.");
    }

    return objectType;
}

MStatus constructAttrAffectsName(const MString &attrName,
                                 const MString &attrUuidStr,
                                 MString &outAttrName) {
    const MString attrNamePrefix = "node_";
    const MString attrNameSuffix = "_attr_";

    MString attrSubstitute(attrName);
    MStatus status = attrSubstitute.substitute(".", "_");
    CHECK_MSTATUS_AND_RETURN_IT(status);

    outAttrName =
        attrNamePrefix + attrUuidStr + attrNameSuffix + attrSubstitute;
    status = outAttrName.substitute("-", "_");
    CHECK_MSTATUS_AND_RETURN_IT(status);
    return status;
}

namespace mmsolver {

MStatus get_connected_node(const MPlug &plug, MObject &out_node) {
    MStatus status = MS::kSuccess;
    if (!plug.isNull() && plug.isConnected()) {
        MPlugArray connected_plugs;
        bool as_src = false;
        bool as_dst = true;
        plug.connectedTo(connected_plugs, as_dst, as_src, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        if (connected_plugs.length() == 1) {
            MPlug connected_plug = connected_plugs[0];
            out_node = connected_plug.node();
        }
    }
    return status;
}

MStatus get_position_from_connected_node(const MPlug &plug, double &x,
                                         double &y, double &z) {
    MObject connected_node;
    MStatus status = get_connected_node(plug, connected_node);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    if (!connected_node.isNull()) {
        MDagPath dag_path;
        MDagPath::getAPathTo(connected_node, dag_path);

        MMatrix matrix = dag_path.inclusiveMatrix(&status);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        x = matrix[3][0];
        y = matrix[3][1];
        z = matrix[3][2];
    }
    return status;
}

}  // namespace mmsolver
