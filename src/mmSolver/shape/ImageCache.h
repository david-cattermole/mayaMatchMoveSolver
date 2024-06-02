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
#include <algorithm>
#include <list>
#include <string>
#include <unordered_map>

// Maya
#include <maya/MImage.h>
#include <maya/MString.h>

// Maya Viewport 2.0
#include <maya/MTextureManager.h>

// MM Solver
#include <mmcore/lib.h>

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

    bool allocate_pixels(const uint32_t width, const uint32_t height,
                         const uint8_t num_channels,
                         const CachePixelDataType pixel_data_type) {
        m_width = width;
        m_height = height;
        m_num_channels = num_channels;
        m_pixel_data_type = pixel_data_type;

        const size_t pixel_data_byte_count = CacheImagePixelData::byte_count();

        if (pixel_data_byte_count == 0) {
            MMSOLVER_MAYA_ERR("mmsolver::CacheImagePixelData:allocate_pixels: "
                              << "Invalid image size for allocating pixel data!"
                              << " width=" << m_width << " height=" << m_height
                              << " num_channels=" << m_num_channels
                              << " pixel_data_type="
                              << static_cast<int>(m_pixel_data_type));
            return false;
        }

        bool ok = false;
        void *data = std::malloc(pixel_data_byte_count);
        if (data) {
            m_pixel_data = data;
            ok = true;
        } else {
            ok = false;
            MMSOLVER_MAYA_ERR(
                "mmsolver::CacheImagePixelData:allocate_pixels: "
                << "Could not allocate pixel data!"
                << " requested=" << pixel_data_byte_count << "B"
                << " requested="
                << (static_cast<float>(pixel_data_byte_count) * 1e-6) << "MB");
        }

        return ok;
    }

    void deallocate_pixels() { std::free(m_pixel_data); }

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

    size_t byte_count() const {
        const uint8_t bytes_per_channel =
            convert_pixel_data_type_to_bytes_per_channel(m_pixel_data_type);
        return m_width * m_height * m_num_channels * bytes_per_channel;
    }

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
// Least-Recently-Used (LRU) Cache using standard C++11 data
// structures.
//
// Inspired by:
// https://web.archive.org/web/20161203001546/http://timday.bitbucket.org/lru.html
//
// Singleton design pattern for C++11:
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
//
// TODO: Support converting to 8-bit LDR image pixels before
// storing. For example converting to sRGB colour space.
//
struct ImageCache {
    using GPUCacheKey = std::string;
    using GPUCacheValue = MTexture *;
    using GPUKeyList = std::list<GPUCacheKey>;
    using GPUKeyListIt = GPUKeyList::iterator;
    using GPUMap =
        std::unordered_map<GPUCacheKey, std::pair<GPUKeyListIt, GPUCacheValue>>;
    using GPUMapIt = GPUMap::iterator;

    using CPUCacheKey = std::string;
    using CPUCacheValue = CacheImagePixelData;
    using CPUKeyList = std::list<CPUCacheKey>;
    using CPUKeyListIt = CPUKeyList::iterator;
    using CPUMap =
        std::unordered_map<CPUCacheKey, std::pair<CPUKeyListIt, CPUCacheValue>>;
    using CPUMapIt = CPUMap::iterator;

public:
    static ImageCache &getInstance() {
        static ImageCache instance;  // Guaranteed to be destroyed.
                                     // Instantiated on first use.
        return instance;
    }

private:
    // Constructor. The {} brackets are needed here.
    ImageCache() : m_cpu_capacity(1), m_gpu_capacity(1) {}

    template <typename KeyList, typename KeyListIt>
    void move_iterator_to_back_of_key_list(KeyList &key_list,
                                           KeyListIt key_list_iterator) {
        // The back of the list is the "most recently used" key.
        key_list.splice(key_list.end(), key_list, key_list_iterator);
    }

public:
    // TODO: Set/Get GPU memory allowed.
    // TODO: Set/Get CPU memory allowed.
    size_t get_gpu_capacity() const {
        const bool verbose = false;
        MMSOLVER_MAYA_VRB("mmsolver::ImageCache::get_cpu_capacity: "
                          << "m_cpu_capacity=" << m_cpu_capacity);

        return m_gpu_capacity;
    }
    size_t get_cpu_capacity() const {
        const bool verbose = false;

        MMSOLVER_MAYA_VRB("mmsolver::ImageCache::get_gpu_capacity: "
                          << "m_gpu_capacity=" << m_gpu_capacity);

        return m_cpu_capacity;
    }

