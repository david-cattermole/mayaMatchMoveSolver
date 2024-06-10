/*
 * Copyright (C) 2024 David Cattermole.
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
 * Calculates the frame number of an image sequence.
 */

#ifndef MM_IMAGE_SEQUENCE_FRAME_LOGIC_NODE_H
#define MM_IMAGE_SEQUENCE_FRAME_LOGIC_NODE_H

// Maya
#include <maya/MFnDependencyNode.h>
#include <maya/MPxNode.h>
#include <maya/MString.h>
#include <maya/MTime.h>
#include <maya/MTypeId.h>
#include <maya/MVector.h>

namespace mmsolver {

class MMImageSequenceFrameLogicNode : public MPxNode {
public:
    MMImageSequenceFrameLogicNode();

    virtual ~MMImageSequenceFrameLogicNode();

    virtual MStatus compute(const MPlug &plug, MDataBlock &data);

    static void *creator();

    static MStatus initialize();

    static MString nodeName();

    static MTypeId m_id;

    // Input Attributes
    static MObject a_inFrame;
    static MObject a_firstFrame;
    static MObject a_startFrame;
    static MObject a_endFrame;

    // Output Attributes
    static MObject a_outFrame;
};

}  // namespace mmsolver

#endif  // MM_IMAGE_SEQUENCE_FRAME_LOGIC_NODE_H
