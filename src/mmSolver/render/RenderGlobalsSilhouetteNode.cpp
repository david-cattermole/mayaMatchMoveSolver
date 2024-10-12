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

#include "RenderGlobalsSilhouetteNode.h"

// STL
#include <cstdint>

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
#include "RenderOverrideSilhouette.h"
#include "mmSolver/nodeTypeIds.h"
#include "mmSolver/render/data/CullFace.h"
#include "mmSolver/utilities/debug_utils.h"

namespace mmsolver {
namespace render {

MTypeId RenderGlobalsSilhouetteNode::m_id(MM_RENDER_GLOBALS_SILHOUETTE_TYPE_ID);

// Input Attributes
MObject RenderGlobalsSilhouetteNode::a_enable;
MObject RenderGlobalsSilhouetteNode::a_overrideColor;
MObject RenderGlobalsSilhouetteNode::a_depthOffset;
MObject RenderGlobalsSilhouetteNode::a_width;
MObject RenderGlobalsSilhouetteNode::a_color;
MObject RenderGlobalsSilhouetteNode::a_alpha;
MObject RenderGlobalsSilhouetteNode::a_cullFace;
MObject RenderGlobalsSilhouetteNode::a_operationNum;

RenderGlobalsSilhouetteNode::RenderGlobalsSilhouetteNode()
    : m_attr_change_callback(0) {}

RenderGlobalsSilhouetteNode::~RenderGlobalsSilhouetteNode() {
    if (m_attr_change_callback) {
        MMessage::removeCallback(m_attr_change_callback);
    }
}

MString RenderGlobalsSilhouetteNode::nodeName() {
    return MString(MM_RENDER_GLOBALS_SILHOUETTE_TYPE_NAME);
}

void RenderGlobalsSilhouetteNode::postConstructor() {
    MObject obj = thisMObject();
    if ((m_attr_change_callback == 0) && (!obj.isNull())) {
        m_attr_change_callback =
            MNodeMessage::addAttributeChangedCallback(obj, attr_change_func);
    }
}

void RenderGlobalsSilhouetteNode::attr_change_func(
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

    RenderOverrideSilhouette *override_ptr =
        (RenderOverrideSilhouette *)renderer->findRenderOverride(
            MM_RENDERER_SILHOUETTE_NAME);
    if (override_ptr == nullptr) {
        MGlobal::displayError(kRendererSilhouetteCmdName +
                              " is not registered.");
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

MStatus RenderGlobalsSilhouetteNode::compute(const MPlug & /*plug*/,
                                             MDataBlock & /*data*/) {
    // This node does not compute any values.
    return MS::kUnknownParameter;
}

void *RenderGlobalsSilhouetteNode::creator() {
    return (new RenderGlobalsSilhouetteNode());
}

MStatus RenderGlobalsSilhouetteNode::initialize() {
    MStatus status;
    MFnNumericAttribute numeric_attribute;
    MFnEnumAttribute enum_attribute;

    // Silhouette Enable
    {
        a_enable = numeric_attribute.create(
            kAttrNameSilhouetteEnable, "enbl", MFnNumericData::kBoolean,
            static_cast<int>(kSilhouetteEnableDefault));
        CHECK_MSTATUS(numeric_attribute.setStorable(true));
        CHECK_MSTATUS(numeric_attribute.setConnectable(true));
        CHECK_MSTATUS(numeric_attribute.setKeyable(true));
        CHECK_MSTATUS(addAttribute(a_enable));
    }

    // Silhouette Override Color
    {
        a_overrideColor = numeric_attribute.create(
            kAttrNameSilhouetteOverrideColor, "ovrdcol",
            MFnNumericData::kBoolean,
            static_cast<int>(kSilhouetteOverrideColorDefault));
        CHECK_MSTATUS(numeric_attribute.setStorable(true));
        CHECK_MSTATUS(numeric_attribute.setConnectable(true));
        CHECK_MSTATUS(numeric_attribute.setKeyable(true));
        CHECK_MSTATUS(addAttribute(a_overrideColor));
    }

    // Silhouette Depth Offset
    {
        auto depth_offset_max = 0.0;
        auto depth_offset_soft_min = -10.0;
        auto depth_offset_soft_max = -0.1;
        a_depthOffset = numeric_attribute.create(
            kAttrNameSilhouetteDepthOffset, "dpthoffst",
            MFnNumericData::kDouble, kSilhouetteDepthOffsetDefault);
        CHECK_MSTATUS(numeric_attribute.setStorable(true));
        CHECK_MSTATUS(numeric_attribute.setConnectable(true));
        CHECK_MSTATUS(numeric_attribute.setKeyable(true));
        CHECK_MSTATUS(numeric_attribute.setMax(depth_offset_max));
        CHECK_MSTATUS(numeric_attribute.setSoftMin(depth_offset_soft_min));
        CHECK_MSTATUS(numeric_attribute.setSoftMax(depth_offset_soft_max));
        CHECK_MSTATUS(addAttribute(a_depthOffset));
    }

    // Silhouette Width
    {
        auto width_min = 0.0;
        auto width_soft_min = 1.0;
        auto width_soft_max = 10.0;
        a_width = numeric_attribute.create(kAttrNameSilhouetteWidth, "wdth",
                                           MFnNumericData::kDouble,
                                           kSilhouetteWidthDefault);
        CHECK_MSTATUS(numeric_attribute.setStorable(true));
        CHECK_MSTATUS(numeric_attribute.setConnectable(true));
        CHECK_MSTATUS(numeric_attribute.setKeyable(true));
        CHECK_MSTATUS(numeric_attribute.setMin(width_min));
        CHECK_MSTATUS(numeric_attribute.setSoftMin(width_soft_min));
        CHECK_MSTATUS(numeric_attribute.setSoftMax(width_soft_max));
        CHECK_MSTATUS(addAttribute(a_width));
    }

    // Silhouette Color (RGB)
    {
        a_color =
            numeric_attribute.createColor(kAttrNameSilhouetteColor, "clr");
        CHECK_MSTATUS(numeric_attribute.setStorable(true));
        CHECK_MSTATUS(numeric_attribute.setConnectable(true));
        CHECK_MSTATUS(numeric_attribute.setKeyable(true));
        CHECK_MSTATUS(numeric_attribute.setDefault(kSilhouetteColorDefault[0],
                                                   kSilhouetteColorDefault[1],
                                                   kSilhouetteColorDefault[2]));
        CHECK_MSTATUS(addAttribute(a_color));
    }

    // Silhouette Alpha
    {
        auto alpha_min = 0.0;
        auto alpha_max = 1.0;
        a_alpha = numeric_attribute.create(kAttrNameSilhouetteAlpha, "alp",
                                           MFnNumericData::kDouble,
                                           kSilhouetteAlphaDefault);
        CHECK_MSTATUS(numeric_attribute.setStorable(true));
        CHECK_MSTATUS(numeric_attribute.setConnectable(true));
        CHECK_MSTATUS(numeric_attribute.setKeyable(true));
        CHECK_MSTATUS(numeric_attribute.setMin(alpha_min));
        CHECK_MSTATUS(numeric_attribute.setMax(alpha_max));
        CHECK_MSTATUS(addAttribute(a_alpha));
    }

    // Silhouette Cull Face
    {
        // Maya uses 'short' for storing all enums.
        const auto front_value = static_cast<short>(CullFace::kFront);
        const auto back_value = static_cast<short>(CullFace::kBack);
        const auto front_and_back_value =
            static_cast<short>(CullFace::kFrontAndBack);
        a_cullFace =
            enum_attribute.create("cullFace", "cllfc", back_value, &status);
        CHECK_MSTATUS(status);
        CHECK_MSTATUS(enum_attribute.addField("Front", front_value));
        CHECK_MSTATUS(enum_attribute.addField("Back", back_value));
        CHECK_MSTATUS(
            enum_attribute.addField("FrontAndBack", front_and_back_value));
        CHECK_MSTATUS(enum_attribute.setStorable(true));
        CHECK_MSTATUS(enum_attribute.setKeyable(true));
        CHECK_MSTATUS(addAttribute(a_cullFace));
    }

    // Silhouette Operation Number
    //
    // This value determines which rendering operations will be
    // enabled. The lower the value, the fewer operations are enabled,
    // and the operations increase linearly.
    {
        auto num_min = 0;
        auto num_max = UINT8_MAX;
        a_operationNum = numeric_attribute.create(
            kAttrNameSilhouetteOperationNum, "opNm", MFnNumericData::kInt,
            kSilhouetteOperationNumDefault);
        CHECK_MSTATUS(numeric_attribute.setStorable(true));
        CHECK_MSTATUS(numeric_attribute.setConnectable(true));
        CHECK_MSTATUS(numeric_attribute.setKeyable(true));
        CHECK_MSTATUS(numeric_attribute.setMin(num_min));
        CHECK_MSTATUS(numeric_attribute.setMax(num_max));
        CHECK_MSTATUS(addAttribute(a_operationNum));
    }

    return MS::kSuccess;
}

}  // namespace render
}  // namespace mmsolver
