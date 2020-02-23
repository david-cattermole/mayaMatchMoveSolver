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


#include <maya/MIOStream.h>

#include <maya/MString.h>
#include <maya/MArgList.h>

#include <maya/MPxData.h>
#include <maya/MTypeId.h>


class MMLensData : public MPxData {
public:
    MMLensData();
    virtual ~MMLensData();

    virtual MStatus readASCII(const MArgList&, unsigned& lastElement);
    virtual MStatus readBinary(istream& in, unsigned length);
    virtual MStatus writeASCII(ostream& out);
    virtual MStatus writeBinary(ostream& out);

    virtual void copy(const MPxData&);
    MTypeId typeId() const;
    MString name() const;

    double value() const;
    void setValue(double);

    static MString typeName();

    static const MString m_typeName;
    static const MTypeId m_id;
    static void* creator();

private:
    double fValue;
};
