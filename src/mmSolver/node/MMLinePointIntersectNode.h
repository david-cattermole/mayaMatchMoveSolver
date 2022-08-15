/*
 * Copyright (C) 2022 David Cattermole.
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
 * Given a 3D point, find the closest point on a straight line.
 *
 * Essentially this will "constrain" a 3D transform's position to a
 * line defined by 2 x 3D points.
 */

#ifndef MM_LINE_POINT_INTERSECT_NODE_H
#define MM_LINE_POINT_INTERSECT_NODE_H

// Maya
#include <maya/MFnDependencyNode.h>
#include <maya/MObject.h>
#include <maya/MPxNode.h>
#include <maya/MString.h>
#include <maya/MTime.h>
#include <maya/MTypeId.h>

// MM SceneGraph
#include <mmscenegraph/mmscenegraph.h>

namespace mmsolver {

class MMLinePointIntersectNode : public MPxNode {
public:
    MMLinePointIntersectNode();

    virtual ~MMLinePointIntersectNode();

    virtual MStatus compute(const MPlug &plug, MDataBlock &data);

    static void *creator();

    static MStatus initialize();

    static MString nodeName();

    static MTypeId m_id;

    // Input Attributes
    static MObject m_inPoint;
    static MObject m_inPointX;
    static MObject m_inPointY;
    static MObject m_inPointZ;
    static MObject m_linePointA;
    static MObject m_linePointAX;
    static MObject m_linePointAY;
    static MObject m_linePointAZ;
    static MObject m_linePointB;
    static MObject m_linePointBX;
    static MObject m_linePointBY;
    static MObject m_linePointBZ;

    // Output Attributes
    static MObject m_outPoint;
    static MObject m_outPointX;
    static MObject m_outPointY;
    static MObject m_outPointZ;
    static MObject m_outDistance;
};

}  // namespace mmsolver

#endif  // MM_LINE_POINT_INTERSECT_NODE_H