    void set_gpu_capacity(const size_t capacity) {
        const bool verbose = false;

        // TODO: Evict the contents of the cache, if the current
        // number of cached items exceeds the new capacity size.
        m_gpu_capacity = capacity;

        MMSOLVER_MAYA_VRB("mmsolver::ImageCache::set_gpu_capacity: "
                          << "m_gpu_capacity=" << m_gpu_capacity);
    }

    void set_cpu_capacity(const size_t capacity) {
        const bool verbose = false;

        // TODO: Evict the contents of the cache, if the current
        // number of cached items exceeds the new capacity size.
        m_cpu_capacity = capacity;

        MMSOLVER_MAYA_VRB("mmsolver::ImageCache::set_cpu_capacity: "
                          << "m_cpu_capacity=" << m_cpu_capacity);
    }

    // TODO: Set/Get Disk space allowed.
    //
    // TODO: Set/Get Disk cache location. Used to find disk-cached
    // files. This should be a directory on a very fast disk.

    // Insert pixels into CPU cache.
    //
    // If the key is already in the image cache, the previous value is
    // erased.
    //
    // Returns true/false, if the the data was inserted or not.
    bool cpu_insert(const CPUCacheKey &key,
                    const CPUCacheValue &image_pixel_data) {
        const bool verbose = false;

        MMSOLVER_MAYA_VRB("mmsolver::ImageCache::cpu_insert: "
                          << "key=" << key);

        const CPUMapIt search = m_cpu_cache_map.find(key);

        const bool found = search != m_cpu_cache_map.end();
        if (found) {
            ImageCache::cpu_erase(key);
        }

        // 'key' is the most-recently-used key.
        CPUKeyListIt key_iterator =
            m_cpu_cache_key_list.insert(m_cpu_cache_key_list.end(), key);

        const auto pair = m_cpu_cache_map.insert(std::make_pair(
            key, std::make_pair(key_iterator, image_pixel_data)));

        const auto inserted_key_iterator = pair.first;
        const bool ok = pair.second;
        assert(ok == true);
        return ok;
    }

    // Insert and upload some pixels to the GPU and cache the result.
    //
    // Returns the GPUCacheValue inserted into the GPU cache.
    GPUCacheValue gpu_insert(MHWRender::MTextureManager *texture_manager,
                             const GPUCacheKey &key,
                             const CPUCacheValue &image_pixel_data) {
        assert(texture_manager != nullptr);
        assert(image_pixel_data.is_valid());
        const bool verbose = false;

        MMSOLVER_MAYA_VRB("mmsolver::ImageCache::gpu_insert: "
                          << "key=" << key);

        // No need for MIP-maps.
        const bool generate_mip_maps = false;

        MTexture *texture = nullptr;
        const GPUMapIt search = m_gpu_cache_map.find(key);
        const bool found = search != m_gpu_cache_map.end();
        if (!found) {
            // If we are at capacity, make room for new entry.
            if (m_gpu_cache_map.size() >= m_gpu_capacity) {
                ImageCache::gpu_evict_one(texture_manager);
            }

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

            // Make 'key' the most-recently-used key.
            GPUKeyListIt key_iterator =
                m_gpu_cache_key_list.insert(m_gpu_cache_key_list.end(), key);

            // Create the key-value entry, linked to the usage record.
            const auto pair = m_gpu_cache_map.insert(
                std::make_pair(key, std::make_pair(key_iterator, texture)));

            const auto inserted_key_iterator = pair.first;
            const bool ok = pair.second;
            assert(ok == true);

        } else {
            GPUKeyListIt iterator = search->second.first;
            texture = search->second.second;
            if (texture == nullptr) {
                MMSOLVER_MAYA_ERR(
                    "mmsolver::ImageCache: gpu_insert: "
                    "Found texture is invalid!");
                return false;
            }

            move_iterator_to_back_of_key_list(m_gpu_cache_key_list, iterator);

            // TODO: If the 'texture_desc' is different than the
            // current texture, it cannot be updated, and must be
            // released and a new texture created instead.

            // The default value of this argument is 0. This means to
            // use the texture's "width * number of bytes per pixel".
            uint32_t rowPitch = 0;

            MHWRender::MTextureUpdateRegion *region = nullptr;
            void *pixel_data = image_pixel_data.pixel_data();
            MStatus status = texture->update(pixel_data, generate_mip_maps,
                                             rowPitch, region);
            CHECK_MSTATUS(status);
        }

        return texture;
    }

    // Find the key in the GPU cache.
    //
    // Returns the GPUCacheValue at the key, or nullptr.
    GPUCacheValue gpu_find(const GPUCacheKey &key) {
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
        return nullptr;
    }

