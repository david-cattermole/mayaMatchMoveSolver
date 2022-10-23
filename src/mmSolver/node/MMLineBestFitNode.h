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
 * Computes 2D line best fit - from a list of points a "best-fit"
 * straight line is estimated.
 *
 * For example this node can be used to visualise a straight line
 * through a number of Markers. So if you place a bunch of markers on
 * a line then add all the 'worldMatrix[0]' nodes into this node, the
 * line computed will represent a perfectly straight line. If lens
 * distortion is perfectly corrected for the shot, the Marker points
 * will perfectly line up with the plate.
 */

#ifndef MM_LINE_BEST_FIT_NODE_H
#define MM_LINE_BEST_FIT_NODE_H

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

class MMLineBestFitNode : public MPxNode {
public:
    MMLineBestFitNode();

    virtual ~MMLineBestFitNode();

    virtual MStatus compute(const MPlug &plug, MDataBlock &data);

    static void *creator();

    static MStatus initialize();

    static MString nodeName();

    static MTypeId m_id;

    // Input Attributes
    static MObject m_transformMatrix;
    static MObject m_parentInverseMatrix;
    static MObject m_lineLength;

    // Output Attributes
    static MObject m_outLine;
    static MObject m_outLineCenterX;
    static MObject m_outLineCenterY;
    static MObject m_outLineDirX;
    static MObject m_outLineDirY;
    static MObject m_outLineSlope;
    static MObject m_outLineAngle;

    static MObject m_outLinePointA;
    static MObject m_outLinePointAX;
    static MObject m_outLinePointAY;

    static MObject m_outLinePointB;
    static MObject m_outLinePointBX;
    static MObject m_outLinePointBY;

private:
    // Internal Data.
    //
    // By re-using some memory we should get better cache locality
    // and/or less memory fragmentation.
    rust::Vec<mmscenegraph::Real> m_point_data_x;
    rust::Vec<mmscenegraph::Real> m_point_data_y;
};

}  // namespace mmsolver

#endif  // MM_LINE_BEST_FIT_NODE_H
