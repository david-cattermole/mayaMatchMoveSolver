/*
 * Uses Non-Linear Least Squares algorithm from levmar library to
 * calculate attribute values based on 2D-to-3D error measurements
 * through a pinhole camera.
 */


#ifndef MAYA_MM_SOLVER_H
#define MAYA_MM_SOLVER_H

// STL
#include <string>  // string
#include <vector>  // vector
#include <map>     // map
#include <utility> // pair

// Utils
#include <utilities/debugUtils.h>

// Maya
#include <maya/MPoint.h>
#include <maya/MStringArray.h>
#include <maya/MAnimCurveChange.h>
#include <maya/MDGModifier.h>
#include <maya/MComputation.h>

// MM Solver
#include <Camera.h>
#include <Marker.h>
#include <Bundle.h>
#include <Attr.h>

// The different solver types to choose from. Currently only 'levmar'
// is supported.
#define SOLVER_TYPE_LEVMAR 0  // Dense LM solver

// The number of errors that are measured per-marker.  
//
// This can be a value of 2 or 3. 3 was used used in the past with
// success, but tests now prove 2 to reduce error with less
// iterations, and is significantly faster overall.
#define ERRORS_PER_MARKER 2

// Use experimental 'optimised' solver function.
#define USE_EXPERIMENTAL_SOLVER 0

// Use manually created jacobian function.
#define USE_ANALYTIC_JACOBIAN 0


typedef std::vector<std::vector<bool> > BoolList2D;
typedef std::pair<int, int> IndexPair;
typedef std::vector<std::pair<int, int> > IndexPairList;

inline
double distance_2d(MPoint a, MPoint b) {
    double dx = (a.x - b.x);
    double dy = (a.y - b.y);
    return sqrt((dx * dx) + (dy * dy));
}

int countUpNumberOfErrors(MarkerPtrList markerList,
                          MTimeArray frameList,
                          MarkerPtrList &validMarkerList,
                          std::vector<MPoint> &markerPosList,
                          IndexPairList &errorToMarkerList,
                          MStatus &status);

int countUpNumberOfUnknownParameters(AttrPtrList attrList,
                                     MTimeArray frameList,
                                     AttrPtrList &camStaticAttrList,
                                     AttrPtrList &camAnimAttrList,
                                     AttrPtrList &staticAttrList,
                                     AttrPtrList &animAttrList,
                                     IndexPairList &paramToAttrList,
                                     MStatus &status);

void findErrorToUnknownRelationship(MarkerPtrList markerList,
                                    AttrPtrList attrList,
                                    MTimeArray frameList,
                                    int numParameters,
                                    int numErrors,
                                    IndexPairList paramToAttrList,
                                    IndexPairList errorToMarkerList,
                                    BoolList2D &markerToAttrMapping,
                                    BoolList2D &errorToParamMapping,
                                    MStatus &status);

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
