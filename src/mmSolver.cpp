/*
 * Sets up the Bundle Adjustment data and sends it off to the bundling algorithm.
 *
 */

#include <mmSolver.h>


// Lev-Mar
#include <levmar.h>  // dlevmar_bc_dif


// STL
#include <ctime>     // time
#include <cmath>     // exp
#include <iostream>  // cout, cerr, endl
#include <string>    // string
#include <vector>    // vector
#include <cassert>   // assert
#include <limits>    // double max value

// Utils
#include <utilities/debugUtils.h>
#include <utilities/stringUtils.h>

// Maya
#include <maya/MGlobal.h>
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
#include <mayaUtils.h>


int countUpNumberOfErrors(MarkerPtrList markerList,
                          MTimeArray frameList,
                          MarkerPtrList &validMarkerList,
                          std::vector<MPoint> &markerPosList,
                          IndexPairList &errorToMarkerList,
                          MStatus &status) {
    // Count up number of errors
    // For each marker on each frame that it is valid, we add ERRORS_PER_MARKER errors.
    int i = 0;
    int j = 0;

    int numErrors = 0;
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
                // First index is into 'markerList'
                // Second index is into 'frameList'
                IndexPair markerPair(i, j);
                errorToMarkerList.push_back(markerPair);
                numErrors += ERRORS_PER_MARKER;

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
    return numErrors;
}


int countUpNumberOfUnknownParameters(AttrPtrList attrList,
                                     MTimeArray frameList,
                                     AttrPtrList &camStaticAttrList,
                                     AttrPtrList &camAnimAttrList,
                                     AttrPtrList &staticAttrList,
                                     AttrPtrList &animAttrList,
                                     std::vector<double> &paramLowerBoundList,
                                     std::vector<double> &paramUpperBoundList,
                                     std::vector<double> &paramWeightList,
                                     IndexPairList &paramToAttrList,
                                     MStatus &status) {
    // Count up number of unknown parameters
    int i = 0;      // index of marker
    int j = 0;      // index of frame
    int numUnknowns = 0;

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
            numUnknowns += frameList.length();
            for (j = 0; j < (int) frameList.length(); ++j) {
                // first index is into 'attrList'
                // second index is into 'frameList'
                IndexPair attrPair(i, j);
                paramToAttrList.push_back(attrPair);

                // Min / max parameter bounds.
                double minValue = attr->getMinimumValue();
                double maxValue = attr->getMaximumValue();
                paramLowerBoundList.push_back(minValue);
                paramUpperBoundList.push_back(maxValue);

                // TODO: Get a weight value from the attribute. Currently
                // weights are not supported in the Maya mmSolver command.
                paramWeightList.push_back(1.0);
            }

            if (attrIsPartOfCamera) {
                camAnimAttrList.push_back(attr);
            } else {
                animAttrList.push_back(attr);
            }
        } else if (attr->isFreeToChange()) {
            ++numUnknowns;
            // first index is into 'attrList'
            // second index is into 'frameList', '-1' means a static value.
            IndexPair attrPair(i, -1);
            paramToAttrList.push_back(attrPair);

            // Min / max parameter bounds.
            double minValue = attr->getMinimumValue();
            double maxValue = attr->getMaximumValue();
            paramLowerBoundList.push_back(minValue);
            paramUpperBoundList.push_back(maxValue);

            // TODO: Get a weight value from the attribute. Currently
            // weights are not supported in the Maya mmSolver command.
            paramWeightList.push_back(1.0);

            if (attrIsPartOfCamera) {
                camStaticAttrList.push_back(attr);
            } else {
                staticAttrList.push_back(attr);
            }
        }
        i++;
    }
    return numUnknowns;
}


/*
 * TODO: Answer this question: 'for each marker, determine which attributes
 * can affect it's bundle.'
 *
 * Detect inputs and outputs for marker-bundle relationships. For each
 * marker, get the bundle, then find all the attributes that affect the bundle
 * (and it's parent nodes). If the bundle cannot be affected by any attribute
 * in the solver, print a warning and remove it from the solve list.
 *
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
 */
