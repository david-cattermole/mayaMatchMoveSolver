/*
 * Copyright (C) 2018, 2019 David Cattermole.
 *
 * This file is part of mmSolver.
 *
 * mmSolver is free software: you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * mmSolver is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
 * ====================================================================
 *
 * Uses Non-Linear Least Squares algorithm to
 * calculate attribute values based on 2D-to-3D error measurements
 * through a pinhole camera.
 */


#ifndef MAYA_MM_SOLVER_H
#define MAYA_MM_SOLVER_H

// STL
#include <string>
#include <vector>
#include <map>
#include <utility>

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

#include <core/bundleAdjust_data.h>
#include <core/bundleAdjust_solveFunc.h>

// The different solver types to choose from:

// Dense LM solver using 'levmar',
#define SOLVER_TYPE_LEVMAR 0
#define SOLVER_TYPE_LEVMAR_NAME "levmar"

// Dense LM solver using 'cminpack' library.
#define SOLVER_TYPE_CMINPACK_LM_DIF 1
#define SOLVER_TYPE_CMINPACK_LM_DIF_NAME "cminpack_lm"

// Dense LM solver, with custom jacobian, using 'cminpack' library.
#define SOLVER_TYPE_CMINPACK_LM_DER 2
#define SOLVER_TYPE_CMINPACK_LM_DER_NAME "cminpack_lmder"

// The default solver to use, if all solvers are available.
#define SOLVER_TYPE_DEFAULT_VALUE SOLVER_TYPE_CMINPACK_LM_DER

// Enable the Maya profiling data collection.
#define MAYA_PROFILE 1

// The number of errors that are measured per-marker.
//
// This can be a value of 2 or 3. 3 was used in the past with
// success, but tests now prove 2 to reduce error with less
// iterations, and is significantly faster overall.
#define ERRORS_PER_MARKER 2


#define CMD_RESULT_SPLIT_CHAR "#"


// Print Statistics for mmSolver command.
//
// These are the possible values:
#define PRINT_STATS_MODE_INPUTS   "inputs"
#define PRINT_STATS_MODE_AFFECTS  "affects"


typedef std::vector<std::vector<bool> > BoolList2D;
typedef std::pair<int, int> IndexPair;
typedef std::vector<std::pair<int, int> > IndexPairList;
typedef std::pair<int, std::string> SolverTypePair;


inline
double distance_2d(MPoint a, MPoint b) {
    double dx = (a.x - b.x);
    double dy = (a.y - b.y);
    return sqrt((dx * dx) + (dy * dy));
}

std::vector<SolverTypePair> getSolverTypes();

SolverTypePair getSolverTypeDefault();

int countUpNumberOfErrors(MarkerPtrList markerList,
                          MTimeArray frameList,
                          MarkerPtrList &validMarkerList,
                          std::vector<MPoint> &markerPosList,
                          std::vector<double> &markerWeightList,
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

void findErrorToUnknownRelationship(MarkerPtrList &markerList,
                                    AttrPtrList &attrList,
                                    MTimeArray &frameList,
                                    int numParameters,
                                    int numErrors,
                                    IndexPairList &paramToAttrList,
                                    IndexPairList &errorToMarkerList,
                                    BoolList2D &markerToAttrMapping,
                                    BoolList2D &errorToParamMapping,
                                    MStatus &status);


// Implements Box Constraints; Issue #64.
inline
double parameterBoundFromInternalToExternal(double value,
                                            double xmin, double xmax,
                                            double offset, double scale) {
    value = (value / scale) - offset;

    // TODO: Implement proper Box Constraints; Issue #64.
    value = std::max<double>(value, xmin);
    value = std::min<double>(value, xmax);
    return value;
}


inline
double parameterBoundsFromExternalToInternal(double value,
                                             double xmin, double xmax,
                                             double offset, double scale){
    value = std::max<double>(value, xmin);
    value = std::min<double>(value, xmax);
    
    value = (value * scale) + offset;
    return value;
}


bool set_initial_parameters(int numberOfParameters,
                            std::vector<double> &paramList,
                            std::vector<std::pair<int, int> > &paramToAttrList,
                            AttrPtrList &attrList,
                            MTimeArray &frameList,
                            MStringArray &outResult);

bool set_maya_attribute_values(int numberOfParameters,
                               std::vector<std::pair<int, int> > &paramToAttrList,
                               AttrPtrList &attrList,
                               std::vector<double> &paramList,
                               MTimeArray &frameList,
                               MDGModifier &dgmod,
                               MAnimCurveChange &curveChange);


bool compute_error_stats(int numberOfErrors,
                         SolverData &userData,
                         double &errorAvg,
                         double &errorMin,
                         double &errorMax);


void print_details(SolverResult &solverResult,
                   SolverData &userData,
                   SolverTimer &timer,
                   int numberOfParameters,
                   int numberOfErrors,
                   std::vector<double> &paramList,
                   MStringArray &outResult);


bool solve(int iterMax,
           double tau,
           double eps1,
           double eps2,
           double eps3,
           double delta,
           int autoDiffType,
           int autoParamScale,
           int solverType,
           CameraPtrList &cameraList,
           MarkerPtrList &markerList,
           BundlePtrList &bundleList,
           AttrPtrList &attrList,
           MTimeArray &frameList,
           MDGModifier &dgmod,
           MAnimCurveChange &curveChange,
           MComputation &computation,
           MString &debugFile,
           MStringArray &printStatsList,
           bool verbose,
           MStringArray &outResult);

#endif // MAYA_MM_SOLVER_H
