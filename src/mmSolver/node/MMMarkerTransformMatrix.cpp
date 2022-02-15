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
#include <maya/MPxTransformationMatrix.h>
#include <maya/MGlobal.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MTransformationMatrix.h>
#include <maya/MIOStream.h>

// MM Solver
#include "mmSolver/nodeTypeIds.h"

namespace mmsolver {

MTypeId MMMarkerTransformMatrix::m_id(MM_MARKER_TRANSFORM_MATRIX_TYPE_ID);


MMMarkerTransformMatrix::MMMarkerTransformMatrix() : m_value(nullptr) {}

MPxTransformationMatrix *MMMarkerTransformMatrix::creator() {
    return new MMMarkerTransformMatrix();
}

LensModel* MMMarkerTransformMatrix::getLensModel() const {
    return m_value;
}

void MMMarkerTransformMatrix::setLensModel(LensModel* value) {
    m_value = value;
}


// This method will be used to return information to Maya. Use the
// attributes which are outside of the regular transform attributes to
// build a new matrix.  This new matrix will be passed back to Maya.
MMatrix MMMarkerTransformMatrix::asMatrix() const {
    MStatus status;
    // Get the current transform matrix
    MMatrix m = ParentClass::asMatrix();

    MTransformationMatrix tm(m);

    // Calculate and add lens distortion to the translates of the
    // matrix.
    LensModel* lensModel = getLensModel();
    if (lensModel != nullptr) {
        MVector translate = tm.getTranslation(MSpace::kTransform, &status);
        CHECK_MSTATUS(status);
        MVector out_translate(translate);

        lensModel->applyModel(
            translate.x, translate.y,
            out_translate.x, out_translate.y);

        status = tm.setTranslation(out_translate, MSpace::kTransform);
        CHECK_MSTATUS(status);
    }

    return tm.asMatrix();
}

MMatrix MMMarkerTransformMatrix::asMatrix(double percent) const {
    MMatrix m = ParentClass::asMatrix(percent);

    // TODO: Calculate and add lens distortion to the translates of
    // the matrix.

    return m;
}

} // namespace mmsolver
