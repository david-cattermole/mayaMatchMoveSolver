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
 * MarkerList class represents an array of Marker objects with a
 * boolean enabling or disabling each marker.
 */

#ifndef MM_SOLVER_MAYA_HELPER_MAYA_MARKER_LIST_H
#define MM_SOLVER_MAYA_HELPER_MAYA_MARKER_LIST_H

// STL
#include <limits>
#include <memory>
#include <vector>

// Maya
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MString.h>

// MM Solver
#include "maya_marker.h"
#include "mmSolver/core/array_mask.h"

class MarkerList {
public:
    MarkerList();
    MarkerList(const MarkerList& other);

    // Query number of elements in the MarkerList.
    size_t size() const;

    // Number of markers that are enabled or disabled.
    size_t count_enabled() const;
    size_t count_disabled() const;

    // Query if the index is in the MarkerList.
    bool in_bounds(const size_t index) const;

    // Returns the marker or enabled status at the given index. Asserts
    // bounds checks.
    std::shared_ptr<Marker> get_marker(const size_t index) const;
    bool get_enabled(const size_t index) const;

    // Sets the marker at the given index. Asserts bounds checks.
    void set_marker(const size_t index, const std::shared_ptr<Marker>& value);
    void set_enabled(const size_t index, const bool value);

    // Set all markers to have an enabled/disabled 'value'.
    void set_all_enabled(const bool value);

    // Update the MarkerList by pushing back all the elements from another
    // MarkerList.
    void push_back_marker_list(const MarkerList& other);

    // Add marker to the list of markers.
    void push_back(const std::shared_ptr<Marker>& marker, const bool enabled);

    // Remove marker from the list, if it exists. Returns
    // true/false if the operation succeeded.
    bool remove_marker(const std::shared_ptr<Marker>& marker);

    // Erase the marker at 'index'.
    bool erase(const size_t index);

    // Remove all elements from the set.
    void clear();

    // Return true/false, depending on if the size is zero.
    bool is_empty() const;

    // Reserve capacity.
    void reserve(size_t new_capacity);

private:
    std::vector<std::shared_ptr<Marker>> m_markers;
    mmsolver::ArrayMask m_arrayMask;
};

#endif  // MM_SOLVER_MAYA_HELPER_MAYA_MARKER_LIST_H
