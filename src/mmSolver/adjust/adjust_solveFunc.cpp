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

#include "adjust_solveFunc.h"

// STL
#include <stdio.h>

#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <ctime>
#include <iostream>
#include <limits>
#include <memory>
#include <string>
#include <vector>

// Maya
#include <maya/MAnimCurveChange.h>
#include <maya/MComputation.h>
#include <maya/MDGContext.h>
#include <maya/MDagPath.h>
#include <maya/MFnAnimCurve.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MFnPluginData.h>
#include <maya/MGlobal.h>
#include <maya/MMatrix.h>
#include <maya/MObject.h>
#include <maya/MPoint.h>
#include <maya/MProfiler.h>
#include <maya/MSelectionList.h>
#include <maya/MStreamUtils.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MVector.h>

#if MAYA_API_VERSION >= 20180000
#include <maya/MDGContextGuard.h>
#endif

// MM Solver
#include <mmcore/mmdata.h>
#include <mmcore/mmmath.h>

#include "adjust_base.h"
#include "adjust_data.h"
#include "adjust_measureErrors.h"
#include "adjust_setParameters.h"
#include "mmSolver/core/matrix_bool_2d.h"
#include "mmSolver/mayahelper/maya_attr.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_lens_model_utils.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/utilities/assert_utils.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/number_utils.h"
#include "mmSolver/utilities/string_utils.h"

namespace mmsolver {

// Per-attribute type delta values
#define PER_ATTR_TYPE_DELTA_VALUE 0

inline int getStringArrayIndexOfValue(const MStringArray &array,
                                      const MString &value) {
#if MAYA_API_VERSION >= 201700
    return array.indexOf(value);
#else
    int index = -1;
    for (unsigned int i = 0; i < array.length(); ++i) {
        if (array[i] == value) {
            index = i;
            break;
        }
    }
    return index;
#endif
}

/*
 * Generate a 'dgdirty' MEL command listing all nodes that may be
 * changed by our solve function.
 */
MString generateDirtyCommand(const int numberOfMarkerErrors,
                             SolverData *userData) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("adjust_solveFunc generateDirtyCommand");

    MString dgDirtyCmd = "dgdirty ";
    MStringArray dgDirtyNodeNames;
    for (int i = 0; i < (numberOfMarkerErrors / ERRORS_PER_MARKER); ++i) {
        IndexPair markerPair = userData->errorToMarkerList[i];

        MarkerPtr marker = userData->markerList[markerPair.first];
        MString markerName = marker->getNodeName();
        const int markerName_idx =
            getStringArrayIndexOfValue(dgDirtyNodeNames, markerName);
        if (markerName_idx == -1) {
            dgDirtyCmd += " \"" + markerName + "\" ";
            dgDirtyNodeNames.append(markerName);
        }

        CameraPtr camera = marker->getCamera();
        MString cameraTransformName = camera->getTransformNodeName();
        MString cameraShapeName = camera->getShapeNodeName();
        const int cameraTransformName_idx =
            getStringArrayIndexOfValue(dgDirtyNodeNames, cameraTransformName);
        if (cameraTransformName_idx == -1) {
            dgDirtyCmd += " \"" + cameraTransformName + "\" ";
            dgDirtyNodeNames.append(cameraTransformName);
        }
        const int cameraShapeName_idx =
            getStringArrayIndexOfValue(dgDirtyNodeNames, cameraShapeName);
        if (cameraShapeName_idx == -1) {
            dgDirtyCmd += " \"" + cameraShapeName + "\" ";
            dgDirtyNodeNames.append(cameraShapeName);
        }

        BundlePtr bundle = marker->getBundle();
        MString bundleName = bundle->getNodeName();
        const int bundleName_idx =
            getStringArrayIndexOfValue(dgDirtyNodeNames, bundleName);
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
double calculateParameterDelta(const double value, const double delta,
                               const double sign, AttrPtr &attr) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("adjust_solveFunc calculateParameterDelta");

    MStatus status = MS::kSuccess;
    const double xmin = attr->getMinimumValue();
    const double xmax = attr->getMaximumValue();

    double new_delta = delta;
#if PER_ATTR_TYPE_DELTA_VALUE == 1
    // Relative delta for different types of solver attribute types.
    const auto object_type = attr->getObjectType();
    const auto solver_attr_type = attr->getSolverAttrType();
    if (object_type == ObjectType::kCamera &&
        (solver_attr_type == AttrSolverType::kCameraFocal)) {
        new_delta *= 0.1;
    } else if (object_type == ObjectType::kLens) {
        new_delta *= 10.0;
    }
    // TODO: Change delta for bundle depending on bundle's distance
    // from camera/origin.
#endif

    // If the value +/- delta would cause the attribute to go
    // out of box-constraints, then we should only use one
    // value, or go in the other direction.
    double new_sign = sign;
    if ((value + new_delta) > xmax) {
        new_sign = -1;
    }
    if ((value - new_delta) < xmin) {
        new_sign = 1;
    }
    return new_delta * new_sign;
}

/*
 * Compare the previous and new parameters to see which parameters
 * have changed. This allows us to only update and measure the changed
 * markers and attributes - speeding up the evaluation.
 */
void determineMarkersToBeEvaluated(
    const int numberOfParameters, const int numberOfMarkers, const double delta,
    const std::vector<double> previousParamList, const double *parameters,
    const mmsolver::MatrixBool2D &errorToParamMatrix,
    std::vector<bool> &out_evalMeasurements) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("adjust_solveFunc determineMarkersToBeEvaluated");

