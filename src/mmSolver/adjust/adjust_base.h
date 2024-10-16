/*
 * Copyright (C) 2018, 2019, 2022 David Cattermole.
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

#ifndef MM_SOLVER_CORE_BUNDLE_ADJUST_BASE_H
#define MM_SOLVER_CORE_BUNDLE_ADJUST_BASE_H

// STL
#include <cassert>
#include <cmath>
#include <string>
#include <utility>
#include <vector>

// Maya
#include <maya/MAnimCurveChange.h>
#include <maya/MComputation.h>
#include <maya/MDGModifier.h>
#include <maya/MPoint.h>
#include <maya/MStringArray.h>

// MM Solver
#include "adjust_data.h"
#include "adjust_defines.h"
#include "adjust_results.h"
#include "adjust_solveFunc.h"
#include "mmSolver/mayahelper/maya_attr.h"
#include "mmSolver/mayahelper/maya_bundle.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_marker.h"
#include "mmSolver/utilities/debug_utils.h"

typedef std::vector<std::vector<bool> > BoolList2D;
typedef std::pair<int, int> IndexPair;
typedef std::vector<std::pair<int, int> > IndexPairList;
typedef std::pair<int, std::string> SolverTypePair;

typedef IndexPairList::iterator IndexPairListIt;
typedef IndexPairList::const_iterator IndexPairListCIt;

std::vector<SolverTypePair> getSolverTypes();

SolverTypePair getSolverTypeDefault();

double parameterBoundFromInternalToExternal(const double value,
                                            const double xmin,
                                            const double xmax,
                                            const double offset,
                                            const double scale);

double parameterBoundFromExternalToInternal(const double value,
                                            const double xmin,
                                            const double xmax,
                                            const double offset,
                                            const double scale);

void lossFunctionTrivial(const double z, double &rho0, double &rho1,
                         double &rho2);

void lossFunctionSoftL1(const double z, double &rho0, double &rho1,
                        double &rho2);

void lossFunctionCauchy(const double z, double &rho0, double &rho1,
                        double &rho2);

void applyLossFunctionToErrors(const int numberOfErrors, double *f,
                               int loss_type, double loss_scale);

bool get_initial_parameters(const int numberOfParameters,
                            std::vector<double> &paramList,
                            std::vector<std::pair<int, int> > &paramToAttrList,
                            const AttrPtrList &attrList, MTimeArray &frameList,
                            SolverResult &out_solverResult);

bool set_maya_attribute_values(
    const int numberOfParameters,
    std::vector<std::pair<int, int> > &paramToAttrList, const AttrPtrList &attrList,
    std::vector<double> &paramList, MTimeArray &frameList, MDGModifier &dgmod,
    MAnimCurveChange &curveChange);

bool compute_error_stats(const int numberOfMarkerErrors,
                         const std::vector<double> &errorDistanceList,
                         double &out_errorAvg, double &out_errorMin,
                         double &out_errorMax);

MStatus logResultsMarkerAffectsAttribute(const MarkerPtrList &markerList,
                                         const AttrPtrList &attrList,
                                         const BoolList2D &markerToAttrList,
                                         AffectsResult &out_result);

bool solve_v1(SolverOptions &solverOptions, CameraPtrList &cameraList,
              MarkerPtrList &markerList, BundlePtrList &bundleList,
              AttrPtrList &attrList, const MTimeArray &frameList,
              StiffAttrsPtrList &stiffAttrsList,
              SmoothAttrsPtrList &smoothAttrsList, MDGModifier &dgmod,
              MAnimCurveChange &curveChange, MComputation &computation,
              const MStringArray &printStatsList, const LogLevel logLevel,
              MStringArray &outResult);

bool solve_v2(SolverOptions &solverOptions, CameraPtrList &cameraList,
              MarkerPtrList &markerList, BundlePtrList &bundleList,
              AttrPtrList &attrList, const MTimeArray &frameList,
              MDGModifier &dgmod, MAnimCurveChange &curveChange,
              MComputation &computation, const MStringArray &printStatsList,
              const LogLevel logLevel, CommandResult &out_cmdResult);

#endif  // MM_SOLVER_CORE_BUNDLE_ADJUST_BASE_H
