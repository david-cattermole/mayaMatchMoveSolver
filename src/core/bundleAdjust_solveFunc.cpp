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
 * The universal solving function, works with any solver.
 *
 * The functions contain the essential core of a minimization solver.
 */

// cminpack
#ifdef USE_SOLVER_CMINPACK
#include <cminpack.h>
#endif

// Lev-Mar
#ifdef USE_SOLVER_LEVMAR
#include <levmar.h>
#endif

// STL
#include <ctime>
#include <cmath>
#include <iostream>
#include <string>
#include <vector>
#include <cassert>
#include <limits>
#include <algorithm>
#include <math.h>
#include <stdio.h>

// Standard Utils
#include <utilities/debugUtils.h>
#include <utilities/stringUtils.h>

// Maya
#include <maya/MVector.h>
#include <maya/MPoint.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MObject.h>
#include <maya/MSelectionList.h>
#include <maya/MDagPath.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MFnAnimCurve.h>
#include <maya/MAnimCurveChange.h>
#include <maya/MMatrix.h>
#include <maya/MComputation.h>
#include <maya/MProfiler.h>
#include <maya/MGlobal.h>

// Solver Utilities
#include <mayaUtils.h>
#include <Camera.h>
#include <Attr.h>

// Local solvers
#include <core/bundleAdjust_base.h>
#include <core/bundleAdjust_data.h>
#include <core/bundleAdjust_solveFunc.h>
#include <core/bundleAdjust_cminpack_base.h>
#include <core/bundleAdjust_levmar_bc_dif.h>


// NOTE: There is a very strange bug in Maya. After setting a number
// of plug values using a DG Context, when quering plug values at the
// same times, the values do not evaluate correctly. To 'trick' Maya
// into triggering an eval the next time a plug is queried we query
// the matrix of a marker node. It doesn't matter which marker node,
// however it does matter that it's a marker node, if the eval is
// performed with a bundle node the error continues to happen.
#define FORCE_TRIGGER_EVAL 1


// Allows us to test (internally), the experimental delta value
// calculation.
// #define USE_EXPERIMENTAL_DELTA_VALUE


#if MAYA_API_VERSION < 201700
int getStringArrayIndexOfValue(MStringArray &array, MString &value) {
    int index = -1;
    for (unsigned int i=0; i<array.length(); ++i) {
        if (array[i] == value) {
            index = i;
            break;
        }
    }
    return index;
}
#endif


/*
 * Generate a 'dgdirty' MEL command listing all nodes that may be
 * changed by our solve function.
 */
MString generateDirtyCommand(int numberOfMarkerErrors, SolverData *ud) {
    MString dgDirtyCmd = "dgdirty ";
    MStringArray dgDirtyNodeNames;
    for (int i = 0; i < (numberOfMarkerErrors / ERRORS_PER_MARKER); ++i) {
        IndexPair markerPair = ud->errorToMarkerList[i];

        MarkerPtr marker = ud->markerList[markerPair.first];
        MString markerName = marker->getNodeName();
#if MAYA_API_VERSION >= 201700
        const int markerName_idx = dgDirtyNodeNames.indexOf(markerName);
#else
        const int markerName_idx = getStringArrayIndexOfValue(dgDirtyNodeNames, markerName);
#endif
        if (markerName_idx == -1) {
            dgDirtyCmd += " \"" + markerName + "\" ";
            dgDirtyNodeNames.append(markerName);
        }

        CameraPtr camera = marker->getCamera();
        MString cameraTransformName = camera->getTransformNodeName();
        MString cameraShapeName = camera->getShapeNodeName();
#if MAYA_API_VERSION >= 201700
        const int cameraTransformName_idx = dgDirtyNodeNames.indexOf(cameraTransformName);
#else
        const int cameraTransformName_idx = getStringArrayIndexOfValue(dgDirtyNodeNames, cameraTransformName);
#endif
        if (cameraTransformName_idx == -1) {
            dgDirtyCmd += " \"" + cameraTransformName + "\" ";
            dgDirtyNodeNames.append(cameraTransformName);
        }
#if MAYA_API_VERSION >= 201700
        const int cameraShapeName_idx = dgDirtyNodeNames.indexOf(cameraShapeName);
#else
        const int cameraShapeName_idx =  getStringArrayIndexOfValue(dgDirtyNodeNames, cameraShapeName);
#endif
        if (cameraShapeName_idx == -1) {
            dgDirtyCmd += " \"" + cameraShapeName + "\" ";
            dgDirtyNodeNames.append(cameraShapeName);
        }

        BundlePtr bundle = marker->getBundle();
        MString bundleName = bundle->getNodeName();
#if MAYA_API_VERSION >= 201700
        const int bundleName_idx = dgDirtyNodeNames.indexOf(bundleName);
#else
        const int bundleName_idx = getStringArrayIndexOfValue(dgDirtyNodeNames, bundleName);
#endif
        if (bundleName_idx == -1) {
            dgDirtyCmd += " \"" + bundleName + "\" ";
            dgDirtyNodeNames.append(bundleName);
        }
    }
    dgDirtyCmd += ";";
    return dgDirtyCmd;
}


