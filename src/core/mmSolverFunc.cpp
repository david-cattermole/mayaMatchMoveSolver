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

// Utils
#include <utilities/debugUtils.h>
#include <utilities/stringUtils.h>

// Maya
#include <maya/MPoint.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MObject.h>
#include <maya/MFnAnimCurve.h>
#include <maya/MAnimCurveChange.h>
#include <maya/MMatrix.h>
#include <maya/MComputation.h>
#include <maya/MProfiler.h>
#include <maya/MGlobal.h>

// Utilities
#include <mayaUtils.h>

// Local solvers
#include <core/mmSolver.h>
#include <core/mmSolverData.h>
#include <core/mmSolverFunc.h>
#include <core/mmSolverCMinpack.h>
#include <core/mmSolverLevMar.h>


// NOTE: There is a very strange bug in Maya. After setting a number
// of plug values using a DG Context, when quering plug values at the
// same times, the values do not evaluate correctly. To 'trick' Maya
// into triggering an eval the next time a plug is queried we query
// the matrix of a marker node. It doesn't matter which marker node,
// however it does matter that it's a marker node, if the eval is
// performed with a bundle node the error continues to happen.
#define FORCE_TRIGGER_EVAL 1


/*
 * Generate a 'dgdirty' MEL command listing all nodes that may be
 * changed by our solve function.
 */
