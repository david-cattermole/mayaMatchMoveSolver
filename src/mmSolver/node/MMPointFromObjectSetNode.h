/*
 * Copyright (C) 2025 David Cattermole.
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
 * Get a 3D point from the members (objects and components) of an
 * object set node.
 */

#ifndef MM_POINT_FROM_OBJECT_SET_NODE_H
#define MM_POINT_FROM_OBJECT_SET_NODE_H

// Maya
#include <maya/MFnDependencyNode.h>
#include <maya/MObject.h>
#include <maya/MPxNode.h>
#include <maya/MString.h>
#include <maya/MTypeId.h>

namespace mmsolver {

class MMPointFromObjectSetNode : public MPxNode {
public:
    MMPointFromObjectSetNode();

    virtual ~MMPointFromObjectSetNode();

    virtual MStatus setDependentsDirty(const MPlug &plug,
                                       MPlugArray &plugArray);

    virtual MStatus compute(const MPlug &plug, MDataBlock &data);

    static void *creator();

    static MStatus initialize();

    static MString nodeName();

    static MTypeId m_id;

    // Input Attributes
    //
    // Set Node Message.
    static MObject a_setNode;

    static MObject a_matrixArray;
    static MObject a_meshArray;

    // Output Attributes
    //
    // Point.
    static MObject a_outPoint;
    static MObject a_outPointX;
    static MObject a_outPointY;
    static MObject a_outPointZ;

    // Matrix.
    static MObject a_outMatrix;
};

}  // namespace mmsolver

#endif  // MM_POINT_FROM_OBJECT_SET_NODE_H
