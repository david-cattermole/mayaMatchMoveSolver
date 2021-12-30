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

#pragma once

#include <memory>
#include <string>

#include "_cxx.h"
#include "_cxxbridge.h"
#include "_symbol_export.h"

namespace mmscenegraph {

class SceneGraph {
public:

    MMSCENEGRAPH_API_EXPORT
    SceneGraph() noexcept;

    MMSCENEGRAPH_API_EXPORT
    void clear() noexcept;

    MMSCENEGRAPH_API_EXPORT
    size_t
    num_transform_nodes() const noexcept;

    MMSCENEGRAPH_API_EXPORT
    size_t
    num_bundle_nodes() const noexcept;

    MMSCENEGRAPH_API_EXPORT
    size_t
    num_camera_nodes() const noexcept;

    MMSCENEGRAPH_API_EXPORT
    size_t
    num_marker_nodes() const noexcept;

    MMSCENEGRAPH_API_EXPORT
    TransformNode
    create_transform_node(
        Translate3DAttrIds translate_attrs,
        Rotate3DAttrIds rotate_attrs,
        Scale3DAttrIds scale_attrs,
        RotateOrder rotate_order) noexcept;

    MMSCENEGRAPH_API_EXPORT
    BundleNode
    create_bundle_node(
        Translate3DAttrIds translate_attrs,
        Rotate3DAttrIds rotate_attrs,
        Scale3DAttrIds scale_attrs,
        RotateOrder rotate_order) noexcept;

    MMSCENEGRAPH_API_EXPORT
    CameraNode
    create_camera_node(
        Translate3DAttrIds translate_attrs,
        Rotate3DAttrIds rotate_attrs,
        Scale3DAttrIds scale_attrs,
        CameraAttrIds camera_attrs,
        RotateOrder rotate_order) noexcept;

    MMSCENEGRAPH_API_EXPORT
    MarkerNode
    create_marker_node(MarkerAttrIds marker_attrs) noexcept;

    MMSCENEGRAPH_API_EXPORT
    bool
    link_marker_to_camera(NodeId mkr_node_id, NodeId cam_node_id) noexcept;

    MMSCENEGRAPH_API_EXPORT
    bool
    link_marker_to_bundle(NodeId mkr_node_id, NodeId bnd_node_id) noexcept;
    
private:
    rust::Box<ShimSceneGraph> inner_;
};

} // namespace mmscenegraph
