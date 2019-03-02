/*
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
#include <cmath>     // exp
#include <iostream>  // cout, cerr, endl
#include <string>    // string
#include <vector>    // vector
#include <cassert>   // assert
#include <limits>    // double max value, NaN
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
//
// *** Simulating box constraints (TODO) ***
//
// Note that box constraints can easily be simulated in C++ Minpack,
// using a change of variables in the function (that hint was found in
// the lmfit documentation).
//
// For example, say you want xmin[j] < x[j] < xmax[j], just apply the
// following change of variable at the beginning of fcn on the
// variables vector, and also on the computed solution after the
// optimization was performed:
//
//   for (j = 0; j < 3; ++j) {
//     real xmiddle = (xmin[j]+xmax[j])/2.;
//     real xwidth = (xmax[j]-xmin[j])/2.;
//     real th =  tanh((x[j]-xmiddle)/xwidth);
//     x[j] = xmiddle + th * xwidth;
//     jacfac[j] = 1. - th * th;
//   }
//
// This change of variables preserves the variables scaling, and is
// almost the identity near the middle of the interval.
//
// Of course, if you use lmder, lmder1, hybrj or hybrj1, the Jacobian
// must be also consistent with that new function, so the column of
// the original Jacobian corresponding to x1 must be multiplied by the
// derivative of the change of variable, i.e jacfac[j].
//
// Similarly, each element of the covariance matrix must be multiplied
// by jacfac[i]*jacfac[j].
//
// For examples on how to implement this in practice, see the portions
// of code delimited by "#ifdef BOX_CONSTRAINTS" in the following
// source files: tlmderc.c, thybrj.c, tchkderc.c.
//
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

    if (ud->verbose == true) {
        if (ud->isNormalCall) {
            // We're not using INFO macro because we don't want a
            // new-line created.
            std::cout << "Eval " << ++ud->iterNum;
        } else if (ud->isJacobianCall) {
            std::cout << "Eval Jacobian " << ++ud->jacIterNum;
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
        return SOLVE_FUNC_FAILURE;
    }

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

            // Get frame time
            MTime frame = currentFrame;
            if (attrPair.second != -1) {
                frame = ud->frameList[attrPair.second];
            }

            attr->setValue(parameters[i], frame, *ud->dgmod, *ud->curveChange);
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

            status = bnd->getPos(bnd_mpos, frame);
            CHECK_MSTATUS(status);
            bnd_mpos = bnd_mpos * cameraWorldProjectionMatrix;
            bnd_mpos.cartesianize();

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

    if (ud->verbose == true) {
        if (ud->isNormalCall) {
            error_avg *= 1.0 / (numberOfErrors / ERRORS_PER_MARKER);
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

