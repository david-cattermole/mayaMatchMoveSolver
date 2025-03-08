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
 * points = [maya.cmds.xform(node, query=True, worldSpace=True,
 * translation=True) for node in nodes] print('points: {}'.format(points))
 *
 * points_components = []
 * for point in points:
 *     points_components.append(point[0])
 *     points_components.append(point[1])
 *     points_components.append(point[2])
 * print('points_components: {}'.format(points_components))
 *
 * OUTPUT_VALUES_AS_POSITION_AND_DIRECTION = "position_and_direction"
 * OUTPUT_VALUES_AS_POSITION_AND_DIRECTION = "position_direction_and_scale"
 * OUTPUT_VALUES_AS_MATRIX_4X4 = "matrix_4x4"
 *
 * result = maya.cmds.mmBestFitPlane(
 *     pointComponent=points_components,
 *     outputValuesAs=OUTPUT_VALUES_AS_MATRIX_4X4,
 *     outputRmsError=True)
 * print('result: {}'.format(result))
 * if result is None:
 *     print('The plane could not be fit to those input points.')
 * elif len(result) in [7, 8]:
 *     plane_position = (result[0], result[1], result[2])
 *     plane_normal = (result[3], result[4], result[5])
 *     plane_fit_error = result[6]
 *     print('plane_position: {}'.format(plane_position))
 *     print('plane_normal : {}'.format(plane_normal))
 *     print('plane_fit_error : {}'.format(plane_fit_error))
 * elif len(result) in [16, 17]:
 *     plane_matrix = (
 *         result[0], result[1], result[2],  result[3],
 *         result[4], result[5], result[6],  result[7],
 *         result[8], result[9], result[10],  result[11],
 *         result[12], result[13], result[14],  result[15],
 *     )
 *     plane_fit_error = result[16]
 *     print('plane_matrix: {}'.format(plane_matrix))
 *     print('plane_fit_error : {}'.format(plane_fit_error))
 *
 *     # Set value of 'pPlane1' node transform to output.
 *     maya.cmds.xform('pPlane1', worldSpace=True, matrix=plane_matrix)
 *
 *
 */

#include "MMBestFitPlaneCmd.h"

// STL
#include <cstring>

// Maya
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MDoubleArray.h>
#include <maya/MPoint.h>
#include <maya/MPointArray.h>
#include <maya/MSyntax.h>
#include <maya/MVector.h>

// MM Solver Libs
#include <mmcore/mmdata.h>
#include <mmcore/mmmath.h>

// MM Scene Graph
#include "mmscenegraph/mmscenegraph.h"

// MM Solver
#include "mmSolver/utilities/debug_utils.h"

// Command arguments
#define POINT_COMPONENTS_SHORT_FLAG "-pc"
#define POINT_COMPONENTS_LONG_FLAG "-pointComponent"

#define WITH_SCALE_SHORT_FLAG "-wsc"
#define WITH_SCALE_LONG_FLAG "-withScale"

#define OUTPUT_VALUES_AS_SHORT_FLAG "-ova"
#define OUTPUT_VALUES_AS_LONG_FLAG "-outputValuesAs"

#define OUTPUT_RMS_ERROR_SHORT_FLAG "-ore"
#define OUTPUT_RMS_ERROR_LONG_FLAG "-outputRmsError"

// Value strings.
#define OUTPUT_VALUES_AS_POSITION_AND_DIRECTION "position_and_direction"
#define OUTPUT_VALUES_AS_POSITION_DIRECTION_AND_SCALE \
    "position_direction_and_scale"
#define OUTPUT_VALUES_AS_MATRIX_4X4 "matrix_4x4"

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

    syntax.addFlag(POINT_COMPONENTS_SHORT_FLAG, POINT_COMPONENTS_LONG_FLAG,
                   MSyntax::kDouble);
    syntax.makeFlagMultiUse(POINT_COMPONENTS_SHORT_FLAG);

    syntax.addFlag(WITH_SCALE_SHORT_FLAG, WITH_SCALE_LONG_FLAG,
                   MSyntax::kBoolean);

    syntax.addFlag(OUTPUT_VALUES_AS_SHORT_FLAG, OUTPUT_VALUES_AS_LONG_FLAG,
                   MSyntax::kString);

    syntax.addFlag(OUTPUT_RMS_ERROR_SHORT_FLAG, OUTPUT_RMS_ERROR_LONG_FLAG,
                   MSyntax::kBoolean);

    return syntax;
}

