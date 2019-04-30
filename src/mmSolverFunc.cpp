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
#include <cminpack.h>  // lmdif
#endif

// Lev-Mar
#ifdef USE_SOLVER_LEVMAR
#include <levmar.h>  // dlevmar_dif
#endif

// STL
#include <ctime>     // time
#include <cmath>     // exp, log
#include <iostream>  // cout, cerr, endl
#include <string>    // string
#include <vector>    // vector
#include <cassert>   // assert
#include <limits>    // double max value, NaN
#include <algorithm>  // min, max
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
#include <mmSolver.h>
#include <mmSolverFunc.h>
#include <mmSolverCMinpack.h>
#include <mmSolverLevMar.h>

#define FABS(x)     (((x)>=0)? (x) : -(x))

// NOTE: There is a very strange bug in Maya. After setting a number
// of plug values using a DG Context, when quering plug values at the
// same times, the values do not evaluate correctly. To 'trick' Maya
// into triggering an eval the next time a plug is queried we query
// the matrix of a marker node. It doesn't matter which marker node,
// however it does matter that it's a marker node, if the eval is
// performed with a bundle node the error continues to happen.
#define FORCE_TRIGGER_EVAL 1


// Function run by cminpack algorithm to test the input parameters, p,
// and compute the output errors, x.
int solveFunc(int numberOfParameters,
              int numberOfErrors,
              const double *parameters,
              double *errors,
              void *userData) {
    register int i = 0;

    SolverData *ud = static_cast<SolverData *>(userData);
    ud->funcBenchTimer->start();
    ud->funcBenchTicks->start();
    ud->computation->setProgress(ud->iterNum);

    // Seems heavy we are opening and closing a file each iteration.
    std::ofstream debugFile;
    if (ud->debugFileName.length() > 0) {
        const char *debugFileChar = ud->debugFileName.asChar();
        debugFile.open(debugFileChar, std::ios_base::app);
    }
    bool debugIsOpen = debugFile.is_open();

    if (ud->isNormalCall) {
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
    } else if (ud->isJacobianCall) {
         ++ud->jacIterNum;
         if (ud->verbose == true) {
              std::cout << "Eval Jacobian " << ud->jacIterNum;
         }
         if (debugIsOpen == true) {
              debugFile << std::endl
                        << "iteration jacobian: " << ud->jacIterNum
                        << std::endl;
         }
    }

    if (ud->isPrintCall) {
      // insert print statements here when nprint is positive.
      //
      // if the nprint parameter to lmdif is positive, the function is
      // called every nprint iterations with iflag=0, so that the
      // function may perform special operations, such as printing
      // residuals.
      return SOLVE_FUNC_SUCCESS;
    }

#ifdef MAYA_PROFILE
    int profileCategory = MProfiler::getCategoryIndex("mmSolver");
    MProfilingScope iterScope(profileCategory,
                              MProfiler::kColorC_L1,
                              "iteration");
#endif

    if (ud->computation->isInterruptRequested()) {
        WRN("User wants to cancel the evalutation!");
        ud->userInterrupted = true;
        return SOLVE_FUNC_FAILURE;
    }

    MGlobal::executeCommand("dgdirty -allPlugs -implicit;");

    // Set Parameter
    MStatus status;
    {
        ud->paramBenchTimer->start();
        ud->paramBenchTicks->start();
#ifdef MAYA_PROFILE
        MProfilingScope setParamScope(profileCategory,
                                      MProfiler::kColorA_L2,
                                      "set parameters");
#endif

        MTime currentFrame = MAnimControl::currentTime();
        for (i = 0; i < numberOfParameters; ++i) {
            IndexPair attrPair = ud->paramToAttrList[i];
            AttrPtr attr = ud->attrList[attrPair.first];

            double xmin = attr->getMinimumValue();
            double xmax = attr->getMaximumValue();
            double value = parameters[i];

            // TODO: Implement proper Box Constraints; Issue #64.
            value = std::max<double>(value, xmin);
            value = std::min<double>(value, xmax);

            // Get frame time
            MTime frame = currentFrame;
            if (attrPair.second != -1) {
                frame = ud->frameList[attrPair.second];
            }

            if (debugIsOpen == true) {
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
        for (i = 0; i < (int) ud->cameraList.size(); ++i) {
            ud->cameraList[i]->clearAttrValueCache();
        }
        ud->paramBenchTimer->stop();
        ud->paramBenchTicks->stop();
    }

    MGlobal::executeCommand("dgdirty -allPlugs -implicit;");

    // Measure Errors
    double error_avg = 0.0;
    double error_max = -0.0;
    double error_min = std::numeric_limits<double>::max();
    {
        ud->errorBenchTimer->start();
        ud->errorBenchTicks->start();
#ifdef MAYA_PROFILE
        MProfilingScope setParamScope(profileCategory,
                                      MProfiler::kColorA_L1,
                                      "measure errors");
#endif

#if FORCE_TRIGGER_EVAL == 1
        {
            MPoint pos;
            i = 0;
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
        for (i = 0; i < (numberOfErrors / ERRORS_PER_MARKER); ++i) {
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
        ud->errorBenchTimer->stop();
        ud->errorBenchTicks->stop();
    }
    ud->funcBenchTimer->stop();
    ud->funcBenchTicks->stop();

    error_avg *= 1.0 / (numberOfErrors / ERRORS_PER_MARKER);

    if (debugIsOpen == true) {
         for (i = 0; i < (numberOfErrors / ERRORS_PER_MARKER); ++i) {
              debugFile << "error i=" << i
                        << " x=" << ud->errorList[(i * ERRORS_PER_MARKER) + 0]
                        << " y=" << ud->errorList[(i * ERRORS_PER_MARKER) + 1]
#if ERRORS_PER_MARKER == 3
                        << " z=" << ud->errorList[(i * ERRORS_PER_MARKER) + 2]
#endif
                        << std::endl;
         }
         for (i = 0; i < (numberOfErrors / ERRORS_PER_MARKER); ++i) {
              debugFile << "error dist i=" << i
                        << " v=" << ud->errorDistanceList[i]
                        << std::endl;
         }
         debugFile << "emin=" << error_min
                   << " emax=" << error_max
                   << " eavg=" << error_avg
                   << std::endl;
    }

    if (ud->verbose == true) {
        if (ud->isNormalCall) {
            std::cout << " | error avg=" << error_avg
                      << " min=" << error_min
                      << " max=" << error_max
                      << std::endl;;
        } else {
            std::cout << std::endl;
        }
    }
    return SOLVE_FUNC_SUCCESS;
}

// Clean up #define
#undef FABS
#undef FORCE_TRIGGER_EVAL
