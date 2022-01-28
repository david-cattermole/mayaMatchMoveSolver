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
 * Command for running mmSolver.
 */

// Internal
#include "common_arg_flags.h"
#include "MMSolverCmd.h"
#include "adjust/adjust_data.h"
#include "adjust/adjust_base.h"

// STL
#include <cmath>
#include <cassert>
#include <cstdlib>
#include <algorithm>

// Utils
#include "utilities/debug_utils.h"

// Maya
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MFnDependencyNode.h>

// Internal Objects
#include "mayahelper/maya_utils.h"
#include "mayahelper/maya_attr.h"
#include "mayahelper/maya_marker.h"
#include "mayahelper/maya_bundle.h"
#include "mayahelper/maya_camera.h"


void createSolveObjectSyntax(MSyntax &syntax) {
    syntax.addFlag(CAMERA_FLAG, CAMERA_FLAG_LONG,
                   MSyntax::kString, MSyntax::kString);
    syntax.addFlag(MARKER_FLAG, MARKER_FLAG_LONG,
                   MSyntax::kString, MSyntax::kString, MSyntax::kString);
    syntax.addFlag(ATTR_FLAG, ATTR_FLAG_LONG,
                   MSyntax::kString,
                   MSyntax::kString, MSyntax::kString,
                   MSyntax::kString, MSyntax::kString);

    syntax.makeFlagMultiUse(CAMERA_FLAG);
    syntax.makeFlagMultiUse(MARKER_FLAG);
    syntax.makeFlagMultiUse(ATTR_FLAG);
    return;
}


