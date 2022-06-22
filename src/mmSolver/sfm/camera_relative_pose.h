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
 * Calculate camera relative poses.
 */

#ifndef MM_SOLVER_SFM_CAMERA_RELATIVE_POSE_H
#define MM_SOLVER_SFM_CAMERA_RELATIVE_POSE_H

// STL
#include <cmath>
#include <vector>

// OpenMVG
#ifdef MMSOLVER_USE_OPENMVG

// #include <openMVG/numeric/numeric.h>
// #include <openMVG/cameras/Camera_Intrinsics.hpp>
// #include <openMVG/cameras/Camera_Pinhole.hpp>
// #include <openMVG/features/feature.hpp>
// #include <openMVG/features/feature_container.hpp>
// #include <openMVG/geometry/pose3.hpp>
// #include <openMVG/matching/indMatch.hpp>
// #include <openMVG/matching/indMatchDecoratorXY.hpp>
// #include <openMVG/matching/regions_matcher.hpp>
// #include <openMVG/multiview/conditioning.hpp>
// #include <openMVG/multiview/motion_from_essential.hpp>
// #include <openMVG/multiview/solver_essential_eight_point.hpp>
// #include <openMVG/multiview/solver_essential_kernel.hpp>
// #include <openMVG/multiview/solver_fundamental_kernel.hpp>
// #include <openMVG/multiview/triangulation.hpp>
// #include <openMVG/numeric/eigen_alias_definition.hpp>
// #include <openMVG/robust_estimation/robust_estimator_ACRansac.hpp>
// #include
// <openMVG/robust_estimation/robust_estimator_ACRansacKernelAdaptator.hpp>
#include <openMVG/sfm/pipelines/sfm_robust_model_estimation.hpp>
#include <openMVG/sfm/sfm_data.hpp>
#include <openMVG/sfm/sfm_data_BA.hpp>
#include <openMVG/sfm/sfm_data_BA_ceres.hpp>
#include <openMVG/sfm/sfm_data_io.hpp>
// #include <openMVG/types.hpp>

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

bool myRobustRelativePose(const openMVG::cameras::IntrinsicBase *intrinsics1,
                          const openMVG::cameras::IntrinsicBase *intrinsics2,
                          const openMVG::Mat &x1, const openMVG::Mat &x2,
                          openMVG::sfm::RelativePose_Info &relativePose_info,
                          const std::pair<size_t, size_t> &size_ima1,
                          const std::pair<size_t, size_t> &size_ima2,
                          const size_t max_iteration_count);

void convert_camera_lens_mm_to_pixel_units(const int32_t image_width,
                                           const int32_t image_height,
                                           const double focal_length_mm,
                                           const double sensor_width_mm,
                                           double &focal_length_pix,
                                           double &ppx_pix, double &ppy_pix);

openMVG::Mat convert_marker_coords_to_matrix(
    const std::vector<std::pair<double, double>> &marker_coords);

bool compute_relative_pose(
    const int32_t image_width_a, const int32_t image_width_b,
    const int32_t image_height_a, const int32_t image_height_b,
    const double focal_length_pix_a, const double focal_length_pix_b,
    const double ppx_pix_a, const double ppx_pix_b, const double ppy_pix_a,
    const double ppy_pix_b,
    const std::vector<std::pair<double, double>> &marker_coords_a,
    const std::vector<std::pair<double, double>> &marker_coords_b,
    const MarkerPtrList &marker_list_a, const MarkerPtrList &marker_list_b,
    openMVG::sfm::RelativePose_Info &pose_info);

bool construct_two_camera_sfm_data_scene(
    const int32_t image_width_a, const int32_t image_width_b,
    const int32_t image_height_a, const int32_t image_height_b,
    const double focal_length_pix_a, const double focal_length_pix_b,
    const double ppx_pix_a, const double ppx_pix_b, const double ppy_pix_a,
    const double ppy_pix_b, const openMVG::sfm::RelativePose_Info &pose_info,
    openMVG::sfm::SfM_Data &scene);

bool triangulate_relative_pose(
    const std::vector<std::pair<double, double>> &marker_coords_a,
    const std::vector<std::pair<double, double>> &marker_coords_b,
    const std::vector<uint32_t> &vec_inliers,
    const MarkerPtrList &marker_list_a, const MarkerPtrList &marker_list_b,
    BundlePtrList &bundle_list, openMVG::sfm::SfM_Data &scene);

bool bundle_adjustment(openMVG::sfm::SfM_Data &scene);

}  // namespace sfm
}  // namespace mmsolver

#endif  // MM_SOLVER_SFM_CAMERA_RELATIVE_POSE_H