#ifdef USE_EXPERIMENTAL_DELTA_VALUE
double getDeltaTransformTranslate(MString nodeName,
                                  CameraPtr cam,
                                  MTime frame,
                                  double imageWidth,
                                  MPoint axis) {
    const double deltaWidth = 1.0;

    // Bundle Translate or Transform Translate
    double filmBackWidth = cam->getFilmbackWidthValue(frame);
    double filmBackHeight = cam->getFilmbackHeightValue(frame);
    double filmBackInvAspect = filmBackHeight / filmBackWidth;

    // Get bundle world matrix
    BundlePtr bnd = BundlePtr(new Bundle());
    bnd->setNodeName(nodeName);

    MMatrix camProjWorldMatrix;
    cam->getWorldProjMatrix(camProjWorldMatrix, frame);

    MMatrix worldMatrix;
    bnd->getMatrix(worldMatrix, frame);

    // Create a new vector along the translate axis (x = (1, 0, 0))
    MPoint point_current;
    bnd->getPos(point_current);
    MPoint point_new(axis);

    // Turn this vector into world space - we now have an axis
    // pointing along the translate axis.
    point_current = point_current * worldMatrix;
    point_new = point_new * worldMatrix;

    // Measure the screen-space position at bundle world pos.
    point_current = point_current * camProjWorldMatrix;
    point_current.cartesianize();
    point_current[0] *= 0.5;
    point_current[1] *= 0.5 * filmBackInvAspect;

    // Measure the screen-space position at bundle world pos plus
    // translate axis.
    point_new = point_new * camProjWorldMatrix;
    point_new.cartesianize();
    point_new[0] *= 0.5;
    point_new[1] *= 0.5 * filmBackInvAspect;

    // Compute the screen-space distance between two points.
    double d = distance_2d(point_current, point_new) * imageWidth;
    d = deltaWidth / d;

    // Use this screen-space distance as the delta.
//    WRN("delta node" << nodeName << "d=" << d);
    return d;
}
#endif // USE_EXPERIMENTAL_DELTA_VALUE


