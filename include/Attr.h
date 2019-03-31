/*
 * Copyright (C) 2018, 2019 David Cattermole.
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
 * Attribute class, represents an attribute that could be modified.
 */

#ifndef MAYA_MM_SOLVER_ATTR_H
#define MAYA_MM_SOLVER_ATTR_H

#include <maya/MObject.h>
#include <maya/MString.h>
#include <maya/MPlug.h>
#include <maya/MTime.h>
#include <maya/MFnAnimCurve.h>
#include <maya/MAnimControl.h>
#include <maya/MDGModifier.h>

#include <vector>
#include <memory>


class Attr {
public:
    Attr();

    MString getName() const;

    MStatus setName(MString value);

    MString getNodeName() const;

    MStatus setNodeName(MString value);

    MString getAttrName() const;

    MStatus setAttrName(MString value);

    MObject getObject();

    MPlug getPlug();

    MObject getAttribute();

    MString getAnimCurveName();

    bool isFreeToChange();

    bool isAnimated();

    bool isConnected();

    MStatus getValue(bool &value, const MTime &time);

    MStatus getValue(int &value, const MTime &time);

    MStatus getValue(double &value, const MTime &time);

    MStatus getValue(MMatrix &value, const MTime &time);

    MStatus getValue(bool &value);

    MStatus getValue(int &value);

    MStatus getValue(double &value);

    MStatus getValue(MMatrix &value);

    MStatus setValue(double value, const MTime &time,
                     MDGModifier &dgmod, MAnimCurveChange &animChange);

    MStatus setValue(double value,
                     MDGModifier &dgmod, MAnimCurveChange &animChange);

    double getMinimumValue();

    void setMinimumValue(double value);

    double getMaximumValue();

    void setMaximumValue(double value);

private:
    MString m_nodeName;
    MString m_attrName;
    MObject m_object;
    MPlug m_plug;
    MString m_animCurveName;
    int m_animated;
    int m_connected;
    int m_isFreeToChange;
    double m_minValue;
    double m_maxValue;
};


typedef std::vector<Attr> AttrList;
typedef AttrList::iterator AttrListIt;

typedef std::shared_ptr<Attr> AttrPtr;
typedef std::vector<std::shared_ptr<Attr> > AttrPtrList;
typedef AttrPtrList::iterator AttrPtrListIt;
typedef AttrPtrList::const_iterator AttrPtrListCIt;

#endif //MAYA_MM_SOLVER_ATTR_H
