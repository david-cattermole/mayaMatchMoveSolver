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
 * Guess a camera pose from a set of known points.
 *
 * This process is known as 'perspective-n-points', and in OpenMVG it's
 * named as 'Resectioning'.
 */

#include "camera_from_known_points.h"

// STL
#include <algorithm>
#include <array>
#include <cmath>
#include <fstream>
#include <iostream>
#include <iterator>
#include <limits>
#include <list>
#include <map>
#include <memory>
#include <string>
#include <thread>
#include <tuple>
#include <vector>

// OpenMVG
#ifdef MMSOLVER_USE_OPENMVG

#include <openMVG/cameras/Camera_Intrinsics.hpp>
#include <openMVG/cameras/Camera_Pinhole.hpp>
#include <openMVG/geometry/pose3.hpp>
#include <openMVG/multiview/solver_resection_p3p_nordberg.hpp>
#include <openMVG/robust_estimation/robust_estimator_ACKernelAdaptorResection.hpp>
#include <openMVG/robust_estimation/robust_estimator_ACRansac.hpp>
#include <openMVG/robust_estimation/robust_estimator_ACRansacKernelAdaptator.hpp>

#endif  // MMSOLVER_USE_OPENMVG

// Maya
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MDagPath.h>
#include <maya/MEulerRotation.h>
#include <maya/MFnDagNode.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MItSelectionList.h>
#include <maya/MMatrix.h>
#include <maya/MMatrixArray.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MPlugArray.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MSyntax.h>
#include <maya/MTime.h>
#include <maya/MTimeArray.h>
#include <maya/MTransformationMatrix.h>
#include <maya/MTypes.h>

// MM Solver
#include "mmSolver/adjust/adjust_defines.h"
#include "mmSolver/mayahelper/maya_attr.h"
#include "mmSolver/mayahelper/maya_bundle.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_marker.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/sfm/sfm_utils.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/number_utils.h"

