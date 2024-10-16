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

#ifndef MM_SOLVER_MM_SCENE_GRAPH_FLAT_SCENE_H
#define MM_SOLVER_MM_SCENE_GRAPH_FLAT_SCENE_H

#include <mmscenegraph/attrdatablock.h>

#include <vector>

#include "_cxx.h"
#include "_cxxbridge.h"
#include "_symbol_export.h"
#include "_types.h"

namespace mmscenegraph {

class FlatScene {
public:
    MMSCENEGRAPH_API_EXPORT
    FlatScene() noexcept;

    MMSCENEGRAPH_API_EXPORT
    explicit FlatScene(rust::Box<ShimFlatScene> flat_scene) noexcept;

    MMSCENEGRAPH_API_EXPORT
    rust::Slice<const Real> markers() const noexcept;

    MMSCENEGRAPH_API_EXPORT
    rust::Slice<const Real> points() const noexcept;

    MMSCENEGRAPH_API_EXPORT
    size_t num_markers() const noexcept;

    MMSCENEGRAPH_API_EXPORT
    size_t num_points() const noexcept;

    MMSCENEGRAPH_API_EXPORT
    void evaluate(AttrDataBlock &attrDataBlock,
                  std::vector<FrameValue> &frames) noexcept;

private:
    rust::Box<ShimFlatScene> inner_;
};

}  // namespace mmscenegraph

#endif  // MM_SOLVER_MM_SCENE_GRAPH_FLAT_SCENE_H
