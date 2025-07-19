/*
 * Copyright (C) 2018, 2019, 2020 David Cattermole.
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
 * A transform matrix that can have translate values offset with lens
 * distortion models.
 */

#include "MMMarkerTransformMatrix.h"

// Maya
#include <maya/MFnNumericAttribute.h>
#include <maya/MGlobal.h>
#include <maya/MIOStream.h>
#include <maya/MPxTransformationMatrix.h>
#include <maya/MTransformationMatrix.h>

// MM Solver
#include <mmcore/mmmath.h>

#include "mmSolver/nodeTypeIds.h"
#include "mmSolver/utilities/assert_utils.h"

namespace mmsolver {

MTypeId MMMarkerTransformMatrix::m_id(MM_MARKER_TRANSFORM_MATRIX_TYPE_ID);

MMMarkerTransformMatrix::MMMarkerTransformMatrix() : m_value(nullptr) {}

MPxTransformationMatrix *MMMarkerTransformMatrix::creator() {
    return new MMMarkerTransformMatrix();
}

std::shared_ptr<mmlens::LensModel> MMMarkerTransformMatrix::getLensModel()
    const {
    return m_value;
}

void MMMarkerTransformMatrix::setLensModel(
    std::shared_ptr<mmlens::LensModel> value) {
    m_value = value;
}

// This method will be used to return information to Maya. Use the
// attributes which are outside of the regular transform attributes to
// build a new matrix.  This new matrix will be passed back to Maya.
MMatrix MMMarkerTransformMatrix::asMatrix() const {
    return MMMarkerTransformMatrix::asMatrix(1.0);
}

MMatrix MMMarkerTransformMatrix::asMatrix(double percent) const {
    MStatus status;
    // Get the current transform matrix
    MMatrix m = ParentClass::asMatrix();

    MTransformationMatrix tm(m);

    // Calculate and add lens distortion to the translates of the
    // matrix.
    std::shared_ptr<mmlens::LensModel> lensModel = getLensModel();
    if (lensModel != nullptr) {
        MVector translate = tm.getTranslation(MSpace::kTransform, &status);
        MMSOLVER_CHECK_MSTATUS(status);
        MVector out_translate(translate);

        double temp_out_x = translate.x;
        double temp_out_y = translate.y;
        lensModel->applyModelUndistort(translate.x, translate.y, temp_out_x,
                                       temp_out_y);
        if (percent == 1.0) {
            if (std::isfinite(temp_out_x)) {
                out_translate.x = temp_out_x;
            }
            if (std::isfinite(temp_out_y)) {
                out_translate.y = temp_out_y;
            }
        } else {
            if (std::isfinite(temp_out_x)) {
                out_translate.x =
                    mmmath::lerp(translate.x, temp_out_x, percent);
            }
            if (std::isfinite(temp_out_y)) {
                out_translate.y =
                    mmmath::lerp(translate.y, temp_out_y, percent);
            }
        }

        status = tm.setTranslation(out_translate, MSpace::kTransform);
        MMSOLVER_CHECK_MSTATUS(status);
    }

    return tm.asMatrix();
}

}  // namespace mmsolver
