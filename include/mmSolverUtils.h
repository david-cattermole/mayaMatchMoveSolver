/*
 * Uses Non-Linear Least Squares algorithm from levmar library to calculate attribute values based on 2D-to-3D error measurements through a pinhole camera.
 */


#ifndef MAYA_MM_SOLVER_UTILS_H
#define MAYA_MM_SOLVER_UTILS_H


#ifndef HAVE_SPLM
#error "HAVE_SPLM were not defined."
#endif


#ifdef HAVE_SPLM
#if HAVE_SPLM == 0
#warning "HAVE_SPLM was not given."
#endif
#endif


// Lev-Mar
#include <levmar.h>  // dlevmar_dif


// Sparse Lev-Mar
#if HAVE_SPLM == 1

#include <splm.h>    // sparselm_difccs

#endif


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
#include <maya/MProfiler.h>

// Utilities
#include <mayaUtils.h>

#define FABS(x)     (((x)>=0)? (x) : -(x))

// NOTE: There is a very strange bug in Maya. After setting a number of plug values
// using a DG Context, when quering plug values at the same times, the values do
// not evaluate correctly. To 'trick' Maya into triggering an eval the next time a
// plug is queried we query the matrix of a marker node. It doesn't matter which
// marker node, however it does matter that it's a marker node, if the eval is
// performed with a bundle node the error continues to happen.
#define FORCE_TRIGGER_EVAL 1

#define SOLVER_TYPE_LEVMAR 0
#define SOLVER_TYPE_SPARSE_LEVMAR 1


#define ERRORS_PER_MARKER 3


// Sparse LM or Lev-Mar Termination Reasons:
const std::string reasons[8] = {
        // reason 0
        "No reason, should not get here!",

        // reason 1
        "Stopped by small gradient J^T e",

        // reason 2
        "Stopped by small Dp",

        // reason 3
        "Stopped by reaching maximum iterations",

        // reason 4
        "Singular matrix. Restart from current parameters with increased \'Tau Factor\'",

        // reason 5
        "Too many failed attempts to increase damping. Restart with increased \'Tau Factor\'",

        // reason 6
        "Stopped by small error",

        // reason 7
        // "stopped by invalid (i.e. NaN or Inf) \"func\" refPoints (user error)",
        "User canceled",
};


// The user data given to levmar.
struct SolverData {
    // Solver Objects.
    CameraPtrList cameraList;
    MarkerPtrList markerList;
    BundlePtrList bundleList;
    AttrPtrList attrList;
    MTimeArray frameList;  // Times to solve

    // Relational mapping indexes.
    std::vector<std::pair<int, int> > paramToAttrList;
    std::vector<std::pair<int, int> > errorToMarkerList;

    // Internal Solver Data.
    std::vector<double> errorList;
    int iterNum;
    int jacIterNum;
    int iterMax;
    int solverType;
    bool isJacobianCalculation;

    // Error Thresholds.
    double tau;
    double eps1;
    double eps2;
    double eps3;
    double delta;

    // Benchmarks
    debug::TimestampBenchmark *jacBenchTimer;
    debug::TimestampBenchmark *funcBenchTimer;
    debug::TimestampBenchmark *errorBenchTimer;
    debug::TimestampBenchmark *paramBenchTimer;
    debug::CPUBenchmark *jacBenchTicks;
    debug::CPUBenchmark *funcBenchTicks;
    debug::CPUBenchmark *errorBenchTicks;
    debug::CPUBenchmark *paramBenchTicks;

    // Storing changes for undo/redo.
    MDGModifier *dgmod;
    MAnimCurveChange *curveChange;

    // Allow user to cancel the solve.
    MComputation *computation;

    // Verbosity.
    bool verbose;
};


inline
double distance_2d(MPoint a, MPoint b)
{
    double dx = (a.x - b.x);
    double dy = (a.y - b.y);
    return sqrt((dx * dx) + (dy * dy));
}


// Function run by lev-mar algorithm to test the input parameters, p, and compute the output errors, x.
inline
void levmar_solveFunc(double *p, double *x, int m, int n, void *data) {
    register int i = 0;
    register bool verbose = false;
    SolverData *ud = static_cast<SolverData *>(data);
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
    return;
}


