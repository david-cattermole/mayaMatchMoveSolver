/*
 * Copyright (C) 2021 David Cattermole.
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
 * Computes 2D line intersection.
 */

#ifndef MM_LINE_INTERSECTION_NODE_H
#define MM_LINE_INTERSECTION_NODE_H

// Maya
#include <maya/MPxNode.h>
#include <maya/MString.h>
#include <maya/MObject.h>
#include <maya/MTime.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MTypeId.h>

class MMLineIntersectNode : public MPxNode {
public:
    MMLineIntersectNode();

    virtual ~MMLineIntersectNode();

    virtual MStatus compute(const MPlug &plug, MDataBlock &data);

    static void *creator();

    static MStatus initialize();

    static MString nodeName();

    static MTypeId m_id;

    // Input Attributes
    //
    // Points
    static MObject a_pointA;
    static MObject a_pointAX;
    static MObject a_pointAY;

    static MObject a_pointB;
    static MObject a_pointBX;
    static MObject a_pointBY;

    static MObject a_pointC;
    static MObject a_pointCX;
    static MObject a_pointCY;

    static MObject a_pointD;
    static MObject a_pointDX;
    static MObject a_pointDY;

    // Output Attributes
    static MObject a_outVanishingPoint;
    static MObject a_outVanishingPointX;
    static MObject a_outVanishingPointY;

    static MObject a_outCosineAngle;
};


#endif // MM_LINE_INTERSECTION_NODE_H
