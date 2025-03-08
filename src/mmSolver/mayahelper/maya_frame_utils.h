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
 * Utilities for frames in Maya.
 */

#ifndef MM_SOLVER_MAYA_HELPER_MAYA_FRAME_UTILS_H
#define MM_SOLVER_MAYA_HELPER_MAYA_FRAME_UTILS_H

// STL
#include <cstddef>
#include <sstream>
#include <string>
#include <unordered_set>
#include <vector>

// Maya
#include <maya/MTime.h>
#include <maya/MTimeArray.h>

// MM Solver
#include "mmSolver/core/array_mask.h"
#include "mmSolver/core/frame.h"
#include "mmSolver/core/frame_list.h"

namespace mmsolver {

MTimeArray create_enabled_time_array(const ArrayMask& mask,
                                     const MTimeArray& timeArray);

std::string create_string_sorted_set_numbers(
    const std::unordered_set<FrameNumber>& set);
std::string create_string_sorted_frame_numbers(const MTimeArray& times);
std::string create_string_sorted_frame_numbers_all(const FrameList& frameList);
std::string create_string_sorted_frame_numbers_enabled(
    const FrameList& frameList);
std::string create_string_sorted_frame_numbers_disabled(
    const FrameList& frameList);

MTimeArray create_time_array(const std::vector<FrameNumber>& frame_numbers);
MTimeArray create_time_array(const std::vector<FrameNumber>& frame_numbers,
                             const MTime::Unit& unit);

MTimeArray create_time_array_enabled(const FrameList& frameList);
MTimeArray create_time_array_enabled(const FrameList& frameList,
                                     const MTime::Unit& unit);

MTimeArray create_time_array_disabled(const FrameList& frameList);
MTimeArray create_time_array_disabled(const FrameList& frameList,
                                      const MTime::Unit& unit);

MTimeArray create_time_array_all(const FrameList& frameList);
MTimeArray create_time_array_all(const FrameList& frameList,
                                 const MTime::Unit& unit);

FrameNumber convert_to_frame_number(const MTime& time);
FrameNumber convert_to_frame_number(const MTime& time, const MTime::Unit& unit);

MTime convert_to_time(const FrameNumber frame);
MTime convert_to_time(const FrameNumber frame, const MTime::Unit& unit);

bool addFrameListToStringStream(const FrameList& frameList,
                                std::stringstream& out_ss);

}  // namespace mmsolver

#endif  // MM_SOLVER_MAYA_HELPER_MAYA_FRAME_UTILS_H
