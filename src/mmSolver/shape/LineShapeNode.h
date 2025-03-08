/*
 * Copyright (C) 2021-2022 David Cattermole.
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

#ifndef MM_LINE_SHAPE_NODE_H
#define MM_LINE_SHAPE_NODE_H

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

// MM SceneGraph
#include <mmscenegraph/mmscenegraph.h>

namespace mmsolver {

class LineShapeNode : public MPxLocatorNode {
public:
    LineShapeNode();

    ~LineShapeNode() override;

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

    // Display Attributes
    static MObject m_draw_name;
    static MObject m_draw_middle;
    static MObject m_color;
    static MObject m_alpha;
    static MObject m_point_size;
    static MObject m_inner_line_width;
    static MObject m_middle_line_width;
    static MObject m_objects;

    // Input Attributes
    static MObject m_transform_matrix;
    static MObject m_parent_inverse_matrix;
    static MObject m_middle_scale;  // Also controls display.

    // Output Attributes
    static MObject m_out_line;
    static MObject m_out_line_center_x;
    static MObject m_out_line_center_y;
    static MObject m_out_line_dir_x;
    static MObject m_out_line_dir_y;
    static MObject m_out_line_slope;
    static MObject m_out_line_angle;

    static MObject m_out_line_point_a;
    static MObject m_out_line_point_ax;
    static MObject m_out_line_point_ay;

    static MObject m_out_line_point_b;
    static MObject m_out_line_point_bx;
    static MObject m_out_line_point_by;

private:
    // Internal Data.
    rust::Vec<mmscenegraph::Real> m_point_data_x;
    rust::Vec<mmscenegraph::Real> m_point_data_y;
};

}  // namespace mmsolver

#endif  // MM_LINE_SHAPE_NODE_H
