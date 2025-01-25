/*
 * Copyright (C) 2018, 2019, 2020, 2025 David Cattermole.
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
 * Calculates the graph relationships between Errors (Markers) and
 * Parameters (Attributes).
 */

#ifndef MM_SOLVER_CORE_BUNDLE_ADJUST_RELATIONSHIPS_H
#define MM_SOLVER_CORE_BUNDLE_ADJUST_RELATIONSHIPS_H

// STL
#include <cassert>
#include <cmath>
#include <string>
#include <unordered_set>
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
#include "adjust_solveFunc.h"
#include "mmSolver/core/matrix_bool_2d.h"
#include "mmSolver/mayahelper/maya_attr.h"
#include "mmSolver/mayahelper/maya_bundle.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_marker.h"
#include "mmSolver/utilities/debug_utils.h"

typedef std::pair<int, int> IndexPair;
typedef std::vector<std::pair<int, int> > IndexPairList;

int countUpNumberOfErrors(
    const MarkerPtrList &markerList, const StiffAttrsPtrList &stiffAttrsList,
    const SmoothAttrsPtrList &smoothAttrsList, const MTimeArray &frameList,
    MarkerPtrList &out_validMarkerList, std::vector<MPoint> &out_markerPosList,
    std::vector<double> &out_markerWeightList,
    IndexPairList &out_errorToMarkerList, int &out_numberOfMarkerErrors,
    int &out_numberOfAttrStiffnessErrors, int &out_numberOfAttrSmoothnessErrors,
    MStatus &status);

int countUpNumberOfUnknownParameters(
    const AttrPtrList &attrList, const MTimeArray &frameList,
    AttrPtrList &out_camStaticAttrList, AttrPtrList &out_camAnimAttrList,
    AttrPtrList &out_staticAttrList, AttrPtrList &out_animAttrList,
    std::vector<double> &out_paramLowerBoundList,
    std::vector<double> &out_paramUpperBoundList,
    std::vector<double> &out_paramWeightList,
    IndexPairList &out_paramToAttrList,
    mmsolver::MatrixBool2D &out_paramFrameList, MStatus &out_status);

void findMarkerToAttributeRelationship(
    const MarkerPtrList &markerList, const AttrPtrList &attrList,
    mmsolver::MatrixBool2D &out_markerToAttrMatrix, MStatus &out_status);

void getMarkerToAttributeRelationship(
    const MarkerPtrList &markerList, const AttrPtrList &attrList,
    mmsolver::MatrixBool2D &out_markerToAttrMatrix, MStatus &out_status);

void findErrorToParameterRelationship(
    const MarkerPtrList &markerList, const AttrPtrList &attrList,
    const MTimeArray &frameList, const int numParameters,
    const int numMarkerErrors, const IndexPairList &paramToAttrList,
    const IndexPairList &errorToMarkerList,
    const mmsolver::MatrixBool2D &markerToAttrMatrix,
    mmsolver::MatrixBool2D &out_errorToParamList, MStatus &out_status);

#endif  // MM_SOLVER_CORE_BUNDLE_ADJUST_RELATIONSHIPS_H
