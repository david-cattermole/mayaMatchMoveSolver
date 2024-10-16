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

#include "RenderGlobalsStandardNode.h"

// Maya
#include <maya/M3dView.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MFnEnumAttribute.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnNumericData.h>
#include <maya/MGlobal.h>
#include <maya/MMessage.h>
#include <maya/MNodeMessage.h>
#include <maya/MPlug.h>
#include <maya/MStreamUtils.h>
#include <maya/MViewport2Renderer.h>

// MM Solver
#include "RenderOverrideStandard.h"
#include "mmSolver/nodeTypeIds.h"
#include "mmSolver/render/data/RenderColorFormat.h"
#include "mmSolver/utilities/debug_utils.h"

namespace mmsolver {
namespace render {

MTypeId RenderGlobalsStandardNode::m_id(MM_RENDER_GLOBALS_STANDARD_TYPE_ID);

RenderGlobalsStandardNode::RenderGlobalsStandardNode()
    : m_attr_change_callback(0) {}

RenderGlobalsStandardNode::~RenderGlobalsStandardNode() {
    if (m_attr_change_callback) {
        MMessage::removeCallback(m_attr_change_callback);
    }
}

MString RenderGlobalsStandardNode::nodeName() {
    return MString(MM_RENDER_GLOBALS_STANDARD_TYPE_NAME);
}

void RenderGlobalsStandardNode::postConstructor() {
    MObject obj = thisMObject();
    if ((m_attr_change_callback == 0) && (!obj.isNull())) {
        m_attr_change_callback =
            MNodeMessage::addAttributeChangedCallback(obj, attr_change_func);
    }
}

void RenderGlobalsStandardNode::attr_change_func(
    MNodeMessage::AttributeMessage msg, MPlug &plug, MPlug & /*other_plug*/,
    void * /*client_data*/) {
    const bool verbose = false;

    MStatus status = MS::kFailure;
    if (msg & MNodeMessage::kAttributeSet) {
        MMSOLVER_MAYA_VRB("Attribute value set on: " << plug.info());
    } else {
        return;
    }
    MString plug_name = plug.partialName(
        /*includeNodeName=*/false,
        /*includeNonMandatoryIndices=*/false,
        /*includeInstancedIndices=*/false,
        /*useAlias=*/false,
        /*useFullAttributePath=*/false,
        /*useLongNames=*/true, &status);
    if (status != MS::kSuccess) {
        return;
    }

    MHWRender::MRenderer *renderer = MHWRender::MRenderer::theRenderer();
    if (!renderer) {
        MGlobal::displayError("VP2 renderer not initialized.");
        return;
    }

    const RenderOverrideStandard *override_ptr =
        (RenderOverrideStandard *)renderer->findRenderOverride(
            MM_RENDERER_STANDARD_NAME);
    if (override_ptr == nullptr) {
        MGlobal::displayError(kRendererStandardCmdName + " is not registered.");
        return;
    }

    // Update viewport.
    M3dView view = M3dView::active3dView(&status);
    if (!status) {
        MGlobal::displayWarning("Failed to find an active 3d view.");
        return;
    }
    view.refresh(/*all=*/false, /*force=*/true);
}

MStatus RenderGlobalsStandardNode::compute(const MPlug & /*plug*/,
                                           MDataBlock & /*data*/) {
    // This node does not compute any values.
    return MS::kUnknownParameter;
}

void *RenderGlobalsStandardNode::creator() {
    return (new RenderGlobalsStandardNode());
}

MStatus RenderGlobalsStandardNode::initialize() { return MS::kSuccess; }

}  // namespace render
}  // namespace mmsolver
