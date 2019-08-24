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


#ifndef MAYA_MM_SOLVER_CORE_BUNDLE_ADJUST_BASE_H
#define MAYA_MM_SOLVER_CORE_BUNDLE_ADJUST_BASE_H

// STL
#include <string>
#include <vector>
#include <map>
#include <utility>
#include <cmath>
#include <cassert>

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
#define SOLVER_TYPE_CMINPACK_LMDIF 1
#define SOLVER_TYPE_CMINPACK_LM_DIF_NAME "cminpack_lmdif"

// Dense LM solver, with custom jacobian, using 'cminpack' library.
#define SOLVER_TYPE_CMINPACK_LMDER 2
#define SOLVER_TYPE_CMINPACK_LM_DER_NAME "cminpack_lmder"

// The default solver to use, if all solvers are available.
#define SOLVER_TYPE_DEFAULT_VALUE SOLVER_TYPE_CMINPACK_LMDER


// Enable the Maya profiling data collection.
#define MAYA_PROFILE 1

// The number of errors that are measured per-marker.
// There are two measurements per-marker, X and Y.
//
// Three measurements were used in the past with
// success, but tests now prove 2 to reduce error with less
// iterations, and is significantly faster overall.
//
// Do not change this definition.
#define ERRORS_PER_MARKER (2)

// Text character used to split up a single result string.
#define CMD_RESULT_SPLIT_CHAR "#"


// Print Statistics for mmSolver command.
//
// These are the possible values:
#define PRINT_STATS_MODE_INPUTS   "inputs"
#define PRINT_STATS_MODE_AFFECTS  "affects"
#define PRINT_STATS_MODE_DEVIATION   "deviation"


// Robust Loss Function Types.
//
#define ROBUST_LOSS_TYPE_TRIVIAL  (0)
#define ROBUST_LOSS_TYPE_SOFT_L_ONE  (1)
#define ROBUST_LOSS_TYPE_CAUCHY  (2)


// CMinpack-specific values for recognising forward or central differencing.
//
#define AUTO_DIFF_TYPE_FORWARD (0)
#define AUTO_DIFF_TYPE_CENTRAL (1)


// CMinpack lmdif Solver default flag values
//
#define CMINPACK_LMDIF_ITERATIONS_DEFAULT_VALUE  (100)
#define CMINPACK_LMDIF_TAU_DEFAULT_VALUE  (1.0)
#define CMINPACK_LMDIF_EPSILON1_DEFAULT_VALUE  (1E-15) // ftol
#define CMINPACK_LMDIF_EPSILON2_DEFAULT_VALUE  (1E-15) // xtol
#define CMINPACK_LMDIF_EPSILON3_DEFAULT_VALUE  (1E-15) // gtol
#define CMINPACK_LMDIF_DELTA_DEFAULT_VALUE  (1E-04)
// cminpack lmdif only supports forward '0=forward' auto-diff'ing.
#define CMINPACK_LMDIF_AUTO_DIFF_TYPE_DEFAULT_VALUE  (AUTO_DIFF_TYPE_FORWARD)
#define CMINPACK_LMDIF_AUTO_PARAM_SCALE_DEFAULT_VALUE  (1)  // default is 'on=1 (mode=1)'
#define CMINPACK_LMDIF_ROBUST_LOSS_TYPE_DEFAULT_VALUE  (ROBUST_LOSS_TYPE_TRIVIAL)
#define CMINPACK_LMDIF_ROBUST_LOSS_SCALE_DEFAULT_VALUE 1.0
#define CMINPACK_LMDIF_SUPPORT_AUTO_DIFF_FORWARD_VALUE true
#define CMINPACK_LMDIF_SUPPORT_AUTO_DIFF_CENTRAL_VALUE false
#define CMINPACK_LMDIF_SUPPORT_PARAMETER_BOUNDS_VALUE true
#define CMINPACK_LMDIF_SUPPORT_ROBUST_LOSS_VALUE false

// CMinpack lmder Solver default flag values
//
#define CMINPACK_LMDER_ITERATIONS_DEFAULT_VALUE  (100)
#define CMINPACK_LMDER_TAU_DEFAULT_VALUE  (1.0)
#define CMINPACK_LMDER_EPSILON1_DEFAULT_VALUE  (1E-15) // ftol
#define CMINPACK_LMDER_EPSILON2_DEFAULT_VALUE  (1E-15) // xtol
#define CMINPACK_LMDER_EPSILON3_DEFAULT_VALUE  (1E-15) // gtol
#define CMINPACK_LMDER_DELTA_DEFAULT_VALUE  (1E-04)
// cminpack lmder supports both forward '0=forward' and 'central' auto-diff'ing.
#define CMINPACK_LMDER_AUTO_DIFF_TYPE_DEFAULT_VALUE  (AUTO_DIFF_TYPE_FORWARD)
#define CMINPACK_LMDER_AUTO_PARAM_SCALE_DEFAULT_VALUE  (1)  // default is 'on=1 (mode=1)'
#define CMINPACK_LMDER_ROBUST_LOSS_TYPE_DEFAULT_VALUE  (ROBUST_LOSS_TYPE_TRIVIAL)
#define CMINPACK_LMDER_ROBUST_LOSS_SCALE_DEFAULT_VALUE 1.0
#define CMINPACK_LMDER_SUPPORT_AUTO_DIFF_FORWARD_VALUE true
#define CMINPACK_LMDER_SUPPORT_AUTO_DIFF_CENTRAL_VALUE true
#define CMINPACK_LMDER_SUPPORT_PARAMETER_BOUNDS_VALUE true
#define CMINPACK_LMDER_SUPPORT_ROBUST_LOSS_VALUE  false

