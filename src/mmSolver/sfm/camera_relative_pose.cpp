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

// NOTE: The following (MSVC) warnings are disabled because of
// OpenMVG, and are mostly caused by Eigen. Annoyingly the warnings
// must be disabled at the top-level of the source file to fully get
// rid of the warnings - it's not possible to wrap these in
// 'push/pop'. Some warnings are also triggered in 'libmv', but not as
// many as 'OpenMVG'.

// Compiler Warning (level 3) C4267: conversion from 'size_t' to
// 'object', possible loss of data.
#pragma warning(disable : 4267)

// Compiler Warning (level 1) C4305: truncation from 'type1' to
// 'type2'.
#pragma warning(disable : 4305)

// Compiler Warning (level 4) C4127: conditional expression is
// constant
#pragma warning(disable : 4127)

// Compiler Warning (levels 3 and 4) C4244: 'conversion' conversion
// from 'type1' to 'type2', possible loss of data.
#pragma warning(disable : 4244)

// Compiler Warning (level 4) C4459: declaration of 'identifier' hides
// global declaration.
#pragma warning(disable : 4459)

// Compiler Warning (level 4) C4456: declaration of 'identifier' hides
// previous local declaration.
#pragma warning(disable : 4456)

// Compiler Warning (level 4) C4100: 'identifier' : unreferenced
// formal parameter.
#pragma warning(disable : 4100)

// Compiler Warning (level 3) C4018: 'token' : signed/unsigned
// mismatch.
#pragma warning(disable : 4018)

// Compiler Warning (level 4) C4714: function 'function' marked as
// __forceinline not inlined.
#pragma warning(disable : 4714)

// Compiler Warning (level 1) C4005: 'identifier' : macro
// redefinition.
#pragma warning(disable : 4005)

// Compiler Warning (level 4) C4702: unreachable code.
#pragma warning(disable : 4702)

#include "camera_relative_pose.h"

// STL
#include <algorithm>
#include <array>
#include <cassert>
#include <chrono>
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
#include <vector>

// OpenMVG
#ifdef MMSOLVER_USE_OPENMVG

#include <ceres/ceres.h>
#include <openMVG/numeric/numeric.h>

#include <openMVG/cameras/Camera_Intrinsics.hpp>
#include <openMVG/cameras/Camera_Pinhole.hpp>
#include <openMVG/features/feature.hpp>
#include <openMVG/features/feature_container.hpp>
#include <openMVG/geometry/pose3.hpp>
#include <openMVG/matching/indMatch.hpp>
#include <openMVG/matching/indMatchDecoratorXY.hpp>
#include <openMVG/matching/regions_matcher.hpp>
#include <openMVG/multiview/conditioning.hpp>
#include <openMVG/multiview/motion_from_essential.hpp>
#include <openMVG/multiview/solver_essential_eight_point.hpp>
#include <openMVG/multiview/solver_essential_kernel.hpp>
#include <openMVG/multiview/solver_fundamental_kernel.hpp>
#include <openMVG/multiview/triangulation.hpp>
#include <openMVG/numeric/eigen_alias_definition.hpp>
#include <openMVG/robust_estimation/robust_estimator_ACRansac.hpp>
#include <openMVG/robust_estimation/robust_estimator_ACRansacKernelAdaptator.hpp>
#include <openMVG/sfm/pipelines/sfm_robust_model_estimation.hpp>
#include <openMVG/sfm/sfm_data.hpp>
#include <openMVG/sfm/sfm_data_BA.hpp>
#include <openMVG/sfm/sfm_data_BA_ceres.hpp>
#include <openMVG/sfm/sfm_data_io.hpp>
#include <openMVG/types.hpp>

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

using KernelType = openMVG::robust::ACKernelAdaptor<
    openMVG::fundamental::kernel::NormalizedEightPointKernel,
    openMVG::fundamental::kernel::SymmetricEpipolarDistanceError,
    openMVG::UnnormalizerT, openMVG::Mat3>;

