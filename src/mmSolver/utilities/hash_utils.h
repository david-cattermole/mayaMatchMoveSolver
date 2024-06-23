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
 * Implements simple hashing on generic data.
 *
 * See this page for an interesting article on hash collisions:
 * http://softwareengineering.stackexchange.com/questions/49550/which-hashing-algorithm-is-best-for-uniqueness-and-speed
 *
 */

#ifndef HASH_UTILS_H
#define HASH_UTILS_H

// STL
#include <cstdlib>  // size_t
#include <string>   // string
#include <vector>   // vector

// Platform-specific functions and macros
#if defined(_MSC_VER)
// Microsoft Visual Studio
#define BIG_CONSTANT(x) (x)
#else
// Other compilers
#define BIG_CONSTANT(x) (x##LLU)
#endif

#if defined(_MSC_VER) && (_MSC_VER < 1600)
// Microsoft Visual Studio
typedef unsigned char uint8_t;
typedef unsigned int uint32_t;
typedef unsigned __int64 uint64_t;
#else
// Other compilers
#include <stdint.h>
#endif

// typedef unsigned long long int CacheKey;

namespace mmsolver {
namespace hash {

// MurmurHash2 hash, for 64-bit versions
//
// From:
// https://github.com/aappleby/smhasher/blob/master/src/MurmurHash2.cpp#L96
//
// MurmurHash2, 64-bit versions, by Austin Appleby
//
// MurmurHash2 was written by Austin Appleby, and is placed in the
// public domain. The author hereby disclaims copyright to the
// MurmurHash2 source code.
//
// The same caveats as 32-bit MurmurHash2 apply here - beware of alignment
// and endian-ness issues if used across multiple platforms.
//
// 64-bit hash for 64-bit platforms
inline uint64_t MurmurHash64A(const void *key, int len, uint64_t seed) {
    const uint64_t m = BIG_CONSTANT(0xc6a4a7935bd1e995);
    const int r = 47;

    uint64_t h = seed ^ (len * m);

    const uint64_t *data = (const uint64_t *)key;
    const uint64_t *end = data + (len / 8);

    while (data != end) {
        uint64_t k = *data++;

        k *= m;
        k ^= k >> r;
        k *= m;

        h ^= k;
        h *= m;
    }

    const unsigned char *data2 = (const unsigned char *)data;

    switch (len & 7) {
        case 7:
            h ^= uint64_t(data2[6]) << 48;
        case 6:
            h ^= uint64_t(data2[5]) << 40;
        case 5:
            h ^= uint64_t(data2[4]) << 32;
        case 4:
            h ^= uint64_t(data2[3]) << 24;
        case 3:
            h ^= uint64_t(data2[2]) << 16;
        case 2:
            h ^= uint64_t(data2[1]) << 8;
        case 1:
            h ^= uint64_t(data2[0]);
            h *= m;
        default:
            break;
    };

    h ^= h >> r;
    h *= m;
    h ^= h >> r;

    return h;
}

template <typename R, typename K>
inline R hashMurmur2(const K *key, int len) {
    const void *p = reinterpret_cast<const void *>(key);
    R h = (R)MurmurHash64A(p, len, 0);
    return h;
}

// Hashing functions, added to the class for convenience.
inline uint64_t make_hash(const std::string &value) {
    return hash::hashMurmur2<uint64_t>(value.c_str(), value.size());
}

// Merges multiple hashes together into a single hash.
template <typename R, typename K, typename A>
inline R mergeHashes(const std::vector<K, A> &hashes, R seed = 0) {
    typename std::vector<K>::const_iterator it;
    R result = seed;
    for (it = hashes.begin(); it != hashes.end(); ++it) {
        result = 16777619 * result ^ *it;
    }
    return result;
}

// Combines a hash with another hash.
//
// Similar to 'boost::combine_hash'.
template <typename K>
inline void combineHash(K &seed, K key) {
    seed = 16777619 * seed ^ key;
}

}  // namespace hash
}  // namespace mmsolver

#endif  // HASH_UTILS_H
