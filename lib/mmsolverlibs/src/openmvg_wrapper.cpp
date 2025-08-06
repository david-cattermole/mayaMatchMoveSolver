/*
 * Copyright (C) 2025 David Cattermole.
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
 * OpenMVG API wrapper implementation.
 */

#include "mmsolverlibs/openmvg_wrapper.h"

// STL
#include <memory>
#include <utility>
#include <vector>

// OpenMVG
#include <openMVG/numeric/numeric.h>

#include <openMVG/cameras/Camera_Intrinsics.hpp>
#include <openMVG/cameras/Camera_Pinhole.hpp>
#include <openMVG/geometry/pose3.hpp>
#include <openMVG/multiview/conditioning.hpp>
#include <openMVG/multiview/motion_from_essential.hpp>
#include <openMVG/multiview/solver_essential_eight_point.hpp>
#include <openMVG/multiview/solver_essential_kernel.hpp>
#include <openMVG/multiview/solver_homography_kernel.hpp>
#include <openMVG/multiview/solver_resection_kernel.hpp>
#include <openMVG/multiview/solver_resection_p3p_nordberg.hpp>
#include <openMVG/multiview/triangulation.hpp>
#include <openMVG/numeric/eigen_alias_definition.hpp>
#include <openMVG/robust_estimation/robust_estimator_ACKernelAdaptorResection.hpp>
#include <openMVG/robust_estimation/robust_estimator_ACRansac.hpp>
#include <openMVG/robust_estimation/robust_estimator_ACRansacKernelAdaptator.hpp>
#include <openMVG/sfm/pipelines/sfm_robust_model_estimation.hpp>
#include <openMVG/sfm/sfm_data.hpp>
#include <openMVG/types.hpp>