bool robust_relative_pose(const openMVG::cameras::IntrinsicBase *intrinsics1,
                          const openMVG::cameras::IntrinsicBase *intrinsics2,
                          const openMVG::Mat &x1, const openMVG::Mat &x2,
                          openMVG::sfm::RelativePose_Info &relativePose_info,
                          const std::pair<size_t, size_t> &size_ima1,
                          const std::pair<size_t, size_t> &size_ima2,
                          const size_t max_iteration_count) {
    // Enable to print out 'MMSOLVER_VRB' results.
    const bool verbose = false;

    MMSOLVER_VRB("robust_relative_pose: intrinsics1: " << intrinsics1);
    MMSOLVER_VRB("robust_relative_pose: intrinsics2: " << intrinsics2);
    MMSOLVER_VRB("robust_relative_pose: x1: " << x1);
    MMSOLVER_VRB("robust_relative_pose: x2: " << x2);
    MMSOLVER_VRB("robust_relative_pose: size_ima1: " << size_ima1.first << ", "
                                                     << size_ima1.second);
    MMSOLVER_VRB("robust_relative_pose: size_ima2: " << size_ima2.first << ", "
                                                     << size_ima2.second);
    MMSOLVER_VRB(
        "robust_relative_pose: max_iteration_count: " << max_iteration_count);
    if (!intrinsics1 || !intrinsics2) {
        return false;
    }

    // Compute the bearing vectors
    const openMVG::Mat3X bearing1 = (*intrinsics1)(x1),
                         bearing2 = (*intrinsics2)(x2);

    auto pinhole_cameras_only =
        isPinhole(intrinsics1->getType()) && isPinhole(intrinsics2->getType());
    auto more_than_five = x1.cols() > 5;
    auto more_than_eight = x1.cols() > 8;

    if (more_than_eight) {
        // Define the AContrario adaptor to use the 8 point essential matrix
        // solver.
        typedef openMVG::robust::ACKernelAdaptor_AngularRadianError<
            openMVG::EightPointRelativePoseSolver, openMVG::AngularError,
            openMVG::Mat3>
            KernelType;

        KernelType kernel(bearing1, bearing2);

        // Robustly estimate the Essential matrix with A Contrario RANSAC
        const double upper_bound_precision =
            (relativePose_info.initial_residual_tolerance ==
             std::numeric_limits<double>::infinity())
                ? std::numeric_limits<double>::infinity()
                : openMVG::D2R(relativePose_info.initial_residual_tolerance);
        const auto ac_ransac_output = openMVG::robust::ACRANSAC(
            kernel, relativePose_info.vec_inliers, max_iteration_count,
            &relativePose_info.essential_matrix, upper_bound_precision,
            verbose);

        const double &threshold = ac_ransac_output.first;
        relativePose_info.found_residual_precision =
            openMVG::R2D(threshold);  // Degree

        auto minimum_samples = KernelType::Solver::MINIMUM_SAMPLES;
        MMSOLVER_VRB(
            "robust_relative_pose: minimum_samples: " << minimum_samples);
        MMSOLVER_VRB("robust_relative_pose: samples: "
                     << relativePose_info.vec_inliers.size());
        if (relativePose_info.vec_inliers.size() < minimum_samples) {
            // no sufficient coverage (the model does not support enough
            // samples)
            return false;
        }

    } else if (more_than_five && pinhole_cameras_only) {
        // Five Point Solver only supports pinhole cameras.

        // Define the AContrario adaptor to use the 5 point essential matrix
        // solver.
        using KernelType = openMVG::robust::ACKernelAdaptorEssential<
            openMVG::essential::kernel::FivePointSolver,
            openMVG::fundamental::kernel::EpipolarDistanceError, openMVG::Mat3>;
        KernelType kernel(
            x1, bearing1, size_ima1.first, size_ima1.second, x2, bearing2,
            size_ima2.first, size_ima2.second,
            dynamic_cast<const openMVG::cameras::Pinhole_Intrinsic *>(
                intrinsics1)
                ->K(),
            dynamic_cast<const openMVG::cameras::Pinhole_Intrinsic *>(
                intrinsics2)
                ->K());

        // Robustly estimation of the Model and its precision
        const auto ac_ransac_output = openMVG::robust::ACRANSAC(
            kernel, relativePose_info.vec_inliers, max_iteration_count,
            &relativePose_info.essential_matrix,
            relativePose_info.initial_residual_tolerance, verbose);

        relativePose_info.found_residual_precision = ac_ransac_output.first;

        auto minimum_samples = KernelType::Solver::MINIMUM_SAMPLES;
        MMSOLVER_VRB("minimum_samples: " << minimum_samples);
        MMSOLVER_VRB("samples: " << relativePose_info.vec_inliers.size());
        if (relativePose_info.vec_inliers.size() < minimum_samples) {
            // no sufficient coverage (the model does not support
            // enough samples)
            return false;
        }
    }

    // estimation of the relative poses based on the cheirality test
    openMVG::geometry::Pose3 relative_pose;
    if (!openMVG::RelativePoseFromEssential(
            bearing1, bearing2, relativePose_info.essential_matrix,
            relativePose_info.vec_inliers, &relative_pose)) {
        return false;
    }

    relativePose_info.relativePose = relative_pose;
    return true;
}

