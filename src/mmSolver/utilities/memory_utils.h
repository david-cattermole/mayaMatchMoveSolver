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
 * Memory-related utilities.
 */

#ifndef MEMORY_UTILS_H
#define MEMORY_UTILS_H

// STL
#include <cstdint>
#include <cstddef>

namespace mmmemory {

enum class MemoryUnit : uint8_t {
    kBytes = 0,
    kKiloBytes,
    kMegaBytes,
    kGigaBytes,
};

double bytes_as_double(const size_t size_as_bytes,
                       const mmmemory::MemoryUnit memory_unit);

}  // namespace mmmemory

#endif  // MEMORY_UTILS_H
