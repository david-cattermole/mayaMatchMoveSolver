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

#include "SkyDomeShapeNode.h"

#include <maya/MString.h>
#include <maya/MColor.h>
#include <maya/MGlobal.h>
#include <maya/MPointArray.h>
#include <maya/MStreamUtils.h>
#include <maya/MEventMessage.h>

// Viewport 2.0
#include <maya/MPxDrawOverride.h>
#include <maya/MDrawRegistry.h>
#include <maya/MUserData.h>
#include <maya/MDrawContext.h>
#include <maya/MHWGeometryUtilities.h>

namespace mmsolver {

class SkyDomeDrawData : public MUserData {
public:
    SkyDomeDrawData()
            : MUserData(/*deleteAfterUse=*/ true) // let Maya clean up
            , m_draw_mode(static_cast<short>(DrawMode::kDrawOnTop))
            , m_transform_mode(static_cast<short>(TransformMode::kNoOffset))
            , m_radius(1.0)
            , m_resolution(32)
            , m_latitude_enable(true)
            , m_longitude_enable(true)
            , m_latitude_line_width(1.0f)
            , m_longitude_line_width(1.0f)
            , m_latitude_divisions(6)
            , m_longitude_divisions(6)
            , m_x_axis_enable(true)
            , m_y_axis_enable(true)
            , m_z_axis_enable(true)
            , m_x_axis_line_width(2.0f)
            , m_y_axis_line_width(2.0f)
            , m_z_axis_line_width(2.0f)
    {}

    ~SkyDomeDrawData() override {
    }

    bool m_global_enable;
    float m_global_line_width;

    short m_draw_mode;
    short m_transform_mode;
    float m_radius;
    uint32_t m_resolution;

    bool m_latitude_enable;
    bool m_longitude_enable;
    float m_latitude_line_width;
    float m_longitude_line_width;
    uint32_t m_latitude_divisions;
    uint32_t m_longitude_divisions;
    MColor m_color_latitude{1.0f, 0.0f, 1.0f, 0.5f};
    MColor m_color_longitude{0.0f, 1.0f, 1.0f, 0.5f};

    bool m_top_axis_enable;
    bool m_bottom_axis_enable;
    bool m_x_axis_enable;
    bool m_y_axis_enable;
    bool m_z_axis_enable;
    float m_x_axis_line_width;
    float m_y_axis_line_width;
    float m_z_axis_line_width;
    MColor m_color_x{1.0f, 0.0f, 0.0f, 1.0f};
    MColor m_color_y{0.0f, 1.0f, 0.0f, 1.0f};
    MColor m_color_z{0.0f, 0.0f, 1.0f, 1.0f};

    unsigned int m_depth_priority;

};

class SkyDomeDrawOverride : public MHWRender::MPxDrawOverride {
public:
    static MHWRender::MPxDrawOverride *Creator(const MObject &obj) {
        return new SkyDomeDrawOverride(obj);
    }

    ~SkyDomeDrawOverride() override;

    MHWRender::DrawAPI supportedDrawAPIs() const override;

    bool isBounded(
            const MDagPath &objPath,
            const MDagPath &cameraPath) const override;

    MBoundingBox boundingBox(
            const MDagPath &objPath,
            const MDagPath &cameraPath) const override;

    MUserData *prepareForDraw(
            const MDagPath &objPath,
            const MDagPath &cameraPath,
            const MHWRender::MFrameContext &frameContext,
            MUserData *oldData) override;

    bool hasUIDrawables() const override { return true; }

    void addUIDrawables(
            const MDagPath &objPath,
            MHWRender::MUIDrawManager &drawManager,
            const MHWRender::MFrameContext &frameContext,
            const MUserData *userData) override;

    bool traceCallSequence() const override {
        // Return true if internal tracing is desired.
        return false;
    }

    void handleTraceMessage(const MString &message) const override {
        MGlobal::displayInfo("SkyDomeDrawOverride: " + message);
        MStreamUtils::stdOutStream()
                << "SkyDomeDrawOverride: " << message.asChar() << '\n';
    }

private:
    SkyDomeDrawOverride(const MObject &obj);

    // The shape node we're attached to.
    SkyDomeShapeNode *m_node;

    // Get attribute values from node.
    MStatus get_node_attr(
        const MDagPath &objPath,
        const MObject &attr,
        bool &value) const;
    MStatus get_node_attr(
        const MDagPath &objPath,
        const MObject &attr,
        int32_t &value) const;
    MStatus get_node_attr(
        const MDagPath &objPath,
        const MObject &attr,
        uint32_t &value) const;
    MStatus get_node_attr(
        const MDagPath &objPath,
        const MObject &attr,
        short &value) const;
    MStatus get_node_attr(
        const MDagPath &objPath,
        const MObject &attr,
        float &value) const;
    MStatus get_node_attr(
        const MDagPath &objPath,
        const MObject &attr,
        MDistance &value) const;

    // Called when the model editor state changes.
    static void on_model_editor_changed_func(void *clientData);
    MCallbackId m_model_editor_changed_callback_id;
};

} // namespace mmsolver

#endif // MM_SKY_DOME_DRAW_OVERRIDE_H
