/*
 * Copyright (C) 2021 David Cattermole.
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
 * Command for running mmCameraSolve.
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

// Internal
#include "mmSolver/MMCameraSolveCmd.h"

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

// Ceres Solver
#ifdef MMSOLVER_USE_CERES

#pragma warning( push )
// Compiler Warning (level 1) C4251: needs to have dll-interface to be
// used by clients of class.
#pragma warning( disable : 4251 )
#include <ceres/ceres.h>
// #include <glog/logging.h>
#pragma warning( pop )

#endif  // MMSOLVER_USE_CERES

// LibMV
#ifdef MMSOLVER_USE_LIBMV

#include <libmv/base/vector.h>
#include <libmv/base/vector_utils.h>
#include <libmv/base/scoped_ptr.h>
#include <libmv/camera/pinhole_camera.h>
#include <libmv/correspondence/export_matches_txt.h>
#include <libmv/correspondence/feature.h>
#include <libmv/correspondence/feature_matching.h>
#include <libmv/correspondence/nRobustViewMatching.h>
#include <libmv/correspondence/import_matches_txt.h>
#include <libmv/correspondence/tracker.h>
#include <libmv/detector/detector_factory.h>
#include <libmv/descriptor/descriptor_factory.h>
#include <libmv/image/image.h>
#include <libmv/image/image_converter.h>
#include <libmv/image/image_drawing.h>
#include <libmv/image/image_io.h>
#include <libmv/logging/logging.h>
#include <libmv/numeric/numeric.h>
#include <libmv/reconstruction/euclidean_reconstruction.h>
#include <libmv/reconstruction/export_blender.h>
#include <libmv/reconstruction/export_ply.h>
#include <libmv/tools/tool.h>
#include <libmv/simple_pipeline/tracks.h>
#include <libmv/simple_pipeline/keyframe_selection.h>
#include <libmv/reconstruction/keyframe_selection.h>
#include <libmv/simple_pipeline/camera_intrinsics.h>
#include <libmv/simple_pipeline/packed_intrinsics.h>

#endif  // MMSOLVER_USE_LIBMV

// OpenMVG
#ifdef MMSOLVER_USE_OPENMVG

#include <openMVG/features/feature.hpp>
#include <openMVG/features/feature_container.hpp>
#include <openMVG/matching/regions_matcher.hpp>
#include <openMVG/matching/indMatch.hpp>
#include <openMVG/multiview/solver_fundamental_kernel.hpp>
#include <openMVG/multiview/conditioning.hpp>
#include <openMVG/numeric/eigen_alias_definition.hpp>
#include <openMVG/numeric/numeric.h>
#include <openMVG/robust_estimation/robust_estimator_ACRansac.hpp>
#include <openMVG/robust_estimation/robust_estimator_ACRansacKernelAdaptator.hpp>
#include <openMVG/types.hpp>

#endif  // MMSOLVER_USE_OPENMVG

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

// MM Solver
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_marker.h"
#include "mmSolver/adjust/adjust_defines.h"

namespace mmsolver {

using MMMarker = Marker;
using MMCamera = Camera;

// // GFlags test.
// #ifdef MMSOLVER_USE_GLOG

// DEFINE_bool(
//     big_menu,
//     true,
//     "Include 'advanced' options in the menu listing");
// DEFINE_string(
//     languages,
//     "english,french,german",
//     "comma-separated list of languages to offer in the 'lang' menu");

// #endif  // MMSOLVER_USE_GLOG

using KernelType =
    openMVG::robust::ACKernelAdaptor<
    openMVG::fundamental::kernel::NormalizedEightPointKernel,
    openMVG::fundamental::kernel::SymmetricEpipolarDistanceError,
    openMVG::UnnormalizerT,
    openMVG::Mat3>;

MMCameraSolveCmd::~MMCameraSolveCmd() {}

void *MMCameraSolveCmd::creator() {
    return new MMCameraSolveCmd();
}

MString MMCameraSolveCmd::cmdName() {
    return MString("mmCameraSolve");
}

/*
 * Tell Maya we have a syntax function.
 */
bool MMCameraSolveCmd::hasSyntax() const {
    return true;
}

bool MMCameraSolveCmd::isUndoable() const {
    return false;
}

/*
 * Add flags to the command syntax
 */
