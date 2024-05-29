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

#ifndef MM_IMAGE_CACHE_H
#define MM_IMAGE_CACHE_H

// STL
#include <string>
#include <unordered_map>

// Maya
#include <maya/MImage.h>
#include <maya/MString.h>

// Maya Viewport 2.0
#include <maya/MTextureManager.h>

// MM Solver
#include <mmcore/lib.h>

#include "ImagePlaneShapeNode.h"
#include "mmSolver/utilities/debug_utils.h"

namespace mmsolver {

enum class CachePixelDataType : uint8_t {
    kU8 = 0,
    kF32,

    // Always the second to last, so it's equal to the number of
    // options.
    kCount,

    // When the pixel data type is not initialized or invalid.
    kUnknown = 255,
};

static uint8_t convert_pixel_data_type_to_bytes_per_channel(
    CachePixelDataType pixel_data_type) {
    uint8_t bytes_per_channel = 0;
    if (pixel_data_type == CachePixelDataType::kU8) {
        // 8-bit unsigned integers use 1 byte.
        bytes_per_channel = 1;
    } else if (pixel_data_type == CachePixelDataType::kF32) {
        // 32-bit floats use 4 bytes.
        bytes_per_channel = 4;
    } else {
        bytes_per_channel = 0;
        MMSOLVER_MAYA_ERR("mmsolver::ImageCache: get_mimage_pixel_data: "
                          << "Invalid pixel type is "
                          << static_cast<int>(pixel_data_type));
    }
    return bytes_per_channel;
}

static MHWRender::MRasterFormat convert_pixel_data_type_to_texture_format(
    const CachePixelDataType pixel_data_type) {
    if (pixel_data_type == CachePixelDataType::kU8) {
        // Assumes the 8-bit data is "RGBA".
        return MHWRender::kR8G8B8A8_UNORM;
    } else if (pixel_data_type == CachePixelDataType::kF32) {
        return MHWRender::kR32G32B32A32_FLOAT;
    }

    return MHWRender::MRasterFormat();
}

struct CacheImagePixelData {
    CacheImagePixelData()
        : m_pixel_data(nullptr)
        , m_width(0)
        , m_height(0)
        , m_num_channels(0)
        , m_pixel_data_type(CachePixelDataType::kUnknown){};

    CacheImagePixelData(void *pixel_data, const uint32_t width,
                        const uint32_t height, const uint8_t num_channels,
                        const CachePixelDataType pixel_data_type)
        : m_pixel_data(pixel_data)
        , m_width(width)
        , m_height(height)
        , m_num_channels(num_channels)
        , m_pixel_data_type(pixel_data_type){};

    ~CacheImagePixelData() = default;

    bool is_valid() const {
        return (m_pixel_data != nullptr) && (m_width != 0) && (m_height != 0) &&
               (m_num_channels != 0) &&
               (m_pixel_data_type != CachePixelDataType::kUnknown);
    };

