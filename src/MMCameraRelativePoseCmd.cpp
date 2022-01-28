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

#include <chrono>
#include <thread>

// Internal
#include <MMCameraRelativePoseCmd.h>
#include "mayahelper/maya_utils.h"
#include "mayahelper/maya_camera.h"
#include "mayahelper/maya_marker.h"

using MMMarker = Marker;
using MMCamera = Camera;

// MM Solver Utils
#include "utilities/debug_utils.h"

// MM Solver Core
#include "adjust/adjust_defines.h"

// OpenMVG
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


// Maya
#include <maya/MSyntax.h>
#include <maya/MArgList.h>
#include <maya/MArgDatabase.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MTime.h>
#include <maya/MTimeArray.h>
#include <maya/MMatrix.h>
#include <maya/MMatrixArray.h>
#include <maya/MDagPath.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MItSelectionList.h>


#define START_FRAME_SHORT_FLAG "-sf"
#define START_FRAME_LONG_FLAG "-startFrame"
#define END_FRAME_SHORT_FLAG "-ef"
#define END_FRAME_LONG_FLAG "-endFrame"


using KernelType =
    openMVG::robust::ACKernelAdaptor<
    openMVG::fundamental::kernel::NormalizedEightPointKernel,
    openMVG::fundamental::kernel::SymmetricEpipolarDistanceError,
    openMVG::UnnormalizerT,
    openMVG::Mat3>;

bool get_marker_coords(
    const uint32_t frame_num,
    const MTime::Unit &uiUnit,
    MMMarker &mkr,
    double &x,
    double &y,
    double &weight,
    bool &enable) {
    auto timeEvalMode = TIME_EVAL_MODE_DG_CONTEXT;
    auto frame = static_cast<double>(frame_num);
    MTime time = MTime(frame, uiUnit);

    mkr.getPosXY(x, y, time, timeEvalMode);
    mkr.getEnable(enable, time, timeEvalMode);
    mkr.getWeight(weight, time, timeEvalMode);

    weight *= static_cast<double>(enable);
    return weight > 0;
}

bool get_camera_values(
    const uint32_t frame_num,
    const MTime::Unit &uiUnit,
    MMCamera &cam,
    int &image_width,
    int &image_height,
    double &focal_length_mm,
    double &sensor_width_mm,
    double &sensor_height_mm) {

    auto timeEvalMode = TIME_EVAL_MODE_DG_CONTEXT;
    auto frame = static_cast<double>(frame_num);
    MTime time = MTime(frame, uiUnit);

    auto filmBackWidth_inch = cam.getFilmbackWidthValue(time, timeEvalMode);
    auto filmBackHeight_inch = cam.getFilmbackHeightValue(time, timeEvalMode);
    sensor_width_mm = filmBackWidth_inch * 25.4;
    sensor_height_mm = filmBackHeight_inch * 25.4;

    focal_length_mm = cam.getFocalLengthValue(time, timeEvalMode);

    image_width = static_cast<int>(sensor_width_mm * 1000.0);
    image_height = static_cast<int>(sensor_height_mm * 1000.0);
    return true;
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
    return false;
}

/*
 * Add flags to the command syntax
 */
MSyntax MMCameraRelativePoseCmd::newSyntax() {
    MSyntax syntax;
    syntax.enableQuery(false);
    syntax.enableEdit(false);

    unsigned int minNumObjects = 0;
    syntax.setObjectType(MSyntax::kSelectionList, minNumObjects);

    syntax.addFlag(
        START_FRAME_SHORT_FLAG,
        START_FRAME_LONG_FLAG,
        MSyntax::kUnsigned);
    syntax.addFlag(
        END_FRAME_SHORT_FLAG,
        END_FRAME_LONG_FLAG,
        MSyntax::kUnsigned);

    return syntax;
}

/*
 * Parse command line arguments
 */
