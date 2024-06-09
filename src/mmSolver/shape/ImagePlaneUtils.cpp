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

#include "ImagePlaneUtils.h"

// Get M_PI constant
#define _USE_MATH_DEFINES
#include <cmath>

// STL
#include <algorithm>
#include <cstring>
#include <string>

// Maya
#include <maya/MColor.h>
#include <maya/MDistance.h>
#include <maya/MEventMessage.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MImage.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MPlugArray.h>
#include <maya/MPoint.h>
#include <maya/MString.h>

// Maya Viewport 2.0
#include <maya/MDrawContext.h>
#include <maya/MGeometryExtractor.h>
#include <maya/MPxGeometryOverride.h>
#include <maya/MShaderManager.h>
#include <maya/MSharedPtr.h>
#include <maya/MUserData.h>

// MM Solver
#include <mmcolorio/lib.h>
#include <mmcore/lib.h>

#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/render/shader/shader_utils.h"
#include "mmSolver/shape/constant_texture_data.h"
#include "mmSolver/utilities/number_utils.h"

namespace mmsolver {

bool getUpstreamNodeFromConnection(const MObject &this_node,
                                   const MString &attr_name,
                                   MPlugArray &out_connections) {
    MStatus status;
    MFnDependencyNode mfn_depend_node(this_node);

    bool wantNetworkedPlug = true;
    MPlug plug =
        mfn_depend_node.findPlug(attr_name, wantNetworkedPlug, &status);
    if (status != MStatus::kSuccess) {
        CHECK_MSTATUS(status);
        return false;
    }
    if (plug.isNull()) {
        MMSOLVER_MAYA_WRN("Could not get plug for \""
                          << mfn_depend_node.name().asChar() << "."
                          << attr_name.asChar() << "\" node.");
        return false;
    }

    bool as_destination = true;
    bool as_source = false;
    // Ask for plugs connecting to this node's ".shaderNode"
    // attribute.
    plug.connectedTo(out_connections, as_destination, as_source, &status);
    if (status != MStatus::kSuccess) {
        CHECK_MSTATUS(status);
        return false;
    }
    if (out_connections.length() == 0) {
        MMSOLVER_MAYA_WRN("No connections to the \""
                          << mfn_depend_node.name().asChar() << "."
                          << attr_name.asChar() << "\" attribute.");
        return false;
    }
    return true;
}

void calculate_node_image_size_string(
    MDagPath &objPath, MObject &draw_image_size_attr, MObject &image_width_attr,
    MObject &image_height_attr, MObject &image_pixel_aspect_attr,
    const uint32_t int_precision, const uint32_t double_precision,
    bool &out_draw_image_size, MString &out_image_size) {
    MStatus status = MS::kSuccess;

    double width = 1.0;
    double height = 1.0;
    double pixel_aspect = 1.0;

    status = getNodeAttr(objPath, draw_image_size_attr, out_draw_image_size);
    CHECK_MSTATUS(status);

    status = getNodeAttr(objPath, image_width_attr, width);
    CHECK_MSTATUS(status);

    status = getNodeAttr(objPath, image_height_attr, height);
    CHECK_MSTATUS(status);

    status = getNodeAttr(objPath, image_pixel_aspect_attr, pixel_aspect);
    CHECK_MSTATUS(status);

    double aspect = (width * pixel_aspect) / height;

    MString width_string;
    MString height_string;
    MString pixel_aspect_string;
    MString aspect_string;

    width_string.set(width, int_precision);
    height_string.set(height, int_precision);
    pixel_aspect_string.set(pixel_aspect, double_precision);
    aspect_string.set(aspect, double_precision);

    out_image_size = MString("Image: ") + width_string + MString(" x ") +
                     height_string + MString(" | PAR ") + pixel_aspect_string +
                     MString(" | ") + aspect_string;
    return;
}

void calculate_node_camera_size_string(MDagPath &objPath,
                                       MObject &draw_camera_size_attr,
                                       MObject &camera_width_inch_attr,
                                       MObject &camera_height_inch_attr,
                                       const uint32_t double_precision,
                                       bool &out_draw_camera_size,
                                       MString &out_camera_size) {
    MStatus status = MS::kSuccess;

    double width = 0.0;
    double height = 0.0;

    status = getNodeAttr(objPath, draw_camera_size_attr, out_draw_camera_size);
    CHECK_MSTATUS(status);

    status = getNodeAttr(objPath, camera_width_inch_attr, width);
    CHECK_MSTATUS(status);

    status = getNodeAttr(objPath, camera_height_inch_attr, height);
    CHECK_MSTATUS(status);

    double aspect = width / height;

    MString width_string;
    MString height_string;
    MString aspect_string;

    width_string.set(width * INCH_TO_MM, double_precision);
    height_string.set(height * INCH_TO_MM, double_precision);
    aspect_string.set(aspect, double_precision);

    out_camera_size = MString("Camera: ") + width_string + MString("mm x ") +
                      height_string + MString("mm | ") + aspect_string;
}

void find_geometry_node_path(MObject &node, MString &attr_name,
                             MDagPath &out_geometry_node_path,
                             MFn::Type &out_geometry_node_type) {
    const auto verbose = false;

    MPlugArray connections;
    bool ok = getUpstreamNodeFromConnection(node, attr_name, connections);
    if (!ok) {
        return;
    }

    for (uint32_t i = 0; i < connections.length(); ++i) {
        MObject node = connections[i].node();

        if (node.hasFn(MFn::kMesh)) {
            MDagPath path;
            MDagPath::getAPathTo(node, path);
            out_geometry_node_path = path;
            out_geometry_node_type = path.apiType();
            MMSOLVER_MAYA_VRB("Validated geometry node: "
                              << " path="
                              << out_geometry_node_path.fullPathName().asChar()
                              << " type=" << node.apiTypeStr());
            break;
        } else {
            MMSOLVER_MAYA_WRN("Geometry node is not correct type:"
                              << " path="
                              << out_geometry_node_path.fullPathName().asChar()
                              << " type=" << node.apiTypeStr());
        }
    }
}

void find_shader_node_path(MObject &node, MString &attr_name,
                           MObject &out_shader_node,
                           MFn::Type &out_shader_node_type) {
    const auto verbose = false;

    MPlugArray connections;
    bool ok = getUpstreamNodeFromConnection(node, attr_name, connections);
    if (!ok) {
        return;
    }

    for (uint32_t i = 0; i < connections.length(); ++i) {
        MObject node = connections[i].node();

        MFnDependencyNode mfn_depend_node(node);
        if (node.hasFn(MFn::kSurfaceShader) || node.hasFn(MFn::kHwShaderNode) ||
            node.hasFn(MFn::kPluginHardwareShader) ||
            node.hasFn(MFn::kPluginHwShaderNode)) {
            out_shader_node = node;
            out_shader_node_type = node.apiType();
            MMSOLVER_MAYA_VRB("Validated shader node: "
                              << " path=" << mfn_depend_node.name().asChar()
                              << " type=" << node.apiTypeStr());
            break;
        } else {
            MMSOLVER_MAYA_WRN("Shader node is not correct type:"
                              << " path=" << mfn_depend_node.name().asChar()
                              << " type=" << node.apiTypeStr());
        }
    }
}

void find_camera_node_path(MObject &node, MString &attr_name,
                           MDagPath &out_camera_node_path,
                           MFn::Type &out_camera_node_type) {
    const auto verbose = false;

    MPlugArray connections;
    bool ok = getUpstreamNodeFromConnection(node, attr_name, connections);
    if (!ok) {
        return;
    }

    for (uint32_t i = 0; i < connections.length(); ++i) {
        MObject node = connections[i].node();

        if (node.hasFn(MFn::kCamera)) {
            MDagPath path;
            MDagPath::getAPathTo(node, path);
            out_camera_node_path = path;
            out_camera_node_type = path.apiType();
            MMSOLVER_MAYA_VRB("Validated camera node: "
                              << " path="
                              << out_camera_node_path.fullPathName().asChar()
                              << " type=" << node.apiTypeStr());
            break;
        } else {
            MMSOLVER_MAYA_WRN("Camera node is not correct type:"
                              << " path="
                              << out_camera_node_path.fullPathName().asChar()
                              << " type=" << node.apiTypeStr());
        }
    }
}

}  // namespace mmsolver