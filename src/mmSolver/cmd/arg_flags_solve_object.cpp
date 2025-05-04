/*
 * Copyright (C) 2018, 2019 David Cattermole.
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

#include "arg_flags_solve_object.h"

// Maya
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MArgParser.h>
#include <maya/MObject.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MSyntax.h>

// Internal Objects
#include "mmSolver/adjust/adjust_data.h"
#include "mmSolver/mayahelper/maya_attr.h"
#include "mmSolver/mayahelper/maya_attr_list.h"
#include "mmSolver/mayahelper/maya_bundle.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_marker.h"
#include "mmSolver/mayahelper/maya_marker_group.h"
#include "mmSolver/mayahelper/maya_marker_list.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/utilities/debug_utils.h"

namespace mmsolver {

void createSolveObjectSyntax(MSyntax &syntax) {
    syntax.addFlag(CAMERA_FLAG, CAMERA_FLAG_LONG, MSyntax::kString,
                   MSyntax::kString);
    syntax.addFlag(MARKER_FLAG, MARKER_FLAG_LONG, MSyntax::kString,
                   MSyntax::kString, MSyntax::kString);
    syntax.addFlag(ATTR_FLAG, ATTR_FLAG_LONG, MSyntax::kString,
                   MSyntax::kString, MSyntax::kString, MSyntax::kString,
                   MSyntax::kString);

    syntax.makeFlagMultiUse(CAMERA_FLAG);
    syntax.makeFlagMultiUse(MARKER_FLAG);
    syntax.makeFlagMultiUse(ATTR_FLAG);
    return;
}

MStatus createMarkerGroupFromMarkerNodeName(const MString &markerName,
                                            MarkerGroupPtr &out_markerGroup) {
    const bool verbose = false;

    MDagPath node_path;
    MStatus status = getAsDagPath(markerName, node_path);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    MObject node_obj;
    while (node_path.length() > 1) {
        status = node_path.pop(1);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        node_obj = node_path.node(&status);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        ObjectType obj_type = computeObjectType(node_obj, node_path);
        if (obj_type == ObjectType::kMarkerGroup) {
            MString markerGroupNodeName = node_path.fullPathName(&status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            out_markerGroup = MarkerGroupPtr(new MarkerGroup());
            out_markerGroup->setNodeName(markerGroupNodeName);
        }
    }
    if (!out_markerGroup) {
        MMSOLVER_MAYA_VRB(
            "createMarkerGroupFromMarkerNodeName: No MarkerGroup node found "
            "for \""
            << markerName.asChar() << "\".");
    }
    return status;
}

MStatus parseSolveObjectArguments(const MArgDatabase &argData,
                                  CameraPtrList &out_cameraList,
                                  MarkerList &out_markerList,
                                  BundlePtrList &out_bundleList,
                                  AttrList &out_attrList) {
    MStatus status = MStatus::kSuccess;

    out_cameraList.clear();
    out_markerList.clear();
    out_bundleList.clear();

    // Get 'Camera'
    MString cameraTransform = "";
    MString cameraShape = "";
    unsigned int cameraNum = argData.numberOfFlagUses(CAMERA_FLAG);
    for (unsigned int i = 0; i < cameraNum; ++i) {
        MArgList cameraArgs;
        status = argData.getFlagArgumentList(CAMERA_FLAG, i, cameraArgs);
        if (status == MStatus::kSuccess) {
            if (cameraArgs.length() != 2) {
                MMSOLVER_MAYA_ERR("Camera argument list must have 2 arguments; "
                                  << "\"cameraTransform\", \"cameraShape\".");
                continue;
            }

            cameraTransform = cameraArgs.asString(0, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            nodeExistsAndIsType(cameraTransform, MFn::Type::kTransform);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            cameraShape = cameraArgs.asString(1, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            nodeExistsAndIsType(cameraShape, MFn::Type::kCamera);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            CameraPtr camera = CameraPtr(new Camera());
            camera->setTransformNodeName(cameraTransform);
            camera->setShapeNodeName(cameraShape);
            out_cameraList.push_back(camera);
        }
    }

    // Get 'Markers'
    ObjectType objectType = ObjectType::kUnknown;
    MDagPath dagPath;
    MString markerName = "";
    MString cameraName = "";
    MString bundleName = "";
    MObject markerObject;
    MObject cameraObject;
    MObject bundleObject;
    unsigned int markerNum = argData.numberOfFlagUses(MARKER_FLAG);
    for (unsigned int i = 0; i < markerNum; ++i) {
        MArgList markerArgs;
        status = argData.getFlagArgumentList(MARKER_FLAG, i, markerArgs);
        if (status == MStatus::kSuccess) {
            if (markerArgs.length() != 3) {
                MMSOLVER_MAYA_ERR(
                    "Marker argument list must have 3 arguments; "
                    << "\"marker\", \"cameraShape\",  \"bundle\".");
                continue;
            }

            markerName = markerArgs.asString(0, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            status = getAsObject(markerName, markerObject);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            status = getAsDagPath(markerName, dagPath);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            objectType = computeObjectType(markerObject, dagPath);
            if (objectType != ObjectType::kMarker) {
                MMSOLVER_MAYA_ERR("Given marker node is not a Marker; "
                                  << markerName.asChar());
                continue;
            }

            cameraName = markerArgs.asString(1, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            status = getAsObject(cameraName, cameraObject);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            status = getAsDagPath(cameraName, dagPath);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            objectType = computeObjectType(cameraObject, dagPath);
            if (objectType != ObjectType::kCamera) {
                MMSOLVER_MAYA_ERR("Given camera node is not a Camera; "
                                  << cameraName.asChar());
                continue;
            }

            bundleName = markerArgs.asString(2, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            status = getAsObject(bundleName, bundleObject);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            status = getAsDagPath(bundleName, dagPath);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            objectType = computeObjectType(bundleObject, dagPath);
            if (objectType != ObjectType::kBundle) {
                MMSOLVER_MAYA_ERR("Given bundle node is not a Bundle; "
                                  << bundleName.asChar());
                continue;
            }

            // Camera
            CameraPtr camera = CameraPtr(new Camera());
            for (unsigned int j = 0; j < out_cameraList.size(); ++j) {
                if (out_cameraList[j]->getShapeNodeName() == cameraName) {
                    camera = out_cameraList[j];
                    break;
                }
            }
            if (camera->getShapeNodeName() == "") {
                MMSOLVER_MAYA_ERR(
                    "Camera shape name was not given with marker. "
                    << "marker=" << markerName << " "
                    << "camera=" << cameraName << " "
                    << "bundle=" << bundleName);
            }
            // TODO: Print warnings if any of the following attributes
            // on the camera are animated/connected:
            //
            // - camera.horizontalFilmAperture
            // - camera.verticalFilmAperture
            // - camera.nearClippingPlane
            // - camera.farClippingPlane
            // - camera.cameraScale
            // - camera.filmFit

            // Bundle
            BundlePtr bundle = BundlePtr(new Bundle());
            for (unsigned int j = 0; j < out_bundleList.size(); ++j) {
                if (out_bundleList[j]->getNodeName() == bundleName) {
                    bundle = out_bundleList[j];
                    break;
                }
            }
            if (bundle->getNodeName() == "") {
                bundle->setNodeName(bundleName);
            }

            // Marker
            for (unsigned int j = 0; j < out_markerList.size(); ++j) {
                MarkerPtr marker = out_markerList.get_marker(j);
                if (marker->getNodeName() == markerName) {
                    MMSOLVER_MAYA_ERR(
                        "Marker name cannot be specified more than once. "
                        << "markerName=" << markerName);
                }
            }
            MarkerPtr marker = MarkerPtr(new Marker());
            marker->setNodeName(markerName);
            marker->setBundle(bundle);
            marker->setCamera(camera);

            // Get Marker Group (if it exists), if not the MarkerGroup
            // pointer will be empty.
            MarkerGroupPtr markerGroup;
            status =
                createMarkerGroupFromMarkerNodeName(markerName, markerGroup);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            marker->setMarkerGroup(markerGroup);

            out_markerList.push_back(marker, /*enabled=*/true);
            out_bundleList.push_back(bundle);
        }
    }

    // Get 'Attributes'
    out_attrList.clear();
    unsigned int attrsNum = argData.numberOfFlagUses(ATTR_FLAG);
    for (unsigned int i = 0; i < attrsNum; ++i) {
        MArgList attrArgs;
        status = argData.getFlagArgumentList(ATTR_FLAG, i, attrArgs);
        if (status == MStatus::kSuccess) {
            if (attrArgs.length() != 5) {
                MMSOLVER_MAYA_ERR(
                    "Attribute argument list must have 5 argument; "
                    << "\"node.attribute\", "
                    << "\"min\", \"max\", "
                    << "\"offset\", \"scale\".");
                continue;
            }

            // TODO: Print errors and exit with failure if any of the
            // following attributes are detected:
            //
            // - camera.horizontalFilmAperture
            // - camera.verticalFilmAperture
            // - camera.nearClippingPlane
            // - camera.farClippingPlane
            // - camera.cameraScale
            // - camera.filmFit
            // - defaultResolution.width
            // - defaultResolution.height
            // - defaultResolution.deviceAspectRatio

            AttrPtr attr = AttrPtr(new Attr());
            MString nodeAttrName = attrArgs.asString(0);
            attr->setName(nodeAttrName);

            // Get Min/Max attribute values
            MString minValueStr = attrArgs.asString(1);
            MString maxValueStr = attrArgs.asString(2);
            if (minValueStr.isDouble()) {
                attr->setMinimumValue(minValueStr.asDouble());
            }
            if (maxValueStr.isDouble()) {
                attr->setMaximumValue(maxValueStr.asDouble());
            }

            // Add an internal offset value used to make sure values
            // are not at 0.0.
            MString offsetValueStr = attrArgs.asString(3);
            if (offsetValueStr.isDouble()) {
                attr->setOffsetValue(offsetValueStr.asDouble());
            }

            // Add an internal scale value.
            //
            // TODO: Get the node this attribute is connected to. If
            // it's a DAG node we must query the position, then create
            // a function to scale down attributes farther away from
            // camera. Issue #26.
            MString scaleValueStr = attrArgs.asString(4);
            if (scaleValueStr.isDouble()) {
                attr->setScaleValue(scaleValueStr.asDouble());
            }

            out_attrList.push_back(attr, /*enabled=*/true);
            MPlug attrPlug = attr->getPlug();
        }
    }

    return status;
}

}  // namespace mmsolver
