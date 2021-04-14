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

#include <maya/MPxLocatorNode.h>
#include <maya/MString.h>
#include <maya/MObject.h>
#include <maya/MTypeId.h>
#include <maya/MPlug.h>
#include <maya/MVector.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MColor.h>
#include <maya/MDistance.h>
#include <maya/MFnUnitAttribute.h>
#include <maya/MArrayDataBuilder.h>

#if MAYA_API_VERSION >= 20190000
#include <maya/MEvaluationNode.h>
#include <assert.h>
#endif

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

#if MAYA_API_VERSION >= 20190000
    MStatus preEvaluation(const MDGContext &context,
                          const MEvaluationNode &evaluationNode) override;

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

    // Attributes
    static MObject m_global_enable;
    static MObject m_transform_mode;
    static MObject m_global_line_width;
    static MObject m_resolution;
    static MObject m_draw_mode;
    static MObject m_radius;
    static MObject m_latitude_enable;
    static MObject m_longitude_enable;
    static MObject m_latitude_line_width;
    static MObject m_longitude_line_width;
    static MObject m_latitude_divisions;
    static MObject m_longitude_divisions;
    static MObject m_x_axis_enable;
    static MObject m_y_axis_enable;
    static MObject m_z_axis_enable;
    static MObject m_x_axis_line_width;
    static MObject m_y_axis_line_width;
    static MObject m_z_axis_line_width;
    static MObject m_top_axis_enable;
    static MObject m_bottom_axis_enable;
};

} // namespace mmsolver

#endif // MM_SKY_DOME_SHAPE_NODE_H
