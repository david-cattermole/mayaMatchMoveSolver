/*
 * Copyright (C) 2021, 2023 David Cattermole.
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

#ifndef MM_SOLVER_RENDER_RENDER_GLOBALS_NODE_H
#define MM_SOLVER_RENDER_RENDER_GLOBALS_NODE_H

// Maya
#include <maya/MFnDependencyNode.h>
#include <maya/MNodeMessage.h>
#include <maya/MObject.h>
#include <maya/MPxNode.h>
#include <maya/MString.h>
#include <maya/MTypeId.h>

namespace mmsolver {
namespace render {

class RenderGlobalsNode : public MPxNode {
public:
    RenderGlobalsNode();

    ~RenderGlobalsNode() override;

    MStatus compute(const MPlug &plug, MDataBlock &data) override;

    static void *creator();

    void postConstructor() override;

    static MStatus initialize();

    static MString nodeName();

    static MTypeId m_id;

    // Input Attributes
    static MObject a_silhouetteEnable;
    static MObject a_silhouetteDepthOffset;
    static MObject a_silhouetteWidth;
    static MObject a_silhouetteColor;
    static MObject a_silhouetteAlpha;

private:
    // Callback IDs for tracking viewport changes.
    MCallbackId m_attr_change_callback;
    static void attr_change_func(MNodeMessage::AttributeMessage msg,
                                 MPlug &plug, MPlug &other_plug,
                                 void *client_data);
};

}  // namespace render
}  // namespace mmsolver

#endif  // MM_SOLVER_RENDER_RENDER_GLOBALS_NODE_H
