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
 * AttrList class represents an array of Attr objects with a
 * boolean enabling or disabling each attribute.
 */

#ifndef MM_SOLVER_MAYA_HELPER_MAYA_ATTR_LIST_H
#define MM_SOLVER_MAYA_HELPER_MAYA_ATTR_LIST_H

// STL
#include <limits>
#include <memory>
#include <vector>

// Maya
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MString.h>

// MM Solver
#include "maya_attr.h"
#include "mmSolver/core/array_mask.h"

class AttrList {
public:
    AttrList();
    AttrList(const AttrList& other);

    // Query number of elements in the AttrList.
    size_t size() const;

    // Number of attributes that are enabled or disabled.
    size_t count_enabled() const;
    size_t count_disabled() const;

    // Query if the index is in the AttrList.
    bool in_bounds(const size_t index) const;

    // Returns the attribute or enabled status at the given index. Asserts
    // bounds checks.
    std::shared_ptr<Attr> get_attr(const size_t index) const;
    bool get_enabled(const size_t index) const;

    // Sets the attribute at the given index. Asserts bounds checks.
    void set_attr(const size_t index, const std::shared_ptr<Attr>& value);
    void set_enabled(const size_t index, const bool value);

    // Set all attributes to have an enabled/disabled 'value'.
    void set_all_enabled(const bool value);

    // Update the AttrList by pushing back all the elements from another
    // AttrList.
    void push_back_attr_list(const AttrList& other);

    // Add attribute to the list of attributes.
    void push_back(const std::shared_ptr<Attr>& attr, const bool enabled);

    // Remove attribute from the list, if it exists. Returns
    // true/false if the operation succeeded.
    bool remove_attr(const std::shared_ptr<Attr>& attr);

    // Erase the attribute at 'index'.
    bool erase(const size_t index);

    // Remove all elements from the set.
    void clear();

    // Return true/false, depending on if the size is zero.
    bool is_empty() const;

    // Reserve capacity.
    void reserve(size_t new_capacity);

private:
    std::vector<std::shared_ptr<Attr>> m_attrs;
    mmsolver::ArrayMask m_arrayMask;
};

#endif  // MM_SOLVER_MAYA_HELPER_MAYA_ATTR_LIST_H
