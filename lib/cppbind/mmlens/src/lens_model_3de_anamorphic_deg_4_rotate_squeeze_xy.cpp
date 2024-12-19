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
 * Class for the 3DE Anamorphic Degree 4 Lens Distortion with Rotation
 * and Squeeze X/Y.
 */

#include <mmcore/mmhash.h>
#include <mmlens/lens_model_3de_anamorphic_deg_4_rotate_squeeze_xy.h>
#include <mmlens/lib.h>

#include <functional>

#include "distortion_operations.h"
#include "distortion_structs.h"

namespace mmlens {

void LensModel3deAnamorphicDeg4RotateSqueezeXY::applyModelUndistort(
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

    auto distortion = Distortion3deAnamorphicStdDeg4();
    distortion.set_parameter(0, m_lens.degree2_cx02);
    distortion.set_parameter(1, m_lens.degree2_cy02);
    distortion.set_parameter(2, m_lens.degree2_cx22);
    distortion.set_parameter(3, m_lens.degree2_cy22);
    distortion.set_parameter(4, m_lens.degree4_cx04);
    distortion.set_parameter(5, m_lens.degree4_cy04);
    distortion.set_parameter(6, m_lens.degree4_cx24);
    distortion.set_parameter(7, m_lens.degree4_cy24);
    distortion.set_parameter(8, m_lens.degree4_cx44);
    distortion.set_parameter(9, m_lens.degree4_cy44);
    distortion.set_parameter(10, m_lens.lens_rotation);
    distortion.set_parameter(11, m_lens.squeeze_x);
    distortion.set_parameter(12, m_lens.squeeze_y);
    distortion.initialize_parameters(m_camera);

    // 'undistort' expects values 0.0 to 1.0, but our inputs are -0.5
    // to 0.5, therefore we must convert.
    const auto direction = DistortionDirection::kUndistort;
    auto out_xy = apply_lens_distortion_once<direction, double, double,
                                             Distortion3deAnamorphicStdDeg4>(
        xdd + 0.5, ydd + 0.5, m_camera, m_film_back_radius_cm, distortion);

    // Convert back to -0.5 to 0.5 coordinate space.
    xu = out_xy.first - 0.5;
    yu = out_xy.second - 0.5;
    return;
}

void LensModel3deAnamorphicDeg4RotateSqueezeXY::applyModelDistort(
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

    auto distortion = Distortion3deAnamorphicStdDeg4();
    distortion.set_parameter(0, m_lens.degree2_cx02);
    distortion.set_parameter(1, m_lens.degree2_cy02);
    distortion.set_parameter(2, m_lens.degree2_cx22);
    distortion.set_parameter(3, m_lens.degree2_cy22);
    distortion.set_parameter(4, m_lens.degree4_cx04);
    distortion.set_parameter(5, m_lens.degree4_cy04);
    distortion.set_parameter(6, m_lens.degree4_cx24);
    distortion.set_parameter(7, m_lens.degree4_cy24);
    distortion.set_parameter(8, m_lens.degree4_cx44);
    distortion.set_parameter(9, m_lens.degree4_cy44);
    distortion.set_parameter(10, m_lens.lens_rotation);
    distortion.set_parameter(11, m_lens.squeeze_x);
    distortion.set_parameter(12, m_lens.squeeze_y);
    distortion.initialize_parameters(m_camera);

    // 'undistort' expects values 0.0 to 1.0, but our inputs are -0.5
    // to 0.5, therefore we must convert.
    const auto direction = DistortionDirection::kRedistort;
    auto out_xy = apply_lens_distortion_once<direction, double, double,
                                             Distortion3deAnamorphicStdDeg4>(
        xdd + 0.5, ydd + 0.5, m_camera, m_film_back_radius_cm, distortion);

    // Convert back to -0.5 to 0.5 coordinate space.
    xu = out_xy.first - 0.5;
    yu = out_xy.second - 0.5;
    return;
}

mmhash::HashValue LensModel3deAnamorphicDeg4RotateSqueezeXY::hashValue() {
    // Apply the 'previous' lens model in the chain.
    std::shared_ptr<LensModel> inputLensModel = LensModel::getInputLensModel();
    mmhash::HashValue hash = 0;
    if (inputLensModel != nullptr) {
        hash = inputLensModel->hashValue();
    }

    hashCameraParameters(hash);

    addToHash(hash, m_lens.degree2_cx02);
    addToHash(hash, m_lens.degree2_cy02);
    addToHash(hash, m_lens.degree2_cx22);
    addToHash(hash, m_lens.degree2_cy22);

    addToHash(hash, m_lens.degree4_cx04);
    addToHash(hash, m_lens.degree4_cy04);
    addToHash(hash, m_lens.degree4_cx24);
    addToHash(hash, m_lens.degree4_cy24);
    addToHash(hash, m_lens.degree4_cx44);
    addToHash(hash, m_lens.degree4_cy44);

    addToHash(hash, m_lens.lens_rotation);
    addToHash(hash, m_lens.squeeze_x);
    addToHash(hash, m_lens.squeeze_y);

    return hash;
}

}  // namespace mmlens
