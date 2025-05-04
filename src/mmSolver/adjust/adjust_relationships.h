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
#include "mmSolver/core/frame.h"
#include "mmSolver/core/frame_list.h"
#include "mmSolver/core/matrix_bool_2d.h"
#include "mmSolver/core/matrix_bool_3d.h"
#include "mmSolver/core/types.h"
#include "mmSolver/mayahelper/maya_attr.h"
#include "mmSolver/mayahelper/maya_attr_list.h"
#include "mmSolver/mayahelper/maya_bundle.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_marker.h"
#include "mmSolver/mayahelper/maya_marker_list.h"
#include "mmSolver/utilities/debug_utils.h"

namespace mmsolver {

typedef std::pair<Index32, Index32> IndexPair;
typedef std::vector<IndexPair> IndexPairList;

Count32 countUpNumberOfErrors(
    const MarkerList &markerList, const StiffAttrsPtrList &stiffAttrsList,
    const SmoothAttrsPtrList &smoothAttrsList, const FrameList &frameList,
    // Outputs
    std::vector<MPoint> &out_markerPosList,
    std::vector<double> &out_markerWeightList,
    IndexPairList &out_errorToMarkerList, Count32 &out_numberOfMarkerErrors,
    Count32 &out_numberOfAttrStiffnessErrors,
    Count32 &out_numberOfAttrSmoothnessErrors, MStatus &status);

Count32 countUpNumberOfUnknownParameters(
    const AttrList &attrList, const FrameList &frameList,
    // Outputs
    AttrList &out_camStaticAttrList, AttrList &out_camAnimAttrList,
    AttrList &out_staticAttrList, AttrList &out_animAttrList,
    std::vector<double> &out_paramLowerBoundList,
    std::vector<double> &out_paramUpperBoundList,
    std::vector<double> &out_paramWeightList,
    IndexPairList &out_paramToAttrList,
    mmsolver::MatrixBool2D &out_paramToFrameMatrix, MStatus &out_status);

Count32 countEnabledMarkersForMarkerToAttrToFrameRelationship(
    const AttrIndex attrIndex, const FrameIndex frameIndex,
    const mmsolver::MatrixBool3D &markerToAttrToFrameMatrix);

Count32 countEnabledAttrsForMarkerToAttrToFrameRelationship(
    const MarkerIndex markerIndex, const FrameIndex frameIndex,
    const mmsolver::MatrixBool3D &markerToAttrToFrameMatrix);

Count32 countEnabledFramesForMarkerToAttrToFrameRelationship(
    const MarkerIndex markerIndex, const AttrIndex attrIndex,
    const mmsolver::MatrixBool3D &markerToAttrToFrameMatrix);

void analyseDependencyGraphRelationships(
    const MarkerList &markerList, const AttrList &attrList,
    const FrameList &frameList,
    // Outputs
    mmsolver::MatrixBool3D &out_markerToAttrToFrameMatrix, MStatus &out_status);

void analyseObjectRelationships(
    const MarkerList &markerList, const AttrList &attrList,
    const FrameList &frameList,
    // Outputs
    mmsolver::MatrixBool3D &out_markerToAttrToFrameMatrix, MStatus &out_status);

void readStoredRelationships(
    const MarkerList &markerList, const AttrList &attrList,
    const FrameList &frameList,
    // Outputs
    Count32 &out_relationshipAttrsExistCount,
    mmsolver::MatrixBool3D &out_markerToAttrToFrameMatrix, MStatus &out_status);

void mapErrorsToParameters(
    const MarkerList &markerList, const AttrList &attrList,
    const FrameList &frameList, const Count32 numParameters,
    const Count32 numMarkerErrors, const IndexPairList &paramToAttrList,
    const IndexPairList &errorToMarkerList,
    const mmsolver::MatrixBool3D &markerToAttrToFrameMatrix,
    // Outputs
    mmsolver::MatrixBool2D &out_errorToParamMatrix, MStatus &out_status);

void calculateMarkerAndParameterCount(
    const MarkerList &markerList, const AttrList &attrList,
    const FrameList &frameList, const Count32 numParameters,
    const Count32 numMarkerErrors, const IndexPairList &paramToAttrList,
    const IndexPairList &errorToMarkerList,
    const mmsolver::MatrixBool3D &markerToAttrToFrameMatrix,
    const FrameSolveMode frameSolveMode,
    // Outputs
    FrameList &out_validFrameList, MStatus &out_status);

void generateValidMarkerAttrFrameLists(
    const MarkerList &markerList, const AttrList &attrList,
    const FrameList &frameList,
    const mmsolver::MatrixBool3D &markerToAttrToFrameMatrix,

    // Outputs
    MarkerList &out_validMarkerList, AttrList &out_validAttrList,
    FrameList &out_validFrameList, MStatus &out_status);

}  // namespace mmsolver

#endif  // MM_SOLVER_CORE_BUNDLE_ADJUST_RELATIONSHIPS_H
