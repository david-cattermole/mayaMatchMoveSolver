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
 * Evaluate a lens distortion node to compute new coordinates.
 */

#ifndef MM_LENS_EVALUATE_NODE_H
#define MM_LENS_EVALUATE_NODE_H

#include <maya/MPxNode.h>

#include <maya/MString.h>
#include <maya/MObject.h>
#include <maya/MTime.h>

#include <maya/MFnDependencyNode.h>
#include <maya/MTypeId.h>


class MMLensEvaluateNode : public MPxNode {
public:
    MMLensEvaluateNode();

    virtual ~MMLensEvaluateNode();

    virtual MStatus compute(const MPlug &plug, MDataBlock &data);

    static void *creator();

    static MStatus initialize();

    static MString nodeName();

    static MTypeId m_id;

    // Input Attributes
    static MObject a_inPoint;
    static MObject a_inPointX;
    static MObject a_inPointY;
    static MObject a_inPointZ;

    // Output Attributes
    static MObject a_outPoint;
    static MObject a_outPointX;
    static MObject a_outPointY;
    static MObject a_outPointZ;

};

#endif // MM_LENS_EVALUATE_NODE_H