bool compute_relative_pose(
    const int32_t image_width_a, const int32_t image_width_b,
    const int32_t image_height_a, const int32_t image_height_b,
    const double focal_length_pix_a, const double focal_length_pix_b,
    const double ppx_pix_a, const double ppx_pix_b, const double ppy_pix_a,
    const double ppy_pix_b,
    const std::vector<std::pair<double, double>> &marker_coords_a,
    const std::vector<std::pair<double, double>> &marker_coords_b,
    const MarkerPtrList &marker_list_a, const MarkerPtrList &marker_list_b,
    openMVG::sfm::RelativePose_Info &pose_info) {
    // Enable to print out 'MMSOLVER_VRB' results.
    const bool verbose = false;

    const openMVG::cameras::Pinhole_Intrinsic cam_a(
        image_width_a, image_height_a, focal_length_pix_a, ppx_pix_a,
        ppy_pix_a);
    const openMVG::cameras::Pinhole_Intrinsic cam_b(
        image_width_b, image_height_b, focal_length_pix_b, ppx_pix_b,
        ppy_pix_b);

    openMVG::Mat marker_coords_matrix_a =
        convert_marker_coords_to_matrix(marker_coords_a);
    openMVG::Mat marker_coords_matrix_b =
        convert_marker_coords_to_matrix(marker_coords_b);

    // Compute the relative pose thanks to an essential matrix
    // estimation.
    const std::pair<size_t, size_t> image_size_a(
        static_cast<size_t>(image_width_a),
        static_cast<size_t>(image_height_a));
    const std::pair<size_t, size_t> image_size_b(
        static_cast<size_t>(image_width_b),
        static_cast<size_t>(image_height_b));
    auto num_max_iter = 4096;
    bool robust_pose_ok = robust_relative_pose(
        &cam_a, &cam_b, marker_coords_matrix_a, marker_coords_matrix_b,
        pose_info, image_size_a, image_size_b, num_max_iter);
    if (!robust_pose_ok) {
        MMSOLVER_ERR("Robust relative pose estimation failure.");
        return false;
    }
    MMSOLVER_VRB("Found an Essential matrix:");
    MMSOLVER_VRB("- precision: " << pose_info.found_residual_precision
                                 << " pixels");

    MMSOLVER_VRB("- #matches: " << marker_coords_matrix_a.size());
    for (auto i = 0; i < marker_coords_matrix_a.size(); i++) {
        auto coord_x_a = marker_coords_matrix_a.col(i)[0];
        auto coord_y_a = marker_coords_matrix_a.col(i)[1];
        auto coord_x_b = marker_coords_matrix_b.col(i)[0];
        auto coord_y_b = marker_coords_matrix_b.col(i)[1];
        MMSOLVER_VRB("  - #match: " << i << " = " << coord_x_a << ","
                                    << coord_y_a << " <-> " << coord_x_b << ","
                                    << coord_y_b);
    }

    MMSOLVER_VRB("- marker_list_a size: " << marker_list_a.size());
    MMSOLVER_VRB("- marker_list_b size: " << marker_list_b.size());
    MMSOLVER_VRB("- #inliers: " << pose_info.vec_inliers.size());
    auto i = 0;
    for (auto inlier : pose_info.vec_inliers) {
        if (inlier < marker_list_a.size()) {
            auto mkr_a = marker_list_a[inlier];
            auto mkr_b = marker_list_b[inlier];
            auto mkr_name_a = mkr_a->getNodeName();
            auto mkr_name_b = mkr_b->getNodeName();
            MMSOLVER_VRB("  - #inlier A: " << i << " = " << inlier
                                           << " mkr: " << mkr_name_a.asChar());
            MMSOLVER_VRB("  - #inlier B: " << i << " = " << inlier
                                           << " mkr: " << mkr_name_b.asChar());
        }
        ++i;
    }

    MMSOLVER_VRB("- Center: " << pose_info.relativePose.center());
    MMSOLVER_VRB("- Translation: " << pose_info.relativePose.translation());
    MMSOLVER_VRB("- Rotation: " << pose_info.relativePose.rotation());
    return true;
}