// Levmar Solver default flag values
//
#define LEVMAR_ITERATIONS_DEFAULT_VALUE  (100)
#define LEVMAR_TAU_DEFAULT_VALUE  (1.0)
#define LEVMAR_EPSILON1_DEFAULT_VALUE  (1E-6)
#define LEVMAR_EPSILON2_DEFAULT_VALUE  (1E-6)
#define LEVMAR_EPSILON3_DEFAULT_VALUE  (1E-6)
#define LEVMAR_DELTA_DEFAULT_VALUE  (1E-04)
#define LEVMAR_AUTO_DIFF_TYPE_DEFAULT_VALUE  (AUTO_DIFF_TYPE_FORWARD)
// LevMar does not have auto-parameter scaling.
#define LEVMAR_AUTO_PARAM_SCALE_DEFAULT_VALUE  (0)
#define LEVMAR_ROBUST_LOSS_TYPE_DEFAULT_VALUE  (ROBUST_LOSS_TYPE_TRIVIAL)
#define LEVMAR_ROBUST_LOSS_SCALE_DEFAULT_VALUE 1.0
#define LEVMAR_SUPPORT_AUTO_DIFF_FORWARD_VALUE true
#define LEVMAR_SUPPORT_AUTO_DIFF_CENTRAL_VALUE true
#define LEVMAR_SUPPORT_PARAMETER_BOUNDS_VALUE true
#define LEVMAR_SUPPORT_ROBUST_LOSS_VALUE false


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


double parameterBoundFromInternalToExternal(double value,
                                            double xmin, double xmax,
                                            double offset, double scale);


double parameterBoundFromExternalToInternal(double value,
                                            double xmin, double xmax,
                                            double offset, double scale);


inline
void lossFunctionTrivial(double z,
                         double &rho0,
                         double &rho1,
                         double &rho2) {
    // Trivial - 'no op' loss function.
    rho0 = z;
    rho1 = 1.0;
    rho2 = 0.0;
};


inline
void lossFunctionSoftL1(double z,
                        double &rho0,
                        double &rho1,
                        double &rho2) {
    // Soft L1
    double t = 1.0 + z;
    rho0 = 2.0 * (std::pow(t, 0.5 - 1.0));
    rho1 = std::pow(t, -0.5);
    rho2 = -0.5 * std::pow(t, -1.5);
};


inline
void lossFunctionCauchy(double z,
                        double &rho0,
                        double &rho1,
                        double &rho2) {
    // Cauchy
    // TODO: replace with 'std::log1p(z)', with C++11.
    rho0 = std::log(1.0 + z);
    double t = 1.0 + z;
    rho1 = 1.0 / t;
    rho2 = -1.0 / std::pow(t, 2.0);
};


inline
void applyLossFunctionToErrors(int numberOfErrors,
                               double *f,
                               int loss_type,
                               double loss_scale) {
    for (int i = 0; i < numberOfErrors; ++i) {
        // The loss function
        double z = std::pow(f[i] / loss_scale, 2);
        double rho0 = z;
        double rho1 = 1.0;
        double rho2 = 0.0;
        if (loss_type == ROBUST_LOSS_TYPE_TRIVIAL) {
            lossFunctionTrivial(z, rho0, rho1, rho2);
        } else if (loss_type == ROBUST_LOSS_TYPE_SOFT_L_ONE) {
            lossFunctionSoftL1(z, rho0, rho1, rho2);
        } else if (loss_type == ROBUST_LOSS_TYPE_CAUCHY) {
            lossFunctionCauchy(z, rho0, rho1, rho2);
        } else {
            DBG("Invalid Robust Loss Type given; value=" << loss_type);
        }
        rho0 *= std::pow(loss_scale, 2.0);
        rho2 /= std::pow(loss_scale, 2.0);

        double J_scale = rho1 + 2.0 * rho2 * std::pow(f[i], 2.0);
        const double eps = std::numeric_limits<double>::epsilon();
        if (J_scale < eps) {
            J_scale = eps;
        }
        J_scale = std::pow(J_scale, 0.5);
        f[i] *= rho1 / J_scale;
    }
    return;
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
                   bool verbose,
                   std::vector<double> &paramList,
                   MStringArray &outResult);


bool solve(SolverOptions &solverOptions,
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

#endif // MAYA_MM_SOLVER_CORE_BUNDLE_ADJUST_BASE_H
