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
#include <utilities/numberUtils.h>
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
#include <maya/MStreamUtils.h>

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


// Given a specific parameter, calculate the expected 'delta' value of
// the parameter.
double calculateParameterDelta(double value,
                               double delta,
                               double sign,
                               AttrPtr attr,
                               CameraPtr cam,
                               MTime frame) {
    MStatus status = MS::kSuccess;

    double xmin = attr->getMinimumValue();
    double xmax = attr->getMaximumValue();

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
        std::ofstream *debugFile,
        MStatus &status) {
    bool debugFileIsOpen = false;
#ifdef WITH_DEBUG_FILE
    if (debugFile != NULL) {
        debugFileIsOpen = debugFile->is_open();
    }
#endif

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

#ifdef WITH_DEBUG_FILE
        if (debugFileIsOpen && debugFile != NULL) {
            (*debugFile) << "i=" << i << " v=" << value << "\n";
        }
#endif
        attr->setValue(value, frame, *ud->dgmod, *ud->curveChange);
    }

    // Commit changed data into Maya
    ud->dgmod->doIt();

    // Save a copy of the parameters - to be used for determining the
    // the difference between the previous and next parameters to be
    // set inside Maya.
    for (int j = 0; j < numberOfParameters; ++j) {
        ud->previousParamList[j] = parameters[j];
    }

    // Invalidate the Camera Matrix cache.
    //
    // In future we might be able to auto-detect if the camera
    // will change based on the current solve and not invalidate
    // the cache but for now we cannot take the risk of an
    // incorrect solve; we clear the cache.
    for (int i = 0; i < (int) ud->cameraList.size(); ++i) {
        ud->cameraList[i]->clearAttrValueCache();
    }

    status = MStatus::kSuccess;
}


inline
double gaussian(double x, double mean, double sigma) {
    return std::exp(
            -(std::pow((x - mean), 2.0) / (2.0 * (std::pow(sigma, 2.0))))
    );
}


/*
 * Compare the previous and new parameters to see which parameters
 * have changed. This allows us to only update and measure the changed
 * markers and attributes - speeding up the evaluation.
 */
void determineMarkersToBeEvaluated(int numberOfParameters,
                                   int numberOfMarkers,
                                   double delta,
                                   std::vector<double> previousParamList,
                                   const double *parameters,
                                   std::vector<std::vector<bool>> errorToParamList,
                                   std::vector<bool> &evalErrorMeasurements) {
    std::vector<int> evalCount(numberOfMarkers, 0);

    // Get all parameters that have changed.
    double approxDelta = fabs(delta) * 0.5;
    bool noneChanged = true;
    std::vector<bool> paramChangedList(numberOfParameters, false);
    for (int i = 0; i < numberOfParameters; ++i) {
        bool changed = !number::isApproxEqual<double>(
            parameters[i], previousParamList[i], approxDelta);
        paramChangedList[i] = changed;
        if (changed) {
            noneChanged = false;
        }
    }

    // Find if a marker does not need to be updated at all.
    for (int i = 0; i < numberOfParameters; ++i) {
        bool changed = paramChangedList[i];
        if (noneChanged == true) {
            changed = true;
        }
        for (int j = 0; j < numberOfMarkers; ++j) {
            if (changed && errorToParamList[j][i]) {
                evalCount[j] = evalCount[j] + 1;
            }
        }
    }

    // Convert evalCount to list of bools
    evalErrorMeasurements.resize((unsigned long) numberOfMarkers, false);
    for (size_t i = 0; i < evalCount.size(); ++i) {
        evalErrorMeasurements[i] = static_cast<bool>(evalCount[i] > 0);
    }
    return;
}


