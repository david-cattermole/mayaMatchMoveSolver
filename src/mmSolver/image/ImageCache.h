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

#ifndef MM_SOLVER_IMAGE_IMAGE_CACHE_H
#define MM_SOLVER_IMAGE_IMAGE_CACHE_H

// STL
#include <algorithm>
#include <list>
#include <string>
#include <unordered_map>
// #include <unordered_set>

// Maya
#include <maya/MImage.h>
#include <maya/MString.h>

// Maya Viewport 2.0
#include <maya/MTextureManager.h>

// MM Solver
#include <mmcore/lib.h>

#include "ImagePixelData.h"
#include "PixelDataType.h"
#include "TextureData.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/number_utils.h"

namespace mmsolver {
namespace image {

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
// storing. For example converting to sRGB colour space, and applying
// tone-mapping to avoid clipping colours, so that as much detail is
// retained - even if it's not colour accurate.
//

enum class CacheEvictionResult : uint8_t { kSuccess = 0, kNotNeeded, kFailed };

struct ImageCache {
    // GPU data types
    using GPUCacheKey = std::string;
    using GPUCacheValue = TextureData;

    using GPUKeyList = std::list<GPUCacheKey>;
    using GPUKeyListIt = GPUKeyList::iterator;

    using GPUMap =
        std::unordered_map<GPUCacheKey, std::pair<GPUKeyListIt, GPUCacheValue>>;
    using GPUMapIt = GPUMap::iterator;

    // using GPUGroupKeySet = std::unordered_set<GPUCacheKey>;
    // using GPUGroupKeySetIt = GPUGroupKeySet::iterator;

    // using GPUCacheGroupKey = std::string;
    // using GPUGroupKeyMap = std::unordered_map<GPUCacheGroupKey,
    // GPUGroupKeySet>; using GPUGroupKeyMapIt = GPUGroupKeyMap::iterator;

    // CPU data types
    using CPUCacheKey = std::string;
    using CPUCacheValue = ImagePixelData;

    using CPUKeyList = std::list<CPUCacheKey>;
    using CPUKeyListIt = CPUKeyList::iterator;

    using CPUMap =
        std::unordered_map<CPUCacheKey, std::pair<CPUKeyListIt, CPUCacheValue>>;
    using CPUMapIt = CPUMap::iterator;

    // using CPUGroupKeySet = std::unordered_set<CPUCacheKey>;
    // using CPUGroupKeySetIt = CPUGroupKeySet::iterator;

    // using CPUCacheGroupKey = std::string;
    // using CPUGroupKeyMap = std::unordered_map<CPUCacheGroupKey,
    // CPUGroupKeySet>; using CPUGroupKeyMapIt = CPUGroupKeyMap::iterator;

public:
    static ImageCache &getInstance() {
        static ImageCache instance;  // Guaranteed to be destroyed.
                                     // Instantiated on first use.
        return instance;
    }

private:
    // Constructor. The {} brackets are needed here.
    ImageCache()
        : m_gpu_capacity_bytes(0)
        , m_cpu_capacity_bytes(0)
        , m_gpu_item_count_minumum(1)
        , m_cpu_item_count_minumum(1)
        , m_gpu_used_bytes(0)
        , m_cpu_used_bytes(0) {}

    template <typename KeyList, typename KeyListIt>
    void move_iterator_to_back_of_key_list(KeyList &key_list,
                                           KeyListIt key_list_iterator) {
        // The back of the list is the "most recently used" key.
        key_list.splice(key_list.end(), key_list, key_list_iterator);
    }

public:
    // Get the capacity of the cache.
    size_t get_gpu_capacity_bytes() const {
        const bool verbose = false;
        MMSOLVER_MAYA_VRB("mmsolver::ImageCache::get_gpu_capacity_bytes: "
                          << "m_gpu_capacity_bytes=" << m_gpu_capacity_bytes);
        return m_gpu_capacity_bytes;
    }
    size_t get_cpu_capacity_bytes() const {
        const bool verbose = false;
        MMSOLVER_MAYA_VRB("mmsolver::ImageCache::get_cpu_capacity_bytes: "
                          << "m_cpu_capacity_bytes=" << m_cpu_capacity_bytes);
        return m_cpu_capacity_bytes;
    }
    size_t get_gpu_used_bytes() const {
        const bool verbose = false;
        MMSOLVER_MAYA_VRB("mmsolver::ImageCache::get_gpu_used_bytes: "
                          << "m_gpu_used_bytes=" << m_gpu_used_bytes);
        return m_gpu_used_bytes;
    }
    size_t get_cpu_used_bytes() const {
        const bool verbose = false;
        MMSOLVER_MAYA_VRB("mmsolver::ImageCache::get_cpu_used_bytes: "
                          << "m_cpu_used_bytes=" << m_cpu_used_bytes);
        return m_cpu_used_bytes;
    }
    size_t get_gpu_item_count() const {
        const bool verbose = false;
        MMSOLVER_MAYA_VRB("mmsolver::ImageCache::get_gpu_item_count: "
                          << "m_gpu_cache_map.size()="
                          << m_gpu_cache_map.size());
        return m_gpu_cache_map.size();
    }
    size_t get_cpu_item_count() const {
        const bool verbose = false;
        MMSOLVER_MAYA_VRB("mmsolver::ImageCache::get_cpu_item_count: "
                          << "m_cpu_cache_map.size()="
                          << m_cpu_cache_map.size());
        return m_cpu_cache_map.size();
    }

