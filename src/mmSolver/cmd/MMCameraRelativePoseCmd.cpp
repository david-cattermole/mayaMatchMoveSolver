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
 * Command for calculating camera relative poses.

import maya.cmds

nodes = maya.cmds.ls('cam_tfm', long=True) or []
nodes += maya.cmds.ls('Track_*_MKR', long=True) or []

maya.cmds.loadPlugin('mmSolver', quiet=True)
maya.cmds.mmCameraRelativePose(nodes, startFrame=21, endFrame=29)

# Possible flags for this tool.
maya.cmds.mmCameraRelativePose(
    cameraA='cameraA',
    cameraB='cameraB',
    frameA=21,
    frameB=29,
    markerBundle=[
        ('markerA1', 'markerB1', 'bundle1'),
        ('markerA2', 'markerB2', 'bundle2'),
        ('markerA3', 'markerB3', 'bundle3'),
        ('markerA4', 'markerB4', 'bundle4'),
        ('markerA5', 'markerB5', 'bundle5'),
        ('markerA6', 'markerB6', 'bundle6'),
    ],
)

#########################################################################

import pprint
import maya.cmds
import mmSolver.api as mmapi

# nodes = maya.cmds.ls('cam_tfm', long=True) or []
mkr_nodes = maya.cmds.ls('Track_*_MKR', long=True) or []

mkr_list = []
mkr_bnd_list = []
for mkr_node in mkr_nodes:
    mkr = mmapi.Marker(node=mkr_node)
    mkr_list.append(mkr)

    bnd = mkr.get_bundle()
    if bnd:
        mkr_node = mkr.get_node()
        bnd_node = bnd.get_node()
        mkr_bnd = [mkr_node, mkr_node, bnd_node]
        mkr_bnd_list.append(mkr_bnd)

# pprint.pprint(mkr_bnd_list)

maya.cmds.loadPlugin('mmSolver', quiet=True)
maya.cmds.mmCameraRelativePose(
    frameA=22,
    frameB=29,
    cameraA='cam_tfm',
    cameraB='cam_tfm',
    markerBundle=mkr_bnd_list
)

 */

// NOTE: The following (MSVC) warnings are disabled because of
// OpenMVG, and are mostly caused by Eigen. Annoyingly the warnings
// must be disabled at the top-level of the source file to fully get
// rid of the warnings - it's not possible to wrap these in
// 'push/pop'. Some warnings are also triggered in 'libmv', but not as
// many as 'OpenMVG'.

// Compiler Warning (level 3) C4267: conversion from 'size_t' to
// 'object', possible loss of data.
#pragma warning( disable : 4267 )

// Compiler Warning (level 1) C4305: truncation from 'type1' to
// 'type2'.
#pragma warning( disable : 4305 )

// Compiler Warning (level 4) C4127: conditional expression is
// constant
#pragma warning( disable : 4127 )

// Compiler Warning (levels 3 and 4) C4244: 'conversion' conversion
// from 'type1' to 'type2', possible loss of data.
#pragma warning( disable : 4244 )

// Compiler Warning (level 4) C4459: declaration of 'identifier' hides
// global declaration.
#pragma warning( disable : 4459 )

// Compiler Warning (level 4) C4456: declaration of 'identifier' hides
// previous local declaration.
#pragma warning( disable : 4456 )

// Compiler Warning (level 4) C4100: 'identifier' : unreferenced
// formal parameter.
#pragma warning( disable : 4100 )

// Compiler Warning (level 3) C4018: 'token' : signed/unsigned
// mismatch.
#pragma warning( disable : 4018 )

// Compiler Warning (level 4) C4714: function 'function' marked as
// __forceinline not inlined.
#pragma warning( disable : 4714 )

// Compiler Warning (level 1) C4005: 'identifier' : macro
// redefinition.
#pragma warning( disable : 4005 )

// Compiler Warning (level 4) C4702: unreachable code.
#pragma warning( disable : 4702 )

#include "MMCameraRelativePoseCmd.h"

// STL
#include <vector>
#include <cmath>
#include <cassert>
#include <list>
#include <string>
#include <algorithm>
#include <fstream>
#include <iostream>
#include <iterator>
#include <map>
#include <limits>
#include <array>
#include <memory>

#include <chrono>
#include <thread>

// OpenMVG
#ifdef MMSOLVER_USE_OPENMVG

#include <openMVG/cameras/Camera_Pinhole.hpp>
#include <openMVG/cameras/Camera_Intrinsics.hpp>
#include <openMVG/features/feature.hpp>
#include <openMVG/features/feature_container.hpp>
#include <openMVG/geometry/pose3.hpp>
#include <openMVG/matching/indMatch.hpp>
#include <openMVG/matching/indMatchDecoratorXY.hpp>
#include <openMVG/matching/regions_matcher.hpp>
#include <openMVG/multiview/triangulation.hpp>
#include <openMVG/multiview/motion_from_essential.hpp>
#include <openMVG/multiview/solver_essential_eight_point.hpp>
#include <openMVG/multiview/solver_essential_kernel.hpp>
#include <openMVG/multiview/solver_fundamental_kernel.hpp>
#include <openMVG/multiview/conditioning.hpp>
#include <openMVG/numeric/eigen_alias_definition.hpp>
#include <openMVG/numeric/numeric.h>
#include <openMVG/sfm/sfm_data.hpp>
#include <openMVG/sfm/sfm_data_BA.hpp>
#include <openMVG/sfm/sfm_data_BA_ceres.hpp>
#include <openMVG/sfm/sfm_data_io.hpp>
#include <openMVG/sfm/pipelines/sfm_robust_model_estimation.hpp>
#include <openMVG/robust_estimation/robust_estimator_ACRansac.hpp>
#include <openMVG/robust_estimation/robust_estimator_ACRansacKernelAdaptator.hpp>
#include <openMVG/types.hpp>

#endif  // MMSOLVER_USE_OPENMVG

// Maya
#include <maya/MTypes.h>
#include <maya/MSyntax.h>
#include <maya/MArgList.h>
#include <maya/MArgDatabase.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MPlugArray.h>
#include <maya/MTime.h>
#include <maya/MTimeArray.h>
#include <maya/MMatrix.h>
#include <maya/MMatrixArray.h>
#include <maya/MDagPath.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MFnDagNode.h>
#include <maya/MItSelectionList.h>
#include <maya/MTransformationMatrix.h>
#include <maya/MEulerRotation.h>


// Internal
#include "mmSolver/adjust/adjust_defines.h"
#include "mmSolver/mayahelper/maya_attr.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_marker.h"
#include "mmSolver/mayahelper/maya_bundle.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/number_utils.h"