    std::vector<int> evalCount(numberOfMarkers, 0);

    // Get all parameters that have changed.
    double approxDelta = std::fabs(delta) * 0.5;
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
        if (noneChanged) {
            changed = true;
        }
        for (int j = 0; j < numberOfMarkers; ++j) {
            const bool errorAffectsParameter = errorToParamMatrix.at(j, i);
            if (changed && errorAffectsParameter) {
                evalCount[j] = evalCount[j] + 1;
            }
        }
    }

    // Convert evalCount to list of bools
    out_evalMeasurements.resize((unsigned long)numberOfMarkers, false);
    for (size_t i = 0; i < evalCount.size(); ++i) {
        out_evalMeasurements[i] = static_cast<bool>(evalCount[i] > 0);
    }
    return;
}

// Add another 'normal function' evaluation to the count.
void incrementNormalIteration(SolverData *userData) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("adjust_solveFunc incrementNormalIteration");

    ++userData->funcEvalNum;
    ++userData->iterNum;
    if (userData->logLevel >= LogLevel::kVerbose) {
        MStreamUtils::stdErrorStream() << "Iteration ";
        MStreamUtils::stdErrorStream() << std::right << std::setfill('0')
                                       << std::setw(4) << userData->iterNum;
        MStreamUtils::stdErrorStream() << " | Eval ";
        MStreamUtils::stdErrorStream() << std::right << std::setfill('0')
                                       << std::setw(4) << userData->funcEvalNum;
    }
    return;
}

// Add another 'jacobian function' evaluation to the count.
void incrementJacobianIteration(SolverData *userData) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("adjust_solveFunc incrementJacobianIteration");

    ++userData->funcEvalNum;
    ++userData->jacIterNum;
    if (userData->logLevel >= LogLevel::kDebug) {
        MStreamUtils::stdErrorStream() << "Jacobian  ";
        MStreamUtils::stdErrorStream() << std::right << std::setfill('0')
                                       << std::setw(4) << userData->jacIterNum;
        MStreamUtils::stdErrorStream() << " | Eval ";
        MStreamUtils::stdErrorStream() << std::right << std::setfill('0')
                                       << std::setw(4) << userData->funcEvalNum;
        if (userData->doCalcJacobian) {
            MStreamUtils::stdErrorStream() << "\n";
        }
    }
    return;
}