    // Set the capacity of the cache.
    void set_gpu_capacity_bytes(MHWRender::MTextureManager *texture_manager,
                                const size_t value);
    void set_cpu_capacity_bytes(const size_t value);

    // Debug functions to display internals of the cache.
    MString generate_cache_brief_text() const;
    void print_cache_brief() const;

    // TODO: Set/Get Disk cache location. Used to find disk-cached
    // files. This should be a directory on a very fast disk.
    //
    // This class should allow a set of threads used for writing CPU
    // cache data to image files. These files should be very fast to
    // read into the CPU memory.
    //
    // We would need methods such as:
    //
    // bool write_cpu_item_to_disk(const CPUCacheKey &key, const bool
    // background=true);
    //
    // bool wait_for_disk_writes();
    //
    // bool disk_find(const DiskCacheKey &key);
    //
    // bool disk_find_file_path(const DiskCacheKey &key);

    // Insert pixels into CPU cache.
    //
    // If the key is already in the image cache, the previous value is
    // erased.
    //
    // Returns true/false, if the the data was inserted or not.
    bool cpu_insert(const CPUCacheKey &key,
                    const CPUCacheValue &image_pixel_data);

    // Insert and upload some pixels to the GPU and cache the result.
    //
    // Returns the GPUCacheValue inserted into the GPU cache.
    GPUCacheValue gpu_insert(MHWRender::MTextureManager *texture_manager,
                             const GPUCacheKey &key,
                             const CPUCacheValue &image_pixel_data);

    // Find the key in the GPU cache.
    //
    // Returns the GPUCacheValue at the key, or nullptr.
    GPUCacheValue gpu_find(const GPUCacheKey &key);

    // Find the key in the CPU cache.
    //
    // Returns the CPUCacheValue at the key, or constructs a default
    // value and returns it.
    CPUCacheValue cpu_find(const CPUCacheKey &key);

    // TODO: Add a 'gpu/cpu_prefetch()' method, used to add the images
    // into a prefetching queue.
    //
    // For the GPU, the images are uploaded to the GPU,
    // asynchronously.
    //
    // For the CPU, the images are read from disk cache, if they are
    // not in memory.
    //
    // There must also be a way to wait for all prefetched images to
    // be loaded before continuing - a "blocking" function call.

    // Evict the least recently used item from the GPU cache.
    //
    // Returns true/false, if an item was removed from the cache or
    // not.
    CacheEvictionResult gpu_evict_one(
        MHWRender::MTextureManager *texture_manager);

    // Evict the least recently used item from the CPU cache.
    //
    // Returns true/false, if an item was removed from the cache or
    // not.
    CacheEvictionResult cpu_evict_one();

    // Remove the key from the image GPU cache.
    //
    // NOTE: Due to the way the LRU cache works, this can be quite
    // slow to to remove a specific key from the cache.
    //
    // Returns true/false, if the key was removed or not.
    bool gpu_erase(MHWRender::MTextureManager *texture_manager,
                   const GPUCacheKey &key);

    // Remove the key from the image CPU cache.
    //
    // NOTE: Due to the way the LRU cache works, this can be quite
    // slow to to remove a specific key from the cache.
    //
    // Returns true/false, if the key was removed or not.
    bool cpu_erase(const CPUCacheKey &key);

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
    CacheEvictionResult gpu_evict_enough_for_new_entry(
        MHWRender::MTextureManager *texture_manager,
        const size_t new_memory_chunk_size);
    CacheEvictionResult cpu_evict_enough_for_new_entry(
        const size_t new_memory_chunk_size);

    // Amount of memory capacity.
    size_t m_gpu_capacity_bytes;
    size_t m_cpu_capacity_bytes;

    // How much memory is currently stored in the cached?
    size_t m_gpu_used_bytes;
    size_t m_cpu_used_bytes;

    // The minimum number of items that are allowed in the cache.  We
    // want to retain a fixed number of images, to avoid invalid
    // conditions in the cache.
    size_t m_gpu_item_count_minumum;
    size_t m_cpu_item_count_minumum;

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

    // // A Map of groups to a Set of key values.
    // //
    // // This map can be used to find all the loaded values used by an
    // // image sequence.
    // GPUGroupKeyMap m_gpu_cache_group_map;
    // CPUGroupKeyMap m_cpu_cache_group_map;
};

MTexture *read_texture_image_file(MHWRender::MTextureManager *texture_manager,
                                  ImageCache &image_cache, MImage &temp_image,
                                  const MString &file_path,
                                  const bool do_texture_update);
}  // namespace image
}  // namespace mmsolver

#endif  // MM_SOLVER_IMAGE_IMAGE_CACHE_H
