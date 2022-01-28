/*
 * Copyright (C) 2018, 2019, 2020 David Cattermole.
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


#ifndef MAYA_MM_SOLVER_CORE_BUNDLE_ADJUST_RELATIONSHIPS_H
#define MAYA_MM_SOLVER_CORE_BUNDLE_ADJUST_RELATIONSHIPS_H

// STL
#include <string>
#include <vector>
#include <utility>
#include <cmath>
#include <cassert>

// Utils
#include "utilities/debug_utils.h"

// Maya
#include <maya/MPoint.h>
#include <maya/MStringArray.h>
#include <maya/MAnimCurveChange.h>
#include <maya/MDGModifier.h>
#include <maya/MComputation.h>

// MM Solver
#include "mayahelper/maya_camera.h"
#include "mayahelper/maya_marker.h"
#include "mayahelper/maya_bundle.h"
#include "mayahelper/maya_attr.h"

#include "adjust_defines.h"
#include "adjust_data.h"
#include "adjust_solveFunc.h"

typedef std::vector<std::vector<bool> > BoolList2D;
typedef std::pair<int, int> IndexPair;
typedef std::vector<std::pair<int, int> > IndexPairList;

int countUpNumberOfErrors(
    const MarkerPtrList &markerList,
    const StiffAttrsPtrList &stiffAttrsList,
    const SmoothAttrsPtrList &smoothAttrsList,
    const MTimeArray &frameList,
    MarkerPtrList &validMarkerList,
    std::vector<MPoint> &markerPosList,
    std::vector<double> &markerWeightList,
    IndexPairList &errorToMarkerList,
    int &numberOfMarkerErrors,
    int &numberOfAttrStiffnessErrors,
    int &numberOfAttrSmoothnessErrors,
    MStatus &status);

int countUpNumberOfUnknownParameters(
    const AttrPtrList &attrList,
    const MTimeArray &frameList,
    AttrPtrList &camStaticAttrList,
    AttrPtrList &camAnimAttrList,
    AttrPtrList &staticAttrList,
    AttrPtrList &animAttrList,
    std::vector<double> &paramLowerBoundList,
    std::vector<double> &paramUpperBoundList,
    std::vector<double> &paramWeightList,
    IndexPairList &paramToAttrList,
    BoolList2D &paramFrameList,
    MStatus &status);

void findMarkerToAttributeRelationship(
    const MarkerPtrList &markerList,
    const AttrPtrList &attrList,
    BoolList2D &markerToAttrList,
    MStatus &status);

void getMarkerToAttributeRelationship(
    const MarkerPtrList &markerList,
    const AttrPtrList &attrList,
    BoolList2D &markerToAttrList,
    MStatus &status);

void findErrorToParameterRelationship(
    const MarkerPtrList &markerList,
    const AttrPtrList &attrList,
    const MTimeArray &frameList,
    const int numParameters,
    const int numMarkerErrors,
    const IndexPairList &paramToAttrList,
    const IndexPairList &errorToMarkerList,
    const BoolList2D &markerToAttrList,
    BoolList2D &errorToParamList,
    MStatus &status);

#endif // MAYA_MM_SOLVER_CORE_BUNDLE_ADJUST_RELATIONSHIPS_H
