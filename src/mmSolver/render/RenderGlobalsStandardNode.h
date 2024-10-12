/*
 * Copyright (C) 2021, 2023, 2024 David Cattermole.
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
 * Stores global values for the mmSolver viewport renderer.
 */

#ifndef MM_SOLVER_RENDER_RENDER_GLOBALS_STANDARD_NODE_H
#define MM_SOLVER_RENDER_RENDER_GLOBALS_STANDARD_NODE_H

// Maya
#include <maya/MFnDependencyNode.h>
#include <maya/MNodeMessage.h>
#include <maya/MObject.h>
#include <maya/MPxNode.h>
#include <maya/MString.h>
#include <maya/MTypeId.h>

namespace mmsolver {
namespace render {

class RenderGlobalsStandardNode : public MPxNode {
public:
    RenderGlobalsStandardNode();

    ~RenderGlobalsStandardNode() override;

    MStatus compute(const MPlug &plug, MDataBlock &data) override;

    static void *creator();

    void postConstructor() override;

    static MStatus initialize();

    static MString nodeName();

    static MTypeId m_id;

private:
    // Callback IDs for tracking viewport changes.
    MCallbackId m_attr_change_callback;
    static void attr_change_func(MNodeMessage::AttributeMessage msg,
                                 MPlug &plug, MPlug &other_plug,
                                 void *client_data);
};

}  // namespace render
}  // namespace mmsolver

#endif  // MM_SOLVER_RENDER_RENDER_GLOBALS_STANDARD_NODE_H
