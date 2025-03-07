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
 * Define the 2D boolean matrix data structure.
 */

#ifndef MM_SOLVER_CORE_MATRIX_BOOL_2D_H
#define MM_SOLVER_CORE_MATRIX_BOOL_2D_H

// STL
#include <cstddef>
#include <iterator>
#include <vector>

// MM Solver
#include "mmSolver/utilities/assert_utils.h"

namespace mmsolver {

/**
 * A memory-efficient 2D boolean matrix implementation.
 *
 * MatrixBool2D provides a 2D matrix interface over a contiguous block of
 * boolean values.
 *
 * Unlike nested std::vector<std::vector<bool>>, this implementation:
 * - Uses a single contiguous memory block for better cache locality.
 * - Avoids pointer indirection and multiple allocations.
 * - Provides consistent performance characteristics.
 * - Maintains a smaller memory footprint.
 *
 * The matrix uses row-major ordering where elements in the same row are stored
 * contiguously. Access to elements is provided through (x,y) coordinates where:
 * - x represents the column index (0 to width-1)
 * - y represents the row index (0 to height-1)
 *
 * Memory layout: The underlying std::vector<bool> is a space-optimized
 * container where each bool typically occupies a single bit. This makes
 * MatrixBool2D particularly efficient for large binary matrices or bitmap-like
 * data structures.
 *
 * Performance characteristics:
 * - Element access: O(1)
 * - Memory usage: ~N bits where N = width * height
 * - Row traversal: Cache-friendly due to contiguous storage
 *
 * Example usage:
 *     // Create a 100x100 matrix initialized to false
 *     MatrixBool2D matrix(100, 100);
 *
 *     // Set some values
 *     matrix.set(50, 50, true);
 *
 *     // Check if a position is valid before access
 *     if (matrix.in_bounds(x, y)) {
 *         bool value = matrix.at(x, y);
 *     }
 *
 *     // Fill entire matrix with a value
 *     matrix.fill(true);
 *
 * NOTE: This class uses assertions for bounds checking in debug builds.
 *       These checks are disabled in release builds for performance.
 */
class MatrixBool2D {
public:
    // Constructor for creating a 'width' x 'height' matrix, with optional
    // 'initial_value'.
    MatrixBool2D(size_t width, size_t height,
                 bool initial_value = false) noexcept
        : m_width(width)
        , m_height(height)
        , m_data(width * height, initial_value) {}

    // Default constructor for empty matrix
    MatrixBool2D() noexcept : m_width(0), m_height(0) {}

    // Getters.
    size_t width() const noexcept { return m_width; }
    size_t height() const noexcept { return m_height; }
    size_t size() const noexcept { return m_data.size(); }
    bool is_empty() const noexcept { return m_data.empty(); }

    // Check if position is within bounds.
    bool in_bounds(size_t x, size_t y) const noexcept {
        return (x < m_width) && (y < m_height);
    }

    // Access element at (x,y).
    bool at(size_t x, size_t y) const noexcept {
        MMSOLVER_ASSERT_DEBUG(x < m_width && y < m_height,
                              "Index out of bounds");
        return m_data[y * m_width + x];
    }

    // Set value at position (x,y).
    void set(size_t x, size_t y, bool value) noexcept {
        MMSOLVER_ASSERT_DEBUG(x < m_width && y < m_height,
                              "Index out of bounds");
        m_data[y * m_width + x] = value;
    }

    // Clear the data.
    void clear() noexcept {
        m_width = 0;
        m_height = 0;
        m_data.clear();
    }

    // Fill the entire matrix with a value
    void fill(bool value) noexcept { m_data.assign(m_data.size(), value); }

    // Method to reset the matrix to a new dimension, reusing the same
    // underlying memory.
    void reset(size_t new_width, size_t new_height, bool fill_value = false) {
        size_t new_size = new_width * new_height;
        m_data.reserve(new_size);
        m_data.resize(new_size);
        m_data.assign(m_data.size(), fill_value);

        m_width = new_width;
        m_height = new_height;
    }

    // Method to reserve memory for future growth.
    void reserve(size_t new_capacity) { m_data.reserve(new_capacity); }

    // Method to get current capacity.
    size_t capacity() const { return m_data.capacity(); }

private:
    size_t m_width;
    size_t m_height;
    std::vector<bool> m_data;
};

}  // namespace mmsolver

#endif  // MM_SOLVER_CORE_MATRIX_BOOL_2D_H
