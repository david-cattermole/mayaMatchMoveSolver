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
#include <mmscenegraph/flatscene.h>

namespace mmscenegraph {

FlatScene::FlatScene(rust::Box<ShimFlatScene> flat_scene) noexcept
        : inner_(std::move(flat_scene)) {
}

rust::Slice<const Real>
FlatScene::points() const noexcept {
    return inner_->points();
}

rust::Slice<const Real>
FlatScene::deviations() const noexcept {
    return inner_->deviations();
}

size_t
FlatScene::num_points() const noexcept {
    return inner_->num_points();
}

size_t
FlatScene::num_deviations() const noexcept {
    return inner_->num_deviations();
}

void
FlatScene::evaluate(
        AttrDataBlock &attrdb,
        std::vector<FrameValue> &frames
) noexcept {
    auto attrdb_inner = attrdb.get_inner();
    rust::Slice<const FrameValue> frames_slice{frames.data(), frames.size()};
    return inner_->evaluate(attrdb_inner, frames_slice);
}

} // namespace mmscenegraph
