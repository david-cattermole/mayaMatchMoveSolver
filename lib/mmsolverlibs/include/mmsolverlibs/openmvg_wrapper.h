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
 * OpenMVG API wrapper for OpenMVG functionality.
 * This provides a clean C API to decouple Maya code from OpenMVG.
 */

#ifndef MMSOLVERLIBS_OPENMVG_WRAPPER_H
#define MMSOLVERLIBS_OPENMVG_WRAPPER_H

#include <cstddef>
#include <cstdint>

namespace mmsolverlibs {
namespace openmvg {

// Forward declarations for opaque types
struct HomographyMatrix;
struct RelativePoseInfo;
struct CameraIntrinsics;
struct Pose3;

// Point structures
struct Point2d {
    double x;
    double y;
};

struct Point3d {
    double x;
    double y;
    double z;
};

// Homography functions
HomographyMatrix* homography_matrix_new();
void homography_matrix_free(HomographyMatrix* matrix);

bool compute_homography(std::int32_t image_width_a, std::int32_t image_width_b,
                        std::int32_t image_height_a,
                        std::int32_t image_height_b,
                        const Point2d* marker_coords_a,
                        std::size_t num_markers_a,
                        const Point2d* marker_coords_b,
                        std::size_t num_markers_b,
                        HomographyMatrix* homography_matrix);

bool robust_homography(
    const double* x1_data, std::size_t x1_rows, std::size_t x1_cols,
    const double* x2_data, std::size_t x2_rows, std::size_t x2_cols,
    HomographyMatrix* homography_matrix, std::uint32_t image_width_1,
    std::uint32_t image_height_1, std::uint32_t image_width_2,
    std::uint32_t image_height_2, std::uint32_t max_iteration_count);

// Camera relative pose functions
RelativePoseInfo* relative_pose_info_new();
void relative_pose_info_free(RelativePoseInfo* info);

CameraIntrinsics* camera_intrinsics_new_pinhole(std::uint32_t width,
                                                std::uint32_t height,
                                                double focal_length, double ppx,
                                                double ppy);
void camera_intrinsics_free(CameraIntrinsics* intrinsics);

bool robust_relative_pose(
    const CameraIntrinsics* intrinsics1, const CameraIntrinsics* intrinsics2,
    const double* x1_data, std::size_t x1_rows, std::size_t x1_cols,
    const double* x2_data, std::size_t x2_rows, std::size_t x2_cols,
    RelativePoseInfo* relative_pose_info, std::uint32_t image_width_1,
    std::uint32_t image_height_1, std::uint32_t image_width_2,
    std::uint32_t image_height_2, std::uint32_t max_iteration_count);

bool compute_relative_pose(
    std::int32_t image_width_a, std::int32_t image_width_b,
    std::int32_t image_height_a, std::int32_t image_height_b,
    double focal_length_pix_a, double focal_length_pix_b, double ppx_pix_a,
    double ppx_pix_b, double ppy_pix_a, double ppy_pix_b,
    const Point2d* marker_coords_a, std::size_t num_markers_a,
    const Point2d* marker_coords_b, std::size_t num_markers_b,
    RelativePoseInfo* relative_pose_info, Point3d* triangulated_points,
    std::size_t* num_triangulated_points);

// Camera from known points (PnP) functions
Pose3* pose3_new();
void pose3_free(Pose3* pose);

bool solve_pnp_p3p_nordberg(const Point3d* world_points,
                            std::size_t num_world_points,
                            const Point2d* image_points,
                            std::size_t num_image_points,
                            const CameraIntrinsics* intrinsics, Pose3* pose,
                            std::uint32_t max_iteration_count);

// Utility functions for extracting data from opaque types
bool homography_matrix_get_data(const HomographyMatrix* matrix, double* data);
bool relative_pose_info_get_rotation(const RelativePoseInfo* info,
                                     double* rotation_matrix);
bool relative_pose_info_get_translation(const RelativePoseInfo* info,
                                        double* translation_vector);
bool pose3_get_rotation(const Pose3* pose, double* rotation_matrix);
bool pose3_get_translation(const Pose3* pose, double* translation_vector);

}  // namespace openmvg
}  // namespace mmsolverlibs

#endif  // MMSOLVERLIBS_OPENMVG_WRAPPER_H