void measureErrors(
        int numberOfParameters,
        int numberOfErrors,
        int numberOfMarkerErrors,
        int numberOfAttrStiffnessErrors,
        int numberOfAttrSmoothnessErrors,
        std::vector<bool> frameIndexEnable,
        std::vector<bool> evalErrorMeasurements,
        double *errors,
        SolverData *ud,
        double &error_avg,
        double &error_max,
        double &error_min,
        std::ofstream *debugFile,
        MStatus &status) {
#ifdef WITH_DEBUG_FILE
    bool debugIsOpen = false;
    if (debugFile != NULL) {
        debugIsOpen = debugFile->is_open();
    }
#endif
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
    int numberOfErrorsMeasured = 0;
    for (int i = 0; i < (numberOfMarkerErrors / ERRORS_PER_MARKER); ++i) {
        IndexPair markerPair = ud->errorToMarkerList[i];
        int markerIndex = markerPair.first;
        int frameIndex = markerPair.second;
        bool skipFrame = frameIndexEnable[frameIndex] == false;
        bool skipMarker = evalErrorMeasurements[i] == false;
        if (skipFrame) {
            // Skip evaluation of this marker error. The 'errors' data
            // is expected to be unchanged from the last evaluation.
            continue;
        }
        if (skipMarker) {
            // Skip calculation of the error if evalErrorMeasurements says
            // not to calculate it. The evalErrorMeasurements is expected
            // to be pre-computed and 'know' something this function does
            // not about the greater structure of the solving problem.
            continue;
        }

        MarkerPtr marker = ud->markerList[markerIndex];
        MTime frame = ud->frameList[frameIndex];

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
        assert(mkr_weight > 0.0);  // 'sqrt' will be NaN if the weight is less than 0.0.
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
        // Convert to -0.5 to 0.5, maintaining the aspect ratio of the
        // film back.
        bnd_mpos[0] *= 0.5;
        bnd_mpos[1] *= 0.5 * filmBackInvAspect;

        // Is the bundle behind the camera?
        bool behind_camera = false;
        double behind_camera_error_factor = 1.0;
        double cam_dot_bnd = cam_dir * bnd_dir;
        // WRN("Camera DOT Bundle: " << cam_dot_bnd);
        if (cam_dot_bnd < 0.0) {
            behind_camera = true;
            behind_camera_error_factor = 1e+6;
        }

#ifdef WITH_DEBUG_FILE
        if (debugIsOpen && debugFile != NULL) {
            (*debugFile) << "Bundle: " << bnd->getNodeName()
                         << "\n";
            (*debugFile) << "Behind Camera: " << behind_camera
                         << "\n";
            (*debugFile) << "Cam DOT Bnd: " << cam_dot_bnd
                         << "\n";
            (*debugFile) << "bnd_mpos: "
                         << bnd_mpos_tmp.x << ", "
                         << bnd_mpos_tmp.y << ", "
                         << bnd_mpos_tmp.z
                         << "\n";
            (*debugFile) << "cam_pos: "
                         << cam_pos.x << ", "
                         << cam_pos.y << ", "
                         << cam_pos.z
                         << "\n";
            (*debugFile) << "cam_dir: "
                         << cam_dir.x << ", "
                         << cam_dir.y << ", "
                         << cam_dir.z
                         << "\n";
            (*debugFile) << "bnd_dir: "
                         << bnd_dir.x << ", "
                         << bnd_dir.y << ", "
                         << bnd_dir.z
                         << "\n";
        }
#endif

        // According to the Ceres solver 'circle_fit.cc'
        // example, using the 'sqrt' distance error function is a
        // bad idea as it will introduce non-linearities, we are
        // better off using something like 'x*x - y*y'. It would
        // be best to test this detail.
        double dx = fabs(mkr_mpos.x - bnd_mpos.x) * ud->imageWidth;
        double dy = fabs(mkr_mpos.y - bnd_mpos.y) * ud->imageWidth;
        double d = distance_2d(mkr_mpos, bnd_mpos) * ud->imageWidth;

        int errorIndex = i * ERRORS_PER_MARKER;
        errors[errorIndex + 0] = dx * mkr_weight * behind_camera_error_factor;
        errors[errorIndex + 1] = dy * mkr_weight * behind_camera_error_factor;

        // 'ud->errorList' is the deviation shown to the user, it
        // should not have any loss functions or scaling applied to it.
        ud->errorList[errorIndex + 0] = dx * behind_camera_error_factor;
        ud->errorList[errorIndex + 1] = dy * behind_camera_error_factor;
        ud->errorDistanceList[i] = d;
        error_avg += d;
        if (d > error_max) { error_max = d; }
        if (d < error_min) { error_min = d; }
        ++numberOfErrorsMeasured;
    }
    if (numberOfErrorsMeasured == 0) {
        error_max = 0.0;
        error_min = 0.0;
        error_avg = 0.0;
        ERR("No Marker measurements were taken.");
    } else {
        error_avg *= 1.0 / numberOfErrorsMeasured;
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
    assert(error_max >= error_min);
    assert(error_min <= error_max);

#ifdef WITH_DEBUG_FILE
    if (debugIsOpen && debugFile != NULL) {
        for (int i = 0; i < (numberOfErrors / ERRORS_PER_MARKER); ++i) {
            (*debugFile) << "error i=" << i
                         << " x=" << ud->errorList[(i * ERRORS_PER_MARKER) + 0]
                         << " y=" << ud->errorList[(i * ERRORS_PER_MARKER) + 1]
                         << "\n";
            (*debugFile) << "error dist i=" << i
                         << " v=" << ud->errorDistanceList[i]
                         << "\n";
        }
        (*debugFile) << "emin=" << error_min
                     << " emax=" << error_max
                     << " eavg=" << error_avg
                     << "\n";
    }
#endif
    return;
}


// Add another 'normal function' evaluation to the count.
void incrementNormalIteration(SolverData *ud,
                              bool debugIsOpen,
                              std::ofstream *debugFile) {
    ++ud->funcEvalNum;
    ++ud->iterNum;
    MStreamUtils::stdErrorStream() << "Iteration ";
    MStreamUtils::stdErrorStream() << std::right << std::setfill ('0') << std::setw(4)
                                   << ud->iterNum;
    MStreamUtils::stdErrorStream() << " | Eval ";
    MStreamUtils::stdErrorStream() << std::right << std::setfill ('0') << std::setw(4)
                                   << ud->funcEvalNum;
#ifdef WITH_DEBUG_FILE
    if (debugIsOpen && debugFile != NULL) {
        (*debugFile) << "\n"
                     << "iteration normal: " << ud->iterNum
                     << "\n";
    }
#endif
    return;
}


// Add another 'jacobian function' evaluation to the count.
void incrementJacobianIteration(SolverData *ud,
                                bool debugIsOpen,
                                std::ofstream *debugFile) {
    ++ud->funcEvalNum;
    ++ud->jacIterNum;
    if (ud->verbose) {
        MStreamUtils::stdErrorStream() << "Jacobian  ";
        MStreamUtils::stdErrorStream() << std::right << std::setfill ('0') << std::setw (4)
                                       << ud->jacIterNum;
        MStreamUtils::stdErrorStream() << " | Eval ";
        MStreamUtils::stdErrorStream() << std::right << std::setfill ('0') << std::setw (4)
                                       << ud->funcEvalNum;
        if (ud->doCalcJacobian) {
            MStreamUtils::stdErrorStream() << "\n";
        }
    }
    #ifdef WITH_DEBUG_FILE
    if (debugIsOpen && debugFile != NULL) {
        (*debugFile) << "\n"
                  << "iteration jacobian: " << ud->jacIterNum
                  << "\n";
    }
    #endif
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
    int numberOfMarkers = numberOfMarkerErrors / ERRORS_PER_MARKER;
    assert(ud->errorToParamList.size() == numberOfMarkers);

    std::vector<bool> evalErrorMeasurements(numberOfMarkers, false);
    determineMarkersToBeEvaluated(
            numberOfParameters,
            numberOfMarkers,
            ud->solverOptions->delta,
            ud->previousParamList,
            parameters,
            ud->errorToParamList,
            evalErrorMeasurements);

    std::ofstream *debugFile = NULL;
    bool debugIsOpen = false;
#ifdef WITH_DEBUG_FILE
    if (ud->debugFileName.length() > 0) {
        const char *debugFileChar = ud->debugFileName.asChar();
        debugFile->open(debugFileChar, std::ios_base::app);
    }
    debugIsOpen = debugFile->is_open();
#endif

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
    if (ud->doCalcJacobian == false) {
        std::vector<bool> frameIndexEnable(ud->frameList.length(), 1);

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
                          frameIndexEnable,
                          evalErrorMeasurements,
                          errors,
                          ud,
                          error_avg, error_max, error_min,
                          debugFile,
                          status);
            ud->timer.errorBenchTimer.stop();
            ud->timer.errorBenchTicks.stop();
        }
    } else {
        // Calculate Jacobian Matrix
        MStatus status;
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
            for (int j = 0; j < numberOfErrors; ++j) {
                errorListA[j] = errors[j];
            }

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
                    attr, cam, currentFrame);

            std::vector<bool> frameIndexEnabled = ud->paramFrameList[i];

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
                // Based on only the changed attribute value only
                // measure the markers that can modify the attribute -
                // we do this using 'frameIndexEnabled' and
                // 'evalErrorMeasurements'.
                measureErrors(numberOfParameters,
                              numberOfErrors,
                              numberOfMarkerErrors,
                              numberOfAttrStiffnessErrors,
                              numberOfAttrSmoothnessErrors,
                              frameIndexEnabled,
                              evalErrorMeasurements,
                              &errorListA[0],
                              ud,
                              error_avg_tmp,
                              error_max_tmp,
                              error_min_tmp,
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
                        attr, cam, currentFrame);
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
                                      frameIndexEnabled,
                                      evalErrorMeasurements,
                                      &errorListB[0],
                                      ud,
                                      error_avg_tmp,
                                      error_max_tmp,
                                      error_min_tmp,
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
        char formatBuffer[128];
        sprintf(
            formatBuffer,
            " | error avg %8.4f   min %8.4f   max %8.4f",
            error_avg,
            error_min,
            error_max);
        MStreamUtils::stdErrorStream() << std::string(formatBuffer) << "\n";
    } else {
        if (ud->verbose) {
            if (!ud->doCalcJacobian) {
                std::cerr << "\n";
            }
        }
    }
    return SOLVE_FUNC_SUCCESS;
}


// Clean up #define
#undef FORCE_TRIGGER_EVAL
