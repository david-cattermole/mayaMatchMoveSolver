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


// The user data given to levmar.
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



#endif // MAYA_MM_SOLVER_CERES_H
