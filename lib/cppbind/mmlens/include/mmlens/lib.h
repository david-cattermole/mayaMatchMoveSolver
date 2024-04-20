/*
 * Copyright (C) 2023 David Cattermole.
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
 */

#ifndef MM_LENS_LIB_H
#define MM_LENS_LIB_H

#include <cmath>
#include <memory>
#include <string>

#include "_cxx.h"
#include "_cxxbridge.h"
#include "_symbol_export.h"
#include "_types.h"

namespace mmlens {

inline double compute_diagonal_normalized_camera_factor(
    const CameraParameters parameters) {
    double w_fb_cm = parameters.film_back_width_cm;
    double h_fb_cm = parameters.film_back_height_cm;
    double film_back_radius_cm =
        std::sqrt(w_fb_cm * w_fb_cm + h_fb_cm * h_fb_cm) / 2.0;
    return film_back_radius_cm;
}

inline mmdata::Vector2D unit_to_diagonal_normalized(
    const CameraParameters parameters, const double film_back_radius_cm,
    const mmdata::Vector2D& point_unit) {
    const double w_fb_cm = parameters.film_back_width_cm;
    const double h_fb_cm = parameters.film_back_height_cm;
    const double x_lco_cm = parameters.lens_center_offset_x_cm;
    const double y_lco_cm = parameters.lens_center_offset_y_cm;
    const mmdata::Vector2D point_cm(
        ((point_unit.x_ - 1.0 / 2.0) * w_fb_cm - x_lco_cm) /
            film_back_radius_cm,
        ((point_unit.y_ - 1.0 / 2.0) * h_fb_cm - y_lco_cm) /
            film_back_radius_cm);
    return point_cm;
}

inline mmdata::Vector2D diagonal_normalized_to_unit(
    CameraParameters parameters, const double film_back_radius_cm,
    const mmdata::Vector2D& point_dn) {
    const double w_fb_cm = parameters.film_back_width_cm;
    const double h_fb_cm = parameters.film_back_height_cm;
    const double x_lco_cm = parameters.lens_center_offset_x_cm;
    const double y_lco_cm = parameters.lens_center_offset_y_cm;

    mmdata::Vector2D point_cm(point_dn.x_ * film_back_radius_cm,
                              point_dn.y_ * film_back_radius_cm);
    auto x_cm = (w_fb_cm / 2) + x_lco_cm;
    auto y_cm = (h_fb_cm / 2) + y_lco_cm;
    point_cm.x_ += x_cm;
    point_cm.y_ += y_cm;
    return mmdata::Vector2D(point_cm.x_ / w_fb_cm, point_cm.y_ / h_fb_cm);
}

}  // namespace mmlens

#endif  // MM_LENS_LIB_H
