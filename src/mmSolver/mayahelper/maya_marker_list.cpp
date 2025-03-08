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
 * An object for an array of markers.
 */

#include "maya_marker_list.h"

// MM Solver Libs
#include <mmsolverlibs/debug.h>

// MM Solver
#include "mmSolver/core/array_mask.h"
#include "mmSolver/utilities/assert_utils.h"

MarkerList::MarkerList() : m_markers(), m_arrayMask() {}

MarkerList::MarkerList(const MarkerList& other)
    : m_markers(other.m_markers), m_arrayMask(other.m_arrayMask) {}

size_t MarkerList::size() const { return m_markers.size(); }

size_t MarkerList::count_enabled() const { return m_arrayMask.count_enabled(); }
size_t MarkerList::count_disabled() const {
    return m_arrayMask.count_disabled();
}

bool MarkerList::in_bounds(const size_t index) const {
    return index < m_markers.size();
}

std::shared_ptr<Marker> MarkerList::get_marker(const size_t index) const {
    MMSOLVER_ASSERT(
        MarkerList::in_bounds(index),
        "Bounds check; index=" << index << " size=" << MarkerList::size());
    return m_markers.at(index);
}

bool MarkerList::get_enabled(const size_t index) const {
    MMSOLVER_ASSERT(
        MarkerList::in_bounds(index),
        "Bounds check; index=" << index << " size=" << MarkerList::size());
    return m_arrayMask.get(index);
}

void MarkerList::set_marker(const size_t index,
                            const std::shared_ptr<Marker>& value) {
    MMSOLVER_ASSERT(
        MarkerList::in_bounds(index),
        "Bounds check; index=" << index << " size=" << MarkerList::size());
    m_markers[index] = value;
}

void MarkerList::set_enabled(const size_t index, const bool value) {
    MMSOLVER_ASSERT(
        MarkerList::in_bounds(index),
        "Bounds check; index=" << index << " size=" << MarkerList::size());
    m_arrayMask.set(index, value);
}

void MarkerList::set_all_enabled(const bool value) {
    for (auto i = 0; i < MarkerList::size(); ++i) {
        m_arrayMask.set(i, value);
    }
}

void MarkerList::push_back_marker_list(const MarkerList& other) {
    for (auto i = 0; i < other.size(); ++i) {
        const std::shared_ptr<Marker> marker = other.get_marker(i);
        const bool enabled = other.get_enabled(i);
        m_markers.push_back(marker);
        m_arrayMask.push_back(enabled);
    }
}

void MarkerList::push_back(const std::shared_ptr<Marker>& marker,
                           const bool enabled) {
    m_markers.push_back(marker);
    m_arrayMask.push_back(enabled);
}

bool MarkerList::remove_marker(const std::shared_ptr<Marker>& marker) {
    const size_t max_index = std::numeric_limits<size_t>::max();

    size_t index = max_index;
    for (auto i = 0; i < m_markers.size(); ++i) {
        if (m_markers[i] == marker) {
            index = i;
            break;
        }
    }
    if (index == max_index) {
        return false;
    }

    return erase(index);
}

bool MarkerList::erase(const size_t index) {
    MMSOLVER_ASSERT(
        MarkerList::in_bounds(index),
        "Bounds check; index=" << index << " size=" << MarkerList::size());
    m_markers.erase(m_markers.begin() + index);
    m_arrayMask.erase(index);
    return true;
}

void MarkerList::clear() {
    m_markers.clear();
    m_arrayMask.clear();
}

bool MarkerList::is_empty() const { return m_markers.empty(); }

void MarkerList::reserve(size_t new_capacity) {
    m_markers.reserve(new_capacity);
    m_arrayMask.reserve(new_capacity);
}
