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

#include "memory_utils.h"

// MM Solver
#include "debug_utils.h"
#include "number_utils.h"

namespace mmmemory {

double bytes_as_double(const size_t size_as_bytes,
                       const mmmemory::MemoryUnit memory_unit) {
    // NOTE: This essentially downcasts to a a 52-bit integer here,
    // so in theory we could loose precision.
    double result = static_cast<double>(size_as_bytes);
    if (memory_unit == mmmemory::MemoryUnit::kBytes) {
        MMSOLVER_MAYA_WRN(
            "mmmemory::bytes_as_double: "
            "Casting bytes to a 'double' value may not maintain precision.");
    } else if (memory_unit == mmmemory::MemoryUnit::kKiloBytes) {
        result /= BYTES_TO_KILOBYTES;
    } else if (memory_unit == mmmemory::MemoryUnit::kMegaBytes) {
        result /= BYTES_TO_MEGABYTES;
    } else if (memory_unit == mmmemory::MemoryUnit::kGigaBytes) {
        result /= BYTES_TO_GIGABYTES;
    } else {
        MMSOLVER_MAYA_ERR(
            "mmmemory::bytes_as_double: "
            "MemoryUnit given is not supported! value="
            << static_cast<int>(memory_unit));
    }
    return result;
}

}  // namespace mmmemory