inline
bool solve(int iterMax,
           double tau,
           double eps1,
           double eps2,
           double eps3,
           double delta,
           int solverType,
           std::vector<std::shared_ptr<Camera> > cameraList,
           std::vector<std::shared_ptr<Marker> > markerList,
           std::vector<std::shared_ptr<Bundle> > bundleList,
           std::vector<std::shared_ptr<Attr> > attrList,
           MTimeArray frameList,
           MDGModifier &dgmod,
           MAnimCurveChange &curveChange,
           MComputation &computation,
           bool verbose,
           MStringArray &outResult) {
    register int i = 0;
    register int j = 0;
    MStatus status;
    int ret = true;
    int profileCategory = MProfiler::getCategoryIndex("mmSolver");
    MProfilingScope profilingScope(profileCategory, MProfiler::kColorC_L3, "solve");
    struct SolverData userData;

    // Indexing maps
    std::vector<std::pair<int, int> > paramToAttrList;
    std::vector<std::pair<int, int> > errorToMarkerList;

    // Errors and parameters as used by the solver.
    std::vector<double> errorList;
    std::vector<double> paramList;

    // Number of unknown parameters.
    int m = 0;

    // Number of measurement errors. (Must be less than or equal to number of unknown parameters).
    int n = 0;

    // Count up number of unknown parameters
    i = 0;
    j = 0;
    for (AttrPtrListIt ait = attrList.begin(); ait != attrList.end(); ++ait) {
        AttrPtr attr = *ait;
        if (attr->isAnimated()) {
            m += frameList.length();
            for (j = 0; j < (int) frameList.length(); ++j) {
                // first index is into 'attrList'
                // second index is into 'frameList'
                std::pair<int, int> attrPair(i, j);
                paramToAttrList.push_back(attrPair);
            }
        } else if (attr->isFreeToChange()) {
            ++m;
            // first index is into 'attrList'
            // second index is into 'frameList', '-1' means a static value.
            std::pair<int, int> attrPair(i, -1);
            paramToAttrList.push_back(attrPair);
        }
        i++;
    }

    // Count up number of errors
    // For each marker on each frame that it is valid, we add ERRORS_PER_MARKER errors.
    i = 0;
    j = 0;
    for (MarkerPtrListIt mit = markerList.begin(); mit != markerList.end(); ++mit) {
        MarkerPtr marker = *mit;
        for (j = 0; j < (int) frameList.length(); ++j) {
            MTime frame = frameList[j];
            
            bool enable = false;
            status = marker->getEnable(enable, frame);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            double weight = 0.0;
            status = marker->getWeight(weight, frame);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            if ((enable == true) && (weight > 0.0))  {
                std::pair<int, int> markerPair(i, j);
                errorToMarkerList.push_back(markerPair);
                n += ERRORS_PER_MARKER;
            }
        }
        i++;
    }

    VRB("Number of Parameters; m=" << m);
    VRB("Number of Errors; n=" << n);
    assert(m <= n);
    paramList.resize((unsigned long) m, 0);
    errorList.resize((unsigned long) n, 0);

    // Debug timers
    debug::TimestampBenchmark errorBenchTimer = debug::TimestampBenchmark();
    debug::TimestampBenchmark paramBenchTimer = debug::TimestampBenchmark();
    debug::TimestampBenchmark solveBenchTimer = debug::TimestampBenchmark();
    debug::TimestampBenchmark funcBenchTimer = debug::TimestampBenchmark();
    debug::TimestampBenchmark jacBenchTimer = debug::TimestampBenchmark();

    debug::CPUBenchmark errorBenchTicks = debug::CPUBenchmark();
    debug::CPUBenchmark paramBenchTicks = debug::CPUBenchmark();
    debug::CPUBenchmark solveBenchTicks = debug::CPUBenchmark();
    debug::CPUBenchmark funcBenchTicks = debug::CPUBenchmark();
    debug::CPUBenchmark jacBenchTicks = debug::CPUBenchmark();

    // Solving Objects.
    userData.cameraList = cameraList;
    userData.markerList = markerList;
    userData.bundleList = bundleList;
    userData.attrList = attrList;
    userData.frameList = frameList;

    // Indexing maps
    userData.paramToAttrList = paramToAttrList;
    userData.errorToMarkerList = errorToMarkerList;

    // Solver Aux data
    userData.errorList = errorList;
    userData.iterNum = 0;
    userData.jacIterNum = 0;
    userData.iterMax = iterMax;
    userData.isJacobianCalculation = false;

    // Solver Errors Thresholds
    userData.tau = tau;
    userData.eps1 = eps1;
    userData.eps2 = eps2;
    userData.eps3 = eps3;
    userData.delta = delta;
    userData.solverType = solverType;

    // Timers
    userData.funcBenchTimer = &funcBenchTimer;
    userData.jacBenchTimer = &jacBenchTimer;
    userData.errorBenchTimer = &errorBenchTimer;
    userData.paramBenchTimer = &paramBenchTimer;

    userData.funcBenchTicks = &funcBenchTicks;
    userData.jacBenchTicks = &jacBenchTicks;
    userData.errorBenchTicks = &errorBenchTicks;
    userData.paramBenchTicks = &paramBenchTicks;

    // Undo/Redo
    userData.dgmod = &dgmod;
    userData.curveChange = &curveChange;

    // Allow user to exit out of solve.
    userData.computation = &computation;

    // Verbosity
    userData.verbose = verbose;

    // Set Initial parameters
    VRB("Set Initial parameters");
    MTime currentFrame = MAnimControl::currentTime();
    i = 0;
    for (i = 0; i < m; ++i) {
        std::pair<int, int> attrPair = paramToAttrList[i];
        AttrPtr attr = attrList[attrPair.first];

        // Get frame time
        MTime frame = currentFrame;
        if (attrPair.second != -1) {
            frame = frameList[attrPair.second];
        }

        double value;
        status = attr->getValue(value, frame);
        CHECK_MSTATUS_AND_RETURN(status, false);

        paramList[i] = value;
    }

//     // Initial Parameters
//     VRB("Initial Parameters: ");
//     for (i = 0; i < m; ++i) {
//         VRB("-> " << paramList[i]);
//     }

    // Options and Info
    unsigned int optsSize = LM_OPTS_SZ;
    unsigned int infoSize = LM_INFO_SZ;
#if HAVE_SPLM == 1
    if (solverType == SOLVER_TYPE_SPARSE_LEVMAR) {
        optsSize = SPLM_OPTS_SZ;
        infoSize = SPLM_INFO_SZ;
    }
#endif
    double opts[optsSize];
    double info[infoSize];

    // Options
    opts[0] = tau;
    opts[1] = eps1;
    opts[2] = eps2;
    opts[3] = eps3;
    opts[4] = delta;

    // no Jacobian, caller allocates work memory, covariance estimated
    VRB("Solving...");
    VRB("Solver Type=" << solverType);
    VRB("Maximum Iterations=" << iterMax);
    VRB("Tau=" << tau);
    VRB("Epsilon1=" << eps1);
    VRB("Epsilon2=" << eps2);
    VRB("Epsilon3=" << eps3);
    VRB("Delta=" << delta);
    computation.setProgressRange(0, iterMax);
    computation.beginComputation();

    // Determine the solver type, levmar or sparse levmar.
    if (solverType != SOLVER_TYPE_LEVMAR) {
        if (solverType == SOLVER_TYPE_SPARSE_LEVMAR) {
#if HAVE_SPLM == 0
            WRN("Selected solver type \'SparseLM\' is not available, switching to \'Lev-Mar\' instead.");
            solverType = SOLVER_TYPE_LEVMAR;
#endif
        } else {
            WRN("Selected Solver Type \'" << solverType << "\' is unknown, switching to \'Lev-Mar\' instead.");
            solverType = SOLVER_TYPE_LEVMAR;
        }
    }

    solveBenchTimer.start();
    solveBenchTicks.start();
    if (solverType == SOLVER_TYPE_LEVMAR) {

        // Allocate a memory block for both 'work' and 'covar', so that
        // the block is close together in physical memory.
        double *work, *covar;
        work = (double *) malloc((LM_DIF_WORKSZ(m, n) + m * m) * sizeof(double));
        if (!work) {
            ERR("Memory allocation request failed.");
            return false;
        }
        covar = work + LM_DIF_WORKSZ(m, n);

        ret = dlevmar_dif(

                // Function to call (input only)
                // Function must be of the structure:
                //   func(double *params, double *x, int m, int n, void *data)
                levmar_solveFunc,

                // Parameters (input and output)
                // Should be filled with initial estimate, will be filled
                // with output parameters
                &paramList[0],

                // Measurement Vector (input only)
                // NULL implies a zero vector
                // NULL,
                &errorList[0],

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
    } else if (solverType == SOLVER_TYPE_SPARSE_LEVMAR) {
#if HAVE_SPLM == 1

        // TODO: We could calculate an (approximate) non-zero value. We can do this by assuming that all dynamic
        // attributes solve on on all single frames and are independant of static attributes.

        // Calculate number of non-zeros.
        int nonzeros = 0;  // Estimated non-zeros

        nonzeros = (n * m) / 2;  // Estimated non-zeros
        // int Jnnz = 128; // TODO: How can we estimate this value better?
        // Jnnz = n * m;
        // struct splm_ccsm jac;
        // splm_ccsm_alloc_novalues(&jac, m, n, Jnnz); // no better estimate of Jnnz yet...
        //
        // // Do calculation
        // userData.isJacobianCalculation = true;
        // nonzeros = jacobianZeroPatternGuess(solveFunc, params, &jac, m, n, (void *) &userData,
        //                                 &errorList[0], delta);
        // userData.isJacobianCalculation = false;
        // INFO("non-zeros=" << nonzeros);
        // for (i=0; i<n; ++i) {
        //     INFO("hx[" << i << "]=" << errorList[i]);
        // }

        // Options
        // TODO: Use 'SPLM_PARDISO' when we can (when we have used Intel MKL), but test using other algorithms.
        opts[5] = SPLM_CHOLMOD;  // Use this if Pardiso is not available.
        // opts[5] = SPLM_PARDISO;

        //
        // Similar to sparselm_dercrs() except that fjac supplies only the non-zero pattern of the Jacobian
        // and its non-zero elements are then appoximated internally with the aid of finite differences.
        // If the analytic Jacobian is available, it is advised to use sparselm_dercrs() above.
        //
        // Returns the number of iterations (>=0) if successful, SPLM_ERROR if failed
        //
        ret = sparselm_difccs(

                levmar_solveFunc,
                // functional relation describing measurements. Given a parameter vector p,
                // computes a prediction of the measurements \hat{x}. p is nvarsx1,
                // \hat{x} is nobsx1, maximum
                //
                // void (*func)(double *p, double *hx, int nvars, int nobs, void *adata),

                NULL,
                // function to initialize the preallocated jac structure with the Jacobian's
                // non-zero pattern. Non-zero elements will be computed with the aid of finite differencing.
                // if NULL, the non-zero pattern of the Jacobian is detected automatically via an
                // exhaustive search procedure that is time-consuming and thus not recommended.
                //
                // void (*fjac)(double *p, struct splm_ccsm *jac, int nvars, int nobs, void *adata),

                // I/O: initial parameter estimates. On output has the estimated solution. size nvars
                &paramList[0],

                // I: measurement vector. size nobs. NULL implies a zero vector
                NULL,

                // I: parameter vector dimension (i.e. #unknowns) [m]
                m,

                // I: number of parameters (starting from the 1st) whose values should not be modified. >=0
                0,

                // I: measurement vector dimension [n]
                n,

                // I: number of nonzeros for the Jacobian J
                nonzeros,

                // I: number of nonzeros for the product J^t*J, -1 if unknown
                -1,

                // I: maximum number of iterations
                iterMax,

                // I: minim. options [\mu, \epsilon1, \epsilon2, \epsilon3, delta, spsolver]. Respectively the scale factor
                // for initial \mu, stopping thresholds for ||J^T e||_inf, ||dp||_2 and ||e||_2, the step used in difference
                // approximation to the Jacobian and the sparse direct solver to employ. Set to NULL for defaults to be used.
                // If \delta<0, the Jacobian is approximated with central differences which are more accurate (but more
                // expensive to compute!) compared to the forward differences employed by default.
                //
                opts,

                // O: information regarding the minimization. Set to NULL if don't care
                // info[0]=||e||_2 at initial p.
                // info[1-4]=[ ||e||_2, ||J^T e||_inf,  ||dp||_2, mu/max[J^T J]_ii ], all computed at estimated p.
                // info[5]= # iterations,
                // info[6]=reason for terminating: 1 - stopped by small gradient J^T e
                //                                 2 - stopped by small dp
                //                                 3 - stopped by itmax
                //                                 4 - singular matrix. Restart from current p with increased mu
                //                                 5 - too many failed attempts to increase damping. Restart with increased mu
                //                                 6 - stopped by small ||e||_2
                //                                 7 - stopped by invalid (i.e. NaN or Inf) "func" values. User error
                // info[7]= # function evaluations
                // info[8]= # Jacobian evaluations
                // info[9]= # linear systems solved, i.e. # attempts for reducing error
                //
                info,

                // pointer to possibly additional data, passed uninterpreted to func, fjac
                (void *) &userData);
#endif
    }
    solveBenchTicks.stop();
    solveBenchTimer.stop();
    computation.endComputation();

    // Set the solved parameters
    INFO("Setting Parameters...");
    for (i = 0; i < m; ++i) {
        std::pair<int, int> attrPair = paramToAttrList[i];
        AttrPtr attr = attrList[attrPair.first];

        // Get frame time
        MTime frame = currentFrame;
        if (attrPair.second != -1) {
            frame = frameList[attrPair.second];
        }

        double value = paramList[i];
        status = attr->setValue(value, frame, dgmod, curveChange);
        CHECK_MSTATUS(status);
    }
    dgmod.doIt();  // Commit changed data into Maya

    std::string resultStr;

    VRB("Results:");
    VRB("Solver returned " << ret << " in " << (int) info[5]
                           << " iterations");

    int reasonNum = (int) info[6];
    VRB("Reason: " << reasons[reasonNum]);
    VRB("Reason number: " << info[6]);
    VRB("");

//    VRB("Solved Parameters:");
//    for (i = 0; i < m; ++i) {
//        VRB("-> " << paramList[i]);
//    }

    // Compute the average error based on the error values
    // the solve function last computed.

    double errorAvg = 0;
    double errorMin = std::numeric_limits<double>::max();
    double errorMax = -0.0;
    double err = 0.0;
    for (i = 0; i < n; ++i) {
        err = userData.errorList[i];
        errorAvg += userData.errorList[i];
        if (err < errorMin) { errorMin = err; }
        if (err > errorMax) { errorMax = err; }
    }
    errorAvg /= (double) n;

    VRB(std::endl << std::endl << "Solve Information:");
    VRB("Initial Error: " << info[0]);
    VRB("Final Error: " << info[1]);
    VRB("Average Error: " << errorAvg);
    VRB("J^T Error: " << info[2]);
    VRB("Dp Error: " << info[3]);
    VRB("Max Error: " << info[4]);

    VRB("Iterations: " << info[5]);
    VRB("Termination Reason: " << reasons[reasonNum]);
    VRB("Function Evaluations: " << info[7]);
    VRB("Jacobian Evaluations: " << info[8]);
    VRB("Attempts for reducing error: " << info[9]);

    solveBenchTimer.print("Solve Time", 1);
    funcBenchTimer.print("Func Time", 1);
    jacBenchTimer.print("Jacobian Time", 1);
    paramBenchTimer.print("Param Time", (uint) userData.iterNum);
    errorBenchTimer.print("Error Time", (uint) userData.iterNum);
    funcBenchTimer.print("Func Time", (uint) userData.iterNum);

    solveBenchTicks.print("Solve Ticks", 1);
    funcBenchTicks.print("Func Ticks", 1);
    jacBenchTicks.print("Jacobian Ticks", 1);
    paramBenchTicks.print("Param Ticks", (uint) userData.iterNum);
    errorBenchTicks.print("Error Ticks", (uint) userData.iterNum);
    funcBenchTicks.print("Func Ticks", (uint) userData.iterNum);


    // Add all the data into the output string from the Maya command.
    resultStr = "success=" + string::numberToString<int>((bool)ret);
    outResult.append(MString(resultStr.c_str()));

    resultStr = "reason_string=" + reasons[reasonNum];
    outResult.append(MString(resultStr.c_str()));

    resultStr = "reason_num=" + string::numberToString<int>(reasonNum);
    outResult.append(MString(resultStr.c_str()));

    resultStr = "solver_parameter_list=";
    for (i = 0; i < m; ++i) {
        resultStr += string::numberToString<double>(paramList[i]);
        resultStr += " ";
    }
    outResult.append(MString(resultStr.c_str()));

    // TODO: Create a list of frames and produce an error
    // per-frame. This information will eventually be given
    // to the user to diagnose problems.
    resultStr = "error_final_list=";
    for (i = 0; i < n; ++i) {
        err = userData.errorList[i];
        resultStr += string::numberToString<double>(err);
        resultStr += " ";
    }
    outResult.append(MString(resultStr.c_str()));

    resultStr = "error_initial=" + string::numberToString<double>(info[0]);
    outResult.append(MString(resultStr.c_str()));

    resultStr = "error_final=" + string::numberToString<double>(info[1]);
    outResult.append(MString(resultStr.c_str()));

    resultStr = "error_final_average=" + string::numberToString<double>(errorAvg);
    outResult.append(MString(resultStr.c_str()));

    resultStr = "error_final_maximum=" + string::numberToString<double>(errorMax);
    outResult.append(MString(resultStr.c_str()));

    resultStr = "error_final_minimum=" + string::numberToString<double>(errorMin);
    outResult.append(MString(resultStr.c_str()));

    resultStr = "error_jt=" + string::numberToString<double>(info[2]);
    outResult.append(MString(resultStr.c_str()));

    resultStr = "error_dp=" + string::numberToString<double>(info[3]);
    outResult.append(MString(resultStr.c_str()));

    resultStr = "error_maximum=" + string::numberToString<double>(info[4]);
    outResult.append(MString(resultStr.c_str()));

    resultStr = "iteration_num=" + string::numberToString<int>((int)info[5]);
    outResult.append(MString(resultStr.c_str()));

    resultStr = "iteration_function_num=" + string::numberToString<int>((int)info[7]);
    outResult.append(MString(resultStr.c_str()));

    resultStr = "iteration_jacobian_num=" + string::numberToString<int>((int)info[8]);
    outResult.append(MString(resultStr.c_str()));

    resultStr = "iteration_attempt_num=" + string::numberToString<int>((int)info[9]);
    outResult.append(MString(resultStr.c_str()));

    resultStr = "timer_solve=" + string::numberToString<double>(solveBenchTimer.get_seconds());
    outResult.append(MString(resultStr.c_str()));

    resultStr = "timer_function=" + string::numberToString<double>(funcBenchTimer.get_seconds());
    outResult.append(MString(resultStr.c_str()));

    resultStr = "timer_jacobian=" + string::numberToString<double>(jacBenchTimer.get_seconds());
    outResult.append(MString(resultStr.c_str()));

    resultStr = "timer_parameter=" + string::numberToString<double>(paramBenchTimer.get_seconds());
    outResult.append(MString(resultStr.c_str()));

    resultStr = "timer_error=" + string::numberToString<double>(paramBenchTimer.get_seconds());
    outResult.append(MString(resultStr.c_str()));
    
    resultStr = "ticks_solve=" + string::numberToString<debug::Ticks>(solveBenchTicks.get_ticks());
    outResult.append(MString(resultStr.c_str()));

    resultStr = "ticks_function=" + string::numberToString<debug::Ticks>(funcBenchTicks.get_ticks());
    outResult.append(MString(resultStr.c_str()));

    resultStr = "ticks_jacobian=" + string::numberToString<debug::Ticks>(jacBenchTicks.get_ticks());
    outResult.append(MString(resultStr.c_str()));

    resultStr = "ticks_parameter=" + string::numberToString<debug::Ticks>(paramBenchTicks.get_ticks());
    outResult.append(MString(resultStr.c_str()));

    resultStr = "ticks_error=" + string::numberToString<debug::Ticks>(paramBenchTicks.get_ticks());
    outResult.append(MString(resultStr.c_str()));

    // TODO: Compute the errors of all markers so we can add it to a vector
    // and return it to the user. This vector should be resized so we can
    // return frame-based information. The UI could then graph this information.
    return ret != -1;
}


#endif // MAYA_MM_SOLVER_UTILS_H
