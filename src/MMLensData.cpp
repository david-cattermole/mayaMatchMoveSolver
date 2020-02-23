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


#include <nodeTypeIds.h>

#include <MMLensData.h>


const MTypeId MMLensData::m_id(MM_LENS_DATA_TYPE_ID);
const MString MMLensData::m_typeName(MM_LENS_DATA_TYPE_NAME);


void* MMLensData::creator() {
    return new MMLensData;
}

MMLensData::MMLensData()
    :fValue(0), MPxData() {
}

MMLensData::~MMLensData() {}

double MMLensData::value() const {
    return fValue;
}

void MMLensData::setValue(double newValue) {
    fValue = newValue;
}

void MMLensData::copy (const MPxData& other){
    fValue = ((const MMLensData&)other).fValue;
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

MStatus MMLensData::readASCII(const MArgList& args,
                              unsigned& lastParsedElement) {
    MStatus status;
    if(args.length() > 0) {
        fValue = args.asDouble(lastParsedElement++, &status);
        return status;
    } else {
        return MS::kFailure;
    }
}

MStatus MMLensData::writeASCII(ostream& out) {
    out << fValue << " ";
    return MS::kSuccess;
}

MStatus MMLensData::readBinary(istream& in, unsigned) {
    in.read((char*) &fValue, sizeof(fValue));
    return in.fail() ? MS::kFailure : MS::kSuccess;
}

MStatus MMLensData::writeBinary(ostream& out) {
    out.write((char*) &fValue, sizeof( fValue));
    return out.fail() ? MS::kFailure : MS::kSuccess;
}