MStatus MMBestFitPlaneCmd::parseArgs(const MArgList &args) {
    MStatus status = MStatus::kSuccess;
    const bool verbose = false;

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

    m_with_scale = false;
    const bool with_scale_flag =
        argData.isFlagSet(WITH_SCALE_SHORT_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    MMSOLVER_MAYA_VRB("mmBestFitPlane: with_scale_flag=" << with_scale_flag);
    if (with_scale_flag) {
        status =
            argData.getFlagArgument(WITH_SCALE_SHORT_FLAG, 0, m_with_scale);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        MMSOLVER_MAYA_VRB("mmBestFitPlane: m_with_scale=" << m_with_scale);
    }

    m_output_values_as = OutputValuesAs::kPositionAndDirection;
    const bool output_as_values_flag =
        argData.isFlagSet(OUTPUT_VALUES_AS_SHORT_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    MMSOLVER_MAYA_VRB(
        "mmBestFitPlane: output_as_values_flag=" << output_as_values_flag);
    if (output_as_values_flag) {
        MString flag_value;
        status =
            argData.getFlagArgument(OUTPUT_VALUES_AS_SHORT_FLAG, 0, flag_value);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        const char *string = flag_value.asChar();
        MMSOLVER_MAYA_VRB("mmBestFitPlane: output_as_values=" << string);
        if (std::strcmp(string, OUTPUT_VALUES_AS_POSITION_AND_DIRECTION) == 0) {
            m_output_values_as = OutputValuesAs::kPositionAndDirection;
        } else if (std::strcmp(string,
                               OUTPUT_VALUES_AS_POSITION_DIRECTION_AND_SCALE) ==
                   0) {
            m_output_values_as = OutputValuesAs::kPositionDirectionAndScale;
        } else if (std::strcmp(string, OUTPUT_VALUES_AS_MATRIX_4X4) == 0) {
            m_output_values_as = OutputValuesAs::kMatrix4x4;
        }
    }
    MMSOLVER_MAYA_VRB("mmBestFitPlane: m_output_values_as="
                      << static_cast<size_t>(m_output_values_as));

    m_output_rms_error = true;
    const bool output_rms_error_flag =
        argData.isFlagSet(OUTPUT_RMS_ERROR_SHORT_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    MMSOLVER_MAYA_VRB(
        "mmBestFitPlane: output_rms_error_flag=" << output_rms_error_flag);
    if (output_rms_error_flag) {
        status = argData.getFlagArgument(OUTPUT_RMS_ERROR_SHORT_FLAG, 0,
                                         m_output_rms_error);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        MMSOLVER_MAYA_VRB(
            "mmBestFitPlane: m_output_rms_error=" << m_output_rms_error);
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
    mmsg::Real plane_scale = 1.0;
    mmsg::Real rms_error = 0.0;

    // Compute the best fit plane.
    rust::Slice<const mmsg::Real> points_xyz_slice{m_points_xyz.data(),
                                                   m_points_xyz.size()};
    const bool ok = mmsg::fit_plane_to_points(
        points_xyz_slice, plane_position_x, plane_position_y, plane_position_z,
        plane_normal_x, plane_normal_y, plane_normal_z, plane_scale, rms_error);
    if (!ok) {
        MMSOLVER_MAYA_ERR("mmBestFitPlane: Failed to compute best fit plane.");
        return MStatus::kFailure;
    }
    if (!m_with_scale) {
        plane_scale = 1.0;
    }

    // Return results as array of double floats:
    MDoubleArray result;
    if (m_output_values_as == OutputValuesAs::kPositionAndDirection) {
        result.append(plane_position_x);
        result.append(plane_position_y);
        result.append(plane_position_z);
        result.append(plane_normal_x);
        result.append(plane_normal_y);
        result.append(plane_normal_z);
    } else if (m_output_values_as ==
               OutputValuesAs::kPositionDirectionAndScale) {
        result.append(plane_position_x);
        result.append(plane_position_y);
        result.append(plane_position_z);
        result.append(plane_normal_x);
        result.append(plane_normal_y);
        result.append(plane_normal_z);
        result.append(plane_scale);
    } else if (m_output_values_as == OutputValuesAs::kMatrix4x4) {
        mmdata::Matrix4x4 matrix;
        const mmdata::Vector3D dir(plane_normal_x, plane_normal_y,
                                   plane_normal_z);
        mmmath::createLookAtMatrixAxisY(dir, matrix);
        matrix.m30_ = plane_position_x;
        matrix.m31_ = plane_position_y;
        matrix.m32_ = plane_position_z;

        // Scale and Rotation matrix 3x3:
        result.append(matrix.m00_ * plane_scale);
        result.append(matrix.m01_ * plane_scale);
        result.append(matrix.m02_ * plane_scale);
        result.append(matrix.m03_ * plane_scale);
        result.append(matrix.m10_ * plane_scale);
        result.append(matrix.m11_ * plane_scale);
        result.append(matrix.m12_ * plane_scale);
        result.append(matrix.m13_ * plane_scale);
        result.append(matrix.m20_ * plane_scale);
        result.append(matrix.m21_ * plane_scale);
        result.append(matrix.m22_ * plane_scale);
        result.append(matrix.m23_ * plane_scale);

        // Translation:
        result.append(matrix.m30_);
        result.append(matrix.m31_);
        result.append(matrix.m32_);
        result.append(matrix.m33_);
    }

    if (m_output_rms_error) {
        result.append(rms_error);
    }

    MPxCommand::setResult(result);
    return status;
}

}  // namespace mmsolver
