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
 * Bundles - objects representing 3D positions can be queried.
 */

#include <maya/MPlug.h>
#include <maya/MObject.h>
#include <maya/MDataHandle.h>
#include <maya/MFnMatrixData.h>
#include <maya/MMatrix.h>
#include <maya/MPoint.h>

#include <mayaUtils.h>
#include <Marker.h>
#include <Bundle.h>
#include <Attr.h>


Bundle::Bundle() :
        m_nodeName(""),
        m_object(),
        m_weight(1.0),
        m_matrix() {
    m_matrix.setAttrName("worldMatrix");
}


MString Bundle::getNodeName() const {
    return m_nodeName;
}

MStatus Bundle::setNodeName(MString value) {
    MStatus status = MS::kSuccess;
    if (value != m_nodeName) {
        status = m_matrix.setNodeName(value);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }
    m_nodeName = value;
    return status;
}

MObject Bundle::getObject() {
    MStatus status;
    MString name = Bundle::getNodeName();
    status = getAsObject(name, m_object);
    return m_object;
}

double Bundle::getWeight() const {
    return m_weight;
}

MStatus Bundle::setWeight(double value) {
    m_weight = value;
    return MS::kSuccess;
}

Attr &Bundle::getMatrixAttr() {
    return m_matrix;
}

MStatus Bundle::getMatrix(MMatrix &value, const MTime &time) {
    return m_matrix.getValue(value, time);
}


MStatus Bundle::getMatrix(MMatrix &value) {
    return m_matrix.getValue(value);
}

MStatus Bundle::getPos(double &x, double &y, double &z, const MTime &time) {
    MStatus status;
    MMatrix matrix;
    status = Bundle::getMatrix(matrix, time);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    x = matrix(3, 0);
    y = matrix(3, 1);
    z = matrix(3, 2);
    return status;
}

MStatus Bundle::getPos(MPoint &point, const MTime &time) {
    MStatus status;
    MMatrix matrix;
    status = Bundle::getMatrix(matrix, time);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    point.x = matrix(3, 0);
    point.y = matrix(3, 1);
    point.z = matrix(3, 2);
    point.w = matrix(3, 3);
    point.cartesianize();
    return status;
}

MStatus Bundle::getPos(double &x, double &y, double &z) {
    MTime time = MAnimControl::currentTime();
    MStatus status = Bundle::getPos(x, y, z, time);
    return status;
}

MStatus Bundle::getPos(MPoint &point) {
    MTime time = MAnimControl::currentTime();
    MStatus status = Bundle::getPos(point, time);
    return status;
}
