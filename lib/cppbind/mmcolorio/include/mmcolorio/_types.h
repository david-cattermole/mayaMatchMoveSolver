/*
 * Copyright (C) 2024 David Cattermole.
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

#include <iostream>

namespace mmcolorio {

enum class ColorSpaceVisibility : uint8_t {
    kActive = 0,
    kInactive,
    kAll,

    // Must be second to last entry. Used to calculate the full list
    // of entries.
    kCount,

    // Must be last entry.
    kUnknown = 255,
};

enum class ColorSpaceRole : uint8_t {
    kDefault = 0,
    kReference,
    kData,
    kColorPicking,
    kSceneLinear,
    kCompositingLog,
    kColorTiming,
    kTexturePaint,
    kMattePaint,
    kRendering,
    kInterchangeScene,
    kInterchangeDisplay,

    // Must be second to last entry. Used to calculate the full list
    // of entries.
    kCount,

    // Must be last entry.
    kUnknown = 255,
};

}  // namespace mmcolorio
