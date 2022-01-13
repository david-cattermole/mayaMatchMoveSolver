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
#include "_types.h"

namespace mmscenegraph {

class AttrDataBlock {
public:

    MMSCENEGRAPH_API_EXPORT
    AttrDataBlock() noexcept;

    MMSCENEGRAPH_API_EXPORT
    rust::Box<ShimAttrDataBlock>
    get_inner() noexcept;

    MMSCENEGRAPH_API_EXPORT
    void
    set_inner(rust::Box<ShimAttrDataBlock> &value) noexcept;

    MMSCENEGRAPH_API_EXPORT
    void clear() noexcept;

    MMSCENEGRAPH_API_EXPORT
    size_t num_attr_static() noexcept;

    MMSCENEGRAPH_API_EXPORT
    size_t num_attr_anim_dense() noexcept;

    MMSCENEGRAPH_API_EXPORT
    AttrId create_attr_static(Real value) noexcept;

    MMSCENEGRAPH_API_EXPORT
    AttrId
    create_attr_anim_dense(
        rust::Vec<Real> values,
        FrameValue frame_start
    ) noexcept;

    MMSCENEGRAPH_API_EXPORT
    Real
    get_attr_value(
        AttrId attr_id,
        FrameValue frame
    ) const noexcept;

    MMSCENEGRAPH_API_EXPORT
    void
    set_attr_value(
        AttrId attr_id,
        FrameValue frame,
        Real value
    ) noexcept;

private:
    rust::Box<ShimAttrDataBlock> inner_;
};

} // namespace mmscenegraph
