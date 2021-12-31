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

class FlatScene {
public:

    MMSCENEGRAPH_API_EXPORT
    FlatScene(rust::Box<ShimFlatScene> flat_scene) noexcept;

private:
    rust::Box<ShimFlatScene> inner_;
};

} // namespace mmscenegraph