bool construct_two_camera_sfm_data_scene(
    const int32_t image_width_a, const int32_t image_width_b,
    const int32_t image_height_a, const int32_t image_height_b,
    const double focal_length_pix_a, const double focal_length_pix_b,
    const double ppx_pix_a, const double ppx_pix_b, const double ppy_pix_a,
    const double ppy_pix_b, const openMVG::sfm::RelativePose_Info &pose_info,
    openMVG::sfm::SfM_Data &scene) {
    auto image_width_size_a = static_cast<size_t>(image_width_a);
    auto image_width_size_b = static_cast<size_t>(image_width_b);
    auto image_height_size_a = static_cast<size_t>(image_height_a);
    auto image_height_size_b = static_cast<size_t>(image_height_b);

    // Setup a SfM scene with two view corresponding the pictures
    scene.views[0].reset(new openMVG::sfm::View(
        /*imgPath=*/"",
        /*view_id=*/0,
        /*intrinsic_id=*/0,
        /*pose_id=*/0, image_width_size_a, image_height_size_a));
    scene.views[1].reset(new openMVG::sfm::View(
        /*imgPath=*/"",
        /*view_id=*/1,
        /*intrinsic_id=*/1,
        /*pose_id=*/1, image_width_size_b, image_height_size_b));

    // Setup intrinsics camera data
    // Each view use it's own pinhole camera intrinsic
    scene.intrinsics[0].reset(new openMVG::cameras::Pinhole_Intrinsic(
        image_width_a, image_height_a, focal_length_pix_a, ppx_pix_a,
        ppy_pix_a));
    scene.intrinsics[1].reset(new openMVG::cameras::Pinhole_Intrinsic(
        image_width_b, image_height_b, focal_length_pix_b, ppx_pix_b,
        ppy_pix_b));

    // Setup poses camera data
    auto pose_a = openMVG::geometry::Pose3(openMVG::Mat3::Identity(),
                                           openMVG::Vec3::Zero());
    auto pose_b = pose_info.relativePose;
    scene.poses[scene.views[0]->id_pose] = pose_a;
    scene.poses[scene.views[1]->id_pose] = pose_b;
    return true;
}

