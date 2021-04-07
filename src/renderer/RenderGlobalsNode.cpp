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
 * Stores global values for the mmSolver viewport renderer.
 */


#include <maya/MGlobal.h>
#include <maya/MStreamUtils.h>
#include <maya/MPlug.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MFnNumericAttribute.h>
// #include <maya/MFnEnumAttribute.h>
#include <maya/MFnNumericData.h>
#include <maya/MMessage.h>
#include <maya/MNodeMessage.h>
#include <maya/MViewport2Renderer.h>
#include <maya/M3dView.h>

#include <cstring>
#include <cmath>

#include <nodeTypeIds.h>

#include "RenderOverride.h"
#include "RenderGlobalsNode.h"

namespace mmsolver {
namespace renderer {


MTypeId RenderGlobalsNode::m_id(MM_RENDER_GLOBALS_TYPE_ID);

// Input Attributes
MObject RenderGlobalsNode::a_wireframeAlpha;

RenderGlobalsNode::RenderGlobalsNode()
        : m_attr_change_callback(0) {}

RenderGlobalsNode::~RenderGlobalsNode() {

    if (m_attr_change_callback) {
        MMessage::removeCallback(m_attr_change_callback);
    }
}

MString RenderGlobalsNode::nodeName() {
    return MString(MM_RENDER_GLOBALS_TYPE_NAME);
}

void RenderGlobalsNode::postConstructor() {
    MObject obj = thisMObject();
    if((m_attr_change_callback == 0) && (!obj.isNull())) {
        m_attr_change_callback = MNodeMessage::addAttributeChangedCallback(
            obj, attr_change_func);
    }
}


void RenderGlobalsNode::attr_change_func(MNodeMessage::AttributeMessage msg,
                                         MPlug &plug,
                                         MPlug & /*other_plug*/,
                                         void* /*client_data*/) {
    MStatus status = MS::kFailure;
    if (msg & MNodeMessage::kAttributeSet) {
        MStreamUtils::stdOutStream()
            << "Attribute value set on: " << plug.info() << '\n';
    } else {
        return;
    }
    MString plug_name = plug.partialName(
        /*includeNodeName=*/ false,
        /*includeNonMandatoryIndices=*/ false,
        /*includeInstancedIndices=*/ false,
        /*useAlias=*/ false,
        /*useFullAttributePath=*/ false,
        /*useLongNames=*/ true,
        &status);
    if (status != MS::kSuccess) {
        return;
    }

    MHWRender::MRenderer *renderer = MHWRender::MRenderer::theRenderer();
    if (!renderer) {
        MGlobal::displayError("VP2 renderer not initialized.");
        return;
    }

    RenderOverride *override_ptr =
        (RenderOverride *) renderer->findRenderOverride(
            MM_RENDERER_NAME);
    if (override_ptr == nullptr) {
        MGlobal::displayError("mmRenderer is not registered.");
        return;
    }

    if (plug_name == "wireframeAlpha") {
        auto value = plug.asDouble(&status);
        CHECK_MSTATUS(status);
        override_ptr->setWireframeAlpha(value);
        MStreamUtils::stdOutStream()
            << "Wireframe Alpha value set: " << value << '\n';
    }

    // Update viewport.
    M3dView view = M3dView::active3dView(&status);
    if (!status) {
        MGlobal::displayWarning("Failed to find an active 3d view.");
        return;
    }
    view.refresh(/*all=*/ false, /*force=*/ true);
    return;
}


MStatus RenderGlobalsNode::compute(const MPlug &/*plug*/,
                                   MDataBlock &/*data*/) {
    // This node does not compute any values.
    return MS::kUnknownParameter;
}

void *RenderGlobalsNode::creator() {
    return (new RenderGlobalsNode());
}

MStatus RenderGlobalsNode::initialize() {
    MStatus status;
    MFnNumericAttribute numericAttr;
    // MFnEnumAttribute enumAttr;

    // MHWRender::kR16G16B16A16_FLOAT;
    // MHWRender::kR32G32B32A32_FLOAT;
    // MHWRender::kR8G8B8A8_UNORM;;

    // // Film Fit; 0=fill, 1=horizontal, 2=vertical, 3=overscan
    // a_filmFit = enumAttr.create(
    //     "filmFit", "ff", 0, &status);
    // CHECK_MSTATUS(status);
    // CHECK_MSTATUS(enumAttr.addField("Fit", 0));
    // CHECK_MSTATUS(enumAttr.addField("Horizontal", 1));
    // CHECK_MSTATUS(enumAttr.addField("Vertical", 2));
    // CHECK_MSTATUS(enumAttr.addField("Overscan", 3));
    // CHECK_MSTATUS(enumAttr.setStorable(true));
    // CHECK_MSTATUS(enumAttr.setKeyable(true));
    // CHECK_MSTATUS(addAttribute(a_filmFit));

    // Wireframe Alpha
    auto alpha_min = 0.0;
    auto alpha_max = 1.0;
    a_wireframeAlpha = numericAttr.create(
        "wireframeAlpha", "wralp",
        MFnNumericData::kDouble, 1.0);
    CHECK_MSTATUS(numericAttr.setStorable(true));
    CHECK_MSTATUS(numericAttr.setKeyable(true));
    CHECK_MSTATUS(numericAttr.setMin(alpha_min));
    CHECK_MSTATUS(numericAttr.setMax(alpha_max));
    CHECK_MSTATUS(addAttribute(a_wireframeAlpha));

    return MS::kSuccess;
}

} // namespace renderer
} // namespace mmsolver
