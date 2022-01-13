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

class EvaluationObjects {
public:

    MMSCENEGRAPH_API_EXPORT
    EvaluationObjects() noexcept;

    MMSCENEGRAPH_API_EXPORT
    rust::Box<ShimEvaluationObjects> get_inner() noexcept;

    MMSCENEGRAPH_API_EXPORT
    size_t num_bundles() const noexcept;

    MMSCENEGRAPH_API_EXPORT
    size_t num_cameras() const noexcept;

    MMSCENEGRAPH_API_EXPORT
    size_t num_markers() const noexcept;

    MMSCENEGRAPH_API_EXPORT
    void clear_all() noexcept;

    MMSCENEGRAPH_API_EXPORT
    void clear_bundles() noexcept;

    MMSCENEGRAPH_API_EXPORT
    void clear_cameras() noexcept;

    MMSCENEGRAPH_API_EXPORT
    void clear_markers() noexcept;

    MMSCENEGRAPH_API_EXPORT
    void add_bundle(BundleNode &bnd_node) noexcept;

    MMSCENEGRAPH_API_EXPORT
    void add_camera(CameraNode &cam_node) noexcept;

    MMSCENEGRAPH_API_EXPORT
    void add_marker(MarkerNode &mkr_node) noexcept;

private:
    rust::Box<ShimEvaluationObjects> inner_;
};

} // namespace mmscenegraph