// A normal evaluation of the errors and parameters.
int solveFunc_measureErrors(
    const int numberOfMarkerErrors, const int numberOfAttrStiffnessErrors,
    const int numberOfAttrSmoothnessErrors, const int numberOfMarkers,
    const int frameListLength, const int profileCategory,
    const double imageWidth, const int numberOfParameters,
    const int numberOfErrors, const double *parameters, double *errors,
    double *jacobian, SolverData *userData, SolverTimer &timer,
    double &error_avg, double &error_max, double &error_min) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("adjust_solveFunc solveFunc_measureErrors");

    std::vector<bool> evalMeasurements(numberOfMarkers, true);
    std::vector<bool> frameIndexEnable(frameListLength, 1);

    // Set Parameters
    MStatus status;
    {
        timer.paramBenchTimer.start();
        timer.paramBenchTicks.start();
#ifdef MAYA_PROFILE
        MProfilingScope setParamScope(profileCategory, MProfiler::kColorA_L2,
                                      "set parameters");
#endif
        status = setParameters(numberOfParameters, parameters, userData);
        timer.paramBenchTimer.stop();
        timer.paramBenchTicks.stop();
    }

    // Measure Errors
    {
        timer.errorBenchTimer.start();
        timer.errorBenchTicks.start();
#ifdef MAYA_PROFILE
        MProfilingScope setParamScope(profileCategory, MProfiler::kColorA_L1,
                                      "measure errors");
#endif
        measureErrors(numberOfErrors, numberOfMarkerErrors,
                      numberOfAttrStiffnessErrors, numberOfAttrSmoothnessErrors,
                      frameIndexEnable, evalMeasurements, imageWidth, errors,
                      userData, error_avg, error_max, error_min, status);
        timer.errorBenchTimer.stop();
        timer.errorBenchTicks.stop();
    }
    return SOLVE_FUNC_SUCCESS;
}

