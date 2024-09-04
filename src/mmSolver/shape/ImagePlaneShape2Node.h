/*
 * Copyright (C) 2022, 2024 David Cattermole.
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

#ifndef MM_IMAGE_PLANE_SHAPE_2_NODE_H
#define MM_IMAGE_PLANE_SHAPE_2_NODE_H

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

namespace mmsolver {

class ImagePlaneShape2Node : public MPxLocatorNode {
public:
    ImagePlaneShape2Node();

    ~ImagePlaneShape2Node() override;

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
    static MString m_display_filter_draw_db_classification;
    static MString m_display_filter_name;
    static MString m_display_filter_label;

    // Attributes
    static MObject m_visible_to_camera_only;
    static MObject m_draw_hud;
    static MObject m_draw_image_size;
    static MObject m_draw_camera_size;
    static MObject m_image_width;
    static MObject m_image_height;
    static MObject m_image_num_channels;
    static MObject m_image_bytes_per_channel;
    static MObject m_image_size_bytes;
    static MObject m_image_pixel_aspect;
    static MObject m_camera_width_inch;
    static MObject m_camera_height_inch;
    static MObject m_lens_hash_current;
    static MObject m_lens_hash_previous;
    static MObject m_geometry_node;
    static MObject m_camera_node;
    static MObject m_shader_is_transparent;

    // Image Attributes
    static MObject m_image_display_channel;
    static MObject m_image_color_gain;
    static MObject m_image_color_exposure;
    static MObject m_image_color_gamma;
    static MObject m_image_color_saturation;
    static MObject m_image_color_soft_clip;
    static MObject m_image_alpha_gain;
    static MObject m_image_default_color;
    static MObject m_image_ignore_alpha;
    static MObject m_image_flip;
    static MObject m_image_flop;
    static MObject m_image_file_path;
    static MObject m_image_frame_number;
    static MObject m_image_input_color_space;
    static MObject m_image_output_color_space;
};

}  // namespace mmsolver

#endif  // MM_IMAGE_PLANE_SHAPE_2_NODE_H
