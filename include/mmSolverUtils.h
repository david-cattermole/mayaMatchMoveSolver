/*
 * Uses Non-Linear Least Squares algorithm from levmar library to calculate attribute values based on 2D-to-3D error measurements through a pinhole camera.
 */


#ifndef MAYA_MM_SOLVER_UTILS_H
#define MAYA_MM_SOLVER_UTILS_H

// Lev-Mar
#include <levmar.h>  // dlevmar_dif

// STL
#include <ctime>     // time
#include <cmath>     // exp
#include <iostream>  // cout, cerr, endl
#include <string>    // string
#include <vector>    // vector
#include <cassert>   // assert
#include <math.h>

// Utils
#include <utilities/debugUtils.h>

// Maya
#include <maya/MPoint.h>
#include <maya/MVector.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MObject.h>
#include <maya/MFnAnimCurve.h>
#include <maya/MAnimCurveChange.h>
#include <maya/MSelectionList.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MMatrix.h>
#include <maya/MFloatMatrix.h>
#include <maya/MFnCamera.h>
#include <maya/MComputation.h>

// GL Math
#include <glm/glm.hpp>


// Lev-Mar Termination Reasons:
const std::string reasons[8] = {
        // reason 0
        "no reason, should not get here",

        // reason 1
        "stopped by small gradient J^T e",

        // reason 2
        "stopped by small Dp",

        // reason 3
        "stopped by itmax",

        // reason 4
        "singular matrix. Restart from current p with increased \\mu",

        // reason 5
        "no further error reduction is possible. Restart with increased mu",

        // reason 6
        "stopped by small ||e||_2",

        // reason 7
        "stopped by invalid (i.e. NaN or Inf) \"func\" refPoints (user error)",
};


struct SolverData {
    CameraPtrList cameraList;
    MarkerPtrList markerList;
    BundlePtrList bundleList;
    AttrPtrList attrList;
    MTimeArray frameList;  // Times to solve

    // Relational mapping indexes.
    std::vector< std::pair<int, int> > paramToAttrList;
    std::vector< std::pair<int, int> > errorToMarkerList;
    std::vector<double> errorList;
    int iterNum;
    debug::TimestampBenchmark *errorBench;
    debug::TimestampBenchmark *paramBench;

    // Storing changes for undo/redo.
    MDGModifier      *dgmod;
    MAnimCurveChange *curveChange;
    MComputation *computation;
    bool verbose;
};


