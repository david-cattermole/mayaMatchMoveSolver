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
 * An object for an array of frames.
 */

#include "frame_list.h"

// MM Solver Libs
#include <mmsolverlibs/debug.h>

// MM Solver
#include "mmSolver/core/array_mask.h"
#include "mmSolver/utilities/assert_utils.h"

namespace mmsolver {

FrameList::FrameList() : m_frameNumbers(), m_arrayMask() {}

FrameList::FrameList(const FrameList& other)
    : m_frameNumbers(other.m_frameNumbers), m_arrayMask(other.m_arrayMask) {}

size_t FrameList::size() const { return m_frameNumbers.size(); }

size_t FrameList::count_enabled() const { return m_arrayMask.count_enabled(); }
size_t FrameList::count_disabled() const {
    return m_arrayMask.count_disabled();
}

bool FrameList::in_bounds(const size_t index) const {
    return index < m_frameNumbers.size();
}

FrameNumber FrameList::min_frame() const {
    if (FrameList::is_empty()) {
        return FRAME_NUMBER_MAX;
    }

    FrameNumber min_frame = FRAME_NUMBER_MAX;
    for (const auto& frame : m_frameNumbers) {
        if (frame < min_frame) {
            min_frame = frame;
        }
    }
    return min_frame;
}

FrameNumber FrameList::max_frame() const {
    if (FrameList::is_empty()) {
        return FRAME_NUMBER_MIN;
    }

    FrameNumber max_frame = FRAME_NUMBER_MIN;
    for (const auto& frame : m_frameNumbers) {
        if (frame > max_frame) {
            max_frame = frame;
        }
    }
    return max_frame;
}

FrameNumber FrameList::get_frame(const size_t index) const {
    MMSOLVER_ASSERT(
        FrameList::in_bounds(index),
        "Bounds check; index=" << index << " size=" << FrameList::size());
    return m_frameNumbers.at(index);
}

bool FrameList::get_enabled(const size_t index) const {
    MMSOLVER_ASSERT(
        FrameList::in_bounds(index),
        "Bounds check; index=" << index << " size=" << FrameList::size());
    return m_arrayMask.get(index);
}

void FrameList::set_frame(const size_t index, const FrameNumber value) {
    MMSOLVER_ASSERT(
        FrameList::in_bounds(index),
        "Bounds check; index=" << index << " size=" << FrameList::size());
    m_frameNumbers[index] = value;
}

void FrameList::set_enabled(const size_t index, const bool value) {
    MMSOLVER_ASSERT(
        FrameList::in_bounds(index),
        "Bounds check; index=" << index << " size=" << FrameList::size());
    m_arrayMask.set(index, value);
}

void FrameList::set_all_enabled(const bool value) {
    for (auto i = 0; i < FrameList::size(); ++i) {
        m_arrayMask.set(i, value);
    }
}

void FrameList::push_back_frame_list(const FrameList& other) {
    for (auto i = 0; i < other.size(); ++i) {
        const FrameNumber frame = other.get_frame(i);
        const bool enabled = other.get_enabled(i);
        m_frameNumbers.push_back(frame);
        m_arrayMask.push_back(enabled);
    }
}

void FrameList::push_back(const FrameNumber frame, const bool enabled) {
    m_frameNumbers.push_back(frame);
    m_arrayMask.push_back(enabled);
}

bool FrameList::remove_frame(const FrameNumber frame) {
    const size_t max_index = std::numeric_limits<size_t>::max();

    size_t index = max_index;
    for (auto i = 0; i < m_frameNumbers.size(); ++i) {
        const FrameNumber number = m_frameNumbers[i];
        if (number == frame) {
            index = i;
            break;
        }
    }
    if (index == max_index) {
        return false;
    }

    return erase(index);
}

bool FrameList::erase(const size_t index) {
    MMSOLVER_ASSERT(
        FrameList::in_bounds(index),
        "Bounds check; index=" << index << " size=" << FrameList::size());
    m_frameNumbers.erase(m_frameNumbers.begin() + index);
    m_arrayMask.erase(index);
    return true;
}

void FrameList::clear() {
    m_frameNumbers.clear();
    m_arrayMask.clear();
}

bool FrameList::is_empty() const { return m_frameNumbers.empty(); }

void FrameList::reserve(size_t new_capacity) {
    m_frameNumbers.reserve(new_capacity);
    m_arrayMask.reserve(new_capacity);
}

}  // namespace mmsolver
