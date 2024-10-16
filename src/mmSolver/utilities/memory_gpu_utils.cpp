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

#include "memory_gpu_utils.h"

// STL
#include <cstring>

// Maya
#include <maya/MStatus.h>

// Maya Viewport 1.0 (Legacy)
#include <maya/MGL.h>
#include <maya/MGLFunctionTable.h>
#include <maya/MHardwareRenderer.h>

// Maya Viewport 2.0
#include <maya/MViewport2Renderer.h>

// MM Solver
#include "debug_utils.h"

namespace mmmemorygpu {

MStatus memory_total_size_in_bytes(size_t &out_size_in_bytes) {
    out_size_in_bytes = 0;
    const MHWRender::MRenderer *renderer = MHWRender::MRenderer::theRenderer();
    if (!renderer) {
        MMSOLVER_MAYA_WRN(
            "mmmemorygpu::memory_total_size_in_bytes: "
            "Failed to get Maya MRenderer!");
        return MStatus::kFailure;
    }
    out_size_in_bytes = static_cast<size_t>(renderer->GPUtotalMemorySize());
    return MStatus::kSuccess;
}

MStatus gpu_memory_usage(size_t &total_memory, size_t &free_memory,
                         size_t &used_memory) {
    const bool verbose = false;
    MStatus status = MStatus::kSuccess;

    total_memory = 0;
    free_memory = 0;
    used_memory = 0;

    MGLFunctionTable *gGLFT = nullptr;
    const MHardwareRenderer *hardware_renderer_ptr =
        MHardwareRenderer::theRenderer();
    if (hardware_renderer_ptr) {
        gGLFT = hardware_renderer_ptr->glFunctionTable();
        MMSOLVER_MAYA_VRB(
            "mmmemorygpu::gpu_memory_usage: "
            "gGLFT="
            << gGLFT);
    }

    if (!gGLFT) {
        MMSOLVER_MAYA_ERR(
            "mmmemorygpu::gpu_memory_usage: "
            "Could not get OpenGL Function Table!");
        return MStatus::kFailure;
    }

    const bool has_extension_nvidia =
        gGLFT->extensionExists(MGLExtension::kMGLext_NVX_gpu_memory_info);
    const bool has_extension_ati =
        gGLFT->extensionExists(MGLExtension::kMGLext_ATI_meminfo);
    MMSOLVER_MAYA_VRB(
        "mmmemorygpu::gpu_memory_usage: "
        "has_extension_nvidia="
        << has_extension_nvidia);
    MMSOLVER_MAYA_VRB(
        "mmmemorygpu::gpu_memory_usage: "
        "has_extension_ati="
        << has_extension_ati);

    const size_t kilobytes_to_bytes = 1024;
    if (has_extension_nvidia) {
        // https://registry.khronos.org/OpenGL/extensions/NVX/NVX_gpu_memory_info.txt
        MGLint nvidia_total_memory_as_kilobytes = 0;
        MGLint nvidia_free_memory_as_kilobytes = 0;
        gGLFT->glGetIntegerv(MGL_GPU_MEMORY_INFO_TOTAL_AVAILABLE_MEMORY_NVX,
                             &nvidia_total_memory_as_kilobytes);
        gGLFT->glGetIntegerv(MGL_GPU_MEMORY_INFO_CURRENT_AVAILABLE_VIDMEM_NVX,
                             &nvidia_free_memory_as_kilobytes);
        total_memory = static_cast<size_t>(nvidia_total_memory_as_kilobytes) *
                       kilobytes_to_bytes;
        free_memory = static_cast<size_t>(nvidia_free_memory_as_kilobytes) *
                      kilobytes_to_bytes;
        used_memory = total_memory - free_memory;
    } else if (has_extension_ati) {
        // https://registry.khronos.org/OpenGL/extensions/ATI/ATI_meminfo.txt
        MGLint ati_vbo_free_memory[4];
        gGLFT->glGetIntegerv(MGL_VBO_FREE_MEMORY_ATI, ati_vbo_free_memory);

        MGLint ati_free_memory_as_kilobytes = ati_vbo_free_memory[0];
        MGLint ati_free_memory_largest_block_as_kilobytes =
            ati_vbo_free_memory[1];

        // Auxiliary memory is memory that an implementation may use
        // as a backup to its primary pool for a certain type of
        // allocation.
        MGLint ati_free_auxiliary_memory_as_kilobytes = ati_vbo_free_memory[2];
        MGLint ati_free_auxiliary_memory_largest_block_as_kilobytes =
            ati_vbo_free_memory[3];

        // ATL cards (using this extension or the extensions supported
        // by Maya) do not allow getting the total amount of memory on
        // the device, so we must call our function.
        size_t ati_total_memory_as_bytes = 0;
        status = memory_total_size_in_bytes(ati_total_memory_as_bytes);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        total_memory = ati_total_memory_as_bytes;
        free_memory = static_cast<size_t>(ati_free_memory_as_kilobytes) *
                      kilobytes_to_bytes;
        used_memory = total_memory - free_memory;
    } else {
        MMSOLVER_MAYA_ERR(
            "mmmemorygpu::gpu_memory_usage: "
            "Neither GL_NVX_gpu_memory_info nor GL_ATI_meminfo "
            "extensions are supported on this system.");
        status = MStatus::kFailure;
    }

    MMSOLVER_MAYA_VRB(
        "mmmemorygpu::gpu_memory_usage: "
        "total_memory="
        << total_memory);
    MMSOLVER_MAYA_VRB(
        "mmmemorygpu::gpu_memory_usage: "
        "free_memory="
        << free_memory);
    MMSOLVER_MAYA_VRB(
        "mmmemorygpu::gpu_memory_usage: "
        "used_memory="
        << used_memory);

    return status;
}

MStatus memory_used_size_in_bytes(size_t &out_size_in_bytes) {
    out_size_in_bytes = 0;

    size_t total_memory = 0;
    size_t free_memory = 0;
    size_t used_memory = 0;

    MStatus status = gpu_memory_usage(total_memory, free_memory, used_memory);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    out_size_in_bytes = used_memory;

    return MStatus::kSuccess;
}

MStatus memory_free_size_in_bytes(size_t &out_size_in_bytes) {
    out_size_in_bytes = 0;

    size_t total_memory = 0;
    size_t free_memory = 0;
    size_t used_memory = 0;

    MStatus status = gpu_memory_usage(total_memory, free_memory, used_memory);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    out_size_in_bytes = free_memory;

    return MStatus::kSuccess;
}

// Gets the GPU memory used by the current Maya process.
//
// NOTE: This is not all the memory used by the GPU, only by the
// current Maya instance.
MStatus current_maya_process_memory_used_size_in_bytes(
    size_t &out_size_in_bytes) {
    out_size_in_bytes = 0;
    const MHWRender::MRenderer *renderer = MHWRender::MRenderer::theRenderer();
    if (!renderer) {
        MMSOLVER_MAYA_WRN(
            "mmmemorygpu::current_maya_process_memory_used_size_in_bytes: "
            "Failed to get Maya MRenderer!");
        return MStatus::kFailure;
    }
    out_size_in_bytes = static_cast<size_t>(renderer->GPUUsedMemorySize(
        MHWRender::MRenderer::MGPUMemType::kMemAll));
    return MStatus::kSuccess;
}

// These methods can be used to inform Maya's internal system of any
// GPU memory that we allocate/de-allocate.
MStatus register_allocated_memory_size_in_bytes(const size_t size_in_bytes) {
    MHWRender::MRenderer *renderer = MHWRender::MRenderer::theRenderer();
    if (!renderer) {
        MMSOLVER_MAYA_WRN(
            "mmmemorygpu::register_allocated_memory_size_in_bytes: "
            "Failed to get Maya MRenderer!");
        return MStatus::kFailure;
    }
    MInt64 *evictedGPUMemSize = nullptr;
    return renderer->holdGPUMemory(size_in_bytes, evictedGPUMemSize);
}

MStatus register_deallocated_memory_size_in_bytes(const size_t size_in_bytes) {
    MHWRender::MRenderer *renderer = MHWRender::MRenderer::theRenderer();
    if (!renderer) {
        MMSOLVER_MAYA_WRN(
            "mmmemorygpu::register_deallocated_memory_size_in_bytes: "
            "Failed to get Maya MRenderer!");
        return MStatus::kFailure;
    }
    return renderer->releaseGPUMemory(size_in_bytes);
}

}  // namespace mmmemorygpu
