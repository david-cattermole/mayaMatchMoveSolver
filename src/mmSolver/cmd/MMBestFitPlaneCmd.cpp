/*
 * Copyright (C) 2024 David Cattermole.
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
 * 'mmBestFitPlane' Maya command.
 *
 * Example usage (in Python):
 *
 * import maya.cmds
 * maya.cmds.loadPlugin('mmSolver', quiet=True)
 *
 * nodes = maya.cmds.ls(sl=True, long=True) or []
 *
 * points = [maya.cmds.xform(node, query=True, worldSpace=True, translation=True)
             for node in nodes]
 * print('points: {}'.format(points))
 *
 * points_components = []
 * for point in points:
 *     points_components.append(point[0])
 *     points_components.append(point[1])
 *     points_components.append(point[2])
 * print('points_components: {}'.format(points_components))
 *
 * result = maya.cmds.mmBestFitPlane(pointComponent=points_components)
 * if result is not None:
 *     assert len(result) == 7
 *     plane_position = (result[0], result[1], result[2])
 *     plane_normal = (result[3], result[4], result[5])
 *     plane_fit_error = result[6]
 *     print('plane_position: {}'.format(plane_position))
 *     print('plane_normal : {}'.format(plane_normal ))
 *     print('plane_fit_error : {}'.format(plane_fit_error ))
 * else:
 *     print('The plane could not be fit to those input points.')
 *
 */

#include "MMBestFitPlaneCmd.h"

// STL
#include <cassert>

// Maya
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MDoubleArray.h>
#include <maya/MPoint.h>
#include <maya/MPointArray.h>
#include <maya/MSyntax.h>
#include <maya/MVector.h>

// MM Solver
#include "mmSolver/utilities/debug_utils.h"

// MM Scene Graph
#include "mmscenegraph/mmscenegraph.h"

// Command arguments
#define POINT_COMPONENTS_SHORT_FLAG "-pc"
#define POINT_COMPONENTS_LONG_FLAG "-pointComponent"

namespace mmsg = mmscenegraph;

namespace mmsolver {

const size_t NUMBER_OF_POINT_COMPONENTS = 3;
const size_t MINIMUM_POINT_COUNT = 3;
const size_t MINIMUM_COMPONENT_COUNT =
    NUMBER_OF_POINT_COMPONENTS * MINIMUM_POINT_COUNT;

MMBestFitPlaneCmd::~MMBestFitPlaneCmd() {}

void *MMBestFitPlaneCmd::creator() { return new MMBestFitPlaneCmd(); }

MString MMBestFitPlaneCmd::cmdName() { return MString("mmBestFitPlane"); }

bool MMBestFitPlaneCmd::hasSyntax() const { return true; }

bool MMBestFitPlaneCmd::isUndoable() const { return false; }

MSyntax MMBestFitPlaneCmd::newSyntax() {
    MSyntax syntax;
    syntax.enableQuery(false);
    syntax.enableEdit(false);

    // Add point flag that takes 3 doubles (x, y, z).
    syntax.addFlag(POINT_COMPONENTS_SHORT_FLAG, POINT_COMPONENTS_LONG_FLAG,
                   MSyntax::kDouble);

    // Allow multiple uses of the point flag
    syntax.makeFlagMultiUse(POINT_COMPONENTS_SHORT_FLAG);

    return syntax;
}

MStatus MMBestFitPlaneCmd::parseArgs(const MArgList &args) {
    MStatus status = MStatus::kSuccess;
    const bool verbose = true;

    MArgDatabase argData(syntax(), args, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    // Get number of 'point' flags used.
    auto numPointComponents = static_cast<size_t>(
        argData.numberOfFlagUses(POINT_COMPONENTS_SHORT_FLAG));
    MMSOLVER_MAYA_VRB(
        "mmBestFitPlane: numPointComponents=" << numPointComponents);
    if (numPointComponents < MINIMUM_COMPONENT_COUNT) {
        MMSOLVER_MAYA_ERR(
            "mmBestFitPlane: "
            "At least 3 points are required using the "
            << POINT_COMPONENTS_SHORT_FLAG << "/" << POINT_COMPONENTS_LONG_FLAG
            << " flag.");
        return MS::kFailure;
    }

    const auto numPoints = numPointComponents / NUMBER_OF_POINT_COMPONENTS;
    MMSOLVER_MAYA_VRB("mmBestFitPlane: numPoints=" << numPoints);

    // Parse all the points
    m_points_xyz.clear();
    m_points_xyz.reserve(numPointComponents);
    for (auto i = 0; i < numPointComponents; i++) {
        MArgList pointArgs;
        status = argData.getFlagArgumentList(POINT_COMPONENTS_SHORT_FLAG, i,
                                             pointArgs);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        mmsg::Real value = pointArgs.asDouble(0, &status);
        MMSOLVER_MAYA_VRB("mmBestFitPlane: i=" << i << " value=" << value);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        m_points_xyz.push_back(value);
    }

    return MStatus::kSuccess;
}

MStatus MMBestFitPlaneCmd::doIt(const MArgList &args) {
    MStatus status = MMBestFitPlaneCmd::parseArgs(args);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    // Output values.
    mmsg::Real plane_position_x = 0.0;
    mmsg::Real plane_position_y = 0.0;
    mmsg::Real plane_position_z = 0.0;
    mmsg::Real plane_normal_x = 0.0;
    mmsg::Real plane_normal_y = 1.0;
    mmsg::Real plane_normal_z = 0.0;
    mmsg::Real rms_error = 0.0;

    // Compute the best fit plane.
    rust::Slice<const mmsg::Real> points_xyz_slice{m_points_xyz.data(),
                                                   m_points_xyz.size()};
    const bool ok = mmsg::fit_plane_to_points(
        points_xyz_slice, plane_position_x, plane_position_y, plane_position_z,
        plane_normal_x, plane_normal_y, plane_normal_z, rms_error);
    if (!ok) {
        MMSOLVER_MAYA_ERR("mmBestFitPlane: Failed to compute best fit plane.");
        return MStatus::kFailure;
    }

    // Return results as array of double floats:
    // [pos_x, pos_y, pos_z, norm_x, norm_y, norm_z, rms_error]
    MDoubleArray result;
    result.append(plane_position_x);
    result.append(plane_position_y);
    result.append(plane_position_z);
    result.append(plane_normal_x);
    result.append(plane_normal_y);
    result.append(plane_normal_z);
    result.append(rms_error);

    MPxCommand::setResult(result);
    return status;
}

}  // namespace mmsolver
