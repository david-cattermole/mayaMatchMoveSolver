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
#include <vector>

// Maya
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
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
#define CPU_CAPACITY_FLAG "-cpc"
#define CPU_CAPACITY_FLAG_LONG "-cpuCapacity"

#define GPU_USED_FLAG "-gpu"
#define GPU_USED_FLAG_LONG "-gpuUsed"
#define CPU_USED_FLAG "-cpu"
#define CPU_USED_FLAG_LONG "-cpuUsed"

#define GPU_ITEM_COUNT_FLAG "-gic"
#define GPU_ITEM_COUNT_FLAG_LONG "-gpuItemCount"
#define CPU_ITEM_COUNT_FLAG "-cic"
#define CPU_ITEM_COUNT_FLAG_LONG "-cpuItemCount"

#define GPU_ERASE_ITEMS_FLAG "-gei"
#define GPU_ERASE_ITEMS_FLAG_LONG "-gpuEraseItems"
#define CPU_ERASE_ITEMS_FLAG "-cei"
#define CPU_ERASE_ITEMS_FLAG_LONG "-cpuEraseItems"

#define GPU_ERASE_GROUP_ITEMS_FLAG "-geg"
#define GPU_ERASE_GROUP_ITEMS_FLAG_LONG "-gpuEraseGroupItems"
#define CPU_ERASE_GROUP_ITEMS_FLAG "-ceg"
#define CPU_ERASE_GROUP_ITEMS_FLAG_LONG "-cpuEraseGroupItems"

#define GPU_GROUP_COUNT_FLAG "-ggc"
#define GPU_GROUP_COUNT_FLAG_LONG "-gpuGroupCount"
#define CPU_GROUP_COUNT_FLAG "-cgc"
#define CPU_GROUP_COUNT_FLAG_LONG "-cpuGroupCount"

#define GPU_GROUP_NAMES_FLAG "-ggn"
#define GPU_GROUP_NAMES_FLAG_LONG "-gpuGroupNames"
#define CPU_GROUP_NAMES_FLAG "-cgn"
#define CPU_GROUP_NAMES_FLAG_LONG "-cpuGroupNames"

#define GPU_GROUP_ITEM_COUNT_FLAG "-ggt"
#define GPU_GROUP_ITEM_COUNT_FLAG_LONG "-gpuGroupItemCount"
#define CPU_GROUP_ITEM_COUNT_FLAG "-cgt"
#define CPU_GROUP_ITEM_COUNT_FLAG_LONG "-cpuGroupItemCount"

