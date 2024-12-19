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
 * Class for the 3DE Radial (Decentered) Degree 4 Cylindric Lens
 * Distortion.
 */

#include <mmcore/mmhash.h>
#include <mmlens/lens_model_3de_radial_decentered_deg_4_cylindric.h>
#include <mmlens/lib.h>

#include <functional>

#include "distortion_operations.h"
#include "distortion_structs.h"

namespace mmlens {

void LensModel3deRadialDecenteredDeg4Cylindric::applyModelUndistort(
    const double xd, const double yd, double &xu, double &yu) {
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

    auto distortion = Distortion3deRadialStdDeg4();
    distortion.set_parameter(0, m_lens.degree2_distortion);
    distortion.set_parameter(1, m_lens.degree2_u);
    distortion.set_parameter(2, m_lens.degree2_v);
    distortion.set_parameter(3, m_lens.degree4_distortion);
    distortion.set_parameter(4, m_lens.degree4_u);
    distortion.set_parameter(5, m_lens.degree4_v);
    distortion.set_parameter(6, m_lens.cylindric_direction);
    distortion.set_parameter(7, m_lens.cylindric_bending);
    distortion.initialize_parameters(m_camera);

    const auto direction = DistortionDirection::kUndistort;

    // 'undistort' expects values 0.0 to 1.0, but our inputs are -0.5
    // to 0.5, therefore we must convert.
    auto out_xy = apply_lens_distortion_once<direction, double, double,
                                             Distortion3deRadialStdDeg4>(
        xdd + 0.5, ydd + 0.5, m_camera, m_film_back_radius_cm, distortion);

    // Convert back to -0.5 to 0.5 coordinate space.
    xu = out_xy.first - 0.5;
    yu = out_xy.second - 0.5;
    return;
}

void LensModel3deRadialDecenteredDeg4Cylindric::applyModelDistort(
    const double xd, const double yd, double &xu, double &yu) {
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

    auto distortion = Distortion3deRadialStdDeg4();
    distortion.set_parameter(0, m_lens.degree2_distortion);
    distortion.set_parameter(1, m_lens.degree2_u);
    distortion.set_parameter(2, m_lens.degree2_v);
    distortion.set_parameter(3, m_lens.degree4_distortion);
    distortion.set_parameter(4, m_lens.degree4_u);
    distortion.set_parameter(5, m_lens.degree4_v);
    distortion.set_parameter(6, m_lens.cylindric_direction);
    distortion.set_parameter(7, m_lens.cylindric_bending);
    distortion.initialize_parameters(m_camera);

    const auto direction = DistortionDirection::kRedistort;

    // 'undistort' expects values 0.0 to 1.0, but our inputs are -0.5
    // to 0.5, therefore we must convert.
    auto out_xy = apply_lens_distortion_once<direction, double, double,
                                             Distortion3deRadialStdDeg4>(
        xdd + 0.5, ydd + 0.5, m_camera, m_film_back_radius_cm, distortion);

    // Convert back to -0.5 to 0.5 coordinate space.
    xu = out_xy.first - 0.5;
    yu = out_xy.second - 0.5;
    return;
}

mmhash::HashValue LensModel3deRadialDecenteredDeg4Cylindric::hashValue() {
    // Apply the 'previous' lens model in the chain.
    std::shared_ptr<LensModel> inputLensModel = LensModel::getInputLensModel();
    mmhash::HashValue hash = 0;
    if (inputLensModel != nullptr) {
        hash = inputLensModel->hashValue();
    }

    hashCameraParameters(hash);

    addToHash(hash, m_lens.degree2_distortion);
    addToHash(hash, m_lens.degree2_u);
    addToHash(hash, m_lens.degree2_v);

    addToHash(hash, m_lens.degree4_distortion);
    addToHash(hash, m_lens.degree4_u);
    addToHash(hash, m_lens.degree4_v);

    addToHash(hash, m_lens.cylindric_direction);
    addToHash(hash, m_lens.cylindric_bending);

    return hash;
}

}  // namespace mmlens
