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
 * Attribute class holds functions for getting and setting an
 * attribute, as well as state information.
 *
 */

#include "maya_attr.h"

// STL
#include <cmath>   // trunc, isfinite
#include <limits>  // numeric_limits<double>::max and min

// Provides C++ compatibility.
// Between Maya 2018 and 2020.
#if MAYA_API_VERSION >= 20180000 && MAYA_API_VERSION < 20200000
#include <maya/MCppCompat.h>
#endif

// Maya
#include <maya/MAnimCurveChange.h>
#include <maya/MAnimUtil.h>
#include <maya/MDGContext.h>
#include <maya/MFn.h>
#include <maya/MFnAnimCurve.h>
#include <maya/MFnAttribute.h>
#include <maya/MFnMatrixData.h>
#include <maya/MGlobal.h>
#include <maya/MMatrix.h>
#include <maya/MObject.h>
#include <maya/MObjectArray.h>
#include <maya/MPlug.h>
#include <maya/MPlugArray.h>
#include <maya/MStatus.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>

#if MAYA_API_VERSION >= 20180000
#include <maya/MDGContextGuard.h>
#endif

#include "maya_utils.h"
#include "mmSolver/adjust/adjust_defines.h"

// Turning USE_DG_CONTEXT on seems to slow down running the test suite by
// approximately 33% (inside 'mayapy', without a GUI).
#define USE_DG_CONTEXT_IN_GUI 1

bool useDgContext(const int timeEvalMode) {
    MStatus status;
    MGlobal::MMayaState state = MGlobal::mayaState(&status);
    MMSOLVER_CHECK_MSTATUS(status);
    const bool is_interactive = state == MGlobal::MMayaState::kInteractive;
    bool use_dg_ctx = USE_DG_CONTEXT_IN_GUI && is_interactive;
    if (timeEvalMode == TIME_EVAL_MODE_SET_TIME) {
        use_dg_ctx = false;
    }
    return use_dg_ctx;
}

Attr::Attr()
    : m_nodeName("")
    , m_attrName("")
    , m_object()
    , m_plug()
    , m_animCurveName("")
    , m_animated(-1)
    , m_connected(-1)
    , m_isFreeToChange(-1)
    , m_minValue(-std::numeric_limits<float>::max())
    , m_maxValue(std::numeric_limits<float>::max())
    , m_offsetValue(0.0)
    , m_scaleValue(1.0)
    , m_objectType(ObjectType::kUninitialized)
    , m_solverAttrType(AttrSolverType::kUninitialized) {
    MDistance distanceOne(1.0, MDistance::internalUnit());
    m_linearFactor = distanceOne.as(MDistance::uiUnit());
    m_linearFactorInv = 1.0 / m_linearFactor;

    MAngle angularOne(1.0, MAngle::internalUnit());
    m_angularFactor = angularOne.as(MAngle::uiUnit());
    m_angularFactorInv = 1.0 / m_angularFactor;
}

MString Attr::getName() const { return m_nodeName + "." + m_attrName; }

MStatus Attr::setName(MString value) {
    MStatus status;
    MStringArray values;
    status = value.split('.', values);
    if (status != MStatus::kSuccess) {
        MMSOLVER_MAYA_ERR("Attr::setName: Error splitting name: "
                          << "\"" << value.asChar() << "\"");
        return MS::kFailure;
    }
    if (values.length() == 2) {
        Attr::setNodeName(values[0]);
        Attr::setAttrName(values[1]);

        auto object_type = Attr::getObjectType();
        auto solverAttrType = computeSolverAttrType(object_type, values[1]);
        Attr::setSolverAttrType(solverAttrType);
    } else {
        MMSOLVER_MAYA_ERR(
            "Attr::setName: Value given has more than one dot character: "
            << "\"" << value.asChar() << "\"");
        return MS::kFailure;
    }
    return status;
}

MString Attr::getNodeName() const { return m_nodeName; }

MStatus Attr::setNodeName(const MString &value) {
    if (value != m_nodeName) {
        m_object = MObject();
        m_plug = MPlug();
        m_animated = -1;
        m_connected = -1;
        m_isFreeToChange = -1;
        m_animCurveName = "";
        m_nodeName = value;

        MObject obj = Attr::getObject();
        m_objectType = computeObjectType(obj);
    }
    return MS::kSuccess;
}

MString Attr::getAttrName() const { return m_attrName; }

