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

#include "MMImageCacheCmd.h"

// STD
#include <cassert>
#include <string>

// Maya
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MString.h>
#include <maya/MSyntax.h>

// Maya Viewport 2.0
#include <maya/MViewport2Renderer.h>

// MM Solver
#include <mmcolorio/lib.h>

#include "mmSolver/image/ImageCache.h"
#include "mmSolver/mayahelper/maya_string_utils.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/path_utils.h"
#include "mmSolver/utilities/string_utils.h"

// Command arguments and command name:
#define GPU_CAPACITY_FLAG "-gpc"
#define GPU_CAPACITY_FLAG_LONG "-gpuCapacity"

#define GPU_USED_FLAG "-gpu"
#define GPU_USED_FLAG_LONG "-gpuUsed"

#define CPU_CAPACITY_FLAG "-cpc"
#define CPU_CAPACITY_FLAG_LONG "-cpuCapacity"

#define CPU_USED_FLAG "-cpu"
#define CPU_USED_FLAG_LONG "-cpuUsed"

#define GPU_ITEM_COUNT_FLAG "-gpi"
#define GPU_ITEM_COUNT_FLAG_LONG "-gpuItemCount"

#define CPU_ITEM_COUNT_FLAG "-cpi"
#define CPU_ITEM_COUNT_FLAG_LONG "-cpuItemCount"

#define BRIEF_TEXT_FLAG "-btx"
#define BRIEF_TEXT_FLAG_LONG "-briefText"