void findErrorToParameterRelationship(MarkerPtrList markerList,
                                      AttrPtrList attrList,
                                      MTimeArray frameList,
                                      int numParameters,
                                      int numErrors,
                                      IndexPairList paramToAttrList,
                                      IndexPairList errorToMarkerList,
                                      BoolList2D &markerToAttrMapping,
                                      BoolList2D &errorToParamMapping,
                                      MStatus &status) {
    int i, j;

    // Command execution options
    bool display = false;  // print out what happens in the python command.
    bool undoable = false;  // we won't modify the scene in any way, only make queries.
    MString cmd = "";
    MStringArray result1;
    MStringArray result2;

    // Calculate the relationship between attributes and markers.
    markerToAttrMapping.resize(markerList.size());
    i = 0;      // index of marker
    j = 0;      // index of attribute
    for (MarkerPtrListCIt mit = markerList.begin(); mit != markerList.end(); ++mit) {
        MarkerPtr marker = *mit;
        CameraPtr cam = marker->getCamera();
        BundlePtr bundle = marker->getBundle();

        // Get node names.
        const char *markerName = marker->getNodeName().asChar();
        const char *camName = cam->getTransformNodeName().asChar();
        const char *bundleName = bundle->getNodeName().asChar();

        // Find list of plug names that are affected by the bundle.
        cmd += "import mmSolver.api as mmapi;";
        cmd += "mmapi.find_attrs_affecting_transform(";
        cmd += "\"";
        cmd += bundleName;
        cmd += "\"";
        cmd += ");";
        status = MGlobal::executePythonCommand(cmd, result1, display, undoable);
        INFO("Python result1 num: " << result1.length());

        // Find list of plug names that are affected by the marker (and camera projection matrix).
        cmd = "";
        cmd += "import mmSolver.api as mmapi;";
        cmd += "mmapi.find_attrs_affecting_transform(";
        cmd += "\"";
        cmd += markerName;
        cmd += "\", ";
        cmd += "cam_tfm=\"";
        cmd += camName;
        cmd += "\"";
        cmd += ");";
        status = MGlobal::executePythonCommand(cmd, result2, display, undoable);
        INFO("Python result2 num: " << result2.length());

        // Determine if the marker can affect the attribute.
        MString affectedPlugName;
        markerToAttrMapping[i].resize(attrList.size(), false);
        for (AttrPtrListCIt ait = attrList.begin(); ait != attrList.end(); ++ait) {
            AttrPtr attr = *ait;

            // Get attribute full path.
            MPlug plug = attr->getPlug();
            MObject attrNode = plug.node();
            MFnDagNode attrFnDagNode(attrNode);
            MString attrNodeName = attrFnDagNode.fullPathName();
            MString attrAttrName = plug.partialName(false, true, true, false, false, true);
            MString attrName = attrNodeName + "." + attrAttrName;

            // Bundle affects attribute
            for (int k = 0; k < result1.length(); ++k) {
                affectedPlugName = result1[k];
                if (attrName == affectedPlugName) {
                    markerToAttrMapping[i][j] = true;
                    break;
                }
            }

            // Marker (or camera) affects attribute
            for (int k = 0; k < result2.length(); ++k) {
                affectedPlugName = result2[k];
                if (attrName == affectedPlugName) {
                    markerToAttrMapping[i][j] = true;
                    break;
                }
            }

            ++j;
        }
        ++i;
    }

    // Calculate the relationship between errors and parameters.
    /*
     * TODO: For each error, work out which parameters can affect it. The
     * parameters may be static or animated and thereby each parameter may
     * affect one or more errors. A single parameter will affect a range of
     * time values, a static parameter affects all time values, but a dynamic
     * parameter will be split into many parameters at different frames, each
     * of those dynamic parameters will only affect a small number of errors.
     * Our goal is to compute a boolean for each error and parameter
     * combination, if the boolean is true the relationship is positive, if
     * false, the computation is skipped and the error returned is zero.
     * This combination is only relevant if the markerToAttrMapping is
     * already true, otherwise we can assume such error/parameter combinations
     * will not be required.
     */
    int markerIndex = 0;
    int markerFrameIndex = 0;
    int attrIndex = 0;
    int attrFrameIndex = 0;
    IndexPair markerIndexPair;
    IndexPair attrIndexPair;
    errorToParamMapping.resize(numErrors);
    i = 0;      // index of error
    j = 0;      // index of parameter
    for (i = 0; i < (numErrors / ERRORS_PER_MARKER); ++i) {
        INFO("i=" << i
                  << " numErrors=" << numErrors
                  << " errorToMarkerList.size()=" << errorToMarkerList.size());
        markerIndexPair = errorToMarkerList[i];
        markerIndex = markerIndexPair.first;
        markerFrameIndex = markerIndexPair.second;
        INFO("markerIndex=" << markerIndex);
        INFO("markerFrameIndex=" << markerFrameIndex);

        MarkerPtr marker = markerList[markerIndex];
        CameraPtr cam = marker->getCamera();
        BundlePtr bundle = marker->getBundle();
        MTime markerFrame = frameList[markerFrameIndex];

        // Get node names.
        const char *markerName = marker->getNodeName().asChar();
        const char *camName = cam->getTransformNodeName().asChar();
        const char *bundleName = bundle->getNodeName().asChar();
        INFO("Marker: " << markerName);
        INFO("MarkerFrame: " << markerFrame.asUnits(MTime::uiUnit()));

        // Determine if the marker can affect the attribute.
        errorToParamMapping[i].resize(numParameters, false);
        for (j = 0; j < numParameters; ++j) {
            INFO("j=" << j
                      << " numParameters=" << numParameters
                      << " paramToAttrList.size()=" << paramToAttrList.size());
            attrIndexPair = paramToAttrList[j];
            attrIndex = attrIndexPair.first;
            attrFrameIndex = attrIndexPair.second;
            INFO("attrIndex=" << attrIndex);
            INFO("attrFrameIndex=" << attrFrameIndex);

            // If the attrFrameIndex is -1, then the attribute is static,
            // not animated.
            AttrPtr attr = attrList[attrIndex];
            MTime attrFrame(-1.0, MTime::uiUnit());
            if (attrFrameIndex >= 0) {
                attrFrame = frameList[attrFrameIndex];
            }
            const char *attrName = attr->getName().asChar();
            INFO("Attr: " << attrName);
            INFO("AttrFrame: " << attrFrame.asUnits(MTime::uiUnit()));

            bool markerAffectsAttr = markerToAttrMapping[markerIndex][attrIndex];
            if (markerAffectsAttr == false) {
                errorToParamMapping[i][j] = markerAffectsAttr;
                continue;
            }

            bool paramAffectsError = true;
            // TODO: Compute 'paramAffectsError' value.
            errorToParamMapping[i][j] = paramAffectsError;

            INFO("i=" << i << " | j=" << j
                      << " : " << paramAffectsError);
        }
    }

    return;
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
    int i = 0;
    int j = 0;
    MStatus status;
    int ret = true;
    int profileCategory = MProfiler::getCategoryIndex("mmSolver");
    MProfilingScope profilingScope(profileCategory, MProfiler::kColorC_L3, "solve");

    // Indexing maps
    IndexPairList paramToAttrList;
    IndexPairList errorToMarkerList;

    // Cache out the marker positions in screen-space, so we don't need to query
    // them during solving.
    std::vector<MPoint> markerPosList;

    // Errors and parameters as used by the solver.
    std::vector<double> errorList(1);
    std::vector<double> paramList(1);

    // Number of unknown parameters.
    int m = 0;

    // Number of measurement errors.
    // (Must be less than or equal to number of unknown parameters).
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
    std::vector<double> paramLowerBoundList;
    std::vector<double> paramUpperBoundList;
    std::vector<double> paramWeightList;
    m = countUpNumberOfUnknownParameters(
            attrList,
            frameList,
            camStaticAttrList,
            camAnimAttrList,
            staticAttrList,
            animAttrList,
            paramLowerBoundList,
            paramUpperBoundList,
            paramWeightList,
            paramToAttrList,
            status
    );
    INFO("camStaticAttrList.size() = " << camStaticAttrList.size());
    INFO("camAnimAttrList.size() = " << camAnimAttrList.size());
    INFO("staticAttrList.size() = " << staticAttrList.size());
    INFO("animAttrList.size() = " << animAttrList.size());
    assert(paramLowerBoundList.size() == m);
    assert(paramUpperBoundList.size() == m);
    assert(paramWeightList.size() == m);

    // Which markers affect which attributes?
    BoolList2D markerToAttrMapping;
    BoolList2D errorToParamMapping;
    findErrorToParameterRelationship(
            markerList,
            attrList,
            frameList,
            m,  // Number of parameters.
            n,  // Number of errors.
            paramToAttrList,
            errorToMarkerList,
            markerToAttrMapping,
            errorToParamMapping,
            status
    );
    // INFO("markerToAttrMapping.size() = " << markerToAttrMapping.size());
    for (i = 0; i < markerToAttrMapping.size(); ++i) {
        // INFO("i = " << i);
        // INFO("markerToAttrMapping[" << i << "].size() = " << markerToAttrMapping[i].size());
        for (j = 0; j < markerToAttrMapping[i].size(); ++j) {
            // INFO("j = " << j);
            INFO("mkr=" << i << " : attr=" << j << " | " << markerToAttrMapping[i][j]);
        }
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

    // Set Initial parameters
    VRB("Set Initial parameters");
    MTime currentFrame = MAnimControl::currentTime();
    i = 0;
    for (i = 0; i < m; ++i) {
        IndexPair attrPair = paramToAttrList[i];
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
    assert(solverType == SOLVER_TYPE_LEVMAR);

    // Start Solving
    solveBenchTimer.start();
    solveBenchTicks.start();

    // Solving Objects.
    struct LevMarSolverData userData;
    userData.cameraList = cameraList;
    userData.markerList = markerList;  // TODO: Can we replace this with valid marker list?
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
        work = (double *) malloc((LM_BC_DIF_WORKSZ(m, n) + m * m) * sizeof(double));
        if (!work) {
            ERR("Memory allocation request failed.");
            return false;
        }
        covar = work + LM_BC_DIF_WORKSZ(m, n);

        // Solve!
        ret = dlevmar_bc_dif(

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

                // vector of lower bounds. If NULL, no lower bounds apply
                &paramLowerBoundList[0],
//                NULL,

                // vector of upper bounds. If NULL, no upper bounds apply (input only)
                &paramUpperBoundList[0],
//                NULL,

                // diagonal scaling constants. NULL implies no scaling (input only)
                &paramWeightList[0],
//                NULL,

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
        IndexPair attrPair = paramToAttrList[i];
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

    // TODO: Compute the errors of all markers so we can add it to a vector
    // and return it to the user. This vector should be resized so we can
    // return frame-based information. The UI could then graph this information.
    return ret != -1;
}
