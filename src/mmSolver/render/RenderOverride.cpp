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
 * mmSolver viewport 2.0 renderer override.
 *
 */

#include "RenderOverride.h"

// Maya
#include <maya/MFnDependencyNode.h>
#include <maya/MGlobal.h>
#include <maya/MItDependencyNodes.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MPlugArray.h>
#include <maya/MShaderManager.h>
#include <maya/MStreamUtils.h>
#include <maya/MString.h>
#include <maya/MUiMessage.h>
#include <maya/MViewport2Renderer.h>

// MM Solver
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/nodeTypeIds.h"
#include "mmSolver/render/ops/HudRender.h"
#include "mmSolver/render/ops/SceneRender.h"
#include "mmSolver/render/passes/DisplayLayer.h"
#include "mmSolver/utilities/debug_utils.h"

namespace mmsolver {
namespace render {

static MStatus create_render_globals_node() {
    const MString command =
        "createNode \"" + MString(MM_RENDER_GLOBALS_TYPE_NAME) + "\" -name \"" +
        MString(kRenderGlobalsNodeName) + "\" -shared -skipSelect;";
    return MGlobal::executeCommand(command,
                                   /*displayEnabled*/ true,
                                   /*undoEnabled*/ true);
}

static MStatus add_custom_attributes_to_all_layers() {
    const MString command =
        "import mmSolver.tools.mmrendererlayers.tool as tool;"
        "tool.setup_all_layers();";
    return MGlobal::executePythonCommand(command,
                                         /*displayEnabled*/ true,
                                         /*undoEnabled*/ true);
}

// Set up operations
RenderOverride::RenderOverride(const MString &name)
    : MRenderOverride(name)
    , m_ui_name(kRendererUiName)
    , m_renderer_change_callback(0)
    , m_render_override_change_callback(0)
    , m_globals_node()
    , m_pull_updates(true)
    , m_multi_sample_enable(false)
    , m_multi_sample_count(1)
    , m_viewport_display_style(0)
    , m_viewport_draw_textures(false) {
    // Remove any operations that already exist from Maya.
    mOperations.clear();

    // Initialise the operations for this override.
    m_current_pass = Pass::kUninitialized;
    m_panel_name.clear();

    // Init target information for the override.
    MHWRender::MRasterFormat color_format = MHWRender::kR8G8B8A8_UNORM;
    MHWRender::MRasterFormat depth_format = MHWRender::kD32_FLOAT;

    // Initialise the targets.
    for (auto i = 0; i < kTargetCount; ++i) {
        m_targets[i] = nullptr;
    }

    // Default values, width, height and samples will be over-written
    // by parameters, as needed.
    const auto sample_count = 1;  // 1 == no multi-sampling.
    const auto default_width = 256;
    const auto default_height = 256;
    const auto array_slice_count = 0;
    const auto is_cube_map = false;

    // 1st Color target
    m_target_override_names[kMainColorTarget] = MString(kMainColorTargetName);
    m_target_descs[kMainColorTarget] = new MHWRender::MRenderTargetDescription(
        m_target_override_names[kMainColorTarget], default_width,
        default_height, sample_count, color_format, array_slice_count,
        is_cube_map);

    // 1st Depth target
    m_target_override_names[kMainDepthTarget] = MString(kMainDepthTargetName);
    m_target_descs[kMainDepthTarget] = new MHWRender::MRenderTargetDescription(
        m_target_override_names[kMainDepthTarget], default_width,
        default_height, sample_count, depth_format, array_slice_count,
        is_cube_map);

    // 2nd Color target
    m_target_override_names[kLayerColorTarget] = MString(kLayerColorTargetName);
    m_target_descs[kLayerColorTarget] = new MHWRender::MRenderTargetDescription(
        m_target_override_names[kLayerColorTarget], default_width,
        default_height, sample_count, color_format, array_slice_count,
        is_cube_map);

    // 2nd Depth target
    m_target_override_names[kLayerDepthTarget] = MString(kLayerDepthTargetName);
    m_target_descs[kLayerDepthTarget] = new MHWRender::MRenderTargetDescription(
        m_target_override_names[kLayerDepthTarget], default_width,
        default_height, sample_count, depth_format, array_slice_count,
        is_cube_map);

    // 3rd Color target
    m_target_override_names[kTempColorTarget] = MString(kTempColorTargetName);
    m_target_descs[kTempColorTarget] = new MHWRender::MRenderTargetDescription(
        m_target_override_names[kTempColorTarget], default_width,
        default_height, sample_count, color_format, array_slice_count,
        is_cube_map);

    // 3rd Depth target
    m_target_override_names[kTempDepthTarget] = MString(kTempDepthTargetName);
    m_target_descs[kTempDepthTarget] = new MHWRender::MRenderTargetDescription(
        m_target_override_names[kTempDepthTarget], default_width,
        default_height, sample_count, depth_format, array_slice_count,
        is_cube_map);
}

RenderOverride::~RenderOverride() {
    MHWRender::MRenderer *theRenderer = MHWRender::MRenderer::theRenderer();
    if (!theRenderer) {
        return;
    }

    // Release targets
    const MHWRender::MRenderTargetManager *targetManager =
        theRenderer->getRenderTargetManager();
    for (auto i = 0; i < kTargetCount; ++i) {
        if (m_target_descs[i]) {
            delete m_target_descs[i];
            m_target_descs[i] = nullptr;
        }

        if (m_targets[i]) {
            if (targetManager) {
                targetManager->releaseRenderTarget(m_targets[i]);
            }
            m_targets[i] = nullptr;
        }
    }

    RenderOverride::cleanup();

    // Clean up callbacks
    if (m_renderer_change_callback) {
        MMessage::removeCallback(m_renderer_change_callback);
    }
    if (m_render_override_change_callback) {
        MMessage::removeCallback(m_render_override_change_callback);
    }
}

// What type of Draw APIs are supported? For now, only "OpenGL Core
// Profile".
MHWRender::DrawAPI RenderOverride::supportedDrawAPIs() const {
    return MHWRender::kOpenGLCoreProfile;
}

bool RenderOverride::startOperationIterator() {
    m_current_pass = Pass::kBegin;
    m_begin_passes.startOperationIterator();
    m_display_layers.startOperationIterator();
    m_end_passes.startOperationIterator();
    return true;
}

MHWRender::MRenderOperation *RenderOverride::renderOperation() {
    if (m_current_pass == Pass::kBegin) {
        auto op = m_begin_passes.renderOperation();
        if (op != nullptr) {
            return op;
        } else {
            m_current_pass = Pass::kLayers;
        }
    }

    if (m_current_pass == Pass::kLayers) {
        auto op = m_display_layers.renderOperation();
        if (op != nullptr) {
            return op;
        } else {
            m_current_pass = Pass::kEnd;
        }
    }

    if (m_current_pass == Pass::kEnd) {
        auto op = m_end_passes.renderOperation();
        if (op != nullptr) {
            return op;
        } else {
            m_current_pass = Pass::kUninitialized;
        }
    }

    return nullptr;
}

bool RenderOverride::nextRenderOperation() {
    if (m_current_pass == Pass::kUninitialized) {
        return false;
    }

    if (m_current_pass == Pass::kBegin) {
        bool ok = m_begin_passes.nextRenderOperation();
        if (ok) {
            return true;
        } else {
            m_current_pass = Pass::kLayers;
        }
    }

    if (m_current_pass == Pass::kLayers) {
        bool ok = m_display_layers.nextRenderOperation();
        if (ok) {
            return true;
        } else {
            m_current_pass = Pass::kEnd;
        }
    }

    if (m_current_pass == Pass::kEnd) {
        bool ok = m_end_passes.nextRenderOperation();
        return ok;
    }

    return false;
}

// Read node plug attributes and set the values.
MStatus RenderOverride::updateParameters() {
    const bool verbose = false;
    MMSOLVER_VRB("RenderOverride::updateParameters: ");

    MStatus status = MS::kSuccess;
    if (!m_pull_updates) {
        return status;
    }

    status = MS::kFailure;
    if (!m_maya_hardware_globals_node.isValid()) {
        // Get the node and cache the handle in an 'MObjectHandle'
        // instance.
        MObject node_obj;
        status = getAsObject(kHardwareRenderGlobalsNodeName, node_obj,
                             /*quiet=*/false);

        if (!node_obj.isNull()) {
            m_maya_hardware_globals_node = node_obj;
        } else {
            // Could not find a valid 'hardwareRenderingGlobals' node,
            // which should always succeed because that node always
            // exists in the Maya scene.
            return status;
        }
    }

    MObject maya_hardware_globals_node_obj =
        m_maya_hardware_globals_node.object();
    MFnDependencyNode maya_hardware_globals_depends_node(
        maya_hardware_globals_node_obj, &status);
    CHECK_MSTATUS(status);

    const bool want_networked_plug = true;

    m_multi_sample_enable = false;
    MPlug sample_enable_plug = maya_hardware_globals_depends_node.findPlug(
        "multiSampleEnable", want_networked_plug, &status);
    CHECK_MSTATUS(status);
    if (status == MStatus::kSuccess) {
        m_multi_sample_enable = sample_enable_plug.asInt();
    }

    m_multi_sample_count = 1;
    if (m_multi_sample_enable) {
        MPlug sample_count_plug = maya_hardware_globals_depends_node.findPlug(
            "multiSampleCount", want_networked_plug, &status);
        CHECK_MSTATUS(status);
        if (status == MStatus::kSuccess) {
            m_multi_sample_count = sample_count_plug.asInt();
        }
    }

    if (!m_globals_node.isValid()) {
        // Get the node and cache the handle in an 'MObjectHandle'
        // instance.
        MObject node_obj;
        status = getAsObject(kRenderGlobalsNodeName, node_obj, /*quiet=*/true);

        if (!node_obj.isNull()) {
            m_globals_node = node_obj;
        } else {
            MMSOLVER_VRB(
                "MM Renderer: "
                "Could not find \"mmRenderGlobals\" node, creating node.");
            status = create_render_globals_node();
            CHECK_MSTATUS(status);

            if (status == MS::kSuccess) {
                status = getAsObject(kRenderGlobalsNodeName, node_obj,
                                     /*quiet=*/true);
                if (!node_obj.isNull()) {
                    m_globals_node = node_obj;
                    add_custom_attributes_to_all_layers();
                } else {
                    return MS::kSuccess;
                }
            } else {
                return MS::kSuccess;
            }
        }
    }
    if (status != MS::kSuccess) {
        return MS::kSuccess;
    }

    MObject globals_node_obj = m_globals_node.object();
    MFnDependencyNode depends_node(globals_node_obj, &status);
    CHECK_MSTATUS(status);

    m_render_color_format = kRenderColorFormatDefault;
    MPlug render_color_format_plug = depends_node.findPlug(
        "renderColorFormat", want_networked_plug, &status);
    CHECK_MSTATUS(status);
    if (status == MStatus::kSuccess) {
        short value = render_color_format_plug.asShort();
        m_render_color_format = static_cast<RenderColorFormat>(value);
    }
    MMSOLVER_VRB("RenderOverride render_color_format: "
                 << static_cast<short>(m_render_color_format));

    return MS::kSuccess;
}

// Get parameters on each layer and set up the values for the
// DisplayLayerList object.
MStatus RenderOverride::getDisplayLayerFromNode(
    MFnDependencyNode &depends_node, MFnDependencyNode &object_set_node,
    unsigned int viewport_display_style, DisplayLayer &out_display_layer) {
    MStatus status = MS::kSuccess;

    const bool verbose = false;
    MMSOLVER_VRB("RenderOverride::getDisplayLayerFromNode: ");

    MString layer_name = depends_node.name();
    MMSOLVER_VRB("RenderOverride DisplayLayer: \"" << layer_name.asChar()
                                                   << '"');
    const bool want_networked_plug = true;

    // Visibility - should the layer draw?
    bool layer_visibility = kLayerVisibilityDefault;
    MPlug visibility_plug = depends_node.findPlug(kAttrNameLayerVisibility,
                                                  want_networked_plug, &status);
    if (status == MStatus::kSuccess) {
        layer_visibility = visibility_plug.asBool();
    }
    MMSOLVER_VRB("RenderOverride Visibility: " << layer_visibility);

    // Display Order - what is the order of the display layer?
    int32_t layer_display_order = kLayerDisplayOrderDefault;
    MPlug display_order_plug = depends_node.findPlug(
        kAttrNameLayerDisplayOrder, want_networked_plug, &status);
    if (status == MStatus::kSuccess) {
        layer_display_order = display_order_plug.asInt();
    }
    MMSOLVER_VRB("RenderOverride Display Order: " << layer_display_order);

    // Layer Mode
    // - Z-Depth (default)
    // - Over
    // - Add / Plus
    LayerMode layer_mode = kLayerModeDefault;
    MPlug layer_mode_plug = object_set_node.findPlug(
        kAttrNameLayerMode, want_networked_plug, &status);
    if (status == MStatus::kSuccess) {
        short value = layer_mode_plug.asShort();
        layer_mode = static_cast<LayerMode>(value);
    }
    MMSOLVER_VRB(
        "RenderOverride Layer Mode: " << static_cast<short>(layer_mode));

    // Layer Mix (float)
    // - Controls the transparency of the layer over other layers.
    float layer_mix = kLayerMixDefault;
    MPlug layer_mix_plug = object_set_node.findPlug(
        kAttrNameLayerMix, want_networked_plug, &status);
    if (status == MStatus::kSuccess) {
        layer_mix = layer_mix_plug.asFloat();
    }
    MMSOLVER_VRB("RenderOverride Layer Mix: " << layer_mix);

    // Draw_Debug the layer detection mode.
    bool layer_draw_debug = kLayerDrawDebugDefault;
    MPlug layer_draw_debug_plug = object_set_node.findPlug(
        kAttrNameLayerDrawDebug, want_networked_plug, &status);
    if (status == MStatus::kSuccess) {
        layer_draw_debug = layer_draw_debug_plug.asBool();
    }
    MMSOLVER_VRB("RenderOverride Layer Draw Debug: " << layer_draw_debug);

    // Display Style
    // - No Override.
    // - Hold Out (invisible, but draws in depth).
    // - Wireframe.
    // - Hidden Line.
    // - Shaded.
    // - Wireframe On Shaded.
    DisplayStyle object_display_style = kObjectDisplayStyleDefault;
    MPlug display_style_plug = object_set_node.findPlug(
        kAttrNameObjectDisplayStyle, want_networked_plug, &status);
    if (status == MStatus::kSuccess) {
        short value = display_style_plug.asShort();
        object_display_style = static_cast<DisplayStyle>(value);
    }
    if (object_display_style == DisplayStyle::kNoDisplayStyleOverride) {
        bool use_shaded =
            viewport_display_style &
            static_cast<unsigned int>(MHWRender::MFrameContext::kGouraudShaded);
        bool use_flat_shaded =
            viewport_display_style &
            static_cast<unsigned int>(MHWRender::MFrameContext::kFlatShaded);
        bool use_wireframe =
            viewport_display_style &
            static_cast<unsigned int>(MHWRender::MFrameContext::kWireFrame);

        if (use_flat_shaded) {
            use_shaded = true;
        }

        if (use_shaded && use_wireframe) {
            object_display_style = DisplayStyle::kWireframeOnShaded;
        } else if (use_shaded) {
            object_display_style = DisplayStyle::kShaded;
        } else if (use_wireframe) {
            object_display_style = DisplayStyle::kWireframe;
        } else {
            object_display_style = DisplayStyle::kHoldOut;
        }
    }
    MMSOLVER_VRB("RenderOverride Display Style: "
                 << static_cast<short>(object_display_style));

    float object_alpha = kObjectAlphaDefault;
    MPlug object_alpha_plug = object_set_node.findPlug(
        kAttrNameObjectAlpha, want_networked_plug, &status);
    if (status == MStatus::kSuccess) {
        object_alpha = object_alpha_plug.asFloat();
    }
    MMSOLVER_VRB("RenderOverride Wireframe Alpha: " << object_alpha);

    // Enable the edge detection mode.
    bool edge_enable = kEdgeEnableDefault;
    MPlug edge_enable_plug = object_set_node.findPlug(
        kAttrNameEdgeEnable, want_networked_plug, &status);
    if (status == MStatus::kSuccess) {
        edge_enable = edge_enable_plug.asBool();
    }
    MMSOLVER_VRB("RenderOverride Edge Enable: " << edge_enable);

    // Edge Color. The color for detected edges.
    MColor edge_color(kEdgeColorDefault[0], kEdgeColorDefault[1],
                      kEdgeColorDefault[2]);
    MPlug edge_color_r_plug = object_set_node.findPlug(
        kAttrNameEdgeColorR, want_networked_plug, &status);
    if (status == MStatus::kSuccess) {
        edge_color.r = edge_color_r_plug.asFloat();
    }
    MPlug edge_color_g_plug = object_set_node.findPlug(
        kAttrNameEdgeColorG, want_networked_plug, &status);
    if (status == MStatus::kSuccess) {
        edge_color.g = edge_color_g_plug.asFloat();
    }
    MPlug edge_color_b_plug = object_set_node.findPlug(
        kAttrNameEdgeColorB, want_networked_plug, &status);
    if (status == MStatus::kSuccess) {
        edge_color.b = edge_color_b_plug.asFloat();
    }
    MMSOLVER_VRB("RenderOverride Edge Color: R=" << edge_color.r
                                                 << " G=" << edge_color.g
                                                 << " B=" << edge_color.b);

    // Edge Alpha - The alpha for detected edges.
    float edge_alpha = kEdgeAlphaDefault;
    MPlug edge_alpha_plug = object_set_node.findPlug(
        kAttrNameEdgeAlpha, want_networked_plug, &status);
    if (status == MStatus::kSuccess) {
        edge_alpha = edge_alpha_plug.asFloat();
    }
    MMSOLVER_VRB("RenderOverride Edge Alpha: " << edge_alpha);

    EdgeDetectMode edge_detect_mode = kEdgeDetectModeDefault;
    MPlug edge_detect_mode_plug = object_set_node.findPlug(
        kAttrNameEdgeDetectMode, want_networked_plug, &status);
    if (status == MStatus::kSuccess) {
        short value = edge_detect_mode_plug.asShort();
        edge_detect_mode = static_cast<EdgeDetectMode>(value);
    }
    MMSOLVER_VRB("RenderOverride Edge Detect Mode: "
                 << static_cast<short>(edge_detect_mode));

    float edge_thickness = kEdgeThicknessDefault;
    MPlug edge_thickness_plug = object_set_node.findPlug(
        kAttrNameEdgeThickness, want_networked_plug, &status);
    if (status == MStatus::kSuccess) {
        edge_thickness = edge_thickness_plug.asFloat();
    }
    MMSOLVER_VRB("RenderOverride Edge Thickness: " << edge_thickness);

    float edge_threshold = kEdgeThresholdDefault;
    MPlug edge_threshold_plug = object_set_node.findPlug(
        kAttrNameEdgeThreshold, want_networked_plug, &status);
    if (status == MStatus::kSuccess) {
        edge_threshold = edge_threshold_plug.asFloat();
    }
    MMSOLVER_VRB("RenderOverride Edge Threshold: " << edge_threshold);

    float edge_threshold_color = kEdgeThresholdColorDefault;
    MPlug edge_threshold_color_plug = object_set_node.findPlug(
        kAttrNameEdgeThresholdColor, want_networked_plug, &status);
    if (status == MStatus::kSuccess) {
        edge_threshold_color = edge_threshold_color_plug.asFloat();
    }
    MMSOLVER_VRB(
        "RenderOverride Edge Threshold Color: " << edge_threshold_color);

    float edge_threshold_alpha = kEdgeThresholdAlphaDefault;
    MPlug edge_threshold_alpha_plug = object_set_node.findPlug(
        kAttrNameEdgeThresholdAlpha, want_networked_plug, &status);
    if (status == MStatus::kSuccess) {
        edge_threshold_alpha = edge_threshold_alpha_plug.asFloat();
    }
    MMSOLVER_VRB(
        "RenderOverride Edge Threshold Alpha: " << edge_threshold_alpha);

    float edge_threshold_depth = kEdgeThresholdDepthDefault;
    MPlug edge_threshold_depth_plug = object_set_node.findPlug(
        kAttrNameEdgeThresholdDepth, want_networked_plug, &status);
    if (status == MStatus::kSuccess) {
        edge_threshold_depth = edge_threshold_depth_plug.asFloat();
    }
    MMSOLVER_VRB(
        "RenderOverride Edge Threshold Depth: " << edge_threshold_depth);

    edge_threshold_color *= edge_threshold;
    edge_threshold_alpha *= edge_threshold;
    edge_threshold_depth *= edge_threshold;

    MObject object_set_obj = object_set_node.object(&status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    out_display_layer.setName(layer_name);
    out_display_layer.setVisibility(layer_visibility);
    out_display_layer.setDisplayOrder(layer_display_order);
    out_display_layer.setLayerMode(layer_mode);
    out_display_layer.setLayerMix(layer_mix);
    out_display_layer.setLayerDrawDebug(layer_draw_debug);
    out_display_layer.setObjectSetNode(object_set_obj);
    out_display_layer.setObjectDisplayStyle(object_display_style);
    out_display_layer.setObjectAlpha(object_alpha);
    out_display_layer.setEdgeEnable(edge_enable);
    out_display_layer.setEdgeDetectMode(edge_detect_mode);
    out_display_layer.setEdgeColor(edge_color);
    out_display_layer.setEdgeAlpha(edge_alpha);
    out_display_layer.setEdgeThickness(edge_thickness);
    out_display_layer.setEdgeThresholdColor(edge_threshold_color);
    out_display_layer.setEdgeThresholdAlpha(edge_threshold_alpha);
    out_display_layer.setEdgeThresholdDepth(edge_threshold_depth);

    return MStatus::kSuccess;
}

// Read node plug attributes and set the values.
MStatus RenderOverride::updateDisplayLayers() {
    const bool verbose = false;
    MMSOLVER_VRB("RenderOverride::updateDisplayLayers: start");

    MStatus status = MS::kSuccess;
    if (!m_pull_updates) {
        return status;
    }

    // Get all the display layers in the current Maya scene.
    MFn::Type dg_filter = MFn::kDisplayLayer;
    MItDependencyNodes it(dg_filter, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    m_display_layers.clearDisplayLayers();
    m_display_layer_nodes.clear();
    for (it.reset(); !it.isDone(); it.next()) {
        MObject node_obj = it.thisNode();
        if (node_obj.isNull()) {
            continue;
        }
        if (!node_obj.hasFn(MFn::kDisplayLayer)) {
            continue;
        }
        if (node_obj.apiType() != MFn::kDisplayLayer) {
            continue;
        }
        MMSOLVER_VRB("RenderOverride::updateDisplayLayers: layer node type: "
                     << node_obj.apiTypeStr());

        MFnDependencyNode depends_node(node_obj, &status);
        CHECK_MSTATUS(status);
        if (status != MS::kSuccess) {
            MMSOLVER_WRN(
                "RenderOverride::updateDisplayLayers: Could not get "
                "MFnDependencyNode for layer, skipping it.");
            continue;
        }
        MMSOLVER_VRB("RenderOverride::updateDisplayLayers: layer node name: "
                     << depends_node.name());

        const bool want_networked_plug = true;

        // Get the 'ObjectSet' node Connected to the Display Layer.
        MPlug message_plug =
            depends_node.findPlug("message", want_networked_plug, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        const bool message_plug_is_source = message_plug.isSource(&status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        if (!message_plug_is_source) {
            MMSOLVER_VRB(
                "RenderOverride::updateDisplayLayers: "
                "\"message\" attribute is not a source: "
                << depends_node.name().asChar());
        }

        const bool message_plug_is_connected =
            message_plug.isConnected(&status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        if (!message_plug_is_connected) {
            MMSOLVER_VRB(
                "RenderOverride::updateDisplayLayers: "
                "\"message\" attribute is not connected: "
                << depends_node.name().asChar());
        }

        MObject object_set_obj;
        MPlugArray connected_plugs;
        message_plug.destinations(connected_plugs, &status);
        CHECK_MSTATUS(status);
        MMSOLVER_VRB(
            "RenderOverride::updateDisplayLayers: "
            "Number of \"message\" attribute destination connections: "
            << connected_plugs.length());
        if (status != MS::kSuccess) {
            MMSOLVER_WRN(
                "RenderOverride::updateDisplayLayers: "
                "No valid destination connections from \"message\" attribute: "
                << depends_node.name().asChar());
            continue;
        }
        if (connected_plugs.length() == 0) {
            MMSOLVER_WRN(
                "RenderOverride::updateDisplayLayers: "
                "No connections from \"message\" attribute: "
                << depends_node.name().asChar());
            continue;
        }

        for (int32_t i = 0; i < connected_plugs.length(); i++) {
            MPlug connected_plug = connected_plugs[i];
            MObject connected_node = connected_plug.node(&status);
            CHECK_MSTATUS(status);

            // TODO: Use 'MFn::kPluginObjectSet' if we switch to a custom object
            // set type.
            if (connected_node.hasFn(MFn::kSet)) {
                object_set_obj = connected_node;
                break;
            }
        }
        if (object_set_obj.isNull()) {
            MMSOLVER_WRN(
                "RenderOverride::updateDisplayLayers: "
                "Object set node is null: "
                << depends_node.name().asChar());
            continue;
        }
        MFnDependencyNode object_set_node(object_set_obj, &status);
        CHECK_MSTATUS(status);
        if (status != MS::kSuccess) {
            MMSOLVER_WRN(
                "RenderOverride::updateDisplayLayers: "
                "Could not use MFnDependencyNode with object set node. "
                "displayLayer: "
                << depends_node.name().asChar());
        }
        MMSOLVER_VRB(
            "RenderOverride::updateDisplayLayers: "
            "ObjectSet node name: "
            << object_set_node.name().asChar());

        MObjectHandle node_handle(node_obj);
        m_display_layer_nodes.push_back(node_handle);

        DisplayLayer display_layer;
        status = RenderOverride::getDisplayLayerFromNode(
            depends_node, object_set_node, m_viewport_display_style,
            display_layer);
        CHECK_MSTATUS(status);
        if (status == MS::kSuccess) {
            display_layer.setObjectDisplayTextures(m_viewport_draw_textures);
            m_display_layers.pushDisplayLayer(std::move(display_layer));
        }
    }

    // Sort display layers based on "display order" attribute on the
    // node. This is an integer that represents the order of the
    // DisplayLayers in the "Display Layer Editor" in Maya UI.
    m_display_layers.sortDisplayLayers();

    m_display_layers.updateNodes();

    MMSOLVER_VRB("RenderOverride::updateDisplayLayers: end");
    return MS::kSuccess;
}

MStatus RenderOverride::updateRenderOperations() {
    const bool verbose = false;
    MMSOLVER_VRB("RenderOverride::updateRenderOperations: ");

    MStatus status = MS::kSuccess;
    status = m_begin_passes.updateRenderOperations();
    CHECK_MSTATUS_AND_RETURN_IT(status);

    status = m_end_passes.updateRenderOperations();
    CHECK_MSTATUS_AND_RETURN_IT(status);

    status = m_display_layers.updateRenderOperations();
    CHECK_MSTATUS_AND_RETURN_IT(status);

    return MS::kSuccess;
}

// Update the render targets that are required for the entire
// override.  References to these targets are set on the individual
// operations as required so that they will send their output to the
// appropriate location.
MStatus RenderOverride::updateRenderTargets() {
    MStatus status = MS::kSuccess;

    const bool verbose = false;
    MMSOLVER_VRB("RenderOverride::updateRenderTargets");

    MHWRender::MRenderer *theRenderer = MHWRender::MRenderer::theRenderer();
    if (!theRenderer) {
        return MS::kFailure;
    }

    // Get the current output target size as specified by the
    // renderer. If it has changed then the targets need to be resized
    // to match.
    uint32_t target_width = 0;
    uint32_t target_height = 0;
    theRenderer->outputTargetSize(target_width, target_height);
    for (auto target_id = 0; target_id < kTargetCount; ++target_id) {
        // Update size value for all target descriptions kept
        m_target_descs[target_id]->setWidth(target_width);
        m_target_descs[target_id]->setHeight(target_height);
        m_target_descs[target_id]->setMultiSampleCount(m_multi_sample_count);
    }

    // Set the bit-depth for color buffers.
    MHWRender::MRasterFormat color_format = MHWRender::kR8G8B8A8_UNORM;
    if (m_render_color_format == RenderColorFormat::kRGBA8BitInt) {
        color_format = MHWRender::kR8G8B8A8_UNORM;
    } else if (m_render_color_format == RenderColorFormat::kRGBA16BitFloat) {
        color_format = MHWRender::kR16G16B16A16_FLOAT;
    } else if (m_render_color_format == RenderColorFormat::kRGBA32BitFloat) {
        color_format = MHWRender::kR32G32B32A32_FLOAT;
    } else {
        MMSOLVER_ERR("Invalid RenderColorFormat given: "
                     << static_cast<short>(m_render_color_format));
    }
    m_target_descs[kMainColorTarget]->setRasterFormat(color_format);
    m_target_descs[kLayerColorTarget]->setRasterFormat(color_format);
    m_target_descs[kTempColorTarget]->setRasterFormat(color_format);

    // Either acquire a new target if it didn't exist before, resize
    // the current target.
    const MHWRender::MRenderTargetManager *targetManager =
        theRenderer->getRenderTargetManager();
    if (!targetManager) {
        return MS::kFailure;
    }
    for (auto target_id = 0; target_id < kTargetCount; ++target_id) {
        // Create a new target.
        if (!m_targets[target_id]) {
            m_targets[target_id] = targetManager->acquireRenderTarget(
                *(m_target_descs[target_id]));
        } else {
            // "Update" using a description will resize as necessary.
            m_targets[target_id]->updateDescription(
                *(m_target_descs[target_id]));
        }
    }

    // Update the render targets on the individual operations.
    m_begin_passes.updateRenderTargets(m_targets);
    m_end_passes.updateRenderTargets(m_targets);
    m_display_layers.updateRenderTargets(m_targets);

    status = MS::kFailure;
    if (m_targets[kMainColorTarget] && m_targets[kMainDepthTarget] &&
        m_targets[kLayerColorTarget] && m_targets[kLayerDepthTarget] &&
        m_targets[kTempColorTarget] && m_targets[kTempDepthTarget]) {
        status = MS::kSuccess;
    }
    return status;
}

MStatus RenderOverride::setPanelNames(const MString &name) {
    MStatus status = MS::kSuccess;

    const bool verbose = false;
    MMSOLVER_VRB("RenderOverride::setPanelNames: " << name.asChar());

    status = m_begin_passes.setPanelNames(name);
    CHECK_MSTATUS(status);

    status = m_end_passes.setPanelNames(name);
    CHECK_MSTATUS(status);

    status = m_display_layers.setPanelNames(name);
    CHECK_MSTATUS(status);

    return MS::kSuccess;
}

// Perform any setup required before render operations are to be executed.
MStatus RenderOverride::setup(const MString &destination) {
    const bool verbose = false;
    MMSOLVER_VRB("RenderOverride::setup: start " << destination.asChar());

    MStatus status = MS::kSuccess;

    // Track changes to the renderer and override for this viewport (nothing
    // will be printed unless mDebugOverride is true)
    if (!m_renderer_change_callback) {
        void *client_data = nullptr;
        m_renderer_change_callback =
            MUiMessage::add3dViewRendererChangedCallback(
                destination, renderer_change_func, client_data);
    }
    if (!m_render_override_change_callback) {
        void *client_data = nullptr;
        m_render_override_change_callback =
            MUiMessage::add3dViewRenderOverrideChangedCallback(
                destination, render_override_change_func, client_data);
    }

    const MHWRender::MFrameContext *frameContext =
        MRenderOverride::getFrameContext();
    if (frameContext) {
        unsigned int display_style = frameContext->getDisplayStyle();
        m_viewport_draw_textures =
            display_style &
            static_cast<unsigned int>(MHWRender::MFrameContext::kTextured);
        m_viewport_display_style = static_cast<unsigned int>(display_style);
    }

    // Get override values.
    status = RenderOverride::updateParameters();
    CHECK_MSTATUS(status);
    status = RenderOverride::updateDisplayLayers();
    CHECK_MSTATUS(status);

    // Construct the render operations.
    status = RenderOverride::updateRenderOperations();
    CHECK_MSTATUS(status);

    // Update any of the render targets which will be required
    status = RenderOverride::updateRenderTargets();
    CHECK_MSTATUS(status);

    // The panel name, used to get the current 3d view (M3dView).
    m_panel_name.set(destination.asChar());
    status = RenderOverride::setPanelNames(m_panel_name);
    CHECK_MSTATUS(status);

    m_current_pass = Pass::kUninitialized;

    MMSOLVER_VRB("RenderOverride::setup: end " << destination.asChar());
    return status;
}

// Perform any cleanup required following the execution of render operations.
//
// End of frame cleanup. Clears out any data on operations which may
// change from frame to frame (render target, output panel name etc).
MStatus RenderOverride::cleanup() {
    const bool verbose = false;
    MMSOLVER_VRB("RenderOverride::cleanup: ");

    // Reset the active view
    m_panel_name.clear();

    // Reset current operation
    m_current_pass = Pass::kUninitialized;

    return MStatus::kSuccess;
}

// Callback for tracking renderer changes
void RenderOverride::renderer_change_func(const MString &panel_name,
                                          const MString &old_renderer,
                                          const MString &new_renderer,
                                          void * /*client_data*/) {
    const bool verbose = false;
    MMSOLVER_VRB("Renderer changed for panel '"
                 << panel_name.asChar() << "'. "
                 << "New renderer is '" << new_renderer.asChar() << "', "
                 << "old was '" << old_renderer.asChar() << "'.");

    if (new_renderer == MM_RENDERER_NAME) {
        MStatus status = create_render_globals_node();
        CHECK_MSTATUS(status);
        status = add_custom_attributes_to_all_layers();
        CHECK_MSTATUS(status);
    }
}

// Callback for tracking render override changes
void RenderOverride::render_override_change_func(const MString &panel_name,
                                                 const MString &old_renderer,
                                                 const MString &new_renderer,
                                                 void * /*client_data*/) {
    const bool verbose = false;
    MMSOLVER_VRB("Render override changed for panel '"
                 << panel_name.asChar() << "'. "
                 << "New override is '" << new_renderer.asChar() << "', "
                 << "old was '" << old_renderer.asChar() << "'.");

    if (new_renderer == MM_RENDERER_NAME) {
        MStatus status = create_render_globals_node();
        CHECK_MSTATUS(status);
        status = add_custom_attributes_to_all_layers();
        CHECK_MSTATUS(status);
    }
}

}  // namespace render
}  // namespace mmsolver
