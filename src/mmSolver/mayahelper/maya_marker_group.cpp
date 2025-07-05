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
 * Querying a marker group node.
 */

#include "maya_marker_group.h"

// STL
#include <memory>

// Maya
#include <maya/MDagPath.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MFnMatrixData.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>

// MM Solver
#include "maya_attr.h"
#include "maya_utils.h"
#include "mmSolver/adjust/adjust_defines.h"

MarkerGroup::MarkerGroup() : m_nodeName(""), m_object() {
    m_depth.setAttrName("depth");
    m_overscan_x.setAttrName("overscanX");
    m_overscan_y.setAttrName("overscanY");
}

MString MarkerGroup::getNodeName() const { return MString(m_nodeName); }

MStatus MarkerGroup::setNodeName(MString value) {
    MStatus status = MS::kSuccess;
    if (value != m_nodeName) {
        m_object = MObject();

        status = m_overscan_x.setNodeName(value);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

        status = m_overscan_y.setNodeName(value);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

        status = m_depth.setNodeName(value);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

        m_nodeName = value;
    }
    return status;
}

MObject MarkerGroup::getObject() {
    if (m_object.isNull()) {
        MStatus status;
        MString name = MarkerGroup::getNodeName();
        status = getAsObject(name, m_object);
        MMSOLVER_CHECK_MSTATUS(status);
    }
    return m_object;
}

Attr &MarkerGroup::getDepthAttr() { return m_depth; }

Attr &MarkerGroup::getOverscanXAttr() { return m_overscan_x; }

Attr &MarkerGroup::getOverscanYAttr() { return m_overscan_y; }

MStatus MarkerGroup::getDepth(double &value, const MTime &time,
                              const int32_t timeEvalMode) {
    MStatus status;
    MPlug plug = m_depth.getPlug();
    if (plug.isNull() == true) {
        value = 1.0;
        status = MS::kSuccess;
    } else {
        status = m_depth.getValue(value, time, timeEvalMode);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }
    return status;
}

MStatus MarkerGroup::getOverscanXY(double &x, double &y, const MTime &time,
                                   const int32_t timeEvalMode) {
    MStatus status;
    auto attr_overscan_x = MarkerGroup::getOverscanXAttr();
    auto attr_overscan_y = MarkerGroup::getOverscanYAttr();
    status = attr_overscan_x.getValue(x, time, timeEvalMode);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    status = attr_overscan_y.getValue(y, time, timeEvalMode);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    return status;
}

MStatus MarkerGroup::getOverscanXY(double &x, double &y,
                                   const int32_t timeEvalMode) {
    MTime time = MAnimControl::currentTime();
    MStatus status = MarkerGroup::getOverscanXY(x, y, time, timeEvalMode);
    return status;
}

MString MarkerGroup::getLongNodeName() {
    MString result;
    MStatus status;

    MObject nodeObj = MarkerGroup::getObject();
    MDagPath nodeDagPath;
    status = MDagPath::getAPathTo(nodeObj, nodeDagPath);
    MMSOLVER_CHECK_MSTATUS(status);

    MString nodeName = nodeDagPath.fullPathName(&status);
    MMSOLVER_CHECK_MSTATUS(status);

    return nodeName;
}
