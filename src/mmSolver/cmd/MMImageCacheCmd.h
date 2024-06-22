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
 * 'mmImageCache' Command for querying and manipulating the MM Solver
 * ImageCache.
 *
 * The mmImageCache command is responsible for querying and setting
 * details of the underlying image cache.
 *
 *
 * Use cases:
 *
 * - Get total amount of used CPU memory, displayed in a UI.
 *
 * - Get total amount of CPU memory on the system.
 *
 * - Get amount of CPU memory used by the current process.
 *
 * - Get total GPU memory.
 *
 * - Get used GPU memory.
 *
 * - Display on an image plane node...
 *   - How much memory the currently loaded image sequence is expected
 *     to take up.
 *   - How much memory each frame takes up.
 *   - What is the currently used CPU and GPU memory by this image
 *     sequence/image plane.
 *
 * - UI to display overall memory usage, with...
 *   - Each loaded image sequence.
 *   - How much memory is used by each image sequence (CPU and GPU).
 *   - The total CPU and GPU memory on the system.
 *   - The used CPU and GPU memory on the system.
 *   - A widget to set the Image Cache memory available as a percentage
 *     or fixed memory amount.
 *
 *
 * MEL:
 *     // Return the number of used GPU memory bytes by the image cache.
 *     mmImageCache -query -gpuUsed;
 *
 *     // Return the number of free GPU memory bytes by the image cache.
 *     mmImageCache -query -gpuFree;
 *
 *     // Return the total number of GPU memory bytes that is allowed
 *     // to be to be used by the image cache.
 *     mmImageCache -query -gpuCapacity;
 *
 *     // Set the number of GPU memory bytes that is allowed to be used.
 *     mmImageCache -edit -gpuCapacity 1000;
 *
 *     // Get the amount of data that the image contains.
 *     //
 *     // This will not actually read the file into memory, just enough
 *     // to find the data type and dimensions.
 *     string $image_sequence = "/path/to/image.####.png";
 *     string $image_file = "/path/to/image.1001.png";
 *     string $data_header[] = `mmReadImage -dataHeader $image_file`;
 *     string $data_size = $data_header[4];
 *
 *     // Set the number of CPU memory bytes that is allowed to be used.
 *     int $start_frame = 1001;
 *     int $end_frame = 1101;
 *     int $frame_count = $end_frame - $start_frame;
 *     int $extra_buffer = 3;  // allow a few more images just in case.
 *     // In reality we should check if the system has enough free
 *     // CPU memory, before attempting to load the full image sequence
 *     // or not.
 *     int $new_capacity = ($data_size * ($frame_count + $extra_buffer))
 *     mmImageCache -edit -cpuCapacity $new_capacity;
 *
 *     // Read the image sequence into RAM.
 *     //
 *     // This call will block until all the images are read and loaded.
 *     // Progress will be printed to std::cout.
 *     mmImageCache -cpuLoadImageSequence
 *                  -startFrame $start_frame
 *                  -endFrame $end_frame
 *                  $image_sequence;
 *
 *     // Loads the images (already in the CPU cache - see above), and
 *     // writes them out to the Disk cache.
 *     mmImageCache -writeDiskCache
 *                  -startFrame $start_frame
 *                  -endFrame $end_frame
 *                  $image_sequence;
 *
 */

#ifndef MAYA_MM_IMAGE_CACHE_CMD_H
#define MAYA_MM_IMAGE_CACHE_CMD_H

// STL
#include <string>
#include <vector>

// Maya
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MGlobal.h>
#include <maya/MPxCommand.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MSyntax.h>

namespace mmsolver {

enum class ImageCacheFlagMode : uint8_t {
    kGpuCapacity = 0,
    kCpuCapacity,
    kGpuUsed,
    kCpuUsed,
    kGpuItemCount,
    kCpuItemCount,
    kGpuEraseGroups,
    kCpuEraseGroups,
    kGpuEraseItems,
    kCpuEraseItems,
    kGpuGroupCount,
    kCpuGroupCount,
    kGpuGroupNames,
    kCpuGroupNames,
    kGpuGroupItemCount,
    kCpuGroupItemCount,
    kGpuGroupItemNames,
    kCpuGroupItemNames,
    kGenerateBriefText,
    kUnknown = 255
};

enum class ImageCacheOutputType : uint8_t {
    kSize = 0,
    kString,
    kStringArray,
    kUnknown = 255
};

class MMImageCacheCmd : public MPxCommand {
public:
    MMImageCacheCmd()
        : m_is_query(false)
        , m_is_edit(false)
        , m_command_flag(ImageCacheFlagMode::kUnknown)
        , m_output_type(ImageCacheOutputType::kUnknown)
        , m_previous_gpu_capacity_bytes(0)
        , m_previous_cpu_capacity_bytes(0)
        , m_gpu_capacity_bytes(0)
        , m_cpu_capacity_bytes(0)
        , m_item_names()
        , m_group_name(){};

    virtual ~MMImageCacheCmd();

    virtual bool hasSyntax() const;
    static MSyntax newSyntax();

    virtual MStatus doIt(const MArgList &args);
    virtual bool isUndoable() const;
    virtual MStatus undoIt();
    virtual MStatus redoIt();

    static void *creator();

    static MString cmdName();

private:
    MStatus parseArgs(const MArgList &args);

    bool m_is_edit;
    bool m_is_query;

    ImageCacheFlagMode m_command_flag;
    ImageCacheOutputType m_output_type;

    // The previous values, before the command was run.
    size_t m_previous_gpu_capacity_bytes;
    size_t m_previous_cpu_capacity_bytes;

    size_t m_gpu_capacity_bytes;
    size_t m_cpu_capacity_bytes;

    std::vector<std::string> m_item_names;
    std::string m_group_name;
};

}  // namespace mmsolver

#endif  // MAYA_MM_IMAGE_CACHE_CMD_H
