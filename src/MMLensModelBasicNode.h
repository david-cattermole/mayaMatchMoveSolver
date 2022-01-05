/*
 * Copyright (C) 2020 David Cattermole.
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
 * Define a lens. The lens is a simple brownian model.
 */

#ifndef MM_LENS_MODEL_BASIC_NODE_H
#define MM_LENS_MODEL_BASIC_NODE_H

#include <maya/MPxNode.h>
#include <maya/MString.h>
#include <maya/MObject.h>
#include <maya/MTypeId.h>


class MMLensModelBasicNode : public MPxNode {
public:
    MMLensModelBasicNode();

    virtual ~MMLensModelBasicNode();

    virtual MStatus compute(const MPlug &plug, MDataBlock &data);

    static void *creator();

    static MStatus initialize();

    static MString nodeName();

    static MTypeId m_id;

    // Input Attributes
    static MObject a_inLens;
    static MObject a_enable;
    static MObject a_k1;
    static MObject a_k2;

    // Output Attributes
    static MObject a_outLens;
};

#endif // MM_LENS_MODEL_BASIC_NODE_H
