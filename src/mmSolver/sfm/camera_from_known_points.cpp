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
#include <cassert>
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

#include <openMVG/numeric/numeric.h>

#include <openMVG/geometry/pose3.hpp>
#include <openMVG/multiview/solver_resection.hpp>
#include <openMVG/numeric/eigen_alias_definition.hpp>
#include <openMVG/robust_estimation/robust_estimator_ACRansac.hpp>
#include <openMVG/robust_estimation/robust_estimator_ACRansacKernelAdaptator.hpp>
#include <openMVG/robust_estimation/robust_estimator_Ransac.hpp>
#include <openMVG/types.hpp>

#include "openMVG/cameras/Camera_Common.hpp"
#include "openMVG/cameras/Camera_Intrinsics.hpp"
#include "openMVG/cameras/Camera_Pinhole.hpp"
#include "openMVG/multiview/projection.hpp"
#include "openMVG/multiview/solver_resection_kernel.hpp"
#include "openMVG/multiview/solver_resection_p3p.hpp"
#include "openMVG/multiview/solver_resection_up2p_kukelova.hpp"

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

/// Pose/Resection Kernel adapter for the A contrario model estimator
/// with known camera intrinsics.
template <typename SolverArg, typename ModelArg = Mat34>
class ACKernelAdaptorResectionIntrinsics {
public:
    using Solver = SolverArg;
    using Model = ModelArg;

    ACKernelAdaptorResectionIntrinsics(
        const openMVG::Mat &x2d,  // Undistorted 2d feature_point location
        const openMVG::Mat &x3d,  // 3D corresponding points
        const openMVG::cameras::IntrinsicBase *camera)
        : x2d_(x2d)
        , x3d_(x3d)
        , logalpha0_(log10(M_PI))
        , N1_(openMVG::Mat3::Identity())
        , camera_(camera) {
        N1_.diagonal().head(2) *= camera->imagePlane_toCameraPlaneError(1.0);
        assert(2 == x2d_.rows());
        assert(3 == x3d_.rows());
        assert(x2d_.cols() == x3d_.cols());
        bearing_vectors_ = camera->operator()(x2d_);
    }

    enum { MINIMUM_SAMPLES = Solver::MINIMUM_SAMPLES };
    enum { MAX_MODELS = Solver::MAX_MODELS };

    void Fit(const std::vector<uint32_t> &samples,
             std::vector<Model> *models) const {
        Solver::Solve(openMVG::ExtractColumns(bearing_vectors_,
                                              samples),  // bearing vectors
                      openMVG::ExtractColumns(x3d_, samples),  // 3D points
                      models);  // Found model hypothesis
    }

    void Errors(const Model &model, std::vector<double> &vec_errors) const {
        // Convert the found model into a Pose3
        const openMVG::Vec3 t = model.block(0, 3, 3, 1);
        const openMVG::geometry::Pose3 pose(
            model.block(0, 0, 3, 3), -model.block(0, 0, 3, 3).transpose() * t);

        vec_errors.resize(x2d_.cols());

        // We ignore distortion since we are using undistorted bearing
        // vector as input.
        const bool ignore_distortion = true;

        for (openMVG::Mat::Index sample = 0; sample < x2d_.cols(); ++sample) {
            vec_errors[sample] =
                (camera_->residual(pose(x3d_.col(sample)), x2d_.col(sample),
                                   ignore_distortion) *
                 N1_(0, 0))
                    .squaredNorm();
        }
    }

    size_t NumSamples() const { return x2d_.cols(); }

    void Unnormalize(Model *model) const {}

    double logalpha0() const { return logalpha0_; }
    double multError() const { return 1.0; }  // point to point error
    openMVG::Mat3 normalizer1() const { return openMVG::Mat3::Identity(); }
    openMVG::Mat3 normalizer2() const { return N1_; }
    double unormalizeError(double val) const { return sqrt(val) / N1_(0, 0); }

private:
    openMVG::Mat x2d_;
    openMVG::Mat bearing_vectors_;
    const openMVG::Mat &x3d_;
    openMVG::Mat3 N1_;
    double logalpha0_;  // Alpha0 is used to make the error adaptive
                        // to the image size
    const openMVG::cameras::IntrinsicBase
        *camera_;  // Intrinsic camera parameter
};

