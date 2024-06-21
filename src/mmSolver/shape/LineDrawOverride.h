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

#ifndef MM_LINE_DRAW_OVERRIDE_H
#define MM_LINE_DRAW_OVERRIDE_H

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
#include "LineShapeNode.h"
#include "mmSolver/utilities/debug_utils.h"

// MM SceneGraph
#include <mmscenegraph/mmscenegraph.h>

namespace mmsolver {

class LineDrawData : public MUserData {
public:
    LineDrawData()
#if MAYA_API_VERSION >= 20220000
        : MUserData()
#else
        // MUserData(bool) constructor is deprecated in Maya 2022+
        // because 'deleteAfterUse' is no longer needed.
        : MUserData(/*deleteAfterUse=*/true)  // let Maya clean up
#endif
        , m_depth_priority(0)
        , m_inner_line_width(1.0)
        , m_middle_line_width(1.0)
        , m_middle_scale(1.0)
        , m_point_size(1.0)
        , m_point_list()
        , m_active(false)
        , m_draw_name(false)
        , m_draw_middle(false) {
    }

    ~LineDrawData() override {}

    MString m_name;
    bool m_active;
    bool m_draw_name;
    bool m_draw_middle;

    unsigned int m_depth_priority;
    double m_point_size;

    double m_inner_line_width;
    double m_middle_line_width;

    double m_middle_scale;

    MColor m_color1{1.0f, 1.0f, 1.0f, 1.0f};
    MColor m_color2{0.0f, 0.0f, 1.0f, 1.0f};

    MPointArray m_point_list;
    rust::Vec<mmscenegraph::Real> m_point_data_x;
    rust::Vec<mmscenegraph::Real> m_point_data_y;
    MPoint m_middle_point_a;
    MPoint m_middle_point_b;
};

class LineDrawOverride : public MHWRender::MPxDrawOverride {
public:
    static MHWRender::MPxDrawOverride *Creator(const MObject &obj) {
        return new LineDrawOverride(obj);
    }

    ~LineDrawOverride() override;

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
        MGlobal::displayInfo("LineDrawOverride: " + message);
        MMSOLVER_MAYA_INFO("LineDrawOverride: " << message.asChar());
    }

private:
    LineDrawOverride(const MObject &obj);

    static void on_model_editor_changed_func(void *clientData);

    LineShapeNode *m_node;
    MCallbackId m_model_editor_changed_callback_id;
};

}  // namespace mmsolver

#endif  // MM_LINE_DRAW_OVERRIDE_H
