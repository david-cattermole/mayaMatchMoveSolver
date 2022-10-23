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

#include <mmscenegraph/evaluationobjects.h>

#include <iostream>
#include <string>

namespace mmscenegraph {

EvaluationObjects::EvaluationObjects() noexcept
    : inner_(shim_create_evaluation_objects_box()) {}

rust::Box<ShimEvaluationObjects> EvaluationObjects::get_inner() noexcept {
    return std::move(inner_);
}

void EvaluationObjects::clear_all() noexcept { return inner_->clear_all(); }

void EvaluationObjects::clear_bundles() noexcept {
    return inner_->clear_bundles();
}

void EvaluationObjects::clear_cameras() noexcept {
    return inner_->clear_cameras();
}

void EvaluationObjects::clear_markers() noexcept {
    return inner_->clear_markers();
}

size_t EvaluationObjects::num_bundles() const noexcept {
    return inner_->num_bundles();
}

size_t EvaluationObjects::num_cameras() const noexcept {
    return inner_->num_cameras();
}

size_t EvaluationObjects::num_markers() const noexcept {
    return inner_->num_markers();
}

void EvaluationObjects::add_bundle(BundleNode &bnd_node) noexcept {
    return inner_->add_bundle(bnd_node);
}

void EvaluationObjects::add_camera(CameraNode &cam_node) noexcept {
    return inner_->add_camera(cam_node);
}

void EvaluationObjects::add_marker(MarkerNode &mkr_node) noexcept {
    return inner_->add_marker(mkr_node);
}

}  // namespace mmscenegraph
