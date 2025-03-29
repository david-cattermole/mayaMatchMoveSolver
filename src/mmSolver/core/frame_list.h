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
 * FrameList class represents an array of integer frame numbers with a
 * boolean enabling or disabling each frame.
 */

#ifndef MM_SOLVER_CORE_FRAME_LIST_H
#define MM_SOLVER_CORE_FRAME_LIST_H

// STL
#include <limits>
#include <vector>

// MM Solver
#include "mmSolver/core/array_mask.h"
#include "mmSolver/core/frame.h"
#include "mmSolver/utilities/assert_utils.h"
#include "mmSolver/utilities/number_utils.h"

namespace mmsolver {

class FrameList {
public:
    FrameList();
    FrameList(const FrameList& other);

    // Query number of elements in the FrameList.
    size_t size() const;

    // Number of frames that are enabled or disabled.
    size_t count_enabled() const;
    size_t count_disabled() const;

    // Query if the index is in the FrameList.
    bool in_bounds(const size_t index) const;

    // Returns the minimum / maximum frame number in the list.
    //
    // These could be considered the start and end frames.
    FrameNumber min_frame() const;
    FrameNumber max_frame() const;

    // Returns the frame number or enabled at the given index. Asserts
    // bounds checks.
    FrameNumber get_frame(const size_t index) const;
    bool get_enabled(const size_t index) const;

    // Sets the frame number at the given index. Asserts bounds
    // checks.
    void set_frame(const size_t index, const FrameNumber value);
    void set_enabled(const size_t index, const bool value);

    // Set all frame numbers to have an enabled/disabled 'value'.
    void set_all_enabled(const bool value);

    // Update the FrameList by pushing back all the elements the other
    // FrameList.
    void push_back_frame_list(const FrameList& other);

    // Add frame to the list of frames.
    void push_back(const FrameNumber frame, const bool enabled);

    // Remove frame from the list, if it exists. Returns
    // true/false if the operation succeeded.
    bool remove_frame(const FrameNumber frame);

    // Erase the frame at 'index'.
    bool erase(const size_t index);

    // Remove all elements from the set.
    void clear();

    // Return true/false, depending on if the size is zero.
    bool is_empty() const;

    // Reserve capacity.
    void reserve(size_t new_capacity);

private:
    std::vector<FrameNumber> m_frameNumbers;
    mmsolver::ArrayMask m_arrayMask;
};

}  // namespace mmsolver

#endif  // MM_SOLVER_CORE_FRAME_LIST_H
