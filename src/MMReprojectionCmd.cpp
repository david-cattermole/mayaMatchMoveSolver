/*
 * Copyright (C) 2019 David Cattermole.
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
 * Command for running mmReprojection.
 */


// Internal
#include <MMReprojectionCmd.h>
#include <mmSolver.h>
#include <mayaUtils.h>
#include <Camera.h>
#include <reprojection.h>

// STL
#include <cmath>
#include <cassert>
// #include <cstdlib>  // getenv

// Utils
#include <utilities/debugUtils.h>
#include <utilities/stringUtils.h>

// Maya
#include <maya/MSyntax.h>
#include <maya/MArgList.h>
#include <maya/MArgDatabase.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MDagPath.h>
#include <maya/MFnDependencyNode.h>



MMReprojectionCmd::~MMReprojectionCmd() {}

void *MMReprojectionCmd::creator() {
    return new MMReprojectionCmd();
}

MString MMReprojectionCmd::cmdName() {
    return MString("mmReprojection");
}

/*
 * Tell Maya we have a syntax function.
 */
bool MMReprojectionCmd::hasSyntax() const {
    return true;
}

bool MMReprojectionCmd::isUndoable() const {
    return false;
}

/*
 * Add flags to the command syntax
 */
MSyntax MMReprojectionCmd::newSyntax() {
    MSyntax syntax;
    syntax.enableQuery(false);
    syntax.enableEdit(false);

    unsigned int minNumObjects = 1;
    syntax.setObjectType(MSyntax::kSelectionList, minNumObjects);

    // Flags
    syntax.addFlag(CAMERA_FLAG, CAMERA_FLAG_LONG, MSyntax::kString, MSyntax::kString);
    syntax.addFlag(TIME_FLAG, TIME_FLAG_LONG, MSyntax::kDouble);
    syntax.addFlag(WORLD_POINT_FLAG, WORLD_POINT_FLAG_LONG, MSyntax::kBoolean);
    syntax.addFlag(NORM_COORD_FLAG, NORM_COORD_FLAG_LONG, MSyntax::kBoolean);

    syntax.makeFlagMultiUse(TIME_FLAG);

    return syntax;
}

/*
 * Parse command line arguments
 */