int solveFunc_calculateJacobianMatrixForParameter(
    const int parameterIndex, const int progressMin, const int progressMax,
    std::vector<double> &paramListA, std::vector<double> &errorListA,
    const std::vector<bool> &evalMeasurements, const int autoDiffType,
    const int ldfjac, const int numberOfMarkerErrors,
    const int numberOfAttrStiffnessErrors,
    const int numberOfAttrSmoothnessErrors, const double imageWidth,
    const int numberOfParameters, const int numberOfErrors,
    const double *parameters, double *errors, double *jacobian,
    SolverData *userData, SolverTimer &timer) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB(
        "adjust_solveFunc solveFunc_calculateJacobianMatrixForParameter");

    MStatus status;

    const double ratio = (double)parameterIndex / (double)numberOfParameters;
    int progressNum = progressMin + static_cast<int>(ratio * progressMax);
    userData->computation->setProgress(progressNum);

    if (userData->computation->isInterruptRequested()) {
        MMSOLVER_MAYA_WRN("User wants to cancel the evaluation!");
        userData->userInterrupted = true;
        return SOLVE_FUNC_FAILURE;
    }

    // Create a copy of the parameters and errors.
    for (int j = 0; j < numberOfParameters; ++j) {
        paramListA[j] = parameters[j];
    }
    for (int j = 0; j < numberOfErrors; ++j) {
        errorListA[j] = errors[j];
    }

    // Calculate the relative delta for each parameter.
    const double delta = userData->solverOptions->delta;
    MMSOLVER_ASSERT(delta > 0.0,
                    "Differentiation delta values must be greater than zero.");

    // 'analytically' calculate the deviation of markers as
    //  will be affected by the new calculated delta value.
    //  This will give us a jacobian matrix, without needing
    //  to set attribute values and re-evaluate them in Maya's
    //  DG.
    IndexPair attrPair = userData->paramToAttrList[parameterIndex];
    AttrPtr attr = userData->attrList[attrPair.first];
    // TODO: Get the camera that is best for the attribute,
    //  not just index 0.
    MarkerPtr mkr = userData->markerList[0];
    CameraPtr cam = mkr->getCamera();

    const double value = parameters[parameterIndex];
    const double deltaA = calculateParameterDelta(value, delta, 1, attr);

    std::vector<bool> frameIndexEnabled;
    frameIndexEnabled.reserve(userData->paramFrameMatrix.height());
    for (auto j = 0; j < userData->paramFrameMatrix.height(); j++) {
        const auto value = userData->paramFrameMatrix.at(parameterIndex, j);
        frameIndexEnabled.push_back(value);
    }

    incrementJacobianIteration(userData);
    paramListA[parameterIndex] = paramListA[parameterIndex] + deltaA;
    {
        timer.paramBenchTimer.start();
        timer.paramBenchTicks.start();
#ifdef MAYA_PROFILE
        MProfilingScope setParamScope(profileCategory, MProfiler::kColorA_L2,
                                      "set parameters");
#endif
        status = setParameters(numberOfParameters, &paramListA[0], userData);
        timer.paramBenchTimer.stop();
        timer.paramBenchTicks.stop();
    }

    double error_avg_tmp = 0;
    double error_max_tmp = 0;
    double error_min_tmp = 0;
    {
        timer.errorBenchTimer.start();
        timer.errorBenchTicks.start();
#ifdef MAYA_PROFILE
        MProfilingScope setParamScope(profileCategory, MProfiler::kColorA_L1,
                                      "measure errors");
#endif
        // Based on only the changed attribute value only
        // measure the markers that can modify the attribute -
        // we do this using 'frameIndexEnabled' and
        // 'evalMeasurements'.
        measureErrors(numberOfErrors, numberOfMarkerErrors,
                      numberOfAttrStiffnessErrors, numberOfAttrSmoothnessErrors,
                      frameIndexEnabled, evalMeasurements, imageWidth,
                      &errorListA[0], userData, error_avg_tmp, error_max_tmp,
                      error_min_tmp, status);
        timer.errorBenchTimer.stop();
        timer.errorBenchTicks.stop();
    }

    if (autoDiffType == AUTO_DIFF_TYPE_FORWARD) {
        MMSOLVER_ASSERT(userData->solverOptions->solverSupportsAutoDiffForward,
                        "The solver must support forward differentiation.");
        // Set the Jacobian matrix using the previously
        // calculated errors (original and A).
        const double inv_delta = 1.0 / deltaA;
        for (size_t j = 0; j < errorListA.size(); ++j) {
            const size_t num = (parameterIndex * ldfjac) + j;
            const double x = (errorListA[j] - errors[j]) * inv_delta;
            userData->jacobianList[num] = x;
            jacobian[num] = x;
        }

    } else if (autoDiffType == AUTO_DIFF_TYPE_CENTRAL) {
        MMSOLVER_ASSERT(userData->solverOptions->solverSupportsAutoDiffCentral,
                        "The solver must support central differentiation.");
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
        const double deltaB = calculateParameterDelta(value, delta, -1, attr);
        if (deltaA == deltaB) {
            // Set the Jacobian matrix using the previously
            // calculated errors (original and A).
            const double inv_delta = 1.0 / deltaA;
            for (size_t j = 0; j < errorListA.size(); ++j) {
                const size_t num = (parameterIndex * ldfjac) + j;
                const double x = (errorListA[j] - errors[j]) * inv_delta;
                userData->jacobianList[num] = x;
                jacobian[num] = x;
            }
        } else {
            incrementJacobianIteration(userData);
            paramListB[parameterIndex] = paramListB[parameterIndex] + deltaB;
            {
                timer.paramBenchTimer.start();
                timer.paramBenchTicks.start();
#ifdef MAYA_PROFILE
                MProfilingScope setParamScope(
                    profileCategory, MProfiler::kColorA_L2, "set parameters");
#endif
                status =
                    setParameters(numberOfParameters, &paramListB[0], userData);
                timer.paramBenchTimer.stop();
                timer.paramBenchTicks.stop();
            }

            error_avg_tmp = 0;
            error_max_tmp = 0;
            error_min_tmp = 0;
            {
                timer.errorBenchTimer.start();
                timer.errorBenchTicks.start();
#ifdef MAYA_PROFILE
                MProfilingScope setParamScope(
                    profileCategory, MProfiler::kColorA_L1, "measure errors");
#endif
                measureErrors(numberOfErrors, numberOfMarkerErrors,
                              numberOfAttrStiffnessErrors,
                              numberOfAttrSmoothnessErrors, frameIndexEnabled,
                              evalMeasurements, imageWidth, &errorListB[0],
                              userData, error_avg_tmp, error_max_tmp,
                              error_min_tmp, status);
                timer.errorBenchTimer.stop();
                timer.errorBenchTicks.stop();
            }

            // Set the Jacobian matrix using the previously
            // calculated errors (A and B).
            MMSOLVER_ASSERT(errorListA.size() == errorListB.size(),
                            "errors A and B must be the same size.");
            double inv_delta = 0.5 / (std::fabs(deltaA) + std::fabs(deltaB));
            for (size_t j = 0; j < errorListA.size(); ++j) {
                size_t num = (parameterIndex * ldfjac) + j;
                double x = (errorListA[j] - errorListB[j]) * inv_delta;
                userData->jacobianList[num] = x;
                jacobian[num] = x;
            }
        }
    }

    return SOLVE_FUNC_SUCCESS;
}

