/*
 * Copyright (C) 2020, 2021 David Cattermole.
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

#include "maya_scene_graph.h"

// STL
#include <limits>
#include <unordered_map>

// Maya
#include <maya/MComputation.h>
#include <maya/MDagPath.h>
#include <maya/MFnAttribute.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MFnTransform.h>
#include <maya/MObject.h>
#include <maya/MStreamUtils.h>
#include <maya/MString.h>
#include <maya/MTime.h>
#include <maya/MTimeArray.h>
#include <maya/MTypes.h>

// MM Solver Libs
#include <mmsolverlibs/debug.h>

// MM SceneGraph
#include <mmscenegraph/mmscenegraph.h>

// MM Solver
#include "maya_attr.h"
#include "maya_attr_list.h"
#include "maya_bundle.h"
#include "maya_camera.h"
#include "maya_frame_utils.h"
#include "maya_marker.h"
#include "maya_marker_group.h"
#include "maya_marker_list.h"
#include "maya_utils.h"
#include "mmSolver/core/frame_list.h"
#include "mmSolver/core/types.h"
#include "mmSolver/utilities/assert_utils.h"
#include "mmSolver/utilities/number_utils.h"

namespace mmsg = mmscenegraph;

namespace mmsolver {

using StringToAttrIdMap = std::unordered_map<std::string, mmsg::AttrId>;
using StringToNodeIdMap = std::unordered_map<std::string, mmsg::NodeId>;

bool is_zero(MPoint value, double tolerance = 1.0e-3) {
    bool x_is_zero = number::isApproxEqual<double>(value.x, 0.0, tolerance);
    bool y_is_zero = number::isApproxEqual<double>(value.y, 0.0, tolerance);
    bool z_is_zero = number::isApproxEqual<double>(value.z, 0.0, tolerance);
    return x_is_zero && y_is_zero && z_is_zero;
}

bool is_zero(MVector value, double tolerance = 1.0e-3) {
    bool x_is_zero = number::isApproxEqual<double>(value.x, 0.0, tolerance);
    bool y_is_zero = number::isApproxEqual<double>(value.y, 0.0, tolerance);
    bool z_is_zero = number::isApproxEqual<double>(value.z, 0.0, tolerance);
    return x_is_zero && y_is_zero && z_is_zero;
}

bool attribute_source_plug(MFnDependencyNode &depend_node, const MString &name,
                           MPlug &out_source_plug) {
    MStatus status = MS::kSuccess;
    const bool want_networked_plug = true;
    MPlug plug = depend_node.findPlug(name, want_networked_plug, &status);
    if (status != MS::kSuccess) {
        return false;
    }
    if (plug.isNull()) {
        return false;
    }

    MPlug source_plug = plug.source();
    if (!source_plug.isNull()) {
        out_source_plug = source_plug;
        return true;
    }

    return false;
}

bool attribute_has_complex_connection(MFnDependencyNode &depend_node,
                                      const MString &name) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("attribute_has_complex_connection");

    MStatus status = MS::kSuccess;
    MPlug source_plug;
    bool ok = attribute_source_plug(depend_node, name, source_plug);
    if (!ok) {
        return false;
    }
    // Input connections can be to an animation curve only.
    MObject source_node_mobject = source_plug.node();
    auto has_anim_curve = source_node_mobject.hasFn(MFn::kAnimCurve);
    if (has_anim_curve) {
        return false;
    }

    MObject source_attr = source_plug.attribute(&status);
    if (status != MS::kSuccess) {
        MMSOLVER_MAYA_WRN(
            "MM Scene Graph attribute_has_complex_connection: "
            "Failed to get source attribute.");
        return true;
    }

    MFnAttribute source_attr_fn(source_attr, &status);
    if (status != MS::kSuccess) {
        MMSOLVER_MAYA_WRN(
            "MM Scene Graph attribute_has_complex_connection: "
            "Failed to get source attribute function set.");
        return true;
    }

    MFnDependencyNode source_node_fn(source_node_mobject, &status);
    if (status != MS::kSuccess) {
        MMSOLVER_MAYA_WRN(
            "MM Scene Graph attribute_has_complex_connection: "
            "Failed to get source node dependency function set.");
        return true;
    }

    bool is_readable = source_attr_fn.isReadable();
    bool is_writable = source_attr_fn.isWritable();
    if (is_readable && !is_writable) {
        // This means the attribute is an 'output attribute'.
        const MString source_node_name = source_node_fn.name();
        const MString source_attr_name = source_attr_fn.name();
        const MString node_name = depend_node.name();
        MMSOLVER_MAYA_WRN(
            "MM Scene Graph: Complex attribute connection detected from "
            << "\"" << source_node_name.asChar() << "."
            << source_attr_name.asChar() << "\""
            << " to "
            << "\"" << node_name.asChar() << "." << name.asChar() << "\": "
            << " attr_is_readable=" << is_readable
            << " attr_is_writable=" << is_writable);
        return true;
    }

    // This means the attribute is an 'output attribute'.
    const MString source_node_name = source_node_fn.name();
    const MString source_attr_name = source_attr_fn.name();
    const MString node_name = depend_node.name();
    MMSOLVER_MAYA_VRB(
        "MM Scene Graph: No complex attribute connection detected from "
        << "\"" << source_node_name.asChar() << "." << source_attr_name.asChar()
        << "\""
        << " to "
        << "\"" << node_name.asChar() << "." << name.asChar() << "\": "
        << " attr_is_readable=" << is_readable
        << " attr_is_writable=" << is_writable);

    return false;
}

MStatus add_attribute(Attr &mayaAttr, const MString &attr_name,
                      const MTimeArray &timeArray,
                      const mmsg::FrameValue start_frame,
                      const mmsg::FrameValue end_frame, const int timeEvalMode,
                      const double scaleFactor,
                      mmsg::AttrDataBlock &out_attrDataBlock,
                      mmsg::AttrId &out_attrId,
                      StringToAttrIdMap &out_attrNameToAttrIdMap) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("add_attribute");

    mayaAttr.setAttrName(attr_name);

    // TODO: If the attribute is keyed, but there's only one frame in
    // the frame list, then we can consider the attribute static, not
    // animated.

    auto animated = mayaAttr.isAnimated();
    // auto locked = !mayaAttr.isFreeToChange();
    auto connected = mayaAttr.isConnected();

    MMSOLVER_ASSERT(
        timeArray.length() > 0,
        "It only makes sense to have an attribute evaluated at some frames.");

    MStatus status = MS::kSuccess;
    double value = 0.0;
    if (animated) {
        // Dense attributes expect the frame and values to be
        // contiguous. Therefore if frames [1, 4, 6] (with size of 3)
        // are wanted, we must allocate memory for frames 1 to 6 (size
        // of 6), not 3.
        auto total_frame_count = (end_frame - start_frame) + 1;
        auto uiUnit = MTime::uiUnit();
        auto values = rust::Vec<mmsg::Real>();
        values.reserve(total_frame_count);
        for (mmsg::FrameValue f = start_frame; f < (end_frame + 1); ++f) {
            auto frame_time = MTime(static_cast<double>(f), uiUnit);
            status = mayaAttr.getValue(value, frame_time, timeEvalMode);
            MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
            values.push_back(value * scaleFactor);
        }
        out_attrId =
            out_attrDataBlock.create_attr_anim_dense(values, start_frame);
    } else if (connected) {
        // Find source of attribute connection.
        MObject node_mobject = mayaAttr.getObject();
        MFnDependencyNode depend_node(node_mobject);
        MPlug source_plug;
        bool ok = attribute_source_plug(depend_node, attr_name, source_plug);
        if (ok) {
            MObject source_plug_node = source_plug.node();
            if (!source_plug_node.isNull()) {
                MString source_node_name;
                status = getUniqueNodeName(source_plug_node, source_node_name);

                bool includeNodeName = false;
                bool includeNonMandatoryIndices = false;
                bool includeInstancedIndices = false;
                bool useAlias = false;
                bool useFullAttributePath = false;
                bool useLongNames = true;
                MString source_attr_name = source_plug.partialName(
                    includeNodeName, includeNonMandatoryIndices,
                    includeInstancedIndices, useAlias, useFullAttributePath,
                    useLongNames);

                auto mayaAttrSource = Attr();
                mayaAttrSource.setNodeName(source_node_name);
                mayaAttrSource.setAttrName(source_attr_name);
                status = add_attribute(
                    mayaAttrSource, source_attr_name, timeArray, start_frame,
                    end_frame, timeEvalMode, scaleFactor, out_attrDataBlock,
                    out_attrId, out_attrNameToAttrIdMap);
                MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
            }
        }
    } else {
        status = mayaAttr.getValue(value, timeEvalMode);
        out_attrId = out_attrDataBlock.create_attr_static(value * scaleFactor);
    }

    const MString nodeAttrName = mayaAttr.getLongName();
    auto nodeAttrNameStr = std::string(nodeAttrName.asChar());
    out_attrNameToAttrIdMap.insert({nodeAttrNameStr, out_attrId});

    return status;
}

MStatus get_translate_attrs(Attr &mayaAttr, const MTimeArray &timeArray,
                            const mmsg::FrameValue start_frame,
                            const mmsg::FrameValue end_frame,
                            const int timeEvalMode,
                            mmsg::AttrDataBlock &out_attrDataBlock,
                            mmsg::Translate3DAttrIds &out_attrIds,
                            StringToAttrIdMap &out_attrNameToAttrIdMap) {
    double scaleFactor = 1.0;  // No conversion.

    MStatus status =
        add_attribute(mayaAttr, MString("translateX"), timeArray, start_frame,
                      end_frame, timeEvalMode, scaleFactor, out_attrDataBlock,
                      out_attrIds.tx, out_attrNameToAttrIdMap);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    status =
        add_attribute(mayaAttr, MString("translateY"), timeArray, start_frame,
                      end_frame, timeEvalMode, scaleFactor, out_attrDataBlock,
                      out_attrIds.ty, out_attrNameToAttrIdMap);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    status =
        add_attribute(mayaAttr, MString("translateZ"), timeArray, start_frame,
                      end_frame, timeEvalMode, scaleFactor, out_attrDataBlock,
                      out_attrIds.tz, out_attrNameToAttrIdMap);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    return status;
}

MStatus get_rotate_attrs(Attr &mayaAttr, const MTimeArray &timeArray,
                         const mmsg::FrameValue start_frame,
                         const mmsg::FrameValue end_frame,
                         const int timeEvalMode,
                         mmsg::AttrDataBlock &out_attrDataBlock,
                         mmsg::Rotate3DAttrIds &out_attrIds,
                         StringToAttrIdMap &out_attrNameToAttrIdMap) {
    double scaleFactor = 1.0;  // No conversion.

    MStatus status =
        add_attribute(mayaAttr, MString("rotateX"), timeArray, start_frame,
                      end_frame, timeEvalMode, scaleFactor, out_attrDataBlock,
                      out_attrIds.rx, out_attrNameToAttrIdMap);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    status =
        add_attribute(mayaAttr, MString("rotateY"), timeArray, start_frame,
                      end_frame, timeEvalMode, scaleFactor, out_attrDataBlock,
                      out_attrIds.ry, out_attrNameToAttrIdMap);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    status =
        add_attribute(mayaAttr, MString("rotateZ"), timeArray, start_frame,
                      end_frame, timeEvalMode, scaleFactor, out_attrDataBlock,
                      out_attrIds.rz, out_attrNameToAttrIdMap);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    return status;
}

MStatus get_scale_attrs(Attr &mayaAttr, const MTimeArray &timeArray,
                        const mmsg::FrameValue start_frame,
                        const mmsg::FrameValue end_frame,
                        const int timeEvalMode,
                        mmsg::AttrDataBlock &out_attrDataBlock,
                        mmsg::Scale3DAttrIds &out_attrIds,
                        StringToAttrIdMap &out_attrNameToAttrIdMap) {
    double scaleFactor = 1.0;  // No conversion.

    MStatus status =
        add_attribute(mayaAttr, MString("scaleX"), timeArray, start_frame,
                      end_frame, timeEvalMode, scaleFactor, out_attrDataBlock,
                      out_attrIds.sx, out_attrNameToAttrIdMap);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    status =
        add_attribute(mayaAttr, MString("scaleY"), timeArray, start_frame,
                      end_frame, timeEvalMode, scaleFactor, out_attrDataBlock,
                      out_attrIds.sy, out_attrNameToAttrIdMap);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    status =
        add_attribute(mayaAttr, MString("scaleZ"), timeArray, start_frame,
                      end_frame, timeEvalMode, scaleFactor, out_attrDataBlock,
                      out_attrIds.sz, out_attrNameToAttrIdMap);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    return status;
}

MStatus get_camera_attrs(
    Attr &mayaAttr, CameraPtr &camera, const MTimeArray &timeArray,
    const mmsg::FrameValue start_frame, const mmsg::FrameValue end_frame,
    const int timeEvalMode, mmsg::AttrDataBlock &out_attrDataBlock,
    mmsg::CameraAttrIds &out_attrIds, mmsg::FilmFit &out_film_fit,
    int32_t &out_render_image_width, int32_t &out_render_image_height,
    StringToAttrIdMap &out_attrNameToAttrIdMap) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("get_camera_attrs");

    double scaleFactor = 1.0;  // No conversion.
    double inch_to_mm = 25.4;

    out_film_fit = static_cast<mmsg::FilmFit>(camera->getFilmFitValue());
    out_render_image_width = camera->getRenderWidthValue();
    out_render_image_height = camera->getRenderHeightValue();

    MStatus status = add_attribute(
        mayaAttr, MString("horizontalFilmAperture"), timeArray, start_frame,
        end_frame, timeEvalMode, inch_to_mm, out_attrDataBlock,
        out_attrIds.sensor_width, out_attrNameToAttrIdMap);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    status = add_attribute(mayaAttr, MString("verticalFilmAperture"), timeArray,
                           start_frame, end_frame, timeEvalMode, inch_to_mm,
                           out_attrDataBlock, out_attrIds.sensor_height,
                           out_attrNameToAttrIdMap);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    status =
        add_attribute(mayaAttr, MString("focalLength"), timeArray, start_frame,
                      end_frame, timeEvalMode, scaleFactor, out_attrDataBlock,
                      out_attrIds.focal_length, out_attrNameToAttrIdMap);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    status = add_attribute(mayaAttr, MString("horizontalFilmOffset"), timeArray,
                           start_frame, end_frame, timeEvalMode, inch_to_mm,
                           out_attrDataBlock, out_attrIds.lens_offset_x,
                           out_attrNameToAttrIdMap);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    status = add_attribute(mayaAttr, MString("verticalFilmOffset"), timeArray,
                           start_frame, end_frame, timeEvalMode, inch_to_mm,
                           out_attrDataBlock, out_attrIds.lens_offset_y,
                           out_attrNameToAttrIdMap);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    status = add_attribute(mayaAttr, MString("nearClipPlane"), timeArray,
                           start_frame, end_frame, timeEvalMode, scaleFactor,
                           out_attrDataBlock, out_attrIds.near_clip_plane,
                           out_attrNameToAttrIdMap);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    status =
        add_attribute(mayaAttr, MString("farClipPlane"), timeArray, start_frame,
                      end_frame, timeEvalMode, scaleFactor, out_attrDataBlock,
                      out_attrIds.far_clip_plane, out_attrNameToAttrIdMap);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    status =
        add_attribute(mayaAttr, MString("cameraScale"), timeArray, start_frame,
                      end_frame, timeEvalMode, scaleFactor, out_attrDataBlock,
                      out_attrIds.camera_scale, out_attrNameToAttrIdMap);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    return status;
}

MStatus get_rotate_order_attr(Attr &mayaAttr, const int timeEvalMode,
                              mmsg::RotateOrder &out_rotateOrder) {
    MStatus status = mayaAttr.setAttrName(MString("rotateOrder"));
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    short value = 0;
    mayaAttr.getValue(value, timeEvalMode);
    switch (value) {
        break;
        case 0:
            out_rotateOrder = mmsg::RotateOrder::kXYZ;
            break;
        case 1:
            out_rotateOrder = mmsg::RotateOrder::kYZX;
            break;
        case 2:
            out_rotateOrder = mmsg::RotateOrder::kZXY;
            break;
        case 3:
            out_rotateOrder = mmsg::RotateOrder::kXZY;
            break;
        case 4:
            out_rotateOrder = mmsg::RotateOrder::kYXZ;
            break;
        case 5:
            out_rotateOrder = mmsg::RotateOrder::kZYX;
            break;
        default:
            out_rotateOrder = mmsg::RotateOrder::kUnknown;
    }
    return status;
}

MStatus get_transform_attrs(Attr &mayaAttr, const MTimeArray &timeArray,
                            const mmsg::FrameValue start_frame,
                            const mmsg::FrameValue end_frame,
                            const int timeEvalMode,
                            mmsg::AttrDataBlock &out_attrDataBlock,
                            mmsg::Translate3DAttrIds &out_translateAttrIds,
                            mmsg::Rotate3DAttrIds &out_rotateAttrIds,
                            mmsg::Scale3DAttrIds &out_scaleAttrIds,
                            mmsg::RotateOrder &out_rotateOrder,
                            StringToAttrIdMap &out_attrNameToAttrIdMap) {
    MStatus status = get_translate_attrs(
        mayaAttr, timeArray, start_frame, end_frame, timeEvalMode,
        out_attrDataBlock, out_translateAttrIds, out_attrNameToAttrIdMap);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    status = get_rotate_attrs(mayaAttr, timeArray, start_frame, end_frame,
                              timeEvalMode, out_attrDataBlock,
                              out_rotateAttrIds, out_attrNameToAttrIdMap);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    status = get_scale_attrs(mayaAttr, timeArray, start_frame, end_frame,
                             timeEvalMode, out_attrDataBlock, out_scaleAttrIds,
                             out_attrNameToAttrIdMap);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    status = get_rotate_order_attr(mayaAttr, timeEvalMode, out_rotateOrder);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    return status;
}

MStatus get_film_fit_attr(Attr &mayaAttr, const int timeEvalMode,
                          mmsg::FilmFit &out_filmFit) {
    MStatus status = mayaAttr.setAttrName(MString("filmFit"));
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    short value = 0;
    mayaAttr.getValue(value, timeEvalMode);
    switch (value) {
        break;
        case 0:
            out_filmFit = mmsg::FilmFit::kFill;
            break;
        case 1:
            out_filmFit = mmsg::FilmFit::kHorizontal;
            break;
        case 2:
            out_filmFit = mmsg::FilmFit::kVertical;
            break;
        case 3:
            out_filmFit = mmsg::FilmFit::kOverscan;
            break;
        default:
            out_filmFit = mmsg::FilmFit::kUnknown;
    }
    return status;
}

MStatus get_marker_attrs(Attr &mayaAttr, const MTimeArray &timeArray,
                         const mmsg::FrameValue start_frame,
                         const mmsg::FrameValue end_frame,
                         const int timeEvalMode, const double overscan_x,
                         const double overscan_y,
                         mmsg::AttrDataBlock &out_attrDataBlock,
                         mmsg::MarkerAttrIds &out_attrIds,
                         StringToAttrIdMap &out_attrNameToAttrIdMap) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("get_marker_attrs");

    MStatus status = MS::kSuccess;
    double scaleFactor = 1.0;  // No conversion.

    // The MarkerGroup's overscan values are used to correct the
    // marker's position as if the overscan values never existed.
    double scaleFactor_x = 1.0 / overscan_x;
    double scaleFactor_y = 1.0 / overscan_y;

    add_attribute(mayaAttr, MString("translateX"), timeArray, start_frame,
                  end_frame, timeEvalMode, scaleFactor_x, out_attrDataBlock,
                  out_attrIds.tx, out_attrNameToAttrIdMap);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    add_attribute(mayaAttr, MString("translateY"), timeArray, start_frame,
                  end_frame, timeEvalMode, scaleFactor_y, out_attrDataBlock,
                  out_attrIds.ty, out_attrNameToAttrIdMap);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    // TODO: The marker weight is more complicated because the user
    // can also disable the marker using the 'enable' attribute.
    //
    // TODO: Do we actually need the weight? It's not used inside
    // mmscenegraph currently.
    add_attribute(mayaAttr, MString("weight"), timeArray, start_frame,
                  end_frame, timeEvalMode, scaleFactor, out_attrDataBlock,
                  out_attrIds.weight, out_attrNameToAttrIdMap);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    return status;
}

// Check if the transform has any of:
//
// - DAG path is invalid.
//
// - DAG node is an instance.
//
// - "Complex" input connections to the transform values, where
//   "complex" means the source connection is computed as the output
//   of a Maya node (which cannot be replaced by MM Scene Graph).
//
// - Non-zero pivot-point (or pivot point translation) transform
//   values.
//
// If a node has any of these, the transform node is not supported and
// we must bail out of using the MM Scene Graph as an acceleration.
MStatus check_transform_node(MDagPath &dag_path) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("check_transform_node");

    MStatus status = MS::kSuccess;

    auto path_valid = dag_path.isValid(&status);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    if (!path_valid) {
        status = MS::kFailure;
        const MString node_name = dag_path.fullPathName();
        MMSOLVER_MAYA_WRN("MM Scene Graph: Invalid DAG path: "
                          << "\"" << node_name.asChar() << "\"");
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    auto is_instanced = dag_path.isInstanced(&status);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    if (is_instanced) {
        status = MS::kFailure;
        const MString node_name = dag_path.fullPathName();
        MMSOLVER_MAYA_WRN("MM Scene Graph: No support for instanced nodes: "
                          << "\"" << node_name.asChar() << "\"");
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    MObject node_mobject = dag_path.node(&status);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    if (node_mobject.isNull()) {
        status = MS::kFailure;
        const MString node_name = dag_path.fullPathName();
        MMSOLVER_MAYA_WRN("MM Scene Graph: Invalid node MObject: "
                          << "\"" << node_name.asChar() << "\"");
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    MFnTransform mfn_transform(node_mobject, &status);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    MPoint scale_pivot = mfn_transform.scalePivot(MSpace::kTransform, &status);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    if (!is_zero(scale_pivot)) {
        status = MS::kFailure;
        const MString node_name = dag_path.fullPathName();
        MMSOLVER_MAYA_WRN(
            "MM Scene Graph: No support for non-zero scale pivot: "
            << "\"" << node_name.asChar() << "\"");
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    MVector scale_pivot_translation =
        mfn_transform.scalePivotTranslation(MSpace::kTransform, &status);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    if (!is_zero(scale_pivot_translation)) {
        status = MS::kFailure;
        const MString node_name = dag_path.fullPathName();
        MMSOLVER_MAYA_WRN(
            "MM Scene Graph: No support for non-zero scale pivot translation: "
            << "\"" << node_name.asChar() << "\"");
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    MPoint rotate_pivot =
        mfn_transform.rotatePivot(MSpace::kTransform, &status);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    if (!is_zero(rotate_pivot)) {
        status = MS::kFailure;
        const MString node_name = dag_path.fullPathName();
        MMSOLVER_MAYA_WRN(
            "MM Scene Graph: No support for non-zero rotate pivot: "
            << "\"" << node_name.asChar() << "\"");
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    MVector rotate_pivot_translation =
        mfn_transform.rotatePivotTranslation(MSpace::kTransform, &status);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    if (!is_zero(rotate_pivot_translation)) {
        status = MS::kFailure;
        const MString node_name = dag_path.fullPathName();
        MMSOLVER_MAYA_WRN(
            "MM Scene Graph: No support for non-zero rotate pivot "
            "translation\": "
            << "\"" << node_name.asChar() << "\"");
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    MFnDependencyNode dg_node(node_mobject);
    auto tx_attr_name = MString("translateX");
    auto tx_has_conn = attribute_has_complex_connection(dg_node, tx_attr_name);
    if (tx_has_conn) {
        status = MS::kFailure;
        const MString node_name = dag_path.fullPathName();
        MMSOLVER_MAYA_WRN("MM Scene Graph: Unsupported attribute connection on "
                          << "\"" << tx_attr_name.asChar() << "\": "
                          << "\"" << node_name.asChar() << "\"");
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    auto ty_attr_name = MString("translateY");
    auto ty_has_conn = attribute_has_complex_connection(dg_node, ty_attr_name);
    if (ty_has_conn) {
        status = MS::kFailure;
        const MString node_name = dag_path.fullPathName();
        MMSOLVER_MAYA_WRN("MM Scene Graph: Unsupported attribute connection on "
                          << "\"" << ty_attr_name.asChar() << "\": "
                          << "\"" << node_name.asChar() << "\"");
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    auto tz_attr_name = MString("translateZ");
    auto tz_has_conn = attribute_has_complex_connection(dg_node, tz_attr_name);
    if (tz_has_conn) {
        status = MS::kFailure;
        const MString node_name = dag_path.fullPathName();
        MMSOLVER_MAYA_WRN("MM Scene Graph: Unsupported attribute connection on "
                          << "\"" << tz_attr_name.asChar() << "\": "
                          << "\"" << node_name.asChar() << "\"");
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    auto rx_attr_name = MString("rotateX");
    auto rx_has_conn = attribute_has_complex_connection(dg_node, rx_attr_name);
    if (rx_has_conn) {
        status = MS::kFailure;
        const MString node_name = dag_path.fullPathName();
        MMSOLVER_MAYA_WRN("MM Scene Graph: Unsupported attribute connection on "
                          << "\"" << rx_attr_name.asChar() << "\": "
                          << "\"" << node_name.asChar() << "\"");
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    auto ry_attr_name = MString("rotateY");
    auto ry_has_conn = attribute_has_complex_connection(dg_node, ry_attr_name);
    if (ry_has_conn) {
        status = MS::kFailure;
        const MString node_name = dag_path.fullPathName();
        MMSOLVER_MAYA_WRN("MM Scene Graph: Unsupported attribute connection on "
                          << "\"" << ry_attr_name.asChar() << "\": "
                          << "\"" << node_name.asChar() << "\"");
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    auto rz_attr_name = MString("rotateZ");
    auto rz_has_conn = attribute_has_complex_connection(dg_node, rz_attr_name);
    if (rz_has_conn) {
        status = MS::kFailure;
        const MString node_name = dag_path.fullPathName();
        MMSOLVER_MAYA_WRN("MM Scene Graph: Unsupported attribute connection on "
                          << "\"" << rz_attr_name.asChar() << "\": "
                          << "\"" << node_name.asChar() << "\"");
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    auto sx_attr_name = MString("scaleX");
    auto sx_has_conn = attribute_has_complex_connection(dg_node, sx_attr_name);
    if (sx_has_conn) {
        status = MS::kFailure;
        const MString node_name = dag_path.fullPathName();
        MMSOLVER_MAYA_WRN("MM Scene Graph: Unsupported attribute connection on "
                          << "\"" << sx_attr_name.asChar() << "\": "
                          << "\"" << node_name.asChar() << "\"");
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    auto sy_attr_name = MString("scaleY");
    auto sy_has_conn = attribute_has_complex_connection(dg_node, sy_attr_name);
    if (sy_has_conn) {
        status = MS::kFailure;
        const MString node_name = dag_path.fullPathName();
        MMSOLVER_MAYA_WRN("MM Scene Graph: Unsupported attribute connection on "
                          << "\"" << sy_attr_name.asChar() << "\": "
                          << "\"" << node_name.asChar() << "\"");
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    auto sz_attr_name = MString("scaleZ");
    auto sz_has_conn = attribute_has_complex_connection(dg_node, sz_attr_name);
    if (sz_has_conn) {
        status = MS::kFailure;
        const MString node_name = dag_path.fullPathName();
        MMSOLVER_MAYA_WRN("MM Scene Graph: Unsupported attribute connection on "
                          << "\"" << sz_attr_name.asChar() << "\": "
                          << "\"" << node_name.asChar() << "\"");
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    return status;
}

MStatus add_transforms(const mmsg::NodeId parent_node_id, MDagPath &dag_path,
                       const MTimeArray &timeArray,
                       const mmsg::FrameValue start_frame,
                       const mmsg::FrameValue end_frame, const int timeEvalMode,
                       mmsg::SceneGraph &out_sceneGraph,
                       mmsg::AttrDataBlock &out_attrDataBlock,
                       StringToNodeIdMap &out_nodeNameToNodeIdMap,
                       StringToAttrIdMap &out_attrNameToAttrIdMap) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("add_transforms");
    MStatus status = MS::kSuccess;

    // Create a single attribute that will be re-used.
    auto mayaAttr = Attr();

    auto translate_attr_ids = mmsg::Translate3DAttrIds();
    auto rotate_attr_ids = mmsg::Rotate3DAttrIds();
    auto scale_attr_ids = mmsg::Scale3DAttrIds();
    auto rotate_order = mmsg::RotateOrder::kUnknown;

    auto previous_node_id = parent_node_id;
    while (dag_path.length() > 0) {
        MString transform_name = dag_path.fullPathName(&status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        auto nodeNameStr = std::string(transform_name.asChar());

        auto tfm_node_id = mmsg::NodeId();
        if (!dag_path.hasFn(MFn::kTransform, &status)) {
            break;
        }

        status = check_transform_node(dag_path);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

        auto search = out_nodeNameToNodeIdMap.find(nodeNameStr);
        if (search != out_nodeNameToNodeIdMap.end()) {
            // Already exists.
            tfm_node_id = search->second;
        } else {
            // Create a new transform.
            status = mayaAttr.setNodeName(transform_name);
            MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

            get_transform_attrs(
                mayaAttr, timeArray, start_frame, end_frame, timeEvalMode,
                out_attrDataBlock, translate_attr_ids, rotate_attr_ids,
                scale_attr_ids, rotate_order, out_attrNameToAttrIdMap);

            auto tfm_node = out_sceneGraph.create_transform_node(
                translate_attr_ids, rotate_attr_ids, scale_attr_ids,
                rotate_order);
            tfm_node_id = tfm_node.id;

            out_nodeNameToNodeIdMap.insert({nodeNameStr, tfm_node_id});
        }
        auto parent_ok =
            out_sceneGraph.set_node_parent(previous_node_id, tfm_node_id);
        MMSOLVER_CORE_UNUSED(parent_ok);
        previous_node_id = tfm_node_id;

        status = dag_path.pop();
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    return status;
}

MStatus add_cameras(const CameraPtrList &cameraList,
                    const MTimeArray &timeArray,
                    const mmsg::FrameValue start_frame,
                    const mmsg::FrameValue end_frame, const int timeEvalMode,
                    std::vector<mmsg::CameraNode> &out_cameraNodes,
                    mmsg::EvaluationObjects &out_evalObjects,
                    mmsg::SceneGraph &out_sceneGraph,
                    mmsg::AttrDataBlock &out_attrDataBlock,
                    StringToNodeIdMap &out_nodeNameToNodeIdMap,
                    StringToAttrIdMap &out_attrNameToAttrIdMap) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("add_cameras");
    MStatus status = MS::kSuccess;

    // Create a single attribute that will be re-used.
    auto mayaAttr = Attr();

    auto translate_attr_ids = mmsg::Translate3DAttrIds();
    auto rotate_attr_ids = mmsg::Rotate3DAttrIds();
    auto scale_attr_ids = mmsg::Scale3DAttrIds();
    auto camera_attr_ids = mmsg::CameraAttrIds();
    auto rotate_order = mmsg::RotateOrder::kUnknown;

    out_cameraNodes.clear();
    out_cameraNodes.reserve(cameraList.size());

    for (auto cit = cameraList.cbegin(); cit != cameraList.cend(); ++cit) {
        auto cam_ptr = *cit;
        auto cam_tfm_name = cam_ptr->getTransformNodeName();
        auto cam_shp_name = cam_ptr->getShapeNodeName();
        auto cam_tfm_obj = cam_ptr->getTransformObject();
        auto cam_shp_obj = cam_ptr->getShapeObject();
        auto tfm_dag_path = MDagPath();
        auto shp_dag_path = MDagPath();
        status = MDagPath::getAPathTo(cam_tfm_obj, tfm_dag_path);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

        MString transform_name = tfm_dag_path.fullPathName(&status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        status = mayaAttr.setNodeName(transform_name);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

        get_transform_attrs(mayaAttr, timeArray, start_frame, end_frame,
                            timeEvalMode, out_attrDataBlock, translate_attr_ids,
                            rotate_attr_ids, scale_attr_ids, rotate_order,
                            out_attrNameToAttrIdMap);

        status = MDagPath::getAPathTo(cam_shp_obj, shp_dag_path);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        MString shape_name = shp_dag_path.fullPathName(&status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        status = mayaAttr.setNodeName(shape_name);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

        auto film_fit = mmsg::FilmFit::kUnknown;
        auto render_image_width = 0;
        auto render_image_height = 0;
        get_camera_attrs(mayaAttr, cam_ptr, timeArray, start_frame, end_frame,
                         timeEvalMode, out_attrDataBlock, camera_attr_ids,
                         film_fit, render_image_width, render_image_height,
                         out_attrNameToAttrIdMap);

        auto cam_node = out_sceneGraph.create_camera_node(
            translate_attr_ids, rotate_attr_ids, scale_attr_ids,
            camera_attr_ids, rotate_order, film_fit, render_image_width,
            render_image_height);
        out_cameraNodes.push_back(cam_node);
        out_evalObjects.add_camera(cam_node);

        auto nodeNameStr = std::string(transform_name.asChar());
        out_nodeNameToNodeIdMap.insert({nodeNameStr, cam_node.id});

        status = tfm_dag_path.pop();
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

        status = add_transforms(
            cam_node.id, tfm_dag_path, timeArray, start_frame, end_frame,
            timeEvalMode, out_sceneGraph, out_attrDataBlock,
            out_nodeNameToNodeIdMap, out_attrNameToAttrIdMap);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }
    return status;
}

MStatus add_bundles(const BundlePtrList &bundleList,
                    const MTimeArray &timeArray,
                    const mmsg::FrameValue start_frame,
                    const mmsg::FrameValue end_frame, const int timeEvalMode,
                    std::vector<mmsg::BundleNode> &out_bundleNodes,
                    mmsg::EvaluationObjects &out_evalObjects,
                    mmsg::SceneGraph &out_sceneGraph,
                    mmsg::AttrDataBlock &out_attrDataBlock,
                    StringToNodeIdMap &out_nodeNameToNodeIdMap,
                    StringToAttrIdMap &out_attrNameToAttrIdMap) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("add_bundles");
    MStatus status = MS::kSuccess;

    // Create a single attribute that will be re-used.
    auto mayaAttr = Attr();

    auto translate_attr_ids = mmsg::Translate3DAttrIds();
    auto rotate_attr_ids = mmsg::Rotate3DAttrIds();
    auto scale_attr_ids = mmsg::Scale3DAttrIds();
    auto rotate_order = mmsg::RotateOrder::kUnknown;

    out_bundleNodes.clear();
    out_bundleNodes.reserve(bundleList.size());

    for (auto cit = bundleList.cbegin(); cit != bundleList.cend(); ++cit) {
        auto bnd_ptr = *cit;
        auto bnd_tfm_name = bnd_ptr->getNodeName();
        auto bnd_tfm_obj = bnd_ptr->getObject();

        auto dag_path = MDagPath();
        status = MDagPath::getAPathTo(bnd_tfm_obj, dag_path);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

        MString transform_name = dag_path.fullPathName(&status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        status = mayaAttr.setNodeName(transform_name);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

        get_transform_attrs(mayaAttr, timeArray, start_frame, end_frame,
                            timeEvalMode, out_attrDataBlock, translate_attr_ids,
                            rotate_attr_ids, scale_attr_ids, rotate_order,
                            out_attrNameToAttrIdMap);

        auto bnd_node = out_sceneGraph.create_bundle_node(
            translate_attr_ids, rotate_attr_ids, scale_attr_ids, rotate_order);
        out_bundleNodes.push_back(bnd_node);
        out_evalObjects.add_bundle(bnd_node);

        auto nodeNameStr = std::string(transform_name.asChar());
        out_nodeNameToNodeIdMap.insert({nodeNameStr, bnd_node.id});

        status = dag_path.pop();
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

        status = add_transforms(bnd_node.id, dag_path, timeArray, start_frame,
                                end_frame, timeEvalMode, out_sceneGraph,
                                out_attrDataBlock, out_nodeNameToNodeIdMap,
                                out_attrNameToAttrIdMap);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }
    return status;
}

MStatus add_markers(
    const MarkerList &markerList, const CameraPtrList &cameraList,
    const BundlePtrList &bundleList, const MTimeArray &timeArray,
    const mmsg::FrameValue start_frame, const mmsg::FrameValue end_frame,
    const int timeEvalMode, const std::vector<mmsg::CameraNode> &cameraNodes,
    const std::vector<mmsg::BundleNode> &bundleNodes,
    std::vector<mmsg::MarkerNode> &out_markerNodes,
    mmsg::EvaluationObjects &out_evalObjects, mmsg::SceneGraph &out_sceneGraph,
    mmsg::AttrDataBlock &out_attrDataBlock,
    StringToAttrIdMap &out_attrNameToAttrIdMap) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("add_markers");

    MStatus status = MS::kSuccess;
    MMSOLVER_ASSERT(cameraList.size() == cameraNodes.size(),
                    "Camera sizes must match MM Scene Graph.");
    MMSOLVER_ASSERT(bundleList.size() == bundleNodes.size(),
                    "Bundle sizes must match MM Scene Graph.");

    // Create a single attribute that will be re-used.
    auto mayaAttr = Attr();

    auto mkr_attr_ids = mmsg::MarkerAttrIds();

    out_markerNodes.clear();
    out_markerNodes.reserve(markerList.size());

    for (uint32_t i = 0; i < markerList.size(); ++i) {
        auto mkr_ptr = markerList.get_marker(i);
        auto mkr_tfm_name = mkr_ptr->getNodeName();
        auto mkr_tfm_obj = mkr_ptr->getObject();

        // Get camera name.
        auto mkr_cam_ptr = mkr_ptr->getCamera();
        auto mkr_cam_shp_name = mkr_cam_ptr->getShapeNodeName();

        mmsg::NodeId cam_node_id = mmsg::NodeId();
        for (uint32_t j = 0; j < cameraList.size(); ++j) {
            if (cameraList[j]->getShapeNodeName() == mkr_cam_shp_name) {
                cam_node_id = cameraNodes[j].id;
                break;
            }
        }

        // Get bundle name.
        auto mkr_bnd_ptr = mkr_ptr->getBundle();
        auto mkr_bnd_tfm_name = mkr_bnd_ptr->getNodeName();

        mmsg::NodeId bnd_node_id = mmsg::NodeId();
        for (uint32_t j = 0; j < bundleList.size(); ++j) {
            if (bundleList[j]->getNodeName() == mkr_bnd_tfm_name) {
                bnd_node_id = bundleNodes[j].id;
                break;
            }
        }

        auto dag_path = MDagPath();
        status = MDagPath::getAPathTo(mkr_tfm_obj, dag_path);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

        MString transform_name = dag_path.fullPathName(&status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        status = mayaAttr.setNodeName(transform_name);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

        // MarkerGroup's Overscan
        double overscan_x = 1.0;
        double overscan_y = 1.0;
        MarkerGroupPtr mkr_grp_ptr = mkr_ptr->getMarkerGroup();
        if (mkr_grp_ptr) {
            // Overscan is assumed to be static, animated overscan is
            // not current supported.
            auto first_time = timeArray[0];
            status = mkr_grp_ptr->getOverscanXY(overscan_x, overscan_y,
                                                first_time, timeEvalMode);
            MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        }

        status = get_marker_attrs(mayaAttr, timeArray, start_frame, end_frame,
                                  timeEvalMode, overscan_x, overscan_y,
                                  out_attrDataBlock, mkr_attr_ids,
                                  out_attrNameToAttrIdMap);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

        auto mkr_node = out_sceneGraph.create_marker_node(mkr_attr_ids);
        out_markerNodes.push_back(mkr_node);
        out_evalObjects.add_marker(mkr_node);

        // Create Marker to Bundle and Camera relationships.
        auto link_camera_ok =
            out_sceneGraph.link_marker_to_camera(mkr_node.id, cam_node_id);
        if (!link_camera_ok) {
            MMSOLVER_MAYA_WRN("add_markers: Cannot link marker to camera; "
                              << " mkr=" << mkr_node.id.index
                              << " cam=" << cam_node_id.index);
            status = MS::kFailure;
        }
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

        auto link_bundle_ok =
            out_sceneGraph.link_marker_to_bundle(mkr_node.id, bnd_node_id);
        if (!link_bundle_ok) {
            MMSOLVER_MAYA_WRN("add_markers: Cannot link marker to bundle; "
                              << " mkr=" << mkr_node.id.index
                              << " bnd=" << bnd_node_id.index);
            status = MS::kFailure;
        }
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }
    return status;
}

MStatus convert_attributes_to_attr_ids(
    const AttrList &attrList, const StringToAttrIdMap &attrNameToAttrIdMap,
    std::vector<mmsg::AttrId> &out_attrIdList) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("convert_attributes_to_attr_ids");

    MStatus status = MS::kSuccess;

    out_attrIdList.clear();
    out_attrIdList.reserve(attrList.size());

    for (AttrIndex attrIndex = 0; attrIndex < attrList.size(); ++attrIndex) {
        AttrPtr attr = attrList.get_attr(attrIndex);

        ObjectType object_type = attr->getObjectType();
        if (object_type == ObjectType::kLens) {
            // Lens objects are not supported by mmSceneGraph.
            auto emptyAttrId = mmsg::AttrId();
            emptyAttrId.attr_type =
                mmsg::AttrType::kNone;  // Do not set any attribute.
            emptyAttrId.index = 0;
            out_attrIdList.push_back(emptyAttrId);
            continue;
        }

        MString attrName = attr->getLongName();
        std::string key = std::string(attrName.asChar());

        // Find mmSceneGraph AttrId from the full (long) attribute
        // name.
        auto search = attrNameToAttrIdMap.find(key);
        if (search != attrNameToAttrIdMap.end()) {
            out_attrIdList.push_back(search->second);
        } else {
            MMSOLVER_MAYA_WRN("MM Scene Graph: Attribute name was not found: "
                              << key << " object_type="
                              << static_cast<uint32_t>(object_type));
            return MS::kFailure;
        }
    }
    MMSOLVER_ASSERT(out_attrIdList.size() == attrList.size(),
                    "Attribute sizes must match MM Scene Graph.");
    return status;
}

MStatus construct_scene_graph(
    const CameraPtrList &cameraList, const MarkerList &markerList,
    const BundlePtrList &bundleList, const AttrList &attrList,
    const FrameList &frameList, const int timeEvalMode,
    mmsg::SceneGraph &out_sceneGraph, mmsg::AttrDataBlock &out_attrDataBlock,
    mmsg::FlatScene &out_flatScene,
    std::vector<mmsg::FrameValue> &out_frameList,
    std::vector<mmsg::CameraNode> &out_cameraNodes,
    std::vector<mmsg::BundleNode> &out_bundleNodes,
    std::vector<mmsg::MarkerNode> &out_markerNodes,
    std::vector<mmsg::AttrId> &out_attrIdList) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB(
        "construct_scene_graph -----------------------------------");

    auto evalObjects = mmsg::EvaluationObjects();
    auto attrNameToAttrIdMap = StringToAttrIdMap();
    auto nodeNameToNodeIdMap = StringToNodeIdMap();

    // Check Frames
    const uint32_t frameListEnabledCount = frameList.count_enabled();
    MMSOLVER_MAYA_VRB("FrameList length: " << frameList.size());
    MMSOLVER_MAYA_VRB("FrameList enabled count: " << frameListEnabledCount);
    MMSOLVER_ASSERT(!frameList.is_empty(),
                    "MM Scene Graph must be evaluated on some frames.");
    MMSOLVER_ASSERT(frameListEnabledCount > 0,
                    "MM Scene Graph must be evaluated on some valid frames.");

    // Frames
    mmsg::FrameValue start_frame = std::numeric_limits<mmsg::FrameValue>::max();
    mmsg::FrameValue end_frame = std::numeric_limits<mmsg::FrameValue>::min();
    for (auto i = 0; i < frameList.size(); ++i) {
        const bool frame_enabled = frameList.get_enabled(i);
        if (!frame_enabled) {
            continue;
        }

        const FrameNumber frame_num = frameList.get_frame(i);
        MMSOLVER_MAYA_VRB("frameList i=" << i << " frame_num=" << frame_num);
        start_frame = std::min<mmsg::FrameValue>(start_frame, frame_num);
        end_frame = std::max<mmsg::FrameValue>(end_frame, frame_num);
        out_frameList.push_back(frame_num);
    }
    auto total_frame_count = (end_frame - start_frame) + 1;
    MMSOLVER_CORE_UNUSED(total_frame_count);
    MMSOLVER_MAYA_VRB("Frames start_frame: " << start_frame);
    MMSOLVER_MAYA_VRB("Frames end_frame: " << end_frame);
    MMSOLVER_MAYA_VRB("Frames frame_count: " << total_frame_count);
    MMSOLVER_MAYA_VRB("Frames count: " << out_frameList.size());
    MMSOLVER_ASSERT(out_frameList.size() == frameList.count_enabled(),
                    "Frame count must match MM Scene Graph.");

    const MTimeArray timeArray = mmsolver::create_time_array_enabled(frameList);
    MMSOLVER_ASSERT(timeArray.length() == frameList.count_enabled(),
                    "Frame count must match MM Scene Graph.");

    MStatus status = add_cameras(cameraList, timeArray, start_frame, end_frame,
                                 timeEvalMode, out_cameraNodes, evalObjects,
                                 out_sceneGraph, out_attrDataBlock,
                                 nodeNameToNodeIdMap, attrNameToAttrIdMap);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    status = add_bundles(bundleList, timeArray, start_frame, end_frame,
                         timeEvalMode, out_bundleNodes, evalObjects,
                         out_sceneGraph, out_attrDataBlock, nodeNameToNodeIdMap,
                         attrNameToAttrIdMap);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    status = add_markers(
        markerList, cameraList, bundleList, timeArray, start_frame, end_frame,
        timeEvalMode, out_cameraNodes, out_bundleNodes, out_markerNodes,
        evalObjects, out_sceneGraph, out_attrDataBlock, attrNameToAttrIdMap);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    // Create parameters to attributes
    status = convert_attributes_to_attr_ids(attrList, attrNameToAttrIdMap,
                                            out_attrIdList);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    // Print number of nodes in the evaluation objects.
    MMSOLVER_MAYA_VRB(
        "EvaluationObjects num_bundles: " << evalObjects.num_bundles());
    MMSOLVER_MAYA_VRB(
        "EvaluationObjects num_cameras: " << evalObjects.num_cameras());
    MMSOLVER_MAYA_VRB(
        "EvaluationObjects num_markers: " << evalObjects.num_markers());

    // Print number of nodes in the scene graph.
    MMSOLVER_MAYA_VRB("SceneGraph num_transform_nodes: "
                      << out_sceneGraph.num_transform_nodes());
    MMSOLVER_MAYA_VRB(
        "SceneGraph num_bundle_nodes: " << out_sceneGraph.num_bundle_nodes());
    MMSOLVER_MAYA_VRB(
        "SceneGraph num_camera_nodes: " << out_sceneGraph.num_camera_nodes());
    MMSOLVER_MAYA_VRB(
        "SceneGraph num_marker_nodes: " << out_sceneGraph.num_marker_nodes());

    // Bake down SceneGraph into FlatScene for fast evaluation.
    out_flatScene = mmsg::bake_scene_graph(out_sceneGraph, evalObjects);

    return status;
}

}  // namespace mmsolver
