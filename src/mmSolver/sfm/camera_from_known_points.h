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
 * Camera From Known Points will calculate a 3D camera pose from known 2D
 * Markers and known 3D bundle positions. This is also known as
 * 'perspective-n-points'.
 *
 * For example when you have calculated a camera pose and 3D bundle
 * positions on frame A and B from 2D Marker positions (see
 * 'camera_relative_pose.h' for details), you can calculate the camera
 * pose on frame C as long as frame C shares at least N bundle
 * positions with frame A and B.
 *
 * There are different algorithms for calculating the camera pose
 * 'resectioning', some require a minimum of 3 (bundle) 3D points as
 * input and then using a robust method (such as AC RANSAC) to get the
 * best camera pose (from the lowest error level). If 6 or more
 * (bundle) 3D points are available it is possible to compute a more
 * accurate camera pose.
 */

#ifndef MM_SOLVER_SFM_CAMERA_FROM_KNOWN_POINTS_H
#define MM_SOLVER_SFM_CAMERA_FROM_KNOWN_POINTS_H

// STL
#include <cmath>
#include <vector>

// OpenMVG
#ifdef MMSOLVER_USE_OPENMVG

#include <openMVG/numeric/numeric.h>

#include <openMVG/numeric/eigen_alias_definition.hpp>
#include <openMVG/types.hpp>

#endif  // MMSOLVER_USE_OPENMVG

// Maya
#include <maya/MAnimCurveChange.h>
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MDGModifier.h>
#include <maya/MGlobal.h>
#include <maya/MIOStream.h>
#include <maya/MPxCommand.h>
#include <maya/MSelectionList.h>
#include <maya/MSyntax.h>
#include <maya/MTime.h>
#include <maya/MTimeArray.h>

// Maya helpers
#include "mmSolver/mayahelper/maya_attr.h"
#include "mmSolver/mayahelper/maya_bundle.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_marker.h"
#include "mmSolver/mayahelper/maya_utils.h"

namespace mmsolver {
namespace sfm {

bool robust_camera_pose_from_known_points(
    const openMVG::Mat &points_2d, const openMVG::Mat &points_3d,
    const std::pair<uint32_t, uint32_t> &image_size,
    const double focal_length_pix, const double ppx_pix, const double ppy_pix,
    const uint32_t max_iteration_count, openMVG::Mat34 &out_projection_matrix);

bool compute_camera_pose_from_known_points(
    const int32_t image_width, const int32_t image_height,
    const double focal_length_pix, const double ppx_pix, const double ppy_pix,
    const std::vector<std::pair<double, double>> &marker_coords,
    const std::vector<std::tuple<double, double, double>> &bundle_coords,
    MTransformationMatrix &out_pose_transform);

}  // namespace sfm
}  // namespace mmsolver

#endif  // MM_SOLVER_SFM_CAMERA_FROM_KNOWN_POINTS_H
