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

namespace mmsolver {

typedef std::pair<int, int> IndexPair;
typedef std::vector<std::pair<int, int> > IndexPairList;

uint32_t countUpNumberOfErrors(
    const MarkerPtrList &markerList, const StiffAttrsPtrList &stiffAttrsList,
    const SmoothAttrsPtrList &smoothAttrsList, const MTimeArray &frameList,
    MarkerPtrList &out_validMarkerList, std::vector<MPoint> &out_markerPosList,
    std::vector<double> &out_markerWeightList,
    IndexPairList &out_errorToMarkerList, uint32_t &out_numberOfMarkerErrors,
    uint32_t &out_numberOfAttrStiffnessErrors,
    uint32_t &out_numberOfAttrSmoothnessErrors, MStatus &status);

uint32_t countUpNumberOfUnknownParameters(
    const AttrPtrList &attrList, const MTimeArray &frameList,
    AttrPtrList &out_camStaticAttrList, AttrPtrList &out_camAnimAttrList,
    AttrPtrList &out_staticAttrList, AttrPtrList &out_animAttrList,
    std::vector<double> &out_paramLowerBoundList,
    std::vector<double> &out_paramUpperBoundList,
    std::vector<double> &out_paramWeightList,
    IndexPairList &out_paramToAttrList,
    mmsolver::MatrixBool2D &out_paramFrameMatrix, MStatus &out_status);

void findMarkerToAttributeRelationship(
    const MarkerPtrList &markerList, const AttrPtrList &attrList,
    mmsolver::MatrixBool2D &out_markerToAttrMatrix, MStatus &out_status);

void getMarkerToAttributeRelationship(
    const MarkerPtrList &markerList, const AttrPtrList &attrList,
    mmsolver::MatrixBool2D &out_markerToAttrMatrix, MStatus &out_status);

void findErrorToParameterRelationship(
    const MarkerPtrList &markerList, const AttrPtrList &attrList,
    const MTimeArray &frameList, const uint32_t numParameters,
    const uint32_t numMarkerErrors, const IndexPairList &paramToAttrList,
    const IndexPairList &errorToMarkerList,
    const mmsolver::MatrixBool2D &markerToAttrMatrix,
    mmsolver::MatrixBool2D &out_errorToParamMatrix, MStatus &out_status);

void calculateMarkerAndParameterCount(
    const MarkerPtrList &markerList, const AttrPtrList &attrList,
    const MTimeArray &frameList, const uint32_t numParameters,
    const uint32_t numMarkerErrors, const IndexPairList &paramToAttrList,
    const IndexPairList &errorToMarkerList,
    const mmsolver::MatrixBool2D &markerToAttrMatrix,
    const FrameSolveMode frameSolveMode,
    std::unordered_set<int32_t> &out_valid_frames,
    std::unordered_set<int32_t> &out_invalid_frames, MStatus &out_status);

}  // namespace mmsolver

#endif  // MM_SOLVER_CORE_BUNDLE_ADJUST_RELATIONSHIPS_H