// Function run by lev-mar algorithm to test the input parameters, p, and compute the output errors, x.
inline
void solveFunc(double *p, double *x, int m, int n, void *data) {
    register int i = 0;
    SolverData *ud = static_cast<SolverData*>(data);
    ud->computation->setProgress(ud->iterNum);
//    INFO("Solve #" << ++ud->iterNum);

    if (ud->computation->isInterruptRequested()){
        WRN("User wants to cancel the solve!");
        // This is an ugly hack to force levmar to stop computing. We give
        // an infinite value which causes levmar detect it and quit the loop.
        for (i=0; i<n; ++i){
            x[i] = INFINITY;
        }
        return;
    }

    ud->paramBench->start();
    MStatus status;
    MTime time;
    CameraPtr cam = ud->cameraList[0];
    MMatrix resultMat;
    status = cam->getWorldProjMatrix(resultMat);

    MTime currentFrame = MAnimControl::currentTime();
    for (i = 0; i < m; ++i) {
        std::pair<int, int> attrPair = ud->paramToAttrList[i];
        AttrPtr attr = ud->attrList[attrPair.first];

        // Get frame time
        MTime frame = currentFrame;
        if (attrPair.second != -1){
            frame = ud->frameList[attrPair.second];
        }

        attr->setValue(p[i], frame, *ud->dgmod, *ud->curveChange);
    }
    ud->dgmod->doIt();
    ud->paramBench->stop();

    // Calculate
    ud->errorBench->start();
    MPoint mkr_mpos;
    MPoint bnd_mpos;
    for (i = 0; i < (n / 3); ++i) {
        std::pair<int, int> markerPair = ud->errorToMarkerList[i];
        MarkerPtr marker = ud->markerList[markerPair.first];
        MTime frame = ud->frameList[markerPair.second];

        // TODO: Test to see if the first dummy call at a different frame is needed.
        status = marker->getPos(mkr_mpos, frame+1);
        CHECK_MSTATUS(status);
        status = marker->getPos(mkr_mpos, frame);
        CHECK_MSTATUS(status);
        mkr_mpos = mkr_mpos * resultMat;
        mkr_mpos.cartesianize();
        glm::vec2 mkr_pos2d(mkr_mpos.x, mkr_mpos.y);

        BundlePtr bnd = marker->getBundle();
        status = bnd->getPos(bnd_mpos, frame-1);
        CHECK_MSTATUS(status);
        status = bnd->getPos(bnd_mpos, frame);
        CHECK_MSTATUS(status);
        bnd_mpos = bnd_mpos * resultMat;
        bnd_mpos.cartesianize();
        glm::vec2 bnd_pos2d(bnd_mpos.x, bnd_mpos.y);

        // NOTE: Interestingly, using an x, y and distance error measurement seems to allow at least some scenes to converge much faster; ~20 iterations compared to ~160 iterations.
        double dx = fabs(mkr_mpos.x - bnd_mpos.x);
        double dy = fabs(mkr_mpos.y - bnd_mpos.y);
        double d = fabs(glm::distance(bnd_pos2d, mkr_pos2d));
        x[(i*3)+0] = dx;  // X error
        x[(i*3)+1] = dy;  // Y error
        x[(i*3)+2] = d;   // Distance error

        ud->errorList[(i*3)+0] = dx;
        ud->errorList[(i*3)+1] = dy;
        ud->errorList[(i*3)+2] = dy;
    }
    ud->errorBench->stop();
    return;
}


