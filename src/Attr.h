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
#include <maya/MDistance.h>
#include <maya/MAngle.h>

#include <vector>
#include <memory>

#include <mayaUtils.h>

// The underlying attribute data type.
#define ATTR_DATA_TYPE_UNKNOWN (0)
#define ATTR_DATA_TYPE_LINEAR (1)
#define ATTR_DATA_TYPE_ANGLE (2)
#define ATTR_DATA_TYPE_NUMERIC (3)

// Solver Types of Attributes.
#define ATTR_SOLVER_TYPE_UNKNOWN      (0)
#define ATTR_SOLVER_TYPE_BUNDLE_TX    (1)
#define ATTR_SOLVER_TYPE_BUNDLE_TY    (2)
#define ATTR_SOLVER_TYPE_BUNDLE_TZ    (3)
#define ATTR_SOLVER_TYPE_CAMERA_TX    (4)
#define ATTR_SOLVER_TYPE_CAMERA_TY    (5)
#define ATTR_SOLVER_TYPE_CAMERA_TZ    (6)
#define ATTR_SOLVER_TYPE_CAMERA_RX    (7)
#define ATTR_SOLVER_TYPE_CAMERA_RY    (8)
#define ATTR_SOLVER_TYPE_CAMERA_RZ    (9)
#define ATTR_SOLVER_TYPE_CAMERA_SX    (10)
#define ATTR_SOLVER_TYPE_CAMERA_SY    (11)
#define ATTR_SOLVER_TYPE_CAMERA_SZ    (12)
#define ATTR_SOLVER_TYPE_CAMERA_FOCAL (13)
#define ATTR_SOLVER_TYPE_TRANSFORM_TX (14)
#define ATTR_SOLVER_TYPE_TRANSFORM_TY (15)
#define ATTR_SOLVER_TYPE_TRANSFORM_TZ (16)
#define ATTR_SOLVER_TYPE_TRANSFORM_RX (17)
#define ATTR_SOLVER_TYPE_TRANSFORM_RY (18)
#define ATTR_SOLVER_TYPE_TRANSFORM_RZ (19)
#define ATTR_SOLVER_TYPE_TRANSFORM_SX (20)
#define ATTR_SOLVER_TYPE_TRANSFORM_SY (21)
#define ATTR_SOLVER_TYPE_TRANSFORM_SZ (22)


inline
unsigned int computeSolverAttrType(unsigned int objectType,
                                   MString attrName) {
    unsigned int attr_type = ATTR_SOLVER_TYPE_UNKNOWN;
    if (objectType == OBJECT_TYPE_BUNDLE) {
        // A bundle node.
        if (attrName == "translateX" || attrName == "tx") {
            attr_type = ATTR_SOLVER_TYPE_BUNDLE_TX;
        } else if (attrName == "translateY" || attrName == "ty") {
            attr_type = ATTR_SOLVER_TYPE_BUNDLE_TY;
        } else if (attrName == "translateZ" || attrName == "tz") {
            attr_type = ATTR_SOLVER_TYPE_BUNDLE_TZ;
        }
    } else if (objectType == OBJECT_TYPE_CAMERA) {
        // A camera node.
        if (attrName == "translateX" || attrName == "tx") {
            attr_type = ATTR_SOLVER_TYPE_CAMERA_TX;
        } else if (attrName == "translateY" || attrName == "ty") {
            attr_type = ATTR_SOLVER_TYPE_CAMERA_TY;
        } else if (attrName == "translateZ" || attrName == "tz") {
            attr_type = ATTR_SOLVER_TYPE_CAMERA_TZ;
        } else if (attrName == "rotateX" || attrName == "rx") {
            attr_type = ATTR_SOLVER_TYPE_CAMERA_RX;
        } else if (attrName == "rotateY" || attrName == "ry") {
            attr_type = ATTR_SOLVER_TYPE_CAMERA_RY;
        } else if (attrName == "rotateZ" || attrName == "rx") {
            attr_type = ATTR_SOLVER_TYPE_CAMERA_RZ;
        } else if (attrName == "scaleX" || attrName == "sx") {
            attr_type = ATTR_SOLVER_TYPE_CAMERA_SX;
        } else if (attrName == "scaleY" || attrName == "sy") {
            attr_type = ATTR_SOLVER_TYPE_CAMERA_SY;
        } else if (attrName == "scaleZ" || attrName == "sz") {
            attr_type = ATTR_SOLVER_TYPE_CAMERA_SZ;
        } else if (attrName == "focalLength" || attrName == "fl") {
            attr_type = ATTR_SOLVER_TYPE_CAMERA_FOCAL;
        }
    } else {
        // A normal transform node.
        if (attrName == "translateX" || attrName == "tx") {
            attr_type = ATTR_SOLVER_TYPE_TRANSFORM_TX;
        } else if (attrName == "translateY" || attrName == "ty") {
            attr_type = ATTR_SOLVER_TYPE_TRANSFORM_TY;
        } else if (attrName == "translateZ" || attrName == "tz") {
            attr_type = ATTR_SOLVER_TYPE_TRANSFORM_TZ;
        } else if (attrName == "rotateX" || attrName == "rx") {
            attr_type = ATTR_SOLVER_TYPE_TRANSFORM_RX;
        } else if (attrName == "rotateY" || attrName == "ry") {
            attr_type = ATTR_SOLVER_TYPE_TRANSFORM_RY;
        } else if (attrName == "rotateZ" || attrName == "rx") {
            attr_type = ATTR_SOLVER_TYPE_TRANSFORM_RZ;
        } else if (attrName == "scaleX" || attrName == "sx") {
            attr_type = ATTR_SOLVER_TYPE_TRANSFORM_SX;
        } else if (attrName == "scaleY" || attrName == "sy") {
            attr_type = ATTR_SOLVER_TYPE_TRANSFORM_SY;
        } else if (attrName == "scaleZ" || attrName == "sz") {
            attr_type = ATTR_SOLVER_TYPE_TRANSFORM_SZ;
        }
    }
    return attr_type;
}


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

    int getAttrType();

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

    double getOffsetValue();

    void setOffsetValue(double value);

    double getScaleValue();

    void setScaleValue(double value);

    unsigned int getObjectType();

    void setObjectType(unsigned int value);

    unsigned int getSolverAttrType();

    void setSolverAttrType(unsigned int value);

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
    double m_offsetValue;
    double m_scaleValue;
    unsigned int m_objectType;
    unsigned int m_solverAttrType;

    double m_linearFactor;
    double m_linearFactorInv;
    double m_angularFactor;
    double m_angularFactorInv;
};


typedef std::vector<Attr> AttrList;
typedef AttrList::iterator AttrListIt;

typedef std::shared_ptr<Attr> AttrPtr;
typedef std::vector<std::shared_ptr<Attr> > AttrPtrList;
typedef AttrPtrList::iterator AttrPtrListIt;
typedef AttrPtrList::const_iterator AttrPtrListCIt;

#endif //MAYA_MM_SOLVER_ATTR_H
