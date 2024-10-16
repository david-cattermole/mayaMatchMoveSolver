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
 */

#ifndef MM_SKY_DOME_DRAW_OVERRIDE_H
#define MM_SKY_DOME_DRAW_OVERRIDE_H

// Maya
#include <maya/MColor.h>
#include <maya/MEventMessage.h>
#include <maya/MGlobal.h>
#include <maya/MPointArray.h>
#include <maya/MStreamUtils.h>
#include <maya/MString.h>

// Maya Viewport 2.0
#include <maya/MDrawContext.h>
#include <maya/MDrawRegistry.h>
#include <maya/MHWGeometryUtilities.h>
#include <maya/MPxDrawOverride.h>
#include <maya/MUserData.h>

// MM Solver
#include "SkyDomeShapeNode.h"
#include "mmSolver/utilities/debug_utils.h"

namespace mmsolver {

class SkyDomeDrawData : public MUserData {
public:
    SkyDomeDrawData()
#if MAYA_API_VERSION >= 20220000
        : MUserData()
#else
        // MUserData(bool) constructor is deprecated in Maya 2022+
        // because 'deleteAfterUse' is no longer needed.
        : MUserData(/*deleteAfterUse=*/true)  // let Maya clean up
#endif
        , m_enable(true)
        , m_draw_mode(static_cast<short>(DrawMode::kDrawOnTop))
        , m_transform_mode(static_cast<short>(TransformMode::kNoOffset))
        , m_line_width(1.0)
        , m_alpha(1.0)
        , m_radius(1.0)
        , m_resolution(32)
        , m_depth_priority(MHWRender::MRenderItem::sDormantFilledDepthPriority)
        , m_axis_x_enable(true)
        , m_axis_y_enable(true)
        , m_axis_z_enable(true)
        , m_axis_x_enable_top(true)
        , m_axis_z_enable_top(true)
        , m_axis_x_enable_bottom(true)
        , m_axis_z_enable_bottom(true)
        , m_axis_x_alpha(1.0f)
        , m_axis_y_alpha(1.0f)
        , m_axis_z_alpha(1.0f)
        , m_axis_x_line_width(2.0f)
        , m_axis_y_line_width(2.0f)
        , m_axis_z_line_width(2.0f)
        , m_grid_lat_enable(true)
        , m_grid_long_enable(true)
        , m_grid_lat_enable_top(true)
        , m_grid_long_enable_top(true)
        , m_grid_lat_enable_bottom(true)
        , m_grid_long_enable_bottom(true)
        , m_grid_lat_alpha(0.5f)
        , m_grid_long_alpha(0.5f)
        , m_grid_lat_line_width(1.0f)
        , m_grid_long_line_width(1.0f)
        , m_grid_lat_divisions(6)
        , m_grid_long_divisions(6) {
    }

    ~SkyDomeDrawData() override {}

    bool m_enable;
    double m_alpha;
    double m_line_width;
    short m_draw_mode;
    short m_transform_mode;
    double m_radius;
    uint32_t m_resolution;
    unsigned int m_depth_priority;

    bool m_axis_x_enable;
    bool m_axis_y_enable;
    bool m_axis_z_enable;
    bool m_axis_x_enable_top;
    bool m_axis_z_enable_top;
    bool m_axis_x_enable_bottom;
    bool m_axis_z_enable_bottom;
    MColor m_axis_x_color{1.0f, 0.0f, 0.0f, 1.0f};
    MColor m_axis_y_color{0.0f, 1.0f, 0.0f, 1.0f};
    MColor m_axis_z_color{0.0f, 0.0f, 1.0f, 1.0f};
    double m_axis_x_alpha;
    double m_axis_y_alpha;
    double m_axis_z_alpha;
    double m_axis_x_line_width;
    double m_axis_y_line_width;
    double m_axis_z_line_width;

    bool m_grid_lat_enable;
    bool m_grid_long_enable;
    bool m_grid_lat_enable_top;
    bool m_grid_long_enable_top;
    bool m_grid_lat_enable_bottom;
    bool m_grid_long_enable_bottom;
    uint32_t m_grid_lat_divisions;
    uint32_t m_grid_long_divisions;
    MColor m_grid_lat_color{1.0f, 0.0f, 1.0f, 0.1f};
    MColor m_grid_long_color{0.0f, 1.0f, 1.0f, 0.1f};
    double m_grid_lat_alpha;
    double m_grid_long_alpha;
    double m_grid_lat_line_width;
    double m_grid_long_line_width;
};

class SkyDomeDrawOverride : public MHWRender::MPxDrawOverride {
public:
    static MHWRender::MPxDrawOverride *Creator(const MObject &obj) {
        return new SkyDomeDrawOverride(obj);
    }

    ~SkyDomeDrawOverride() override;

    MHWRender::DrawAPI supportedDrawAPIs() const override;

    bool isBounded(const MDagPath &objPath,
                   const MDagPath &cameraPath) const override;

    MBoundingBox boundingBox(const MDagPath &objPath,
                             const MDagPath &cameraPath) const override;

    MUserData *prepareForDraw(const MDagPath &objPath,
                              const MDagPath &cameraPath,
                              const MHWRender::MFrameContext &frameContext,
                              MUserData *oldData) override;

    bool hasUIDrawables() const override { return true; }

    void addUIDrawables(const MDagPath &objPath,
                        MHWRender::MUIDrawManager &drawManager,
                        const MHWRender::MFrameContext &frameContext,
                        const MUserData *userData) override;

    bool traceCallSequence() const override {
        // Return true if internal tracing is desired.
        return false;
    }

    void handleTraceMessage(const MString &message) const override {
        MGlobal::displayInfo("SkyDomeDrawOverride: " + message);
        MMSOLVER_MAYA_INFO("SkyDomeDrawOverride: " << message.asChar());
    }

private:
    explicit SkyDomeDrawOverride(const MObject &obj);

    // The shape node we're attached to.
    SkyDomeShapeNode *m_node;

    // Get attribute values from node.
    MStatus get_node_attr(const MDagPath &objPath, const MObject &attr,
                          bool &value) const;
    MStatus get_node_attr(const MDagPath &objPath, const MObject &attr,
                          int32_t &value) const;
    MStatus get_node_attr(const MDagPath &objPath, const MObject &attr,
                          uint32_t &value) const;
    MStatus get_node_attr(const MDagPath &objPath, const MObject &attr,
                          short &value) const;
    MStatus get_node_attr(const MDagPath &objPath, const MObject &attr,
                          float &value) const;
    MStatus get_node_attr(const MDagPath &objPath, const MObject &attr,
                          double &value) const;
    MStatus get_node_attr(const MDagPath &objPath, const MObject &attr,
                          MDistance &value) const;
    MStatus get_node_attr(const MDagPath &objPath, const MObject &attr,
                          MColor &value) const;

    // Called when the model editor state changes.
    static void on_model_editor_changed_func(void *clientData);
    MCallbackId m_model_editor_changed_callback_id;
};

}  // namespace mmsolver

#endif  // MM_SKY_DOME_DRAW_OVERRIDE_H
