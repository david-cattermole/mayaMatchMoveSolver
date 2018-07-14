/*
 * Sets up the Bundle Adjustment data and sends it off to the bundling algorithm.
 *
 * TODO: Detect inputs and outputs for marker-bundle relationships. For each
 * marker, get the bundle, then find all the attributes that affect the bundle
 * (and it's parent nodes). If the bundle cannot be affected by any attribute
 * in the solver, print a warning and remove it from the solve list.
 * This relationship building will be the basis for the Ceres
 * residual/parameter block creation. Note we do not need to worry about time
 * in our relationship building, connections cannot be made at different
 * times (and if they did, that would be stupid). This relationship building
 * could mean we only need to measure a limited number of bundles, hence
 * improving performance.
 *
 * There are special cases for detecting inputs/outputs between markers and attributes.
 * - Any transform node/attribute above the marker in the DAG that affects the world transform.
 * - Cameras; transform attributes and focal length will affect all markers
 *
 * # Here is some WIP Python code to detect input/outputs:
 * import maya.OpenMaya as OpenMaya
 * import mmSolver._api as mmapi
 * obj = mmapi.utils.get_as_object('Track_02_MKR')
 * it = OpenMaya.MItDependencyGraph(obj, OpenMaya.MFn.kInvalid, OpenMaya.MItDependencyGraph.kUpstream)
 * while not it.isDone():
 *     # print it
 *     cur = it.currentItem()
 *     depNodeFn = OpenMaya.MFnDependencyNode(cur)
 *     nodePath = depNodeFn.name()
 *     print nodePath
 *     it.next()
 *
 */

#include <mmSolver.h>

#ifndef HAVE_SPLM
#error "HAVE_SPLM were not defined."
#endif

#ifdef HAVE_SPLM
#if HAVE_SPLM == 0
#warning "HAVE_SPLM was not given."
#endif
#endif

#ifdef HAVE_CERES
#if HAVE_CERES == 0
#warning "HAVE_CERES was not given."
#endif
#endif

// Lev-Mar
#include <levmar.h>  // dlevmar_dif

// Sparse Lev-Mar
#if HAVE_SPLM == 1

#include <splm.h>    // sparselm_difccs

#endif

// Ceres
#if HAVE_CERES == 1

#include <ceres/ceres.h>

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
#include <maya/MItDependencyGraph.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MMatrix.h>
#include <maya/MFloatMatrix.h>
#include <maya/MFnCamera.h>
#include <maya/MComputation.h>
#include <maya/MProfiler.h>

#include <mmSolverLevMar.h>
#include <mmSolverCeres.h>
#include <mayaUtils.h>


int countUpNumberOfErrors(MarkerPtrList markerList,
                          MTimeArray frameList,
                          MarkerPtrList &validMarkerList,
                          std::vector<MPoint> markerPosList,
                          IndexPairList &errorToMarkerList,
                          MStatus &status) {
    // Count up number of errors
    // For each marker on each frame that it is valid, we add ERRORS_PER_MARKER errors.
    register int i = 0;
    register int j = 0;

    int num_errors = 0;

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

            if ((enable == true) && (weight > 0.0)) {
                IndexPair markerPair(i, j);
                errorToMarkerList.push_back(markerPair);
                num_errors += ERRORS_PER_MARKER;

                validMarkerList.push_back(marker);

                // Get Marker Position.
                MMatrix cameraWorldProjectionMatrix;
                CameraPtr camera = marker->getCamera();
                status = camera->getWorldProjMatrix(cameraWorldProjectionMatrix, frame);
                CHECK_MSTATUS(status);
                MPoint marker_pos;
                status = marker->getPos(marker_pos, frame);
                CHECK_MSTATUS(status);
                marker_pos = marker_pos * cameraWorldProjectionMatrix;
                marker_pos.cartesianize();
                markerPosList.push_back(marker_pos);
            }
        }
        i++;
    }
    return num_errors;
}