bool robust_camera_pose_from_known_points(
    const openMVG::Mat &points_2d, const openMVG::Mat &points_3d,
    const std::pair<size_t, size_t> &image_size, const double focal_length_pix,
    const double ppx_pix, const double ppy_pix,
    const size_t max_iteration_count, openMVG::Mat34 &out_projection_matrix) {
    // Enable to print out 'MMSOLVER_VRB' results.
    const bool verbose = false;

    // Upper bound pixel tolerance for residual errors.
    const double error_max = std::numeric_limits<double>::infinity();

    // The amount of pixel error that is computed.
    double out_error_max = std::numeric_limits<double>::infinity();

    // NFA = Number of False Alarms.
    double out_min_nfa = std::numeric_limits<double>::infinity();

    const auto image_width = image_size.first;
    const auto image_height = image_size.second;
    MMSOLVER_VRB(
        "robust_camera_pose_from_known_points: points 2D: " << points_2d);
    MMSOLVER_VRB(
        "robust_camera_pose_from_known_points: points 3D: " << points_3d);
    MMSOLVER_VRB("robust_camera_pose_from_known_points: image size (pixel): "
                 << image_width << "x" << image_height);
    MMSOLVER_VRB("robust_camera_pose_from_known_points: focal length (pixel): "
                 << focal_length_pix);
    MMSOLVER_VRB(
        "robust_camera_pose_from_known_points: principal point (pixel): "
        << ppx_pix << "x" << ppy_pix);
    MMSOLVER_VRB("robust_camera_pose_from_known_points: max_iteration_count: "
                 << max_iteration_count);

    double error_upper_bound = std::numeric_limits<double>::infinity();
    if (error_max != std::numeric_limits<double>::infinity()) {
        error_upper_bound = (error_max * error_max);
    }

    auto solution_found = false;
    size_t minimum_samples = 0;
    size_t samples = 0;

    std::vector<uint32_t> vec_inliers = {};
    vec_inliers.clear();
    vec_inliers.reserve(points_2d.size());

    {
        // Classic resection using 6 points, computed with a Direct
        // Linear Transform (DLT).
        using SolverType = openMVG::resection::kernel::SixPointResectionSolver;
        using KernelType = openMVG::robust::ACKernelAdaptorResection<
            SolverType, openMVG::resection::SquaredPixelReprojectionError,
            openMVG::robust::UnnormalizerResection, openMVG::Mat34>;

        minimum_samples = SolverType::MINIMUM_SAMPLES;

        KernelType kernel(points_2d, image_width, image_height, points_3d);

        // Robustly estimate the Resection matrix with A Contrario (AC)
        // RANSAC.
        const auto ac_ransac_output = openMVG::robust::ACRANSAC(
            kernel, vec_inliers, max_iteration_count, &out_projection_matrix,
            error_upper_bound, verbose);
        out_error_max = ac_ransac_output.first;
        out_min_nfa = ac_ransac_output.second;
        samples = vec_inliers.size();

        // MMSOLVER_VRB("projection matrix: " << out_projection_matrix);
    }

    MMSOLVER_VRB(
        "robust_camera_pose_from_known_points: valid samples: " << samples);
    MMSOLVER_VRB("robust_camera_pose_from_known_points: minimum samples: "
                 << minimum_samples);
    if (samples < minimum_samples) {
        // no sufficient coverage (not enough matching data points
        // given)
        MMSOLVER_VRB("Camera Pose could not be found with 6 points."
                     << " error=" << out_error_max << " pixels"
                     << ", number of false alarms=" << out_min_nfa
                     << ", minimum samples required=" << minimum_samples
                     << ", valid samples=" << samples);
    } else {
        solution_found = true;
    }

    // Try again, with an algorithm needing only 3 points.
    if (!solution_found) {
        {
            // P3P Nordberg (ECCV18)
            //
            // https://openaccess.thecvf.com/content_ECCV_2018/html/Mikael_Persson_Lambda_Twist_An_ECCV_2018_paper.html
            const openMVG::cameras::Pinhole_Intrinsic camera_intrinsics(
                image_width, image_height, focal_length_pix, ppx_pix, ppy_pix);

            using SolverType = openMVG::euclidean_resection::P3PSolver_Nordberg;
            using KernelType =
                ACKernelAdaptorResectionIntrinsics<SolverType, openMVG::Mat34>;

            minimum_samples = SolverType::MINIMUM_SAMPLES;

            KernelType kernel(points_2d, points_3d, &camera_intrinsics);

            // Robustly estimate the Resection matrix with A Contrario (AC)
            // RANSAC.
            const auto ac_ransac_output = openMVG::robust::ACRANSAC(
                kernel, vec_inliers, max_iteration_count,
                &out_projection_matrix, error_upper_bound, verbose);
            out_error_max = ac_ransac_output.first;
            out_min_nfa = ac_ransac_output.second;
            samples = vec_inliers.size();
            MMSOLVER_VRB("projection matrix: " << out_projection_matrix);
        }

        MMSOLVER_VRB(
            "robust_camera_pose_from_known_points: valid samples: " << samples);
        MMSOLVER_VRB("robust_camera_pose_from_known_points: minimum samples: "
                     << minimum_samples);
        if (samples < minimum_samples) {
            // no sufficient coverage (not enough matching data points
            // given)
            MMSOLVER_WRN("Camera Pose could not be found with 6 or 3 points."
                         << " error=" << out_error_max << " pixels"
                         << ", number of false alarms=" << out_min_nfa
                         << ", minimum samples required=" << minimum_samples
                         << ", valid samples=" << samples);
        } else {
            solution_found = true;
        }
    }

    if (!solution_found) {
        return false;
    }

    MMSOLVER_VRB("Found a Camera matrix from known points:");
    MMSOLVER_VRB("- matrix: " << out_projection_matrix);
    MMSOLVER_VRB("- error: " << out_error_max << " pixels");
    MMSOLVER_VRB("- number of false alarms: " << out_min_nfa);

    MMSOLVER_VRB("- #points 3D: " << points_3d.size());
    for (auto i = 0; i < points_3d.size(); i++) {
        auto point_3d_x = points_3d.col(i)[0];
        auto point_3d_y = points_3d.col(i)[1];
        auto point_3d_z = points_3d.col(i)[2];
        MMSOLVER_VRB("  - #point 3D: " << i << " = " << point_3d_x << ","
                                       << point_3d_y << "," << point_3d_z);
    }

    MMSOLVER_VRB("- #points 2D: " << points_2d.size());
    for (auto i = 0; i < points_2d.size(); i++) {
        auto point_2d_x = points_2d.col(i)[0];
        auto point_2d_y = points_2d.col(i)[1];
        MMSOLVER_VRB("  - #point 2D: " << i << " = " << point_2d_x << ","
                                       << point_2d_y);
    }

    MMSOLVER_VRB("- #inliers: " << samples);

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
        convert_bundle_coords_to_matrix(bundle_coords);

    const std::pair<size_t, size_t> image_size(
        static_cast<size_t>(image_width), static_cast<size_t>(image_height));

    openMVG::Mat34 projection_matrix;
    auto num_max_iter = 1024;
    bool ok = robust_camera_pose_from_known_points(
        marker_coords_matrix, bundle_coords_matrix, image_size,
        focal_length_pix, ppx_pix, ppy_pix, num_max_iter, projection_matrix);
    if (!ok) {
        MMSOLVER_ERR(
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

    out_pose_transform = convert_pose_to_maya_transform_matrix(pose);

    return true;
}

}  // namespace sfm
}  // namespace mmsolver
