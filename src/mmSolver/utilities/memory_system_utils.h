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
 * Get details about the OS system memory.
 */

#ifndef MEMORY_SYSTEM_UTILS_H
#define MEMORY_SYSTEM_UTILS_H

// STL
#include <cstddef>

namespace mmmemorysystem {
void process_memory_usage(size_t &peak_resident_set_size,
                          size_t &current_resident_set_size);
size_t system_physical_memory_total();
size_t system_physical_memory_free();
size_t system_physical_memory_used();

}  // namespace mmmemorysystem

#endif  // MEMORY_SYSTEM_UTILS_H