// Calculate Jacobian Matrix
int solveFunc_calculateJacobianMatrix(
    const int numberOfMarkerErrors, const int numberOfAttrStiffnessErrors,
    const int numberOfAttrSmoothnessErrors, const int numberOfMarkers,
    const int profileCategory, const double imageWidth,
    const int numberOfParameters, const int numberOfErrors,
    const double *parameters, double *errors, double *jacobian,
    SolverData *userData, SolverTimer &timer) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("adjust_solveFunc solveFunc_calculateJacobianMatrix");

    MMSOLVER_ASSERT(
        (userData->solverOptions->solverType == SOLVER_TYPE_CMINPACK_LMDER) ||
            (userData->solverOptions->solverType == SOLVER_TYPE_CERES_LMDER),
        "Only CMinpack LMDER and Ceres LMDER can calculate a jacobian matrix "
        "manually.");
    int autoDiffType = userData->solverOptions->autoDiffType;

    // Get longest dimension for jacobian matrix
    int ldfjac = numberOfErrors;
    if (ldfjac < numberOfParameters) {
        ldfjac = numberOfParameters;
    }

    const int progressMin = userData->computation->progressMin();
    const int progressMax = userData->computation->progressMax();
    userData->computation->setProgress(progressMin);

    std::vector<bool> evalMeasurements(numberOfMarkers, false);
    determineMarkersToBeEvaluated(numberOfParameters, numberOfMarkers,
                                  userData->solverOptions->delta,
                                  userData->previousParamList, parameters,
                                  userData->errorToParamMatrix, evalMeasurements);

    // Calculate the jacobian matrix.
    std::vector<double> paramListA(numberOfParameters, 0);
    std::vector<double> errorListA(numberOfErrors, 0);
    for (int i = 0; i < numberOfParameters; ++i) {
        int result = solveFunc_calculateJacobianMatrixForParameter(
            i, progressMin, progressMax, paramListA, errorListA,
            evalMeasurements, autoDiffType, ldfjac,

            numberOfMarkerErrors, numberOfAttrStiffnessErrors,
            numberOfAttrSmoothnessErrors, imageWidth, numberOfParameters,
            numberOfErrors, parameters, errors, jacobian, userData, timer);
        if (result == SOLVE_FUNC_FAILURE) {
            return result;
        }
    }

    return SOLVE_FUNC_SUCCESS;
}

// Function run by solver algorithm to test the input parameters,
// 'parameters', and compute the output errors, 'errors'.
int solveFunc(const int numberOfParameters, const int numberOfErrors,
              const double *parameters, double *errors, double *jacobian,
              void *rawUserData) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("adjust_solveFunc solveFunc");

    SolverData *userData = static_cast<SolverData *>(rawUserData);
    userData->timer.funcBenchTimer.start();
    userData->timer.funcBenchTicks.start();

    MMSOLVER_MAYA_VRB(
        "adjust_solverFunc solveFunc "
        "isPrintCall: "
        << userData->isPrintCall);
    MMSOLVER_MAYA_VRB(
        "adjust_solverFunc solveFunc "
        "isNormalCall: "
        << userData->isNormalCall);
    MMSOLVER_MAYA_VRB(
        "adjust_solverFunc solveFunc "
        "isJacobianCall: "
        << userData->isJacobianCall);
    MMSOLVER_MAYA_VRB(
        "adjust_solverFunc solveFunc "
        "doCalcJacobian: "
        << userData->doCalcJacobian);

    auto imageWidth = userData->solverOptions->imageWidth;

    const auto frameListLength = userData->frameList.length();
    auto frameCount = frameListLength;
    if (!userData->doCalcJacobian && frameCount > 1) {
        userData->computation->setProgress(userData->iterNum);
    }

    const int numberOfMarkerErrors = userData->numberOfMarkerErrors;
    const int numberOfAttrStiffnessErrors =
        userData->numberOfAttrStiffnessErrors;
    const int numberOfAttrSmoothnessErrors =
        userData->numberOfAttrSmoothnessErrors;
    const int numberOfMarkers = numberOfMarkerErrors / ERRORS_PER_MARKER;
    MMSOLVER_ASSERT(
        userData->errorToParamMatrix.width() ==
            static_cast<size_t>(numberOfMarkers),
        "Marker count and width of 'errorToParamMatrix' must match.");

    if (userData->isNormalCall) {
        incrementNormalIteration(userData);
    } else if (userData->isJacobianCall && !userData->doCalcJacobian) {
        incrementJacobianIteration(userData);
    }

    if (userData->isPrintCall) {
        // insert print statements here when nprint is positive.
        //
        // if the nprint parameter to 'lmdif' or 'lmder' is positive,
        // the function is called every nprint iterations with iflag=0,
        // so that the function may perform special operations, such as
        // printing residuals.
        return SOLVE_FUNC_SUCCESS;
    }

    if (userData->computation->isInterruptRequested()) {
        MMSOLVER_MAYA_WRN("User wants to cancel the solve!");
        userData->userInterrupted = true;
        return SOLVE_FUNC_FAILURE;
    }

    if (verbose) {
        for (auto i = 0; i < numberOfParameters; i++) {
            MMSOLVER_MAYA_VRB(
                "adjust_solveFunc solveFunc "
                "parameters["
                << i << "] = " << parameters[i]);
        }
    }

