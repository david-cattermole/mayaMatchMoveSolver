/*
 * Sets up the Bundle Adjustment data and sends it off to the bundling algorithm.
 *
 */

#include <mmSolver.h>

// Lev-Mar
#include <levmar.h>  // dlevmar_bc_dir, dlevmar_bc_der


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
#include <utilities/numberUtils.h>

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
                          std::vector<double> &markerWeightList,
                          IndexPairList &errorToMarkerList,
                          MStatus &status) {
    // Count up number of errors
    // For each marker on each frame that it is valid, we add ERRORS_PER_MARKER errors.
    int i = 0;
    int j = 0;

    // For normalising the marker weight per-frame, create a mapping
    // data structure to use later.
    typedef std::map<int, double> FrameIndexDoubleMapping;
    typedef FrameIndexDoubleMapping::iterator FrameIndexDoubleMappingIt;
    FrameIndexDoubleMapping weightMaxPerFrame;
    FrameIndexDoubleMappingIt xit;

    // Get all the marker data
    int numErrors = 0;
    for (MarkerPtrListIt mit = markerList.begin(); mit != markerList.end(); ++mit) {
        MarkerPtr marker = *mit;
        for (j = 0; j < (int) frameList.length(); ++j) {
            MTime frame = frameList[j];

            bool enable = false;
            status = marker->getEnable(enable, frame);
            CHECK_MSTATUS_AND_RETURN(status, numErrors);

            double weight = 0.0;
            status = marker->getWeight(weight, frame);
            CHECK_MSTATUS_AND_RETURN(status, numErrors);

            if ((enable == true) && (weight > 0.0)) {
                // First index is into 'markerList'
                // Second index is into 'frameList'
                IndexPair markerPair(i, j);
                errorToMarkerList.push_back(markerPair);
                numErrors += ERRORS_PER_MARKER;

                validMarkerList.push_back(marker);

                // Add marker weights, into a cached list to be used
                // during solving for direct look-up.
                markerWeightList.push_back(weight);

                // Get maximum weight value of all marker weights
                // per-frame
                xit = weightMaxPerFrame.find(j);
                double weight_max = weight;
                if (xit != weightMaxPerFrame.end()) {
                    weight_max = xit->second;
                    if (weight > weight_max) {
                        weight_max = weight;
                    }
                    weightMaxPerFrame.erase(xit);
                }
                weightMaxPerFrame.insert(std::pair<int, double>(j, weight_max));

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

    // Normalise the weights per-frame, using the weight 'max'
    // computed above.
    i = 0;
    typedef IndexPairList::const_iterator IndexPairListCit;
    IndexPairListCit eit = errorToMarkerList.begin();
    for (; eit != errorToMarkerList.end(); ++eit) {
        double weight = markerWeightList[i];

        int markerIndex = eit->first;
        int frameIndex = eit->second;

        xit = weightMaxPerFrame.find(frameIndex);
        assert(xit != weightMaxPerFrame.end());
        double weight_max = xit->second;

        weight = weight / weight_max;
        markerWeightList[i] = weight;
        ++i;
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
            for (unsigned int k = 0; k < dagNode.childCount(); ++k) {
                MObject childObj = dagNode.child(k, &status);
                CHECK_MSTATUS(status);
                if (childObj.apiType() == MFn::kCamera) {
                    attrIsPartOfCamera = true;
                }
            }

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
            // This is not the same as Marker weights.
            paramWeightList.push_back(1.0);

            if (attrIsPartOfCamera) {
                camStaticAttrList.push_back(attr);
            } else {
                staticAttrList.push_back(attr);
            }
        } else {
            const char *attrName = attr->getName().asChar();
            ERR("attr is not animated or free: " << attrName);
        }
        i++;
    }
    return numUnknowns;
}


/*! Solve everything!
 *
 * This function is responsible for taking the given cameras, markers,
 * bundles and solver options, and modifying the current Maya scene,
 * saving changes in the 'dgmod' variable, and returning the results
 * in the outResult.
 *
 */
bool solve(int iterMax,
           double tau,
           double eps1,
           double eps2,
           double eps3,
           double delta,
           int autoDiffType,
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
    std::string resultStr;
    int ret = true;
    int profileCategory = MProfiler::getCategoryIndex("mmSolver");
    MProfilingScope profilingScope(profileCategory, MProfiler::kColorC_L3, "solve");

    // Change the sign of the delta
    double delta_factor = std::abs(delta);
    if (autoDiffType == 1) {
        // Central Differencing (to use forward differing the delta
        // must be a positive number)
        delta_factor *= -1;
    }

    // Indexing maps
    IndexPairList paramToAttrList;
    IndexPairList errorToMarkerList;

    // Cache out the marker positions in screen-space, so we don't
    // need to query them during solving.
    std::vector<MPoint> markerPosList;

    // Cache the marker weights, for scaling the marker errors during
    // solving.
    std::vector<double> markerWeightList;

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
            markerWeightList,
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
    assert(paramLowerBoundList.size() == m);
    assert(paramUpperBoundList.size() == m);
    assert(paramWeightList.size() == m);
    assert(m >= attrList.size());

    VRB("Number of Parameters; m=" << m);
    VRB("Number of Errors; n=" << n);
    if (m > n) {
        ERR("Solver failure; cannot solve for more attributes (\"parameters\") "
            << "than number of markers (\"errors\"). "
            << "parameters=" << m << " "
            << "errors =" << n);
        resultStr = "success=0";
        outResult.append(MString(resultStr.c_str()));
        return false;
    }
    paramList.resize((unsigned long) m, 0);
    errorList.resize((unsigned long) n, 0);

    // Error distance measurement - fur end users to read.
    std::vector<double> errorDistanceList;
    errorDistanceList.resize((unsigned long) n / ERRORS_PER_MARKER, 0);
    assert(errorToMarkerList.size() == errorDistanceList.size());

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
    VRB("Set Initial parameters...");
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
        CHECK_MSTATUS(status);
        if (status != MS::kSuccess) {
            resultStr = "success=0";
            outResult.append(MString(resultStr.c_str()));
            return false;
        }

        paramList[i] = value;
    }

     // Initial Parameters
     VRB("Initial Parameters: ");
     for (i = 0; i < m; ++i) {
         VRB("-> " << paramList[i]);
     }

    VRB("Solving...");
    VRB("Solver Type=" << solverType);
    VRB("Maximum Iterations=" << iterMax);
    VRB("Tau=" << tau);
    VRB("Epsilon1=" << eps1);
    VRB("Epsilon2=" << eps2);
    VRB("Epsilon3=" << eps3);
    VRB("Delta=" << fabs(delta_factor));
    VRB("Auto Differencing Type=" << autoDiffType);
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
    userData.markerWeightList = markerWeightList;

    // Solver Aux data
    userData.errorList = errorList;
    userData.errorDistanceList = errorDistanceList;
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
    userData.delta = delta_factor;
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
    const unsigned int optsSize = LM_OPTS_SZ;
    const unsigned int infoSize = LM_INFO_SZ;
    double opts[optsSize];
    double info[infoSize];

    // Options
    opts[0] = tau;
    opts[1] = eps1;
    opts[2] = eps2;
    opts[3] = eps3;
    opts[4] = delta_factor;

    if (solverType == SOLVER_TYPE_LEVMAR) {

        // TODO: Determine a function that will 'guess' the 'delta'
        // value for the jacobian function parameters. We could
        // experiment with distance from camera, or simply based on a
        // general look up tables. For 'angle' based attributes, use 1
        // or 5 degrees, for distance use 1cm, or 1,000cm when the
        // transform is far away from the camera.

        // Allocate a memory block for both 'work' and 'covar', so that
        // the block is close together in physical memory.
        double *work, *covar;
        work = (double *) malloc((LM_BC_DIF_WORKSZ(m, n) + m * m) * sizeof(double));
        if (!work) {
            ERR("Memory allocation request failed.");
            resultStr = "success=0";
            outResult.append(MString(resultStr.c_str()));
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
                &errorList[0],

                // Parameter Vector Dimension (input only)
                // (i.e. #unknowns)
                m,

                // Measurement Vector Dimension (input only)
                n,

                // vector of lower bounds. If NULL, no lower bounds apply
                &paramLowerBoundList[0],

                // vector of upper bounds. If NULL, no upper bounds apply (input only)
                &paramUpperBoundList[0],

                // diagonal scaling constants. NULL implies no scaling (input only)
                &paramWeightList[0],

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
        ERR("Solver type is expected to be levmar. solverType=" << solverType);
        resultStr = "success=0";
        outResult.append(MString(resultStr.c_str()));
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
        errorAvg += userData.errorDistanceList[i / ERRORS_PER_MARKER];
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
        paramBenchTimer.print("Param Time", (unsigned int) userData.iterNum);
        errorBenchTimer.print("Error Time", (unsigned int) userData.iterNum);
        funcBenchTimer.print("Func Time", (unsigned int) userData.iterNum);

        solveBenchTicks.print("Solve Ticks", 1);
        funcBenchTicks.print("Func Ticks", 1);
        jacBenchTicks.print("Jacobian Ticks", 1);
        paramBenchTicks.print("Param Ticks", (unsigned int) userData.iterNum);
        errorBenchTicks.print("Error Ticks", (unsigned int) userData.iterNum);
        funcBenchTicks.print("Func Ticks", (unsigned int) userData.iterNum);
    }

    // Add all the data into the output string from the Maya command.
    resultStr = "success=" + string::numberToString<int>((bool) ret);
    outResult.append(MString(resultStr.c_str()));

    resultStr = "reason_string=" + reasons[reasonNum];
    outResult.append(MString(resultStr.c_str()));

    resultStr = "reason_num=" + string::numberToString<int>(reasonNum);
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

    resultStr = "solve_parameter_list=";
    for (i = 0; i < m; ++i) {
        resultStr += string::numberToString<double>(paramList[i]);
        resultStr += CMD_RESULT_SPLIT_CHAR;
    }
    outResult.append(MString(resultStr.c_str()));

    resultStr = "solve_error_list=";
    for (i = 0; i < n; ++i) {
        err = userData.errorList[i];
        resultStr += string::numberToString<double>(err);
        resultStr += CMD_RESULT_SPLIT_CHAR;
    }
    outResult.append(MString(resultStr.c_str()));

    // Marker-Frame-Error relationship
    typedef std::pair<int, double> ErrorPair;
    typedef std::map<int, ErrorPair> TimeErrorMapping;
    typedef TimeErrorMapping::iterator TimeErrorMappingIt;
    TimeErrorMapping frameErrorMapping;
    TimeErrorMappingIt ait;
    for (i = 0; i < (n / ERRORS_PER_MARKER); ++i) {
        IndexPair markerPair = userData.errorToMarkerList[i];
        MarkerPtr marker = userData.markerList[markerPair.first];
        MTime frame = userData.frameList[markerPair.second];
        const char *markerName = marker->getNodeName().asChar();
        double d = userData.errorDistanceList[i];

        ait = frameErrorMapping.find(markerPair.second);
        ErrorPair pair;
        if (ait != frameErrorMapping.end()) {
            pair = ait->second;
            pair.first += 1;
            pair.second += d;
            frameErrorMapping.erase(ait);
        } else {
            pair.first = 1;
            pair.second = d;
        }
        frameErrorMapping.insert(std::pair<int, ErrorPair>(markerPair.second, pair));

        resultStr = "error_per_marker_per_frame=";
        resultStr += markerName;
        resultStr += CMD_RESULT_SPLIT_CHAR;
        resultStr += string::numberToString<double>(frame.asUnits(MTime::uiUnit()));
        resultStr += CMD_RESULT_SPLIT_CHAR;
        resultStr += string::numberToString<double>(d);
        outResult.append(MString(resultStr.c_str()));
    }

    for (TimeErrorMappingIt mit = frameErrorMapping.begin(); mit != frameErrorMapping.end(); ++mit) {
        int frameIndex = mit->first;
        MTime frame = userData.frameList[frameIndex];
        ait = frameErrorMapping.find(frameIndex);
        double num = 0;
        double d = 0;
        if (ait != frameErrorMapping.end()) {
            ErrorPair pair = ait->second;
            num = pair.first;
            d = pair.second;
        } else {
            continue;
        }

        resultStr = "error_per_frame=";
        resultStr += string::numberToString<double>(frame.asUnits(MTime::uiUnit()));
        resultStr += CMD_RESULT_SPLIT_CHAR;
        resultStr += string::numberToString<double>(d / num);
        outResult.append(MString(resultStr.c_str()));
    }
    return ret != -1;
}
