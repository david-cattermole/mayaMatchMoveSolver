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

#ifndef MM_SOLVER_SFM_SFM_UTILS_H
#define MM_SOLVER_SFM_SFM_UTILS_H

// STL
#include <cmath>
#include <memory>
#include <tuple>
#include <vector>

// OpenMVG
#ifdef MMSOLVER_USE_OPENMVG

#include <openMVG/geometry/pose3.hpp>
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
#include <mmlens/lens_model.h>

#include "mmSolver/mayahelper/maya_attr.h"
#include "mmSolver/mayahelper/maya_bundle.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_marker.h"
#include "mmSolver/mayahelper/maya_utils.h"

namespace mmsolver {
namespace sfm {

bool get_marker_coords_at_frame(const MTime &time, MarkerPtr &mkr, double &x,
                                double &y, double &weight, bool &enable);

bool get_marker_coords_at_frame(const MTime time, Marker &mkr, double &x,
                                double &y, double &weight, bool &enable);

bool get_bundle_coords_at_frame(const MTime &time, BundlePtr &bnd, double &x,
                                double &y, double &z, double &weight);

MStatus get_camera_values(const MTime &time, CameraPtr &cam, int &image_width,
                          int &image_height, double &focal_length_mm,
                          double &sensor_width_mm, double &sensor_height_mm);

bool get_camera_image_res(const uint32_t frame_num, const MTime::Unit &uiUnit,
                          Camera &cam, int &image_width, int &image_height);

void convert_camera_lens_mm_to_pixel_units(const int32_t image_width,
                                           const int32_t image_height,
                                           const double focal_length_mm,
                                           const double sensor_width_mm,
                                           double &focal_length_pix,
                                           double &ppx_pix, double &ppy_pix);

openMVG::Mat convert_marker_coords_to_matrix(
    const std::vector<std::pair<double, double>> &marker_coords);

openMVG::Mat convert_bundle_coords_to_matrix(
    const std::vector<std::tuple<double, double, double>> &bundle_coords);

openMVG::Mat convert_bundle_coords_to_matrix_flip_z(
    const std::vector<std::tuple<double, double, double>> &bundle_coords);

MStatus parseCameraSelectionList(
    const MSelectionList &selection_list, const MTime &time, CameraPtr &camera,
    Attr &camera_tx_attr, Attr &camera_ty_attr, Attr &camera_tz_attr,
    Attr &camera_rx_attr, Attr &camera_ry_attr, Attr &camera_rz_attr,
    int32_t &image_width, int32_t &image_height, double &focal_length_mm,
    double &sensor_width_mm, double &sensor_height_mm);

MStatus parse_camera_argument(const MSelectionList &selection_list,
                              CameraPtr &camera, Attr &camera_tx_attr,
                              Attr &camera_ty_attr, Attr &camera_tz_attr,
                              Attr &camera_rx_attr, Attr &camera_ry_attr,
                              Attr &camera_rz_attr);

bool add_marker_at_frame(const MTime &time, const int32_t image_width,
                         const int32_t image_height,
                         const std::shared_ptr<mmlens::LensModel> &lensModel,
                         MarkerPtr &marker,
                         std::vector<std::pair<double, double>> &marker_coords);

bool add_marker_pair_at_frame(
    const MTime &time_a, const MTime &time_b, const int32_t image_width_a,
    const int32_t image_width_b, const int32_t image_height_a,
    const int32_t image_height_b,
    const std::shared_ptr<mmlens::LensModel> &lensModel_a,
    const std::shared_ptr<mmlens::LensModel> &lensModel_b, MarkerPtr &marker_a,
    MarkerPtr &marker_b,
    std::vector<std::pair<double, double>> &marker_coords_a,
    std::vector<std::pair<double, double>> &marker_coords_b);

bool add_bundle_at_frame(
    const MTime &time, BundlePtr &bundle,
    std::vector<std::tuple<double, double, double>> &bundle_coords);

bool is_valid_pose(const openMVG::geometry::Pose3 &pose);

MTransformationMatrix convert_pose_to_maya_transform_matrix(
    const openMVG::geometry::Pose3 &pose,
    const double camera_translation_scale);

}  // namespace sfm
}  // namespace mmsolver

#endif  // MM_SOLVER_SFM_SFM_UTILS_H
