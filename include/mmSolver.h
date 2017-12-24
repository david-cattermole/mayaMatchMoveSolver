/*
 * Uses Non-Linear Least Squares algorithm from levmar library to calculate attribute values based on 2D-to-3D error measurements through a pinhole camera.
 */


#ifndef MAYA_MM_SOLVER_H
#define MAYA_MM_SOLVER_H

// STL
#include <string>  // string
#include <vector>  // vector

// Utils
#include <utilities/debugUtils.h>

// Maya
#include <maya/MPoint.h>
#include <maya/MStringArray.h>
#include <maya/MAnimCurveChange.h>
#include <maya/MDGModifier.h>
#include <maya/MComputation.h>

//
#include <Camera.h>
#include <Marker.h>
#include <Bundle.h>
#include <Attr.h>

// The different solver types to choose from:
// Dense LM solver
#define SOLVER_TYPE_LEVMAR 0

// Sparse LM Solver
#define SOLVER_TYPE_LEVMAR_SPARSE 1

// Default Ceres options
#define SOLVER_TYPE_CERES 2

// For small problems (< 100 parameters)
#define SOLVER_TYPE_CERES_TRUST_REGION_DENSE_QR 3

// For general sparse problems (many non-zero values in the Jacobian)
#define SOLVER_TYPE_CERES_TRUST_REGION_SPARSE_NORMAL_CHOLESKY 4

// For Bundle Adjustments with ~100 cameras.
#define SOLVER_TYPE_CERES_TRUST_REGION_DENSE_SCHUR 5

// For Bundle Adjustments with ~100 cameras, with sparse support.
#define SOLVER_TYPE_CERES_TRUST_REGION_SPARSE_SCHUR 6

// For huge Bundle Adjustments with +1000 cameras.
#define SOLVER_TYPE_CERES_TRUST_REGION_ITERATIVE_SCHUR 7


// The number of errors that are measured per-marker.
#define ERRORS_PER_MARKER 3


inline
double distance_2d(MPoint a, MPoint b)
{
    double dx = (a.x - b.x);
    double dy = (a.y - b.y);
    return sqrt((dx * dx) + (dy * dy));
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
           MStringArray &outResult);

#endif // MAYA_MM_SOLVER_H
