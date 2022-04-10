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

#ifndef MM_SOLVER_MAYA_HELPER_MAYA_ATTR_H
#define MM_SOLVER_MAYA_HELPER_MAYA_ATTR_H

#include <vector>
#include <memory>

#include <maya/MObject.h>
#include <maya/MString.h>
#include <maya/MPlug.h>
#include <maya/MTime.h>
#include <maya/MFnAnimCurve.h>
#include <maya/MAnimControl.h>
#include <maya/MDGModifier.h>
#include <maya/MDistance.h>
#include <maya/MAngle.h>

#include "maya_utils.h"

// The underlying attribute data type.
#define ATTR_DATA_TYPE_UNKNOWN (0)
#define ATTR_DATA_TYPE_LINEAR (1)
#define ATTR_DATA_TYPE_ANGLE (2)
#define ATTR_DATA_TYPE_NUMERIC (3)

// Solver Types of Attributes.
#define ATTR_SOLVER_TYPE_UNINITIALIZED (0)
#define ATTR_SOLVER_TYPE_UNKNOWN       (1)
#define ATTR_SOLVER_TYPE_BUNDLE_TX     (2)
#define ATTR_SOLVER_TYPE_BUNDLE_TY     (3)
#define ATTR_SOLVER_TYPE_BUNDLE_TZ     (4)
#define ATTR_SOLVER_TYPE_CAMERA_TX     (5)
#define ATTR_SOLVER_TYPE_CAMERA_TY     (6)
#define ATTR_SOLVER_TYPE_CAMERA_TZ     (7)
#define ATTR_SOLVER_TYPE_CAMERA_RX     (8)
#define ATTR_SOLVER_TYPE_CAMERA_RY     (9)
#define ATTR_SOLVER_TYPE_CAMERA_RZ     (10)
#define ATTR_SOLVER_TYPE_CAMERA_SX     (11)
#define ATTR_SOLVER_TYPE_CAMERA_SY     (12)
#define ATTR_SOLVER_TYPE_CAMERA_SZ     (13)
#define ATTR_SOLVER_TYPE_CAMERA_FOCAL  (14)
#define ATTR_SOLVER_TYPE_TRANSFORM_TX  (15)
#define ATTR_SOLVER_TYPE_TRANSFORM_TY  (16)
#define ATTR_SOLVER_TYPE_TRANSFORM_TZ  (17)
#define ATTR_SOLVER_TYPE_TRANSFORM_RX  (18)
#define ATTR_SOLVER_TYPE_TRANSFORM_RY  (19)
#define ATTR_SOLVER_TYPE_TRANSFORM_RZ  (20)
#define ATTR_SOLVER_TYPE_TRANSFORM_SX  (21)
#define ATTR_SOLVER_TYPE_TRANSFORM_SY  (22)
#define ATTR_SOLVER_TYPE_TRANSFORM_SZ  (23)

// Lens distortion model.
#define ATTR_SOLVER_TYPE_LENS_BASIC_K1                       (24)
#define ATTR_SOLVER_TYPE_LENS_BASIC_K2                       (25)
#define ATTR_SOLVER_TYPE_LENS_3DE_CLASSIC_DISTORTION         (26)
#define ATTR_SOLVER_TYPE_LENS_3DE_CLASSIC_ANAMORPHIC_SQUEEZE (27)
#define ATTR_SOLVER_TYPE_LENS_3DE_CLASSIC_CURVATURE_X        (28)
#define ATTR_SOLVER_TYPE_LENS_3DE_CLASSIC_CURVATURE_Y        (29)
#define ATTR_SOLVER_TYPE_LENS_3DE_CLASSIC_QUARTIC_DISTORTION (30)

