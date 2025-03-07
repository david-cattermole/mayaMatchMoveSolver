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
 * Define the array mask data structure.
 */

#include "array_mask.h"

// STL
#include <algorithm>
#include <cassert>
#include <sstream>
#include <vector>

// Maya
#include <maya/MTime.h>
#include <maya/MTimeArray.h>

// MM Solver
#include "mmSolver/utilities/assert_utils.h"

namespace mmsolver {

ArrayMask::ArrayMask() : m_mask(){};

ArrayMask::ArrayMask(const size_t size, const bool initial_value)
    : m_mask(size, initial_value) {}

void ArrayMask::resize(const size_t new_size, bool value) {
    m_mask.resize(new_size, value);
}

void ArrayMask::reserve(const size_t new_capacity) {
    m_mask.reserve(new_capacity);
}

bool ArrayMask::erase(const size_t index) {
    MMSOLVER_ASSERT(
        ArrayMask::in_bounds(index),
        "Bounds check; index=" << index << " size=" << ArrayMask::size());
    auto iterator = m_mask.erase(m_mask.begin() + index);
    return true;
}

void ArrayMask::push_back(const bool value) { m_mask.push_back(value); }

void ArrayMask::clear() { m_mask.clear(); }

size_t ArrayMask::size() const { return m_mask.size(); }

bool ArrayMask::is_empty() const { return m_mask.empty(); }

bool ArrayMask::in_bounds(const size_t index) const {
    return index < m_mask.size();
}

bool ArrayMask::get(const size_t index) const {
    MMSOLVER_ASSERT(
        ArrayMask::in_bounds(index),
        "Bounds check; index=" << index << " size=" << ArrayMask::size());
    return m_mask.at(index);
}

void ArrayMask::set(const size_t index, const bool value) {
    MMSOLVER_ASSERT(
        ArrayMask::in_bounds(index),
        "Bounds check; index=" << index << " size=" << ArrayMask::size());
    m_mask[index] = value;
}

bool ArrayMask::operator[](const size_t index) const {
    MMSOLVER_ASSERT(
        ArrayMask::in_bounds(index),
        "Bounds check; index=" << index << " size=" << ArrayMask::size());
    return m_mask[index];
}

size_t ArrayMask::count_enabled() const {
    return std::count(m_mask.begin(), m_mask.end(), true);
}

size_t ArrayMask::count_disabled() const {
    return std::count(m_mask.begin(), m_mask.end(), false);
}

}  // namespace mmsolver
