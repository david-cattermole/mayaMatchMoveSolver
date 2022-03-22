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
#include <mmscenegraph/attrdatablock.h>


namespace mmscenegraph {

AttrDataBlock::AttrDataBlock() noexcept
        : inner_(shim_create_attr_data_block_box()) {
}

rust::Box<ShimAttrDataBlock>
AttrDataBlock::get_inner() noexcept {
    return std::move(inner_);
}

void
AttrDataBlock::set_inner(rust::Box<ShimAttrDataBlock> &value) noexcept {
    inner_ = std::move(value);
    return;
}

void
AttrDataBlock::clear() noexcept {
    return inner_->clear();
}

size_t
AttrDataBlock::num_attr_static() noexcept {
    return inner_->num_attr_static();
}

size_t
AttrDataBlock::num_attr_anim_dense() noexcept {
    return inner_->num_attr_anim_dense();
}

AttrId
AttrDataBlock::create_attr_static(Real value) noexcept {
    return inner_->create_attr_static(value);
}

AttrId
AttrDataBlock::create_attr_anim_dense(
        rust::Vec<Real> values,
        FrameValue frame_start
) noexcept {
    return inner_->create_attr_anim_dense(values, frame_start);
}

Real
AttrDataBlock::get_attr_value(
        AttrId attr_id,
        FrameValue frame
) const noexcept {
    return inner_->get_attr_value(attr_id, frame);
}

bool
AttrDataBlock::set_attr_value(
        AttrId attr_id,
        FrameValue frame,
        Real value
) noexcept {
    return inner_->set_attr_value(attr_id, frame, value);
}

} // namespace mmscenegraph
