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
 * An object for an array of attrs.
 */

#include "maya_attr_list.h"

// MM Solver Libs
#include <mmsolverlibs/debug.h>

// MM Solver
#include "mmSolver/core/array_mask.h"
#include "mmSolver/utilities/assert_utils.h"

AttrList::AttrList() : m_attrs(), m_arrayMask() {}

AttrList::AttrList(const AttrList& other)
    : m_attrs(other.m_attrs), m_arrayMask(other.m_arrayMask) {}

size_t AttrList::size() const { return m_attrs.size(); }

size_t AttrList::count_enabled() const { return m_arrayMask.count_enabled(); }
size_t AttrList::count_disabled() const { return m_arrayMask.count_disabled(); }

bool AttrList::in_bounds(const size_t index) const {
    return index < m_attrs.size();
}

std::shared_ptr<Attr> AttrList::get_attr(const size_t index) const {
    MMSOLVER_ASSERT(
        AttrList::in_bounds(index),
        "Bounds check; index=" << index << " size=" << AttrList::size());
    return m_attrs.at(index);
}

bool AttrList::get_enabled(const size_t index) const {
    MMSOLVER_ASSERT(
        AttrList::in_bounds(index),
        "Bounds check; index=" << index << " size=" << AttrList::size());
    return m_arrayMask.get(index);
}

void AttrList::set_attr(const size_t index,
                        const std::shared_ptr<Attr>& value) {
    MMSOLVER_ASSERT(
        AttrList::in_bounds(index),
        "Bounds check; index=" << index << " size=" << AttrList::size());
    m_attrs[index] = value;
}

void AttrList::set_enabled(const size_t index, const bool value) {
    MMSOLVER_ASSERT(
        AttrList::in_bounds(index),
        "Bounds check; index=" << index << " size=" << AttrList::size());
    m_arrayMask.set(index, value);
}

void AttrList::set_all_enabled(const bool value) {
    for (auto i = 0; i < AttrList::size(); ++i) {
        m_arrayMask.set(i, value);
    }
}

void AttrList::push_back_attr_list(const AttrList& other) {
    for (auto i = 0; i < other.size(); ++i) {
        const std::shared_ptr<Attr> attr = other.get_attr(i);
        const bool enabled = other.get_enabled(i);
        m_attrs.push_back(attr);
        m_arrayMask.push_back(enabled);
    }
}

void AttrList::push_back(const std::shared_ptr<Attr>& attr,
                         const bool enabled) {
    m_attrs.push_back(attr);
    m_arrayMask.push_back(enabled);
}

bool AttrList::remove_attr(const std::shared_ptr<Attr>& attr) {
    const size_t max_index = std::numeric_limits<size_t>::max();

    size_t index = max_index;
    for (auto i = 0; i < m_attrs.size(); ++i) {
        if (m_attrs[i] == attr) {
            index = i;
            break;
        }
    }
    if (index == max_index) {
        return false;
    }

    return erase(index);
}

bool AttrList::erase(const size_t index) {
    MMSOLVER_ASSERT(
        AttrList::in_bounds(index),
        "Bounds check; index=" << index << " size=" << AttrList::size());
    m_attrs.erase(m_attrs.begin() + index);
    m_arrayMask.erase(index);
    return true;
}

void AttrList::clear() {
    m_attrs.clear();
    m_arrayMask.clear();
}

bool AttrList::is_empty() const { return m_attrs.empty(); }

void AttrList::reserve(size_t new_capacity) {
    m_attrs.reserve(new_capacity);
    m_arrayMask.reserve(new_capacity);
}