inline
unsigned int computeSolverAttrType(ObjectType objectType,
                                   MString &attrName) {
    uint32_t attr_type = ATTR_SOLVER_TYPE_UNKNOWN;
    if (objectType == ObjectType::kBundle) {
        // A bundle node.
        if (attrName == "translateX" || attrName == "tx") {
            attr_type = ATTR_SOLVER_TYPE_BUNDLE_TX;
        } else if (attrName == "translateY" || attrName == "ty") {
            attr_type = ATTR_SOLVER_TYPE_BUNDLE_TY;
        } else if (attrName == "translateZ" || attrName == "tz") {
            attr_type = ATTR_SOLVER_TYPE_BUNDLE_TZ;
        }
    } else if (objectType == ObjectType::kCamera) {
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
    } else if (objectType == ObjectType::kLens) {
        // A lens model node.
        if (attrName == "k1") {
            attr_type = ATTR_SOLVER_TYPE_LENS_BASIC_K1;
        } else if (attrName == "k2") {
            attr_type = ATTR_SOLVER_TYPE_LENS_BASIC_K2;
        } else if (attrName == "distortion") {
            attr_type = ATTR_SOLVER_TYPE_LENS_3DE_CLASSIC_DISTORTION;
        } else if (attrName == "anamorphicSqueeze") {
            attr_type = ATTR_SOLVER_TYPE_LENS_3DE_CLASSIC_ANAMORPHIC_SQUEEZE;
        } else if (attrName == "curvatureX") {
            attr_type = ATTR_SOLVER_TYPE_LENS_3DE_CLASSIC_CURVATURE_X;
        } else if (attrName == "curvatureY") {
            attr_type = ATTR_SOLVER_TYPE_LENS_3DE_CLASSIC_CURVATURE_Y;
        } else if (attrName == "quarticDistortion") {
            attr_type = ATTR_SOLVER_TYPE_LENS_3DE_CLASSIC_QUARTIC_DISTORTION;
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
    MStatus setNodeName(const MString &value);

    MString getAttrName() const;
    MStatus setAttrName(const MString &value);

    MObject getObject();
    MPlug getPlug();
    MObject getAttribute();
    MString getAnimCurveName();
    int getAttrType();

    bool isFreeToChange();
    bool isAnimated();
    bool isConnected();

    MStatus getValue(bool &value, const MTime &time, const int timeEvalMode);
    MStatus getValue(int &value, const MTime &time, const int timeEvalMode);
    MStatus getValue(short &value, const MTime &time, const int timeEvalMode);
    MStatus getValue(double &value, const MTime &time, const int timeEvalMode);
    MStatus getValue(MMatrix &value, const MTime &time, const int timeEvalMode);

    MStatus getValue(bool &value, const int timeEvalMode);
    MStatus getValue(int &value, const int timeEvalMode);
    MStatus getValue(short &value, const int timeEvalMode);
    MStatus getValue(double &value, const int timeEvalMode);
    MStatus getValue(MMatrix &value, const int timeEvalMode);

    MStatus setValue(
        const double value,
        const MTime &time,
        MDGModifier &dgmod,
        MAnimCurveChange &animChange);

    MStatus setValue(
        const double value,
        MDGModifier &dgmod,
        MAnimCurveChange &animChange);

    double getMinimumValue() const;
    double getMaximumValue() const;
    double getOffsetValue() const;
    double getScaleValue() const;
    ObjectType getObjectType() const;
    unsigned int getSolverAttrType() const;

    void setMinimumValue(const double value);
    void setMaximumValue(const double value);
    void setOffsetValue(const double value);
    void setScaleValue(const double value);
    void setObjectType(const ObjectType value);
    void setSolverAttrType(const unsigned int value);

    MString getLongNodeName();
    MString getLongAttributeName();
    MString getLongName();

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
    ObjectType m_objectType;
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


struct SmoothAttrs {
    int attrIndex;
    AttrPtr weightAttr;
    AttrPtr varianceAttr;
    AttrPtr valueAttr;
};

typedef std::vector<SmoothAttrs> SmoothAttrsList;
typedef SmoothAttrsList::iterator SmoothAttrsListIt;

typedef std::shared_ptr<SmoothAttrs> SmoothAttrsPtr;
typedef std::vector<std::shared_ptr<SmoothAttrs> > SmoothAttrsPtrList;
typedef SmoothAttrsPtrList::iterator SmoothAttrsPtrListIt;
typedef SmoothAttrsPtrList::const_iterator SmoothAttrsPtrListCIt;


struct StiffAttrs {
    int attrIndex;
    AttrPtr weightAttr;
    AttrPtr varianceAttr;
    AttrPtr valueAttr;
};

typedef std::vector<StiffAttrs> StiffAttrsList;
typedef StiffAttrsList::iterator StiffAttrsListIt;

typedef std::shared_ptr<StiffAttrs> StiffAttrsPtr;
typedef std::vector<std::shared_ptr<StiffAttrs> > StiffAttrsPtrList;
typedef StiffAttrsPtrList::iterator StiffAttrsPtrListIt;
typedef StiffAttrsPtrList::const_iterator StiffAttrsPtrListCIt;


#endif // MM_SOLVER_MAYA_HELPER_MAYA_ATTR_H