    void *pixel_data() const { return m_pixel_data; };
    uint32_t width() const { return m_width; }
    uint32_t height() const { return m_height; }
    uint8_t num_channels() const { return m_num_channels; }
    CachePixelDataType pixel_data_type() const { return m_pixel_data_type; }

private:
    void *m_pixel_data;
    uint32_t m_width;
    uint32_t m_height;
    uint8_t m_num_channels;
    CachePixelDataType m_pixel_data_type;
};

// The ImageCache, used to load and cache images into GPU, CPU and
// Disk.
//
// Singleton design pattern for C++11
// https://stackoverflow.com/a/1008289
//
// TODO: Use 4 layers of reading textures.
//
// Layer 0: The texture is GPU memory, in the
// MHWRender::MTextureManager. If the texture is not in GPU memory,
// look in the (CPU) Image Cache.
//
// Layer 1: The texture pixel data is stored in RAM, in the (CPU)
// Image Cache. If the texture pixel data cannot be found in the Image
// Cache, look in the Disk Cache.
//
// Layer 2: The texture pixel data is stored on disk in a fast-to-read
// (8-bit) image format (https://qoiformat.org/
// https://crates.io/crates/qoi) which as been converted to sRGB
// colour space. If the file cannot be found, read the original file
// path.
//
// Layer 3: The original file path should be read and decoded, and
// then placed into a queue to be saved into the disk cache. The queue
// of images are processed off the main thread, so that the
// interactive session does not slow down.

// TODO: Read image (and insert into cache).
//
// TODO: Set/Get CPU memory allowed.
//
// TODO: Set/Get GPU memory allowed.
//
// TODO: Set/Get Disk space allowed.
//
// TODO: Set/Get Disk cache location. Used to find disk-cached
// files. This should be a directory on a very fast disk.
//
// TODO: Support converting to 8-bit LDR image pixels before
// storing. For example converting to sRGB colour space.
struct ImageCache {
    using CPUCacheKey = std::string;
    using GPUCacheKey = std::string;
    using CPUMap = std::unordered_map<CPUCacheKey, CacheImagePixelData>;
    using GPUMap = std::unordered_map<GPUCacheKey, MTexture *>;

public:
    static ImageCache &getInstance() {
        static ImageCache instance;  // Guaranteed to be destroyed.
                                     // Instantiated on first use.
        return instance;
    }

private:
    // Constructor. The {} brackets are needed here.
    ImageCache() {}

public:
    // Insert pixels into image CPU cache.
    //
    // If the key is already in the image cache, the previous value is
    // erased.
    bool cpu_insert(const CPUCacheKey &key,
                    const CacheImagePixelData &image_pixel_data) {
        auto search = m_cpu_cache_map.find(key);

        const bool found = search != m_cpu_cache_map.end();
        if (found) {
            ImageCache::cpu_erase(key);
        }

        const bool ok = m_cpu_cache_map.insert({key, image_pixel_data}).second;
        return ok;
    }

    // Insert
    MTexture *gpu_insert(MHWRender::MTextureManager *texture_manager,
                         const GPUCacheKey &key,
                         const CacheImagePixelData &image_pixel_data) {
        assert(texture_manager != nullptr);
        assert(image_pixel_data.is_valid());
        const bool verbose = false;

        // No need for MIP-maps.
        const bool generate_mip_maps = false;

        MTexture *texture = nullptr;
        auto search = m_gpu_cache_map.find(key);
        const bool found = search != m_gpu_cache_map.end();
        if (!found) {
            const uint32_t width = image_pixel_data.width();
            const uint32_t height = image_pixel_data.height();
            const uint8_t number_of_channels = image_pixel_data.num_channels();
            const CachePixelDataType pixel_data_type =
                image_pixel_data.pixel_data_type();
            const uint8_t bytes_per_channel =
                convert_pixel_data_type_to_bytes_per_channel(pixel_data_type);
            void *pixel_data = image_pixel_data.pixel_data();

            MHWRender::MTextureDescription texture_desc;
            texture_desc.setToDefault2DTexture();
            texture_desc.fWidth = width;
            texture_desc.fHeight = height;
            texture_desc.fDepth = 1;

            texture_desc.fMipmaps = 1;
            texture_desc.fArraySlices = 1;
            texture_desc.fTextureType = MHWRender::kImage2D;
            texture_desc.fFormat =
                convert_pixel_data_type_to_texture_format(pixel_data_type);

            texture_desc.fBytesPerRow =
                number_of_channels * bytes_per_channel * width;
            texture_desc.fBytesPerSlice = texture_desc.fBytesPerRow * height;

            MMSOLVER_MAYA_VRB("mmsolver::ImageCache: gpu_insert: "
                              << "width=" << width << " height=" << height
                              << " number_of_channels="
                              << static_cast<int>(number_of_channels));
            MMSOLVER_MAYA_VRB("mmsolver::ImageCache: gpu_insert: "
                              << "bytes_per_channel="
                              << static_cast<int>(bytes_per_channel));
            MMSOLVER_MAYA_VRB("mmsolver::ImageCache: gpu_insert: "
                              << "pixel_data_type="
                              << static_cast<int>(pixel_data_type));
            MMSOLVER_MAYA_VRB("mmsolver::ImageCache: gpu_insert: "
                              << "pixel_data=" << pixel_data);

            MMSOLVER_MAYA_VRB("mmsolver::ImageCache: gpu_insert:"
                              << " fBytesPerRow=" << texture_desc.fBytesPerRow
                              << " fBytesPerSlice="
                              << texture_desc.fBytesPerSlice);

            // If the texture name provided is an empty string then the
            // texture will not be cached as part of the internal texture
            // caching system. Thus each such call to this method will
            // create a new texture.
            texture = texture_manager->acquireTexture(
                m_empty_string, texture_desc, pixel_data, generate_mip_maps);
            if (texture == nullptr) {
                MMSOLVER_MAYA_ERR(
                    "mmsolver::ImageCache: gpu_insert: "
                    "Could not acquire texture!");
                return false;
            }

        } else {
            texture = search->second;
            if (texture == nullptr) {
                MMSOLVER_MAYA_ERR(
                    "mmsolver::ImageCache: gpu_insert: "
                    "Found texture is invalid!");
                return false;
            }

            m_gpu_cache_map.erase(search);

            // TODO: If the 'texture_desc' is different than the
            // current texture, it cannot be updated, and must be
            // released and a new texture created instead.
            // // ImageCache::gpu_erase(key);

            // The default value of this argument is 0. This means to use
            // the texture's width * the number of bytes per pixel.
            uint32_t rowPitch = 0;

            MHWRender::MTextureUpdateRegion *region = nullptr;
            void *pixel_data = image_pixel_data.pixel_data();
            MStatus status = texture->update(pixel_data, generate_mip_maps,
                                             rowPitch, region);
            CHECK_MSTATUS(status);
        }

        const bool ok = m_gpu_cache_map.insert({key, texture}).second;
        assert(ok == true);
        return texture;
    }