MStatus MMCameraRelativePoseCmd::parseArgs(const MArgList &args) {
    MStatus status = MStatus::kSuccess;

    MArgDatabase argData(syntax(), args, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    m_startFrame = 1;
    if (argData.isFlagSet(START_FRAME_SHORT_FLAG)) {
        status = argData.getFlagArgument(START_FRAME_SHORT_FLAG, 0,
                                         m_startFrame);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    m_endFrame = 120;
    if (argData.isFlagSet(END_FRAME_SHORT_FLAG)) {
        status = argData.getFlagArgument(END_FRAME_SHORT_FLAG, 0, m_endFrame);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    auto objects = MSelectionList();
    status = argData.getObjects(objects);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    auto uiUnit = MTime::uiUnit();

    // Reset saved data structures.
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

    MItSelectionList iter1(objects);
    for (; !iter1.isDone(); iter1.next()) {
        MDagPath nodeDagPath;
        MObject node_obj;

        status = iter1.getDagPath(nodeDagPath);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        status = iter1.getDependNode(node_obj);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        auto node_name = nodeDagPath.fullPathName();
        auto object_type = computeObjectType(node_obj, nodeDagPath);
        if (object_type == ObjectType::kCamera) {
            // Add Cameras
            MMSOLVER_INFO("Camera name: " << node_name.asChar());
            MString transform_node_name = nodeDagPath.fullPathName();

            status = nodeDagPath.extendToShapeDirectlyBelow(0);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            MString shape_node_name = nodeDagPath.fullPathName();

            auto cam = MMCamera();
            cam.setTransformNodeName(transform_node_name);
            cam.setShapeNodeName(shape_node_name);

            get_camera_values(
                m_startFrame,
                uiUnit,
                cam,
                m_image_width_a,
                m_image_height_a,
                m_focal_length_mm_a,
                m_sensor_width_mm_a,
                m_sensor_height_mm_a);
            get_camera_values(
                m_endFrame,
                uiUnit,
                cam,
                m_image_width_b,
                m_image_height_b,
                m_focal_length_mm_b,
                m_sensor_width_mm_b,
                m_sensor_height_mm_b);
        }
    }
    MMSOLVER_INFO("image A: " << m_image_width_a << "x" << m_image_height_a);
    MMSOLVER_INFO("image B: " << m_image_width_b << "x" << m_image_height_b);
    MMSOLVER_INFO("sensor (mm) A: " << m_sensor_width_mm_a
         << "x" << m_sensor_height_mm_a);
    MMSOLVER_INFO("sensor (mm) B: " << m_sensor_width_mm_b
         << "x" << m_sensor_height_mm_b);
    MMSOLVER_INFO("focal (mm) A: " << m_focal_length_mm_a);
    MMSOLVER_INFO("focal (mm) B: " << m_focal_length_mm_b);

    // Parse objects into Camera intrinsics and Tracking Markers.
    MItSelectionList iter2(objects);
    for (; !iter2.isDone(); iter2.next()) {
        MDagPath nodeDagPath;
        MObject node_obj;

        status = iter2.getDagPath(nodeDagPath);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        status = iter2.getDependNode(node_obj);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        auto node_name = nodeDagPath.fullPathName();
        auto object_type = computeObjectType(node_obj, nodeDagPath);
        if (object_type == ObjectType::kMarker) {
            // Add Markers
            MMSOLVER_INFO("Marker name: " << node_name.asChar());
            auto mkr = MMMarker();
            mkr.setNodeName(node_name);

            double x_a = 0.0;
            double x_b = 0.0;
            double y_a = 0.0;
            double y_b = 0.0;
            bool enable_a = true;
            bool enable_b = true;
            double weight_a = 1.0;
            double weight_b = 1.0;

            auto success_a = get_marker_coords(
                m_startFrame, uiUnit, mkr,
                x_a, y_a,
                weight_a, enable_a);
            auto success_b = get_marker_coords(
                m_endFrame, uiUnit, mkr,
                x_b, y_b,
                weight_b, enable_b);
            if (success_a && success_b) {
                double xx_a =
                    (x_a + 0.5) * static_cast<double>(m_image_width_a);
                double yy_a =
                    (y_a + 0.5) * static_cast<double>(m_image_height_a);
                double xx_b =
                    (x_b + 0.5) * static_cast<double>(m_image_width_b);
                double yy_b =
                    (y_b + 0.5) * static_cast<double>(m_image_height_b);
                MMSOLVER_INFO("x_a : " << x_a << " y_a : " << y_a);
                MMSOLVER_INFO("xx_a: " << xx_a << " yy_a: " << yy_a);
                MMSOLVER_INFO("x_b : " << x_b << " y_b : " << y_b);
                MMSOLVER_INFO("xx_b: " << xx_b << " yy_b: " << yy_b);
                auto xy_a = std::pair<double, double>{xx_a, yy_a};
                auto xy_b = std::pair<double, double>{xx_b, yy_b};
                m_marker_coords_a.push_back(xy_a);
                m_marker_coords_b.push_back(xy_b);
            }
        }
    }

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

    // Compute the relative pose thanks to a essential matrix estimation
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
    MMSOLVER_INFO("- #inliers: " << pose_info.vec_inliers.size());
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
    openMVG::sfm::SfM_Data &scene) {
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

            num++;
        }
    }
    return num > 0;
}

bool bundle_adjustment(openMVG::sfm::SfM_Data &scene) {
    // Perform Bundle Adjustment of the scene.
    //
    // TODO: This crashes, at least on Windows with MSVC :(
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
    if (0) {
        auto adjust_ok = bundle_adjustment(scene);
        if (!adjust_ok) {
            MMSOLVER_ERR("Bundle Adjustment failed.");
            status = MS::kFailure;
            return status;
        }
    }

    MMSOLVER_INFO("K ---");
    std::this_thread::sleep_for(std::chrono::milliseconds(10));
    openMVG::sfm::Save(
        scene,
        "EssentialGeometry_after.json",
        openMVG::sfm::ESfM_Data(openMVG::sfm::ESfM_Data::ALL));

    // TODO: Convert the sfm_data back to Maya data and set Camera and Bundles.

    MMCameraRelativePoseCmd::setResult(outResult);
    return status;
}