MStatus Attr::setAttrName(const MString &value) {
    if (value != m_attrName) {
        m_object = MObject();
        m_plug = MPlug();
        m_animated = -1;
        m_animCurveName = "";
        m_isFreeToChange = -1;
    }
    m_attrName = value;
    return MS::kSuccess;
}

MObject Attr::getObject() {
    if (m_object.isNull()) {
        MStatus status;
        // Get the MObject for the underlying node.
        MString name = Attr::getNodeName();
        status = getAsObject(name, m_object);
        MMSOLVER_CHECK_MSTATUS(status);
    }
    return m_object;
}

MPlug Attr::getPlug() {
    MStatus status;
    if (m_plug.isNull() == true) {
        MObject nodeObj = Attr::getObject();
        MString attrName = Attr::getAttrName();
        MFnDependencyNode dependsNode(nodeObj, &status);
        MPlug plug =
            dependsNode.findPlug(attrName, /*wantNetworkedPlug=*/true, &status);
        if (status != MStatus::kSuccess) {
            // MString name = Attr::getName();
            // MMSOLVER_MAYA_WRN("Attribute cannot be found; " << name);
            return m_plug;
        }

        // For attributes like 'worldMatrix', where we need the first
        // element of the array, not the attribute itself.
        if (plug.isArray()) {
            // Here we need 'evaluateNumElements' in case Maya hasn't
            // already computed how many elements the array plug is
            // expected to have.
            plug.evaluateNumElements(&status);
            MMSOLVER_CHECK_MSTATUS(status);
            const unsigned int num = plug.numElements(&status);
            MMSOLVER_CHECK_MSTATUS(status);
            if (num > 0) {
                plug = plug.elementByPhysicalIndex(0, &status);
                if (status != MStatus::kSuccess) {
                    MMSOLVER_MAYA_ERR("Could not get first plug element.");
                    return m_plug;
                }
            }
        }
        m_plug = plug;
    }
    return m_plug;
}

MObject Attr::getAttribute() {
    MPlug plug = Attr::getPlug();
    MObject attrObj;
    if (!plug.isNull()) {
        attrObj = plug.attribute();
    }
    return attrObj;
}

/*
 * Get the attribute type; linear, angle or numeric.
 */
AttrDataType Attr::getAttrType() {
    auto attrType = AttrDataType::kUnknown;
    MObject attrObj = Attr::getAttribute();
    MFn::Type mfnAttrType = attrObj.apiType();
    if ((mfnAttrType == MFn::Type::kDoubleLinearAttribute) ||
        (mfnAttrType == MFn::Type::kFloatLinearAttribute)) {
        attrType = AttrDataType::kLinear;
    } else if ((mfnAttrType == MFn::Type::kDoubleAngleAttribute) ||
               (mfnAttrType == MFn::Type::kFloatAngleAttribute)) {
        attrType = AttrDataType::kAngle;
    } else {
        attrType = AttrDataType::kNumeric;
    }
    return attrType;
}

/*
 * Find out if a plug can be changed or not.
 *
 * Attributes that cannot change could be:
 * - Locked
 * - Already have an incoming connection
 */
bool Attr::isFreeToChange() {
    if (m_isFreeToChange < 0) {
        MPlug plug = Attr::getPlug();
        if (plug.isFreeToChange() == MPlug::kFreeToChange) {
            m_isFreeToChange = 1;
        } else {
            m_isFreeToChange = 0;
        }
    }
    return m_isFreeToChange != 0;
}

/*
 * Determine if a plug is being animated using an animCurve.
 */
bool Attr::isAnimated() {
    MStatus status;
    if (m_animated < 0) {
        MPlug plug = Attr::getPlug();

        bool animated = false;
        const bool isDest = plug.isDestination(&status);
        MMSOLVER_CHECK_MSTATUS(status);
        if (isDest) {
            MPlugArray connPlugs;
            bool asDest = true;  // get the source plugs on the other
                                 // end of 'plug'.
            bool asSrc = false;
            plug.connectedTo(connPlugs, asDest, asSrc, &status);
            MMSOLVER_CHECK_MSTATUS(status);
            for (unsigned int i = 0; i < connPlugs.length(); ++i) {
                MPlug connPlug = connPlugs[i];
                MObject connObj = connPlug.node(&status);
                MMSOLVER_CHECK_MSTATUS(status);
                if (connObj.hasFn(MFn::Type::kAnimCurve)) {
                    animated = true;
                    MFnDependencyNode dependsNode(connObj, &status);
                    MMSOLVER_CHECK_MSTATUS(status);
                    m_animCurveName = dependsNode.name(&status);
                    MMSOLVER_CHECK_MSTATUS(status);
                    break;
                }
            }
        }

        if (status != MS::kSuccess) {
            MString name = Attr::getName();
            MMSOLVER_MAYA_ERR("Attr::isAnimated failed; " << name);
            animated = false;  // lets assume that if it failed, the
                               // plug cannot be animated.
        }
        m_connected = (int)isDest;
        m_animated = (int)animated;
    }
    return m_animated != 0;
}