    // Find the key in the CPU cache.
    //
    // Returns the CPUCacheValue at the key, or constructs a default
    // value and returns it.
    CPUCacheValue cpu_find(const CPUCacheKey &key) {
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

    // Evict the least recently used item from the GPU cache.
    //
    // Returns true/false, if an item was removed from the cache or
    // not.
    bool gpu_evict_one(MHWRender::MTextureManager *texture_manager) {
        const bool verbose = false;

        MMSOLVER_MAYA_VRB("mmsolver::ImageCache::gpu_evict_one: ");

        assert(texture_manager != nullptr);
        if (m_gpu_cache_key_list.empty()) {
            return false;
        }

        const GPUCacheKey lru_key = m_gpu_cache_key_list.front();
        const GPUMapIt lru_key_iterator = m_gpu_cache_map.find(lru_key);
        assert(lru_key_iterator != m_gpu_cache_map.end());

        GPUCacheValue texture = lru_key_iterator->second.second;
        texture_manager->releaseTexture(texture);

        m_gpu_cache_map.erase(lru_key_iterator);
        m_gpu_cache_key_list.pop_front();
        return true;
    }

    // Evict the least recently used item from the CPU cache.
    //
    // Returns true/false, if an item was removed from the cache or
    // not.
    bool cpu_evict_one() {
        const bool verbose = false;

        MMSOLVER_MAYA_VRB("mmsolver::ImageCache::cpu_evict_one: ");

        if (m_cpu_cache_key_list.empty()) {
            return false;
        }

        const CPUCacheKey lru_key = m_cpu_cache_key_list.front();
        const CPUMapIt lru_key_iterator = m_cpu_cache_map.find(lru_key);
        assert(lru_key_iterator != m_cpu_cache_map.end());

        CPUCacheValue value = lru_key_iterator->second.second;
        value.deallocate_pixels();

        m_cpu_cache_map.erase(lru_key_iterator);
        m_cpu_cache_key_list.pop_front();
        return true;
    }

    // Remove the key from the image GPU cache.
    //
    // NOTE: Due to the way the LRU cache works, this can be quite
    // slow to to remove a specific key from the cache.
    //
    // Returns true/false, if the key was removed or not.
    bool gpu_erase(MHWRender::MTextureManager *texture_manager,
                   const GPUCacheKey &key) {
        const bool verbose = false;

        MMSOLVER_MAYA_VRB("mmsolver::ImageCache::gpu_erase: ");

        const GPUMapIt search = m_gpu_cache_map.find(key);
        const bool found = search != m_gpu_cache_map.end();
        if (found) {
            GPUCacheValue value = search->second.second;

            assert(texture_manager != nullptr);
            texture_manager->releaseTexture(value);

            m_gpu_cache_map.erase(search);

            // NOTE: This is a O(n) linear operation, and can be very
            // slow since the list items is spread out in memory.
            m_gpu_cache_key_list.remove(key);
        }
        return found;
    }

    // Remove the key from the image CPU cache.
    //
    // NOTE: Due to the way the LRU cache works, this can be quite
    // slow to to remove a specific key from the cache.
    //
    // Returns true/false, if the key was removed or not.
    bool cpu_erase(const CPUCacheKey &key) {
        const bool verbose = false;

        MMSOLVER_MAYA_VRB("mmsolver::ImageCache::cpu_erase: ");

        const CPUMapIt search = m_cpu_cache_map.find(key);
        const bool found = search != m_cpu_cache_map.end();
        if (found) {
            CPUCacheValue value = search->second.second;
            value.deallocate_pixels();

            m_cpu_cache_map.erase(search);

            // NOTE: This is a O(n) linear operation, and can be very
            // slow since the list items is spread out in memory.
            m_cpu_cache_key_list.remove(key);
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
    // A Map of keys to values.
    //
    // An unordered hash map is used to map file path strings to CPU
    // Image Data and GPU texture resources.
    //
    // These maps also contain pointers into the 'key list' data
    // structures, allowing us to map from the values to the 'key
    // list's.
    GPUMap m_gpu_cache_map;
    CPUMap m_cpu_cache_map;

    // List of keys.
    //
    // A double-ended linked list (std::list) is used because we want
    // to be able to push/pop and access the (front/back) ends of the
    // list as fast as possible.
    //
    // Additionally, the linked list ensure that the pointers of each
    // item in the list stays consistent over time, so that pointers
    // into the memory can be used directly without fear that the
    // underlying memory will be cleared.
    //
    // The 'front' of the list is the "least recently used" key.  The
    // 'back' of the list is the "most recently used" key.
    GPUKeyList m_gpu_cache_key_list;
    CPUKeyList m_cpu_cache_key_list;

    // Number of items allowed in the cache.
    size_t m_gpu_capacity;
    size_t m_cpu_capacity;

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
