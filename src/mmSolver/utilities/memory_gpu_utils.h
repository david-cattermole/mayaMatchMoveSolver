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
 * Get details about the GPU memory.
 */

#ifndef MEMORY_GPU_UTILS_H
#define MEMORY_GPU_UTILS_H

// Maya
#include <maya/MStatus.h>

namespace mmmemorygpu {

// Messages to show users in error cases.
static const char *GPU_DISABLED_MESSAGE =
    "GPU has been disabled with MMSOLVER_USE_GPU=0 environment variable.";
static const char *USE_GPU_ENV_VAR_QUESTION =
    "Maybe running on a machine without a GPU? "
    "Try setting the environment variable MMSOLVER_USE_GPU=0";

// Returns true when the MMSOLVER_USE_GPU environment variable is set
// to a non-zero value.
//
// When enabled, all GPU memory queries report zero without touching
// the Maya renderer or OpenGL, because doing so can crash (SIGSEGV)
// on machines with a display but no (working) GPU, such as a virtual
// X11 session.
bool gpu_enabled_via_env_var();

MStatus memory_total_size_in_bytes(size_t &out_size_in_bytes);
MStatus memory_used_size_in_bytes(size_t &out_size_in_bytes);
MStatus memory_free_size_in_bytes(size_t &out_size_in_bytes);

MStatus current_maya_process_memory_used_size_in_bytes(
    size_t &out_size_in_bytes);

MStatus register_allocated_memory_size_in_bytes(const size_t size_in_bytes);
MStatus register_deallocated_memory_size_in_bytes(const size_t size_in_bytes);

}  // namespace mmmemorygpu

#endif  // MEMORY_GPU_UTILS_H
