/*
 * Copyright (C) 2022, 2023 David Cattermole.
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
 * Class for the 3DE classic lens distortion model.
 */

#include <ldpk/ldpk_classic_ld_model_distortion.h>
#include <ldpk/ldpk_vec2d.h>
#include <mmcore/mmdata.h>
#include <mmcore/mmhash.h>
#include <mmlens/lens_model_3de_classic.h>
#include <mmlens/lib.h>

#include <functional>

#include "distortion_operations.h"
#include "distortion_structs.h"

namespace mmlens {

void LensModel3deClassic::applyModelUndistort(const double xd, const double yd,
                                              double &xu, double &yu) {
    if (m_state != LensModelState::kClean) {
        m_film_back_radius_cm =
            mmlens::compute_diagonal_normalized_camera_factor(m_camera);
        m_state = LensModelState::kClean;
    }

    // Apply the 'previous' lens model in the chain.
    std::shared_ptr<LensModel> inputLensModel = LensModel::getInputLensModel();
    double xdd = xd;
    double ydd = yd;
    if (inputLensModel != nullptr) {
        inputLensModel->applyModelUndistort(xdd, ydd, xdd, ydd);
    }

    auto distortion = Distortion3deClassic();
    distortion.set_parameter(0, m_lens.distortion);
    distortion.set_parameter(1, m_lens.anamorphic_squeeze);
    distortion.set_parameter(2, m_lens.curvature_x);
    distortion.set_parameter(3, m_lens.curvature_y);
    distortion.set_parameter(4, m_lens.quartic_distortion);
    distortion.initialize_parameters(m_camera);

    const auto direction = DistortionDirection::kUndistort;

    // 'undistort' expects values 0.0 to 1.0, but our inputs are -0.5
    // to 0.5, therefore we must convert.
    auto out_xy = apply_lens_distortion_once<direction, double, double,
                                             Distortion3deClassic>(
        xdd + 0.5, ydd + 0.5, m_camera, m_film_back_radius_cm, distortion);

    // Convert back to -0.5 to 0.5 coordinate space.
    xu = out_xy.first - 0.5;
    yu = out_xy.second - 0.5;
    return;
}

void LensModel3deClassic::applyModelDistort(const double xd, const double yd,
                                            double &xu, double &yu) {
    if (m_state != LensModelState::kClean) {
        m_film_back_radius_cm =
            mmlens::compute_diagonal_normalized_camera_factor(m_camera);
        m_state = LensModelState::kClean;
    }

    // Apply the 'previous' lens model in the chain.
    std::shared_ptr<LensModel> inputLensModel = LensModel::getInputLensModel();
    double xdd = xd;
    double ydd = yd;
    if (inputLensModel != nullptr) {
        inputLensModel->applyModelDistort(xdd, ydd, xdd, ydd);
    }

    auto distortion = Distortion3deClassic();
    distortion.set_parameter(0, m_lens.distortion);
    distortion.set_parameter(1, m_lens.anamorphic_squeeze);
    distortion.set_parameter(2, m_lens.curvature_x);
    distortion.set_parameter(3, m_lens.curvature_y);
    distortion.set_parameter(4, m_lens.quartic_distortion);
    distortion.initialize_parameters(m_camera);

    const auto direction = DistortionDirection::kRedistort;

    // The lens distortion operation expects values 0.0 to 1.0, but
    // our inputs are -0.5 to 0.5, therefore we must convert.
    auto out_xy = apply_lens_distortion_once<direction, double, double,
                                             Distortion3deClassic>(
        xdd + 0.5, ydd + 0.5, m_camera, m_film_back_radius_cm, distortion);

    // Convert back to -0.5 to 0.5 coordinate space.
    xu = out_xy.first - 0.5;
    yu = out_xy.second - 0.5;
    return;
}

mmhash::HashValue LensModel3deClassic::hashValue() {
    // Apply the 'previous' lens model in the chain.
    std::shared_ptr<LensModel> inputLensModel = LensModel::getInputLensModel();
    mmhash::HashValue hash = 0;
    if (inputLensModel != nullptr) {
        hash = inputLensModel->hashValue();
    }

    mmhash::combine(hash, std::hash<double>()(m_camera.focal_length_cm));
    mmhash::combine(hash, std::hash<double>()(m_camera.film_back_width_cm));
    mmhash::combine(hash, std::hash<double>()(m_camera.film_back_height_cm));
    mmhash::combine(hash, std::hash<double>()(m_camera.pixel_aspect));
    mmhash::combine(hash,
                    std::hash<double>()(m_camera.lens_center_offset_x_cm));
    mmhash::combine(hash,
                    std::hash<double>()(m_camera.lens_center_offset_y_cm));

    mmhash::combine(hash, std::hash<double>()(m_lens.distortion));
    mmhash::combine(hash, std::hash<double>()(m_lens.anamorphic_squeeze));
    mmhash::combine(hash, std::hash<double>()(m_lens.curvature_x));
    mmhash::combine(hash, std::hash<double>()(m_lens.curvature_y));
    mmhash::combine(hash, std::hash<double>()(m_lens.quartic_distortion));

    return hash;
}

}  // namespace mmlens