namespace mmsolver {
namespace sfm {

// Use AC-RANSAC to try and find the camera pose from matching 2D and 3D points.
//
// - The points_3d matrix is expected to have the Z-coordinate flipped
//   to match OpenMVG (rather than Maya).
bool robust_camera_pose_from_known_points(
    const openMVG::Mat &points_2d, const openMVG::Mat &points_3d,
    const std::pair<uint32_t, uint32_t> &image_size,
    const double focal_length_pix, const double ppx_pix, const double ppy_pix,
    const uint32_t max_iteration_count, openMVG::Mat34 &out_projection_matrix) {
    // Enable to print out 'MMSOLVER_MAYA_VRB' results.
    const bool verbose = false;

    // Upper bound pixel tolerance for residual errors.
    double error_upper_bound = std::numeric_limits<double>::infinity();

    std::vector<uint32_t> vec_inliers = {};
    vec_inliers.clear();
    vec_inliers.reserve(points_2d.cols());

    // P3P Nordberg (ECCV18) - an algorithm needing only 3 points.
    //
    // https://openaccess.thecvf.com/content_ECCV_2018/html/Mikael_Persson_Lambda_Twist_An_ECCV_2018_paper.html
    using SolverType = openMVG::euclidean_resection::P3PSolver_Nordberg;
    using KernelType =
        openMVG::ACKernelAdaptorResection_Intrinsics<SolverType,
                                                     openMVG::Mat34>;

    const auto image_width = image_size.first;
    const auto image_height = image_size.second;
    const openMVG::cameras::Pinhole_Intrinsic camera_intrinsics(
        image_width, image_height, focal_length_pix, ppx_pix, ppy_pix);

    KernelType kernel(points_2d, points_3d, &camera_intrinsics);

    // Robustly estimate the Resection matrix with A Contrario (AC)
    // RANSAC.
    const auto ac_ransac_output = openMVG::robust::ACRANSAC(
        kernel, vec_inliers, max_iteration_count, &out_projection_matrix,
        error_upper_bound, verbose);
    // The amount of pixel error that is computed.
    double out_error_max = ac_ransac_output.first;

    // NFA = Number of False Alarms.
    double out_min_nfa = ac_ransac_output.second;

    auto solution_found = false;
    const size_t samples = vec_inliers.size();
    const int minimum_samples = SolverType::MINIMUM_SAMPLES;
    if (samples < minimum_samples) {
        // no sufficient coverage (not enough matching data points
        // given)
        MMSOLVER_MAYA_WRN(
            "Camera Pose could not be found with at least 3 points."
            << " error=" << out_error_max << " pixels"
            << ", number of false alarms=" << out_min_nfa
            << ", minimum samples required=" << minimum_samples
            << ", valid samples=" << samples);
    } else {
        solution_found = true;
    }

    if (!solution_found) {
        return false;
    }

    MMSOLVER_MAYA_VRB("Found a Camera matrix from known points:");
    MMSOLVER_MAYA_VRB("- matrix: " << out_projection_matrix);
    MMSOLVER_MAYA_VRB("- error: " << out_error_max << " pixels");
    MMSOLVER_MAYA_VRB("- number of false alarms: " << out_min_nfa);

    MMSOLVER_MAYA_VRB("- #points 3D: " << points_3d.cols());
    for (auto i = 0; i < points_3d.cols(); i++) {
        auto point_3d_x = points_3d.col(i)[0];
        auto point_3d_y = points_3d.col(i)[1];
        auto point_3d_z = points_3d.col(i)[2];
        MMSOLVER_MAYA_VRB("  - #point 3D: " << i << " = " << point_3d_x << ","
                                            << point_3d_y << "," << point_3d_z);
    }

    MMSOLVER_MAYA_VRB("- #points 2D: " << points_2d.cols());
    for (auto i = 0; i < points_2d.cols(); i++) {
        auto point_2d_x = points_2d.col(i)[0];
        auto point_2d_y = points_2d.col(i)[1];
        MMSOLVER_MAYA_VRB("  - #point 2D: " << i << " = " << point_2d_x << ","
                                            << point_2d_y);
    }

    MMSOLVER_MAYA_VRB("- #inliers: " << samples);

    return true;
}

bool compute_camera_pose_from_known_points(
    const int32_t image_width, const int32_t image_height,
    const double focal_length_pix, const double ppx_pix, const double ppy_pix,
    const std::vector<std::pair<double, double>> &marker_coords,
    const std::vector<std::tuple<double, double, double>> &bundle_coords,
    MTransformationMatrix &out_pose_transform) {
    openMVG::Mat marker_coords_matrix =
        convert_marker_coords_to_matrix(marker_coords);

    openMVG::Mat bundle_coords_matrix =
        convert_bundle_coords_to_matrix_flip_z(bundle_coords);

    const std::pair<uint32_t, uint32_t> image_size(
        static_cast<uint32_t>(image_width),
        static_cast<uint32_t>(image_height));

    openMVG::Mat34 projection_matrix;
    auto num_max_iter = 1024;
    bool ok = robust_camera_pose_from_known_points(
        marker_coords_matrix, bundle_coords_matrix, image_size,
        focal_length_pix, ppx_pix, ppy_pix, num_max_iter, projection_matrix);
    if (!ok) {
        MMSOLVER_MAYA_ERR(
            "Robust camera pose from known points estimation failure.");
        return false;
    }

    openMVG::Mat3 intrinsic_matrix;
    openMVG::Mat3 rotation_matrix;
    openMVG::Vec3 translation_vector;
    openMVG::KRt_From_P(projection_matrix, &intrinsic_matrix, &rotation_matrix,
                        &translation_vector);

    auto pose = openMVG::geometry::Pose3(
        rotation_matrix, -rotation_matrix.transpose() * translation_vector);

    double camera_translation_scale = 1.0;
    out_pose_transform =
        convert_pose_to_maya_transform_matrix(pose, camera_translation_scale);

    return true;
}

}  // namespace sfm
}  // namespace mmsolver