// Given a specific parameter, calculate the expected 'delta' value of
// the parameter.
//
// To do this calculation, we should take into account the type of
// attribute this parameter points to. For example, for a
// 'bundle.translateX' we know the direction (in screen-space) this
// attribute will move in, and we can calculate how far the attribute
// value will move, if the bundle is moved forward by '1 percent' of
// the camera's FOV. Calculating this '1 percent' per-parameter will
// give us a sense of how much to move each parameter to get a
// screen-space-"uniform" deviation. A bundle attribute axis that is
// pointed away from the camera will need to move much farther than an
// attribute axis pointed orthogonal to the camera's direction.
double calculateParameterDelta(double value,
                               double delta,
                               double sign,
                               AttrPtr attr,
                               CameraPtr cam,
                               MTime frame,
                               double imageWidth) {
    MStatus status = MS::kSuccess;

    double xmin = attr->getMinimumValue();
    double xmax = attr->getMaximumValue();

#ifdef USE_EXPERIMENTAL_DELTA_VALUE
    // Determine the attribute 'type'.
    unsigned int object_type = attr->getObjectType();
    unsigned int attr_type = attr->getSolverAttrType();

    bool has_min = xmin > (-std::numeric_limits<float>::max());
    bool has_max = xmax < std::numeric_limits<float>::max();

    MDagPath nodeDagPath;
    getAsDagPath(attr->getNodeName(), nodeDagPath);
    MString nodeName = nodeDagPath.fullPathName();
//    WRN("nodeName: " << nodeName
//        << " attr: " << attr->getAttrName()
//        << " attr_type: " << attr_type
//        << " object_type: " << object_type);

    // Switch based on attribute type.
    MPoint axis_tx(1.0, 0.0, 0.0);
    MPoint axis_ty(0.0, 1.0, 0.0);
    MPoint axis_tz(0.0, 0.0, 1.0);
    if (has_min && has_max) {
        // Attribute with min/max values.
        // Use a specific ratio, such as 0.1 percent.
        delta = std::abs(xmax - xmin) * 0.001;
    } else if (attr_type == ATTR_SOLVER_TYPE_BUNDLE_TX) {
        delta = 0.0001;
//        delta = getDeltaTransformTranslate(
//                nodeName, cam, frame,
//                imageWidth, axis_tx);
    } else if (attr_type == ATTR_SOLVER_TYPE_BUNDLE_TY) {
        delta = 0.0001;
//        delta = getDeltaTransformTranslate(
//                nodeName, cam, frame,
//                imageWidth, axis_ty);
    } else if (attr_type == ATTR_SOLVER_TYPE_BUNDLE_TZ) {
        delta = 0.0001;
//        delta = getDeltaTransformTranslate(
//                nodeName, cam, frame,
//                imageWidth, axis_tz);
    } else if (attr_type == ATTR_SOLVER_TYPE_CAMERA_TX) {
        delta = 0.0001;
//        delta = getDeltaTransformTranslate(
//                nodeName, cam, frame,
//                imageWidth, axis_tx);
    } else if (attr_type == ATTR_SOLVER_TYPE_CAMERA_TY) {
        delta = 0.0001;
//        delta = getDeltaTransformTranslate(
//                nodeName, cam, frame,
//                imageWidth, axis_ty);
    } else if (attr_type == ATTR_SOLVER_TYPE_CAMERA_TZ) {
        delta = 0.0001;
//        delta = getDeltaTransformTranslate(
//                nodeName, cam, frame,
//                imageWidth, axis_tz);
     } else if (attr_type == ATTR_SOLVER_TYPE_CAMERA_RX) {
        // Camera Rotate X and Y (tilt and pan)
        // Note: We assume the camera rotation order is ZXY.
        // All camera rotations should be screen-space FOV degree values.

        // Calculate the Angle of View of the camera, width and height
        // axis.
        double filmBackHeight = cam->getFilmbackHeightValue(frame);
        double focalLength = cam->getFocalLengthValue(frame);
        double fov_y = 0.;
        bool asDegrees = true;
        getAngleOfView(filmBackHeight, focalLength, fov_y, asDegrees);
        // As a ratio of the camera FOV in width and height, use this
        // to tilt and pan the camera attributes.
        delta = fov_y * 0.01;
    } else if (attr_type == ATTR_SOLVER_TYPE_CAMERA_RY) {
        double filmBackWidth = cam->getFilmbackWidthValue(frame);
        double focalLength = cam->getFocalLengthValue(frame);
        double fov_x = 0.;
        bool asDegrees = true;
        getAngleOfView(filmBackWidth, focalLength, fov_x, asDegrees);
        delta = fov_x * 0.01;
    } else if (attr_type == ATTR_SOLVER_TYPE_CAMERA_RZ) {
        // - Camera Rotate Z (roll)
        //   - Note: We assume the camera rotation order is ZXY.
        //   - Use a fixed value? The Camera FOV will not affect this
        //     method.
        //   - How-far away from the center of the camera's FOV?
        delta = 0.1;
    } else if (attr_type == ATTR_SOLVER_TYPE_CAMERA_SX) {
        // - Camera Scale
        //   - Throw an error - nobody should solve camera scale.
        //   - Or should we consider this a transform scale?
        //   - At the very least we should print-out a warning.
        delta = 0.0001;
        WRN("User has requested solving of camera scaleX attribute; "
                    << "that's not a good idea.");
    } else if (attr_type == ATTR_SOLVER_TYPE_CAMERA_SY) {
         delta = 0.0001;
        WRN("User has requested solving of camera scaleY attribute; "
                    << "that's not a good idea.");
    } else if (attr_type == ATTR_SOLVER_TYPE_CAMERA_SZ) {
         delta = 0.0001;
        WRN("User has requested solving of camera scaleZ attribute; "
                    << "that's not a good idea.");
    } else if (attr_type == ATTR_SOLVER_TYPE_CAMERA_FOCAL) {
        // Camera Focal length
         delta = 1.0;  // 1.0 mm.
    } else if (attr_type == ATTR_SOLVER_TYPE_TRANSFORM_TX) {
        delta = 0.0001;
//        delta = getDeltaTransformTranslate(
//                nodeName, cam, frame,
//                imageWidth, axis_tx);
    } else if (attr_type == ATTR_SOLVER_TYPE_TRANSFORM_TY) {
        delta = 0.0001;
//        delta = getDeltaTransformTranslate(
//                nodeName, cam, frame,
//                imageWidth, axis_ty);
    } else if (attr_type == ATTR_SOLVER_TYPE_TRANSFORM_TZ) {
        delta = 0.0001;
//        delta = getDeltaTransformTranslate(
//                nodeName, cam, frame,
//                imageWidth, axis_tz);
    } else if (attr_type == ATTR_SOLVER_TYPE_TRANSFORM_RX) {
        // Transform rotate
        //  Calculate the rotation axis plane's area as seen in the
        //  current camera's FOV.
        delta = 0.0001;
    } else if (attr_type == ATTR_SOLVER_TYPE_TRANSFORM_RY) {
         delta = 0.0001;
    } else if (attr_type == ATTR_SOLVER_TYPE_TRANSFORM_RZ) {
         delta = 0.0001;
    } else if (attr_type == ATTR_SOLVER_TYPE_TRANSFORM_SX) {
        // Transform scale
        // Use a fixed ratio? Like 1 percent. *=1.001 and *=0.999?
        delta = 0.001;
    } else if (attr_type == ATTR_SOLVER_TYPE_TRANSFORM_SY) {
         delta = 0.001;
    } else if (attr_type == ATTR_SOLVER_TYPE_TRANSFORM_SZ) {
         delta = 0.001;
    }
#endif // USE_EXPERIMENTAL_DELTA_VALUE

    // If the value +/- delta would cause the attribute to go
    // out of box-constraints, then we should only use one
    // value, or go in the other direction.
    if ((value + delta) > xmax) {
        sign = -1;
    }
    if ((value - delta) < xmin) {
        sign = 1;
    }
    return delta * sign;
}