/*
 * TODO: Answer this question: 'for each marker, determine which attributes
 * can affect it's bundle.'
 *
 * Detect inputs and outputs for marker-bundle relationships. For each
 * marker, get the bundle, then find all the attributes that affect the bundle
 * (and it's parent nodes). If the bundle cannot be affected by any attribute
 * in the solver, print a warning and remove it from the solve list.
 * This relationship building will be the basis for the Ceres
 * residual/parameter block creation. Note we do not need to worry about time
 * in our relationship building, connections cannot be made at different
 * times (and if they did, that would be stupid). This relationship building
 * could mean we only need to measure a limited number of bundles, hence
 * improving performance.
 *
 * There are special cases for detecting inputs/outputs between markers and attributes.
 * - Any transform node/attribute above the marker in the DAG that affects the world transform.
 * - Cameras; transform attributes and focal length will affect all markers
 */
int countUpNumberOfUnknownParameters(AttrPtrList attrList,
                                     MTimeArray frameList,
                                     AttrPtrList &camStaticAttrList,
                                     AttrPtrList &camAnimAttrList,
                                     AttrPtrList &staticAttrList,
                                     AttrPtrList &animAttrList,
                                     IndexPairList &paramToAttrList,
                                     MStatus &status) {
    // Count up number of unknown parameters
    register int i = 0;      // index of marker
    register int j = 0;      // index of frame

    int m = 0;

    // int k = 0;  // index of errorToMarkerList
    for (AttrPtrListIt ait = attrList.begin(); ait != attrList.end(); ++ait) {
        AttrPtr attr = *ait;
        MObject nodeObj = attr->getObject();
        bool attrIsPartOfCamera = false;

        MFnDependencyNode dependNode(nodeObj);
        if (nodeObj.apiType() == MFn::kTransform) {
            MFnDagNode dagNode(nodeObj);
            for (int k = 0; k < dagNode.childCount(); ++k) {
                MObject childObj = dagNode.child(k, &status);
                CHECK_MSTATUS(status);
                if (childObj.apiType() == MFn::kCamera) {
                    attrIsPartOfCamera = true;
                }
            }

            // // TODO: Look up affected attributes to make sure the
            // // attribute really does belong to the camera and will
            // // affect the solve.
            // MObjectArray attrObjs;
            // MString worldMatrixAttrName = "worldMatrix";
            // MObject attributeObj = dependNode.attribute(worldMatrixAttrName, &status);
            // CHECK_MSTATUS(status);
            // dependNode.getAffectedAttributes(attributeObj, attrObjs);

        } else if (nodeObj.apiType() == MFn::kCamera) {
            attrIsPartOfCamera = true;
        }

        if (attr->isAnimated()) {
            m += frameList.length();
            for (j = 0; j < (int) frameList.length(); ++j) {
                // first index is into 'attrList'
                // second index is into 'frameList'
                IndexPair attrPair(i, j);
                paramToAttrList.push_back(attrPair);
            }

            if (attrIsPartOfCamera) {
                camAnimAttrList.push_back(attr);
            } else {
                animAttrList.push_back(attr);
            }
        } else if (attr->isFreeToChange()) {
            ++m;
            // first index is into 'attrList'
            // second index is into 'frameList', '-1' means a static value.
            std::pair<int, int> attrPair(i, -1);
            paramToAttrList.push_back(attrPair);

            if (attrIsPartOfCamera) {
                camStaticAttrList.push_back(attr);
            } else {
                staticAttrList.push_back(attr);
            }
        }
        i++;
    }
    return m;
}


