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

#include <iostream>
#include <string>
#include <mmscenegraph/scenegraph.h>

namespace mmscenegraph {

SceneGraph::SceneGraph() noexcept
        : inner_(shim_create_scene_graph_box()) {
    std::cout << "SceneGraph()" << '\n';
}

void
SceneGraph::clear() noexcept {
    return inner_->clear();
}

size_t
SceneGraph::num_transform_nodes() const noexcept {
    return inner_->num_transform_nodes();
}

size_t
SceneGraph::num_bundle_nodes() const noexcept {
    return inner_->num_bundle_nodes();
}

size_t
SceneGraph::num_camera_nodes() const noexcept {
    return inner_->num_camera_nodes();
}

size_t
SceneGraph::num_marker_nodes() const noexcept {
    return inner_->num_marker_nodes();
}

TransformNode
SceneGraph::create_transform_node(
        Translate3DAttrIds translate_attrs,
        Rotate3DAttrIds rotate_attrs,
        Scale3DAttrIds scale_attrs,
        RotateOrder rotate_order) noexcept {
    return inner_->create_transform_node(
        translate_attrs,
        rotate_attrs,
        scale_attrs,
        rotate_order);
}

BundleNode
SceneGraph::create_bundle_node(
        Translate3DAttrIds translate_attrs,
        Rotate3DAttrIds rotate_attrs,
        Scale3DAttrIds scale_attrs,
        RotateOrder rotate_order) noexcept {
    return inner_->create_bundle_node(
        translate_attrs,
        rotate_attrs,
        scale_attrs,
        rotate_order);
}

CameraNode
SceneGraph::create_camera_node(
        Translate3DAttrIds translate_attrs,
        Rotate3DAttrIds rotate_attrs,
        Scale3DAttrIds scale_attrs,
        CameraAttrIds camera_attrs,
        RotateOrder rotate_order) noexcept {
    return inner_->create_camera_node(
        translate_attrs,
        rotate_attrs,
        scale_attrs,
        camera_attrs,
        rotate_order);
}

MarkerNode
SceneGraph::create_marker_node(
        MarkerAttrIds marker_attrs) noexcept {
    return inner_->create_marker_node(marker_attrs);
}

} // namespace mmscenegraph
