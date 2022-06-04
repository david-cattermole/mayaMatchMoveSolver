/*
 * Copyright (C) 2020,2022 David Cattermole.
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
 * Class for a pass-through 'null' lens distortion model.
 */

#include "lens_model_passthrough.h"

void LensModelPassthrough::applyModelUndistort(const double xd, const double yd,
                                               double &xu, double &yu) {
    // Apply the 'previous' lens model in the chain.
    std::shared_ptr<LensModel> inputLensModel = LensModel::getInputLensModel();
    double xdd = xd;
    double ydd = yd;
    if (inputLensModel != nullptr) {
        inputLensModel->applyModelUndistort(xdd, ydd, xdd, ydd);
    }

    // Do nothing. This LensModel is a pass-through only.
    xu = xdd;
    yu = ydd;
    return;
}

void LensModelPassthrough::applyModelDistort(const double xd, const double yd,
                                             double &xu, double &yu) {
    // Apply the 'previous' lens model in the chain.
    std::shared_ptr<LensModel> inputLensModel = LensModel::getInputLensModel();
    double xdd = xd;
    double ydd = yd;
    if (inputLensModel != nullptr) {
        inputLensModel->applyModelDistort(xdd, ydd, xdd, ydd);
    }

    // Do nothing. This LensModel is a pass-through only.
    xu = xdd;
    yu = ydd;
    return;
}

mmhash::HashValue LensModelPassthrough::hashValue() {
    // Apply the 'previous' lens model in the chain.
    std::shared_ptr<LensModel> inputLensModel = LensModel::getInputLensModel();
    mmhash::HashValue hash = 0;
    if (inputLensModel != nullptr) {
        hash = inputLensModel->hashValue();
    }

    // Do nothing. This LensModel is a pass-through only.
    return hash;
}
