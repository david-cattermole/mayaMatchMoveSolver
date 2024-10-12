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

#ifndef MM_IMAGE_PLANE_UTILS_H
#define MM_IMAGE_PLANE_UTILS_H

// Maya
#include <maya/MColor.h>
#include <maya/MEventMessage.h>
#include <maya/MGlobal.h>
#include <maya/MImage.h>
#include <maya/MPointArray.h>
#include <maya/MStreamUtils.h>
#include <maya/MString.h>

// Maya Viewport 2.0
#include <maya/MDrawContext.h>
#include <maya/MDrawRegistry.h>
#include <maya/MHWGeometryUtilities.h>
#include <maya/MPxGeometryOverride.h>
#include <maya/MUserData.h>

// MM Solver
#include <mmcore/lib.h>

#include "ImagePlaneShapeNode.h"
#include "mmSolver/utilities/debug_utils.h"

namespace mmsolver {

enum class ImageDisplayChannel {
    kRGBA = 0,
    kRGB,
    kRed,
    kGreen,
    kBlue,
    kAlpha,
    kLuminance
};

bool getUpstreamNodeFromConnection(const MObject &this_node,
                                   const MString &attr_name,
                                   MPlugArray &out_connections);

void calculate_node_image_size_string(
    MDagPath &objPath, MObject &draw_image_size_attr, MObject &image_width_attr,
    MObject &image_height_attr, MObject &image_pixel_aspect_attr,
    const uint32_t int_precision, const uint32_t double_precision,
    bool &out_draw_image_size, MString &out_image_size);

void calculate_node_camera_size_string(MDagPath &objPath,
                                       MObject &draw_camera_size_attr,
                                       MObject &camera_width_inch_attr,
                                       MObject &camera_height_inch_attr,
                                       const uint32_t double_precision,
                                       bool &out_draw_camera_size,
                                       MString &out_camera_size);

void find_geometry_node_path(MObject &node, MString &attr_name,
                             MDagPath &out_geometry_node_path,
                             MFn::Type &out_geometry_node_type);

void find_shader_node_path(MObject &node, MString &attr_name,
                           MObject &out_shader_node,
                           MFn::Type &out_shader_node_type);

void find_camera_node_path(MObject &node, MString &attr_name,
                           MDagPath &out_camera_node_path,
                           MFn::Type &out_camera_node_type);

}  // namespace mmsolver

#endif  // MM_IMAGE_PLANE_UTILS_H