MStatus parseSolveObjectArguments(const MArgDatabase &argData,
                                  CameraPtrList      &out_cameraList,
                                  MarkerPtrList      &out_markerList,
                                  BundlePtrList      &out_bundleList,
                                  AttrPtrList        &out_attrList) {
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
                MMSOLVER_ERR("Camera argument list must have 2 arguments; "
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
                MMSOLVER_ERR("Marker argument list must have 3 arguments; "
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
                MMSOLVER_ERR("Given marker node is not a Marker; "
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
                MMSOLVER_ERR("Given camera node is not a Camera; "
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
                MMSOLVER_ERR("Given bundle node is not a Bundle; "
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
                MMSOLVER_ERR("Camera shape name was not given with marker. "
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
                if (out_markerList[j]->getNodeName() == markerName) {
                    MMSOLVER_ERR("Marker name cannot be specified more than once. "
                        << "markerName=" << markerName);
                }
            }
            MarkerPtr marker = MarkerPtr(new Marker());
            marker->setNodeName(markerName);
            marker->setBundle(bundle);
            marker->setCamera(camera);

            out_markerList.push_back(marker);
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
                MMSOLVER_ERR("Attribute argument list must have 5 argument; "
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

            out_attrList.push_back(attr);
            MPlug attrPlug = attr->getPlug();
        }
    }

    return status;
}


void createAttributeDetailsSyntax(MSyntax &syntax) {
    syntax.addFlag(STIFFNESS_FLAG, STIFFNESS_FLAG_LONG,
                   MSyntax::kString,
                   MSyntax::kString,
                   MSyntax::kString,
                   MSyntax::kString);
    syntax.addFlag(SMOOTHNESS_FLAG, SMOOTHNESS_FLAG_LONG,
                   MSyntax::kString,
                   MSyntax::kString,
                   MSyntax::kString,
                   MSyntax::kString);

    syntax.makeFlagMultiUse(STIFFNESS_FLAG);
    syntax.makeFlagMultiUse(SMOOTHNESS_FLAG);
    return;
}


MStatus parseAttributeDetailsArguments(const MArgDatabase &argData,
                                       const AttrPtrList   attrList,
                                       StiffAttrsPtrList  &out_stiffAttrsList,
                                       SmoothAttrsPtrList &out_smoothAttrsList) {
    MStatus status = MStatus::kSuccess;

    out_stiffAttrsList.clear();
    out_smoothAttrsList.clear();

    // Get Stiffness Values
    unsigned int stiffnessNum = argData.numberOfFlagUses(STIFFNESS_FLAG);
    for (unsigned int i = 0; i < stiffnessNum; ++i) {
        MArgList stiffnessArgs;
        status = argData.getFlagArgumentList(STIFFNESS_FLAG, i, stiffnessArgs);
        if (status == MStatus::kSuccess) {
            if (stiffnessArgs.length() != 4) {
                MMSOLVER_ERR("Attribute Stiffness argument list must have 4 argument; "
                            << "\"node.attribute\", "
                            << "\"node.attributeStiffWeight\", "
                            << "\"node.attributeStiffVariance\", "
                            << "\"node.attributeStiffValue\".");
                continue;
            }

            // Find the already created Attribute.
            MString nodeAttrName = stiffnessArgs.asString(0);
            AttrPtr foundAttr;
            int foundIndex = 0;
            for (AttrPtrListCIt ait = attrList.cbegin();
                 ait != attrList.cend();
                 ++ait) {
                AttrPtr attr = *ait;
                if (nodeAttrName == attr->getName()) {
                    foundAttr = attr;
                    break;
                }
                foundIndex++;
            }
            if (foundAttr->getName() == ".") {
                MMSOLVER_ERR("Attribute Stiffness name is not a declared attribute; "
                            << nodeAttrName);
                continue;
            }
            AttrPtr stiffWeightAttr = AttrPtr(new Attr());
            MString weightNodeAttrName = stiffnessArgs.asString(1);
            stiffWeightAttr->setName(weightNodeAttrName);

            AttrPtr stiffVarianceAttr = AttrPtr(new Attr());
            MString varianceNodeAttrName = stiffnessArgs.asString(2);
            stiffVarianceAttr->setName(varianceNodeAttrName);

            AttrPtr stiffValueAttr = AttrPtr(new Attr());
            MString valueNodeAttrName = stiffnessArgs.asString(3);
            stiffValueAttr->setName(valueNodeAttrName);

            StiffAttrsPtr stiffAttrs = StiffAttrsPtr(new StiffAttrs());
            stiffAttrs->attrIndex = foundIndex;
            stiffAttrs->weightAttr = stiffWeightAttr;
            stiffAttrs->varianceAttr = stiffVarianceAttr;
            stiffAttrs->valueAttr = stiffValueAttr;

            out_stiffAttrsList.push_back(stiffAttrs);
        }
    }

    // Get Smoothness Values
    unsigned int smoothnessNum = argData.numberOfFlagUses(SMOOTHNESS_FLAG);
    for (unsigned int i = 0; i < smoothnessNum; ++i) {
        MArgList smoothnessArgs;
        status = argData.getFlagArgumentList(SMOOTHNESS_FLAG, i, smoothnessArgs);
        if (status == MStatus::kSuccess) {
            if (smoothnessArgs.length() != 4) {
                MMSOLVER_ERR("Attribute Smoothness argument list must have 4 argument; "
                            << "\"node.attribute\", "
                            << "\"node.attributeSmoothWeight\", "
                            << "\"node.attributeSmoothVariance\", "
                            << "\"node.attributeSmoothValue\".");
                continue;
            }

            // Find the already created Attribute.
            MString nodeAttrName = smoothnessArgs.asString(0);
            AttrPtr foundAttr;
            int foundIndex = 0;
            for (AttrPtrListCIt ait = attrList.cbegin();
                 ait != attrList.cend();
                 ++ait) {
                AttrPtr attr = *ait;
                if (nodeAttrName == attr->getName()) {
                    foundAttr = attr;
                    break;
                }
                foundIndex++;
            }
            if (foundAttr->getName() == ".") {
                MMSOLVER_ERR("Attribute Smoothness name is not a declared attribute; "
                            << nodeAttrName);
                continue;
            }
            AttrPtr smoothWeightAttr = AttrPtr(new Attr());
            MString weightNodeAttrName = smoothnessArgs.asString(1);
            smoothWeightAttr->setName(weightNodeAttrName);

            AttrPtr smoothVarianceAttr = AttrPtr(new Attr());
            MString varianceNodeAttrName = smoothnessArgs.asString(2);
            smoothVarianceAttr->setName(varianceNodeAttrName);

            AttrPtr smoothValueAttr = AttrPtr(new Attr());
            MString valueNodeAttrName = smoothnessArgs.asString(3);
            smoothValueAttr->setName(valueNodeAttrName);

            SmoothAttrsPtr smoothAttrs = SmoothAttrsPtr(new SmoothAttrs());
            smoothAttrs->attrIndex = foundIndex;
            smoothAttrs->weightAttr = smoothWeightAttr;
            smoothAttrs->varianceAttr = smoothVarianceAttr;
            smoothAttrs->valueAttr = smoothValueAttr;

            out_smoothAttrsList.push_back(smoothAttrs);
        }
    }

    return status;
}


void createSolveFramesSyntax(MSyntax &syntax) {
    syntax.addFlag(FRAME_FLAG, FRAME_FLAG_LONG,
                   MSyntax::kLong);
    syntax.makeFlagMultiUse(FRAME_FLAG);
    return;
}


MStatus parseSolveFramesArguments(const MArgDatabase &argData,
                                  MTimeArray         &out_frameList) {
    MStatus status = MStatus::kSuccess;

    // Get 'Frames'
    out_frameList.clear();
    MTime::Unit unit = MTime::uiUnit();
    unsigned int framesNum = argData.numberOfFlagUses(FRAME_FLAG);
    for (unsigned int i = 0; i < framesNum; ++i) {
        MArgList frameArgs;
        status = argData.getFlagArgumentList(FRAME_FLAG, i, frameArgs);
        if (status == MStatus::kSuccess) {
            if (frameArgs.length() != 1) {
                MMSOLVER_ERR("Attribute argument list must have 1 argument; \"frame\".");
                continue;
            }
            int value = frameArgs.asInt(0, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            MTime frame = MTime((double) value, unit);
            out_frameList.append(frame);
        }
    }

    // Make sure we have a frame list.
    if (out_frameList.length() == 0) {
        status = MS::kFailure;
        status.perror("Frame List length is 0, must have a frame to solve.");
    }

    return status;
}
