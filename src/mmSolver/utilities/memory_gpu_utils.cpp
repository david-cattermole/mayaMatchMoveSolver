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
#include <cstdlib>
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
#include "assert_utils.h"
#include "debug_utils.h"

namespace mmmemorygpu {

bool gpu_enabled_via_env_var() {
    static const bool enabled = []() {
        // Enabled by default. A value of "0" disables the GPU.
        const char *value = std::getenv("MMSOLVER_USE_GPU");
        if (!value) {
            return true;
        }

        const bool is_disabled = (std::strcmp(value, "0") == 0);
        if (is_disabled) {
            return false;
        }

        return true;
    }();
    return enabled;
}

MStatus memory_total_size_in_bytes(size_t &out_size_in_bytes) {
    out_size_in_bytes = 0;
    if (!gpu_enabled_via_env_var()) {
        MMSOLVER_MAYA_WRN("mmmemorygpu::memory_total_size_in_bytes: "
                          << GPU_DISABLED_MESSAGE);
        return MStatus::kSuccess;
    }

    // Never force renderer initialization; on a machine with a
    // display but no (working) GPU, initializing Viewport 2.0 on
    // demand can crash (SIGSEGV). If the renderer does not already
    // exist, fall back to reporting zero GPU memory.
    const bool initialize_renderer = false;
    const MHWRender::MRenderer *renderer =
        MHWRender::MRenderer::theRenderer(initialize_renderer);
    if (!renderer) {
        MMSOLVER_MAYA_WRN(
            "mmmemorygpu::memory_total_size_in_bytes: "
            "Failed to get Maya MRenderer! "
            << USE_GPU_ENV_VAR_QUESTION);
        return MStatus::kSuccess;
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

    if (!gpu_enabled_via_env_var()) {
        MMSOLVER_MAYA_WRN(
            "mmmemorygpu::gpu_memory_usage: " << GPU_DISABLED_MESSAGE);
        return MStatus::kSuccess;
    }

    // Guard: if the VP2 renderer isn't available there is no real GPU
    // (e.g. virtual X11 display / no GPU hardware).  Touching the
    // legacy MHardwareRenderer below without this check can segfault
    // when a software OpenGL context is present but has no actual GPU.
    //
    // Never force renderer initialization; initializing Viewport 2.0
    // on demand can itself crash (SIGSEGV) without a working GPU.
    const bool initialize_renderer = false;
    MHWRender::MRenderer *vp2_renderer =
        MHWRender::MRenderer::theRenderer(initialize_renderer);
    if (!vp2_renderer) {
        MMSOLVER_MAYA_WRN(
            "mmmemorygpu::gpu_memory_usage: "
            "Failed to get Maya MRenderer! "
            << USE_GPU_ENV_VAR_QUESTION);
        return MStatus::kSuccess;
    }

    // The VP2 MRenderer singleton can be non-null even when the
    // viewport renderer failed to truly initialize (e.g. headless
    // mayapy, a virtual X11 display, or no working GPU). In that
    // state the legacy Viewport 1.0 MGLFunctionTable below may also
    // come back non-null, but its internal OpenGL function pointers
    // are never bound, and calling into it crashes (SIGSEGV). A
    // missing MTextureManager is a reliable signal that the renderer
    // never finished initializing, so check that first and bail out
    // before touching the legacy GL function table.
    MHWRender::MTextureManager *texture_manager =
        vp2_renderer->getTextureManager();
    if (!texture_manager) {
        MMSOLVER_MAYA_WRN(
            "mmmemorygpu::gpu_memory_usage: "
            "Could not get MTextureManager! "
            << USE_GPU_ENV_VAR_QUESTION);
        return MStatus::kSuccess;
    }

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
        MMSOLVER_MAYA_WRN(
            "mmmemorygpu::gpu_memory_usage: "
            "Could not get OpenGL Function Table! "
            << USE_GPU_ENV_VAR_QUESTION);
        return MStatus::kSuccess;
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
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

        total_memory = ati_total_memory_as_bytes;
        free_memory = static_cast<size_t>(ati_free_memory_as_kilobytes) *
                      kilobytes_to_bytes;
        used_memory = total_memory - free_memory;
    } else {
        MMSOLVER_MAYA_WRN(
            "mmmemorygpu::gpu_memory_usage: "
            "Neither GL_NVX_gpu_memory_info nor GL_ATI_meminfo "
            "extensions are supported on this system. "
            "Maybe running on a machine without a GPU? "
            "Falling back to zero GPU memory.");
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
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    out_size_in_bytes = used_memory;

    return MStatus::kSuccess;
}

MStatus memory_free_size_in_bytes(size_t &out_size_in_bytes) {
    out_size_in_bytes = 0;

    size_t total_memory = 0;
    size_t free_memory = 0;
    size_t used_memory = 0;

    MStatus status = gpu_memory_usage(total_memory, free_memory, used_memory);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

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
    if (!gpu_enabled_via_env_var()) {
        MMSOLVER_MAYA_WRN(
            "mmmemorygpu::current_maya_process_memory_used_size_in_bytes: "
            "GPU query was disabled with "
            "MMSOLVER_USE_GPU environment variable.");
        return MStatus::kSuccess;
    }
    // Never force renderer initialization; it can crash (SIGSEGV)
    // without a working GPU.
    const bool initialize_renderer = false;
    const MHWRender::MRenderer *renderer =
        MHWRender::MRenderer::theRenderer(initialize_renderer);
    if (!renderer) {
        MMSOLVER_MAYA_WRN(
            "mmmemorygpu::current_maya_process_memory_used_size_in_bytes: "
            "Failed to get Maya MRenderer! "
            << USE_GPU_ENV_VAR_QUESTION);
        return MStatus::kSuccess;
    }
    out_size_in_bytes = static_cast<size_t>(renderer->GPUUsedMemorySize(
        MHWRender::MRenderer::MGPUMemType::kMemAll));
    return MStatus::kSuccess;
}

// These methods can be used to inform Maya's internal system of any
// GPU memory that we allocate/de-allocate.
MStatus register_allocated_memory_size_in_bytes(const size_t size_in_bytes) {
    if (!gpu_enabled_via_env_var()) {
        MMSOLVER_MAYA_WRN(
            "mmmemorygpu::register_allocated_memory_size_in_bytes: "
            << GPU_DISABLED_MESSAGE);
        return MStatus::kSuccess;
    }

    // Never force renderer initialization; it can crash (SIGSEGV)
    // without a working GPU.
    const bool initialize_renderer = false;
    MHWRender::MRenderer *renderer =
        MHWRender::MRenderer::theRenderer(initialize_renderer);
    if (!renderer) {
        MMSOLVER_MAYA_WRN(
            "mmmemorygpu::register_allocated_memory_size_in_bytes: "
            "Failed to get Maya MRenderer! "
            << GPU_DISABLED_MESSAGE);
        return MStatus::kSuccess;
    }
    MInt64 *evictedGPUMemSize = nullptr;
    return renderer->holdGPUMemory(size_in_bytes, evictedGPUMemSize);
}

MStatus register_deallocated_memory_size_in_bytes(const size_t size_in_bytes) {
    if (!gpu_enabled_via_env_var()) {
        MMSOLVER_MAYA_WRN(
            "mmmemorygpu::register_deallocated_memory_size_in_bytes: "
            << GPU_DISABLED_MESSAGE);
        return MStatus::kSuccess;
    }

    // Never force renderer initialization; it can crash (SIGSEGV)
    // without a working GPU.
    const bool initialize_renderer = false;
    MHWRender::MRenderer *renderer =
        MHWRender::MRenderer::theRenderer(initialize_renderer);
    if (!renderer) {
        MMSOLVER_MAYA_WRN(
            "mmmemorygpu::register_deallocated_memory_size_in_bytes: "
            "Failed to get Maya MRenderer! "
            << USE_GPU_ENV_VAR_QUESTION);
        return MStatus::kSuccess;
    }
    return renderer->releaseGPUMemory(size_in_bytes);
}

}  // namespace mmmemorygpu