#define GPU_GROUP_ITEM_NAMES_FLAG "-gin"
#define GPU_GROUP_ITEM_NAMES_FLAG_LONG "-gpuGroupItemNames"
#define CPU_GROUP_ITEM_NAMES_FLAG "-cin"
#define CPU_GROUP_ITEM_NAMES_FLAG_LONG "-cpuGroupItemNames"

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

    syntax.setObjectType(MSyntax::kStringObjects);

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

    CHECK_MSTATUS(
        syntax.addFlag(GPU_ERASE_ITEMS_FLAG, GPU_ERASE_ITEMS_FLAG_LONG));
    CHECK_MSTATUS(
        syntax.addFlag(CPU_ERASE_ITEMS_FLAG, CPU_ERASE_ITEMS_FLAG_LONG));

    CHECK_MSTATUS(syntax.addFlag(GPU_ERASE_GROUP_ITEMS_FLAG,
                                 GPU_ERASE_GROUP_ITEMS_FLAG_LONG));
    CHECK_MSTATUS(syntax.addFlag(CPU_ERASE_GROUP_ITEMS_FLAG,
                                 CPU_ERASE_GROUP_ITEMS_FLAG_LONG));

    CHECK_MSTATUS(
        syntax.addFlag(GPU_GROUP_COUNT_FLAG, GPU_GROUP_COUNT_FLAG_LONG));
    CHECK_MSTATUS(
        syntax.addFlag(CPU_GROUP_COUNT_FLAG, CPU_GROUP_COUNT_FLAG_LONG));

    CHECK_MSTATUS(
        syntax.addFlag(GPU_GROUP_NAMES_FLAG, GPU_GROUP_NAMES_FLAG_LONG));
    CHECK_MSTATUS(
        syntax.addFlag(CPU_GROUP_NAMES_FLAG, CPU_GROUP_NAMES_FLAG_LONG));

    CHECK_MSTATUS(syntax.addFlag(GPU_GROUP_ITEM_COUNT_FLAG,
                                 GPU_GROUP_ITEM_COUNT_FLAG_LONG));
    CHECK_MSTATUS(syntax.addFlag(CPU_GROUP_ITEM_COUNT_FLAG,
                                 CPU_GROUP_ITEM_COUNT_FLAG_LONG));

    CHECK_MSTATUS(syntax.addFlag(GPU_GROUP_ITEM_NAMES_FLAG,
                                 GPU_GROUP_ITEM_NAMES_FLAG_LONG));
    CHECK_MSTATUS(syntax.addFlag(CPU_GROUP_ITEM_NAMES_FLAG,
                                 CPU_GROUP_ITEM_NAMES_FLAG_LONG));

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

    // Get string objects given to the command.
    MStringArray string_objects;
    argData.getObjects(string_objects);

    // TODO: Do we actually use the group name? Or can it be removed?
    m_group_name = "";
    if (string_objects.length() > 0) {
        const std::string item_name = string_objects[0].asChar();
        m_group_name = item_name;
    }
    MMSOLVER_MAYA_VRB(
        "MMImageCacheCmd::parseArgs: "
        "m_group_name=\""
        << m_group_name << "\"");

    for (auto i = 0; i < string_objects.length(); i++) {
        const std::string item_name = string_objects[i].asChar();
        m_item_names.push_back(item_name);
        MMSOLVER_MAYA_VRB(
            "MMImageCacheCmd::parseArgs: "
            "m_item_names["
            << i << "]=\"" << item_name << "\"");
    }

    const bool has_gpu_capacity = argData.isFlagSet(GPU_CAPACITY_FLAG, &status);
    const bool has_cpu_capacity = argData.isFlagSet(CPU_CAPACITY_FLAG, &status);
    const bool has_gpu_used = argData.isFlagSet(GPU_USED_FLAG, &status);
    const bool has_cpu_used = argData.isFlagSet(CPU_USED_FLAG, &status);

    const bool has_gpu_item_count =
        argData.isFlagSet(GPU_ITEM_COUNT_FLAG, &status);
    const bool has_cpu_item_count =
        argData.isFlagSet(CPU_ITEM_COUNT_FLAG, &status);

    const bool has_gpu_erase_items =
        argData.isFlagSet(GPU_ERASE_ITEMS_FLAG, &status);
    const bool has_cpu_erase_items =
        argData.isFlagSet(CPU_ERASE_ITEMS_FLAG, &status);

    const bool has_gpu_erase_group_items =
        argData.isFlagSet(GPU_ERASE_GROUP_ITEMS_FLAG, &status);
    const bool has_cpu_erase_group_items =
        argData.isFlagSet(CPU_ERASE_GROUP_ITEMS_FLAG, &status);

    const bool has_gpu_group_count =
        argData.isFlagSet(GPU_GROUP_COUNT_FLAG, &status);
    const bool has_cpu_group_count =
        argData.isFlagSet(CPU_GROUP_COUNT_FLAG, &status);
    const bool has_gpu_group_names =
        argData.isFlagSet(GPU_GROUP_NAMES_FLAG, &status);
    const bool has_cpu_group_names =
        argData.isFlagSet(CPU_GROUP_NAMES_FLAG, &status);

    const bool has_gpu_group_item_count =
        argData.isFlagSet(GPU_GROUP_ITEM_COUNT_FLAG, &status);
    const bool has_cpu_group_item_count =
        argData.isFlagSet(CPU_GROUP_ITEM_COUNT_FLAG, &status);
    const bool has_gpu_group_item_names =
        argData.isFlagSet(GPU_GROUP_ITEM_NAMES_FLAG, &status);
    const bool has_cpu_group_item_names =
        argData.isFlagSet(CPU_GROUP_ITEM_NAMES_FLAG, &status);

    const bool has_print_brief = argData.isFlagSet(BRIEF_TEXT_FLAG, &status);

    if (m_is_query) {
        if (has_gpu_capacity) {
            m_command_flag = ImageCacheFlagMode::kGpuCapacity;
            m_output_type = ImageCacheOutputType::kSize;
        } else if (has_cpu_capacity) {
            m_command_flag = ImageCacheFlagMode::kCpuCapacity;
            m_output_type = ImageCacheOutputType::kSize;
        } else if (has_gpu_used) {
            m_command_flag = ImageCacheFlagMode::kGpuUsed;
            m_output_type = ImageCacheOutputType::kSize;
        } else if (has_cpu_used) {
            m_command_flag = ImageCacheFlagMode::kCpuUsed;
            m_output_type = ImageCacheOutputType::kSize;
        } else if (has_gpu_item_count) {
            m_command_flag = ImageCacheFlagMode::kGpuItemCount;
            m_output_type = ImageCacheOutputType::kSize;
        } else if (has_cpu_item_count) {
            m_command_flag = ImageCacheFlagMode::kCpuItemCount;
            m_output_type = ImageCacheOutputType::kSize;
        } else if (has_gpu_group_count) {
            m_command_flag = ImageCacheFlagMode::kGpuGroupCount;
            m_output_type = ImageCacheOutputType::kSize;
        } else if (has_cpu_group_count) {
            m_command_flag = ImageCacheFlagMode::kCpuGroupCount;
            m_output_type = ImageCacheOutputType::kSize;
        } else if (has_gpu_group_names) {
            m_command_flag = ImageCacheFlagMode::kGpuGroupNames;
            m_output_type = ImageCacheOutputType::kStringArray;
        } else if (has_cpu_group_names) {
            m_command_flag = ImageCacheFlagMode::kCpuGroupNames;
            m_output_type = ImageCacheOutputType::kStringArray;
        } else if (has_gpu_group_item_count || has_cpu_group_item_count ||
                   has_gpu_group_item_names || has_cpu_group_item_names) {
            if (string_objects.length() != 1) {
                status = MStatus::kFailure;
                status.perror(
                    "mmImageCache: "
                    "One group name must be given to command!");
                return status;
            }

            if (has_gpu_group_item_count) {
                m_command_flag = ImageCacheFlagMode::kGpuGroupItemCount;
                m_output_type = ImageCacheOutputType::kSize;
            } else if (has_cpu_group_item_count) {
                m_command_flag = ImageCacheFlagMode::kCpuGroupItemCount;
                m_output_type = ImageCacheOutputType::kSize;
            } else if (has_gpu_group_item_names) {
                m_command_flag = ImageCacheFlagMode::kGpuGroupItemNames;
                m_output_type = ImageCacheOutputType::kStringArray;
            } else if (has_cpu_group_item_names) {
                m_command_flag = ImageCacheFlagMode::kCpuGroupItemNames;
                m_output_type = ImageCacheOutputType::kStringArray;
            }
        } else if (has_print_brief) {
            m_command_flag = ImageCacheFlagMode::kGenerateBriefText;
            m_output_type = ImageCacheOutputType::kString;
        } else {
            MMSOLVER_MAYA_ERR(
                "MMImageCacheCmd::parseArgs: "
                "Invalid command query flag! "
                "m_command_flag="
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
        } else if (has_gpu_erase_items) {
            m_command_flag = ImageCacheFlagMode::kGpuEraseItems;
            m_output_type = ImageCacheOutputType::kSize;
        } else if (has_cpu_erase_items) {
            m_command_flag = ImageCacheFlagMode::kCpuEraseItems;
            m_output_type = ImageCacheOutputType::kSize;
        } else if (has_gpu_erase_group_items) {
            m_command_flag = ImageCacheFlagMode::kGpuEraseGroupItems;
            m_output_type = ImageCacheOutputType::kSize;
        } else if (has_cpu_erase_group_items) {
            m_command_flag = ImageCacheFlagMode::kCpuEraseGroupItems;
            m_output_type = ImageCacheOutputType::kSize;
        } else {
            MMSOLVER_MAYA_ERR(
                "MMImageCacheCmd::parseArgs: "
                "Invalid command flag! "
                "m_command_flag="
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
                          const size_t cpu_capacity_bytes,
                          const std::vector<std::string> &item_names,
                          const std::string &group_name,
                          size_t &out_item_count) {
    const bool verbose = false;
    MStatus status = MStatus::kSuccess;

    const auto command_flag_int = static_cast<int>(command_flag);
    if (verbose) {
        std::stringstream item_names_ss;
        for (auto it = item_names.begin(); it != item_names.end(); it++) {
            auto item_name = *it;
            item_names_ss << item_name << ";";
        }
        MMSOLVER_MAYA_VRB("MMImageCacheCmd::set_values: "
                          << "command_flag=" << command_flag_int
                          << " gpu_capacity_bytes=" << gpu_capacity_bytes
                          << " cpu_capacity_bytes=" << cpu_capacity_bytes
                          << " item_names=" << item_names_ss.str()
                          << " item_names.size()=" << item_names.size()
                          << " group_name=" << group_name.c_str()
                          << " group_name.size()=" << group_name.size());
    }

    out_item_count = 0;
    if (command_flag == ImageCacheFlagMode::kGpuCapacity) {
        MMSOLVER_MAYA_VRB("MMImageCacheCmd::set_values: "
                          << "flag=\"" << GPU_CAPACITY_FLAG_LONG << "\"");

        MHWRender::MTextureManager *texture_manager = nullptr;
        status = get_texture_manager(texture_manager);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        image_cache.set_gpu_capacity_bytes(texture_manager, gpu_capacity_bytes);
    } else if (command_flag == ImageCacheFlagMode::kCpuCapacity) {
        MMSOLVER_MAYA_VRB("MMImageCacheCmd::set_values: "
                          << "flag=\"" << CPU_CAPACITY_FLAG_LONG << "\"");

        image_cache.set_cpu_capacity_bytes(cpu_capacity_bytes);
    } else if (command_flag == ImageCacheFlagMode::kGpuEraseItems) {
        MMSOLVER_MAYA_VRB("MMImageCacheCmd::set_values: "
                          << "flag=\"" << GPU_ERASE_ITEMS_FLAG_LONG << "\"");

        MHWRender::MTextureManager *texture_manager = nullptr;
        status = get_texture_manager(texture_manager);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        for (auto it = item_names.begin(); it != item_names.end(); it++) {
            auto item_name = *it;
            MMSOLVER_MAYA_VRB("MMImageCacheCmd::set_values: "
                              << "item_name=\"" << item_name.c_str() << "\"");
            const bool ok =
                image_cache.gpu_erase_item(texture_manager, item_name);
            out_item_count += static_cast<bool>(ok);
        }
    } else if (command_flag == ImageCacheFlagMode::kCpuEraseItems) {
        MMSOLVER_MAYA_VRB("MMImageCacheCmd::set_values: "
                          << "flag=\"" << CPU_ERASE_ITEMS_FLAG_LONG << "\"");

        for (auto it = item_names.begin(); it != item_names.end(); it++) {
            auto item_name = *it;
            MMSOLVER_MAYA_VRB("MMImageCacheCmd::set_values: "
                              << "item_name=\"" << item_name.c_str() << "\"");
            const bool ok = image_cache.cpu_erase_item(item_name);
            out_item_count += static_cast<bool>(ok);
        }
    } else if (command_flag == ImageCacheFlagMode::kGpuEraseGroupItems) {
        MMSOLVER_MAYA_VRB("MMImageCacheCmd::set_values: "
                          << "flag=\"" << CPU_ERASE_GROUP_ITEMS_FLAG_LONG
                          << "\"");

        if (group_name.size() == 0) {
            MMSOLVER_MAYA_ERR("MMImageCacheCmd::set_values: "
                              << "\"" << GPU_ERASE_GROUP_ITEMS_FLAG_LONG
                              << "\" "
                              << "flag needs a group name, but none given! "
                                 "group_name.size()="
                              << static_cast<int>(group_name.size()));
            return MStatus::kFailure;
        }

        MHWRender::MTextureManager *texture_manager = nullptr;
        status = get_texture_manager(texture_manager);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        for (auto it = item_names.begin(); it != item_names.end(); it++) {
            auto item_name = *it;
            MMSOLVER_MAYA_VRB("MMImageCacheCmd::set_values: "
                              << "item_name=\"" << item_name.c_str() << "\"");
            out_item_count +=
                image_cache.gpu_erase_group_items(texture_manager, item_name);
        }
    } else if (command_flag == ImageCacheFlagMode::kCpuEraseGroupItems) {
        MMSOLVER_MAYA_VRB("MMImageCacheCmd::set_values: "
                          << "flag=\"" << CPU_ERASE_GROUP_ITEMS_FLAG_LONG
                          << "\"");

        if (group_name.size() == 0) {
            MMSOLVER_MAYA_ERR("MMImageCacheCmd::set_values: "
                              << "\"" << CPU_ERASE_GROUP_ITEMS_FLAG_LONG
                              << "\" "
                              << "flag needs a group name, but none given! "
                                 "group_name.size()="
                              << static_cast<int>(group_name.size()));
            return MStatus::kFailure;
        }

        MMSOLVER_MAYA_VRB("MMImageCacheCmd::set_values: "
                          << "group_name=\"" << group_name.c_str() << "\"");

        for (auto it = item_names.begin(); it != item_names.end(); it++) {
            auto item_name = *it;
            MMSOLVER_MAYA_VRB("MMImageCacheCmd::set_values: "
                              << "item_name=\"" << item_name.c_str() << "\"");
            out_item_count += image_cache.cpu_erase_group_items(item_name);
        }
    } else {
        MMSOLVER_MAYA_ERR(
            "MMImageCacheCmd::set_values: "
            "Invalid command flag! "
            "command_flag="
            << static_cast<int>(command_flag));
        return MStatus::kFailure;
    }

    MMSOLVER_MAYA_VRB(
        "MMImageCacheCmd::set_values: out_item_count=" << out_item_count);

    return status;
}

MStatus get_value_size(image::ImageCache &image_cache,
                       const ImageCacheFlagMode command_flag,
                       const std::string &group_name, size_t &out_value) {
    out_value = 0;

    if (command_flag == ImageCacheFlagMode::kGpuCapacity) {
        out_value = image_cache.get_gpu_capacity_bytes();
    } else if (command_flag == ImageCacheFlagMode::kCpuCapacity) {
        out_value = image_cache.get_cpu_capacity_bytes();
    } else if (command_flag == ImageCacheFlagMode::kGpuUsed) {
        out_value = image_cache.get_gpu_used_bytes();
    } else if (command_flag == ImageCacheFlagMode::kCpuUsed) {
        out_value = image_cache.get_cpu_used_bytes();
    } else if (command_flag == ImageCacheFlagMode::kGpuItemCount) {
        out_value = image_cache.get_gpu_item_count();
    } else if (command_flag == ImageCacheFlagMode::kCpuItemCount) {
        out_value = image_cache.get_cpu_item_count();
    } else if (command_flag == ImageCacheFlagMode::kGpuGroupCount) {
        out_value = image_cache.get_gpu_group_count();
    } else if (command_flag == ImageCacheFlagMode::kCpuGroupCount) {
        out_value = image_cache.get_cpu_group_count();
    } else if (command_flag == ImageCacheFlagMode::kGpuGroupItemCount) {
        out_value = image_cache.gpu_group_item_count(group_name);
    } else if (command_flag == ImageCacheFlagMode::kCpuGroupItemCount) {
        out_value = image_cache.cpu_group_item_count(group_name);
    } else {
        MMSOLVER_MAYA_ERR(
            "MMImageCacheCmd::get_value_size: "
            "Invalid command flag! "
            "command_flag="
            << static_cast<int>(command_flag));
        return MStatus::kFailure;
    }

    return MStatus::kSuccess;
}

MStatus get_value_string(image::ImageCache &image_cache,
                         const ImageCacheFlagMode command_flag,
                         MString &out_result) {
    if (command_flag == ImageCacheFlagMode::kGenerateBriefText) {
        out_result = image_cache.generate_cache_brief_text();
    } else {
        MMSOLVER_MAYA_ERR(
            "MMImageCacheCmd::get_value_string: "
            "Invalid command flag! "
            "command_flag="
            << static_cast<int>(command_flag));
        return MStatus::kFailure;
    }

    return MStatus::kSuccess;
}

MStatus get_value_string_array(image::ImageCache &image_cache,
                               const ImageCacheFlagMode command_flag,
                               const std::string &group_name,
                               MStringArray &out_results) {
    bool ok = true;
    std::vector<std::string> outputs;

    if (command_flag == ImageCacheFlagMode::kGpuGroupNames) {
        image_cache.gpu_group_names(outputs);
    } else if (command_flag == ImageCacheFlagMode::kCpuGroupNames) {
        image_cache.cpu_group_names(outputs);
    } else if (command_flag == ImageCacheFlagMode::kGpuGroupItemNames) {
        if (group_name.size() == 0) {
            MMSOLVER_MAYA_ERR("MMImageCacheCmd::get_value_string_array: "
                              << "\"" << GPU_GROUP_ITEM_NAMES_FLAG_LONG << "\" "
                              << "flag needs a group name, but none given! "
                                 "group_name.size()="
                              << static_cast<int>(group_name.size()));
            return MStatus::kFailure;
        }

        ok = image_cache.gpu_group_item_names(group_name, outputs);
    } else if (command_flag == ImageCacheFlagMode::kCpuGroupItemNames) {
        if (group_name.size() == 0) {
            MMSOLVER_MAYA_ERR("MMImageCacheCmd::get_value_string_array: "
                              << "\"" << CPU_GROUP_ITEM_NAMES_FLAG_LONG << "\" "
                              << "flag needs a group name, but none given! "
                                 "group_name.size()="
                              << static_cast<int>(group_name.size()));
            return MStatus::kFailure;
        }

        ok = image_cache.cpu_group_item_names(group_name, outputs);
    } else {
        MMSOLVER_MAYA_ERR(
            "MMImageCacheCmd::get_value_string_array: "
            "Invalid command flag! "
            "command_flag="
            << static_cast<int>(command_flag));
        return MStatus::kFailure;
    }

    if (!ok) {
        MMSOLVER_MAYA_ERR(
            "MMImageCacheCmd::get_value_string_array: "
            "failed to apply action! ok="
            << static_cast<int>(ok));
        return MStatus::kFailure;
    }

    out_results.clear();
    for (auto i = 0; i < outputs.size(); i++) {
        const auto value = outputs[i];
        out_results.append(MString(value.c_str()));
    }

    return MStatus::kSuccess;
}

MStatus MMImageCacheCmd::doIt(const MArgList &args) {
    const bool verbose = false;

    // Read all the flag arguments.
    MStatus status = parseArgs(args);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    if (m_is_query) {
        image::ImageCache &image_cache = image::ImageCache::getInstance();

        if (m_output_type == ImageCacheOutputType::kString) {
            MString result;
            status = get_value_string(image_cache, m_command_flag, result);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            MMImageCacheCmd::setResult(result);
        } else if (m_output_type == ImageCacheOutputType::kSize) {
            size_t result = 0;
            status = get_value_size(image_cache, m_command_flag, m_group_name,
                                    result);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            MString result_string(mmmayastring::numberToMString(result));
            MMImageCacheCmd::setResult(result_string);
        } else if (m_output_type == ImageCacheOutputType::kStringArray) {
            MStringArray results;
            status = get_value_string_array(image_cache, m_command_flag,
                                            m_group_name, results);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            MMImageCacheCmd::setResult(results);
        } else {
            MMSOLVER_MAYA_ERR(
                "MMImageCacheCmd::doIt: "
                "Invalid command query flag! "
                "value="
                << static_cast<int>(m_command_flag));
            return MStatus::kFailure;
        }

    } else if (m_is_edit) {
        image::ImageCache &image_cache = image::ImageCache::getInstance();

        size_t item_count = 0;
        status = set_values(image_cache, m_command_flag, m_gpu_capacity_bytes,
                            m_cpu_capacity_bytes, m_item_names, m_group_name,
                            item_count);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        if (m_output_type == ImageCacheOutputType::kSize) {
            MString result_string(mmmayastring::numberToMString(item_count));
            MMImageCacheCmd::setResult(result_string);
        }
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

        size_t item_count = 0;
        status = set_values(image_cache, m_command_flag, m_gpu_capacity_bytes,
                            m_cpu_capacity_bytes, m_item_names, m_group_name,
                            item_count);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        if (m_output_type == ImageCacheOutputType::kSize) {
            MString result_string(mmmayastring::numberToMString(item_count));
            MMImageCacheCmd::setResult(result_string);
        }
    }
    return status;
}

MStatus MMImageCacheCmd::undoIt() {
    MStatus status = MStatus::kSuccess;
    if (m_is_edit) {
        if ((m_command_flag == ImageCacheFlagMode::kGpuEraseItems) ||
            (m_command_flag == ImageCacheFlagMode::kCpuEraseItems) ||
            (m_command_flag == ImageCacheFlagMode::kGpuEraseGroupItems) ||
            (m_command_flag == ImageCacheFlagMode::kCpuEraseGroupItems)) {
            status = MStatus::kFailure;
            MMSOLVER_MAYA_ERR(
                "MMImageCacheCmd::undoIt: "
                "Invalid command edit flag! "
                "value="
                << static_cast<int>(m_command_flag));
        } else {
            image::ImageCache &image_cache = image::ImageCache::getInstance();

            size_t item_count = 0;
            status = set_values(image_cache, m_command_flag,
                                m_previous_gpu_capacity_bytes,
                                m_previous_cpu_capacity_bytes, m_item_names,
                                m_group_name, item_count);
            CHECK_MSTATUS_AND_RETURN_IT(status);
        }
    }
    return status;
}

}  // namespace mmsolver