inline
bool solve(int iterMax,
           std::vector< std::shared_ptr<Camera> > cameraList,
           std::vector< std::shared_ptr<Marker> > markerList,
           std::vector< std::shared_ptr<Bundle> > bundleList,
           std::vector< std::shared_ptr<Attr> > attrList,
           MTimeArray frameList,
           MDGModifier &dgmod,
           MAnimCurveChange &curveChange,
           MComputation &computation,
           double &outError) {
    register int i, j;
    MStatus status;
    int ret;

    // Number of unknown parameters.
    int m = 0;

    // Count up number of unknown parameters
    std::vector< std::pair<int,int> > paramToAttrList;
    i = 0;
    j = 0;
    for (AttrPtrListIt ait = attrList.begin(); ait != attrList.end(); ++ait){
        AttrPtr attr = *ait;
        if (attr->getDynamic()) {
            m += frameList.length();
            for (j=0; j < (int) frameList.length(); ++j){
                // first index is into 'attrList'
                // second index is into 'frameList'
                std::pair<int, int> attrPair(i, j);
                paramToAttrList.push_back(attrPair);
            }
        } else {
            ++m;
            // first index is into 'attrList'
            // second index is into 'frameList', '-1' means a static value.
            std::pair<int, int> attrPair(i, -1);
            paramToAttrList.push_back(attrPair);
        }
        i++;
    }
    double params[m];

    // Number of measurement errors. (Must be less than or equal to number of unknown parameters).
    int n = 0;

    // Count up number of errors
    // For each marker on each frame that it is valid, we add 3 errors.
    std::vector< std::pair<int,int> > errorToMarkerList;
    i = 0;
    j = 0;
    for (MarkerPtrListIt mit = markerList.begin(); mit != markerList.end(); ++mit){
        MarkerPtr marker = *mit;
        for (j = 0; j < (int) frameList.length(); ++j){
            MTime frame = frameList[j];
            bool valid;
            status = marker->getValid(valid, frame);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            if (valid){
                std::pair<int, int> markerPair(i, j);
                errorToMarkerList.push_back(markerPair);
                n += 3;
            }
        }
        i++;
    }

    INFO("params m=" << m);
    INFO("errors n=" << n);
    assert(m <= n);
    std::vector<double> errorList;
    errorList.resize((unsigned long) n);
    for (i=0; i<n; ++i) {
        errorList[i] = 0.0;
    }

    // Standard Lev-Mar arguments.
    double opts[LM_OPTS_SZ];
    double info[LM_INFO_SZ];

    // Options
    // TODO: Test for the best nudge factor. Should nudgeFactor be a function input variable?
    double nudgeFactor = 10.0;
    opts[0] = LM_INIT_MU * nudgeFactor;
    opts[1] = 1E-15;
    opts[2] = 1E-15;
    opts[3] = 1E-20;
    opts[4] = -LM_DIFF_DELTA * (nudgeFactor * 0.1);

    // Debug timers
    debug::TimestampBenchmark errorBench = debug::TimestampBenchmark();
    debug::TimestampBenchmark paramBench = debug::TimestampBenchmark();

    struct SolverData userData;
    userData.cameraList = cameraList;
    userData.markerList = markerList;
    userData.bundleList = bundleList;
    userData.attrList = attrList;
    userData.frameList = frameList;
    userData.paramToAttrList = paramToAttrList;
    userData.errorToMarkerList = errorToMarkerList;
    userData.errorList = errorList;
    userData.iterNum = 0;
    userData.errorBench = &errorBench;
    userData.paramBench = &paramBench;
    userData.dgmod = &dgmod;
    userData.curveChange = &curveChange;
    userData.computation = &computation;

    // Set Initial parameters
    INFO("Set Initial parameters");
    MTime currentFrame = MAnimControl::currentTime();
    i = 0;
    for (i=0; i<m; ++i){
        std::pair<int, int> attrPair = paramToAttrList[i];
        AttrPtr attr = attrList[attrPair.first];

        // Get frame time
        MTime frame = currentFrame;
        if (attrPair.second != -1){
            frame = frameList[attrPair.second];
        }

        double value;
        status = attr->getValue(value, frame);
        CHECK_MSTATUS_AND_RETURN(status, false);

        params[i] = value;
    }

    // // Initial Parameters
    // INFO("Initial Parameters: ");
    // for (i = 0; i < m; ++i) {
    //     INFO("-> " << params[i]);
    // }
    // INFO("");

    // Allocate a memory block for both 'work' and 'covar', so that
    // the block is close together in physical memory.
    double *work, *covar;
    work = (double *) malloc((LM_DIF_WORKSZ(m, n) + m * m) * sizeof(double));
    if (!work) {
        ERR("Memory allocation request failed.");
        return false;
    }
    covar = work + LM_DIF_WORKSZ(m, n);

    // no Jacobian, caller allocates work memory, covariance estimated
    INFO("Solving...");
    INFO("Maximum Iterations=" << iterMax);
    computation.setProgressRange(0, iterMax);
    computation.beginComputation();
    ret = dlevmar_dif(

            // Function to call (input only)
            // Function must be of the structure:
            //   func(double *params, double *x, int m, int n, void *data)
            solveFunc,

            // Parameters (input and output)
            // Should be filled with initial estimate, will be filled
            // with output parameters
            params,

            // Measurement Vector (input only)
            // NULL implies a zero vector
            NULL,

            // Parameter Vector Dimension (input only)
            // (i.e. #unknowns)
            m,

            // Measurement Vector Dimension (input only)
            n,

            // Maximum Number of Iterations (input only)
            iterMax,

            // Minimisation options (input only)
            // opts[0] = tau      (scale factor for initialTransform mu)
            // opts[1] = epsilon1 (stopping threshold for ||J^T e||_inf)
            // opts[2] = epsilon2 (stopping threshold for ||Dp||_2)
            // opts[3] = epsilon3 (stopping threshold for ||e||_2)
            // opts[4] = delta    (step used in difference approximation to the Jacobian)
            //
            // If \delta<0, the Jacobian is approximated with central differences
            // which are more accurate (but slower!) compared to the forward
            // differences employed by default.
            // Set to NULL for defaults to be used.
            opts,

            // Output Information (output only)
            // information regarding the minimization.
            // info[0] = ||e||_2 at initialTransform params.
            // info[1-4] = (all computed at estimated params)
            //  [
            //   ||e||_2,
            //   ||J^T e||_inf,
            //   ||Dp||_2,
            //   \mu/max[J^T J]_ii
            //  ]
            // info[5] = number of iterations,
            // info[6] = reason for terminating:
            //   1 - stopped by small gradient J^T e
            //   2 - stopped by small Dp
            //   3 - stopped by iterMax
            //   4 - singular matrix. Restart from current params with increased \mu
            //   5 - no further error reduction is possible. Restart with increased mu
            //   6 - stopped by small ||e||_2
            //   7 - stopped by invalid (i.e. NaN or Inf) "func" refPoints; a user error
            // info[7] = number of function evaluations
            // info[8] = number of Jacobian evaluations
            // info[9] = number linear systems solved (number of attempts for reducing error)
            //
            // Set to NULL if don't care
            info,

            // Working Data (input only)
            // working memory, allocated internally if NULL. If !=NULL, it is assumed to
            // point to a memory chunk at least LM_DIF_WORKSZ(m, n)*sizeof(double) bytes
            // long
            work,

            // Covariance matrix (output only)
            // Covariance matrix corresponding to LS solution; Assumed to point to a mxm matrix.
            // Set to NULL if not needed.
            covar,

            // Custom Data for 'func' (input only)
            // pointer to possibly needed additional data, passed uninterpreted to func.
            // Set to NULL if not needed
            (void *) &userData);
    computation.endComputation();

    free(work);

    INFO("Results:");
    INFO("Levenberg-Marquardt returned " << ret << " in " << (int) info[5]
                                         << " iterations");

    // Build in some logic as to what happens when the solver finishes due to various problems.
    // We could restart the solve with an increased "mu" value if we get reason 4 or 5. We also need to cap the number of restarts, so we don't restart recursively.
    int reasonNum = (int) info[6];
    INFO("Reason: " << reasons[reasonNum]);
    INFO("Reason number: " << info[6]);
    INFO("");

    INFO("Solved Parameters:");
    for (i = 0; i < m; ++i) {
        INFO("-> " << params[i]);
    }
    INFO("");

    // Compute the average error based on the error values the solve function last computed.
    // TODO: Create a list of frames and produce an error per-frame. This information will eventually be given to the user to diagnose problems.
    double avgError = 0;
    for (i = 0; i < n; ++i) {
        avgError += userData.errorList[i];
    }
    avgError /= (double) n;

    INFO(std::endl << std::endl << "Solve Information:");
    INFO("Initial Error: " << info[0]);
    INFO("Final Error: " << info[1]);
    INFO("Average Error: " << avgError);
    INFO("J^T Error: " << info[2]);
    INFO("Dp Error: " << info[3]);
    INFO("Max Error: " << info[4]);

    INFO("Iterations: " << info[5]);
    INFO("Termination Reason: " << reasons[reasonNum]);
    INFO("Function Evaluations: " << info[7]);
    INFO("Jacobian Evaluations: " << info[8]);
    INFO("Attempts for reducing error: " << info[9]);

    paramBench.printInSec("Param Time:", 1);
    errorBench.printInSec("Error Time:", 1);

    outError = info[1];

    return ret != -1;
}


#endif // MAYA_MM_SOLVER_UTILS_H