// Init structure by inlier triangulation
bool triangulate_relative_pose(
    const std::vector<std::pair<double, double>> &marker_coords_a,
    const std::vector<std::pair<double, double>> &marker_coords_b,
    const std::vector<uint32_t> &vec_inliers,
    const MarkerPtrList &marker_list_a, const MarkerPtrList &marker_list_b,
    BundlePtrList &bundle_list, openMVG::sfm::SfM_Data &scene) {
    // Enable to print out 'MMSOLVER_VRB' results.
    const bool verbose = false;

    auto num = 0;
    openMVG::sfm::Landmarks &landmarks = scene.structure;
    openMVG::geometry::Pose3 pose_a = scene.poses[scene.views[0]->id_pose];
    openMVG::geometry::Pose3 pose_b = scene.poses[scene.views[1]->id_pose];
    for (const auto inlier_idx : vec_inliers) {
        auto coord_a = marker_coords_a[inlier_idx];
        auto coord_b = marker_coords_b[inlier_idx];
        auto coord_x_a = std::get<0>(coord_a);
        auto coord_y_a = std::get<1>(coord_a);
        auto coord_x_b = std::get<0>(coord_b);
        auto coord_y_b = std::get<1>(coord_b);

        const auto feature_a =
            openMVG::features::SIOPointFeature(coord_x_a, coord_y_a);
        const auto feature_b =
            openMVG::features::SIOPointFeature(coord_x_b, coord_y_b);
        const auto feature_coord_a = feature_a.coords().cast<double>();
        const auto feature_coord_b = feature_b.coords().cast<double>();

        // Point triangulation
        openMVG::Vec3 bundle_pos;
        const auto triangulation_method =
            openMVG::ETriangulationMethod::DEFAULT;
        auto triangulate_ok = openMVG::Triangulate2View(
            pose_a.rotation(), pose_a.translation(),
            (*scene.intrinsics[0])(feature_coord_a), pose_b.rotation(),
            pose_b.translation(), (*scene.intrinsics[1])(feature_coord_b),
            bundle_pos, triangulation_method);
        if (triangulate_ok) {
            // TODO: Ensure the land-markers/control points are
            // centered around the 3D origin - we do not want our
            // camera to be far away from the origin.

            // Add a new landmark (3D point with it's 2d observations)
            auto id_view_a = scene.views[0]->id_view;
            auto id_view_b = scene.views[1]->id_view;
            openMVG::sfm::Landmark landmark;
            landmark.obs[id_view_a] =
                openMVG::sfm::Observation(feature_coord_a, inlier_idx);
            landmark.obs[id_view_b] =
                openMVG::sfm::Observation(feature_coord_b, inlier_idx);
            landmark.X = bundle_pos;
            landmarks.insert({inlier_idx, landmark});

            auto mkr_a = marker_list_a[inlier_idx];
            auto mkr_b = marker_list_b[inlier_idx];
            auto bnd = bundle_list[inlier_idx];
            auto mkr_name_a = mkr_a->getNodeName();
            auto mkr_name_b = mkr_b->getNodeName();
            auto bnd_name = bnd->getNodeName();
            MMSOLVER_VRB("triangulated Marker A: " << mkr_name_a.asChar());
            MMSOLVER_VRB("triangulated Marker B: " << mkr_name_b.asChar());
            MMSOLVER_VRB("triangulated bundle: " << bnd_name.asChar());
            num++;
        }
    }
    return num > 0;
}

bool bundle_adjustment(openMVG::sfm::SfM_Data &scene) {
    // Enable to print out 'MMSOLVER_VRB' results.
    const bool verbose = false;

    // Perform Bundle Adjustment of the scene.
    //
    // TODO: Add "openMVG::sfm::Control_Point_Parameter" to allow
    // locked bundles.
    //
    auto optimize_options = openMVG::sfm::Optimize_Options(
        openMVG::cameras::Intrinsic_Parameter_Type::ADJUST_ALL,
        openMVG::sfm::Extrinsic_Parameter_Type::ADJUST_ALL,
        openMVG::sfm::Structure_Parameter_Type::ADJUST_ALL);
    // TODO: use 'optimize_options.control_point_opt.bUse_control_points'
    auto bundle_adjust_verbose = verbose;
    auto bundle_adjust_multithreaded = false;
    auto ceres_options =
        openMVG::sfm::Bundle_Adjustment_Ceres::BA_Ceres_options(
            bundle_adjust_verbose, bundle_adjust_multithreaded);
    ceres_options.bCeres_summary_ = true;
    ceres_options.bUse_loss_function_ = false;

    ceres_options.linear_solver_type_ =
        static_cast<int>(ceres::DENSE_NORMAL_CHOLESKY);
    ceres_options.preconditioner_type_ = static_cast<int>(ceres::JACOBI);
    ceres_options.sparse_linear_algebra_library_type_ =
        static_cast<int>(ceres::NO_SPARSE);

    MMSOLVER_VRB(
        "ceres_options.bCeres_summary_: " << ceres_options.bCeres_summary_);
    MMSOLVER_VRB("ceres_options.nb_threads_: " << ceres_options.nb_threads_);
    MMSOLVER_VRB("ceres_options.linear_solver_type_: "
                 << ceres_options.linear_solver_type_);
    MMSOLVER_VRB("ceres_options.preconditioner_type_: "
                 << ceres_options.preconditioner_type_);
    MMSOLVER_VRB("ceres_options.sparse_linear_algebra_library_type_: "
                 << ceres_options.sparse_linear_algebra_library_type_);
    MMSOLVER_VRB("ceres_options.bUse_loss_function_: "
                 << ceres_options.bUse_loss_function_);

    openMVG::sfm::Bundle_Adjustment_Ceres bundle_adjustment(ceres_options);
    return bundle_adjustment.Adjust(scene, optimize_options);
}

}  // namespace sfm
}  // namespace mmsolver