// Set Parameter values
void setParameters(
        const int numberOfParameters,
        const double *parameters,
        SolverData *ud,
        bool writeDebug,
        std::ofstream &debugFile,
        MStatus &status) {
    bool debugFileIsOpen = debugFile.is_open();

    MTime currentFrame = MAnimControl::currentTime();
    for (int i = 0; i < numberOfParameters; ++i) {
        IndexPair attrPair = ud->paramToAttrList[i];
        AttrPtr attr = ud->attrList[attrPair.first];

        double offset = attr->getOffsetValue();
        double scale = attr->getScaleValue();
        double xmin = attr->getMinimumValue();
        double xmax = attr->getMaximumValue();
        double value = parameters[i];
        value = parameterBoundFromInternalToExternal(
            value,
            xmin, xmax,
            offset, scale);

        // Get frame time
        MTime frame = currentFrame;
        if (attrPair.second != -1) {
            frame = ud->frameList[attrPair.second];
        }

        if (writeDebug == true && debugFileIsOpen == true) {
            debugFile << "i=" << i
                      << " v=" << value
                      << std::endl;
        }
        attr->setValue(value, frame, *ud->dgmod, *ud->curveChange);
    }

    // Commit changed data into Maya
    ud->dgmod->doIt();

    // Invalidate the Camera Matrix cache.
    //
    // In future we might be able to auto-detect if the camera
    // will change based on the current solve and not invalidate
    // the cache but for now we cannot take the risk of an
    // incorrect solve; we clear the cache.
    for (int i = 0; i < (int) ud->cameraList.size(); ++i) {
        ud->cameraList[i]->clearAttrValueCache();
    }
}


inline
double gaussian(double x, double mean, double sigma) {
    return std::exp(
            -(std::pow((x - mean), 2.0) / (2.0 * (std::pow(sigma, 2.0))))
    );
}