void findMarkerToAttrRelationship(MarkerPtrList validMarkerList,
                                  AttrPtrList camStaticAttrList,
                                  AttrPtrList camAnimAttrList,
                                  AttrPtrList staticAttrList,
                                  AttrPtrList animAttrList,
                                  BoolList2D &markerToAttrMapping,
                                  MStatus &status) {
    register int i = 0;      // index of marker
    register int j = 0;      // index of frame

    markerToAttrMapping.resize(validMarkerList.size());

    for (MarkerPtrListCIt mit = validMarkerList.begin(); mit != validMarkerList.end(); ++mit) {
        MarkerPtr marker = *mit;
        std::vector<bool> attrMapping;

        CameraPtr cam = marker->getCamera();

        // TODO: Recurse above camera transform in DAG, add all transforms to the list.
        MObjectArray camTfmObjs;
        camTfmObjs.append(cam->getTransformObject());

        MObject camTfmObj = cam->getTransformObject();
        MObject camShpObj = cam->getShapeObject();
        // TODO: If 'attr' is on camTfmObj or camShpObj, save the relationship
        // between the marker and attr. These attrs should go into a special
        // block of parameters, these camera attrs will affect all attrs.

        for (AttrPtrListCIt ait = camStaticAttrList.begin(); ait != camStaticAttrList.end(); ++ait) {
            AttrPtr attr = *ait;
            // markerToAttrMapping
        }

        // TODO: Find the attributes that affect this marker. If we cannot
        // detect any attributes, print a warning and drop the marker from
        // the list???

        // For each attribute, loop over all markers, find the camera, if
        // the attribute is on the camera, add the relationship. Next, find
        // the bundle from the marker, check if the attribute is on the
        // bundle, if so add the relationship, if not, continue. Now look
        // at the node above the bundle, check if the attribute is on the
        // node, continue until we reach the root world node.
        //
        // NOTE: We can also use MFnDependencyNode::getAffectedAttributes
        // and MFnDependencyNode::getAffectedByAttributes to detect which
        // attributes are actually affecting the matrix or world matrix
        // of a transform node, etc.


        // TODO: Look up the graph
//        MObject attrNodeObj = attr->getObject();
//        MItDependencyGraph dgIt(
//                attrNodeObj,
//                MFn::kInvalid, // all node types
//                MItDependencyGraph::kUpstream // From destination to source
//        );
//        while (!dgIt.isDone(&status)) {
//            CHECK_MSTATUS(status);
//
//            MObject item = dgIt.currentItem(&status);
//            CHECK_MSTATUS(status);
//
//            MFnDependencyNode depNodeFn = MFnDependencyNode(item);
//            // nodePath = depNodeFn.name()
//            // depNodeFn.getAffectedAttributes()
//            // depNodeFn.
//
//        }

        i++;
    }
}


