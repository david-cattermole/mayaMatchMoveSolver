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
 * Define the utilities for working on Maya frame data.
 */

#include "maya_frame_utils.h"

// STL
#include <algorithm>
#include <sstream>
#include <unordered_set>
#include <vector>

// Maya
#include <maya/MTime.h>
#include <maya/MTimeArray.h>

// MM Solver
#include "mmSolver/core/array_mask.h"
#include "mmSolver/core/frame_list.h"
#include "mmSolver/utilities/assert_utils.h"

namespace mmsolver {

MTimeArray create_enabled_time_array(const ArrayMask &mask,
                                     const MTimeArray &timeArray) {
    MMSOLVER_ASSERT(timeArray.length() == static_cast<uint32_t>(mask.size()),
                    "create_enabled_time_array can only work when the mask and "
                    "timeArray are consistently sized.");

    auto result = MTimeArray();
    const auto ui_unit = MTime::uiUnit();

    for (unsigned int i = 0; i < timeArray.length(); ++i) {
        if (!mask[i]) {
            continue;
        }
        result.append(timeArray[i]);
    }

    return result;
}

std::string create_string_sorted_set_numbers(
    const std::unordered_set<FrameNumber> &set) {
    std::vector<FrameNumber> sorted(set.begin(), set.end());
    std::sort(sorted.begin(), sorted.end());

    std::string result = "";
    for (auto i = 0; i < sorted.size(); ++i) {
        result += std::to_string(sorted[i]);
        if (i < sorted.size() - 1) {
            result += ", ";  // Add separator between elements.
        }
    }

    return result;
}

std::string create_string_sorted_frame_numbers(const MTimeArray &times) {
    const auto uiUnit = MTime::uiUnit();

    const auto frameCount = static_cast<FrameCount>(times.length());
    std::vector<FrameNumber> sortedFrames;
    sortedFrames.reserve(frameCount);

    for (FrameCount i = 0; i < frameCount; ++i) {
        const auto time = times[i];
        const FrameNumber frameNumber =
            static_cast<FrameNumber>(time.asUnits(uiUnit));
        sortedFrames.push_back(frameNumber);
    }
    std::sort(sortedFrames.begin(), sortedFrames.end());

    std::string result = "";
    for (auto i = 0; i < sortedFrames.size(); ++i) {
        result += std::to_string(sortedFrames[i]);
        if (i < sortedFrames.size() - 1) {
            result += ", ";  // Add separator between elements.
        }
    }

    return result;
}

std::string create_string_sorted_frame_numbers_all(const FrameList &frameList) {
    const auto frameCount = static_cast<FrameCount>(frameList.size());
    std::vector<FrameNumber> sortedFrames;
    sortedFrames.reserve(frameCount);

    for (FrameCount i = 0; i < frameCount; ++i) {
        const FrameNumber frameNumber = frameList.get_frame(i);
        sortedFrames.push_back(frameNumber);
    }
    std::sort(sortedFrames.begin(), sortedFrames.end());

    std::string result = "";
    for (auto i = 0; i < sortedFrames.size(); ++i) {
        result += std::to_string(sortedFrames[i]);
        if (i < sortedFrames.size() - 1) {
            result += ", ";  // Add separator between elements.
        }
    }

    return result;
}

namespace {

std::string create_string_sorted_frame_numbers_with_state(
    const FrameList &frameList, const bool only_state) {
    const auto frameCount = static_cast<FrameCount>(frameList.size());
    std::vector<FrameNumber> sortedFrames;
    sortedFrames.reserve(frameCount);

    for (FrameCount i = 0; i < frameCount; ++i) {
        const FrameNumber frameNumber = frameList.get_frame(i);
        const bool enabled = frameList.get_enabled(i);
        if (enabled == only_state) {
            sortedFrames.push_back(frameNumber);
        }
    }
    std::sort(sortedFrames.begin(), sortedFrames.end());

    std::string result = "";
    for (auto i = 0; i < sortedFrames.size(); ++i) {
        result += std::to_string(sortedFrames[i]);
        if (i < sortedFrames.size() - 1) {
            result += ", ";  // Add separator between elements.
        }
    }

    return result;
}

}  // namespace

std::string create_string_sorted_frame_numbers_enabled(
    const FrameList &frameList) {
    return create_string_sorted_frame_numbers_with_state(frameList,
                                                         /*only_state=*/true);
}

std::string create_string_sorted_frame_numbers_disabled(
    const FrameList &frameList) {
    return create_string_sorted_frame_numbers_with_state(frameList,
                                                         /*only_state=*/false);
}

MTimeArray create_time_array(const std::vector<FrameNumber> &frame_numbers) {
    const auto unit = MTime::uiUnit();
    return create_time_array(frame_numbers, unit);
}
MTimeArray create_time_array(const std::vector<FrameNumber> &frame_numbers,
                             const MTime::Unit &unit) {
    auto timeArray = MTimeArray();
    for (FrameIndex frameIndex = 0; frameIndex < frame_numbers.size();
         ++frameIndex) {
        const FrameNumber frameNumber = frame_numbers[frameIndex];
        MTime time = convert_to_time(frameNumber, unit);
        timeArray.append(time);
    }
    return timeArray;
}

MTimeArray create_time_array_enabled(const FrameList &frameList) {
    const auto unit = MTime::uiUnit();
    return create_time_array_enabled(frameList, unit);
}
MTimeArray create_time_array_enabled(const FrameList &frameList,
                                     const MTime::Unit &unit) {
    auto timeArray = MTimeArray();
    for (FrameIndex frameIndex = 0; frameIndex < frameList.size();
         ++frameIndex) {
        const FrameNumber frameNumber = frameList.get_frame(frameIndex);
        const bool enabled = frameList.get_enabled(frameIndex);
        if (enabled) {
            MTime time = convert_to_time(frameNumber, unit);
            timeArray.append(time);
        }
    }
    return timeArray;
}

MTimeArray create_time_array_disabled(const FrameList &frameList) {
    const auto unit = MTime::uiUnit();
    return create_time_array_disabled(frameList, unit);
}
MTimeArray create_time_array_disabled(const FrameList &frameList,
                                      const MTime::Unit &unit) {
    auto timeArray = MTimeArray();
    for (FrameIndex frameIndex = 0; frameIndex < frameList.size();
         ++frameIndex) {
        const FrameNumber frameNumber = frameList.get_frame(frameIndex);
        const bool enabled = frameList.get_enabled(frameIndex);
        if (!enabled) {
            MTime time = convert_to_time(frameNumber, unit);
            timeArray.append(time);
        }
    }
    return timeArray;
}

MTimeArray create_time_array_all(const FrameList &frameList) {
    const auto unit = MTime::uiUnit();
    return create_time_array_all(frameList, unit);
}
MTimeArray create_time_array_all(const FrameList &frameList,
                                 const MTime::Unit &unit) {
    auto timeArray = MTimeArray();
    for (FrameIndex frameIndex = 0; frameIndex < frameList.size();
         ++frameIndex) {
        const FrameNumber frameNumber = frameList.get_frame(frameIndex);
        MTime time = convert_to_time(frameNumber, unit);
        timeArray.append(time);
    }
    return timeArray;
}

FrameNumber convert_to_frame_number(const MTime &time) {
    const auto unit = MTime::uiUnit();
    return convert_to_frame_number(time, unit);
}
FrameNumber convert_to_frame_number(const MTime &time,
                                    const MTime::Unit &unit) {
    const double value = time.asUnits(unit);
    return static_cast<FrameNumber>(value);
}

MTime convert_to_time(const FrameNumber frame) {
    const auto unit = MTime::uiUnit();
    return convert_to_time(frame, unit);
}
MTime convert_to_time(const FrameNumber frame, const MTime::Unit &unit) {
    const double frame_double = static_cast<double>(frame);
    MTime time = MTime(frame_double, unit);
    return time;
}

static inline bool addNumberRangeToStringStream(const int startNum,
                                                const int endNum,
                                                std::stringstream &out_ss) {
    if (endNum != -1) {
        if (startNum == endNum) {
            out_ss << " " << startNum;
        } else if ((endNum - startNum) == 1) {
            out_ss << " " << startNum << " " << endNum;
        } else {
            out_ss << " " << startNum << "-" << endNum;
        }
    }
    return true;
}

bool addFrameListToStringStream(const FrameList &frameList,
                                std::stringstream &out_ss) {
    // Display contiguous frame numbers in the format '10-13', rather
    // than '10 11 12 13'.
    //
    // This function is ported from Python, see the function
    // 'intListToString', in ./python/mmSolver/utils/converttypes.py

    int startNum = -1;
    int endNum = -1;
    int prevNum = -1;

    const auto frameCount = frameList.size();
    for (auto i = 0; i < frameCount; i++) {
        const bool frameEnabled = frameList.get_enabled(i);
        if (!frameEnabled) {
            continue;
        }

        const FrameNumber frameNum = frameList.get_frame(i);

        bool first = i == 0;
        bool last = (i + 1) == frameCount;

        if (first) {
            // Start a new group.
            startNum = frameNum;
            endNum = frameNum;
        }

        if ((prevNum + 1) != frameNum) {
            // End old group.
            endNum = prevNum;
            addNumberRangeToStringStream(startNum, endNum, out_ss);

            // New group.
            startNum = frameNum;
            endNum = frameNum;
        }

        if (last) {
            // Close off final group.
            endNum = frameNum;
            addNumberRangeToStringStream(startNum, endNum, out_ss);
        }

        prevNum = frameNum;
    }

    return frameCount > 0;
}

}  // namespace mmsolver