namespace mmsolverlibs {
namespace openmvg {

// Opaque type implementations
struct HomographyMatrix {
    openMVG::Mat3 matrix;
};

struct RelativePoseInfo {
    openMVG::sfm::RelativePose_Info info;
};

struct CameraIntrinsics {
    std::unique_ptr<openMVG::cameras::IntrinsicBase> intrinsics;
};

struct Pose3 {
    openMVG::geometry::Pose3 pose;
};

// Homography functions.
HomographyMatrix* homography_matrix_new() { return new HomographyMatrix(); }

void homography_matrix_free(HomographyMatrix* matrix) { delete matrix; }

bool compute_homography(std::int32_t image_width_a, std::int32_t image_width_b,
                        std::int32_t image_height_a,
                        std::int32_t image_height_b,
                        const Point2d* marker_coords_a,
                        std::size_t num_markers_a,
                        const Point2d* marker_coords_b,
                        std::size_t num_markers_b,
                        HomographyMatrix* homography_matrix) {
    if (!marker_coords_a || !marker_coords_b || !homography_matrix ||
        num_markers_a != num_markers_b || num_markers_a < 4) {
        return false;
    }

    // Convert input data to OpenMVG format.
    std::vector<std::pair<double, double>> coords_a, coords_b;

    for (size_t i = 0; i < num_markers_a; ++i) {
        coords_a.emplace_back(marker_coords_a[i].x, marker_coords_a[i].y);
        coords_b.emplace_back(marker_coords_b[i].x, marker_coords_b[i].y);
    }

    // Create matrices for OpenMVG.
    openMVG::Mat x1(2, num_markers_a);
    openMVG::Mat x2(2, num_markers_b);

    for (size_t i = 0; i < num_markers_a; ++i) {
        x1(0, i) = coords_a[i].first;
        x1(1, i) = coords_a[i].second;
        x2(0, i) = coords_b[i].first;
        x2(1, i) = coords_b[i].second;
    }

    // Use robust homography estimation.
    const uint32_t max_iteration_count = 4096;
    const std::pair<uint32_t, uint32_t> size_ima1(image_width_a,
                                                  image_height_a);
    const std::pair<uint32_t, uint32_t> size_ima2(image_width_b,
                                                  image_height_b);

    return robust_homography(x1.data(), x1.rows(), x1.cols(), x2.data(),
                             x2.rows(), x2.cols(), homography_matrix,
                             image_width_a, image_height_a, image_width_b,
                             image_height_b, max_iteration_count);
}

bool robust_homography(
    const double* x1_data, std::size_t x1_rows, std::size_t x1_cols,
    const double* x2_data, std::size_t x2_rows, std::size_t x2_cols,
    HomographyMatrix* homography_matrix, std::uint32_t image_width_1,
    std::uint32_t image_height_1, std::uint32_t image_width_2,
    std::uint32_t image_height_2, std::uint32_t max_iteration_count) {
    if (!x1_data || !x2_data || !homography_matrix || x1_rows != 2 ||
        x2_rows != 2 || x1_cols != x2_cols || x1_cols < 4) {
        return false;
    }

    // Create Eigen matrices from raw data
    openMVG::Mat x1 = Eigen::Map<const openMVG::Mat>(x1_data, x1_rows, x1_cols);
    openMVG::Mat x2 = Eigen::Map<const openMVG::Mat>(x2_data, x2_rows, x2_cols);

    const std::pair<uint32_t, uint32_t> size_ima1(image_width_1,
                                                  image_height_1);
    const std::pair<uint32_t, uint32_t> size_ima2(image_width_2,
                                                  image_height_2);

    try {
        using namespace openMVG;
        using namespace openMVG::robust;

        typedef ACKernelAdaptor<openMVG::homography::kernel::FourPointSolver,
                                openMVG::homography::kernel::AsymmetricError,
                                UnnormalizerI, openMVG::Mat3>
            KernelType;

        // Create homography kernel.
        KernelType kernel(x1, size_ima1.first, size_ima1.second, x2,
                          size_ima2.first, size_ima2.second, false);

        Mat3 H;
        std::vector<uint32_t> vec_inliers;
        const std::pair<double, double> ACRansacOut =
            ACRANSAC(kernel, vec_inliers, max_iteration_count, &H,
                     std::numeric_limits<double>::infinity(), false);

        if (vec_inliers.size() > KernelType::MINIMUM_SAMPLES * 2.5) {
            homography_matrix->matrix = H;
            return true;
        }
    } catch (...) {
        return false;
    }

    return false;
}

// Camera relative pose functions.
RelativePoseInfo* relative_pose_info_new() { return new RelativePoseInfo(); }

void relative_pose_info_free(RelativePoseInfo* info) { delete info; }

CameraIntrinsics* camera_intrinsics_new_pinhole(std::uint32_t width,
                                                std::uint32_t height,
                                                double focal_length, double ppx,
                                                double ppy) {
    auto intrinsics = new CameraIntrinsics();
    intrinsics->intrinsics =
        std::make_unique<openMVG::cameras::Pinhole_Intrinsic>(
            width, height, focal_length, ppx, ppy);
    return intrinsics;
}

void camera_intrinsics_free(CameraIntrinsics* intrinsics) { delete intrinsics; }

bool robust_relative_pose(
    const CameraIntrinsics* intrinsics1, const CameraIntrinsics* intrinsics2,
    const double* x1_data, std::size_t x1_rows, std::size_t x1_cols,
    const double* x2_data, std::size_t x2_rows, std::size_t x2_cols,
    RelativePoseInfo* relative_pose_info, std::uint32_t image_width_1,
    std::uint32_t image_height_1, std::uint32_t image_width_2,
    std::uint32_t image_height_2, std::uint32_t max_iteration_count) {
    if (!intrinsics1 || !intrinsics2 || !x1_data || !x2_data ||
        !relative_pose_info || x1_rows != 2 || x2_rows != 2 ||
        x1_cols != x2_cols || x1_cols < 8) {
        return false;
    }

    openMVG::Mat x1 = Eigen::Map<const openMVG::Mat>(x1_data, x1_rows, x1_cols);
    openMVG::Mat x2 = Eigen::Map<const openMVG::Mat>(x2_data, x2_rows, x2_cols);

    const std::pair<size_t, size_t> size_ima1(image_width_1, image_height_1);
    const std::pair<size_t, size_t> size_ima2(image_width_2, image_height_2);

    try {
        using namespace openMVG;
        using namespace openMVG::sfm;
        using namespace openMVG::cameras;
        using namespace openMVG::geometry;
        using namespace openMVG::robust;

        // Use simplified direct robust relative pose estimation
        std::vector<uint32_t> vec_selected_inliers;

        if (!openMVG::sfm::robustRelativePose(
                intrinsics1->intrinsics.get(), intrinsics2->intrinsics.get(),
                x1, x2, relative_pose_info->info, size_ima1, size_ima2,
                max_iteration_count)) {
            return false;
        }
        return true;
    } catch (...) {
        return false;
    }

    return false;
}

bool compute_relative_pose(
    std::int32_t image_width_a, std::int32_t image_width_b,
    std::int32_t image_height_a, std::int32_t image_height_b,
    double focal_length_pix_a, double focal_length_pix_b, double ppx_pix_a,
    double ppx_pix_b, double ppy_pix_a, double ppy_pix_b,
    const Point2d* marker_coords_a, std::size_t num_markers_a,
    const Point2d* marker_coords_b, std::size_t num_markers_b,
    RelativePoseInfo* relative_pose_info, Point3d* triangulated_points,
    std::size_t* num_triangulated_points) {
    if (!marker_coords_a || !marker_coords_b || !relative_pose_info ||
        num_markers_a != num_markers_b || num_markers_a < 8) {
        return false;
    }

    // Create camera intrinsics.
    auto intrinsics1 =
        camera_intrinsics_new_pinhole(image_width_a, image_height_a,
                                      focal_length_pix_a, ppx_pix_a, ppy_pix_a);
    auto intrinsics2 =
        camera_intrinsics_new_pinhole(image_width_b, image_height_b,
                                      focal_length_pix_b, ppx_pix_b, ppy_pix_b);

    // Convert points to matrices.
    openMVG::Mat x1(2, num_markers_a);
    openMVG::Mat x2(2, num_markers_b);

    for (size_t i = 0; i < num_markers_a; ++i) {
        x1(0, i) = marker_coords_a[i].x;
        x1(1, i) = marker_coords_a[i].y;
        x2(0, i) = marker_coords_b[i].x;
        x2(1, i) = marker_coords_b[i].y;
    }

    const uint32_t max_iteration_count = 4096;
    bool result = robust_relative_pose(
        intrinsics1, intrinsics2, x1.data(), x1.rows(), x1.cols(), x2.data(),
        x2.rows(), x2.cols(), relative_pose_info, image_width_a, image_height_a,
        image_width_b, image_height_b, max_iteration_count);

    // TODO: Implement triangulation if needed.
    if (triangulated_points && num_triangulated_points) {
        *num_triangulated_points = 0;
    }

    camera_intrinsics_free(intrinsics1);
    camera_intrinsics_free(intrinsics2);

    return result;
}

// Camera from known points (PnP) functions.
Pose3* pose3_new() { return new Pose3(); }

void pose3_free(Pose3* pose) { delete pose; }

bool solve_pnp_p3p_nordberg(const Point3d* world_points,
                            std::size_t num_world_points,
                            const Point2d* image_points,
                            std::size_t num_image_points,
                            const CameraIntrinsics* intrinsics, Pose3* pose,
                            std::uint32_t max_iteration_count) {
    if (!world_points || !image_points || !intrinsics || !pose ||
        num_world_points != num_image_points || num_world_points < 3) {
        return false;
    }

    try {
        using namespace openMVG;
        using namespace openMVG::robust;

        // Convert input points
        Mat x2d(2, num_image_points);
        Mat x3d(3, num_world_points);

        for (size_t i = 0; i < num_image_points; ++i) {
            x2d(0, i) = image_points[i].x;
            x2d(1, i) = image_points[i].y;
        }

        for (size_t i = 0; i < num_world_points; ++i) {
            x3d(0, i) = world_points[i].x;
            x3d(1, i) = world_points[i].y;
            x3d(2, i) = world_points[i].z;
        }

        typedef openMVG::robust::ACKernelAdaptorResection<
            openMVG::resection::kernel::SixPointResectionSolver,
            openMVG::resection::PixelReprojectionError,
            openMVG::robust::UnnormalizerResection, openMVG::Mat34>
            KernelType;

        // Get image dimensions from camera intrinsics
        const auto* pinhole_intrinsics =
            dynamic_cast<const openMVG::cameras::Pinhole_Intrinsic*>(
                intrinsics->intrinsics.get());
        if (!pinhole_intrinsics) {
            return false;
        }

        KernelType kernel(x2d, pinhole_intrinsics->w(), pinhole_intrinsics->h(),
                          x3d);

        Mat34 P;
        std::vector<uint32_t> vec_inliers;
        const std::pair<double, double> ACRansacOut =
            ACRANSAC(kernel, vec_inliers, max_iteration_count, &P,
                     std::numeric_limits<double>::infinity(), false);

        if (vec_inliers.size() >= KernelType::MINIMUM_SAMPLES) {
            // Extract pose from projection matrix
            Mat3 K, R;
            Vec3 t;
            openMVG::KRt_From_P(P, &K, &R, &t);
            pose->pose = openMVG::geometry::Pose3(R, -R.transpose() * t);
            return true;
        }
    } catch (...) {
        return false;
    }

    return false;
}

// Utility functions for extracting data from opaque types
bool homography_matrix_get_data(const HomographyMatrix* matrix, double* data) {
    if (!matrix || !data) {
        return false;
    }

    for (int i = 0; i < 9; ++i) {
        data[i] = matrix->matrix.data()[i];
    }
    return true;
}

bool relative_pose_info_get_rotation(const RelativePoseInfo* info,
                                     double* rotation_matrix) {
    if (!info || !rotation_matrix) {
        return false;
    }

    const openMVG::Mat3& R = info->info.relativePose.rotation();
    for (int i = 0; i < 9; ++i) {
        rotation_matrix[i] = R.data()[i];
    }
    return true;
}

bool relative_pose_info_get_translation(const RelativePoseInfo* info,
                                        double* translation_vector) {
    if (!info || !translation_vector) {
        return false;
    }

    const openMVG::Vec3& t = info->info.relativePose.translation();
    translation_vector[0] = t[0];
    translation_vector[1] = t[1];
    translation_vector[2] = t[2];
    return true;
}

bool pose3_get_rotation(const Pose3* pose, double* rotation_matrix) {
    if (!pose || !rotation_matrix) {
        return false;
    }

    const openMVG::Mat3& R = pose->pose.rotation();
    for (int i = 0; i < 9; ++i) {
        rotation_matrix[i] = R.data()[i];
    }
    return true;
}

bool pose3_get_translation(const Pose3* pose, double* translation_vector) {
    if (!pose || !translation_vector) {
        return false;
    }

    const openMVG::Vec3& t = pose->pose.translation();
    translation_vector[0] = t[0];
    translation_vector[1] = t[1];
    translation_vector[2] = t[2];
    return true;
}

}  // namespace openmvg
}  // namespace mmsolverlibs