MString generateDirtyCommand(int numberOfErrors, SolverData *ud) {
    MString dgDirtyCmd = "dgdirty ";
    MStringArray dgDirtyNodeNames;
    for (int i = 0; i < (numberOfErrors / ERRORS_PER_MARKER); ++i) {
        IndexPair markerPair = ud->errorToMarkerList[i];

        MarkerPtr marker = ud->markerList[markerPair.first];
        MString markerName = marker->getNodeName();
        if (dgDirtyNodeNames.indexOf(markerName) == -1) {
            dgDirtyCmd += " \"" + markerName + "\" ";
            dgDirtyNodeNames.append(markerName);
        }

        CameraPtr camera = marker->getCamera();
        MString cameraTransformName = camera->getTransformNodeName();
        MString cameraShapeName = camera->getShapeNodeName();
        if (dgDirtyNodeNames.indexOf(cameraTransformName) == -1) {
            dgDirtyCmd += " \"" + cameraTransformName + "\" ";
            dgDirtyNodeNames.append(cameraTransformName);
        }
        if (dgDirtyNodeNames.indexOf(cameraShapeName) == -1) {
            dgDirtyCmd += " \"" + cameraShapeName + "\" ";
            dgDirtyNodeNames.append(cameraShapeName);
        }

        BundlePtr bundle = marker->getBundle();
        MString bundleName = bundle->getNodeName();
        if (dgDirtyNodeNames.indexOf(bundleName) == -1) {
            dgDirtyCmd += " \"" + bundleName + "\" ";
            dgDirtyNodeNames.append(bundleName);
        }
    }
    dgDirtyCmd += ";";
    return dgDirtyCmd;
}


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
double calculateParameterDelta(int deltaDirection) {
    double delta = 1.0;

    // Get attribute

    // Determine the attribute 'type'.

    // Switch based on attribute type.
    // - Camera Translate
    //   - ???
    // - Camera Rotate X and Y (tilt and pan)
    //   - All camera rotations should be screen-space FOV degree
    //     values.
    //   - Calculate the Angle of View of the camera, width and height
    //     axis.
    //   - As a ratio of the camera FOV in width and height, use this
    //     to tilt and pan the camera attributes.
    // - Camera Rotate Z (roll)
    //   - Use a fixed value? The Camera FOV will not affect this
    //     method.
    // - Camera Scale
    //   - Throw an error - nobody should solve camera scale.
    //   - Or should we consider this a transform scale?
    //   - At the very least we should print-out a warning.
    // - Bundle Translate or Transform Translate
    //   - Get bundle world matrix
    //   - Create a new vector along the translate axis (x = (1, 0, 0))
    //   - Turn this vector into world space - we now have an axis
    //     pointing along the translate axis.
    //   - Measure the screen-space position at bundle world pos.
    //   - Measure the screen-space position at bundle world pos plus
    //     translate axis.
    //   - Compute the screen-space distance between two points.
    //   - Use this screen-space distance as the delta.
    // - Transform rotate
    //   - Calculate the rotation axis plane's area as seen in the
    //     current camera's FOV.
    // - Transform scale
    //   - Use a fixed ratio? Like 1 or 5 percent. *=1.05 and *=0.95?
    // - Focal length
    //   - Use a fixed ratio? *=1.05 and *=0.95?
    // - Attribute with min/max values.
    //   - Use a specific ratio, such as 1 percent.
    // - Misc attribute
    //   - Use a fixed number? 0.1?

    return delta;
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
        value = (value / scale) - offset;

        // TODO: Implement proper Box Constraints; Issue #64.
        value = std::max<double>(value, xmin);
        value = std::min<double>(value, xmax);

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


// Measure Errors
void measureErrors(
        int numberOfParameters,
        int numberOfErrors,
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

    MMatrix cameraWorldProjectionMatrix;
    MPoint mkr_mpos;
    MPoint bnd_mpos;
    for (int i = 0; i < (numberOfErrors / ERRORS_PER_MARKER); ++i) {
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

        double left = 0;
        double right = 0;
        double top = 0;
        double bottom = 0;
        camera->getFrustum(left, right, top, bottom, frame);

        BundlePtr bnd = marker->getBundle();

        // Use pre-computed marker position and weight
        mkr_mpos = ud->markerPosList[i];
        double mkr_weight = ud->markerWeightList[i];
        mkr_weight = std::sqrt(mkr_weight);

        MVector bnd_dir;
        status = bnd->getPos(bnd_mpos, frame);
        CHECK_MSTATUS(status);
        MPoint bnd_mpos_tmp(bnd_mpos);
        bnd_dir = bnd_mpos_tmp - cam_pos;
        bnd_dir.normalize();
        bnd_mpos = bnd_mpos * cameraWorldProjectionMatrix;
        bnd_mpos.cartesianize();

        // Is the bundle behind the camera?
        bool behind_camera = false;
        double cam_dot_bnd = cam_dir * bnd_dir;
        // WRN("Camera DOT Bundle: " << cam_dot_bnd);
        if (cam_dot_bnd < 0.0) {
            behind_camera = true;
        }

        if (writeDebug == true && debugIsOpen == true) {
            debugFile << "Bundle: " << bnd->getNodeName()
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
        double dx = fabs(mkr_mpos.x - bnd_mpos.x) * ((right - left) * ud->imageWidth);
        double dy = fabs(mkr_mpos.y - bnd_mpos.y) * ((right - left) * ud->imageWidth);
        double d = distance_2d(mkr_mpos, bnd_mpos) * ((right - left) * ud->imageWidth);

        errors[(i * ERRORS_PER_MARKER) + 0] = dx * mkr_weight;  // X error
        errors[(i * ERRORS_PER_MARKER) + 1] = dy * mkr_weight;  // Y error

        ud->errorList[(i * ERRORS_PER_MARKER) + 0] = dx;
        ud->errorList[(i * ERRORS_PER_MARKER) + 1] = dy;

#if ERRORS_PER_MARKER == 3
        // d = distance_2d(mkr_mpos, bnd_mpos) * ((right - left) * ud->imageWidth);
        errors[(i * ERRORS_PER_MARKER) + 2] = d * mkr_weight;   // Distance error
        ud->errorList[(i * ERRORS_PER_MARKER) + 2] = d;
#endif

        ud->errorDistanceList[i] = d;
        error_avg += d;
        if (d > error_max) { error_max = d; }
        if (d < error_min) { error_min = d; }
    }

    error_avg *= 1.0 / (numberOfErrors / ERRORS_PER_MARKER);

    if (writeDebug == true && debugIsOpen == true) {
        for (int i = 0; i < (numberOfErrors / ERRORS_PER_MARKER); ++i) {
            debugFile << "error i=" << i
                      << " x=" << ud->errorList[(i * ERRORS_PER_MARKER) + 0]
                      << " y=" << ud->errorList[(i * ERRORS_PER_MARKER) + 1]
#if ERRORS_PER_MARKER == 3
                      << " z=" << ud->errorList[(i * ERRORS_PER_MARKER) + 2]
#endif
                      << std::endl;
        }
        for (int i = 0; i < (numberOfErrors / ERRORS_PER_MARKER); ++i) {
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
    ++ud->iterNum;
    // We're not using INFO macro because we don't want a
    // new-line created.
    if (ud->verbose == true) {
        std::cout << "Eval " << ud->iterNum;
    }
    if (debugIsOpen == true) {
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
    ++ud->jacIterNum;
    if (ud->verbose == true) {
        if (ud->doCalcJacobian == false) {
            std::cout << "Eval Jacobian " << ud->jacIterNum;
        } else {
            std::cout << "Eval Jacobian " << ud->jacIterNum << std::endl;
        }
    }
    if (debugIsOpen == true) {
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
    if (ud->doCalcJacobian == false) {
        ud->computation->setProgress(ud->iterNum);
    }

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
    } else if (ud->isJacobianCall == true && ud->doCalcJacobian == false) {
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
        WRN("User wants to cancel the evalutation!");
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
        MString dgDirtyCmd = generateDirtyCommand(numberOfErrors, ud);
        MGlobal::executeCommand(dgDirtyCmd);
    }

    // Calculate residual errors, or jacobian matrix?
    double error_avg = 0;
    double error_max = 0;
    double error_min = 0;
    if (ud->doCalcJacobian == false) {
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
        assert(ud->solverOptions->solverType == SOLVER_TYPE_CMINPACK_LM_DER);
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
        writeDebug = true;
        for (int i = 0; i < numberOfParameters; ++i) {
            double ratio = (double) i / (double) numberOfParameters;
            ud->computation->setProgress(progressMin + (ratio * progressMax));

            if (ud->computation->isInterruptRequested()) {
                WRN("User wants to cancel the evalutation!");
                ud->userInterrupted = true;
                return SOLVE_FUNC_FAILURE;
            }

            // Create a copy of the parameters and errors.
            std::vector<double> paramListA(numberOfParameters, 0);
            for (int j = 0; j < numberOfParameters; ++j) {
                paramListA[j] = parameters[j];
            }
            std::vector<double> errorListA(numberOfErrors, 0);

            // // Calculate the relative delta for each parameter.
            // double delta = calculateParameterDelta()
            double delta = ud->solverOptions->delta;

            // // TODO: If the value +/- delta would cause the attribute to go out of
            // //   box-constraints, then we should only use one value, or go in
            // //   the other direction.
            // double sign = 1;  // or '-1' to set delta negative

            // TODO: Find a way to 'analytically' calculate the deviation of
            //   markers as will be affected by the new calculated delta
            //   value.  This will give us a jacobian matrix, without needing
            //   to set attribute values and re-evaluate them in Maya's DG.

            incrementJacobianIteration(ud, debugIsOpen, debugFile);
            paramListA[i] = paramListA[i] + delta;
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

            if (autoDiffType == CMINPACK_AUTO_DIFF_TYPE_FORWARD) {
                // Set the Jacobian matrix using the previously
                // calculated errors (original and A).
                double inv_delta = 1.0 / delta;
                for (int j = 0; j < errorListA.size(); ++j) {
                    int num = (i * ldfjac) + j;
                    double x = (errorListA[j] - errors[j]) * inv_delta;
                    ud->jacobianList[num] = x;
                    jacobian[num] = x;
                }

            } else if (autoDiffType == CMINPACK_AUTO_DIFF_TYPE_CENTRAL) {
                std::vector<double> paramListB(numberOfParameters, 0);
                for (int j = 0; j < numberOfParameters; ++j) {
                    paramListB[j] = parameters[j];
                }
                std::vector<double> errorListB(numberOfErrors, 0);

                incrementJacobianIteration(ud, debugIsOpen, debugFile);
                paramListB[i] = paramListB[i] - delta;
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
                double inv_delta = 0.5 / delta;
                for (int j = 0; j < errorListA.size(); ++j) {
                    int num = (i * ldfjac) + j;
                    double x = (errorListA[j] - errorListB[j]) * inv_delta;
                    ud->jacobianList[num] = x;
                    jacobian[num] = x;
                }
            }
        }
    }
    ud->timer.funcBenchTimer.stop();
    ud->timer.funcBenchTicks.stop();

    if (ud->verbose == true) {
        if (ud->isNormalCall) {
            std::cout << " | error avg=" << error_avg
                      << " min=" << error_min
                      << " max=" << error_max
                      << std::endl;;
        } else {
            if (ud->doCalcJacobian == false) {    
                std::cout << std::endl;
            }            
        }
    }
    return SOLVE_FUNC_SUCCESS;
}


// Clean up #define
#undef FORCE_TRIGGER_EVAL
