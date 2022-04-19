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
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdlib>
#include <ctime>
#include <iostream>
#include <limits>
#include <memory>
#include <stdio.h>
#include <string>
#include <vector>

// Maya
#include <maya/MAnimCurveChange.h>
#include <maya/MComputation.h>
#include <maya/MDagPath.h>
#include <maya/MDGContext.h>
#include <maya/MFnAnimCurve.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MFnPluginData.h>
#include <maya/MGlobal.h>
#include <maya/MMatrix.h>
#include <maya/MObject.h>
#include <maya/MPoint.h>
#include <maya/MProfiler.h>
#include <maya/MStreamUtils.h>
#include <maya/MSelectionList.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MVector.h>

#if MAYA_API_VERSION >= 20180000
#include <maya/MDGContextGuard.h>
#endif

// MM Solver
#include "mmSolver/core/mmdata.h"
#include "mmSolver/core/mmmath.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_attr.h"
#include "mmSolver/utilities/number_utils.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/string_utils.h"
#include "adjust_base.h"
#include "adjust_data.h"
#include "adjust_lensModel.h"
#include "adjust_setParameters.h"
#include "adjust_measureErrors.h"


// Per-attribute type delta values
#define PER_ATTR_TYPE_DELTA_VALUE 1



inline
int getStringArrayIndexOfValue(MStringArray &array, MString &value) {
#if MAYA_API_VERSION >= 201700
    return array.indexOf(value);
#else
    int index = -1;
    for (unsigned int i=0; i<array.length(); ++i) {
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
MString generateDirtyCommand(int numberOfMarkerErrors, SolverData *ud) {
    MString dgDirtyCmd = "dgdirty ";
    MStringArray dgDirtyNodeNames;
    for (int i = 0; i < (numberOfMarkerErrors / ERRORS_PER_MARKER); ++i) {
        IndexPair markerPair = ud->errorToMarkerList[i];

        MarkerPtr marker = ud->markerList[markerPair.first];
        MString markerName = marker->getNodeName();
        const int markerName_idx = getStringArrayIndexOfValue(
            dgDirtyNodeNames,
            markerName);
        if (markerName_idx == -1) {
            dgDirtyCmd += " \"" + markerName + "\" ";
            dgDirtyNodeNames.append(markerName);
        }

        CameraPtr camera = marker->getCamera();
        MString cameraTransformName = camera->getTransformNodeName();
        MString cameraShapeName = camera->getShapeNodeName();
        const int cameraTransformName_idx = getStringArrayIndexOfValue(
            dgDirtyNodeNames,
            cameraTransformName);
        if (cameraTransformName_idx == -1) {
            dgDirtyCmd += " \"" + cameraTransformName + "\" ";
            dgDirtyNodeNames.append(cameraTransformName);
        }
        const int cameraShapeName_idx =  getStringArrayIndexOfValue(
            dgDirtyNodeNames,
            cameraShapeName);
        if (cameraShapeName_idx == -1) {
            dgDirtyCmd += " \"" + cameraShapeName + "\" ";
            dgDirtyNodeNames.append(cameraShapeName);
        }

        BundlePtr bundle = marker->getBundle();
        MString bundleName = bundle->getNodeName();
        const int bundleName_idx = getStringArrayIndexOfValue(
            dgDirtyNodeNames,
            bundleName);
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
double calculateParameterDelta(const double value,
                               const double delta,
                               const double sign,
                               AttrPtr &attr) {
    MStatus status = MS::kSuccess;
    const double xmin = attr->getMinimumValue();
    const double xmax = attr->getMaximumValue();

    double new_delta = delta;
#if PER_ATTR_TYPE_DELTA_VALUE == 1
    // Relative delta for different types of solver attribute types.
    const auto object_type = attr->getObjectType();
    const auto solver_attr_type = attr->getSolverAttrType();
    if (object_type == ObjectType::kCamera
        && (solver_attr_type == AttrSolverType::kCameraFocal)) {
        new_delta *= 0.1;
    } else if (object_type == ObjectType::kLens) {
        new_delta *= 0.01;
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
void determineMarkersToBeEvaluated(int numberOfParameters,
                                   int numberOfMarkers,
                                   double delta,
                                   std::vector<double> previousParamList,
                                   const double *parameters,
                                   std::vector<std::vector<bool>> errorToParamList,
                                   std::vector<bool> &evalMeasurements) {
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
    evalMeasurements.resize((unsigned long) numberOfMarkers, false);
    for (size_t i = 0; i < evalCount.size(); ++i) {
        evalMeasurements[i] = static_cast<bool>(evalCount[i] > 0);
    }
    return;
}


// Add another 'normal function' evaluation to the count.
void incrementNormalIteration(SolverData *ud) {
    ++ud->funcEvalNum;
    ++ud->iterNum;
    MStreamUtils::stdErrorStream() << "Iteration ";
    MStreamUtils::stdErrorStream() << std::right << std::setfill ('0') << std::setw(4)
                                   << ud->iterNum;
    MStreamUtils::stdErrorStream() << " | Eval ";
    MStreamUtils::stdErrorStream() << std::right << std::setfill ('0') << std::setw(4)
                                   << ud->funcEvalNum;
    return;
}


// Add another 'jacobian function' evaluation to the count.
void incrementJacobianIteration(SolverData *ud) {
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
    return;
}


// Function run by cminpack algorithm to test the input parameters, p,
// and compute the output errors, x.
int solveFunc(const int numberOfParameters,
              const int numberOfErrors,
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
    assert(ud->errorToParamList.size() == static_cast<size_t>(numberOfMarkers));

    if (ud->isNormalCall) {
        incrementNormalIteration(ud);
    } else if (ud->isJacobianCall && !ud->doCalcJacobian) {
        incrementJacobianIteration(ud);
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
        MMSOLVER_WRN("User wants to cancel the evaluation!");
        ud->userInterrupted = true;
        return SOLVE_FUNC_FAILURE;
    }

#ifdef MAYA_PROFILE
    int profileCategory = MProfiler::getCategoryIndex("mmSolver");
    MProfilingScope iterScope(profileCategory,
                              MProfiler::kColorC_L1,
                              "iteration");
#endif

    const bool interactive = ud->mayaSessionState == MGlobal::MMayaState::kInteractive;
    const bool sceneGraphIsMayaDAG = ud->solverOptions->sceneGraphMode == SceneGraphMode::kMayaDag;
    if (interactive && sceneGraphIsMayaDAG) {
        MString dgDirtyCmd = generateDirtyCommand(numberOfMarkerErrors, ud);
        MGlobal::executeCommand(dgDirtyCmd);
    }

    // Calculate residual errors, or jacobian matrix?
    double error_avg = 0;
    double error_max = 0;
    double error_min = 0;
    if (ud->doCalcJacobian == false) {
        // A normal evaluation of the errors and parameters.
        std::vector<bool> evalMeasurements(numberOfMarkers, true);
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
            status = setParameters(
                    numberOfParameters,
                    parameters,
                    ud);
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
            measureErrors(numberOfErrors,
                          numberOfMarkerErrors,
                          numberOfAttrStiffnessErrors,
                          numberOfAttrSmoothnessErrors,
                          frameIndexEnable,
                          evalMeasurements,
                          errors,
                          ud,
                          error_avg, error_max, error_min,
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

        std::vector<bool> evalMeasurements(numberOfMarkers, false);
        determineMarkersToBeEvaluated(
                numberOfParameters,
                numberOfMarkers,
                ud->solverOptions->delta,
                ud->previousParamList,
                parameters,
                ud->errorToParamList,
                evalMeasurements);

        // Calculate the jacobian matrix.
        std::vector<double> paramListA(numberOfParameters, 0);
        std::vector<double> errorListA(numberOfErrors, 0);
        for (int i = 0; i < numberOfParameters; ++i) {
            double ratio = (double) i / (double) numberOfParameters;
            int progressNum = progressMin + static_cast<int>(ratio * progressMax);
            ud->computation->setProgress(progressNum);

            if (ud->computation->isInterruptRequested()) {
                MMSOLVER_WRN("User wants to cancel the evaluation!");
                ud->userInterrupted = true;
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
                    value, delta, 1, attr);

            std::vector<bool> frameIndexEnabled = ud->paramFrameList[i];

            incrementJacobianIteration(ud);
            paramListA[i] = paramListA[i] + deltaA;
            {
                ud->timer.paramBenchTimer.start();
                ud->timer.paramBenchTicks.start();
#ifdef MAYA_PROFILE
                MProfilingScope setParamScope(profileCategory,
                                              MProfiler::kColorA_L2,
                                              "set parameters");
#endif
                status = setParameters(
                        numberOfParameters,
                        &paramListA[0],
                        ud);
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
                // 'evalMeasurements'.
                measureErrors(numberOfErrors,
                              numberOfMarkerErrors,
                              numberOfAttrStiffnessErrors,
                              numberOfAttrSmoothnessErrors,
                              frameIndexEnabled,
                              evalMeasurements,
                              &errorListA[0],
                              ud,
                              error_avg_tmp,
                              error_max_tmp,
                              error_min_tmp,
                              status);
                ud->timer.errorBenchTimer.stop();
                ud->timer.errorBenchTicks.stop();
            }

            if (autoDiffType == AUTO_DIFF_TYPE_FORWARD) {
                assert(ud->solverOptions->solverSupportsAutoDiffForward);
                // Set the Jacobian matrix using the previously
                // calculated errors (original and A).
                double inv_delta = 1.0 / deltaA;
                for (size_t j = 0; j < errorListA.size(); ++j) {
                    size_t num = (i * ldfjac) + j;
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
                        value, delta, -1, attr);
                if (deltaA == deltaB) {
                    // Set the Jacobian matrix using the previously
                    // calculated errors (original and A).
                    double inv_delta = 1.0 / deltaA;
                    for (size_t j = 0; j < errorListA.size(); ++j) {
                        size_t num = (i * ldfjac) + j;
                        double x = (errorListA[j] - errors[j]) * inv_delta;
                        ud->jacobianList[num] = x;
                        jacobian[num] = x;
                    }
                } else {

                    incrementJacobianIteration(ud);
                    paramListB[i] = paramListB[i] + deltaB;
                    {
                        ud->timer.paramBenchTimer.start();
                        ud->timer.paramBenchTicks.start();
#ifdef MAYA_PROFILE
                        MProfilingScope setParamScope(profileCategory,
                                                      MProfiler::kColorA_L2,
                                                      "set parameters");
#endif
                        status = setParameters(
                                numberOfParameters,
                                &paramListB[0],
                                ud);
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
                        measureErrors(numberOfErrors,
                                      numberOfMarkerErrors,
                                      numberOfAttrStiffnessErrors,
                                      numberOfAttrSmoothnessErrors,
                                      frameIndexEnabled,
                                      evalMeasurements,
                                      &errorListB[0],
                                      ud,
                                      error_avg_tmp,
                                      error_max_tmp,
                                      error_min_tmp,
                                      status);
                        ud->timer.errorBenchTimer.stop();
                        ud->timer.errorBenchTicks.stop();
                    }

                    // Set the Jacobian matrix using the previously
                    // calculated errors (A and B).
                    assert(errorListA.size() == errorListB.size());
                    double inv_delta = 0.5 / (std::fabs(deltaA) + std::fabs(deltaB));
                    for (size_t j = 0; j < errorListA.size(); ++j) {
                        size_t num = (i * ldfjac) + j;
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