// Measure Errors
void measureErrors(
        int numberOfParameters,
        int numberOfErrors,
        int numberOfMarkerErrors,
        int numberOfAttrStiffnessErrors,
        int numberOfAttrSmoothnessErrors,
        double *errors,
        SolverData *ud,
        double &error_avg,
        double &error_max,
        double &error_min,
        bool writeDebug,
        std::ofstream &debugFile,
        MStatus &status) {
    bool debugIsOpen = debugFile.is_open();
    error_avg = 0.0;
    error_max = -0.0;
    error_min = std::numeric_limits<double>::max();

#if FORCE_TRIGGER_EVAL == 1
    {
        MPoint pos;
        int i = 0;
        IndexPair markerPair = ud->errorToMarkerList[i];
        MarkerPtr marker = ud->markerList[markerPair.first];
        MTime frame = ud->frameList[markerPair.second];
        status = marker->getPos(pos, frame + 1);
        CHECK_MSTATUS(status);
    }
#endif

    // Compute Marker Errors
    MMatrix cameraWorldProjectionMatrix;
    MPoint mkr_mpos;
    MPoint bnd_mpos;
    for (int i = 0; i < (numberOfMarkerErrors / ERRORS_PER_MARKER); ++i) {
        IndexPair markerPair = ud->errorToMarkerList[i];
        MarkerPtr marker = ud->markerList[markerPair.first];
        MTime frame = ud->frameList[markerPair.second];

        CameraPtr camera = marker->getCamera();
        status = camera->getWorldProjMatrix(cameraWorldProjectionMatrix, frame);
        CHECK_MSTATUS(status);

        MVector cam_dir;
        MPoint cam_pos;
        camera->getWorldPosition(cam_pos, frame);
        camera->getForwardDirection(cam_dir, frame);
        double filmBackWidth = camera->getFilmbackWidthValue(frame);
        double filmBackHeight = camera->getFilmbackHeightValue(frame);
        double filmBackInvAspect = filmBackHeight / filmBackWidth;

        BundlePtr bnd = marker->getBundle();

        // Use pre-computed marker position and weight
        mkr_mpos = ud->markerPosList[i];
        double mkr_weight = ud->markerWeightList[i];
        mkr_weight = std::sqrt(mkr_weight);

        // Re-project Bundle into screen-space.
        MVector bnd_dir;
        status = bnd->getPos(bnd_mpos, frame);
        CHECK_MSTATUS(status);
        MPoint bnd_mpos_tmp(bnd_mpos);
        bnd_dir = bnd_mpos_tmp - cam_pos;
        bnd_dir.normalize();
        bnd_mpos = bnd_mpos * cameraWorldProjectionMatrix;
        bnd_mpos.cartesianize();
        // convert to -0.5 to 0.5, maintaining the aspect ratio of the
        // film back.
        bnd_mpos[0] *= 0.5;
        bnd_mpos[1] *= 0.5 * filmBackInvAspect;

        // Is the bundle behind the camera?
        bool behind_camera = false;
        bool behind_camera_error_factor = 1.0;
        double cam_dot_bnd = cam_dir * bnd_dir;
        // WRN("Camera DOT Bundle: " << cam_dot_bnd);
        if (cam_dot_bnd < 0.0) {
            behind_camera = true;
            behind_camera_error_factor = 1e+6;
        }

        if (writeDebug && debugIsOpen) {
            debugFile << "Bundle: " << bnd->getNodeName()
                      << std::endl;
            debugFile << "Behind Camera: " << behind_camera
                      << std::endl;
            debugFile << "Cam DOT Bnd: " << cam_dot_bnd
                      << std::endl;
            debugFile << "bnd_mpos: "
                      << bnd_mpos_tmp.x << ", "
                      << bnd_mpos_tmp.y << ", "
                      << bnd_mpos_tmp.z
                      << std::endl;
            debugFile << "cam_pos: "
                      << cam_pos.x << ", "
                      << cam_pos.y << ", "
                      << cam_pos.z
                      << std::endl;
            debugFile << "cam_dir: "
                      << cam_dir.x << ", "
                      << cam_dir.y << ", "
                      << cam_dir.z
                      << std::endl;
            debugFile << "bnd_dir: "
                      << bnd_dir.x << ", "
                      << bnd_dir.y << ", "
                      << bnd_dir.z
                      << std::endl;
        }

        // According to the Ceres solver 'circle_fit.cc'
        // example, using the 'sqrt' distance error function is a
        // bad idea as it will introduce non-linearities, we are
        // better off using something like 'x*x - y*y'. It would
        // be best to test this detail.
        double dx = fabs(mkr_mpos.x - bnd_mpos.x) * ud->imageWidth;
        double dy = fabs(mkr_mpos.y - bnd_mpos.y) * ud->imageWidth;
        double d = distance_2d(mkr_mpos, bnd_mpos) * ud->imageWidth;

        errors[(i * ERRORS_PER_MARKER) + 0] = dx * mkr_weight * behind_camera_error_factor;  // X error
        errors[(i * ERRORS_PER_MARKER) + 1] = dy * mkr_weight * behind_camera_error_factor;  // Y error

        // 'ud->errorList' is the deviation shown to the user, it
        // should not have any loss functions or scaling applied to it.
        ud->errorList[(i * ERRORS_PER_MARKER) + 0] = dx * behind_camera_error_factor;
        ud->errorList[(i * ERRORS_PER_MARKER) + 1] = dy * behind_camera_error_factor;
        ud->errorDistanceList[i] = d;
        error_avg += d;
        if (d > error_max) { error_max = d; }
        if (d < error_min) { error_min = d; }
    }

    // Compute the stiffness values for the the attributes of the 'error' array.
    // Stiffness is an error weighting back to the previous value.
    double attrValue = 0.0;
    double stiffValue = 0.0;
    double stiffWeight = 0.0;
    double stiffVariance = 1.0;
    const int stiffIndexOffset = 0;
    for (int i = 0; i < numberOfAttrStiffnessErrors; ++i) {
        int indexIntoErrorArray = numberOfMarkerErrors + stiffIndexOffset + i;
        StiffAttrsPtr stiffAttrs = ud->stiffAttrsList[i];
        int attrIndex = stiffAttrs->attrIndex;
        AttrPtr stiffWeightAttr = stiffAttrs->weightAttr;
        AttrPtr stiffVarianceAttr = stiffAttrs->varianceAttr;
        AttrPtr stiffValueAttr = stiffAttrs->valueAttr;
        AttrPtr attr = ud->attrList[attrIndex];

        // Query the current value of the value, and calculate
        //  the difference between the stiffness value.
        stiffWeightAttr->getValue(stiffWeight);
        stiffVarianceAttr->getValue(stiffVariance);
        stiffValueAttr->getValue(stiffValue);
        attr->getValue(attrValue);

        double error = ((1.0 / gaussian(attrValue, stiffValue, stiffVariance)) - 1.0);
        ud->errorList[indexIntoErrorArray] = error * stiffWeight;
        errors[indexIntoErrorArray] = error * stiffWeight;
    }

    // Compute the smoothness values for the the attributes of the 'error' array.
    // Smoothness is an error weighting to the predicted next value that is smooth.
    double smoothValue = 0.0;
    double smoothWeight = 0.0;
    double smoothVariance = 1.0;
    const int smoothIndexOffset = numberOfAttrStiffnessErrors;
    for (int i = 0; i < numberOfAttrSmoothnessErrors; ++i) {
        int indexIntoErrorArray = numberOfMarkerErrors + smoothIndexOffset + i;
        SmoothAttrsPtr smoothAttrs = ud->smoothAttrsList[i];
        int attrIndex = smoothAttrs->attrIndex;
        AttrPtr smoothWeightAttr = smoothAttrs->weightAttr;
        AttrPtr smoothVarianceAttr = smoothAttrs->varianceAttr;
        AttrPtr smoothValueAttr = smoothAttrs->valueAttr;
        AttrPtr attr = ud->attrList[attrIndex];

        // Query the current value of the value, and calculate
        //  the difference between the smoothness value.
        smoothWeightAttr->getValue(smoothWeight);
        smoothVarianceAttr->getValue(smoothVariance);
        smoothValueAttr->getValue(smoothValue);
        attr->getValue(attrValue);

        double error = ((1.0 / gaussian(attrValue, smoothValue, smoothVariance)) - 1.0);
        ud->errorList[indexIntoErrorArray] = error * smoothWeight;
        errors[indexIntoErrorArray] = error * smoothWeight;
    }

    // Changes the errors to be scaled by the loss function.
    // This will reduce the affect outliers have on the solve.
    if (ud->solverOptions->solverSupportsRobustLoss) {
        // TODO: Scale the jacobian by the loss function too?
        applyLossFunctionToErrors(numberOfErrors, errors,
                                  ud->solverOptions->robustLossType,
                                  ud->solverOptions->robustLossScale);
    }

    error_avg *= 1.0 / (numberOfErrors / ERRORS_PER_MARKER);

    if (writeDebug && debugIsOpen) {
        for (int i = 0; i < (numberOfErrors / ERRORS_PER_MARKER); ++i) {
            debugFile << "error i=" << i
                      << " x=" << ud->errorList[(i * ERRORS_PER_MARKER) + 0]
                      << " y=" << ud->errorList[(i * ERRORS_PER_MARKER) + 1]
                      << std::endl;
            debugFile << "error dist i=" << i
                      << " v=" << ud->errorDistanceList[i]
                      << std::endl;
        }
        debugFile << "emin=" << error_min
                  << " emax=" << error_max
                  << " eavg=" << error_avg
                  << std::endl;
    }
    return;
}


