/*
 * Copyright (C) 2023 David Cattermole.
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
 */

#ifndef MM_SOLVER_RENDER_PASSES_DISPLAY_LAYER_H
#define MM_SOLVER_RENDER_PASSES_DISPLAY_LAYER_H

// STL
#include <vector>

// Maya
#include <maya/MBoundingBox.h>
#include <maya/MColor.h>
#include <maya/MDagMessage.h>
#include <maya/MObjectHandle.h>
#include <maya/MRenderTargetManager.h>
#include <maya/MString.h>
#include <maya/MUiMessage.h>
#include <maya/MViewport2Renderer.h>

// MM Solver
#include "mmSolver/render/RenderGlobalsNode.h"
#include "mmSolver/render/data/DisplayStyle.h"
#include "mmSolver/render/data/EdgeDetectMode.h"
#include "mmSolver/render/data/RenderColorFormat.h"
#include "mmSolver/render/data/constants.h"

namespace mmsolver {
namespace render {

// Display Layer passes
//
// Enumerations to identify an operation within a list of
// operations, used for each layer of the render override.
enum DisplayLayerPasses {
    kCopyOp = 0,

    // Draw the scene (except image planes), but only write to the
    // depth channel.
    kSceneDepthPass,

    kEdgeDetectOp,

    // Hidden Line - Draw the scene as wireframe, but it will be cut
    // out from the depth pass.
    kSceneRenderPass,

    // Merges all render layers together.
    kLayerMergeOp,

    // Holds the total number of entries (must be last field).
    kLayerPassesCount
};

class DisplayLayer {
public:
    DisplayLayer();
    ~DisplayLayer();

    MStatus updateRenderOperations();
    MStatus updateRenderTargets(MHWRender::MRenderTarget** targets);
    MStatus setPanelNames(const MString& name);
    MRenderOperation* getOperation(size_t& current_op);

    // The Display Layer name.
    MString name() const { return m_name; }
    void setName(const MString& value) { m_name = value; }

    bool visibility() const { return m_visibility; }
    void setVisibility(const bool value) { m_visibility = value; }

    int32_t displayOrder() const { return m_display_order; }
    void setDisplayOrder(const int32_t value) { m_display_order = value; }

    // How to composite the layer?
    LayerMode layerMode() const { return m_layer_mode; }
    void setLayerMode(const LayerMode value) { m_layer_mode = value; }

    // How the layer blends into the layer stack.
    float layerMix() const { return m_layer_mix; }
    void setLayerMix(const float value) { m_layer_mix = value; }

    bool layerDrawDebug() const { return m_layer_draw_debug; }
    void setLayerDrawDebug(const bool value) { m_layer_draw_debug = value; }

    // How does the Display Layer render?
    DisplayStyle objectDisplayStyle() const { return m_object_display_style; }
    void setObjectDisplayStyle(const DisplayStyle value) {
        m_object_display_style = value;
    }

    bool objectDisplayTextures() const { return m_object_display_textures; }
    void setObjectDisplayTextures(const bool value) {
        m_object_display_textures = value;
    }

    float objectAlpha() const { return m_object_alpha; }
    void setObjectAlpha(const float value) { m_object_alpha = value; }

    bool edgeEnable() const { return m_edge_enable; }
    void setEdgeEnable(const bool value) { m_edge_enable = value; }

    // What edge detection algorithm to use?
    EdgeDetectMode edgeDetectMode() const { return m_edge_detect_mode; }
    void setEdgeDetectMode(const EdgeDetectMode value) {
        m_edge_detect_mode = value;
    }

    MColor edgeColor() const { return m_edge_color; }
    void setEdgeColor(const MColor& value) { m_edge_color = value; }

    float edgeAlpha() const { return m_edge_alpha; }
    void setEdgeAlpha(const float value) { m_edge_alpha = value; }

    float edgeThickness() const { return m_edge_thickness; }
    void setEdgeThickness(const float value) { m_edge_thickness = value; }

    // What is the threshold for when an edge is detected?
    float edgeThresholdColor() const { return m_edge_threshold_color; }
    void setEdgeThresholdColor(const float value) {
        m_edge_threshold_color = value;
    }

    float edgeThresholdAlpha() const { return m_edge_threshold_alpha; }
    void setEdgeThresholdAlpha(const float value) {
        m_edge_threshold_alpha = value;
    }

    float edgeThresholdDepth() const { return m_edge_threshold_depth; }
    void setEdgeThresholdDepth(const float value) {
        m_edge_threshold_depth = value;
    }

private:
    // Operations for each layer. The same operations are used for all
    // layers, but each operation may be disabled/enabled to provide
    // different features.
    MHWRender::MRenderOperation* m_ops[DisplayLayerPasses::kLayerPassesCount];

    // Layer properties
    MString m_name;
    bool m_visibility;
    int32_t m_display_order;
    LayerMode m_layer_mode;
    float m_layer_mix;
    bool m_layer_draw_debug;

    // Object Pass appearance
    DisplayStyle m_object_display_style;
    bool m_object_display_textures;
    float m_object_alpha;

    // Edge Pass appearance
    bool m_edge_enable;
    EdgeDetectMode m_edge_detect_mode;
    MColor m_edge_color;
    float m_edge_alpha;
    float m_edge_thickness;
    float m_edge_threshold_color;
    float m_edge_threshold_alpha;
    float m_edge_threshold_depth;
};

// Used to compare two DisplayLists and return the smallest. This can
// be used with 'std::sort' to re-order std::vector<DisplayList>.
static bool compareDisplayLayer(const DisplayLayer& lhs,
                                const DisplayLayer& rhs) {
    return lhs.displayOrder() < rhs.displayOrder();
}

}  // namespace render
}  // namespace mmsolver

#endif  // MAYA_MM_SOLVER_RENDER_PASSES_DISPLAY_LAYER_H
