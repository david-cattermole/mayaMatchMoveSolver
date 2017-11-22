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
#include <utilities/cgCameraUtils.h>

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

    // Storing changes for undo/redo.
    MDGModifier      *dgmod;
    MAnimCurveChange *animChange;
    bool verbose;
};


// Function run by lev-mar algorithm to test the input parameters, p, and compute the output errors, x.
inline
void solveFunc(double *p, double *x, int m, int n, void *data) {
    register int i, j;
    SolverData *udata = static_cast<SolverData*>(data);

    CameraPtr cam = udata->cameraList[0];
    MMatrix camWorldMat = cam->getMatrix().inverse();
    MFnCamera cameraFn(cam->getShapeObject());
    MMatrix camProjMat = MMatrix(cameraFn.projectionMatrix().matrix);

    MMatrix resultMat = camWorldMat * camProjMat;

    for (i = 0; i < m; ++i) {
        MPlug plug = udata->attrList[i]->getPlug();
        INFO("set i=" << i << " " << plug.name() << " p=" << p[i]);
        udata->dgmod->newPlugValueDouble(plug, p[i]);
    }
    udata->dgmod->doIt();

    // Force evaluate bundles
    for (i = 0; i < (n / 3); ++i) {
        MarkerPtr mkr = udata->markerList[i];
        glm::vec3 mkr_pos;
        mkr->getPos(mkr_pos);

        BundlePtr bnd = mkr->getBundle();
        glm::vec3 bnd_pos;
        bnd->getPos(bnd_pos);
    }

    // NOTE: In order to handle undo/redo, we must use a 'MDGModifier' class. Such a class does not support time
    // changes or setting plug values at specific times; this doesn't matter. Any plug value set should only be a
    // 'static' attribute value in any case. Any plug value get can be achieved with a MDGContext class in the plug.
    // Plug values at different times must be animCurves and therefore we can use MFnAnimCurve for value setting and
    // MAnimCurveChange for undo/redo. Otherwise the only need to change times will be for evaluation at a specific
    // time.

    // Calculate
    MPoint mkr_mpos;
    MPoint bnd_mpos;
    for (i = 0; i < (n / 3); ++i) {
        MarkerPtr mkr = udata->markerList[i];
        mkr->getPos(mkr_mpos);
        INFO("mkr name=" << mkr->getNodeName()
                         << " x=" << mkr_mpos.x
                         << " y=" << mkr_mpos.y
                         << " z=" << mkr_mpos.z
                         << " w=" << mkr_mpos.w
        );
        mkr_mpos = mkr_mpos * resultMat;
        mkr_mpos.cartesianize();

        INFO("mkr name=" << mkr->getNodeName()
                         << " x=" << mkr_mpos.x
                         << " y=" << mkr_mpos.y
                         << " z=" << mkr_mpos.z
                         << " w=" << mkr_mpos.w
        );
        glm::vec2 mkr_pos2d(mkr_mpos.x, mkr_mpos.y);

        BundlePtr bnd = mkr->getBundle();
        bnd->getPos(bnd_mpos);
        INFO("bnd name=" << bnd->getNodeName()
                         << " x=" << bnd_mpos.x
                         << " y=" << bnd_mpos.y
                         << " z=" << bnd_mpos.z
                         << " w=" << bnd_mpos.w
        );
        bnd_mpos = bnd_mpos * resultMat;
        bnd_mpos.cartesianize();
        INFO("bnd name=" << bnd->getNodeName()
                         << " x=" << bnd_mpos.x
                         << " y=" << bnd_mpos.y
                         << " z=" << bnd_mpos.z
                         << " w=" << bnd_mpos.w
        );
        glm::vec2 bnd_pos2d(bnd_mpos.x, bnd_mpos.y);

        double dx = fabs(mkr_pos2d.x - bnd_pos2d.x);
        double dy = fabs(mkr_pos2d.y - bnd_pos2d.y);
        double d = fabs(glm::distance(bnd_pos2d, mkr_pos2d));
        INFO("err " << i << " : dx=" << dx << " dy=" << dy << " d=" << d);
        x[i+0] = 0.5 * (d * d);    // Distance error
        x[i+1] = 0.5 * (d * d);    // Distance error
        x[i+2] = 0.5 * (d * d);    // Distance error
    }
}


inline
bool solve(int iterMax,
           std::vector< std::shared_ptr<Camera> > cameraList,
           std::vector< std::shared_ptr<Marker> > markerList,
           std::vector< std::shared_ptr<Bundle> > bundleList,
           std::vector< std::shared_ptr<Attr> > attrList,
           MDGModifier &dgmod,
           double &outError) {
    register int i, j;
    int ret;

    // Number of unknown parameters.
    const int m = (const int) attrList.size();
    double params[m];

    // Number of measurement errors. (Must be less than or equal to number of unknown parameters).
    int n = (int) (markerList.size() * 3);  // TODO: Revise this when more cameras are added into the solve.
    INFO("m=" << m);
    INFO("n=" << n);
    assert(m <= n);

    // Standard Lev-Mar arguments.
    double opts[LM_OPTS_SZ];
    double info[LM_INFO_SZ];

    // Options
    double nudgeFactor = 1.0; // 1E+6;
    opts[0] = LM_INIT_MU * nudgeFactor;
    opts[1] = 1E-15;
    opts[2] = 1E-15;
    opts[3] = 1E-20;
    opts[4] = -LM_DIFF_DELTA * nudgeFactor;

    struct SolverData userData;
    userData.cameraList = cameraList;
    userData.markerList = markerList;
    userData.bundleList = bundleList;
    userData.attrList = attrList;
    userData.dgmod = &dgmod;

    // Set Initial parameters
    INFO("Set Initial parameters");
    i = 0;
    for (AttrPtrListIt ait = attrList.begin(); ait != attrList.end(); ++ait, ++i){
        AttrPtr attr = *ait;
        MPlug plug = attr->getPlug();
        params[i] = plug.asDouble();
    }

    // Initial Parameters
    INFO("Initial Parameters: ");
    for (i = 0; i < m; ++i) {
        INFO("-> " << params[i]);
    }
    INFO("");

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

    free(work);

    INFO("Results:");
    INFO("Levenberg-Marquardt returned " << ret << " in " << (int) info[5]
                                         << " iterations");

    int reasonNum = (int) info[6];
    INFO("Reason: " << reasons[reasonNum]);
    INFO("Reason number: " << info[6]);
    INFO("");

    INFO("Solved Parameters:");
    for (i = 0; i < m; ++i) {
        INFO("-> " << params[i]);
    }
    INFO("");

    INFO(std::endl << std::endl << "Solve Information:");
    INFO("Initial Error: " << info[0]);

    INFO("Overall Error: " << info[1]);
    INFO("J^T Error: " << info[2]);
    INFO("Dp Error: " << info[3]);
    INFO("Max Error: " << info[4]);

    INFO("Iterations: " << info[5]);
    INFO("Termination Reason: " << reasons[reasonNum]);
    INFO("Function Evaluations: " << info[7]);
    INFO("Jacobian Evaluations: " << info[8]);
    INFO("Attempts for reducing error: " << info[9]);

    outError = info[1];

    return ret != -1;
}


#endif // MAYA_MM_SOLVER_UTILS_H