// Add another 'normal function' evaluation to the count.
void incrementNormalIteration(SolverData *ud,
                              bool debugIsOpen,
                              std::ofstream &debugFile) {
    ++ud->funcEvalNum;
    ++ud->iterNum;
    // We're not using INFO macro because we don't want a
    // new-line created.
    std::cerr << "Eval ";
    std::cerr << std::right << std::setfill ('0') << std::setw(4)
              << ud->funcEvalNum;
    std::cerr << " | Normal   ";
    std::cerr << std::right << std::setfill ('0') << std::setw(4)
              << ud->iterNum;
    if (debugIsOpen) {
        debugFile << std::endl
                  << "iteration normal: " << ud->iterNum
                  << std::endl;
    }
    return;
}


// Add another 'jacobian function' evaluation to the count.
void incrementJacobianIteration(SolverData *ud,
                                bool debugIsOpen,
                                std::ofstream &debugFile) {
    ++ud->funcEvalNum;
    ++ud->jacIterNum;
    if (ud->verbose) {
        std::cerr << "Eval ";
        std::cerr << std::right << std::setfill ('0') << std::setw (4)
                  << ud->funcEvalNum;
        std::cerr << " | Jacobian ";
        std::cerr << std::right << std::setfill ('0') << std::setw (4)
                  << ud->jacIterNum;
        if (ud->doCalcJacobian) {
            std::cerr << std::endl;
        }
    }
    if (debugIsOpen) {
        debugFile << std::endl
                  << "iteration jacobian: " << ud->jacIterNum
                  << std::endl;
    }
    return;
}


