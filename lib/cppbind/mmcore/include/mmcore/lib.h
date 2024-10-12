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

#ifndef MM_CORE_LIB_H
#define MM_CORE_LIB_H

#include <memory>
#include <string>

#include "_cxx.h"
#include "_cxxbridge.h"
#include "_symbol_export.h"
#include "_types.h"
#include "mmcamera.h"
#include "mmcoord.h"
#include "mmcore.h"
#include "mmdata.h"
#include "mmhash.h"
#include "mmmath.h"

namespace mmcore {

rust::String expand_file_path_string(const rust::Str& value, FrameValue frame);

}  // namespace mmcore

#endif  // MM_CORE_LIB_H
