/*
 * Uses Non-Linear Least Squares algorithm to calculate attribute values based on 2D-to-3D error measurements through a pinhole camera.
 */

#include <mmSolverCeres.h>

// STL
#include <ctime>     // time
#include <cmath>     // exp
#include <iostream>  // cout, cerr, endl
#include <string>    // string
#include <vector>    // vector
#include <cassert>   // assert
#include <limits>    // double max value
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


ReprojectionErrorFunctor::ReprojectionErrorFunctor(CeresSolverData &data) {
    m_solverData = data;
}


bool
ReprojectionErrorFunctor::operator()(double const* const* parameters,
                                     double* residuals) const {
    // This function calculates the errors.
    // TODO: Create a template to evaluate in both LevMar and Ceres.

    register int i = 0;
    register bool verbose = false;

    // Create the variable names the same as LevMar.
    int m = 12; // number of parameters/unknowns
    int n = 36; // number of errors
    const double* p = parameters[0];
    double* x = residuals;


    CeresSolverData *ud = const_cast<CeresSolverData*>(&m_solverData);
    ud->funcBenchTimer->start();
    ud->funcBenchTicks->start();
    ud->computation->setProgress(ud->iterNum);
    verbose = ud->verbose;
    if (ud->isJacobianCalculation == false) {
        std::cout << "Solve " << ++ud->iterNum;
    } else {
        std::cout << "Solve Jacobian " << ++ud->jacIterNum;
    }

    int profileCategory = MProfiler::getCategoryIndex("mmSolver");
    MProfilingScope iterScope(profileCategory, MProfiler::kColorC_L1, "iteration");

    if (ud->computation->isInterruptRequested()) {
        WRN("User wants to cancel the solve!");
        return false; // Ceres sees this as a failed calculation.
    }

    // Set Parameter
    MStatus status;
    {
        ud->paramBenchTimer->start();
        ud->paramBenchTicks->start();
        MProfilingScope setParamScope(profileCategory, MProfiler::kColorA_L2, "set parameters");

        MTime currentFrame = MAnimControl::currentTime();
        for (i = 0; i < m; ++i) {
            std::pair<int, int> attrPair = ud->paramToAttrList[i];
            AttrPtr attr = ud->attrList[attrPair.first];

            // Get frame time
            MTime frame = currentFrame;
            if (attrPair.second != -1) {
                frame = ud->frameList[attrPair.second];
            }

            attr->setValue(p[i], frame, *ud->dgmod, *ud->curveChange);
        }

        // Commit changed data into Maya
        ud->dgmod->doIt();

        // Invalidate the Camera Matrix cache.
        // In future we might be able to auto-detect if the camera will change based on
        // the current solve and not invalidate the cache but for now we cannot take the
        // risk of an incorrect solve; we clear the cache.
        for (i = 0; i < (int) ud->cameraList.size(); ++i) {
            ud->cameraList[i]->clearWorldProjMatrixCache();
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
        MProfilingScope setParamScope(profileCategory, MProfiler::kColorA_L1, "measure errors");

#if FORCE_TRIGGER_EVAL == 1
        {
            MPoint pos;
            i = 0;
            std::pair<int, int> markerPair = ud->errorToMarkerList[i];
            MarkerPtr marker = ud->markerList[markerPair.first];
            MTime frame = ud->frameList[markerPair.second];
            status = marker->getPos(pos, frame + 1);
            CHECK_MSTATUS(status);
        }
#endif

        MMatrix cameraWorldProjectionMatrix;
        MPoint mkr_mpos;
        MPoint bnd_mpos;
        for (i = 0; i < (n / ERRORS_PER_MARKER); ++i) {
            std::pair<int, int> markerPair = ud->errorToMarkerList[i];
            MarkerPtr marker = ud->markerList[markerPair.first];
            MTime frame = ud->frameList[markerPair.second];

            CameraPtr camera = marker->getCamera();
            status = camera->getWorldProjMatrix(cameraWorldProjectionMatrix, frame);
            CHECK_MSTATUS(status);

            BundlePtr bnd = marker->getBundle();

            // TODO: If we convert these points into normalised image-space
            // then we can pre-compute the marker positions, this might have
            // a signficant performance improvement.
            status = marker->getPos(mkr_mpos, frame);
            CHECK_MSTATUS(status);
            mkr_mpos = mkr_mpos * cameraWorldProjectionMatrix;
            mkr_mpos.cartesianize();

            status = bnd->getPos(bnd_mpos, frame);
            CHECK_MSTATUS(status);
            bnd_mpos = bnd_mpos * cameraWorldProjectionMatrix;
            bnd_mpos.cartesianize();

            // NOTE: Interestingly, using an x, y and distance error measurement
            // seems to allow at least some scenes to converge much faster;
            // ~20 iterations compared to ~160 iterations.
            // TODO: dx, dy and d are all in world units. We should shift them
            // into 'image space', so that we can refer to the error in
            // terms of pixels.
            double dx = fabs(mkr_mpos.x - bnd_mpos.x);
            double dy = fabs(mkr_mpos.y - bnd_mpos.y);
            double d = distance_2d(mkr_mpos, bnd_mpos);

            x[(i * ERRORS_PER_MARKER) + 0] = dx;  // X error
            x[(i * ERRORS_PER_MARKER) + 1] = dy;  // Y error
            x[(i * ERRORS_PER_MARKER) + 2] = d;   // Distance error

            ud->errorList[(i * ERRORS_PER_MARKER) + 0] = dx;
            ud->errorList[(i * ERRORS_PER_MARKER) + 1] = dy;
            ud->errorList[(i * ERRORS_PER_MARKER) + 2] = d;

            error_avg += d;
            if (d > error_max) { error_max = d; }
            if (d < error_min) { error_min = d; }
        }
        ud->errorBenchTimer->stop();
        ud->errorBenchTicks->stop();
    }
    ud->funcBenchTimer->stop();
    ud->funcBenchTicks->stop();

    if (ud->isJacobianCalculation == false) {
        error_avg /= (n / ERRORS_PER_MARKER);
        INFO(" | error avg=" << error_avg << " min=" << error_min << " max=" << error_max);
    }


    return true;
}