    // Find the key in the image GPU cache.
    MTexture *gpu_find(const GPUCacheKey &key) {
        auto search = m_gpu_cache_map.find(key);
        const bool found = search != m_gpu_cache_map.end();
        if (found) {
            return search->second;
        }
        return nullptr;
    }

    // Find the key in the image CPU cache.
    CacheImagePixelData cpu_find(const CPUCacheKey &key) {
        auto search = m_cpu_cache_map.find(key);
        const bool found = search != m_cpu_cache_map.end();
        if (found) {
            return search->second;
        }
        return CacheImagePixelData();
    }

    // Remove the key from the image GPU cache.
    bool gpu_erase(MHWRender::MTextureManager *texture_manager,
                   const GPUCacheKey &key) {
        const auto search = m_gpu_cache_map.find(key);
        const bool found = search != m_gpu_cache_map.end();
        if (found) {
            MTexture *texture = search->second;

            assert(texture_manager != nullptr);
            texture_manager->releaseTexture(texture);
            m_gpu_cache_map.erase(search);
        }
        return found;
    }

    // Remove the key from the image CPU cache.
    bool cpu_erase(const CPUCacheKey &key) {
        auto search = m_cpu_cache_map.find(key);
        const bool found = search != m_cpu_cache_map.end();
        if (found) {
            CacheImagePixelData value = search->second;
            // TODO: De-allocate the cache value. We must clear the
            // existing memory before adding the new pixel data.
            m_cpu_cache_map.erase(search);
        }
        return found;
    }

    // C++ 11; deleting the methods we don't want to ensure they can never be
    // used.
    //
    // Note: Scott Meyers mentions in his Effective Modern C++ book,
    // that deleted functions should generally be public as it results
    // in better error messages due to the compilers behavior to check
    // accessibility before deleted status.
    ImageCache(ImageCache const &) = delete;
    void operator=(ImageCache const &) = delete;

private:
    // TODO: Implement an LRU with standard C++.
    //
    // https://web.archive.org/web/20161203001546/http://timday.bitbucket.org/lru.html
    // https://bitbucket.org/timday/lru_cache/src/master/include/lru_cache_using_std.h
    //
    CPUMap m_cpu_cache_map;
    GPUMap m_gpu_cache_map;

    // Pre-allocated empty string to be re-used inside the class, to
    // avoid reallocations.
    MString m_empty_string;
};

MTexture *read_image_file(MHWRender::MTextureManager *texture_manager,
                          ImageCache &image_cache, MImage &temp_image,
                          const MString &file_path,
                          const MImage::MPixelType pixel_type,
                          const bool do_texture_update);

}  // namespace mmsolver

#endif  // MM_IMAGE_CACHE_H
