/*
 * Copyright (C) 2023 David Cattermole.
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

#include "scene_utils.h"

// Maya
#include <maya/M3dView.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MItDag.h>
#include <maya/MItDependencyNodes.h>
#include <maya/MIteratorType.h>
#include <maya/MPlug.h>
#include <maya/MPlugArray.h>
#include <maya/MRenderTargetManager.h>
#include <maya/MSelectionList.h>
#include <maya/MShaderManager.h>
#include <maya/MStateManager.h>
#include <maya/MString.h>
#include <maya/MViewport2Renderer.h>

// MM Solver
#include "mmSolver/mayahelper/maya_utils.h"

namespace mmsolver {
namespace render {

// Test if a node is an image plane.
MString get_dependency_node_classification(MFnDependencyNode& depend_fn) {
    const bool verbose = false;
    MStatus status = MS::kSuccess;
    MString node_type_name = depend_fn.typeName(&status);
    if (status != MS::kSuccess) {
        MMSOLVER_MAYA_VRB(
            "NodeManager::dependency_node_is_geometry: failed to get type "
            "name for node \""
            << depend_fn.absoluteName().asChar() << "\".");
        return MString();
    }
    MString node_type_classification =
        MFnDependencyNode::classification(node_type_name);
    return node_type_classification;
}

bool node_classification_is_geometry(const MString& node_type_classification) {
    const MString accepted_token("drawdb/geometry");
    int32_t result = node_type_classification.indexW(accepted_token);
    return result != -1;
}

bool node_classification_is_image_plane(
    const MString& node_type_classification) {
    const MString accepted_token("drawdb/geometry/mmSolver/imagePlane");
    int32_t result = node_type_classification.indexW(accepted_token);
    return result != -1;
}

MStatus add_all_image_planes(MSelectionList& out_selection_list) {
    MStatus status = MS::kSuccess;
    const bool verbose = false;

    MIntArray filterTypes;
    filterTypes.append(static_cast<int32_t>(MFn::kCamera));
    filterTypes.append(static_cast<int32_t>(MFn::kImagePlane));
    filterTypes.append(static_cast<int32_t>(MFn::kPluginShape));
    filterTypes.append(static_cast<int32_t>(MFn::kPluginLocatorNode));
    filterTypes.append(static_cast<int32_t>(MFn::kPluginImagePlaneNode));

    MIteratorType infoObject;
    infoObject.setObjectType(MIteratorType::kMObject);
    infoObject.setFilterList(filterTypes, &status);

    // NOTE: MItDag does not seem to support 'underworld' DAG paths
    // such as Maya imagePlane nodes.
    MObject node;
    MDagPath dagPath;
    MItDag it(infoObject);
    for (; !it.isDone(); it.next()) {
        status = it.getPath(dagPath);
        CHECK_MSTATUS(status);
        if (status != MS::kSuccess) {
            continue;
        }
        if (!dagPath.isValid()) {
            continue;
        }

        MMSOLVER_MAYA_VRB(
            "add_all_image_planes: "
            "node=\""
            << dagPath.fullPathName().asChar() << "\" is being considered.");

        bool ok = false;
        if (dagPath.hasFn(MFn::kCamera) || dagPath.hasFn(MFn::kImagePlane) ||
            dagPath.hasFn(MFn::kPluginImagePlaneNode)) {
            // By definition these must be image planes, so we don't need
            // to check any further.
            MMSOLVER_MAYA_VRB(
                "add_all_image_planes: "
                "node=\""
                << dagPath.fullPathName().asChar()
                << "\" has MFn::kCamera, MFn::kImagePlane or "
                   "MFn::kPluginImagePlaneNode.");
            ok = true;
        } else {
            // Check to see if the DAG path has a "magic string" node
            // classification so we treat it as an image plane.
            node = dagPath.node();
            MFnDependencyNode depend_fn(node);
            const MString node_classification =
                get_dependency_node_classification(depend_fn);
            if (node_classification_is_image_plane(node_classification)) {
                MMSOLVER_MAYA_VRB(
                    "add_all_image_planes: "
                    "node=\""
                    << dagPath.fullPathName().asChar()
                    << "\" has draw classification.");
                ok = true;
            }
        }

        if (ok) {
            MDagPath shapeDagPath(dagPath);
            out_selection_list.add(shapeDagPath);
        }
    }

    if (verbose) {
        MStatus status = MS::kSuccess;
        MDagPath dag_path;
        for (int i = 0; i < out_selection_list.length(); i++) {
            status = out_selection_list.getDagPath(i, dag_path);
            if (status == MS::kSuccess) {
                MMSOLVER_MAYA_VRB(
                    "add_all_image_planes: "
                    "i="
                    << i << " node=\"" << dag_path.fullPathName().asChar()
                    << "\".");
            }
        }
    }

    return MS::kSuccess;
}

MStatus only_named_layer_objects(MObject& layer_node,
                                 MSelectionList& out_selection_list) {
    const bool verbose = false;
    MStatus status = MS::kSuccess;

    MFnDependencyNode layer_depends_fn(layer_node, &status);
    CHECK_MSTATUS(status);
    MMSOLVER_MAYA_VRB("only_named_layer_objects: layer: "
                      << layer_depends_fn.name().asChar());

    const bool want_networked_plug = true;

    // Get connection from layer to objects;
    // 'DisplayLayer.drawInfo' -> 'Transform.drawOverrides'.
    MPlug draw_info_plug =
        layer_depends_fn.findPlug("drawInfo", want_networked_plug, &status);
    CHECK_MSTATUS(status);

    if (status != MStatus::kSuccess || draw_info_plug.isNull()) {
        return status;
    }

    MPlugArray destination_plugs;
    draw_info_plug.destinations(destination_plugs, &status);
    MMSOLVER_MAYA_VRB(
        "only_named_layer_objects: count: " << destination_plugs.length());

    MDagPath dag_path;
    for (auto i = 0; i < destination_plugs.length(); ++i) {
        if (destination_plugs[i].isNull()) {
            continue;
        }

        MObject destination_node = destination_plugs[i].node();

        if (!destination_node.hasFn(MFn::kTransform) &&
            !destination_node.hasFn(MFn::kMesh) &&
            !destination_node.hasFn(MFn::kNurbsSurface) &&
            !destination_node.hasFn(MFn::kShape) &&
            !destination_node.hasFn(MFn::kPluginLocatorNode) &&
            !destination_node.hasFn(MFn::kPluginShape)) {
            if (verbose) {
                MFnDependencyNode depend_fn(destination_node);
                MMSOLVER_MAYA_VRB("only_named_layer_objects: discard node: i = "
                                  << i << " - "
                                  << depend_fn.absoluteName().asChar());
            }
            continue;
        }

        MFnDependencyNode depend_fn(destination_node);
        MMSOLVER_MAYA_VRB("only_named_layer_objects: accept node: i = "
                          << i << " - " << depend_fn.absoluteName().asChar());

        const MString node_classification =
            get_dependency_node_classification(depend_fn);

        if (node_classification_is_image_plane(node_classification)) {
            continue;
        }
        if (!node_classification_is_geometry(node_classification)) {
            continue;
        }
        out_selection_list.add(destination_node);

        status = MDagPath::getAPathTo(destination_node, dag_path);
        if (status == MStatus::kSuccess) {
            unsigned int shape_count = 0;
            status = dag_path.numberOfShapesDirectlyBelow(shape_count);
            for (auto j = 0; j < shape_count; ++j) {
                MDagPath shape_path(dag_path);
                shape_path.extendToShapeDirectlyBelow(j);

                MMSOLVER_MAYA_VRB("only_named_layer_objects: shape_node: i="
                                  << i << " j=" << j << " - "
                                  << shape_path.fullPathName().asChar());

                out_selection_list.add(shape_path);
            }
        }
    }
    return status;
}

const MSelectionList* find_draw_objects(const DrawObjects draw_objects,
                                        const MString& layer_name,
                                        MSelectionList& out_selection_list) {
    const bool verbose = false;

    out_selection_list.clear();

    if (draw_objects == DrawObjects::kOnlyNamedLayerObjects) {
        // Get the objects from the given display layer node.
        MObject layer_node;
        MStatus status = getAsObject(layer_name, layer_node);
        CHECK_MSTATUS(status);
        if ((status != MS::kSuccess) || layer_node.isNull()) {
            return nullptr;
        }

        MFnDependencyNode layer_depends_fn(layer_node, &status);
        CHECK_MSTATUS(status);
        MMSOLVER_MAYA_VRB(
            "find_draw_objects::layer: " << layer_depends_fn.name().asChar());

        const bool want_networked_plug = true;

        // Get connection from layer to objects;
        // 'DisplayLater.drawInfo' -> 'Transform.drawOverrides'.
        MPlug draw_info_plug =
            layer_depends_fn.findPlug("drawInfo", want_networked_plug, &status);
        CHECK_MSTATUS(status);
        if (status == MStatus::kSuccess && !draw_info_plug.isNull()) {
            MPlugArray destination_plugs;
            draw_info_plug.destinations(destination_plugs, &status);
            MMSOLVER_MAYA_VRB(
                "find_draw_objects::count: " << destination_plugs.length());

            for (auto i = 0; i < destination_plugs.length(); ++i) {
                if (destination_plugs[i].isNull()) {
                    continue;
                }
                MObject destination_node = destination_plugs[i].node();

                MDagPath dag_path;
                status = MDagPath::getAPathTo(destination_node, dag_path);
                if (status == MStatus::kSuccess) {
                    if ((dag_path.apiType() == MFn::kShape) ||
                        (dag_path.apiType() == MFn::kPluginLocatorNode) ||
                        (dag_path.apiType() == MFn::kPluginShape)) {
                        MMSOLVER_MAYA_VRB("find_draw_objects::node: i = "
                                          << i << " - "
                                          << dag_path.fullPathName().asChar());
                        out_selection_list.add(dag_path);
                    }

                    unsigned int shape_count = 0;
                    status = dag_path.numberOfShapesDirectlyBelow(shape_count);
                    for (auto j = 0; j < shape_count; ++j) {
                        MDagPath shape_path(dag_path);
                        shape_path.extendToShapeDirectlyBelow(j);

                        MMSOLVER_MAYA_VRB(
                            "find_draw_objects::shape_node: i="
                            << i << " j=" << j << " - "
                            << shape_path.fullPathName().asChar());

                        out_selection_list.add(shape_path);
                    }
                }
            }
        }

        return &out_selection_list;
    } else if (draw_objects == DrawObjects::kNoOverride) {
        return nullptr;
    } else if (draw_objects == DrawObjects::kOnlyCameraBackgroundImagePlanes) {
        // override drawn objects to only image planes under cameras.
        MItDag it;
        it.traverseUnderWorld(true);
        for (it.reset(); !it.isDone(); it.next()) {
            auto item = it.currentItem();
            if (item.hasFn(MFn::kImagePlane)) {
                MDagPath path;
                it.getPath(path);
                if (path.pathCount() < 2) {
                    continue;
                }
                out_selection_list.add(path);
            } else if ((item.apiType() == MFn::kPluginLocatorNode) ||
                       (item.apiType() == MFn::kPluginShape)) {
                MDagPath path;
                it.getPath(path);
                out_selection_list.add(path);
            }
        }
        return &out_selection_list;
    } else if (draw_objects == DrawObjects::kAllImagePlanes) {
        // override drawn objects to all image planes not under cameras.
        MItDag it;
        it.traverseUnderWorld(false);
        for (it.reset(); !it.isDone(); it.next()) {
            auto item = it.currentItem();
            if (item.hasFn(MFn::kImagePlane) ||
                (item.apiType() == MFn::kPluginLocatorNode) ||
                (item.apiType() == MFn::kPluginShape)) {
                MDagPath path;
                it.getPath(path);
                out_selection_list.add(path);
            }
        }
        return &out_selection_list;
    }
    return nullptr;
}

bool set_background_clear_operation(
    const BackgroundStyle background_style, const uint32_t clear_mask,
    MHWRender::MClearOperation& out_clear_operation) {
    if (background_style == BackgroundStyle::kTransparentBlack) {
        float val[4] = {0.0f, 0.0f, 0.0f, 0.0f};
        out_clear_operation.setOverridesColors(false);
        out_clear_operation.setClearColor(val);
        out_clear_operation.setClearColor2(val);
        out_clear_operation.setClearGradient(true);
        out_clear_operation.setClearStencil(0);
        // A depth value of 1.0f represents the 'most distant'
        // object. As objects draw, they draw darker pixels on top of
        // this background color.
        out_clear_operation.setClearDepth(1.0f);
    } else if (background_style == BackgroundStyle::kMayaDefault) {
        // This is the default settings that come from the user's
        // preferences. MRenderer provides us a way to get these
        // values automatically.
        MHWRender::MRenderer* renderer = MHWRender::MRenderer::theRenderer();
        const bool gradient = renderer->useGradient();
        const MColor color1 = renderer->clearColor();
        const MColor color2 = renderer->clearColor2();

        float val1[4] = {color1[0], color1[1], color1[2], 1.0f};
        float val2[4] = {color2[0], color2[1], color2[2], 1.0f};

        out_clear_operation.setOverridesColors(true);
        out_clear_operation.setClearColor(val1);
        out_clear_operation.setClearColor2(val2);
        // NOTE: The gradient is forced to enabled because
        // MRenderer::useGradient() appears to return zero when
        // playblasting, but correctly returns values when rendering
        // in the interactive Maya viewport. If we force the clear
        // gradient enabled, the 'clearColor's will be set to solid
        // colours when a non-gradient is waned.
        out_clear_operation.setClearGradient(true);
        out_clear_operation.setClearStencil(0);
        out_clear_operation.setClearDepth(1.0f);
    } else {
        MMSOLVER_MAYA_ERR(
            "set_background_clear_operation: Background style is invalid: "
            << static_cast<short>(background_style));
    }

    out_clear_operation.setMask(clear_mask);

    return true;
}

}  // namespace render
}  // namespace mmsolver
