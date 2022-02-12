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
 * class for the basic brownian lens distortion model.
 */

#include "lens_model_3de_classic.h"

// MM Solver
#include "mmSolver/utilities/debug_utils.h"


double LensModel3deClassic::getDistortion() const {
    return m_distortion;
}

void LensModel3deClassic::setDistortion(double value) {
    m_distortion = value;
    return;
}

double LensModel3deClassic::getAnamorphicSqueeze() const {
    return m_anamorphicSqueeze;
}

void LensModel3deClassic::setAnamorphicSqueeze(double value) {
    m_anamorphicSqueeze = value;
    return;
}

double LensModel3deClassic::getCurvatureX() const {
    return m_curvatureX;
}

void LensModel3deClassic::setCurvatureX(double value) {
    m_curvatureX = value;
    return;
}

double LensModel3deClassic::getCurvatureY() const {
    return m_curvatureY;
}

void LensModel3deClassic::setCurvatureY(double value) {
    m_curvatureY = value;
    return;
}

double LensModel3deClassic::getQuarticDistortion() const {
    return m_quarticDistortion;
}

void LensModel3deClassic::setQuarticDistortion(double value) {
    m_quarticDistortion = value;
    return;
}

LensModel* LensModel3deClassic::getInputLensModel() const {
    return m_inputLensModel;
}

void LensModel3deClassic::setInputLensModel(LensModel* value) {
    m_inputLensModel = value;
    return;
}

void LensModel3deClassic::initModel() const {
    // Initialize the 'previous' lens model in the chain.
    LensModel* inputLensModel = LensModel3deClassic::getInputLensModel();
    if (inputLensModel != nullptr) {
        inputLensModel->initModel();
    }

    m_lensPlugin->setParameterValue("tde4_focal_length_cm", LensModel::m_focalLength_cm);
    m_lensPlugin->setParameterValue("tde4_filmback_width_cm", LensModel::m_filmBackWidth_cm);
    m_lensPlugin->setParameterValue("tde4_filmback_height_cm", LensModel::m_filmBackHeight_cm);
    m_lensPlugin->setParameterValue("tde4_pixel_aspect", LensModel::m_pixelAspect);
    m_lensPlugin->setParameterValue("tde4_lens_center_offset_x_cm", LensModel::m_lensCenterOffsetX_cm);
    m_lensPlugin->setParameterValue("tde4_lens_center_offset_y_cm", LensModel::m_lensCenterOffsetX_cm);

    m_lensPlugin->setParameterValue("Distortion", m_distortion);
    m_lensPlugin->setParameterValue("Anamorphic Squeeze", m_anamorphicSqueeze);
    m_lensPlugin->setParameterValue("Curvature X", m_curvatureX);
    m_lensPlugin->setParameterValue("Curvature Y", m_curvatureY);
    m_lensPlugin->setParameterValue("Quartic Distortion", m_quarticDistortion);
    m_lensPlugin->initializeParameters();
    return;
}

void LensModel3deClassic::applyModel(double xd,
                                     double yd,
                                     double &xu,
                                     double &yu) const {
    // Apply the 'previous' lens model in the chain.
    LensModel* inputLensModel = LensModel3deClassic::getInputLensModel();
    if (inputLensModel != nullptr) {
        inputLensModel->applyModel(xd, yd, xd, yd);
    }

    // 'undistort' expects values 0.0 to 1.0, but our inputs are -0.5
    // to 0.5, therefore we must convert.
    m_lensPlugin->undistort(xd + 0.5, yd + 0.5, xu, yu);
    xu -= 0.5;
    yu -= 0.5;
    return;
}
