/*
 * Uses Non-Linear Least Squares algorithm to calculate attribute
 * values based on 2D-to-3D error measurements through a pinhole
 * camera.
 */

#include <mmSolverLevMar.h>

// Lev-Mar
#include <levmar.h>  // dlevmar_dif

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


#define FABS(x)     (((x)>=0)? (x) : -(x))

// NOTE: There is a very strange bug in Maya. After setting a number
// of plug values using a DG Context, when quering plug values at the
// same times, the values do not evaluate correctly. To 'trick' Maya
// into triggering an eval the next time a plug is queried we query
// the matrix of a marker node. It doesn't matter which marker node,
// however it does matter that it's a marker node, if the eval is
// performed with a bundle node the error continues to happen.
#define FORCE_TRIGGER_EVAL 1


// Function run by lev-mar algorithm to test the input parameters, p,
// and compute the output errors, x.
void levmarSolveFunc(double *p, double *x, int m, int n, void *data) {
    register int i = 0;
    register bool verbose = false;
    LevMarSolverData *ud = static_cast<LevMarSolverData *>(data);
    ud->funcBenchTimer->start();
    ud->funcBenchTicks->start();
    ud->computation->setProgress(ud->iterNum);
    verbose = ud->verbose;
    if (ud->isJacobianCalculation == false) {
        // We're not using INFO macro because we don't want a new-line
        // created.
        std::cout << "Solve " << ++ud->iterNum;
    } else {
        INFO("Solve Jacobian " << ++ud->jacIterNum);
    }

    int profileCategory = MProfiler::getCategoryIndex("mmSolver");
    MProfilingScope iterScope(profileCategory, MProfiler::kColorC_L1, "iteration");

    if (ud->computation->isInterruptRequested()) {
        WRN("User wants to cancel the solve!");
        // This is an ugly hack to force levmar to stop computing. We give
        // a NaN value which causes levmar detect it and quit the loop.
        for (i = 0; i < n; ++i) {
            x[i] = NAN;
        }
        return;
    }

    // Set Parameter
    MStatus status;
    {
        ud->paramBenchTimer->start();
        ud->paramBenchTicks->start();
        MProfilingScope setParamScope(profileCategory, MProfiler::kColorA_L2, "set parameters");

        MTime currentFrame = MAnimControl::currentTime();
        for (i = 0; i < m; ++i) {
            IndexPair attrPair = ud->paramToAttrList[i];
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
        MProfilingScope setParamScope(profileCategory, MProfiler::kColorA_L1, "measure errors");

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
        for (i = 0; i < (n / ERRORS_PER_MARKER); ++i) {
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

            mkr_mpos = ud->markerPosList[i];  // Use pre-computed marker position

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
            double d = fabs(dx) + fabs(dy);

            x[(i * ERRORS_PER_MARKER) + 0] = dx;  // X error
            x[(i * ERRORS_PER_MARKER) + 1] = dy;  // Y error

            ud->errorList[(i * ERRORS_PER_MARKER) + 0] = dx;
            ud->errorList[(i * ERRORS_PER_MARKER) + 1] = dy;

#if ERRORS_PER_MARKER == 3
            // d = distance_2d(mkr_mpos, bnd_mpos) * ((right - left) * ud->imageWidth);
            x[(i * ERRORS_PER_MARKER) + 2] = d;   // Distance error
            ud->errorList[(i * ERRORS_PER_MARKER) + 2] = d;
#endif

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
        error_avg *= 1.0 / (n / ERRORS_PER_MARKER);
        INFO(" | error avg=" << error_avg << " min=" << error_min << " max=" << error_max);
    }
    return;
}


// Function run by lev-mar algorithm to test the input parameters, p,
// and compute the output errors, x.
//
// TODO: If this function is used in future, we should add timing and
//  Maya profiling into this function, just like the non-'Optimise'
//  function.
#if USE_EXPERIMENTAL_SOLVER == 1
void levmarSolveOptimiseFunc(double *p, double *x, int m, int n, void *data) {
    register int i = 0;
    register int j = 0;
    register bool verbose = false;
    LevMarSolverData *ud = static_cast<LevMarSolverData *>(data);
    ud->computation->setProgress(ud->iterNum);
    verbose = ud->verbose;
    if (ud->isJacobianCalculation == false) {
        // We're not using INFO macro because we don't want a new-line
        // created.
        std::cout << "Solve " << ++ud->iterNum;
    } else {
        INFO("Solve Jacobian " << ++ud->jacIterNum);
    }

    if (ud->computation->isInterruptRequested()) {
        WRN("User wants to cancel the solve!");
        // This is an ugly hack to force levmar to stop computing. We
        // give a NaN value which causes levmar detect it and quit the
        // loop.
        for (i = 0; i < n; ++i) {
            x[i] = NAN;
        }
        return;
    }

    // Set Parameter
    int numSetParams = 0;
    MStatus status;
    {
        MTime currentFrame = MAnimControl::currentTime();
        for (j = 0; j < m; ++j) {
            IndexPair attrPair = ud->paramToAttrList[j];
            AttrPtr attr = ud->attrList[attrPair.first];

            // Get frame time
            MTime frame = currentFrame;
            if (attrPair.second != -1) {
                frame = ud->frameList[attrPair.second];
            }

            bool paramAffectsError = ud->errorToParamMapping[i][j];
            if (paramAffectsError == true) {
                attr->setValue(p[j], frame, *ud->dgmod, *ud->curveChange);
                ++numSetParams;
            }
        }

        // Commit changed data into Maya
        ud->dgmod->doIt();

        // Invalidate the Camera Matrix cache.
        //
        // In future we might be able to auto-detect if the camera
        // will change based on the current solve and not invalidate
        // the cache but for now we cannot take the risk of an
        // incorrect solve; we clear the cache.
        for (j = 0; j < (int) ud->cameraList.size(); ++j) {
            ud->cameraList[j]->clearAttrValueCache();
        }
    }

    // Measure Errors
    double error_avg = 0.0;
    double error_max = -0.0;
    double error_min = std::numeric_limits<double>::max();
    {

#if FORCE_TRIGGER_EVAL == 1
        {
            MPoint pos;
            int errorIndex = 0;
            IndexPair markerPair = ud->errorToMarkerList[errorIndex];
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
            IndexPair markerPair = ud->errorToMarkerList[i];
            MarkerPtr marker = ud->markerList[markerPair.first];
            MTime markerFrame = ud->frameList[markerPair.second];

            // Set Parameter
            numSetParams = 0;
            {
                for (j = 0; j < m; ++j) {
                    IndexPair attrPair = ud->paramToAttrList[j];
                    AttrPtr attr = ud->attrList[attrPair.first];

                    // Only set the attribute if we're on the same
                    // time as the error evaluation.
                    if (attrPair.second == markerPair.second && attrPair.second != -1) {
                        bool paramAffectsError = ud->errorToParamMapping[i][j];
                        MTime attrFrame = ud->frameList[attrPair.second];
                        if (paramAffectsError == true) {
                            attr->setValue(p[j], attrFrame, *ud->dgmod, *ud->curveChange);
                            ++numSetParams;
                        }
                    } else {
                        // DBG("static marker and attr frame");
                    }
                }

                // Commit changed data into Maya
                ud->dgmod->doIt();

                // Invalidate the Camera Matrix cache.
                //
                // In future we might be able to auto-detect if the camera
                // will change based on the current solve and not invalidate
                // the cache but for now we cannot take the risk of an
                // incorrect solve; we clear the cache.
                for (j = 0; j < (int) ud->cameraList.size(); ++j) {
                    ud->cameraList[j]->clearAttrValueCache();
                }
            }

#if FORCE_TRIGGER_EVAL == 1
            {
                MPoint pos;
                int errorIndex = i;
                IndexPair markerPair = ud->errorToMarkerList[errorIndex];
                MarkerPtr marker = ud->markerList[markerPair.first];
                MTime frame = ud->frameList[markerPair.second];
                status = marker->getPos(pos, frame + 1);
                CHECK_MSTATUS(status);
            }
#endif

            CameraPtr camera = marker->getCamera();
            status = camera->getWorldProjMatrix(cameraWorldProjectionMatrix, markerFrame);
            CHECK_MSTATUS(status);

            double left = 0;
            double right = 0;
            double top = 0;
            double bottom = 0;
            camera->getFrustum(left, right, top, bottom, markerFrame);

            BundlePtr bnd = marker->getBundle();

            mkr_mpos = ud->markerPosList[i]; // Use pre-computed marker position

            status = bnd->getPos(bnd_mpos, markerFrame);
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
            double d = fabs(dx) + fabs(dy);

            x[(i * ERRORS_PER_MARKER) + 0] = dx;  // X error
            x[(i * ERRORS_PER_MARKER) + 1] = dy;  // Y error

            ud->errorList[(i * ERRORS_PER_MARKER) + 0] = dx;
            ud->errorList[(i * ERRORS_PER_MARKER) + 1] = dy;

#if ERRORS_PER_MARKER == 3
            // d = distance_2d(mkr_mpos, bnd_mpos) * ((right - left) * ud->imageWidth);
            x[(i * ERRORS_PER_MARKER) + 2] = d;   // Distance error
            ud->errorList[(i * ERRORS_PER_MARKER) + 2] = d;
#endif

            error_avg += d;
            if (d > error_max) { error_max = d; }
            if (d < error_min) { error_min = d; }
        }
    }

    if (ud->isJacobianCalculation == false) {
        // error_avg /= (n / ERRORS_PER_MARKER);
        error_avg *= 1.0 / (n / ERRORS_PER_MARKER);
        INFO(" | error avg=" << error_avg << " min=" << error_min << " max=" << error_max);
    }
    return;
}
#endif


// Finite difference approximation to the Jacobian of func
#if USE_ANALYTIC_JACOBIAN == 1
void finite_diff_jacobian_approx(
        void (*func)(double *p, double *hx, int m, int n, void *adata), // function to differentiate
        double *p,     // I: current parameter estimate, mx1
        double *hxp,   // I: func evaluated at p, i.e. hx=func(p), nx1
        double *hxm,   // W/O: work array for evaluating func(p+delta), nx1
        double delta,  // increment for computing the Jacobian
        double *jac,   // O: array for storing approximated Jacobian, nxm
        int m,
        int n,
        int method,    // Approximation method , 0 = forward, 1 = central
        void *adata) {
    register int i, j;
    double tmp;
    register double d;

    LevMarSolverData *ud = static_cast<LevMarSolverData *>(adata);

    for (j = 0; j < m; ++j) {
        // determine d=max(1E-04*|p[j]|, delta), see HZ
        d = 1E-04 * p[j]; // force evaluation
        d = FABS(d);
        if (d < delta)
            d = delta;

        if (method == 0) {
            // Forward Differencing

            // Run the function with adjusted parameter value
            tmp = p[j];
            p[j] += d;
            (*func)(p, hxp, m, n, adata);
            p[j] = tmp;

            d = 1.0 / d;  // invert so that divisions can be carried out faster as multiplications
            for (i = 0; i < n; ++i) {
                jac[i * m + j] = (hxp[i] - hxm[i]) * d;
            }
        } else {
            // Central Differencing

            // Run the function, with the negative p value.
            tmp = p[j];
            p[j] -= d;
            (*func)(p, hxm, m, n, adata);

            // Run the function, with the positive p value.
            p[j] = tmp + d;
            (*func)(p, hxp, m, n, adata);
            p[j] = tmp; // restore

            d = 0.5 / d; // invert so that divisions can be carried out faster as multiplications
            for (i = 0; i < n; ++i) {
                jac[i * m + j] = (hxp[i] - hxm[i]) * d;
            }
        }
    }
}
#endif


// A function given to lev-mar which will compute a jacobian.
#if USE_ANALYTIC_JACOBIAN == 1
void levmarSolveJacFunc(double *p, double *jac, int m, int n, void *data) {
    register int i = 0;
    register bool verbose = false;
    LevMarSolverData *ud = static_cast<LevMarSolverData *>(data);
    verbose = ud->verbose;

    VRB("Calculating Jacobian Matrix...");

    ud->jacBenchTimer->start();
    ud->jacBenchTicks->start();

    // Error lists, used when computing the jacobian.
    std::vector<double> errorList(1);
    std::vector<double> errorList2(1);
    errorList.resize((unsigned long) n, 0);
    errorList2.resize((unsigned long) n, 0);

    ud->isJacobianCalculation = true;
    double delta = ud->delta;
    int method = 0;
    if (delta < 0) {
        VRB("Using Central Finite Differencing.");
        delta = -delta;
        method = 1;
    } else {
        // Run the initial function to get the current parameter error
        // list.
        VRB("Using Forward Finite Differencing.");
        (*levmarSolveFunc)(p, &errorList[0], m, n, data);
    }

    // Run function again and compute the jacobian.    
    finite_diff_jacobian_approx(
            levmarSolveFunc,
            p,
            &errorList[0],
            &errorList2[0],
            delta,
            jac,
            m,
            n,
            method,
            data);

    ud->isJacobianCalculation = false;

    ud->jacBenchTimer->stop();
    ud->jacBenchTicks->stop();
    return;
}
#endif

// A function given to lev-mar which will compute a jacobian.
#if USE_EXPERIMENTAL_SOLVER == 1
#if USE_ANALYTIC_JACOBIAN == 1
void levmarSolveJacOptimiseFunc(double *p, double *jac, int m, int n, void *data) {
    register int i = 0;
    register bool verbose = false;
    LevMarSolverData *ud = static_cast<LevMarSolverData *>(data);
    verbose = ud->verbose;

    VRB("Calculating Jacobian Matrix...");

    ud->jacBenchTimer->start();
    ud->jacBenchTicks->start();

    // Error lists, used when computing the jacobian.
    std::vector<double> errorList(1);
    std::vector<double> errorList2(1);
    errorList.resize((unsigned long) n, 0);
    errorList2.resize((unsigned long) n, 0);

    ud->isJacobianCalculation = true;
    double delta = ud->delta;
    int method = 0;
    if (delta < 0) {
        VRB("Using Central Finite Differencing.");
        delta = -delta;
        method = 1;
    } else {
        // Run the initial function to get the current parameter error
        // list.
        VRB("Using Forward Finite Differencing.");
        (*levmarSolveOptimiseFunc)(p, &errorList[0], m, n, data);
    }

    // Run function again and compute the jacobian.    
    finite_diff_jacobian_approx(
            levmarSolveOptimiseFunc,
            p,
            &errorList[0],
            &errorList2[0],
            delta,
            jac,
            m,
            n,
            method,
            data);

    ud->isJacobianCalculation = false;

    ud->jacBenchTimer->stop();
    ud->jacBenchTicks->stop();
    return;
}

#endif
#endif