/*
 * Determine if another plug is connected to this plug (so we cannot
 * change the value).
 */
bool Attr::isConnected() {
    MStatus status;
    MPlug plug = Attr::getPlug();

    if (m_connected < 0) {
        const bool isDest = plug.isDestination(&status);
        MMSOLVER_CHECK_MSTATUS(status);
        m_connected = (int)isDest;
    }
    return m_connected != 0;
}

MString Attr::getAnimCurveName() {
    MString result = "";
    // isAnimated will compute 'm_animCurveName' for us.
    const bool animated = Attr::isAnimated();
    if (animated == true) {
        result = m_animCurveName;
    }
    return result;
}

namespace {

// Windows MSVC doesn't have 'trunc' function, so we create our own.
inline double my_trunc(double d) {
    return (d > 0) ? std::floor(d) : std::ceil(d);
}

}  // namespace

MStatus Attr::getValue(bool &value, const MTime &time, const int timeEvalMode) {
    MStatus status;
    const bool connected = Attr::isConnected();
    const bool animated = Attr::isAnimated();
    MPlug plug = Attr::getPlug();
    const bool use_dg_ctx = useDgContext(timeEvalMode);

    if (animated) {
        MFnAnimCurve curveFn(plug, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        double curveValue = 0;
        status = curveFn.evaluate(time, curveValue);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        value = my_trunc(curveValue) != 0;
    } else if (connected) {
        if (use_dg_ctx) {
#if MAYA_API_VERSION >= 20180000
            MDGContext ctx(time);
            MDGContextGuard ctxGuard(ctx);
            value = plug.asBool(&status);
#else
            MDGContext ctx(time);
            value = plug.asBool(ctx, &status);
#endif
        } else {
            MAnimControl::setCurrentTime(time);
#if MAYA_API_VERSION >= 20180000
            MDGContext ctx = MDGContext::current();
            MDGContextGuard ctxGuard(ctx);
            value = plug.asBool(&status);
#else
            value = plug.asBool(MDGContext::fsNormal, &status);
#endif
        }
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    } else {
        value = plug.asBool();
    }

    return MS::kSuccess;
}

MStatus Attr::getValue(int &value, const MTime &time, const int timeEvalMode) {
    MStatus status;
    const bool connected = Attr::isConnected();
    const bool animated = Attr::isAnimated();
    MPlug plug = Attr::getPlug();
    const bool use_dg_ctx = useDgContext(timeEvalMode);

    if (animated) {
        MFnAnimCurve curveFn(plug, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        double curveValue = 0;
        status = curveFn.evaluate(time, curveValue);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        value = (int)curveValue;
    } else if (connected) {
        if (use_dg_ctx) {
#if MAYA_API_VERSION >= 20180000
            MDGContext ctx(time);
            MDGContextGuard ctxGuard(ctx);
            value = plug.asInt(&status);
#else
            MDGContext ctx(time);
            value = plug.asInt(ctx, &status);
#endif
        } else {
            MAnimControl::setCurrentTime(time);
#if MAYA_API_VERSION >= 20180000
            MDGContext ctx = MDGContext::current();
            MDGContextGuard ctxGuard(ctx);
            value = plug.asInt(&status);
#else
            value = plug.asInt(MDGContext::fsNormal, &status);
#endif
        }
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    } else {
        value = plug.asInt();
    }

    return MS::kSuccess;
}

MStatus Attr::getValue(short &value, const MTime &time,
                       const int timeEvalMode) {
    MStatus status;
    const bool connected = Attr::isConnected();
    const bool animated = Attr::isAnimated();
    MPlug plug = Attr::getPlug();
    const bool use_dg_ctx = useDgContext(timeEvalMode);

    if (animated) {
        MFnAnimCurve curveFn(plug, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        double curveValue = 0;
        status = curveFn.evaluate(time, curveValue);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        value = (short)curveValue;
    } else if (connected) {
        if (use_dg_ctx) {
#if MAYA_API_VERSION >= 20180000
            MDGContext ctx(time);
            MDGContextGuard ctxGuard(ctx);
            value = plug.asShort(&status);
#else
            MDGContext ctx(time);
            value = plug.asShort(ctx, &status);
#endif
        } else {
            MAnimControl::setCurrentTime(time);
#if MAYA_API_VERSION >= 20180000
            MDGContext ctx = MDGContext::current();
            MDGContextGuard ctxGuard(ctx);
            value = plug.asShort(&status);
#else
            value = plug.asShort(MDGContext::fsNormal, &status);
#endif
        }
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    } else {
        value = plug.asShort();
    }

    return MS::kSuccess;
}

MStatus Attr::getValue(double &value, const MTime &time,
                       const int timeEvalMode) {
    MStatus status;
    const bool connected = Attr::isConnected();
    const bool animated = Attr::isAnimated();
    MPlug plug = Attr::getPlug();
    const bool use_dg_ctx = useDgContext(timeEvalMode);

    if (animated) {
        MFnAnimCurve curveFn(plug);
        curveFn.evaluate(time, value);
    } else if (connected) {
        if (use_dg_ctx) {
#if MAYA_API_VERSION >= 20180000
            MDGContext ctx(time);
            MDGContextGuard ctxGuard(ctx);
            value = plug.asDouble(&status);
#else
            MDGContext ctx(time);
            value = plug.asDouble(ctx, &status);
#endif
        } else {
            MAnimControl::setCurrentTime(time);
#if MAYA_API_VERSION >= 20180000
            MDGContext ctx = MDGContext::current();
            MDGContextGuard ctxGuard(ctx);
            value = plug.asDouble(&status);
#else
            value = plug.asDouble(MDGContext::fsNormal, &status);
#endif
        }
    } else {
        value = plug.asDouble();
    }

    auto attrType = Attr::getAttrType();
    if (attrType == AttrDataType::kAngle) {
        value *= m_angularFactor;
    }
    return MS::kSuccess;
}

MStatus Attr::getValue(MMatrix &value, const MTime &time,
                       const int timeEvalMode) {
    MStatus status;
    MPlug plug = Attr::getPlug();
    const bool use_dg_ctx = useDgContext(timeEvalMode);

    // Do we change the behaviour for a dynamic attribute?
    MObject matrixObj;
    if (use_dg_ctx) {
#if MAYA_API_VERSION >= 20180000
        MDGContext ctx(time);
        MDGContextGuard ctxGuard(ctx);
        matrixObj = plug.asMObject(&status);
#else
        MDGContext ctx(time);
        matrixObj = plug.asMObject(ctx, &status);
#endif
    } else {
        MAnimControl::setCurrentTime(time);
#if MAYA_API_VERSION >= 20180000
        MDGContext ctx = MDGContext::current();
        MDGContextGuard ctxGuard(ctx);
        matrixObj = plug.asMObject(&status);
#else
        matrixObj = plug.asMObject(MDGContext::fsNormal, &status);
#endif
    }
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    MFnMatrixData matrixData(matrixObj, &status);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    value = matrixData.matrix(&status);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    return status;
}

MStatus Attr::getValue(bool &value, const int timeEvalMode) {
    MTime time = MAnimControl::currentTime();
    return Attr::getValue(value, time, timeEvalMode);
}

MStatus Attr::getValue(int &value, const int timeEvalMode) {
    MTime time = MAnimControl::currentTime();
    return Attr::getValue(value, time, timeEvalMode);
}

MStatus Attr::getValue(short &value, const int timeEvalMode) {
    MTime time = MAnimControl::currentTime();
    return Attr::getValue(value, time, timeEvalMode);
}

MStatus Attr::getValue(double &value, const int timeEvalMode) {
    MTime time = MAnimControl::currentTime();
    return Attr::getValue(value, time, timeEvalMode);
}

MStatus Attr::getValue(MMatrix &value, const int timeEvalMode) {
    MTime time = MAnimControl::currentTime();
    return Attr::getValue(value, time, timeEvalMode);
}

MStatus Attr::setValue(double value, const MTime &time, MDGModifier &dgmod,
                       MAnimCurveChange &animChange) {
    MStatus status = MS::kSuccess;

    MPlug plug = Attr::getPlug();
    if (!std::isfinite(value)) {
        status = MS::kFailure;
        MString name = Attr::getName();
        MString plugName = plug.name(&status);
        MMSOLVER_MAYA_ERR("Set attribute with non-finite value;"
                          << " name=" << name << " plug=" << plugName
                          << " value=" << value << " time=" << time.value());
        return status;
    }

    const bool connected = Attr::isConnected();
    const bool animated = Attr::isAnimated();

    auto attrType = Attr::getAttrType();
    if (attrType == AttrDataType::kAngle) {
        value *= m_angularFactorInv;
    }

    if (animated) {
        MFnAnimCurve curveFn(plug, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        unsigned int keyIndex = 0;
        // TODO: The keyframe index may be possible to cache, as long
        //  as we can control that when a new keyframe is inserted, we
        //  invalidate the cache, or instead of invalidating the cache
        //  we automatically increment all keyframe indexes based on
        //  the newly insert keyframe index.
        const bool found = curveFn.find(time, keyIndex);
        if (found) {
            curveFn.setValue(keyIndex, value, &animChange);
        } else {
            curveFn.addKeyframe(time, value, &animChange);
        }
    } else if (connected) {
        // TODO: What do we do??? Just error?
        MString name = Attr::getName();
        MString plugName = plug.name(&status);
        MMSOLVER_MAYA_ERR(
            "Dynamic attributes that aren't animated cannot be set; "
            << "name=" << name << " "
            << "plug=" << plugName);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    } else {
        dgmod.newPlugValueDouble(plug, value);
    }
    return status;
}

MStatus Attr::setValue(const double value, MDGModifier &dgmod,
                       MAnimCurveChange &animChange) {
    MTime time = MAnimControl::currentTime();
    return Attr::setValue(value, time, dgmod, animChange);
}

double Attr::getMinimumValue() const { return m_minValue; }

void Attr::setMinimumValue(const double value) { m_minValue = value; }

double Attr::getMaximumValue() const { return m_maxValue; }

void Attr::setMaximumValue(const double value) { m_maxValue = value; }

double Attr::getOffsetValue() const { return m_offsetValue; }

void Attr::setOffsetValue(const double value) { m_offsetValue = value; }

double Attr::getScaleValue() const { return m_scaleValue; }

void Attr::setScaleValue(const double value) { m_scaleValue = value; }

ObjectType Attr::getObjectType() const { return m_objectType; }

void Attr::setObjectType(const ObjectType value) { m_objectType = value; }

AttrSolverType Attr::getSolverAttrType() const { return m_solverAttrType; }

void Attr::setSolverAttrType(const AttrSolverType value) {
    m_solverAttrType = value;
}

MString Attr::getLongNodeName() {
    MString result;
    MStatus status;
    MString nodeName;

    MObject nodeObj = Attr::getObject();
    if (nodeObj.hasFn(MFn::kDagNode)) {
        MDagPath nodeDagPath;
        status = MDagPath::getAPathTo(nodeObj, nodeDagPath);
        MMSOLVER_CHECK_MSTATUS(status);

        nodeName = nodeDagPath.fullPathName(&status);
        MMSOLVER_CHECK_MSTATUS(status);
    } else if (nodeObj.hasFn(MFn::kDependencyNode)) {
        MFnDependencyNode dependFn(nodeObj, &status);
        MMSOLVER_CHECK_MSTATUS(status);
        nodeName = dependFn.name();
    } else {
        nodeName = Attr::getNodeName();
        MMSOLVER_MAYA_ERR(
            "Attr::getLongNodeName: Node is not DAG or DG node - invalid "
            "object: "
            << "\"" << nodeName.asChar() << "\"");
    }

    return nodeName;
}

MString Attr::getLongAttributeName() {
    MStatus status;
    MObject attrObj = Attr::getAttribute();
    const bool attrIsNull = attrObj.isNull();
    MMSOLVER_CHECK(attrIsNull == false, "Attribute is not valid.");
    if (attrIsNull) {
        MMSOLVER_MAYA_INFO("Attr::getLongAttributeName: Node Name: "
                           << "\"" << m_nodeName.asChar() << "\"");
        MMSOLVER_MAYA_INFO("Attr::getLongAttributeName: Attr Name: "
                           << "\"" << m_attrName.asChar() << "\"");
        MMSOLVER_MAYA_INFO("Attr::getLongAttributeName: Anim Curve Name: "
                           << "\"" << m_animCurveName.asChar() << "\"");
        return MString();
    }
    MFnAttribute attrMFn(attrObj, &status);
    MMSOLVER_CHECK_MSTATUS(status);
    return attrMFn.name();
}

MString Attr::getLongName() {
    MString result;
    MString nodeName = Attr::getLongNodeName();
    MString attrName = Attr::getLongAttributeName();
    result = nodeName;
    result += ".";
    result += attrName;
    return result;
}

#undef USE_DG_CONTEXT_IN_GUI
