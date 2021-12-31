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

#include <vector>

// Utils
#include <utilities/debugUtils.h>

// Maya
#include <maya/MStatus.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MObject.h>
#include <maya/MObjectArray.h>
#include <maya/MDagPath.h>
#include <maya/MPlug.h>
#include <maya/MSelectionList.h>
#include <maya/MFnDependencyNode.h>


#define OBJECT_TYPE_UNKNOWN      (0)
#define OBJECT_TYPE_ATTRIBUTE    (1)
#define OBJECT_TYPE_MARKER       (2)
#define OBJECT_TYPE_BUNDLE       (3)
#define OBJECT_TYPE_CAMERA       (4)
#define OBJECT_TYPE_IMAGE_PLANE  (5)
#define OBJECT_TYPE_MARKER_GROUP (6)
#define OBJECT_TYPE_COLLECTION   (7)


enum class ObjectType
{
    kUnknown = OBJECT_TYPE_UNKNOWN,
    kAttribute = OBJECT_TYPE_ATTRIBUTE,
    kMarker = OBJECT_TYPE_MARKER,
    kBundle = OBJECT_TYPE_BUNDLE,
    kCamera = OBJECT_TYPE_CAMERA,
    kImagePlane = OBJECT_TYPE_IMAGE_PLANE,
    kMarkerGroup = OBJECT_TYPE_MARKER_GROUP,
    kCollection = OBJECT_TYPE_COLLECTION,
};


MStatus getAsSelectionList(
    const MStringArray &nodeNames,
    MSelectionList &selList);


MStatus getAsSelectionList(
    const MString nodeName,
    MSelectionList &selList);


MStatus nodeExistsAndIsType(
    const MString nodeName,
    const MFn::Type nodeType);


MStatus getAsObject(
    const MString nodeName,
    MObject &object);


MStatus getAsDagPath(
    const MString nodeName,
    MDagPath &nodeDagPath);

bool hasAttrName(
    MFnDependencyNode &dependFn,
    const MString attrName);


// Analogous to the Python function "mmSolver.api.get_object_type()"
ObjectType computeObjectType(
    const MObject node_obj,
    MDagPath &nodeDagPath);


// Generate attribute name used to set and look up 'attribute affects'
// on nodes.
MStatus constructAttrAffectsName(
    const MString attrName,
    const MString attrUuidStr,
    MString &outAttrName);

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
