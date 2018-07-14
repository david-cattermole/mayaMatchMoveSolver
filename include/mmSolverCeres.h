/*
 * Uses Non-Linear Least Squares algorithm from levmar library to calculate attribute values based on 2D-to-3D error measurements through a pinhole camera.
 */


#ifndef MAYA_MM_SOLVER_CERES_H
#define MAYA_MM_SOLVER_CERES_H

// STL
#include <string>  // string
#include <vector>  // vector

// Utils
#include <utilities/debugUtils.h>

// Maya
#include <maya/MPoint.h>
#include <maya/MTimeArray.h>
#include <maya/MStringArray.h>
#include <maya/MAnimCurveChange.h>
#include <maya/MDGModifier.h>
#include <maya/MComputation.h>

// Internal Objects
#include <Camera.h>
#include <Marker.h>
#include <Bundle.h>
#include <Attr.h>


//
#include <mmSolver.h>


#include <ceres/ceres.h>


// The user data given to ceres.
struct CeresSolverData {
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
    int numParameters;
    int numErrors;
    std::vector<double> errorList;
    int iterNum;
    int jacIterNum;
    int iterMax;
    int solverType;
    bool isJacobianCalculation;
    double imageWidth;

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



class ReprojectionErrorFunctor {
public:
    ReprojectionErrorFunctor(CeresSolverData &data);

    bool operator()(double const* const* parameters,
                    double* residuals) const;

// Factory to hide the construction of the CostFunction object from
// the client code.
    static ceres::CostFunction* create(CeresSolverData &data) {
        ceres::DynamicNumericDiffCostFunction<ReprojectionErrorFunctor, ceres::CENTRAL>* cost_function =
                new ceres::DynamicNumericDiffCostFunction<ReprojectionErrorFunctor, ceres::CENTRAL>(new ReprojectionErrorFunctor(data));
        return cost_function;
    }

private:
    CeresSolverData m_solverData;
};

#if 0  // Turn off unfinished impementation of Ceres MarkerBundleCamera solver.
// Defines a triplet of Marker, Bundle and Camera.
struct MarkerBundleCameraData {
    // Solver Objects.
    CameraPtr camera;
    MPoint marker_pos;
    MarkerPtr marker;
    BundlePtr bundle;
    AttrPtrList attrList;
    MTime frame;      // Time to solve
    MTimeArray frameList;  // Times to solve

    // Relational mapping indexes.
    std::vector<std::pair<int, int> > paramToAttrList;
    // std::vector<std::pair<int, int> > errorToMarkerList;

    // Internal Solver Data.
    int numParameters;
    int numErrors;
//    std::vector<double> errorList;
//    int iterNum;
//    int jacIterNum;
//    int iterMax;
//    int solverType;
//    bool isJacobianCalculation;

    // Storing changes for undo/redo.
    MDGModifier *dgmod;
    MAnimCurveChange *curveChange;

//    // Allow user to cancel the solve.
//    MComputation *computation;

    // Verbosity.
    bool verbose;
};


class MarkerBundleCameraCostFunctor {
public:
    explicit MarkerBundleCameraCostFunctor(MarkerBundleCameraData &data);

    bool operator()(double const* const* parameters,
                    double* residuals) const;

// Factory to hide the construction of the CostFunction object from
// the client code.
    static ceres::DynamicNumericDiffCostFunction<MarkerBundleCameraCostFunctor, ceres::CENTRAL>* create(MarkerBundleCameraData &data) {
        ceres::DynamicNumericDiffCostFunction<MarkerBundleCameraCostFunctor, ceres::CENTRAL>* cost_function =
                new ceres::DynamicNumericDiffCostFunction<MarkerBundleCameraCostFunctor, ceres::CENTRAL>(new MarkerBundleCameraCostFunctor(data));
        return cost_function;
    }

private:
    MarkerBundleCameraData m_data;
};
#endif


#endif // MAYA_MM_SOLVER_CERES_H