bool solve(int iterMax,
           double tau,
           double eps1,
           double eps2,
           double eps3,
           double delta,
           int solverType,
           CameraPtrList cameraList,
           MarkerPtrList markerList,
           BundlePtrList bundleList,
           AttrPtrList attrList,
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

    // Indexing maps
    IndexPairList paramToAttrList;
    IndexPairList errorToMarkerList;

    // Cache out the marker positions in screen-space

    std::vector<MPoint> markerPosList;
    // Errors and parameters as used by the solver.
    std::vector<double> errorList(1);
    std::vector<double> paramList(1);

    // Number of unknown parameters.
    int m = 0;

    // Number of measurement errors. (Must be less than or equal to number of unknown parameters).
    int n = 0;

    // Count up number of errors
    MarkerPtrList validMarkerList;
    n = countUpNumberOfErrors(
            markerList,
            frameList,
            validMarkerList,
            markerPosList,
            errorToMarkerList,
            status
    );

    // Count up number of unknown parameters
    AttrPtrList camStaticAttrList;
    AttrPtrList camAnimAttrList;
    AttrPtrList staticAttrList;
    AttrPtrList animAttrList;
    m = countUpNumberOfUnknownParameters(
            attrList,
            frameList,
            camStaticAttrList,
            camAnimAttrList,
            staticAttrList,
            animAttrList,
            paramToAttrList,
            status
    );

    // Which markers affect which attributes?
    BoolList2D markerToAttrMapping;
    findMarkerToAttrRelationship(
            validMarkerList,
            camStaticAttrList,
            camAnimAttrList,
            staticAttrList,
            animAttrList,
            markerToAttrMapping,
            status
    );

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

    // Determine the solver type, levmar, sparse levmar or ceres, etc.
    bool solverIsCeres = false;
    switch (solverType) {

        case SOLVER_TYPE_LEVMAR:
            solverIsCeres = false;
            break;

        case SOLVER_TYPE_LEVMAR_SPARSE:
#if HAVE_SPLM == 0
            WRN("Selected solver type \'SparseLM\' is not available, switching to \'Lev-Mar\' instead.");
            solverType = SOLVER_TYPE_LEVMAR;
#endif
            solverIsCeres = false;
            break;

        case SOLVER_TYPE_CERES:
        case SOLVER_TYPE_CERES_TRUST_REGION_DENSE_QR:
        case SOLVER_TYPE_CERES_TRUST_REGION_SPARSE_NORMAL_CHOLESKY:
        case SOLVER_TYPE_CERES_TRUST_REGION_DENSE_SCHUR:
        case SOLVER_TYPE_CERES_TRUST_REGION_SPARSE_SCHUR:
        case SOLVER_TYPE_CERES_TRUST_REGION_ITERATIVE_SCHUR:
            solverIsCeres = true;
#if HAVE_CERES == 0
        WRN("Selected solver type \'Ceres\' is not available, switching to \'Lev-Mar\' instead.");
        solverType = SOLVER_TYPE_LEVMAR;
        solverIsCeres = false;
#endif
            break;

        default:
            assert(false); // Bad solver type.
            break;
    }

    // Start Solving
    if (!solverIsCeres) {
        solveBenchTimer.start();
        solveBenchTicks.start();

        // Solving Objects.
        struct LevMarSolverData userData;
        userData.cameraList = cameraList;
        userData.markerList = markerList;
        userData.bundleList = bundleList;
        userData.attrList = attrList;
        userData.frameList = frameList;

        // Indexing maps
        userData.paramToAttrList = paramToAttrList;
        userData.errorToMarkerList = errorToMarkerList;
        userData.markerPosList = markerPosList;

        // Solver Aux data
        userData.errorList = errorList;
        userData.iterNum = 0;
        userData.jacIterNum = 0;
        userData.iterMax = iterMax;
        userData.isJacobianCalculation = false;
        userData.imageWidth = 2048.0;  // TODO: Get actual image plane resolution.

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

        // Options and Info
        unsigned int optsSize = LM_OPTS_SZ;
        unsigned int infoSize = LM_INFO_SZ;
#if HAVE_SPLM == 1
        if (solverType == SOLVER_TYPE_LEVMAR_SPARSE) {
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

        if (solverType == SOLVER_TYPE_LEVMAR) {

            // TODO: Define a jacobian function to calculate the jacobian
            // matrix explicitly.
            // TODO: Determine a function that will 'guess' the 'delta' value
            // for the jacobian function parameters. We could experiment with
            // distance from camera, or simply based on a general look up
            // tables. For 'angle' based attributes, use 1 or 5 degrees, for distance use 1cm, or 1,000cm when the transform is far away from the camera.
            // TODO: Use the Maya DG graph structure to determine the sparsity
            // structure, a relation of cause and effect; which attributes
            // affect which markers.
            // TODO: Add 'Box Constraint' variant of levmar. Lower/upper
            // bounds is set based on the Attribute parameters given, or
            // if none are given, default to the double minimum and maximum
            // limits.

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
                    levmarSolveFunc,

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
        } else if (solverType == SOLVER_TYPE_LEVMAR_SPARSE) {
#if HAVE_SPLM == 1

            // TODO: We could calculate an (approximate) non-zero value. We can do this by assuming that all dynamic
            // attributes solve on on all single frames and are independant of static attributes.

            // Calculate number of non-zeros.
            int nonzeros = 0;  // Estimated non-zeros

            nonzeros = (n * m) / 2;  // Estimated non-zeros

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

                    levmarSolveFunc,
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
        } else {
            ERR("Solver type is expected to be a levmar variant. solverType=" << solverType);
            return false;
        }


        solveBenchTicks.stop();
        solveBenchTimer.stop();
        computation.endComputation();

        // Set the solved parameters
        VRB("Setting Parameters...");
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

//        VRB("Solved Parameters:");
//        for (i = 0; i < m; ++i) {
//            VRB("-> " << paramList[i]);
//        }

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

        if (verbose) {
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
        }

        // Add all the data into the output string from the Maya command.
        resultStr = "success=" + string::numberToString<int>((bool) ret);
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

        resultStr = "iteration_num=" + string::numberToString<int>((int) info[5]);
        outResult.append(MString(resultStr.c_str()));

        resultStr = "iteration_function_num=" + string::numberToString<int>((int) info[7]);
        outResult.append(MString(resultStr.c_str()));

        resultStr = "iteration_jacobian_num=" + string::numberToString<int>((int) info[8]);
        outResult.append(MString(resultStr.c_str()));

        resultStr = "iteration_attempt_num=" + string::numberToString<int>((int) info[9]);
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

    } else {
        if (solverType == SOLVER_TYPE_CERES_TRUST_REGION_SPARSE_SCHUR) {
            struct CeresSolverData userData;

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
            userData.numParameters = m;
            userData.numErrors = n;
            userData.errorList = errorList;
            userData.iterNum = 0;
            userData.jacIterNum = 0;
            userData.iterMax = iterMax;
            userData.isJacobianCalculation = false;
            userData.imageWidth = 2048.0;  // TODO: Get actual image plane resolution.

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

            // Define the cost function
            ceres::CostFunction *cost_function = ReprojectionErrorFunctor::create(userData);
            ceres::DynamicNumericDiffCostFunction <ReprojectionErrorFunctor, ceres::CENTRAL> *dyn_cost_function =
                    static_cast<ceres::DynamicNumericDiffCostFunction <ReprojectionErrorFunctor, ceres::CENTRAL> *>(cost_function);
            dyn_cost_function->AddParameterBlock(m);
            dyn_cost_function->SetNumResiduals(n);

            // Create the problem
            ceres::Problem problem;
            problem.AddResidualBlock(
                    cost_function,
                    NULL, // CauchyLoss(1.0), HuberLoss(1.0), NULL=squared loss,
                    &paramList[0]
            );
            problem.AddParameterBlock(&paramList[0], m);

            // Run the solver!
            ceres::Solver::Options options;
            options.minimizer_progress_to_stdout = true;
            // options.gradient_tolerance = 1e-12;
            // options.function_tolerance = 1e-6;
            // options.max_num_iterations = iterMax;
            options.num_threads = 1;
            options.num_linear_solver_threads = 1;
            // options.min_trust_region_radius = eps1;
            options.dense_linear_algebra_library_type = ceres::LAPACK;
            // options.min_linear_solver_iterations = 5;
            // options.max_linear_solver_iterations = 500;
            // options.linear_solver_type = ceres::DENSE_QR;
            // options.linear_solver_type = ceres::SPARSE_NORMAL_CHOLESKY;
            // options.linear_solver_type = ceres::DENSE_SCHUR;
            options.linear_solver_type = ceres::SPARSE_SCHUR;
            ceres::Solver::Summary summary;
            ceres::Solve(options, &problem, &summary);
            INFO(summary.FullReport());

#if 0  // Turn off the SOLVER_TYPE_CERES, as the implementation is incomplete.
        } else if (solverType == SOLVER_TYPE_CERES) {
            // TODO: Use 'Problem::SetParameterLowerBound' and
            // 'Problem::SetParameterUpperBound' to allow the user to specify
            // the min and max values for the parameter.

            ceres::Problem problem;

            // Create parameter blocks
            i = 0;
            for (AttrPtrListIt ait = attrList.begin(); ait != attrList.end(); ++ait) {
                AttrPtr attr = *ait;
                if (attr->isAnimated()) {
                    for (j = 0; j < (int) frameList.length(); ++j) {
                        INFO("parameter block: "
                                     << i << " " << " at " << frameList[j]
                                     // << " | " << &paramList[0]+i
                                     << " | " << attr->getName());
//                        problem.AddParameterBlock(&paramList[0]+i, 1);
//                        problem.SetParameterLowerBound(&paramList[0]+i, 0, attr->getMinimumValue());
//                        problem.SetParameterUpperBound(&paramList[0]+i, 0, attr->getMaximumValue());
                        ++i;
                    }
                } else if (attr->isFreeToChange()) {
                    INFO("parameter block: "
                                 << i << " at -1 | "
                                 // << &paramList[0]+i
                                 << " | " << attr->getName());
//                    problem.AddParameterBlock(&paramList[0]+i, 1);
//                    problem.SetParameterLowerBound(&paramList[0]+i, 0, attr->getMinimumValue());
//                    problem.SetParameterUpperBound(&paramList[0]+i, 0, attr->getMaximumValue());
                    ++i;
                }
            }

            // problem.AddParameterBlock(&paramList[0], m);

            // Add residuals
            for (i = 0; i < (n / ERRORS_PER_MARKER); ++i) {
                std::pair<int, int> markerPair = errorToMarkerList[i];
                MarkerPtr marker = markerList[markerPair.first];
                MTime frame = frameList[markerPair.second];
                CameraPtr camera = marker->getCamera();
                BundlePtr bundle = marker->getBundle();

                // Get Marker Position.
                MMatrix cameraWorldProjectionMatrix;
                status = camera->getWorldProjMatrix(cameraWorldProjectionMatrix, frame);
                CHECK_MSTATUS(status);
                MPoint marker_pos;
                status = marker->getPos(marker_pos, frame);
                CHECK_MSTATUS(status);
                marker_pos = marker_pos * cameraWorldProjectionMatrix;
                marker_pos.cartesianize();

                INFO("residual: "
                             << i << " at " << frame
                             << " | " << marker->getNodeName()
                             << " | " << marker_pos.x << ", " << marker_pos.y << ", " << marker_pos.z);

                MarkerBundleCameraData data();
                data.marker_pos = marker_pos;
                data.marker = marker;
                data.bundle = bundle;
                data.camera = camera;
                data.attrList = attrList;
                data.frame = frame;
                data.frameList = frameList;
                data.paramToAttrList = paramToAttrList;
                data.numParameters = m;
                data.numErrors = ERRORS_PER_MARKER;
                data.dgmod = &dgmod;
                data.curveChange = &curveChange;
                data.verbose = verbose;

                ceres::DynamicNumericDiffCostFunction <MarkerBundleCameraCostFunctor, ceres::CENTRAL> *cost_function =
                        MarkerBundleCameraCostFunctor::create(data);

                int parameterSize = m;
                cost_function->SetNumResiduals(ERRORS_PER_MARKER); // Cause
                cost_function->AddParameterBlock(parameterSize);   // Effect
                problem.AddResidualBlock(
                        static_cast<ceres::CostFunction *>(cost_function),
                        NULL, // new ceres::HuberLoss(1.0), CauchyLoss(1.0), NULL=squared loss,
                        &paramList[0]
                );
            }

            // Run the solver!
            ceres::Solver::Options options;
            options.minimizer_progress_to_stdout = true;
            options.num_threads = 1;
            options.num_linear_solver_threads = 1;
            options.max_num_iterations = iterMax;
            // use_nonmonotonic_steps; Allow the solver to accept parameters values that increase the error in
            // the short-term, but will find a better overall error.
            options.use_nonmonotonic_steps = true;
            options.dense_linear_algebra_library_type = ceres::LAPACK;
            options.linear_solver_type = ceres::SPARSE_SCHUR;
            ceres::Solver::Summary summary;
            ceres::Solve(options, &problem, &summary);
            INFO(summary.FullReport());
#endif

        } else {
            ERR("Solver type is expected to be a levmar variant. solverType=" << solverType);
            return false;
        }
    }


    // TODO: Compute the errors of all markers so we can add it to a vector
    // and return it to the user. This vector should be resized so we can
    // return frame-based information. The UI could then graph this information.
    return ret != -1;
}

