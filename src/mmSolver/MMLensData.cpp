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
 * Holds Lens Distortion information in the Maya DG.
 */

#include "MMLensData.h"

// MM Solver
#include "mmSolver/nodeTypeIds.h"
#include "mmSolver/lens/lens_model.h"

namespace mmsolver {

const MTypeId MMLensData::m_id(MM_LENS_DATA_TYPE_ID);
const MString MMLensData::m_typeName(MM_LENS_DATA_TYPE_NAME);


void* MMLensData::creator() {
    return new MMLensData;
}

MMLensData::MMLensData()
    : m_value(nullptr), MPxData() {
}

MMLensData::~MMLensData() {}

LensModel* MMLensData::getValue() const {
    return m_value;
}

void MMLensData::setValue(LensModel* value) {
    m_value = value;
}

void MMLensData::copy(const MPxData& other) {
    m_value = ((const MMLensData&)other).m_value;
}

MTypeId MMLensData::typeId() const {
    return MMLensData::m_id;
}

// Function required by base-class.
MString MMLensData::name() const {
    return MMLensData::m_typeName;
}

// This is static, so to be called by plug-in initlaiize functions.
MString MMLensData::typeName() {
    return MString(MM_LENS_DATA_TYPE_NAME);
}

MStatus MMLensData::readASCII(const MArgList& /*args*/,
                              unsigned& /*lastParsedElement*/) {
    return MS::kSuccess;
}

MStatus MMLensData::writeASCII(ostream& /*out*/) {
    return MS::kSuccess;
}

MStatus MMLensData::readBinary(istream& /*in*/, unsigned) {
    return MS::kSuccess;
}

MStatus MMLensData::writeBinary(ostream& /*out*/) {
    return MS::kSuccess;
}

} // namespace mmsolver
