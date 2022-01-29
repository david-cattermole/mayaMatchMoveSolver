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

#include "RenderGlobalsNode.h"

// STL
#include <cstring>
#include <cmath>

// Maya
#include <maya/MGlobal.h>
#include <maya/MStreamUtils.h>
#include <maya/MPlug.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnEnumAttribute.h>
#include <maya/MFnNumericData.h>
#include <maya/MMessage.h>
#include <maya/MNodeMessage.h>
#include <maya/MViewport2Renderer.h>
#include <maya/M3dView.h>

#include "mmSolver/nodeTypeIds.h"
#include "RenderOverride.h"

namespace mmsolver {
namespace render {


MTypeId RenderGlobalsNode::m_id(MM_RENDER_GLOBALS_TYPE_ID);

// Input Attributes
MObject RenderGlobalsNode::a_mode;
MObject RenderGlobalsNode::a_renderFormat;
MObject RenderGlobalsNode::a_multiSampleCount;
MObject RenderGlobalsNode::a_wireframeAlpha;
MObject RenderGlobalsNode::a_edgeThickness;
MObject RenderGlobalsNode::a_edgeThreshold;

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

    // TODO: When the node is created for the first time, it should
    // query the RenderOverride's values and set the attributes on the
    // node.
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

    if (plug_name == "edgeThickness") {
        auto value = plug.asDouble(&status);
        CHECK_MSTATUS(status);
        override_ptr->setEdgeThickness(value);
        MStreamUtils::stdOutStream()
            << "Edge Thickness value set: " << value << '\n';
    }

    if (plug_name == "edgeThreshold") {
        auto value = plug.asDouble(&status);
        CHECK_MSTATUS(status);
        override_ptr->setEdgeThreshold(value);
        MStreamUtils::stdOutStream()
            << "Edge Threshold value set: " << value << '\n';
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
    MFnNumericAttribute nAttr;
    MFnEnumAttribute eAttr;

    // Render Format; 0=8-bit float, 1=16-bit float, 2=32-bit float
    a_renderFormat = eAttr.create(
        "renderFormat", "rndfmt",
        static_cast<short>(RenderFormat::kRGBA8BitInt),
        &status);
    CHECK_MSTATUS(status);
    CHECK_MSTATUS(eAttr.addField(
                      "RGBA 8-Bit (integer)",
                      static_cast<short>(RenderFormat::kRGBA8BitInt)));
    CHECK_MSTATUS(eAttr.addField(
                      "RGBA 16-Bit (float)",
                      static_cast<short>(RenderFormat::kRGBA16BitFloat)));
    CHECK_MSTATUS(eAttr.addField(
                      "RGBA 32-Bit (float)",
                      static_cast<short>(RenderFormat::kRGBA32BitFloat)));
    CHECK_MSTATUS(eAttr.setStorable(true));
    CHECK_MSTATUS(eAttr.setKeyable(true));
    CHECK_MSTATUS(addAttribute(a_renderFormat));

    // Render Format; 0=8-bit float, 1=16-bit float, 2=32-bit float
    a_mode = eAttr.create(
        "mode", "md", 0, &status);
    CHECK_MSTATUS(status);
    CHECK_MSTATUS(eAttr.addField("Zero", 0));
    CHECK_MSTATUS(eAttr.addField("One", 1));
    CHECK_MSTATUS(eAttr.addField("Two", 2));
    CHECK_MSTATUS(eAttr.addField("Three", 3));
    CHECK_MSTATUS(eAttr.addField("Four", 4));
    CHECK_MSTATUS(eAttr.setStorable(true));
    CHECK_MSTATUS(eAttr.setKeyable(true));
    CHECK_MSTATUS(addAttribute(a_mode));

    // Multi-Sample Count
    auto sample_min = 1;
    auto sample_max = 128;
    a_multiSampleCount = nAttr.create(
        "multiSampleCount", "mssmpct",
        MFnNumericData::kInt, 1);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setMin(sample_min));
    CHECK_MSTATUS(nAttr.setMax(sample_max));
    CHECK_MSTATUS(addAttribute(a_multiSampleCount));

    // Wireframe Alpha
    auto alpha_min = 0.0;
    auto alpha_max = 1.0;
    a_wireframeAlpha = nAttr.create(
        "wireframeAlpha", "wralp",
        MFnNumericData::kDouble, kWireframeAlphaDefault);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setMin(alpha_min));
    CHECK_MSTATUS(nAttr.setMax(alpha_max));
    CHECK_MSTATUS(addAttribute(a_wireframeAlpha));

    // Edge Thickness
    auto thickness_min = 0.0;
    // auto thickness_max = 1.0;
    a_edgeThickness = nAttr.create(
        "edgeThickness", "edgthk",
        MFnNumericData::kDouble, kEdgeThicknessDefault);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setMin(thickness_min));
    // CHECK_MSTATUS(nAttr.setMax(thickness_max));
    CHECK_MSTATUS(addAttribute(a_edgeThickness));

    // Edge Threshold
    auto threshold_min = 0.0;
    auto threshold_max = 1.0;
    a_edgeThreshold = nAttr.create(
        "edgeThreshold", "edgthd",
        MFnNumericData::kDouble, kEdgeThresholdDefault);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setMin(threshold_min));
    CHECK_MSTATUS(nAttr.setMax(threshold_max));
    CHECK_MSTATUS(addAttribute(a_edgeThreshold));

    return MS::kSuccess;
}

} // namespace render
} // namespace mmsolver