MSyntax MMCameraSolveCmd::newSyntax() {
    MSyntax syntax;
    syntax.enableQuery(false);
    syntax.enableEdit(false);

    unsigned int minNumObjects = 0;
    syntax.setObjectType(MSyntax::kSelectionList, minNumObjects);

    syntax.addFlag("-sf", "-startFrame", MSyntax::kUnsigned);
    syntax.addFlag("-ef", "-endFrame", MSyntax::kUnsigned);

    return syntax;
}

bool get_marker_coord(
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

bool get_camera_image_res(
    const uint32_t frame_num,
    const MTime::Unit &uiUnit,
    MMCamera &cam,
    int &image_width,
    int &image_height) {

    auto timeEvalMode = TIME_EVAL_MODE_DG_CONTEXT;
    auto frame = static_cast<double>(frame_num);
    MTime time = MTime(frame, uiUnit);

    auto filmBackWidth = cam.getFilmbackWidthValue(time, timeEvalMode);
    auto filmBackHeight = cam.getFilmbackHeightValue(time, timeEvalMode);
    image_width = static_cast<int>(filmBackWidth * 10000.0);
    image_height = static_cast<int>(filmBackHeight * 10000.0);
    return true;
}

/*
 * Parse command line arguments
 */
MStatus MMCameraSolveCmd::parseArgs(const MArgList &args) {
    MStatus status = MStatus::kSuccess;

    MArgDatabase argData(syntax(), args, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    m_startFrame = 1;
    if (argData.isFlagSet("-sf")) {
        status = argData.getFlagArgument("-sf", 0, m_startFrame);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    m_endFrame = 120;
    if (argData.isFlagSet("-ef")) {
        status = argData.getFlagArgument("-ef", 0, m_endFrame);
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

    MItSelectionList iter1(objects);
    for (; !iter1.isDone(); iter1.next()) {
        MDagPath nodeDagPath;
        MObject node_obj;

        status = iter1.getDagPath(nodeDagPath);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        status = iter1.getDependNode(node_obj);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        auto node_name = nodeDagPath.fullPathName();
        // MMSOLVER_INFO("Node name: " << node_name.asChar());

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

            get_camera_image_res(
                m_startFrame,
                uiUnit,
                cam,
                m_image_width_a,
                m_image_height_a);
            get_camera_image_res(
                m_endFrame,
                uiUnit,
                cam,
                m_image_width_b,
                m_image_height_b);
        }
    }
    MMSOLVER_INFO("image A: " << m_image_width_a << "x" << m_image_height_a);
    MMSOLVER_INFO("image B: " << m_image_width_b << "x" << m_image_height_b);

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
        // MMSOLVER_INFO("Node name: " << node_name.asChar());

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

            auto success_a = get_marker_coord(
                m_startFrame, uiUnit, mkr,
                x_a, y_a,
                weight_a, enable_a);
            auto success_b = get_marker_coord(
                m_endFrame, uiUnit, mkr,
                x_b, y_b,
                weight_b, enable_b);
            if (success_a && success_b) {
                double xx_a = (x_a + 0.5) * static_cast<double>(m_image_width_a);
                double yy_a = (y_a + 0.5) * static_cast<double>(m_image_height_a);
                double xx_b = (x_b + 0.5) * static_cast<double>(m_image_width_b);
                double yy_b = (y_b + 0.5) * static_cast<double>(m_image_height_b);
                MMSOLVER_INFO("x_a : " << x_a  << " y_a : " << y_a);
                MMSOLVER_INFO("xx_a: " << xx_a << " yy_a: " << yy_a);
                MMSOLVER_INFO("x_b : " << x_b  << " y_b : " << y_b);
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


#ifdef MMSOLVER_USE_LIBMV

void get_file_path_extension(const std::string &file,
                             std::string *path_name,
                             std::string *ext) {
    size_t dot_pos = file.rfind(".");
    if (dot_pos != std::string::npos) {
        *path_name = file.substr(0, dot_pos);
        *ext = file.substr(dot_pos + 1, file.length() - dot_pos - 1);
    } else {
        *path_name = file;
        *ext = "";
    }
}

#endif  // MMSOLVER_USE_LIBMV


#ifdef MMSOLVER_USE_CERES

struct CostFunctor {
    template<typename T>
    bool operator()(const T *const x, T *residual) const {
        residual[0] = 10.0 - x[0];
        return true;
    }
};

// Data generated using the following octave code.
//   randn('seed', 23497);
//   m = 0.3;
//   c = 0.1;
//   x=[0:0.075:5];
//   y = exp(m * x + c);
//   noise = randn(size(x)) * 0.2;
//   y_observed = y + noise;
//   data = [x', y_observed'];
const int kNumObservations = 67;

// clang-format off
const double data[] = {
    0.000000e+00, 1.133898e+00,
    7.500000e-02, 1.334902e+00,
    1.500000e-01, 1.213546e+00,
    2.250000e-01, 1.252016e+00,
    3.000000e-01, 1.392265e+00,
    3.750000e-01, 1.314458e+00,
    4.500000e-01, 1.472541e+00,
    5.250000e-01, 1.536218e+00,
    6.000000e-01, 1.355679e+00,
    6.750000e-01, 1.463566e+00,
    7.500000e-01, 1.490201e+00,
    8.250000e-01, 1.658699e+00,
    9.000000e-01, 1.067574e+00,
    9.750000e-01, 1.464629e+00,
    1.050000e+00, 1.402653e+00,
    1.125000e+00, 1.713141e+00,
    1.200000e+00, 1.527021e+00,
    1.275000e+00, 1.702632e+00,
    1.350000e+00, 1.423899e+00,
    1.425000e+00, 1.543078e+00,
    1.500000e+00, 1.664015e+00,
    1.575000e+00, 1.732484e+00,
    1.650000e+00, 1.543296e+00,
    1.725000e+00, 1.959523e+00,
    1.800000e+00, 1.685132e+00,
    1.875000e+00, 1.951791e+00,
    1.950000e+00, 2.095346e+00,
    2.025000e+00, 2.361460e+00,
    2.100000e+00, 2.169119e+00,
    2.175000e+00, 2.061745e+00,
    2.250000e+00, 2.178641e+00,
    2.325000e+00, 2.104346e+00,
    2.400000e+00, 2.584470e+00,
    2.475000e+00, 1.914158e+00,
    2.550000e+00, 2.368375e+00,
    2.625000e+00, 2.686125e+00,
    2.700000e+00, 2.712395e+00,
    2.775000e+00, 2.499511e+00,
    2.850000e+00, 2.558897e+00,
    2.925000e+00, 2.309154e+00,
    3.000000e+00, 2.869503e+00,
    3.075000e+00, 3.116645e+00,
    3.150000e+00, 3.094907e+00,
    3.225000e+00, 2.471759e+00,
    3.300000e+00, 3.017131e+00,
    3.375000e+00, 3.232381e+00,
    3.450000e+00, 2.944596e+00,
    3.525000e+00, 3.385343e+00,
    3.600000e+00, 3.199826e+00,
    3.675000e+00, 3.423039e+00,
    3.750000e+00, 3.621552e+00,
    3.825000e+00, 3.559255e+00,
    3.900000e+00, 3.530713e+00,
    3.975000e+00, 3.561766e+00,
    4.050000e+00, 3.544574e+00,
    4.125000e+00, 3.867945e+00,
    4.200000e+00, 4.049776e+00,
    4.275000e+00, 3.885601e+00,
    4.350000e+00, 4.110505e+00,
    4.425000e+00, 4.345320e+00,
    4.500000e+00, 4.161241e+00,
    4.575000e+00, 4.363407e+00,
    4.650000e+00, 4.161576e+00,
    4.725000e+00, 4.619728e+00,
    4.800000e+00, 4.737410e+00,
    4.875000e+00, 4.727863e+00,
    4.950000e+00, 4.669206e+00,
};
// clang-format on

struct ExponentialResidual {
    ExponentialResidual(double x, double y) : x_(x), y_(y) {}

    template<typename T>
    bool operator()(const T *const m, const T *const c, T *residual) const {
        residual[0] = y_ - exp(m[0] * x_ + c[0]);
        return true;
    }

private:
    const double x_;
    const double y_;
};

#endif  // MMSOLVER_USE_CERES

MStatus MMCameraSolveCmd::doIt(const MArgList &args) {
    MStatus status = MStatus::kSuccess;

    // Read all the flag arguments.
    status = parseArgs(args);
    if (status == MStatus::kFailure) {
        return status;
    }

    // Command Outputs
    MDoubleArray outResult;

    // // Test the GLOG library.
    // MMSOLVER_INFO("Camera Solve Command - This is a log message!\n");

#ifdef MMSOLVER_USE_CERES
    // Ceres Solver - Example #1
    //
    // https://ceres-solver.googlesource.com/ceres-solver/+/master/examples/helloworld.cc
    {
        // The variable to solve for with its initial value.
        double initial_x = 5.0;
        double x = initial_x;

        // Build the problem.
        ceres::Problem problem;

        // Set up the only cost function (also known as residual). This uses
        // auto-differentiation to obtain the derivative (jacobian).
        ceres::CostFunction *cost_function =
            new ceres::AutoDiffCostFunction<CostFunctor, 1, 1>(
                new CostFunctor);
        problem.AddResidualBlock(cost_function, nullptr, &x);

        // Run the solver!
        ceres::Solver::Options options;
        options.linear_solver_type = ceres::DENSE_QR;
        options.minimizer_progress_to_stdout = true;
        ceres::Solver::Summary summary;
        ceres::Solve(options, &problem, &summary);

        MMSOLVER_INFO(summary.BriefReport());
        MMSOLVER_INFO("x : " << initial_x << " -> " << x);
    }

    // Ceres Solver - Example #2 - Curve Fitting
    //
    // https://ceres-solver.googlesource.com/ceres-solver/+/master/examples/curve_fitting.cc
    {
        double m = 0.0;
        double c = 0.0;

        ceres::Problem problem;
        for (int i = 0; i < kNumObservations; ++i) {
            problem.AddResidualBlock(
                new ceres::AutoDiffCostFunction<ExponentialResidual, 1, 1, 1>(
                    new ExponentialResidual(data[2 * i],
                                            data[2 * i + 1])),
                nullptr,
                &m,
                &c);
        }

        ceres::Solver::Options options;
        options.max_num_iterations = 25;
        options.linear_solver_type = ceres::DENSE_QR;
        options.minimizer_progress_to_stdout = true;

        ceres::Solver::Summary summary;
        Solve(options, &problem, &summary);
        MMSOLVER_INFO(summary.BriefReport());
        MMSOLVER_INFO("Initial m: " << 0.0 << " c: " << 0.0);
        MMSOLVER_INFO("Final   m: " << m << " c: " << c);
    }
#endif  // MMSOLVER_USE_CERES

#ifdef MMSOLVER_USE_LIBMV
    // LibMV - Example #1
    {
        auto focal = 500.0;
        libmv::Vec2 principal_point(0.0, 0.0);
        libmv::Vec2f pixel(0.0, 0.0);
        libmv::Vec2u img_size(1920.0, 1080.0);

        auto cam = libmv::PinholeCamera(focal, principal_point);
        auto img_width = cam.image_width();
        cam.set_image_size(img_size);
        auto img_width2 = cam.image_width();
        auto ray = cam.Ray(pixel);

        auto focal_x = cam.focal_x();
        auto focal_y = cam.focal_y();
        MMSOLVER_INFO("img_width = " << img_width);
        MMSOLVER_INFO("img_width2 = " << img_width2);
        MMSOLVER_INFO("ray = " << ray);
        MMSOLVER_INFO("focal_x = " << focal_x);
        MMSOLVER_INFO("focal_y = " << focal_y);
    }

    // LibMV - Example #2 - Reconstruct Video
    //
    // Estimate the camera trajectory using matches.
    {
        // Input values
        std::string input_file_path = "matches.txt";
        std::string output_file_path = "reconstruction.py";
        int image_width = 1920;
        int image_height = 1080;
        double focal_length = 50.0;
        double principal_point_u0 = 0.0;
        double principal_point_v0 = 0.0;

        // Imports matches
        libmv::tracker::FeaturesGraph fg;
        FeatureSet *fs = fg.CreateNewFeatureSet();

        MMSOLVER_INFO("Loading Matches file...");
        libmv::ImportMatchesFromTxt(input_file_path, &fg.matches_, fs);
        MMSOLVER_INFO("Loading Matches file...[DONE].");

        // Estimates the camera trajectory and 3D structure of the scene
        int w = image_width;
        int h = image_height;
        if (principal_point_u0 > 0) {
            w = static_cast<int>(2.0 * (principal_point_u0 + 0.5));
        }
        if (principal_point_v0 > 0) {
            h = static_cast<int>(2.0 * (principal_point_v0 + 0.5));
        }

        MMSOLVER_INFO("Euclidean Reconstruction From Video...");
        std::list<libmv::Reconstruction *> reconstructions;
        EuclideanReconstructionFromVideo(
            fg.matches_,
            w, h,
            focal_length,
            &reconstructions);
        MMSOLVER_INFO("Euclidean Reconstruction From Video...[DONE]");

        // Exports the reconstructions
        MMSOLVER_INFO("Exporting Reconstructions...");
        std::string file_path_name;
        std::string file_ext;
        get_file_path_extension(output_file_path, &file_path_name, &file_ext);
        std::transform(file_ext.begin(), file_ext.end(), file_ext.begin(),
                       ::tolower);

        int i = 0;
        std::list<libmv::Reconstruction *>::iterator iter = reconstructions.begin();
        if (file_ext == "ply") {
            for (; iter != reconstructions.end(); ++iter) {
                std::stringstream s;
                if (reconstructions.size() > 1)
                    s << file_path_name << "-" << i << ".ply";
                else
                    s << output_file_path;
                libmv::ExportToPLY(**iter, s.str());
            }
        } else if (file_ext == "py") {
            for (; iter != reconstructions.end(); ++iter) {
                std::stringstream s;
                if (reconstructions.size() > 1)
                    s << file_path_name << "-" << i << ".py";
                else
                    s << output_file_path;
                libmv::ExportToBlenderScript(**iter, s.str());
            }
        }MMSOLVER_INFO("Exporting Reconstructions...[DONE]");

        // Cleaning
        MMSOLVER_INFO("Cleaning.");
        iter = reconstructions.begin();
        for (; iter != reconstructions.end(); ++iter) {
            (*iter)->ClearCamerasMap();
            (*iter)->ClearStructuresMap();
            delete *iter;
        }
        reconstructions.clear();
        // Delete the features graph
        fg.DeleteAndClear();
    }
#endif  // MMSOLVER_USE_LIBMV

    // OpenMVG - Fundamental matrix robust estimation
    {
        auto minimal_samples = KernelType::MINIMUM_SAMPLES;
        uint32_t num_max_iteration = 1024;
        double precision = std::numeric_limits<double>::infinity();
        bool verbose = true;

        auto point_to_line = true;  // configure as point to line error model.
        auto num_markers = m_marker_coords_a.size();
        openMVG::Mat marker_coords_a(2, num_markers);
        openMVG::Mat marker_coords_b(2, num_markers);
        for (size_t k = 0; k < num_markers; ++k) {
            auto coord_a = m_marker_coords_a[k];
            auto coord_b = m_marker_coords_b[k];
            openMVG::Vec2 mat_a(std::get<0>(coord_a), std::get<1>(coord_a));
            openMVG::Vec2 mat_b(std::get<0>(coord_b), std::get<1>(coord_b));
            marker_coords_a.col(k) = mat_a;
            marker_coords_b.col(k) = mat_b;
        }

        MMSOLVER_INFO("num_markers: " << num_markers);
        KernelType kernel(
            marker_coords_a, m_image_width_a, m_image_height_a,
            marker_coords_b, m_image_width_b, m_image_height_b,
            point_to_line);
        MMSOLVER_INFO("kernel.NumSamples(): " << kernel.NumSamples());
        MMSOLVER_INFO("kernel.logalpha0(): " << kernel.logalpha0());
        MMSOLVER_INFO("kernel.multError(): " << kernel.multError());
        MMSOLVER_INFO("kernel.normalizer1(): " << kernel.normalizer1());
        MMSOLVER_INFO("kernel.normalizer2(): " << kernel.normalizer2());

        std::vector<uint32_t> inliers;
        openMVG::Mat3 matrix;
        const std::pair<double, double> ac_ransac_out =
            openMVG::robust::ACRANSAC(
                kernel,
                inliers,
                num_max_iteration,
                &matrix,
                precision,
                verbose);
        const double &errorMax = ac_ransac_out.first;
        const double &minNFA = ac_ransac_out.second;
        auto number_of_inliers = inliers.size();
        MMSOLVER_INFO("errorMax: " << errorMax << " pixels");
        MMSOLVER_INFO("minNFA: " << minNFA);
        MMSOLVER_INFO("KernelType::MINIMUM_SAMPLES: " << KernelType::MINIMUM_SAMPLES);
        MMSOLVER_INFO("matrix: " << matrix);
        MMSOLVER_INFO("inliers.size(): " << number_of_inliers);

        // Check the fundamental support some point to be considered
        // as valid.
        if (number_of_inliers > minimal_samples) {
            MMSOLVER_INFO("Found a fundamental under the confidence threshold of: "
                 << errorMax << " pixels\n\t"
                 << "with: " << inliers.size() << " inliers"
                 << " from: " << num_markers
                 << " correspondences\n");
            outResult.append(errorMax);
            outResult.append(minNFA);
        } else {
            MMSOLVER_INFO("ACRANSAC was unable to estimate a rigid fundamental");
        }
    }

    MMCameraSolveCmd::setResult(outResult);
    return status;
}

} // namespace mmsolver
