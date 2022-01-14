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

// Do not define 'min' and 'max' macros on MS Windows (with MSVC),
// added to fix errors with LDPK.
#define NOMINMAX

// STL
#include <algorithm>

// Internal
#include <utilities/debugUtils.h>
#include <core/lensModel3deClassic.h>


double LensModel3deClassic::getK1() const {
    return m_k1;
}

void LensModel3deClassic::setK1(double value) {
    m_k1 = value;
    return;
}

double LensModel3deClassic::getK2() const {
    return m_k2;
}

void LensModel3deClassic::setK2(double value) {
    m_k2 = value;
    return;
}

double LensModel3deClassic::getSqueeze() const {
    return m_squeeze;
}

void LensModel3deClassic::setSqueeze(double value) {
    m_squeeze = value;
    return;
}

LensModel* LensModel3deClassic::getInputLensModel() const {
    return m_inputLensModel;
}

void LensModel3deClassic::setInputLensModel(LensModel* value) {
    m_inputLensModel = value;
    return;
}

void LensModel3deClassic::applyModel(double xd,
                                     double yd,
                                     double &xu,
                                     double &yu) const {
    // First compute the lens distortion from the 'previous' lens
    // model.
    LensModel* inputLensModel = LensModel3deClassic::getInputLensModel();
    if (inputLensModel != NULL) {
        inputLensModel->applyModel(xd, yd, xd, yd);
    }
    
    m_lensPlugin->setParameterValue("tde4_focal_length_cm", 3.0);
    m_lensPlugin->setParameterValue("tde4_filmback_width_cm", 2.4);
    m_lensPlugin->setParameterValue("tde4_filmback_height_cm", 3.6);
    m_lensPlugin->setParameterValue("tde4_pixel_aspect", 1.0);
    m_lensPlugin->setParameterValue("tde4_lens_center_offset_x_cm", 0.0);
    m_lensPlugin->setParameterValue("tde4_lens_center_offset_y_cm", 0.0);

    m_lensPlugin->setParameterValue("Distortion", m_k1);
    m_lensPlugin->setParameterValue("Anamorphic Squeeze", m_squeeze);
    m_lensPlugin->setParameterValue("Curvature X", 0.0);
    m_lensPlugin->setParameterValue("Curvature Y", 0.0);
    m_lensPlugin->setParameterValue("Quartic Distortion", m_k2);
    m_lensPlugin->initializeParameters();

    // 'undistort' expects values 0.0 to 1.0, but our inputs are -0.5
    // to 0.5, therefore we must convert.
    m_lensPlugin->undistort(xd + 0.5, yd + 0.5, xu, yu);
    xu -= 0.5;
    yu -= 0.5;
    return;
}
