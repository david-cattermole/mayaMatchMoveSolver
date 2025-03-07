/*
 * Copyright (C) 2025 David Cattermole.
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
 * Define the Array Mask data structure.
 */

#ifndef MM_SOLVER_CORE_ARRAY_MASK_H
#define MM_SOLVER_CORE_ARRAY_MASK_H

// STL
#include <cstddef>
#include <string>
#include <vector>

// Maya
#include <maya/MTime.h>
#include <maya/MTimeArray.h>

namespace mmsolver {

class ArrayMask {
public:
    // Default constructor
    ArrayMask();

    // Constructor with initial size and value
    explicit ArrayMask(size_t size, bool initial_value = false);

    // Modify vector.
    void push_back(const bool value);
    bool erase(const size_t index);
    void clear();

    // Query size.
    size_t size() const;
    bool is_empty() const;

    // Capacity methods
    void resize(const size_t new_size, const bool value = false);
    void reserve(const size_t new_capacity);

    // Element access
    bool in_bounds(const size_t index) const;
    bool get(const size_t index) const;
    void set(const size_t index, const bool value);
    bool operator[](const size_t index) const;

    // Get raw access to internal data (for slice creation).
    const std::vector<bool>& raw_data() const { return m_mask; }

    // Utility functions
    size_t count_enabled() const;
    size_t count_disabled() const;

private:
    std::vector<bool> m_mask;
};

}  // namespace mmsolver

#endif  // MM_SOLVER_CORE_ARRAY_MASK_H
