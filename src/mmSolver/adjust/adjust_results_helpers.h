/*
 * Copyright (C) 2022 David Cattermole.
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
 * Common functions used to set result data structures.
 */

#ifndef MM_SOLVER_CORE_BUNDLE_ADJUST_RESULTS_HELPERS_H
#define MM_SOLVER_CORE_BUNDLE_ADJUST_RESULTS_HELPERS_H

// STL
#include <unordered_map>

// Maya
#include <maya/MDGModifier.h>
#include <maya/MFnAttribute.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnNumericData.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>

inline MStatus find_plug(const char *attr_name, MFnDependencyNode &dgNodeFn,
                         MPlug &outPlug) {
    const bool wantNetworkedPlug = true;
    outPlug = dgNodeFn.findPlug(attr_name, wantNetworkedPlug);
    return MS::kSuccess;
}

inline MStatus create_numeric_attr(const char *attr_name, MObject &node,
                                   MDGModifier &dgmod,
                                   MFnNumericAttribute &numeric_attr,
                                   const MFnNumericData::Type numeric_type) {
    MObject attr = numeric_attr.create(attr_name, attr_name, numeric_type);
    MStatus status = dgmod.addAttribute(node, attr);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    return status;
}

inline MStatus create_typed_attr(const char *attr_name, MObject &node,
                                 MDGModifier &dgmod,
                                 MFnTypedAttribute &typed_attr,
                                 const MFnData::Type &data_type) {
    MObject attr = typed_attr.create(attr_name, attr_name, data_type);
    MStatus status = dgmod.addAttribute(node, attr);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    return status;
}

MStatus create_deviation_attrs_on_node(
    MObject &node, const std::unordered_multimap<double, double> &map,
    const char *deviation_attr_name, const char *deviation_avg_attr_name,
    const char *deviation_max_attr_name,
    const char *deviation_max_frame_attr_name, MDGModifier &dgmod,
    MAnimCurveChange &curveChange);

#endif  // MM_SOLVER_CORE_BUNDLE_ADJUST_RESULTS_HELPERS_H
