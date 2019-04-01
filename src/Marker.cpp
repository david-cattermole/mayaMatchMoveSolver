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

#include <maya/MFnDependencyNode.h>
#include <maya/MPlug.h>
#include <maya/MObject.h>
#include <maya/MFnMatrixData.h>
#include <maya/MMatrix.h>
#include <maya/MPoint.h>

#include <memory>

#include <mayaUtils.h>
#include <Camera.h>
#include <Bundle.h>
#include <Marker.h>
#include <Attr.h>

Marker::Marker() :
        m_nodeName(""),
        m_object(),
        m_camera(),
        m_bundle() {
    m_matrix.setAttrName("worldMatrix");
    m_px.setAttrName("translateX");
    m_py.setAttrName("translateY");
    m_enable.setAttrName("enable");
    m_weight.setAttrName("weight");
}

MString Marker::getNodeName() const {
    return MString(m_nodeName);
}

MStatus Marker::setNodeName(MString value) {
    MStatus status = MS::kSuccess;
    if (value != m_nodeName) {
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
    }
    m_nodeName = value;
    return status;
}

MObject Marker::getObject() {
    MStatus status;
    MString name = Marker::getNodeName();
    status = getAsObject(name, m_object);
    return m_object;
}

CameraPtr Marker::getCamera() {
    return m_camera;
}

MStatus Marker::setCamera(CameraPtr &value) {
    m_camera = value;
    return MS::kSuccess;
}

BundlePtr Marker::getBundle() {
    return m_bundle;
}

MStatus Marker::setBundle(BundlePtr &value) {
    m_bundle = value;
    return MS::kSuccess;
}

Attr &Marker::getMatrixAttr() {
    return m_matrix;
}

Attr &Marker::getEnableAttr() {
    return m_enable;
}

Attr &Marker::getWeightAttr() {
    return m_weight;
}

Attr &Marker::getPosXAttr() {
    return m_px;
}

Attr &Marker::getPosYAttr() {
    return m_py;
}

MStatus Marker::getMatrix(MMatrix &value, const MTime &time) {
    return m_matrix.getValue(value, time);
}

MStatus Marker::getMatrix(MMatrix &value) {
    return m_matrix.getValue(value);
}

MStatus Marker::getPos(double &x, double &y, double &z, const MTime &time) {
    MStatus status;
    MMatrix matrix;
    status = Marker::getMatrix(matrix, time);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    x = matrix(3, 0);
    y = matrix(3, 1);
    z = matrix(3, 2);
    return status;
}

MStatus Marker::getPos(MPoint &point, const MTime &time) {
    MStatus status;
    MMatrix matrix;
    status = Marker::getMatrix(matrix, time);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    point.x = matrix(3, 0);
    point.y = matrix(3, 1);
    point.z = matrix(3, 2);
    point.w = matrix(3, 3);
    point.cartesianize();
    return status;
}

MStatus Marker::getPos(double &x, double &y, double &z) {
    MTime time = MAnimControl::currentTime();
    MStatus status = Marker::getPos(x, y, z, time);
    return status;
}

MStatus Marker::getPos(MPoint &point) {
    MTime time = MAnimControl::currentTime();
    MStatus status = Marker::getPos(point, time);
    return status;
}

MStatus Marker::getEnable(bool &value, const MTime &time) {
    MStatus status;
    MPlug plug = m_enable.getPlug();
    if (plug.isNull() == true) {
        value = true;
        status = MS::kSuccess;
    } else {
        status = m_enable.getValue(value, time);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }
    return status;
}

MStatus Marker::getWeight(double &value, const MTime &time) {
    MStatus status;
    MPlug plug = m_weight.getPlug();
    if (plug.isNull() == true) {
        value = 1.0;
        status = MS::kSuccess;
    } else {
        status = m_weight.getValue(value, time);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }
    return status;
}