#ifdef MAYA_PROFILE
    const int profileCategory = MProfiler::getCategoryIndex("mmSolver");
    MProfilingScope iterScope(profileCategory, MProfiler::kColorC_L1,
                              "iteration");
#else
    const int profileCategory = 0;
#endif

    const bool interactive =
        userData->mayaSessionState == MGlobal::MMayaState::kInteractive;
    const bool sceneGraphIsMayaDAG =
        userData->solverOptions->sceneGraphMode == SceneGraphMode::kMayaDag;
    if (interactive && sceneGraphIsMayaDAG) {
        MString dgDirtyCmd =
            generateDirtyCommand(numberOfMarkerErrors, userData);
        MGlobal::executeCommand(dgDirtyCmd);
    }

    // Calculate residual errors, or jacobian matrix?
    double error_avg = 0;
    double error_max = 0;
    double error_min = 0;
    int calculation_status = SOLVE_FUNC_SUCCESS;
    if (!userData->doCalcJacobian) {
        calculation_status = solveFunc_measureErrors(
            numberOfMarkerErrors, numberOfAttrStiffnessErrors,
            numberOfAttrSmoothnessErrors, numberOfMarkers, frameListLength,
            profileCategory, imageWidth, numberOfParameters, numberOfErrors,
            parameters, errors, jacobian, userData, userData->timer, error_avg,
            error_max, error_min);
    } else {
        calculation_status = solveFunc_calculateJacobianMatrix(
            numberOfMarkerErrors, numberOfAttrStiffnessErrors,
            numberOfAttrSmoothnessErrors, numberOfMarkers, profileCategory,
            imageWidth, numberOfParameters, numberOfErrors, parameters, errors,
            jacobian, userData, userData->timer);
    }
    userData->timer.funcBenchTimer.stop();
    userData->timer.funcBenchTicks.stop();

    if (verbose) {
        for (auto i = 0; i < numberOfErrors; i++) {
            MMSOLVER_MAYA_VRB(
                "adjust_solveFunc solveFunc "
                "residuals["
                << i << "] = " << errors[i]);
        }

        if (userData->doCalcJacobian) {
            const int numberOfJacobians = numberOfParameters * numberOfErrors;
            for (auto i = 0; i < numberOfJacobians; i++) {
                MMSOLVER_MAYA_VRB(
                    "adjust_solveFunc solveFunc "
                    "jacobian["
                    << i << "] = " << jacobian[i]);
            }
        }
    }

    if (calculation_status == SOLVE_FUNC_FAILURE) {
        return calculation_status;
    }

    if (userData->isNormalCall) {
        if (userData->logLevel >= LogLevel::kVerbose) {
            char formatBuffer[128];
            sprintf(formatBuffer, " | error avg %8.4f   min %8.4f   max %8.4f",
                    error_avg, error_min, error_max);
            MStreamUtils::stdErrorStream() << std::string(formatBuffer) << "\n";
        }
    } else {
        if (userData->logLevel >= LogLevel::kDebug) {
            if (!userData->doCalcJacobian) {
                std::cerr << "\n";
            }
        }
    }

    return SOLVE_FUNC_SUCCESS;
}

}  // namespace mmsolver