// TODO: Add these flags to the command to allow querying two different cameras.
#define CAMERA_A_SHORT_FLAG "-ca"
#define CAMERA_A_LONG_FLAG "-cameraA"

#define CAMERA_B_SHORT_FLAG "-cb"
#define CAMERA_B_LONG_FLAG "-cameraB"

#define FRAME_A_SHORT_FLAG "-fa"
#define FRAME_A_LONG_FLAG "-frameA"

#define FRAME_B_SHORT_FLAG "-fb"
#define FRAME_B_LONG_FLAG "-frameB"

#define MARKER_BUNDLE_SHORT_FLAG "-mb"
#define MARKER_BUNDLE_LONG_FLAG "-markerBundle"

namespace mmsolver {

using KernelType =
    openMVG::robust::ACKernelAdaptor<
    openMVG::fundamental::kernel::NormalizedEightPointKernel,
    openMVG::fundamental::kernel::SymmetricEpipolarDistanceError,
    openMVG::UnnormalizerT,
    openMVG::Mat3>;

bool get_marker_coords(
    const MTime &time,
    MarkerPtr &mkr,
    double &x,
    double &y,
    double &weight,
    bool &enable) {
    auto timeEvalMode = TIME_EVAL_MODE_DG_CONTEXT;

    mkr->getPosXY(x, y, time, timeEvalMode);
    mkr->getEnable(enable, time, timeEvalMode);
    mkr->getWeight(weight, time, timeEvalMode);

    weight *= static_cast<double>(enable);
    return weight > 0;
}

MStatus get_camera_values(
    const MTime &time,
    CameraPtr &cam,
    int &image_width,
    int &image_height,
    double &focal_length_mm,
    double &sensor_width_mm,
    double &sensor_height_mm) {
    MStatus status = MStatus::kSuccess;

    auto timeEvalMode = TIME_EVAL_MODE_DG_CONTEXT;

    auto filmBackWidth_inch = cam->getFilmbackWidthValue(time, timeEvalMode);
    auto filmBackHeight_inch = cam->getFilmbackHeightValue(time, timeEvalMode);
    sensor_width_mm = filmBackWidth_inch * INCH_TO_MM;
    sensor_height_mm = filmBackHeight_inch * INCH_TO_MM;

    focal_length_mm = cam->getFocalLengthValue(time, timeEvalMode);

    image_width = static_cast<int>(sensor_width_mm * 1000.0);
    image_height = static_cast<int>(sensor_height_mm * 1000.0);

    return status;
}



bool myRobustRelativePose
(
    const openMVG::cameras::IntrinsicBase *intrinsics1,
    const openMVG::cameras::IntrinsicBase *intrinsics2,
    const openMVG::Mat &x1,
    const openMVG::Mat &x2,
    openMVG::sfm::RelativePose_Info &relativePose_info,
    const std::pair<size_t, size_t> &size_ima1,
    const std::pair<size_t, size_t> &size_ima2,
    const size_t max_iteration_count) {
    if (!intrinsics1 || !intrinsics2) {
        return false;
    }

    // MMSOLVER_INFO("=== 1");
    // std::this_thread::sleep_for(std::chrono::milliseconds(10));

    // Compute the bearing vectors
    const openMVG::Mat3X
        bearing1 = (*intrinsics1)(x1),
        bearing2 = (*intrinsics2)(x2);

    // MMSOLVER_INFO("=== 2");
    // std::this_thread::sleep_for(std::chrono::milliseconds(10));

    auto pinhole_cameras_only = isPinhole(intrinsics1->getType())
        && isPinhole(intrinsics2->getType());
    auto more_than_five = x1.cols() > 5;
    auto more_than_eight = x1.cols() > 8;

    if (more_than_eight) {
        // MMSOLVER_INFO("=== 7");
        // std::this_thread::sleep_for(std::chrono::milliseconds(10));

        // Define the AContrario adaptor to use the 8 point essential matrix solver.
        typedef openMVG::robust::ACKernelAdaptor_AngularRadianError <
            openMVG::EightPointRelativePoseSolver,
            openMVG::AngularError,
            openMVG::Mat3>
            KernelType;

        KernelType kernel(bearing1, bearing2);

        // Robustly estimate the Essential matrix with A Contrario ransac
        const double upper_bound_precision =
            (relativePose_info.initial_residual_tolerance ==
             std::numeric_limits<double>::infinity()) ?
            std::numeric_limits<double>::infinity()
            : openMVG::D2R(
                relativePose_info.initial_residual_tolerance);
        const auto ac_ransac_output =
            openMVG::robust::ACRANSAC(kernel, relativePose_info.vec_inliers,
                                      max_iteration_count,
                                      &relativePose_info.essential_matrix,
                                      upper_bound_precision, false);
        MMSOLVER_INFO("=== 8");

        const double &threshold = ac_ransac_output.first;
        relativePose_info.found_residual_precision = openMVG::R2D(
            threshold); // Degree

        // auto minimum_samples = KernelType::Solver::MINIMUM_SAMPLES * 2.5;
        auto minimum_samples = KernelType::Solver::MINIMUM_SAMPLES;
        if (relativePose_info.vec_inliers.size() < minimum_samples) {
            MMSOLVER_INFO("=== 9");
            return false; // no sufficient coverage (the model does not support enough samples)
        }
    } else if (more_than_five && pinhole_cameras_only) {
        // Five Point Solver only supports pinhole cameras.

        // MMSOLVER_INFO("=== 3");
        // std::this_thread::sleep_for(std::chrono::milliseconds(10));

        // Define the AContrario adaptor to use the 5 point essential matrix solver.
        using KernelType = openMVG::robust::ACKernelAdaptorEssential<
            openMVG::essential::kernel::FivePointSolver,
            openMVG::fundamental::kernel::EpipolarDistanceError,
            openMVG::Mat3>;
        KernelType kernel(x1, bearing1, size_ima1.first, size_ima1.second,
                          x2, bearing2, size_ima2.first, size_ima2.second,
                          dynamic_cast<const openMVG::cameras::Pinhole_Intrinsic *>(intrinsics1)->K(),
                          dynamic_cast<const openMVG::cameras::Pinhole_Intrinsic *>(intrinsics2)->K());

        // MMSOLVER_INFO("=== 4");
        // std::this_thread::sleep_for(std::chrono::milliseconds(10));

        // Robustly estimation of the Model and its precision
        const auto ac_ransac_output = openMVG::robust::ACRANSAC(
            kernel, relativePose_info.vec_inliers,
            max_iteration_count, &relativePose_info.essential_matrix,
            relativePose_info.initial_residual_tolerance, false);

        // MMSOLVER_INFO("=== 5");
        // std::this_thread::sleep_for(std::chrono::milliseconds(10));

        relativePose_info.found_residual_precision = ac_ransac_output.first;

        // auto minimum_samples = KernelType::Solver::MINIMUM_SAMPLES * 2.5;
        auto minimum_samples = KernelType::Solver::MINIMUM_SAMPLES;
        if (relativePose_info.vec_inliers.size() < minimum_samples) {

            // MMSOLVER_INFO("=== 6");
            // std::this_thread::sleep_for(std::chrono::milliseconds(10));

            return false; // no sufficient coverage (the model does not support enough samples)
        }
    }

    // MMSOLVER_INFO("=== 10");
    // std::this_thread::sleep_for(std::chrono::milliseconds(10));


    // estimation of the relative poses based on the cheirality test
    openMVG::geometry::Pose3 relative_pose;
    if (!openMVG::RelativePoseFromEssential(
            bearing1,
            bearing2,
            relativePose_info.essential_matrix,
            relativePose_info.vec_inliers, &relative_pose)) {
        return false;
    }

    // MMSOLVER_INFO("=== 11");
    // std::this_thread::sleep_for(std::chrono::milliseconds(10));

    relativePose_info.relativePose = relative_pose;
    return true;
}


void convert_camera_lens_mm_to_pixel_units(
    const int32_t image_width,
    const int32_t image_height,
    const double focal_length_mm,
    const double sensor_width_mm,
    double &focal_length_pix,
    double &ppx_pix,
    double &ppy_pix) {
    focal_length_pix = focal_length_mm / sensor_width_mm;
    focal_length_pix *= static_cast<double>(image_width);
    ppx_pix = static_cast<double>(image_width) * 0.5;
    ppy_pix = static_cast<double>(image_height) * 0.5;
    return;
}

// Prepare the corresponding 2D marker data.
openMVG::Mat convert_marker_coords_to_matrix(
    const std::vector<std::pair<double, double>> &marker_coords) {
    auto num = marker_coords.size();
    openMVG::Mat result(2, num);
    for (size_t k = 0; k < num; ++k) {
        auto coord = marker_coords[k];
        result.col(k) =
            openMVG::Vec2(std::get<0>(coord),
                          std::get<1>(coord));
    }
    return result;
}

bool compute_relative_pose(
    const int32_t image_width_a,
    const int32_t image_width_b,
    const int32_t image_height_a,
    const int32_t image_height_b,
    const double focal_length_pix_a,
    const double focal_length_pix_b,
    const double ppx_pix_a,
    const double ppx_pix_b,
    const double ppy_pix_a,
    const double ppy_pix_b,
    const std::vector<std::pair<double, double>> &marker_coords_a,
    const std::vector<std::pair<double, double>> &marker_coords_b,
    const MarkerPtrList &marker_list_a,
    const MarkerPtrList &marker_list_b,
    openMVG::sfm::RelativePose_Info &pose_info) {

    MMSOLVER_INFO("B ---");
    std::this_thread::sleep_for(std::chrono::milliseconds(10));
    const openMVG::cameras::Pinhole_Intrinsic cam_a(
        image_width_a,
        image_height_a,
        focal_length_pix_a,
        ppx_pix_a,
        ppy_pix_a);
    const openMVG::cameras::Pinhole_Intrinsic cam_b(
        image_width_b,
        image_height_b,
        focal_length_pix_b,
        ppx_pix_b,
        ppy_pix_b);

    MMSOLVER_INFO("C ---");
    std::this_thread::sleep_for(std::chrono::milliseconds(10));

    openMVG::Mat marker_coords_matrix_a =
        convert_marker_coords_to_matrix(marker_coords_a);
    openMVG::Mat marker_coords_matrix_b =
        convert_marker_coords_to_matrix(marker_coords_b);

    MMSOLVER_INFO("D ---");
    std::this_thread::sleep_for(std::chrono::milliseconds(10));

    // Compute the relative pose thanks to an essential matrix
    // estimation.
    const std::pair<size_t, size_t> image_size_a(
        static_cast<size_t>(image_width_a),
        static_cast<size_t>(image_height_a));
    const std::pair<size_t, size_t> image_size_b(
        static_cast<size_t>(image_width_b),
        static_cast<size_t>(image_height_b));
    auto num_max_iter = 4096;
    bool robust_pose_ok = myRobustRelativePose(
        &cam_a, &cam_b,
        marker_coords_matrix_a,
        marker_coords_matrix_b,
        pose_info,
        image_size_a,
        image_size_b,
        num_max_iter);
    MMSOLVER_INFO("D2 ---");
    std::this_thread::sleep_for(std::chrono::milliseconds(10));
    if (!robust_pose_ok) {
        MMSOLVER_ERR("Robust relative pose estimation failure.");
        return false;
    }
    std::this_thread::sleep_for(std::chrono::milliseconds(10));
    MMSOLVER_INFO("Found an Essential matrix:");
    MMSOLVER_INFO("- precision: " << pose_info.found_residual_precision << " pixels");

    MMSOLVER_INFO("- #matches: " << marker_coords_matrix_a.size());
    for (auto i = 0; i < marker_coords_matrix_a.size(); i++ ) {
        auto coord_x_a = marker_coords_matrix_a.col(i)[0];
        auto coord_y_a = marker_coords_matrix_a.col(i)[1];
        auto coord_x_b = marker_coords_matrix_b.col(i)[0];
        auto coord_y_b = marker_coords_matrix_b.col(i)[1];
        MMSOLVER_INFO(
            "  - #match: "
            << i << " = "
            << coord_x_a << "," << coord_y_a
            << " <-> "
            << coord_x_b << "," << coord_y_b);
    }

    MMSOLVER_INFO("- m_marker_list_a size: " << marker_list_a.size());
    MMSOLVER_INFO("- m_marker_list_b size: " << marker_list_b.size());
    MMSOLVER_INFO("- #inliers: " << pose_info.vec_inliers.size());
    auto i = 0;
    for (auto inlier : pose_info.vec_inliers) {
        if (inlier < marker_list_a.size()) {
            auto mkr_a = marker_list_a[inlier];
            auto mkr_b = marker_list_b[inlier];
            auto mkr_name_a = mkr_a->getNodeName();
            auto mkr_name_b = mkr_b->getNodeName();
            MMSOLVER_INFO(
                "  - #inlier A: "
                << i << " = " << inlier << " mkr: " << mkr_name_a.asChar());
            MMSOLVER_INFO(
                "  - #inlier B: "
                << i << " = " << inlier << " mkr: " << mkr_name_b.asChar());
        }
        ++i;
    }

    MMSOLVER_INFO("- Translation: " << pose_info.relativePose.translation());
    MMSOLVER_INFO("- Rotation: " << pose_info.relativePose.rotation());
    std::this_thread::sleep_for(std::chrono::milliseconds(10));
    return true;
}

bool construct_two_camera_sfm_data_scene(
    const int32_t image_width_a,
    const int32_t image_width_b,
    const int32_t image_height_a,
    const int32_t image_height_b,
    const double focal_length_pix_a,
    const double focal_length_pix_b,
    const double ppx_pix_a,
    const double ppx_pix_b,
    const double ppy_pix_a,
    const double ppy_pix_b,
    const openMVG::sfm::RelativePose_Info &pose_info,
    openMVG::sfm::SfM_Data &scene) {
    auto image_width_size_a = static_cast<size_t>(image_width_a);
    auto image_width_size_b = static_cast<size_t>(image_width_b);
    auto image_height_size_a = static_cast<size_t>(image_height_a);
    auto image_height_size_b = static_cast<size_t>(image_height_b);

    // Setup a SfM scene with two view corresponding the pictures
    MMSOLVER_INFO("E ---");
    std::this_thread::sleep_for(std::chrono::milliseconds(10));
    scene.views[0].reset(
        new openMVG::sfm::View(
            /*imgPath=*/ "",
            /*view_id=*/ 0,
            /*intrinsic_id=*/ 0,
            /*pose_id=*/ 0,
            image_width_size_a,
            image_height_size_a)
    );
    scene.views[1].reset(
        new openMVG::sfm::View(
            /*imgPath=*/ "",
            /*view_id=*/ 1,
            /*intrinsic_id=*/ 1,
            /*pose_id=*/ 1,
            image_width_size_b,
            image_height_size_b)
    );

    // Setup intrinsics camera data
    // Each view use it's own pinhole camera intrinsic
    MMSOLVER_INFO("F ---");
    std::this_thread::sleep_for(std::chrono::milliseconds(10));
    scene.intrinsics[0].reset(
        new openMVG::cameras::Pinhole_Intrinsic(
            image_width_a,
            image_height_a,
            focal_length_pix_a,
            ppx_pix_a, ppy_pix_a));
    scene.intrinsics[1].reset(
        new openMVG::cameras::Pinhole_Intrinsic(
            image_width_b,
            image_height_b,
            focal_length_pix_b,
            ppx_pix_b, ppy_pix_b));

    // Setup poses camera data
    MMSOLVER_INFO("G ---");
    std::this_thread::sleep_for(std::chrono::milliseconds(10));
    auto pose_a = openMVG::geometry::Pose3(
        openMVG::Mat3::Identity(),
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
    const MarkerPtrList &marker_list_a,
    const MarkerPtrList &marker_list_b,
    BundlePtrList &bundle_list,
    openMVG::sfm::SfM_Data &scene) {
    auto num = 0;
    openMVG::sfm::Landmarks &landmarks = scene.structure;
    openMVG::geometry::Pose3 pose_a = scene.poses[scene.views[0]->id_pose];
    openMVG::geometry::Pose3 pose_b = scene.poses[scene.views[1]->id_pose];
    for (const auto inlier_idx : vec_inliers) {
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
        MMSOLVER_INFO("triangulate inlier_idx: " << inlier_idx);

        auto coord_a = marker_coords_a[inlier_idx];
        auto coord_b = marker_coords_b[inlier_idx];
        auto coord_x_a = std::get<0>(coord_a);
        auto coord_y_a = std::get<1>(coord_a);
        auto coord_x_b = std::get<0>(coord_b);
        auto coord_y_b = std::get<1>(coord_b);

        const auto feature_a = openMVG::features::SIOPointFeature(coord_x_a,
                                                                  coord_y_a);
        const auto feature_b = openMVG::features::SIOPointFeature(coord_x_b,
                                                                  coord_y_b);
        const auto feature_coord_a = feature_a.coords().cast<double>();
        const auto feature_coord_b = feature_b.coords().cast<double>();

        // Point triangulation
        openMVG::Vec3 bundle_pos;
        const auto triangulation_method = openMVG::ETriangulationMethod::DEFAULT;
        auto triangulate_ok = openMVG::Triangulate2View(
            pose_a.rotation(),
            pose_a.translation(),
            (*scene.intrinsics[0])(feature_coord_a),
            pose_b.rotation(),
            pose_b.translation(),
            (*scene.intrinsics[1])(feature_coord_b),
            bundle_pos,
            triangulation_method);
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
            landmarks.insert({landmarks.size(), landmark});

            auto mkr_a = marker_list_a[inlier_idx];
            auto mkr_b = marker_list_b[inlier_idx];
            auto bnd = bundle_list[inlier_idx];
            auto mkr_name_a = mkr_a->getNodeName();
            auto mkr_name_b = mkr_b->getNodeName();
            auto bnd_name = bnd->getNodeName();
            MMSOLVER_INFO("triangulated Marker A: " << mkr_name_a.asChar());
            MMSOLVER_INFO("triangulated Marker B: " << mkr_name_b.asChar());
            MMSOLVER_INFO("triangulated bundle: " << bnd_name.asChar());
            num++;
        }
    }
    return num > 0;
}

bool bundle_adjustment(openMVG::sfm::SfM_Data &scene) {
    // Perform Bundle Adjustment of the scene.
    //
    // TODO: Add "openMVG::sfm::Control_Point_Parameter" to allow
    // locked bundles.
    //
    auto optimize_options =
        openMVG::sfm::Optimize_Options(
            openMVG::cameras::Intrinsic_Parameter_Type::ADJUST_ALL,
            openMVG::sfm::Extrinsic_Parameter_Type::ADJUST_ALL,
            openMVG::sfm::Structure_Parameter_Type::ADJUST_ALL);
    // TODO: use 'optimize_options.control_point_opt.bUse_control_points'
    auto bundle_adjust_verbose = true;
    auto bundle_adjust_multithreaded = false;
    auto ceres_options = openMVG::sfm::Bundle_Adjustment_Ceres::BA_Ceres_options(
        bundle_adjust_verbose,
        bundle_adjust_multithreaded);
    ceres_options.bCeres_summary_ = true;
    ceres_options.bUse_loss_function_ = false;
    MMSOLVER_INFO("ceres_options.bCeres_summary_: "
         << ceres_options.bCeres_summary_);
    MMSOLVER_INFO("ceres_options.linear_solver_type_: "
         << ceres_options.linear_solver_type_);
    MMSOLVER_INFO("ceres_options.preconditioner_type_: "
         << ceres_options.preconditioner_type_);
    MMSOLVER_INFO("ceres_options.sparse_linear_algebra_library_type_: "
         << ceres_options.sparse_linear_algebra_library_type_);
    MMSOLVER_INFO("ceres_options.bUse_loss_function_: "
         << ceres_options.bUse_loss_function_);
    std::this_thread::sleep_for(std::chrono::milliseconds(10));
    openMVG::sfm::Bundle_Adjustment_Ceres bundle_adjustment(ceres_options);
    return bundle_adjustment.Adjust(
        scene,
        optimize_options);
}

MStatus parseCameraSelectionList(
    const MSelectionList &selection_list,
    const MTime &time,
    CameraPtr &camera,
    Attr &camera_tx_attr,
    Attr &camera_ty_attr,
    Attr &camera_tz_attr,
    Attr &camera_rx_attr,
    Attr &camera_ry_attr,
    Attr &camera_rz_attr,
    int32_t &image_width,
    int32_t &image_height,
    double &focal_length_mm,
    double &sensor_width_mm,
    double &sensor_height_mm
) {
    MMSOLVER_INFO("parseCameraSelectionList1");
    MStatus status = MStatus::kSuccess;

    MDagPath nodeDagPath;
    MObject node_obj;

    if (selection_list.length() > 0) {
        status = selection_list.getDagPath(0, nodeDagPath);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        status = selection_list.getDependNode(0, node_obj);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        MString transform_node_name = nodeDagPath.fullPathName();
        MMSOLVER_INFO("Camera name: " << transform_node_name.asChar());

        auto object_type = computeObjectType(node_obj, nodeDagPath);
        if (object_type == ObjectType::kCamera) {
            MMSOLVER_INFO("parseCameraSelectionList2");
            status = nodeDagPath.extendToShapeDirectlyBelow(0);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            MString shape_node_name = nodeDagPath.fullPathName();

            MMSOLVER_INFO("parseCameraSelectionList3");
            camera = CameraPtr(new Camera());
            camera->setTransformNodeName(transform_node_name);
            camera->setShapeNodeName(shape_node_name);

            MMSOLVER_INFO("parseCameraSelectionList4");
            camera_tx_attr.setNodeName(transform_node_name);
            camera_ty_attr.setNodeName(transform_node_name);
            camera_tz_attr.setNodeName(transform_node_name);
            camera_rx_attr.setNodeName(transform_node_name);
            camera_ry_attr.setNodeName(transform_node_name);
            camera_rz_attr.setNodeName(transform_node_name);

            MMSOLVER_INFO("parseCameraSelectionList5");
            camera_tx_attr.setAttrName(MString("translateX"));
            camera_ty_attr.setAttrName(MString("translateY"));
            camera_tz_attr.setAttrName(MString("translateZ"));
            camera_rx_attr.setAttrName(MString("rotateX"));
            camera_ry_attr.setAttrName(MString("rotateY"));
            camera_rz_attr.setAttrName(MString("rotateZ"));

            MMSOLVER_INFO("parseCameraSelectionList6");
            status = get_camera_values(
                time,
                camera,
                image_width,
                image_height,
                focal_length_mm,
                sensor_width_mm,
                sensor_height_mm);
            CHECK_MSTATUS_AND_RETURN_IT(status);
        } else {
            MMSOLVER_ERR(
                "Given node is not a valid camera: "
                << transform_node_name.asChar());
            status = MS::kFailure;
            return status;
        }
    }

    MMSOLVER_INFO("parseCameraSelectionList7");
    return status;
}


MStatus addMarkerBundles(
    const MTime &time_a,
    const MTime &time_b,
    const int32_t image_width_a,
    const int32_t image_height_a,
    const int32_t image_width_b,
    const int32_t image_height_b,
    MarkerPtr &marker_a,
    MarkerPtr &marker_b,
    BundlePtr &bundle,
    BundlePtrList &bundle_list,
    MarkerPtrList &marker_list_a,
    MarkerPtrList &marker_list_b,
    std::vector<std::pair<double, double>> &marker_coords_a,
    std::vector<std::pair<double, double>> &marker_coords_b
) {
    MMSOLVER_INFO("addMarkerBundle1");
    MStatus status = MStatus::kSuccess;

    double x_a = 0.0;
    double x_b = 0.0;
    double y_a = 0.0;
    double y_b = 0.0;
    bool enable_a = true;
    bool enable_b = true;
    double weight_a = 1.0;
    double weight_b = 1.0;

    auto success_a = get_marker_coords(
        time_a, marker_a,
        x_a, y_a,
        weight_a, enable_a);
    MMSOLVER_INFO("addMarkerBundle2");
    auto success_b = get_marker_coords(
        time_b, marker_b,
        x_b, y_b,
        weight_b, enable_b);
    MMSOLVER_INFO("addMarkerBundle3");
    if (success_a && success_b) {
        MMSOLVER_INFO("addMarkerBundle4");
        double xx_a =
            (x_a + 0.5) * static_cast<double>(image_width_a);
        double yy_a =
            (y_a + 0.5) * static_cast<double>(image_height_a);
        double xx_b =
            (x_b + 0.5) * static_cast<double>(image_width_b);
        double yy_b =
            (y_b + 0.5) * static_cast<double>(image_height_b);
        MMSOLVER_INFO("x_a : " << x_a << " y_a : " << y_a);
        MMSOLVER_INFO("xx_a: " << xx_a << " yy_a: " << yy_a);
        MMSOLVER_INFO("x_b : " << x_b << " y_b : " << y_b);
        MMSOLVER_INFO("xx_b: " << xx_b << " yy_b: " << yy_b);
        auto xy_a = std::pair<double, double>{xx_a, yy_a};
        auto xy_b = std::pair<double, double>{xx_b, yy_b};
        MMSOLVER_INFO("addMarkerBundle5");
        marker_coords_a.push_back(xy_a);
        marker_coords_b.push_back(xy_b);

        MMSOLVER_INFO("addMarkerBundle6");
        marker_list_a.push_back(marker_a);
        marker_list_b.push_back(marker_b);
        bundle_list.push_back(bundle);
    }

    MMSOLVER_INFO("addMarkerBundle7");
    return status;
}


MMCameraRelativePoseCmd::~MMCameraRelativePoseCmd() {}

void *MMCameraRelativePoseCmd::creator() {
    return new MMCameraRelativePoseCmd();
}

MString MMCameraRelativePoseCmd::cmdName() {
    return MString("mmCameraRelativePose");
}

/*
 * Tell Maya we have a syntax function.
 */
bool MMCameraRelativePoseCmd::hasSyntax() const {
    return true;
}

bool MMCameraRelativePoseCmd::isUndoable() const {
    return true;
}

/*
 * Add flags to the command syntax
 */
MSyntax MMCameraRelativePoseCmd::newSyntax() {
    MStatus status = MStatus::kSuccess;

    MSyntax syntax;
    syntax.enableQuery(false);
    syntax.enableEdit(false);

    CHECK_MSTATUS(
        syntax.addFlag(
            CAMERA_A_SHORT_FLAG,
            CAMERA_A_LONG_FLAG,
            MSyntax::kSelectionItem));
    CHECK_MSTATUS(
        syntax.addFlag(
            CAMERA_B_SHORT_FLAG,
            CAMERA_B_LONG_FLAG,
            MSyntax::kSelectionItem));

    CHECK_MSTATUS(
        syntax.addFlag(
            FRAME_A_SHORT_FLAG,
            FRAME_A_LONG_FLAG,
            MSyntax::kUnsigned));
    CHECK_MSTATUS(
        syntax.addFlag(
            FRAME_B_SHORT_FLAG,
            FRAME_B_LONG_FLAG,
            MSyntax::kUnsigned));

    CHECK_MSTATUS(
        syntax.addFlag(
            MARKER_BUNDLE_SHORT_FLAG,
            MARKER_BUNDLE_LONG_FLAG,
            MSyntax::kString, MSyntax::kString, MSyntax::kString));
    CHECK_MSTATUS(syntax.makeFlagMultiUse(MARKER_BUNDLE_SHORT_FLAG));

    return syntax;
}

/*
 * Parse command line arguments
 */
MStatus MMCameraRelativePoseCmd::parseArgs(const MArgList &args) {
    MStatus status = MStatus::kSuccess;

    MArgDatabase argData(syntax(), args, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    // Reset saved data structures.
    m_marker_list_a.clear();
    m_marker_list_b.clear();
    m_bundle_list.clear();
    m_marker_coords_a.clear();
    m_marker_coords_b.clear();
    m_image_width_a = 1;
    m_image_height_a = 1;
    m_image_width_b = 1;
    m_image_height_b = 1;
    m_focal_length_mm_a = 35.0;
    m_focal_length_mm_b = 35.0;
    m_sensor_width_mm_a = 36.0;
    m_sensor_width_mm_b = 36.0;
    m_sensor_height_mm_a = 24.0;
    m_sensor_height_mm_b = 24.0;

    m_frame_a = 1;
    if (argData.isFlagSet(FRAME_A_SHORT_FLAG)) {
        status = argData.getFlagArgument(FRAME_A_SHORT_FLAG, 0,
                                         m_frame_a);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    m_frame_b = 1;
    if (argData.isFlagSet(FRAME_B_SHORT_FLAG)) {
        status = argData.getFlagArgument(FRAME_B_SHORT_FLAG, 0, m_frame_b);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    auto uiUnit = MTime::uiUnit();
    auto frame_value_a = static_cast<double>(m_frame_a);
    auto frame_value_b = static_cast<double>(m_frame_b);
    m_time_a = MTime(frame_value_a, uiUnit);
    m_time_b = MTime(frame_value_b, uiUnit);

    MMSOLVER_INFO("run parseCameraSelectionList A");
    MSelectionList camera_selection_list_a;
    argData.getFlagArgument(CAMERA_A_SHORT_FLAG, 0, camera_selection_list_a);
    status = parseCameraSelectionList(
        camera_selection_list_a,
        m_time_a,
        m_camera_a,
        m_camera_tx_attr_a,
        m_camera_ty_attr_a,
        m_camera_tz_attr_a,
        m_camera_rx_attr_a,
        m_camera_ry_attr_a,
        m_camera_rz_attr_a,
        m_image_width_a,
        m_image_height_a,
        m_focal_length_mm_a,
        m_sensor_width_mm_a,
        m_sensor_height_mm_a);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    MMSOLVER_INFO("run parseCameraSelectionList B");
    MSelectionList camera_selection_list_b;
    argData.getFlagArgument(CAMERA_B_SHORT_FLAG, 0, camera_selection_list_b);
    status = parseCameraSelectionList(
        camera_selection_list_b,
        m_time_b,
        m_camera_b,
        m_camera_tx_attr_b,
        m_camera_ty_attr_b,
        m_camera_tz_attr_b,
        m_camera_rx_attr_b,
        m_camera_ry_attr_b,
        m_camera_rz_attr_b,
        m_image_width_b,
        m_image_height_b,
        m_focal_length_mm_b,
        m_sensor_width_mm_b,
        m_sensor_height_mm_b);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    MMSOLVER_INFO("image A: " << m_image_width_a << "x" << m_image_height_a);
    MMSOLVER_INFO("image B: " << m_image_width_b << "x" << m_image_height_b);
    MMSOLVER_INFO("sensor (mm) A: " << m_sensor_width_mm_a
         << "x" << m_sensor_height_mm_a);
    MMSOLVER_INFO("sensor (mm) B: " << m_sensor_width_mm_b
         << "x" << m_sensor_height_mm_b);
    MMSOLVER_INFO("focal (mm) A: " << m_focal_length_mm_a);
    MMSOLVER_INFO("focal (mm) B: " << m_focal_length_mm_b);

    // Parse objects into Camera intrinsics and Tracking Markers.
    uint32_t numberOfMarkerBundleFlags = argData.numberOfFlagUses(MARKER_BUNDLE_SHORT_FLAG);
    MMSOLVER_INFO("numberOfMarkerBundleFlags: " << numberOfMarkerBundleFlags);
    if (numberOfMarkerBundleFlags > 0) {
        for (uint32_t i = 0; i < numberOfMarkerBundleFlags; ++i) {
            MMSOLVER_INFO("i: " << i);
            MArgList markerBundleArgs;
            ObjectType objectType = ObjectType::kUnknown;
            MDagPath dagPath;
            MString markerNameA = "";
            MString markerNameB = "";
            MString bundleName = "";
            MObject markerObject;
            MObject bundleObject;
            status = argData.getFlagArgumentList(MARKER_BUNDLE_SHORT_FLAG, i, markerBundleArgs);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            MMSOLVER_INFO("markerBundleArgs.length(): " << markerBundleArgs.length());
            if (markerBundleArgs.length() != 3) {
                MMSOLVER_ERR("Marker Bundle argument list must have 3 arguments; "
                             << "\"markerA\", \"markerB\",  \"bundle\".");
                continue;
            }

            markerNameA = markerBundleArgs.asString(0, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            status = getAsObject(markerNameA, markerObject);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            status = getAsDagPath(markerNameA, dagPath);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            objectType = computeObjectType(markerObject, dagPath);
            if (objectType != ObjectType::kMarker) {
                MMSOLVER_ERR("Given marker node is not a Marker; "
                    << markerNameA.asChar());
                continue;
            }
            MMSOLVER_INFO("Got markerNameA: " << markerNameA.asChar());

            markerNameB = markerBundleArgs.asString(1, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            status = getAsObject(markerNameB, markerObject);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            status = getAsDagPath(markerNameB, dagPath);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            objectType = computeObjectType(markerObject, dagPath);
            if (objectType != ObjectType::kMarker) {
                MMSOLVER_ERR("Given marker node is not a Marker; "
                    << markerNameB.asChar());
                continue;
            }
            MMSOLVER_INFO("Got markerNameB: " << markerNameB.asChar());

            bundleName = markerBundleArgs.asString(2, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            status = getAsObject(bundleName, bundleObject);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            status = getAsDagPath(bundleName, dagPath);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            objectType = computeObjectType(bundleObject, dagPath);
            if (objectType != ObjectType::kBundle) {
                MMSOLVER_ERR("Given bundle node is not a Bundle; "
                    << bundleName.asChar());
                continue;
            }
            MMSOLVER_INFO("Got bundleName: " << bundleName.asChar());

            BundlePtr bundle = BundlePtr(new Bundle());
            bundle->setNodeName(bundleName);

            MarkerPtr marker_a = MarkerPtr(new Marker());
            marker_a->setNodeName(markerNameA);
            marker_a->setBundle(bundle);
            marker_a->setCamera(m_camera_a);

            MarkerPtr marker_b = MarkerPtr(new Marker());
            marker_b->setNodeName(markerNameB);
            marker_b->setBundle(bundle);
            marker_b->setCamera(m_camera_b);

            MMSOLVER_INFO("run addMarkerBundles");
            addMarkerBundles(
                m_time_a,
                m_time_b,
                m_image_width_a,
                m_image_height_a,
                m_image_width_b,
                m_image_height_b,
                marker_a,
                marker_b,
                bundle,
                m_bundle_list,
                m_marker_list_a,
                m_marker_list_b,
                m_marker_coords_a,
                m_marker_coords_b
            );
        }
    }

    MMSOLVER_INFO("parse m_marker_list_a size: " << m_marker_list_a.size());
    MMSOLVER_INFO("parse m_marker_list_b size: " << m_marker_list_b.size());

    return status;
}

MStatus MMCameraRelativePoseCmd::doIt(const MArgList &args) {
    MStatus status = MStatus::kSuccess;

    // Read all the flag arguments.
    status = parseArgs(args);
    if (status == MStatus::kFailure) {
        return status;
    }

    // Command Outputs
    MDoubleArray outResult;

    // Essential geometry filtering of putative matches
    MMSOLVER_INFO("Compute Essential geometry...");
    std::this_thread::sleep_for(std::chrono::milliseconds(10));

    double focal_length_pix_a = 0.0;
    double focal_length_pix_b = 0.0;
    double ppx_pix_a = 0.0;
    double ppx_pix_b = 0.0;
    double ppy_pix_a = 0.0;
    double ppy_pix_b = 0.0;
    convert_camera_lens_mm_to_pixel_units(
        m_image_width_a,
        m_image_height_a,
        m_focal_length_mm_a,
        m_sensor_width_mm_a,
        focal_length_pix_a,
        ppx_pix_a,
        ppy_pix_a);
    convert_camera_lens_mm_to_pixel_units(
        m_image_width_b,
        m_image_height_b,
        m_focal_length_mm_b,
        m_sensor_width_mm_b,
        focal_length_pix_b,
        ppx_pix_b,
        ppy_pix_b);

    openMVG::sfm::RelativePose_Info pose_info;
    auto relative_pose_ok = compute_relative_pose(
        m_image_width_a,
        m_image_width_b,
        m_image_height_a,
        m_image_height_b,
        focal_length_pix_a,
        focal_length_pix_b,
        ppx_pix_a,
        ppx_pix_b,
        ppy_pix_a,
        ppy_pix_b,
        m_marker_coords_a,
        m_marker_coords_b,
        m_marker_list_a,
        m_marker_list_b,
        pose_info);
    if (!relative_pose_ok) {
        MMSOLVER_ERR("Compute Relative pose failed.");
        status = MS::kFailure;
        return status;
    }

    openMVG::sfm::SfM_Data scene;
    auto sfm_data_ok = construct_two_camera_sfm_data_scene(
        m_image_width_a,
        m_image_width_b,
        m_image_height_a,
        m_image_height_b,
        focal_length_pix_a,
        focal_length_pix_b,
        ppx_pix_a,
        ppx_pix_b,
        ppy_pix_a,
        ppy_pix_b,
        pose_info,
        scene);
    if (!sfm_data_ok) {
        MMSOLVER_ERR("Failed to construct two camera SfM scene.");
        status = MS::kFailure;
        return status;
    }

    // Triangulate and check valid points. Invalid points that do not
    // work are discarded (removed from the list of inliers).
    //
    // Init structure by inlier triangulation
    MMSOLVER_INFO("H ---");
    std::this_thread::sleep_for(std::chrono::milliseconds(10));
    auto triangulate_ok = triangulate_relative_pose(
        m_marker_coords_a,
        m_marker_coords_b,
        pose_info.vec_inliers,
        m_marker_list_a,
        m_marker_list_b,
        m_bundle_list,
        scene);
    if (!triangulate_ok) {
        MMSOLVER_ERR("Triangulate relative pose points failed.");
        status = MS::kFailure;
        return status;
    }

    MMSOLVER_INFO("I ---");
    std::this_thread::sleep_for(std::chrono::milliseconds(10));
    openMVG::sfm::Save(
        scene,
        "EssentialGeometry_before.json",
        openMVG::sfm::ESfM_Data(openMVG::sfm::ESfM_Data::ALL));

    MMSOLVER_INFO("J ---");
    std::this_thread::sleep_for(std::chrono::milliseconds(10));
    auto adjust_ok = bundle_adjustment(scene);
    if (!adjust_ok) {
        MMSOLVER_ERR("Bundle Adjustment failed.");
        status = MS::kFailure;
        return status;
    }

    MMSOLVER_INFO("K ---");
    std::this_thread::sleep_for(std::chrono::milliseconds(10));
    openMVG::sfm::Save(
        scene,
        "EssentialGeometry_after.json",
        openMVG::sfm::ESfM_Data(openMVG::sfm::ESfM_Data::ALL));

    // the conversion matrix from OpenGL default coordinate system
    //  to the camera coordinate system:
    //
    // [ 1  0  0  0] * [ x ] = [ x ]
    //   0 -1  0  0      y      -y
    //   0  0 -1  0      z      -z
    //   0  0  0  1      1       1
    // const double c_convert_matrix[4][4] = {
    //     {1.0,  0.0,  0.0, 0.0},
    //     {0.0, -1.0,  0.0, 0.0},
    //     {0.0,  0.0, -1.0, 0.0},
    //     {0.0,  0.0,  0.0, 1.0}};
    const double c_convert_matrix[4][4] = {
        {1.0,  0.0,  0.0, 0.0},
        {0.0,  1.0,  0.0, 0.0},
        {0.0,  0.0,  1.0, 0.0},
        {0.0,  0.0,  0.0, 1.0}};
    MMatrix maya_convert_matrix(c_convert_matrix);

    // TODO: Convert the sfm_data back to Maya data and set Camera and
    // Bundles.
    auto views = scene.GetViews();
    auto poses = scene.GetPoses();
    auto intrinsics = scene.GetIntrinsics();
    for (auto it : views) {
        auto key = it.first;
        auto view = *it.second;
        auto pose_id = view.id_pose;
        MMSOLVER_INFO("view: " << key << "=" << pose_id);

        auto pose = scene.GetPoseOrDie(&view);
        auto pose_translation = pose.translation();
        auto pose_rotation = pose.rotation();
        MMSOLVER_INFO("pose translation: " << pose_translation);
        MMSOLVER_INFO("pose rotation: " << pose_rotation);

        MPoint maya_translate(
            pose_translation[0],
            pose_translation[1],
            pose_translation[2]);

        // const double c_rotate_matrix[4][4] = {
        //     {pose_rotation(0, 0),  pose_rotation(0, 1), pose_rotation(0, 2), pose_rotation(0, 3)},
        //     {pose_rotation(1, 0),  pose_rotation(1, 1), pose_rotation(1, 2), pose_rotation(1, 3)},
        //     {pose_rotation(2, 0),  pose_rotation(2, 1), pose_rotation(2, 2), pose_rotation(2, 3)},
        //     {pose_rotation(3, 0),  pose_rotation(3, 1), pose_rotation(3, 2), pose_rotation(3, 3)},
        // };

        const double c_rotate_matrix[4][4] = {
            {pose_rotation(0, 0),  pose_rotation(1, 0), pose_rotation(2, 0), pose_rotation(3, 0)},
            {pose_rotation(0, 1),  pose_rotation(1, 1), pose_rotation(2, 1), pose_rotation(3, 1)},
            {pose_rotation(0, 2),  pose_rotation(1, 2), pose_rotation(2, 2), pose_rotation(3, 2)},
            {pose_rotation(0, 3),  pose_rotation(1, 3), pose_rotation(2, 3), pose_rotation(3, 3)},
        };
        // auto maya_rotate_matrix = MMatrix(c_rotate_matrix).inverse();
        MMatrix maya_rotate_matrix(c_rotate_matrix);

        maya_rotate_matrix = maya_rotate_matrix * maya_convert_matrix;
        maya_translate = maya_translate * maya_convert_matrix;

        // TODO: Expose the Rotation Order, so we can match the camera
        // that needs it.
        auto rotate_order = MEulerRotation::kZXY; // kXYZ
        auto value_time = m_time_b;
        // auto rotate_order = m_camera_b_rotate_order;
        if (pose_id == 0) {
            // rotate_order = m_camera_a_rotate_order;
            value_time = m_time_a;
        }

        auto euler_rotation = MEulerRotation::decompose(
            maya_rotate_matrix,
            rotate_order);
        auto rx = euler_rotation.x * RADIANS_TO_DEGREES;
        auto ry = euler_rotation.y * RADIANS_TO_DEGREES;
        auto rz = euler_rotation.z * RADIANS_TO_DEGREES;
        MMSOLVER_INFO("pose euler rotation (ZXY): " << rx << "," << ry << "," << rz);

        m_camera_tx_attr_a.setValue(maya_translate.x, value_time, m_dgmod, m_curveChange);
        m_camera_ty_attr_a.setValue(maya_translate.y, value_time, m_dgmod, m_curveChange);
        m_camera_tz_attr_a.setValue(maya_translate.z, value_time, m_dgmod, m_curveChange);

        m_camera_rx_attr_a.setValue(rx, value_time, m_dgmod, m_curveChange);
        m_camera_ry_attr_a.setValue(ry, value_time, m_dgmod, m_curveChange);
        m_camera_rz_attr_a.setValue(rz, value_time, m_dgmod, m_curveChange);
    }

    auto attr_tx = Attr();
    auto attr_ty = Attr();
    auto attr_tz = Attr();

    MMSOLVER_INFO("m_bundle_list size: " << m_bundle_list.size());

    std::this_thread::sleep_for(std::chrono::milliseconds(10));
    auto landmarks = scene.GetLandmarks();
    auto timeEvalMode = TIME_EVAL_MODE_DG_CONTEXT;
    auto i = 0;
    for (auto it : landmarks) {
        auto key = it.first;
        auto landmark = it.second;
        auto pos = landmark.X;
        double tx = pos[0];
        double ty = pos[1];
        double tz = pos[2];
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
        MMSOLVER_INFO("landmark: " << key
                      << " x=" << tx << " y=" << ty << " z=" << tz);

        if (i < m_bundle_list.size()) {
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
            auto bnd = m_bundle_list[i];
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
            auto bnd_name = bnd->getNodeName();
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
            MMSOLVER_INFO("landmark bnd: " << bnd_name.asChar());

            attr_tx.setNodeName(bnd_name);
            attr_ty.setNodeName(bnd_name);
            attr_tz.setNodeName(bnd_name);

            attr_tx.setAttrName(MString("translateX"));
            attr_ty.setAttrName(MString("translateY"));
            attr_tz.setAttrName(MString("translateZ"));

            MPoint maya_translate(pos[0], pos[1], pos[2]);
            maya_translate = maya_translate * maya_convert_matrix;

            attr_tx.setValue(maya_translate.x, m_dgmod, m_curveChange);
            attr_ty.setValue(maya_translate.y, m_dgmod, m_curveChange);
            attr_tz.setValue(maya_translate.z, m_dgmod, m_curveChange);
        }

        ++i;
    }
    m_dgmod.doIt();

    MMCameraRelativePoseCmd::setResult(outResult);
    return status;
}

MStatus MMCameraRelativePoseCmd::redoIt() {
    MStatus status;
    m_dgmod.doIt();
    m_curveChange.redoIt();
    return status;
}

MStatus MMCameraRelativePoseCmd::undoIt() {
    MStatus status;
    m_curveChange.undoIt();
    m_dgmod.undoIt();
    return status;
}


} // namespace mmsolver
