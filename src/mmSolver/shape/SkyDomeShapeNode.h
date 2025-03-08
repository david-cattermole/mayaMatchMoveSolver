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

#ifndef MM_SKY_DOME_SHAPE_NODE_H
#define MM_SKY_DOME_SHAPE_NODE_H

// Maya
#include <maya/MArrayDataBuilder.h>
#include <maya/MColor.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MDistance.h>
#include <maya/MFnUnitAttribute.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MPxLocatorNode.h>
#include <maya/MString.h>
#include <maya/MTypeId.h>
#include <maya/MVector.h>

#if MAYA_API_VERSION >= 20190000
#include <maya/MEvaluationNode.h>
#endif

// MM Solver
#include "mmSolver/utilities/assert_utils.h"

namespace mmsolver {

enum class DrawMode : short {
    kUseCustomDepth = 0,
    kDrawOnTop = 1,
    // kDrawBehind = 2,
};

enum class TransformMode : short {
    kNoOffset = 0,
    kCenterOfCamera = 1,
};

class SkyDomeShapeNode : public MPxLocatorNode {
public:
    SkyDomeShapeNode();

    ~SkyDomeShapeNode() override;

    MStatus compute(const MPlug &plug, MDataBlock &data) override;

    bool isBounded() const override;

    MBoundingBox boundingBox() const override;

    bool excludeAsLocator() const;

#if MAYA_API_VERSION >= 20190000
    MStatus preEvaluation(const MDGContext &context,
                          const MEvaluationNode &evaluationNode) override;
#endif

#if MAYA_API_VERSION >= 20200000
    void getCacheSetup(const MEvaluationNode &evalNode,
                       MNodeCacheDisablingInfo &disablingInfo,
                       MNodeCacheSetupInfo &cacheSetupInfo,
                       MObjectArray &monitoredAttributes) const override;
#endif

    static void *creator();

    static MStatus initialize();

    static MString nodeName();

    // Node specific meta-data.
    static MTypeId m_id;
    static MString m_draw_db_classification;
    static MString m_draw_registrant_id;
    static MString m_selection_type_name;
    static MString m_display_filter_name;
    static MString m_display_filter_label;

    // Attributes
    static MObject m_enable;
    static MObject m_transform_mode;
    static MObject m_alpha;
    static MObject m_line_width;
    static MObject m_resolution;
    static MObject m_draw_mode;
    static MObject m_radius;

    static MObject m_axis_x_enable;
    static MObject m_axis_y_enable;
    static MObject m_axis_z_enable;
    static MObject m_axis_x_enable_top;
    static MObject m_axis_z_enable_top;
    static MObject m_axis_x_enable_bottom;
    static MObject m_axis_z_enable_bottom;
    static MObject m_axis_x_color;
    static MObject m_axis_y_color;
    static MObject m_axis_z_color;
    static MObject m_axis_x_alpha;
    static MObject m_axis_y_alpha;
    static MObject m_axis_z_alpha;
    static MObject m_axis_x_line_width;
    static MObject m_axis_y_line_width;
    static MObject m_axis_z_line_width;

    static MObject m_grid_lat_enable;
    static MObject m_grid_long_enable;
    static MObject m_grid_lat_enable_top;
    static MObject m_grid_long_enable_top;
    static MObject m_grid_lat_enable_bottom;
    static MObject m_grid_long_enable_bottom;
    static MObject m_grid_lat_color;
    static MObject m_grid_long_color;
    static MObject m_grid_lat_alpha;
    static MObject m_grid_long_alpha;
    static MObject m_grid_lat_line_width;
    static MObject m_grid_long_line_width;
    static MObject m_grid_lat_divisions;
    static MObject m_grid_long_divisions;
};

}  // namespace mmsolver

#endif  // MM_SKY_DOME_SHAPE_NODE_H