// Function run by cminpack algorithm to test the input parameters, p,
// and compute the output errors, x.
int solveFunc(int numberOfParameters,
              int numberOfErrors,
              const double *parameters,
              double *errors,
              double *jacobian,
              void *userData) {
    SolverData *ud = static_cast<SolverData *>(userData);
    ud->timer.funcBenchTimer.start();
    ud->timer.funcBenchTicks.start();
    if (!ud->doCalcJacobian) {
        ud->computation->setProgress(ud->iterNum);
    }

    int numberOfMarkerErrors = ud->numberOfMarkerErrors;
    int numberOfAttrStiffnessErrors = ud->numberOfAttrStiffnessErrors;
    int numberOfAttrSmoothnessErrors = ud->numberOfAttrSmoothnessErrors;

    // TODO: Is this not slow to open and close a file at each
    // iteration - is there a more elegant solution?
    std::ofstream debugFile;
    if (ud->debugFileName.length() > 0) {
        const char *debugFileChar = ud->debugFileName.asChar();
        debugFile.open(debugFileChar, std::ios_base::app);
    }
    bool debugIsOpen = debugFile.is_open();

    if (ud->isNormalCall) {
        incrementNormalIteration(ud, debugIsOpen, debugFile);
    } else if (ud->isJacobianCall && !ud->doCalcJacobian) {
        incrementJacobianIteration(ud, debugIsOpen, debugFile);
    }

    if (ud->isPrintCall) {
        // insert print statements here when nprint is positive.
        //
        // if the nprint parameter to 'lmdif' or 'lmder' is positive,
        // the function is called every nprint iterations with iflag=0,
        // so that the function may perform special operations, such as
        // printing residuals.
        return SOLVE_FUNC_SUCCESS;
    }

    if (ud->computation->isInterruptRequested()) {
        WRN("User wants to cancel the evaluation!");
        ud->userInterrupted = true;
        return SOLVE_FUNC_FAILURE;
    }

#ifdef MAYA_PROFILE
    int profileCategory = MProfiler::getCategoryIndex("mmSolver");
    MProfilingScope iterScope(profileCategory,
                              MProfiler::kColorC_L1,
                              "iteration");
#endif

    bool interactive = ud->mayaSessionState == MGlobal::MMayaState::kInteractive;
    if (interactive) {
        MString dgDirtyCmd = generateDirtyCommand(numberOfMarkerErrors, ud);
        MGlobal::executeCommand(dgDirtyCmd);
    }

    // Calculate residual errors, or jacobian matrix?
    double error_avg = 0;
    double error_max = 0;
    double error_min = 0;
    if (!ud->doCalcJacobian) {
        bool writeDebug = true;

        // Set Parameters
        MStatus status;
        {
            ud->timer.paramBenchTimer.start();
            ud->timer.paramBenchTicks.start();
#ifdef MAYA_PROFILE
            MProfilingScope setParamScope(profileCategory,
                                          MProfiler::kColorA_L2,
                                          "set parameters");
#endif
            setParameters(
                    numberOfParameters,
                    parameters,
                    ud,
                    writeDebug,
                    debugFile,
                    status);
            ud->timer.paramBenchTimer.stop();
            ud->timer.paramBenchTicks.stop();
        }

        // Measure Errors
        {
            ud->timer.errorBenchTimer.start();
            ud->timer.errorBenchTicks.start();
#ifdef MAYA_PROFILE
            MProfilingScope setParamScope(profileCategory,
                                          MProfiler::kColorA_L1,
                                          "measure errors");
#endif
            measureErrors(numberOfParameters,
                          numberOfErrors,
                          numberOfMarkerErrors,
                          numberOfAttrStiffnessErrors,
                          numberOfAttrSmoothnessErrors,
                          errors,
                          ud,
                          error_avg, error_max, error_min,
                          writeDebug,
                          debugFile,
                          status);
            ud->timer.errorBenchTimer.stop();
            ud->timer.errorBenchTicks.stop();
        }
    } else {
        // Calculate Jacobian Matrix
        MStatus status;
        bool writeDebug = true;
        assert(ud->solverOptions->solverType == SOLVER_TYPE_CMINPACK_LMDER);
        int autoDiffType = ud->solverOptions->autoDiffType;

        // Get longest dimension for jacobian matrix
        int ldfjac = numberOfErrors;
        if (ldfjac < numberOfParameters) {
            ldfjac = numberOfParameters;
        }

        int progressMin = ud->computation->progressMin();
        int progressMax = ud->computation->progressMax();
        ud->computation->setProgress(progressMin);

        // Calculate the jacobian matrix.
        MTime currentFrame = MAnimControl::currentTime();
        writeDebug = true;
        for (int i = 0; i < numberOfParameters; ++i) {
            double ratio = (double) i / (double) numberOfParameters;
            int progressNum = progressMin + static_cast<int>(ratio * progressMax);
            ud->computation->setProgress(progressNum);

            if (ud->computation->isInterruptRequested()) {
                WRN("User wants to cancel the evaluation!");
                ud->userInterrupted = true;
                return SOLVE_FUNC_FAILURE;
            }

            // Create a copy of the parameters and errors.
            std::vector<double> paramListA(numberOfParameters, 0);
            for (int j = 0; j < numberOfParameters; ++j) {
                paramListA[j] = parameters[j];
            }
            std::vector<double> errorListA(numberOfErrors, 0);

            // Calculate the relative delta for each parameter.
            double delta = ud->solverOptions->delta;
            assert(delta > 0.0);

            // 'analytically' calculate the deviation of markers as
            //  will be affected by the new calculated delta value.
            //  This will give us a jacobian matrix, without needing
            //  to set attribute values and re-evaluate them in Maya's
            //  DG.
            IndexPair attrPair = ud->paramToAttrList[i];
            AttrPtr attr = ud->attrList[attrPair.first];
            // TODO: Get the camera that is best for the attribute,
            //  not just index 0.
            MarkerPtr mkr = ud->markerList[0];
            CameraPtr cam = mkr->getCamera();

            double value = parameters[i];
            double deltaA = calculateParameterDelta(
                    value, delta, 1,
                    attr, cam, currentFrame,
                    ud->imageWidth);

            incrementJacobianIteration(ud, debugIsOpen, debugFile);
            paramListA[i] = paramListA[i] + deltaA;
            {
                ud->timer.paramBenchTimer.start();
                ud->timer.paramBenchTicks.start();
#ifdef MAYA_PROFILE
                MProfilingScope setParamScope(profileCategory,
                                              MProfiler::kColorA_L2,
                                              "set parameters");
#endif
                setParameters(
                        numberOfParameters,
                        &paramListA[0],
                        ud,
                        writeDebug,
                        debugFile,
                        status);
                ud->timer.paramBenchTimer.stop();
                ud->timer.paramBenchTicks.stop();
            }

            double error_avg_tmp = 0;
            double error_max_tmp = 0;
            double error_min_tmp = 0;
            {
                ud->timer.errorBenchTimer.start();
                ud->timer.errorBenchTicks.start();
#ifdef MAYA_PROFILE
                MProfilingScope setParamScope(profileCategory,
                                              MProfiler::kColorA_L1,
                                              "measure errors");
#endif
                measureErrors(numberOfParameters,
                              numberOfErrors,
                              numberOfMarkerErrors,
                              numberOfAttrStiffnessErrors,
                              numberOfAttrSmoothnessErrors,
                              &errorListA[0],
                              ud,
                              error_avg_tmp,
                              error_max_tmp,
                              error_min_tmp,
                              writeDebug,
                              debugFile,
                              status);
                ud->timer.errorBenchTimer.stop();
                ud->timer.errorBenchTicks.stop();
            }

            if (autoDiffType == AUTO_DIFF_TYPE_FORWARD) {
                assert(ud->solverOptions->solverSupportsAutoDiffForward);
                // Set the Jacobian matrix using the previously
                // calculated errors (original and A).
                double inv_delta = 1.0 / deltaA;
                for (int j = 0; j < errorListA.size(); ++j) {
                    int num = (i * ldfjac) + j;
                    double x = (errorListA[j] - errors[j]) * inv_delta;
                    ud->jacobianList[num] = x;
                    jacobian[num] = x;
                }

            } else if (autoDiffType == AUTO_DIFF_TYPE_CENTRAL) {
                assert(ud->solverOptions->solverSupportsAutoDiffCentral);
                // Create another copy of parameters and errors.
                std::vector<double> paramListB(numberOfParameters, 0);
                for (int j = 0; j < numberOfParameters; ++j) {
                    paramListB[j] = parameters[j];
                }
                std::vector<double> errorListB(numberOfErrors, 0);

                // Get the new delta, from the oposite direction. If
                // we don't calculate a different delta value, we
                // something has gone wrong and a second evaluation is
                // not needed.
                double deltaB = calculateParameterDelta(
                        value, delta, -1,
                        attr, cam, currentFrame,
                        ud->imageWidth);
                if (deltaA == deltaB) {
                    // Set the Jacobian matrix using the previously
                    // calculated errors (original and A).
                    double inv_delta = 1.0 / deltaA;
                    for (int j = 0; j < errorListA.size(); ++j) {
                        int num = (i * ldfjac) + j;
                        double x = (errorListA[j] - errors[j]) * inv_delta;
                        ud->jacobianList[num] = x;
                        jacobian[num] = x;
                    }
                } else {

                    incrementJacobianIteration(ud, debugIsOpen, debugFile);
                    paramListB[i] = paramListB[i] + deltaB;
                    {
                        ud->timer.paramBenchTimer.start();
                        ud->timer.paramBenchTicks.start();
#ifdef MAYA_PROFILE
                        MProfilingScope setParamScope(profileCategory,
                                                      MProfiler::kColorA_L2,
                                                      "set parameters");
#endif
                        setParameters(numberOfParameters,
                                      &paramListB[0],
                                      ud,
                                      writeDebug,
                                      debugFile,
                                      status);
                        ud->timer.paramBenchTimer.stop();
                        ud->timer.paramBenchTicks.stop();
                    }

                    error_avg_tmp = 0;
                    error_max_tmp = 0;
                    error_min_tmp = 0;
                    {
                        ud->timer.errorBenchTimer.start();
                        ud->timer.errorBenchTicks.start();
#ifdef MAYA_PROFILE
                        MProfilingScope setParamScope(profileCategory,
                                                      MProfiler::kColorA_L1,
                                                      "measure errors");
#endif
                        measureErrors(numberOfParameters,
                                      numberOfErrors,
                                      numberOfMarkerErrors,
                                      numberOfAttrStiffnessErrors,
                                      numberOfAttrSmoothnessErrors,
                                      &errorListB[0],
                                      ud,
                                      error_avg_tmp,
                                      error_max_tmp,
                                      error_min_tmp,
                                      writeDebug,
                                      debugFile,
                                      status);
                        ud->timer.errorBenchTimer.stop();
                        ud->timer.errorBenchTicks.stop();
                    }

                    // Set the Jacobian matrix using the previously
                    // calculated errors (A and B).
                    assert(errorListA.size() == errorListB.size());
                    double inv_delta = 0.5 / (fabs(deltaA) + fabs(deltaB));
                    for (int j = 0; j < errorListA.size(); ++j) {
                        int num = (i * ldfjac) + j;
                        double x = (errorListA[j] - errorListB[j]) * inv_delta;
                        ud->jacobianList[num] = x;
                        jacobian[num] = x;
                    }
                }
            }
        }
    }
    ud->timer.funcBenchTimer.stop();
    ud->timer.funcBenchTicks.stop();

    if (ud->isNormalCall) {
        fprintf(
            stderr,
            " | error avg %8.4f   min %8.4f   max %8.4f\n",
            error_avg,
            error_min,
            error_max);
    } else {
        if (ud->verbose) {
            if (!ud->doCalcJacobian) {
                std::cerr << std::endl;
            }
        }
    }
    return SOLVE_FUNC_SUCCESS;
}


// Clean up #define
#undef FORCE_TRIGGER_EVAL
