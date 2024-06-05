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

#include "ImageCache.h"

// Get M_PI constant
#define _USE_MATH_DEFINES
#include <cmath>

// STL
#include <cassert>
#include <cstdlib>
#include <cstring>
#include <string>

// Maya
#include <maya/MImage.h>
#include <maya/MString.h>

// Maya Viewport 2.0
#include <maya/MTextureManager.h>

// MM Solver
#include <mmcolorio/lib.h>
#include <mmcore/lib.h>

#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/render/shader/shader_utils.h"
#include "mmSolver/shape/constant_texture_data.h"
#include "mmSolver/utilities/number_utils.h"
#include "mmSolver/utilities/path_utils.h"

namespace mmsolver {

// Get GPU memory info from the Maya API:
//
// MRenderer::GPUtotalMemorySize()
// MRenderer::GPUUsedMemorySize()
//
//
// These methods can be used to inform Maya's internal system of any
// GPU memory that we allocate/deallocate:
//
// MRenderer::holdGPUMemory();
// MRenderer::releaseGPUMemory();
//
//
// How to get the amount of (CPU) system memory?
// https://stackoverflow.com/questions/2513505/how-to-get-available-memory-c-g
// https://stackoverflow.com/questions/63166/how-to-determine-cpu-and-memory-consumption-from-inside-a-process/
//
//
// On UNIX-like operating systems, use sysconf to get the amount of
// system memory:
//
// #include <unistd.h>
// unsigned long long getTotalSystemMemory()
// {
//     long pages = sysconf(_SC_PHYS_PAGES);
//     long page_size = sysconf(_SC_PAGE_SIZE);
//     return pages * page_size;
// }
//
//
// On Windows, use GlobalMemoryStatusEx:
//
// #include <windows.h>
// unsigned long long getTotalSystemMemory()
// {
//     MEMORYSTATUSEX status;
//     status.dwLength = sizeof(status);
//     GlobalMemoryStatusEx(&status);
//     return status.ullTotalPhys;
// }
//
//
// Helpful code:
// https://github.com/david-cattermole/cpp-utilities/blob/master/include/fileSystemUtils.h
// https://github.com/david-cattermole/cpp-utilities/blob/master/include/hashUtils.h
// https://github.com/david-cattermole/cpp-utilities/blob/master/include/osMemoryUtils.h

void *get_mimage_pixel_data(const MImage &image,
                            const CachePixelDataType pixel_data_type,
                            const uint32_t width, const uint32_t height,
                            const uint8_t number_of_channels,
                            uint8_t &out_bytes_per_channel,
                            MHWRender::MRasterFormat &out_texture_format) {
    const bool verbose = false;

    const uint32_t print_num_pixels = 8;
    void *pixel_data = nullptr;
    if (pixel_data_type == CachePixelDataType::kU8) {
        MMSOLVER_MAYA_VRB("mmsolver::ImageCache: get_mimage_pixel_data:"
                          << " pixel_data_type=CachePixelDataType::kU8");

        // 8-bit unsigned integers use 1 byte.
        out_bytes_per_channel = 1;

        const bool is_rgba = image.isRGBA();
        MMSOLVER_MAYA_VRB("mmsolver::ImageCache: get_mimage_pixel_data:"
                          << " is_rgba=" << is_rgba);
        if (is_rgba) {
            out_texture_format = MHWRender::kR8G8B8A8_UNORM;
        } else {
            out_texture_format = MHWRender::kB8G8R8A8;
        }

        unsigned char *pixels = image.pixels();

        if (verbose) {
            for (uint32_t row = 0; row <= print_num_pixels; row++) {
                const uint32_t index = row * number_of_channels;
                const uint32_t r = static_cast<uint32_t>(pixels[index + 0]);
                const uint32_t g = static_cast<uint32_t>(pixels[index + 1]);
                const uint32_t b = static_cast<uint32_t>(pixels[index + 2]);
                const uint32_t a = static_cast<uint32_t>(pixels[index + 3]);
                MMSOLVER_MAYA_VRB("mmsolver::ImageCache: get_mimage_pixel_data:"
                                  << " row=" << row << " pixel=" << r << ", "
                                  << g << ", " << b << ", " << a);
            }
        }

        // TODO: Allow giving the explicit input and output color
        // space names.
        //
        // TODO: Allow outputting 32-bit/16-bit float pixel data, to
        // ensure the plate doesn't get quantize.
        //
        // mmcolorio::image_convert_srgb_to_linear_srgb_u8(pixels, width,
        // height,
        //                                                 number_of_channels);

        // mmcolorio::test_opencolorio(pixels, width, height,
        // number_of_channels);

        pixel_data = static_cast<void *>(pixels);
    } else if (pixel_data_type == CachePixelDataType::kF32) {
        MMSOLVER_MAYA_VRB("mmsolver::ImageCache: get_mimage_pixel_data:"
                          << " pixel_data_type=CachePixelDataType::kF32");

        // 32-bit floats use 4 bytes.
        out_bytes_per_channel = 4;

        out_texture_format = MHWRender::kR32G32B32A32_FLOAT;

        float *floatPixels = image.floatPixels();

        if (verbose) {
            for (uint32_t row = 0; row <= print_num_pixels; row++) {
                const uint32_t index = row * number_of_channels;
                const float r = floatPixels[index + 0];
                const float g = floatPixels[index + 1];
                const float b = floatPixels[index + 2];
                const float a = floatPixels[index + 3];
                MMSOLVER_MAYA_VRB("mmsolver::ImageCache: get_mimage_pixel_data:"
                                  << " row=" << row << " pixel=" << r << ", "
                                  << g << ", " << b << ", " << a);
            }
        }

        // mmcolorio::image_convert_srgb_to_linear_srgb_f32(
        //     floatPixels, width, height, number_of_channels);

        pixel_data = static_cast<void *>(floatPixels);
    } else {
        MMSOLVER_MAYA_ERR("mmsolver::ImageCache: get_mimage_pixel_data: "
                          << "Invalid pixel type is "
                          << static_cast<int>(pixel_data_type));
        return nullptr;
    }

    return pixel_data;
}

CachePixelDataType convert_mpixel_type_to_pixel_data_type(
    MImage::MPixelType pixel_type) {
    CachePixelDataType pixel_data_type = CachePixelDataType::kUnknown;
    if (pixel_type == MImage::MPixelType::kByte) {
        pixel_data_type = CachePixelDataType::kU8;
    } else if (pixel_type == MImage::MPixelType::kFloat) {
        pixel_data_type = CachePixelDataType::kF32;
    } else {
        MMSOLVER_MAYA_WRN(
            "mmsolver::ImageCache: convert_mpixel_type_to_pixel_data_type: "
            "Invalid MImage::MPixelType value.");
    }
    return pixel_data_type;
}

MStatus read_with_mimage(MImage &image, MString &file_path,
                         const MImage::MPixelType pixel_type,
                         uint32_t &out_width, uint32_t &out_height,
                         uint8_t &out_number_of_channels,
                         uint8_t &out_bytes_per_channel,
                         MHWRender::MRasterFormat &out_texture_format,
                         CachePixelDataType &out_pixel_data_type,
                         void *&out_pixel_data) {
    const bool verbose = false;

    MStatus status = MStatus::kSuccess;

    // TODO: This code can be changed to whatever reading function
    // that reads the input file path.
    status = image.readFromFile(file_path, pixel_type);
    CHECK_MSTATUS(status);
    if (status != MS::kSuccess) {
        MMSOLVER_MAYA_WRN("mmsolver::ImageCache: read_with_mimage:"
                          << " failed to read image \"" << file_path.asChar()
                          << "\".");
        return status;
    }

    image.getSize(out_width, out_height);
    MMSOLVER_MAYA_VRB("mmsolver::ImageCache: read_with_mimage:"
                      << " width=" << out_width << " height=" << out_height);

    out_pixel_data_type = convert_mpixel_type_to_pixel_data_type(pixel_type);

    out_pixel_data = get_mimage_pixel_data(
        image, out_pixel_data_type, out_width, out_height,
        out_number_of_channels, out_bytes_per_channel, out_texture_format);

    return status;
}

MTexture *read_image_file(MHWRender::MTextureManager *texture_manager,
                          ImageCache &image_cache, MImage &temp_image,
                          const MString &file_path,
                          const MImage::MPixelType pixel_type,
                          const bool do_texture_update) {
    assert(texture_manager != nullptr);

    const bool verbose = false;
    MMSOLVER_MAYA_VRB("mmsolver::ImageCache: read_image_file:"
                      << " file_path=" << file_path.asChar());

    MString resolved_file_path = file_path;
    MStatus status = mmpath::resolve_input_file_path(resolved_file_path);
    if (status != MS::kSuccess) {
        MMSOLVER_MAYA_VRB("mmsolver::ImageCache: read_image_file:"
                          << " file does not exist \""
                          << resolved_file_path.asChar() << "\".");
        return nullptr;
    }

    std::string key = std::string(resolved_file_path.asChar());
    CacheTextureData texture_data = image_cache.gpu_find(key);

    MMSOLVER_MAYA_VRB("mmsolver::ImageCache: read_image_file: findTexture: "
                      << texture_data.is_valid());
    MMSOLVER_MAYA_VRB(
        "mmsolver::ImageCache: read_image_file: do_texture_update="
        << do_texture_update);
    if (texture_data.is_valid() && (do_texture_update == false)) {
        MMSOLVER_MAYA_VRB("mmsolver::ImageCache: read_image_file DONE1:"
                          << " texture=" << texture_data.texture());
        return texture_data.texture();
    }

    // TODO: We should test if the file exists, then cache
    // result. This avoids us having to check the disk each time we
    // hit a frame that is outside the frame range of the image
    // sequence. This would mean that we would then need to be able to
    // flush that cached result - for example if the image sequence
    // changes. Alternatively, we could could pre-cache the file path
    // existence as soon as the user changes the file path. Another
    // approach would be to expose a Maya command that would allow
    // Python user code to add the list of valid images into the
    // cache.

    CacheImagePixelData image_pixel_data = image_cache.cpu_find(key);

    uint32_t width = 0;
    uint32_t height = 0;
    uint8_t number_of_channels = 4;
    uint8_t bytes_per_channel = 0;
    MHWRender::MRasterFormat texture_format;
    CachePixelDataType pixel_data_type = CachePixelDataType::kUnknown;
    void *maya_owned_pixel_data = nullptr;

    const bool image_pixel_data_valid = image_pixel_data.is_valid();
    if (image_pixel_data_valid) {
        maya_owned_pixel_data = image_pixel_data.pixel_data();
        width = image_pixel_data.width();
        height = image_pixel_data.height();
        number_of_channels = image_pixel_data.num_channels();
        pixel_data_type = image_pixel_data.pixel_data_type();
        bytes_per_channel =
            convert_pixel_data_type_to_bytes_per_channel(pixel_data_type);

        if (pixel_data_type == CachePixelDataType::kU8) {
            // Assumes the 8-bit data is "RGBA".
            texture_format = MHWRender::kR8G8B8A8_UNORM;
        } else if (pixel_data_type == CachePixelDataType::kF32) {
            texture_format = MHWRender::kR32G32B32A32_FLOAT;
        }

    } else {
        // TODO: This code can be changed to whatever reading function
        // that reads the input file path.

        status = read_with_mimage(temp_image, resolved_file_path, pixel_type,
                                  width, height, number_of_channels,
                                  bytes_per_channel, texture_format,
                                  pixel_data_type, maya_owned_pixel_data);
        if (status != MS::kSuccess) {
            return nullptr;
        }

        // TODO: any image manipulations required can be done here.
        // TODO: Apply colour correction via OIIO.
        // // image.verticalFlip();
    }

    if (!maya_owned_pixel_data) {
        MMSOLVER_MAYA_ERR("mmsolver::ImageCache: read_image_file: "
                          << "Invalid pixel data!");
        return nullptr;
    }

    CacheImagePixelData gpu_image_pixel_data =
        CacheImagePixelData(static_cast<void *>(maya_owned_pixel_data), width,
                            height, number_of_channels, pixel_data_type);

    texture_data =
        image_cache.gpu_insert(texture_manager, key, gpu_image_pixel_data);
    MMSOLVER_MAYA_VRB("mmsolver::ImageCache: read_image_file: "
                      << "gpu_inserted=" << texture_data.texture());

    // Duplicate the Maya-owned pixel data for our image cache.
    const size_t pixel_data_byte_count =
        width * height * number_of_channels * bytes_per_channel;
    image_pixel_data = CacheImagePixelData();
    const bool allocated_ok = image_pixel_data.allocate_pixels(
        width, height, number_of_channels, pixel_data_type);
    if (allocated_ok == false) {
        MMSOLVER_MAYA_ERR("mmsolver::ImageCache: read_image_file: "
                          << "Could not allocate pixel data!");
        return nullptr;
    }
    assert(image_pixel_data.is_valid() == true);
    assert(image_pixel_data.byte_count() == pixel_data_byte_count);
    std::memcpy(image_pixel_data.pixel_data(), maya_owned_pixel_data,
                pixel_data_byte_count);

    const bool cpu_inserted = image_cache.cpu_insert(key, image_pixel_data);
    MMSOLVER_MAYA_VRB("mmsolver::ImageCache: read_image_file: "
                      << "cpu_inserted=" << cpu_inserted);

    MMSOLVER_MAYA_VRB("mmsolver::ImageCache: read_image_file DONE2:"
                      << " texture=" << texture_data.texture());

    return texture_data.texture();
}

bool ImageCache::cpu_insert(const CPUCacheKey &key,
                            const CPUCacheValue &image_pixel_data) {
    const bool verbose = false;

    MMSOLVER_MAYA_VRB("mmsolver::ImageCache::cpu_insert: "
                      << "key=" << key);

    const CPUMapIt search = m_cpu_cache_map.find(key);
    const bool found = search != m_cpu_cache_map.end();
    if (found) {
        ImageCache::cpu_erase(key);
    }

    // If we are at capacity, make room for new entry.
    const size_t image_data_size = image_pixel_data.byte_count();
    const bool evict_ok =
        ImageCache::cpu_evict_enough_for_new_entry(image_data_size);
    if (!evict_ok) {
        MMSOLVER_MAYA_WRN(
            "mmsolver::ImageCache::cpu_insert: evicting memory failed!");
    }

    m_cpu_used_bytes += image_data_size;
    assert(m_cpu_used_bytes <= m_cpu_capacity_bytes);

    // Because we are inserting into the cache, the 'key' is the
    // most-recently-used item.
    CPUKeyListIt key_iterator =
        m_cpu_cache_key_list.insert(m_cpu_cache_key_list.end(), key);

    const auto pair = m_cpu_cache_map.insert(
        std::make_pair(key, std::make_pair(key_iterator, image_pixel_data)));

    const auto inserted_key_iterator = pair.first;
    const bool ok = pair.second;
    assert(ok == true);
    return ok;
}

void update_texture(MTexture *texture,
                    const ImageCache::CPUCacheValue &image_pixel_data) {
    const bool verbose = false;

    // No need for MIP-maps.
    const bool generate_mip_maps = false;

    // TODO: If the 'texture_desc' is different than the
    // current texture, it cannot be updated, and must be
    // released and a new texture created instead.

    // The default value of this argument is 0. This means to
    // use the texture's "width * number of bytes per pixel".
    uint32_t rowPitch = 0;

    MHWRender::MTextureUpdateRegion *region = nullptr;
    void *pixel_data = image_pixel_data.pixel_data();
    MStatus status =
        texture->update(pixel_data, generate_mip_maps, rowPitch, region);
    CHECK_MSTATUS(status);
}

ImageCache::GPUCacheValue ImageCache::gpu_insert(
    MHWRender::MTextureManager *texture_manager, const GPUCacheKey &key,
    const ImageCache::CPUCacheValue &image_pixel_data) {
    assert(texture_manager != nullptr);
    assert(image_pixel_data.is_valid());
    const bool verbose = false;

    MMSOLVER_MAYA_VRB("mmsolver::ImageCache::gpu_insert: "
                      << "key=" << key);

    GPUCacheValue texture_data = GPUCacheValue();
    const ImageCache::GPUMapIt search = m_gpu_cache_map.find(key);
    const bool found = search != m_gpu_cache_map.end();
    if (!found) {
        // If we are at capacity, make room for new entry.
        const size_t image_data_size = image_pixel_data.byte_count();
        const bool evict_ok = ImageCache::gpu_evict_enough_for_new_entry(
            texture_manager, image_data_size);
        if (!evict_ok) {
            MMSOLVER_MAYA_WRN(
                "mmsolver::ImageCache::gpu_insert: evicting memory failed!");
        }

        const bool allocate_ok = texture_data.allocate_texture(
            texture_manager, image_pixel_data.pixel_data(),
            image_pixel_data.width(), image_pixel_data.height(),
            image_pixel_data.num_channels(),
            image_pixel_data.pixel_data_type());
        if (!allocate_ok) {
            MMSOLVER_MAYA_ERR(
                "mmsolver::ImageCache: gpu_insert: "
                "Could not allocate texture!");
        }

        if (!texture_data.is_valid()) {
            return GPUCacheValue();
        }

        m_gpu_used_bytes += texture_data.byte_count();
        assert(m_gpu_used_bytes <= m_gpu_capacity_bytes);

        // Make 'key' the most-recently-used key, because when we
        // insert an item into the cache, it's used most recently.
        ImageCache::GPUKeyListIt key_iterator =
            m_gpu_cache_key_list.insert(m_gpu_cache_key_list.end(), key);

        // Create the key-value entry, linked to the usage record.
        const auto pair = m_gpu_cache_map.insert(
            std::make_pair(key, std::make_pair(key_iterator, texture_data)));

        const auto inserted_key_iterator = pair.first;
        const bool ok = pair.second;
        assert(ok == true);
    } else {
        ImageCache::GPUKeyListIt iterator = search->second.first;
        texture_data = search->second.second;
        if (!texture_data.is_valid()) {
            MMSOLVER_MAYA_ERR(
                "mmsolver::ImageCache: gpu_insert: "
                "Found texture is invalid!");
            return ImageCache::GPUCacheValue();
        }

        move_iterator_to_back_of_key_list(m_gpu_cache_key_list, iterator);

        update_texture(texture_data.texture(), image_pixel_data);
    }

    return texture_data;
}

ImageCache::GPUCacheValue ImageCache::gpu_find(const GPUCacheKey &key) {
    const bool verbose = false;

    MMSOLVER_MAYA_VRB("mmsolver::ImageCache::gpu_find: "
                      << "key=" << key);

    const GPUMapIt search = m_gpu_cache_map.find(key);
    const bool found = search != m_gpu_cache_map.end();
    if (found) {
        GPUKeyListIt iterator = search->second.first;
        GPUCacheValue value = search->second.second;
        move_iterator_to_back_of_key_list(m_gpu_cache_key_list, iterator);
        return value;
    }
    return GPUCacheValue();
}

ImageCache::CPUCacheValue ImageCache::cpu_find(const CPUCacheKey &key) {
    const bool verbose = false;

    MMSOLVER_MAYA_VRB("mmsolver::ImageCache::cpu_find: "
                      << "key=" << key);

    const CPUMapIt search = m_cpu_cache_map.find(key);
    const bool found = search != m_cpu_cache_map.end();
    if (found) {
        CPUKeyListIt iterator = search->second.first;
        CPUCacheValue value = search->second.second;
        move_iterator_to_back_of_key_list(m_cpu_cache_key_list, iterator);
        return value;
    }
    return CPUCacheValue();
}

bool ImageCache::gpu_evict_one(MHWRender::MTextureManager *texture_manager) {
    const bool verbose = false;

    MMSOLVER_MAYA_VRB("mmsolver::ImageCache::gpu_evict_one: ");

    MMSOLVER_MAYA_VRB(
        "mmsolver::ImageCache::gpu_evict_one: "
        "before m_gpu_used_bytes="
        << m_gpu_used_bytes);

    assert(texture_manager != nullptr);
    if (m_gpu_cache_key_list.empty()) {
        return false;
    }

    const GPUCacheKey lru_key = m_gpu_cache_key_list.front();
    const GPUMapIt lru_key_iterator = m_gpu_cache_map.find(lru_key);
    assert(lru_key_iterator != m_gpu_cache_map.end());

    GPUCacheValue texture_data = lru_key_iterator->second.second;
    m_gpu_used_bytes -= texture_data.byte_count();
    texture_data.deallocate_texture(texture_manager);

    m_gpu_cache_map.erase(lru_key_iterator);
    m_gpu_cache_key_list.pop_front();

    MMSOLVER_MAYA_VRB(
        "mmsolver::ImageCache::gpu_evict_one: "
        "after m_gpu_used_bytes="
        << m_gpu_used_bytes);
    return true;
}

bool ImageCache::cpu_evict_one() {
    const bool verbose = false;

    MMSOLVER_MAYA_VRB("mmsolver::ImageCache::cpu_evict_one: ");

    MMSOLVER_MAYA_VRB(
        "mmsolver::ImageCache::cpu_evict_one: "
        "before m_cpu_used_bytes="
        << m_cpu_used_bytes);

    if (m_cpu_cache_key_list.empty()) {
        return false;
    }

    const CPUCacheKey lru_key = m_cpu_cache_key_list.front();
    const CPUMapIt lru_key_iterator = m_cpu_cache_map.find(lru_key);
    assert(lru_key_iterator != m_cpu_cache_map.end());

    CPUCacheValue image_pixel_data = lru_key_iterator->second.second;
    m_cpu_used_bytes -= image_pixel_data.byte_count();
    image_pixel_data.deallocate_pixels();

    m_cpu_cache_map.erase(lru_key_iterator);
    m_cpu_cache_key_list.pop_front();

    MMSOLVER_MAYA_VRB(
        "mmsolver::ImageCache::cpu_evict_one: "
        "after m_cpu_used_bytes="
        << m_cpu_used_bytes);
    return true;
}

bool ImageCache::gpu_evict_enough_for_new_entry(
    MHWRender::MTextureManager *texture_manager,
    const size_t new_memory_chunk_size) {
    const bool verbose = false;

    MMSOLVER_MAYA_VRB("mmsolver::ImageCache::gpu_evict_enough_for_new_entry: ");

    if (m_gpu_cache_key_list.empty()) {
        return false;
    }

    // If we are at capacity remove the least recently used items
    // until we have enough room to store 'new_memory_chunk_size'.
    size_t new_used_bytes = m_gpu_used_bytes + new_memory_chunk_size;
    MMSOLVER_MAYA_VRB(
        "mmsolver::ImageCache::gpu_evict_enough_for_new_entry: "
        "new_used_bytes="
        << new_used_bytes);
    while (new_used_bytes > m_gpu_capacity_bytes) {
        const bool ok = ImageCache::gpu_evict_one(texture_manager);
        if (!ok) {
            break;
        }
        new_used_bytes = m_gpu_used_bytes + new_memory_chunk_size;
        MMSOLVER_MAYA_VRB(
            "mmsolver::ImageCache::gpu_evict_enough_for_new_entry: "
            "new_used_bytes="
            << new_used_bytes);
    }

    return true;
}

bool ImageCache::cpu_evict_enough_for_new_entry(
    const size_t new_memory_chunk_size) {
    const bool verbose = false;

    MMSOLVER_MAYA_VRB("mmsolver::ImageCache::cpu_evict_enough_for_new_entry: ");

    if (m_cpu_cache_key_list.empty()) {
        return false;
    }

    // If we are at capacity remove the least recently used items
    // until we have enough room to store 'new_memory_chunk_size'.
    size_t new_used_bytes = m_cpu_used_bytes + new_memory_chunk_size;
    MMSOLVER_MAYA_VRB(
        "mmsolver::ImageCache::cpu_evict_enough_for_new_entry: "
        "new_used_bytes="
        << new_used_bytes);
    while (new_used_bytes > m_cpu_capacity_bytes) {
        const bool ok = ImageCache::cpu_evict_one();
        if (!ok) {
            break;
        }
        new_used_bytes = m_cpu_used_bytes + new_memory_chunk_size;
        MMSOLVER_MAYA_VRB(
            "mmsolver::ImageCache::cpu_evict_enough_for_new_entry: "
            "new_used_bytes="
            << new_used_bytes);
    }

    return true;
}

bool ImageCache::gpu_erase(MHWRender::MTextureManager *texture_manager,
                           const GPUCacheKey &key) {
    const bool verbose = false;

    MMSOLVER_MAYA_VRB("mmsolver::ImageCache::gpu_erase: ");

    const GPUMapIt search = m_gpu_cache_map.find(key);
    const bool found = search != m_gpu_cache_map.end();
    if (found) {
        GPUCacheValue texture_data = search->second.second;
        m_gpu_used_bytes -= texture_data.byte_count();
        texture_data.deallocate_texture(texture_manager);

        m_gpu_cache_map.erase(search);

        // NOTE: This is a O(n) linear operation, and can be very
        // slow since the list items is spread out in memory.
        m_gpu_cache_key_list.remove(key);
    }
    return found;
}

bool ImageCache::cpu_erase(const CPUCacheKey &key) {
    const bool verbose = false;

    MMSOLVER_MAYA_VRB("mmsolver::ImageCache::cpu_erase: ");

    const CPUMapIt search = m_cpu_cache_map.find(key);
    const bool found = search != m_cpu_cache_map.end();
    if (found) {
        CPUCacheValue image_pixel_data = search->second.second;
        m_cpu_used_bytes -= image_pixel_data.byte_count();
        image_pixel_data.deallocate_pixels();

        m_cpu_cache_map.erase(search);

        // NOTE: This is a O(n) linear operation, and can be very
        // slow since the list items is spread out in memory.
        m_cpu_cache_key_list.remove(key);
    }
    return found;
}

}  // namespace mmsolver