MStatus MMReprojectionCmd::parseArgs(const MArgList &args) {
    MStatus status = MStatus::kSuccess;

    MArgDatabase argData(syntax(), args, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    // Get World Point flag
    m_asWorldPoint = false;
    bool worldPointFlagIsSet = argData.isFlagSet(WORLD_POINT_FLAG, &status);
    if (worldPointFlagIsSet == true) {
        status = argData.getFlagArgument(WORLD_POINT_FLAG, 0, m_asWorldPoint);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    // Get Normalized Coordinate flag
    m_asNormalizedCoordinate = false;
    bool normCoordFlagIsSet = argData.isFlagSet(NORM_COORD_FLAG, &status);
    if (normCoordFlagIsSet == true) {
        status = argData.getFlagArgument(NORM_COORD_FLAG, 0, m_asNormalizedCoordinate);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    // Get Transforms
    m_nodeList.clear();
    status = argData.getObjects(m_nodeList);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    if (m_nodeList.length() == 0) {
        ERR("No objects given!");
        status = MStatus::kFailure;
        return status;
    }

    // Get Time
    unsigned int timeNum = argData.numberOfFlagUses(TIME_FLAG);
    if (timeNum == 0) {
        ERR("No times flags given. Time values are required.");
        status = MStatus::kFailure;
        return status;
    }
    m_timeList.clear();
    MTime::Unit unit = MTime::uiUnit();
    MArgList argList;
    for (unsigned int i = 0; i < timeNum; ++i) {
        status = argData.getFlagArgumentList(TIME_FLAG, i, argList);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        double tmp = argList.asDouble(i, &status);
        MTime time(tmp, unit);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        m_timeList.append(time);
    }
    if (m_timeList.length() == 0) {
        ERR("No time values to query.");
        status = MStatus::kFailure;
        return status;
    }

    // Get Camera
    bool cameraFlagIsSet = argData.isFlagSet(CAMERA_FLAG, &status);
    if (cameraFlagIsSet == false) {
        ERR("\'camera\' flag was not given, but is required!");
        status = MStatus::kFailure;
        return status;
    }
    MString cameraTransform = "";
    MString cameraShape = "";
    MArgList cameraArgs;
    status = argData.getFlagArgumentList(CAMERA_FLAG, 0, cameraArgs);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    if (cameraArgs.length() != 2) {
        ERR("\'camera\' flag must have 2 arguments; "
            << "\"cameraTransform\", \"cameraShape\".");
        status = MStatus::kFailure;
        return status;
    }

    cameraTransform = cameraArgs.asString(0, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    nodeExistsAndIsType(cameraTransform, MFn::Type::kTransform);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    m_camera.setTransformNodeName(cameraTransform);

    cameraShape = cameraArgs.asString(1, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    nodeExistsAndIsType(cameraShape, MFn::Type::kCamera);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    m_camera.setShapeNodeName(cameraShape);

    return status;
}


MStatus MMReprojectionCmd::doIt(const MArgList &args) {
//
//  Description:
//    implements the MEL mmReprojection command.
//
//  Arguments:
//    argList - the argument list that was passes to the command from MEL
//
//  Return Value:
//    MStatus::kSuccess - command succeeded
//    MStatus::kFailure - command failed (returning this value will cause the
//                     MEL script that is being run to terminate unless the
//                     error is caught using a "catch" statement.
//
    MStatus status = MStatus::kSuccess;
    
    // Command Outputs
    MDoubleArray outWorldPointResult;
    MDoubleArray outNormCoordResult;

    // Read all the flag arguments.
    status = parseArgs(args);
    if (status == MStatus::kFailure) {
        return status;
    }

    // Flush the query cache for the camera.
    m_camera.clearAuxilaryAttrsCache();
    m_camera.clearProjMatrixCache();
    m_camera.clearWorldProjMatrixCache();
    m_camera.clearAttrValueCache();

    // Camera
    double focalLength = 35;
    double horizontalFilmAperture = 1;
    double verticalFilmAperture = 1;
    double horizontalFilmOffset = 0;
    double verticalFilmOffset = 0;
    short filmFit = 1;
    double nearClipPlane = 0.1;
    double farClipPlane = 1000;
    double cameraScale = 1;

    // Image
    double imageWidth = 1024;
    double imageHeight = 1024;

    // Manipulation
    MMatrix applyMatrix;
    bool overrideScreenX = false;
    bool overrideScreenY = false;
    bool overrideScreenZ = false;
    double screenX = 0;
    double screenY = 0;
    double screenZ = 0;
    double depthScale = 1.0;

    // Reprojection Outputs
    double outCoordX;
    double outCoordY;
    double outNormCoordX;
    double outNormCoordY;
    double outPixelX;
    double outPixelY;
    bool outInsideFrustum;
    double outPointX;
    double outPointY;
    double outPointZ;
    double outWorldPointX;
    double outWorldPointY;
    double outWorldPointZ;
    MMatrix outMatrix;
    MMatrix outWorldMatrix;
    MMatrix outCameraProjectionMatrix;
    MMatrix outInverseCameraProjectionMatrix;
    MMatrix outWorldCameraProjectionMatrix;
    MMatrix outWorldInverseCameraProjectionMatrix;
    double outHorizontalPan;
    double outVerticalPan;

    Attr cameraMatrixAttr = m_camera.getMatrixAttr();
    for (unsigned int i = 0; i < m_nodeList.length(); ++i) {
        MDagPath dagPath;
        status = m_nodeList.getDagPath(i, dagPath);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        MString nodeNamePath = dagPath.fullPathName(&status);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        Attr tfmMatrixAttr;
        tfmMatrixAttr.setNodeName(nodeNamePath);
        tfmMatrixAttr.setAttrName("worldMatrix");
        for (unsigned int j = 0; j < m_timeList.length(); ++j) {
            MTime time = m_timeList[j];

            MMatrix camMatrix;
            MMatrix tfmMatrix;
            status = cameraMatrixAttr.getValue(camMatrix, time);
            status = tfmMatrixAttr.getValue(tfmMatrix, time);

            // Possibly Animated
            focalLength = m_camera.getFocalLengthValue(time);
            horizontalFilmAperture = m_camera.getFilmbackWidthValue(time);
            verticalFilmAperture = m_camera.getFilmbackHeightValue(time);
            horizontalFilmOffset = m_camera.getFilmbackOffsetXValue(time);
            verticalFilmOffset = m_camera.getFilmbackOffsetYValue(time);

            // Assumed to not be animated.
            farClipPlane = m_camera.getFarClipPlaneValue();
            cameraScale = m_camera.getCameraScaleValue();
            filmFit = m_camera.getFilmFitValue();
            imageWidth = m_camera.getRenderWidthValue();
            imageHeight = m_camera.getRenderHeightValue();

            // Query the reprojection.
            status = reprojection(
                    tfmMatrix,
                    camMatrix,

                    // Camera
                    focalLength,
                    horizontalFilmAperture,
                    verticalFilmAperture,
                    horizontalFilmOffset,
                    verticalFilmOffset,
                    filmFit,
                    nearClipPlane,
                    farClipPlane,
                    cameraScale,

                    // Image
                    imageWidth,
                    imageHeight,

                    // Manipulation
                    applyMatrix,
                    overrideScreenX,
                    overrideScreenY,
                    overrideScreenZ,
                    screenX,
                    screenY,
                    screenZ,
                    depthScale,

                    // Outputs
                    outCoordX, outCoordY,
                    outNormCoordX, outNormCoordY,
                    outPixelX, outPixelY,
                    outInsideFrustum,
                    outPointX, outPointY, outPointZ,
                    outWorldPointX, outWorldPointY, outWorldPointZ,
                    outMatrix,
                    outWorldMatrix,
                    outCameraProjectionMatrix,
                    outInverseCameraProjectionMatrix,
                    outWorldCameraProjectionMatrix,
                    outWorldInverseCameraProjectionMatrix,
                    outHorizontalPan,
                    outVerticalPan);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            if (m_asWorldPoint == true) {
                outWorldPointResult.append(outWorldPointX);
                outWorldPointResult.append(outWorldPointY);
                outWorldPointResult.append(outWorldPointZ);
            }
            if (m_asNormalizedCoordinate == true) {            
                outNormCoordResult.append(outNormCoordX);
                outNormCoordResult.append(outNormCoordY);
            }
        }
    }
    
    if (m_asWorldPoint == true) {
        MMReprojectionCmd::setResult(outWorldPointResult);
    }

    if (m_asNormalizedCoordinate == true) {
        MMReprojectionCmd::setResult(outNormCoordResult);
    }
    return status;
}