namespace mmsolver {

MMImageCacheCmd::~MMImageCacheCmd() {}

void *MMImageCacheCmd::creator() { return new MMImageCacheCmd(); }

MString MMImageCacheCmd::cmdName() { return MString("mmImageCache"); }

/*
 * Tell Maya we have a syntax function.
 */
bool MMImageCacheCmd::hasSyntax() const { return true; }

bool MMImageCacheCmd::isUndoable() const { return true; }

/*
 * Add flags to the command syntax
 */
MSyntax MMImageCacheCmd::newSyntax() {
    MStatus status = MStatus::kSuccess;

    MSyntax syntax;
    syntax.enableQuery(true);
    syntax.enableEdit(true);

    CHECK_MSTATUS(syntax.addFlag(GPU_CAPACITY_FLAG, GPU_CAPACITY_FLAG_LONG,
                                 MSyntax::kString));
    CHECK_MSTATUS(syntax.addFlag(CPU_CAPACITY_FLAG, CPU_CAPACITY_FLAG_LONG,
                                 MSyntax::kString));

    CHECK_MSTATUS(syntax.addFlag(GPU_USED_FLAG, GPU_USED_FLAG_LONG));
    CHECK_MSTATUS(syntax.addFlag(CPU_USED_FLAG, CPU_USED_FLAG_LONG));

    CHECK_MSTATUS(
        syntax.addFlag(GPU_ITEM_COUNT_FLAG, GPU_ITEM_COUNT_FLAG_LONG));
    CHECK_MSTATUS(
        syntax.addFlag(CPU_ITEM_COUNT_FLAG, CPU_ITEM_COUNT_FLAG_LONG));

    CHECK_MSTATUS(syntax.addFlag(BRIEF_TEXT_FLAG, BRIEF_TEXT_FLAG_LONG));

    return syntax;
}

/*
 * Parse command line arguments
 */
MStatus MMImageCacheCmd::parseArgs(const MArgList &args) {
    MStatus status = MStatus::kSuccess;
    const bool verbose = false;

    MArgDatabase argData(syntax(), args, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    m_is_query = argData.isQuery();
    m_is_edit = argData.isEdit();

    MMSOLVER_MAYA_VRB(
        "MMImageCacheCmd::parseArgs: "
        "m_is_query="
        << m_is_query);
    MMSOLVER_MAYA_VRB(
        "MMImageCacheCmd::parseArgs: "
        "m_is_edit="
        << m_is_edit);

    const bool has_gpu_capacity = argData.isFlagSet(GPU_CAPACITY_FLAG, &status);
    const bool has_cpu_capacity = argData.isFlagSet(CPU_CAPACITY_FLAG, &status);
    const bool has_gpu_used = argData.isFlagSet(GPU_USED_FLAG, &status);
    const bool has_cpu_used = argData.isFlagSet(CPU_USED_FLAG, &status);
    const bool has_gpu_item_count =
        argData.isFlagSet(GPU_ITEM_COUNT_FLAG, &status);
    const bool has_cpu_item_count =
        argData.isFlagSet(CPU_ITEM_COUNT_FLAG, &status);
    const bool has_print_brief = argData.isFlagSet(BRIEF_TEXT_FLAG, &status);

    if (m_is_query) {
        if (has_gpu_capacity) {
            m_command_flag = ImageCacheFlagMode::kGpuCapacity;
        } else if (has_cpu_capacity) {
            m_command_flag = ImageCacheFlagMode::kCpuCapacity;
        } else if (has_gpu_used) {
            m_command_flag = ImageCacheFlagMode::kGpuUsed;
        } else if (has_cpu_used) {
            m_command_flag = ImageCacheFlagMode::kCpuUsed;
        } else if (has_gpu_item_count) {
            m_command_flag = ImageCacheFlagMode::kGpuItemCount;
        } else if (has_cpu_item_count) {
            m_command_flag = ImageCacheFlagMode::kCpuItemCount;
        } else if (has_print_brief) {
            m_command_flag = ImageCacheFlagMode::kGenerateBriefText;
        } else {
            MMSOLVER_MAYA_ERR(
                "MMImageCacheCmd::parseArgs: "
                "Invalid command query flag!"
                "value="
                << static_cast<int>(m_command_flag));
            return MStatus::kFailure;
        }
    } else if (m_is_edit) {
        image::ImageCache &image_cache = image::ImageCache::getInstance();

        if (has_gpu_capacity) {
            m_command_flag = ImageCacheFlagMode::kGpuCapacity;
            MString mstring;
            status = argData.getFlagArgument(GPU_CAPACITY_FLAG, 0, mstring);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            m_gpu_capacity_bytes =
                mmmayastring::mstringToNumber<size_t>(mstring);

            // Store the current value, so we can undo later.
            m_previous_gpu_capacity_bytes =
                image_cache.get_gpu_capacity_bytes();
        } else if (has_cpu_capacity) {
            m_command_flag = ImageCacheFlagMode::kCpuCapacity;
            MString mstring;
            status = argData.getFlagArgument(CPU_CAPACITY_FLAG, 0, mstring);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            m_cpu_capacity_bytes =
                mmmayastring::mstringToNumber<size_t>(mstring);

            // Store the current value, so we can undo later.
            m_previous_cpu_capacity_bytes =
                image_cache.get_cpu_capacity_bytes();
        } else {
            MMSOLVER_MAYA_ERR(
                "MMImageCacheCmd::parseArgs: "
                "Invalid command edit flag!"
                "value="
                << static_cast<int>(m_command_flag));
            return MStatus::kFailure;
        }
    } else {
        MMSOLVER_MAYA_ERR(
            "MMImageCacheCmd::parseArgs: "
            "Command is not in query or edit mode! "
            "Please use query or edit mode.");
        return MStatus::kFailure;
    }

    MMSOLVER_MAYA_VRB(
        "MMImageCacheCmd::parseArgs: "
        "Command flag="
        << static_cast<int>(m_command_flag));

    return status;
}

inline MStatus get_texture_manager(
    MHWRender::MTextureManager *&texture_manager) {
    MHWRender::MRenderer *renderer = MHWRender::MRenderer::theRenderer();
    if (!renderer) {
        MMSOLVER_MAYA_ERR(
            "MMImageCacheCmd::get_texture_manager: "
            "Could not get MRenderer!");
        return MStatus::kFailure;
    }

    texture_manager = renderer->getTextureManager();
    if (!texture_manager) {
        MMSOLVER_MAYA_ERR(
            "MMImageCacheCmd::get_texture_manager: "
            "Could not get MTextureManager!");
        return MStatus::kFailure;
    }

    return MStatus::kSuccess;
}

inline MStatus set_values(image::ImageCache &image_cache,
                          const ImageCacheFlagMode command_flag,
                          const size_t gpu_capacity_bytes,
                          const size_t cpu_capacity_bytes) {
    MStatus status = MStatus::kSuccess;

    if (command_flag == ImageCacheFlagMode::kGpuCapacity) {
        MHWRender::MTextureManager *texture_manager = nullptr;
        status = get_texture_manager(texture_manager);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        image_cache.set_gpu_capacity_bytes(texture_manager, gpu_capacity_bytes);
    } else if (command_flag == ImageCacheFlagMode::kCpuCapacity) {
        image_cache.set_cpu_capacity_bytes(cpu_capacity_bytes);
    } else {
        MMSOLVER_MAYA_ERR(
            "MMImageCacheCmd::set_values: "
            "Invalid command edit flag! "
            "value="
            << static_cast<int>(command_flag));
        return MStatus::kFailure;
    }

    return status;
}

MStatus MMImageCacheCmd::doIt(const MArgList &args) {
    MStatus status = MStatus::kSuccess;
    const bool verbose = false;

    // Read all the flag arguments.
    status = parseArgs(args);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    if (m_is_query) {
        image::ImageCache &image_cache = image::ImageCache::getInstance();

        if (m_command_flag == ImageCacheFlagMode::kGenerateBriefText) {
            MString mstring = image_cache.generate_cache_brief_text();
            MMImageCacheCmd::setResult(mstring);
        } else {
            size_t bytes_value = 0;
            if (m_command_flag == ImageCacheFlagMode::kGpuCapacity) {
                bytes_value = image_cache.get_gpu_capacity_bytes();
            } else if (m_command_flag == ImageCacheFlagMode::kCpuCapacity) {
                bytes_value = image_cache.get_cpu_capacity_bytes();
            } else if (m_command_flag == ImageCacheFlagMode::kGpuUsed) {
                bytes_value = image_cache.get_gpu_used_bytes();
            } else if (m_command_flag == ImageCacheFlagMode::kCpuUsed) {
                bytes_value = image_cache.get_cpu_used_bytes();
            } else if (m_command_flag == ImageCacheFlagMode::kGpuItemCount) {
                bytes_value = image_cache.get_gpu_item_count();
            } else if (m_command_flag == ImageCacheFlagMode::kCpuItemCount) {
                bytes_value = image_cache.get_cpu_item_count();
            } else {
                MMSOLVER_MAYA_ERR(
                    "MMImageCacheCmd::doIt: "
                    "Invalid command query flag! "
                    "value="
                    << static_cast<int>(m_command_flag));
                return MStatus::kFailure;
            }

            MString number_mstring(mmmayastring::numberToMString(bytes_value));
            MMImageCacheCmd::setResult(number_mstring);
        }
    } else if (m_is_edit) {
        image::ImageCache &image_cache = image::ImageCache::getInstance();
        set_values(image_cache, m_command_flag, m_gpu_capacity_bytes,
                   m_cpu_capacity_bytes);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    } else {
        MMSOLVER_MAYA_ERR(
            "MMImageCacheCmd::doIt: "
            "Command is not in query or edit mode! "
            "Please use query or edit mode.");
        return MStatus::kFailure;
    }

    return status;
}

MStatus MMImageCacheCmd::redoIt() {
    MStatus status = MStatus::kSuccess;
    if (m_is_edit) {
        image::ImageCache &image_cache = image::ImageCache::getInstance();
        status = set_values(image_cache, m_command_flag, m_gpu_capacity_bytes,
                            m_cpu_capacity_bytes);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }
    return status;
}

MStatus MMImageCacheCmd::undoIt() {
    MStatus status = MStatus::kSuccess;
    if (m_is_edit) {
        image::ImageCache &image_cache = image::ImageCache::getInstance();
        status = set_values(image_cache, m_command_flag,
                            m_previous_gpu_capacity_bytes,
                            m_previous_cpu_capacity_bytes);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }
    return status;
}

}  // namespace mmsolver
