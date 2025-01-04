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
 * Markers - Querying a 2D node (but it's actually a 3D DAG node)
 */

#include "maya_marker.h"

// STL
#include <memory>

// Maya
#include <maya/MDagPath.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MFnMatrixData.h>
#include <maya/MMatrix.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MPoint.h>

// MM Solver
#include "maya_attr.h"
#include "maya_bundle.h"
#include "maya_camera.h"
#include "maya_marker_group.h"
#include "maya_utils.h"
#include "mmSolver/adjust/adjust_defines.h"
#include "mmSolver/utilities/debug_utils.h"

Marker::Marker()
    : m_nodeName(""), m_object(), m_camera(), m_bundle(), m_markerGroup() {
    m_matrix.setAttrName("worldMatrix");
    m_px.setAttrName("translateX");
    m_py.setAttrName("translateY");
    m_enable.setAttrName("enable");
    m_weight.setAttrName("weight");
}

MString Marker::getNodeName() const { return MString(m_nodeName); }

MStatus Marker::setNodeName(MString value) {
    MStatus status = MS::kSuccess;
    if (value != m_nodeName) {
        m_object = MObject();

        status = m_matrix.setNodeName(value);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        status = m_px.setNodeName(value);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        status = m_py.setNodeName(value);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        status = m_enable.setNodeName(value);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        status = m_weight.setNodeName(value);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        m_nodeName = value;
    }
    return status;
}

MObject Marker::getObject() {
    if (m_object.isNull()) {
        MStatus status;
        MString name = Marker::getNodeName();
        status = getAsObject(name, m_object);
        CHECK_MSTATUS(status);
    }
    return m_object;
}

CameraPtr Marker::getCamera() { return m_camera; }

MStatus Marker::setCamera(CameraPtr &value) {
    m_camera = value;
    return MS::kSuccess;
}

BundlePtr Marker::getBundle() { return m_bundle; }

MStatus Marker::setBundle(BundlePtr &value) {
    m_bundle = value;
    return MS::kSuccess;
}

MarkerGroupPtr Marker::getMarkerGroup() { return m_markerGroup; }

MStatus Marker::setMarkerGroup(MarkerGroupPtr &value) {
    m_markerGroup = value;
    return MS::kSuccess;
}

Attr &Marker::getMatrixAttr() { return m_matrix; }

Attr &Marker::getEnableAttr() { return m_enable; }

Attr &Marker::getWeightAttr() { return m_weight; }

Attr &Marker::getPosXAttr() { return m_px; }

Attr &Marker::getPosYAttr() { return m_py; }

MStatus Marker::getMatrix(MMatrix &value, const MTime &time,
                          const int timeEvalMode) {
    return m_matrix.getValue(value, time, timeEvalMode);
}

MStatus Marker::getMatrix(MMatrix &value, const int timeEvalMode) {
    return m_matrix.getValue(value, timeEvalMode);
}

MStatus Marker::getPos(double &x, double &y, double &z, const MTime &time,
                       const int timeEvalMode) {
    MStatus status;
    MMatrix matrix;
    status = Marker::getMatrix(matrix, time, timeEvalMode);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    x = matrix(3, 0);
    y = matrix(3, 1);
    z = matrix(3, 2);
    return status;
}

MStatus Marker::getPos(MPoint &point, const MTime &time,
                       const int timeEvalMode) {
    MStatus status;
    MMatrix matrix;
    status = Marker::getMatrix(matrix, time, timeEvalMode);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    point.x = matrix(3, 0);
    point.y = matrix(3, 1);
    point.z = matrix(3, 2);
    point.w = matrix(3, 3);
    point.cartesianize();
    return status;
}

MStatus Marker::getPos(double &x, double &y, double &z,
                       const int timeEvalMode) {
    MTime time = MAnimControl::currentTime();
    MStatus status = Marker::getPos(x, y, z, time, timeEvalMode);
    return status;
}

MStatus Marker::getPos(MPoint &point, const int timeEvalMode) {
    MTime time = MAnimControl::currentTime();
    MStatus status = Marker::getPos(point, time, timeEvalMode);
    return status;
}

MStatus Marker::getPosXY(double &out_x, double &out_y, const MTime &time,
                         const int timeEvalMode, const bool applyOverscan) {
    MStatus status;
    const bool verbose = false;

    auto attr_pos_x = Marker::getPosXAttr();
    auto attr_pos_y = Marker::getPosYAttr();

    double overscan_x = 1.0;
    double overscan_y = 1.0;
    if (applyOverscan) {
        if (m_markerGroup) {
            // Take into account the MarkerGroup's 'overscan'
            // attributes. The Marker X/Y values should be multiplied by
            // the inverse of the overscan X/Y values.
            status = m_markerGroup->getOverscanXY(overscan_x, overscan_y, time,
                                                  timeEvalMode);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            overscan_x = 1.0 / overscan_x;
            overscan_y = 1.0 / overscan_y;
        } else {
            MMSOLVER_MAYA_VRB(
                "Marker::getPosXY: MarkerGroup node not found for \""
                << m_nodeName.asChar() << "\".");
        }
    }

    status = attr_pos_x.getValue(out_x, time, timeEvalMode);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    status = attr_pos_y.getValue(out_y, time, timeEvalMode);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    out_x *= overscan_x;
    out_y *= overscan_y;
    return status;
}

MStatus Marker::getPosXY(double &out_x, double &out_y, const int timeEvalMode,
                         const bool applyOverscan) {
    MTime time = MAnimControl::currentTime();
    MStatus status =
        Marker::getPosXY(out_x, out_y, time, timeEvalMode, applyOverscan);
    return status;
}

MStatus Marker::getEnable(bool &value, const MTime &time,
                          const int timeEvalMode) {
    MStatus status;
    MPlug plug = m_enable.getPlug();
    if (plug.isNull() == true) {
        value = true;
        status = MS::kSuccess;
    } else {
        status = m_enable.getValue(value, time, timeEvalMode);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }
    return status;
}

MStatus Marker::getWeight(double &value, const MTime &time,
                          const int timeEvalMode) {
    MStatus status = MS::kSuccess;
    MPlug plug = m_weight.getPlug();
    if (plug.isNull() == true) {
        value = 1.0;
        status = MS::kSuccess;
    } else {
        status = m_weight.getValue(value, time, timeEvalMode);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }
    return status;
}

MString Marker::getLongNodeName() {
    MObject nodeObj = Marker::getObject();

    MDagPath nodeDagPath;
    MStatus status = MDagPath::getAPathTo(nodeObj, nodeDagPath);
    CHECK_MSTATUS(status);

    MString result = nodeDagPath.fullPathName(&status);
    CHECK_MSTATUS(status);

    return result;
}
