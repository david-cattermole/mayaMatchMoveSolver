/*
 * Copyright (C) 2020 David Cattermole.
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
 * Fanctor class for the basic brownian lens distortion model.
 */

#include "lens_model_basic.h"

// STL
#include <cmath>

// MM Solver
#include "mmSolver/utilities/debug_utils.h"


void LensModelBasic::initModel() const {
    // Initialize the 'previous' lens model in the chain.
    std::shared_ptr<LensModel> inputLensModel = LensModelBasic::getInputLensModel();
    if (inputLensModel != nullptr) {
        inputLensModel->initModel();
    }
    // This node does not need to initialize a 3DE lens plug-in.
    return;
}

void LensModelBasic::applyModelUndistort(const double xd,
                                         const double yd,
                                         double &xu,
                                         double &yu) const {
    // Apply the 'previous' lens model in the chain.
    std::shared_ptr<LensModel> inputLensModel = LensModel::getInputLensModel();
    double xdd = xd;
    double ydd = yd;
    if (inputLensModel != nullptr) {
        inputLensModel->applyModelUndistort(xdd, ydd, xdd, ydd);
    }

    // Brownian lens distortion model.
    //
    // xu = xd + ((xd - xc) * ((k1 * r2) + (k2 * r4)));
    // yu = yd + ((yd - yc) * ((k1 * r2) + (k2 * r4)));
    //
    // where:
    //   xu = undistorted image point
    //   xd = distorted image point
    //   xc = distortion center
    //   k1, k2, etc = Nth radial distortion coefficent
    //   p1, p2, etc = Nth tangential distortion coefficent
    //   r = sqrt(pow(xd - xc, 2) + pow(yd - yc, 2))
    //
    // TODO: Expose the lens distortion center as a parameter.
    double xc = 0.0;
    double yc = 0.0;

    double r = std::sqrt(std::pow(xd - xc, 2) + std::pow(yd - yc, 2));
    double r2 = std::pow(r, 2);
    double r4 = std::pow(r, 4) * 2.0;

    xu = xdd + ((xdd - xc) * ((m_k1 * r2) + (m_k2 * r4)));
    yu = ydd + ((ydd - yc) * ((m_k1 * r2) + (m_k2 * r4)));
    return;
}
