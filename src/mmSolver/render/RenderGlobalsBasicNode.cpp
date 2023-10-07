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

#include "RenderGlobalsBasicNode.h"

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
#include "RenderOverrideBasic.h"
#include "mmSolver/nodeTypeIds.h"
#include "mmSolver/render/data/RenderColorFormat.h"
#include "mmSolver/utilities/debug_utils.h"

namespace mmsolver {
namespace render {

MTypeId RenderGlobalsBasicNode::m_id(MM_RENDER_GLOBALS_BASIC_TYPE_ID);

// Input Attributes
MObject RenderGlobalsBasicNode::a_silhouetteEnable;
MObject RenderGlobalsBasicNode::a_silhouetteDepthOffset;
MObject RenderGlobalsBasicNode::a_silhouetteWidth;
MObject RenderGlobalsBasicNode::a_silhouetteColor;
MObject RenderGlobalsBasicNode::a_silhouetteAlpha;

RenderGlobalsBasicNode::RenderGlobalsBasicNode() : m_attr_change_callback(0) {}

RenderGlobalsBasicNode::~RenderGlobalsBasicNode() {
    if (m_attr_change_callback) {
        MMessage::removeCallback(m_attr_change_callback);
    }
}

MString RenderGlobalsBasicNode::nodeName() {
    return MString(MM_RENDER_GLOBALS_BASIC_TYPE_NAME);
}

void RenderGlobalsBasicNode::postConstructor() {
    MObject obj = thisMObject();
    if ((m_attr_change_callback == 0) && (!obj.isNull())) {
        m_attr_change_callback =
            MNodeMessage::addAttributeChangedCallback(obj, attr_change_func);
    }
}

void RenderGlobalsBasicNode::attr_change_func(
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

    RenderOverrideBasic *override_ptr =
        (RenderOverrideBasic *)renderer->findRenderOverride(
            MM_RENDERER_BASIC_NAME);
    if (override_ptr == nullptr) {
        MGlobal::displayError(kRendererBasicCmdName + " is not registered.");
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

MStatus RenderGlobalsBasicNode::compute(const MPlug & /*plug*/,
                                        MDataBlock & /*data*/) {
    // This node does not compute any values.
    return MS::kUnknownParameter;
}

void *RenderGlobalsBasicNode::creator() {
    return (new RenderGlobalsBasicNode());
}

MStatus RenderGlobalsBasicNode::initialize() {
    MStatus status;
    MFnNumericAttribute numeric_attribute;
    MFnEnumAttribute enum_attribute;

    // Silhouette Enable
    {
        a_silhouetteEnable = numeric_attribute.create(
            kAttrNameSilhouetteEnable, "slhttenbl", MFnNumericData::kBoolean,
            static_cast<int>(kSilhouetteEnableDefault));
        CHECK_MSTATUS(numeric_attribute.setStorable(true));
        CHECK_MSTATUS(numeric_attribute.setConnectable(true));
        CHECK_MSTATUS(numeric_attribute.setKeyable(true));
        CHECK_MSTATUS(addAttribute(a_silhouetteEnable));
    }

    // Silhouette Depth Offset
    {
        auto depth_offset_max = 0.0;
        auto depth_offset_soft_min = -10.0;
        auto depth_offset_soft_max = -0.1;
        a_silhouetteDepthOffset = numeric_attribute.create(
            kAttrNameSilhouetteDepthOffset, "slhttdpthoffst",
            MFnNumericData::kDouble, kSilhouetteDepthOffsetDefault);
        CHECK_MSTATUS(numeric_attribute.setStorable(true));
        CHECK_MSTATUS(numeric_attribute.setConnectable(true));
        CHECK_MSTATUS(numeric_attribute.setKeyable(true));
        CHECK_MSTATUS(numeric_attribute.setMax(depth_offset_max));
        CHECK_MSTATUS(numeric_attribute.setSoftMin(depth_offset_soft_min));
        CHECK_MSTATUS(numeric_attribute.setSoftMax(depth_offset_soft_max));
        CHECK_MSTATUS(addAttribute(a_silhouetteDepthOffset));
    }

    // Silhouette Width
    {
        auto width_min = 0.0;
        auto width_soft_min = 1.0;
        auto width_soft_max = 10.0;
        a_silhouetteWidth = numeric_attribute.create(
            kAttrNameSilhouetteWidth, "slhttwdth", MFnNumericData::kDouble,
            kSilhouetteWidthDefault);
        CHECK_MSTATUS(numeric_attribute.setStorable(true));
        CHECK_MSTATUS(numeric_attribute.setConnectable(true));
        CHECK_MSTATUS(numeric_attribute.setKeyable(true));
        CHECK_MSTATUS(numeric_attribute.setMin(width_min));
        CHECK_MSTATUS(numeric_attribute.setSoftMin(width_soft_min));
        CHECK_MSTATUS(numeric_attribute.setSoftMax(width_soft_max));
        CHECK_MSTATUS(addAttribute(a_silhouetteWidth));
    }

    // Silhouette Color (RGB)
    {
        a_silhouetteColor =
            numeric_attribute.createColor(kAttrNameSilhouetteColor, "slhttclr");
        CHECK_MSTATUS(numeric_attribute.setStorable(true));
        CHECK_MSTATUS(numeric_attribute.setConnectable(true));
        CHECK_MSTATUS(numeric_attribute.setKeyable(true));
        CHECK_MSTATUS(numeric_attribute.setDefault(kSilhouetteColorDefault[0],
                                                   kSilhouetteColorDefault[1],
                                                   kSilhouetteColorDefault[2]));
        CHECK_MSTATUS(addAttribute(a_silhouetteColor));
    }

    // Silhouette Alpha
    {
        auto alpha_min = 0.0;
        auto alpha_max = 1.0;
        a_silhouetteAlpha = numeric_attribute.create(
            kAttrNameSilhouetteAlpha, "slhttalp", MFnNumericData::kDouble,
            kSilhouetteAlphaDefault);
        CHECK_MSTATUS(numeric_attribute.setStorable(true));
        CHECK_MSTATUS(numeric_attribute.setConnectable(true));
        CHECK_MSTATUS(numeric_attribute.setKeyable(true));
        CHECK_MSTATUS(numeric_attribute.setMin(alpha_min));
        CHECK_MSTATUS(numeric_attribute.setMax(alpha_max));
        CHECK_MSTATUS(addAttribute(a_silhouetteAlpha));
    }

    return MS::kSuccess;
}

}  // namespace render
}  // namespace mmsolver
