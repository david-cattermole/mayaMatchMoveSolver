/*
 * Copyright (C) 2018, 2019, 2022, 2025 David Cattermole.
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
 * Data structures to keep track of the solve, and return to the user.
 */

#ifndef MM_SOLVER_CORE_BUNDLE_ADJUST_RESULTS_H
#define MM_SOLVER_CORE_BUNDLE_ADJUST_RESULTS_H

// STL
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdlib>
#include <functional>
#include <limits>
#include <map>
#include <string>
#include <tuple>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

// Maya
#include <maya/MFnDagNode.h>
#include <maya/MObject.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>

// MM Solver Libs
#include <mmsolverlibs/debug.h>

// MM Solver
#include "adjust_data.h"
#include "adjust_defines.h"
#include "adjust_relationships.h"
#include "mmSolver/core/matrix_bool_2d.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/string_utils.h"

using Ticks = mmsolver::debug::Ticks;

struct SolverResult {
    typedef SolverResult Self;

    bool success;
    double errorAvg;
    double errorMin;
    double errorMax;
    int reason_number;
    std::string reason;
    int iterations;
    int functionEvals;
    int jacobianEvals;
    double errorFinal;
    bool user_interrupted;
    int count;  // number of samples in this result.

    SolverResult()
        : success(true)
        , errorAvg(0.0)
        , errorMin(std::numeric_limits<double>::max())
        , errorMax(-0.0)
        , errorFinal(0.0)
        , reason_number(0)
        , reason()
        , iterations(0)
        , functionEvals(0)
        , jacobianEvals(0)
        , user_interrupted(false)
        , count(0) {}

    void add(const Self &other) {
        Self::success = std::min(Self::success, other.success);

        Self::errorFinal += other.errorFinal;
        Self::errorAvg += other.errorAvg;
        Self::errorMin = std::min(Self::errorMin, other.errorMin);
        Self::errorMax = std::max(Self::errorMax, other.errorMax);

        Self::iterations += other.iterations;
        Self::functionEvals += other.functionEvals;
        Self::jacobianEvals += other.jacobianEvals;

        Self::reason_number = other.reason_number;
        Self::reason = other.reason;

        Self::count += other.count;
    }

    void divide() {
        double count_inverse = 1.0;
        if (Self::count > 1) {
            count_inverse = 1.0 / static_cast<double>(Self::count);
        }

        Self::errorAvg *= count_inverse;
        Self::errorFinal *= count_inverse;

        Self::count = 1;
    }

    void appendToMStringArray(MStringArray &result) {
        std::string str;

        std::string value = mmstring::numberToString<int>(Self::success);
        str = "success=" + value;
        result.append(MString(str.c_str()));

        value = mmstring::numberToString<int>(Self::reason_number);
        str = "reason_num=" + value;
        result.append(MString(str.c_str()));

        value = Self::reason;
        str = "reason_string=" + value;
        result.append(MString(str.c_str()));

        value = mmstring::numberToString<double>(Self::errorFinal);
        str = "error_final=" + value;
        result.append(MString(str.c_str()));

        value = mmstring::numberToString<double>(Self::errorAvg);
        str = "error_final_average=" + value;
        result.append(MString(str.c_str()));

        value = mmstring::numberToString<double>(Self::errorMax);
        str = "error_final_maximum=" + value;
        result.append(MString(str.c_str()));

        value = mmstring::numberToString<double>(Self::errorMin);
        str = "error_final_minimum=" + value;
        result.append(MString(str.c_str()));

        value = mmstring::numberToString<int>(Self::iterations);
        str = "iteration_num=" + value;
        result.append(MString(str.c_str()));

        value = mmstring::numberToString<int>(Self::functionEvals);
        str = "iteration_function_num=" + value;
        result.append(MString(str.c_str()));

        value = mmstring::numberToString<int>(Self::jacobianEvals);
        str = "iteration_jacobian_num=" + value;
        result.append(MString(str.c_str()));

        value = mmstring::numberToString<int>(Self::user_interrupted);
        str = "user_interrupted=" + value;
        result.append(MString(str.c_str()));
    }
};

struct TimerResult {
    typedef TimerResult Self;

    int count;
    double timer_solve;
    double timer_function;
    double timer_jacobian;
    double timer_parameter;
    double timer_error;
    Ticks ticks_solve;
    Ticks ticks_function;
    Ticks ticks_jacobian;
    Ticks ticks_parameter;
    Ticks ticks_error;

    TimerResult()
        : count(0)
        , timer_solve(0.0)
        , timer_function(0.0)
        , timer_jacobian(0.0)
        , timer_parameter(0.0)
        , timer_error(0.0)
        , ticks_solve(0)
        , ticks_function(0)
        , ticks_jacobian(0)
        , ticks_parameter(0)
        , ticks_error(0) {}

    void fill(const SolverTimer &timer) {
        Self::count = 1;

        Self::timer_solve = timer.solveBenchTimer.get_seconds();
        Self::timer_function = timer.funcBenchTimer.get_seconds();
        Self::timer_jacobian = timer.jacBenchTimer.get_seconds();
        Self::timer_parameter = timer.paramBenchTimer.get_seconds();
        Self::timer_error = timer.paramBenchTimer.get_seconds();

        Self::ticks_solve = timer.solveBenchTicks.get_ticks();
        Self::ticks_function = timer.funcBenchTicks.get_ticks();
        Self::ticks_jacobian = timer.jacBenchTicks.get_ticks();
        Self::ticks_parameter = timer.paramBenchTicks.get_ticks();
        Self::ticks_error = timer.paramBenchTicks.get_ticks();
    }

    void add(const Self &other) {
        Self::timer_solve += other.timer_solve;
        Self::timer_function += other.timer_function;
        Self::timer_jacobian += other.timer_jacobian;
        Self::timer_parameter += other.timer_parameter;
        Self::timer_error += other.timer_error;

        Self::ticks_solve += other.ticks_solve;
        Self::ticks_function += other.ticks_function;
        Self::ticks_jacobian += other.ticks_jacobian;
        Self::ticks_parameter += other.ticks_parameter;
        Self::ticks_error += other.ticks_error;

        Self::count += other.count;
    }

    void divide() {
        double count_inverse = 1.0;
        if (Self::count > 1) {
            count_inverse = 1.0 / static_cast<double>(Self::count);
        }

        Self::timer_solve *= count_inverse;
        Self::timer_function *= count_inverse;
        Self::timer_jacobian *= count_inverse;
        Self::timer_parameter *= count_inverse;
        Self::timer_error *= count_inverse;

        Self::ticks_solve *= count_inverse;
        Self::ticks_function *= count_inverse;
        Self::ticks_jacobian *= count_inverse;
        Self::ticks_parameter *= count_inverse;
        Self::ticks_error *= count_inverse;

        Self::count = 1;
    }

    void appendToMStringArray(MStringArray &result) {
        std::string str;

        std::string value = mmstring::numberToString<double>(Self::timer_solve);
        str = "timer_solve=" + value;
        result.append(MString(str.c_str()));

        value = mmstring::numberToString<double>(Self::timer_function);
        str = "timer_function=" + value;
        result.append(MString(str.c_str()));

        value = mmstring::numberToString<double>(Self::timer_jacobian);
        str = "timer_jacobian=" + value;
        result.append(MString(str.c_str()));

        value = mmstring::numberToString<double>(Self::timer_parameter);
        str = "timer_parameter=" + value;
        result.append(MString(str.c_str()));

        value = mmstring::numberToString<double>(Self::timer_error);
        str = "timer_error=" + value;
        result.append(MString(str.c_str()));

        value = mmstring::numberToString<Ticks>(Self::ticks_solve);
        str = "ticks_solve=" + value;
        result.append(MString(str.c_str()));

        value = mmstring::numberToString<Ticks>(Self::ticks_function);
        str = "ticks_function=" + value;
        result.append(MString(str.c_str()));

        value = mmstring::numberToString<Ticks>(Self::ticks_jacobian);
        str = "ticks_jacobian=" + value;
        result.append(MString(str.c_str()));

        value = mmstring::numberToString<Ticks>(Self::ticks_parameter);
        str = "ticks_parameter=" + value;
        result.append(MString(str.c_str()));

        value = mmstring::numberToString<Ticks>(Self::ticks_error);
        str = "ticks_error=" + value;
        result.append(MString(str.c_str()));
    }
};

struct SolveValuesResult {
    typedef SolveValuesResult Self;

    int count;
    std::vector<double> solve_parameter_list;
    std::vector<double> solve_error_list;

    SolveValuesResult() : count(0) {}

    void fill(const int numberOfParameters, const int numberOfErrors,
              const std::vector<double> &paramList,
              const std::vector<double> &errorList) {
        for (auto i = 0; i < numberOfParameters; ++i) {
            const double param_value = paramList[i];
            Self::solve_parameter_list.push_back(param_value);
        }

        for (auto i = 0; i < numberOfErrors; ++i) {
            const double err_value = errorList[i];
            Self::solve_error_list.push_back(err_value);
        }

        Self::count = 1;
    }

    void add(const Self &other) {
        if (other.count == 0) {
            return;
        }

        if (Self::count == 0) {
            Self::solve_parameter_list = other.solve_parameter_list;
            Self::solve_error_list = other.solve_error_list;
            Self::count = other.count;
        } else {
            auto solve_parameter_count =
                std::min(Self::solve_parameter_list.size(),
                         other.solve_parameter_list.size());
            for (auto i = 0; i < solve_parameter_count; ++i) {
                Self::solve_parameter_list[i] += other.solve_parameter_list[i];
            }

            auto solve_error_count = std::min(Self::solve_error_list.size(),
                                              other.solve_error_list.size());
            for (auto i = 0; i < solve_error_count; ++i) {
                Self::solve_error_list[i] += other.solve_error_list[i];
            }

            Self::count += other.count;
        }
    }

    void divide() {
        double count_inverse = 1.0;
        if (Self::count > 1) {
            count_inverse = 1.0 / static_cast<double>(Self::count);
        }

        for (double &i : Self::solve_parameter_list) {
            i *= count_inverse;
        }

        for (double &i : Self::solve_error_list) {
            i *= count_inverse;
        }

        Self::count = 1;
    }

    void appendToMStringArray(MStringArray &result) {
        std::string str = "solve_parameter_list=";
        for (const auto &value : Self::solve_parameter_list) {
            str += mmstring::numberToString<double>(value);
            str += CMD_RESULT_SPLIT_CHAR;
        }
        result.append(MString(str.c_str()));

        str = "solve_error_list=";
        for (const auto &value : Self::solve_error_list) {
            str += mmstring::numberToString<double>(value);
            str += CMD_RESULT_SPLIT_CHAR;
        }
        result.append(MString(str.c_str()));
    }
};

struct ErrorMetricsResult {
    typedef ErrorMetricsResult Self;
    typedef std::pair<int, int> IndexPair;
    typedef std::pair<double, double> DoublePair;
    typedef std::unordered_multimap<double, double> MultiMapDoubleDouble;
    typedef std::pair<std::string, MultiMapDoubleDouble> StrMultiMapDoublePair;
    typedef std::unordered_map<std::string, MultiMapDoubleDouble>
        MapStringMultiMapDoubleDouble;

    MapStringMultiMapDoubleDouble error_per_marker_per_frame;
    MultiMapDoubleDouble error_per_frame;

    ErrorMetricsResult() = default;

    void fill(const int numberOfMarkerErrors, const MarkerPtrList &markerList,
              const MTimeArray &frameList,
              const std::vector<IndexPair> &errorToMarkerList,
              const std::vector<double> &errorDistanceList) {
        typedef std::pair<int, double> ErrorPair;
        typedef std::pair<int, ErrorPair> IntErrorPair;
        typedef std::map<int, ErrorPair> TimeErrorMapping;
        typedef TimeErrorMapping::iterator TimeErrorMappingIt;

        const auto ui_unit = MTime::uiUnit();

        TimeErrorMapping frame_error_mapping;
        for (auto i = 0; i < (numberOfMarkerErrors / ERRORS_PER_MARKER); ++i) {
            const IndexPair marker_pair = errorToMarkerList[i];
            MarkerPtr marker = markerList[marker_pair.first];
            const MTime frame = frameList[marker_pair.second];
            const MString marker_node_name = marker->getNodeName();
            const char *marker_name = marker_node_name.asChar();
            const double deviation = errorDistanceList[i];
            const double frame_value = frame.asUnits(ui_unit);

            TimeErrorMappingIt ait =
                frame_error_mapping.find(marker_pair.second);
            ErrorPair error_pair;
            if (ait != frame_error_mapping.end()) {
                error_pair = ait->second;
                error_pair.first += 1;
                error_pair.second += deviation;
                frame_error_mapping.erase(ait);
            } else {
                error_pair.first = 1;
                error_pair.second = deviation;
            }
            auto int_error_pair = IntErrorPair(marker_pair.second, error_pair);
            frame_error_mapping.insert(int_error_pair);

            auto double_pair = DoublePair(frame_value, deviation);

            auto search = Self::error_per_marker_per_frame.find(marker_name);
            if (search != Self::error_per_marker_per_frame.end()) {
                search->second.insert(double_pair);
            } else {
                auto sub_map = MultiMapDoubleDouble();
                sub_map.insert(double_pair);

                auto str_double_map_pair =
                    StrMultiMapDoublePair(marker_name, sub_map);
                Self::error_per_marker_per_frame.insert(str_double_map_pair);
            }
        }

        for (TimeErrorMappingIt mit = frame_error_mapping.begin();
             mit != frame_error_mapping.end(); ++mit) {
            int frameIndex = mit->first;
            MTime frame = frameList[frameIndex];
            TimeErrorMappingIt ait = frame_error_mapping.find(frameIndex);

            double num = 0;
            double deviation = 0;
            if (ait != frame_error_mapping.end()) {
                ErrorPair pair = ait->second;
                num = pair.first;
                deviation = pair.second;
            } else {
                continue;
            }

            auto frame_value = frame.asUnits(ui_unit);
            auto pair = DoublePair(frame_value, deviation / num);
            Self::error_per_frame.insert(pair);
        }
    }

    void add(const Self &other) {
        for (const auto &kv : other.error_per_frame) {
            Self::error_per_frame.insert({kv.first, kv.second});
        }

        for (const auto &kv : other.error_per_marker_per_frame) {
            const auto search = Self::error_per_marker_per_frame.find(kv.first);
            if (search != Self::error_per_marker_per_frame.end()) {
                // Found Marker node in map, add all the elements into
                // the existing map.
                auto existing_map = search->second;
                const auto other_map = kv.second;
                for (const auto &sub_kv : other_map) {
                    existing_map.insert({sub_kv.first, sub_kv.second});
                }
            } else {
                // No Marker node found, the Marker node is new, so we
                // add the other map directly into this map.
                Self::error_per_marker_per_frame.insert({kv.first, kv.second});
            }
        }
    }

    void divide() {
        for (auto it = Self::error_per_frame.begin();
             it != Self::error_per_frame.end();) {
            auto const &key = it->first;

            // Sum all values given for the same key.
            double value = 0.0;
            auto count = 0;
            auto value_iterators = Self::error_per_frame.equal_range(key);

            for (auto vit = value_iterators.first;
                 vit != value_iterators.second; vit++) {
                value += vit->second;
                ++count;
                if (it != vit) {
                    Self::error_per_frame.erase(vit);
                }
            }

            if (count > 1) {
                it->second = value / static_cast<double>(count);
            }

            // Only iterate over unique keys once.
            //
            // Skip to the next iterator that doesn't start with 'key'.
            while (++it != Self::error_per_frame.end() && it->first == key) {
            }
        }
    }

    void appendToMStringArray(MStringArray &result) {
        std::string str;
        for (const auto &kv : Self::error_per_marker_per_frame) {
            const auto marker_name = kv.first;
            const auto map = kv.second;

            for (const auto &sub_kv : map) {
                const auto frame_value = sub_kv.first;
                const auto error_value = sub_kv.second;

                str = "error_per_marker_per_frame=";
                str += marker_name;
                str += CMD_RESULT_SPLIT_CHAR;
                str += mmstring::numberToString<double>(frame_value);
                str += CMD_RESULT_SPLIT_CHAR;
                str += mmstring::numberToString<double>(error_value);
                result.append(MString(str.c_str()));
            }
        }

        for (auto it = Self::error_per_frame.cbegin();
             it != Self::error_per_frame.cend();) {
            const auto frame_value = it->first;
            const auto error_value = it->second;

            str = "error_per_frame=";
            str += mmstring::numberToString<double>(frame_value);
            str += CMD_RESULT_SPLIT_CHAR;
            str += mmstring::numberToString<double>(error_value);
            result.append(MString(str.c_str()));

            // Only iterate over unique keys once.
            //
            // Skip to the next iterator that doesn't start with
            // 'frame_value'.
            while (++it != Self::error_per_frame.cend() &&
                   it->first == frame_value) {
            }
        }
    }
};

template <class T>
inline void hash_combine(std::size_t &s, const T &v) {
    std::hash<T> h;
    s ^= h(v) + 0x9e3779b9 + (s << 6) + (s >> 2);
}

struct MarkerAttrNamePair {
    typedef MarkerAttrNamePair Self;

    std::string marker_name;
    std::string attr_name;

    MarkerAttrNamePair(std::string marker_name_, std::string attr_name_)
        : marker_name(std::move(marker_name_))
        , attr_name(std::move(attr_name_)){};

    bool operator==(const Self &other) const {
        return (Self::marker_name == other.marker_name &&
                Self::attr_name == other.attr_name);
    }
};

namespace std {

template <>
struct hash<MarkerAttrNamePair> {
    size_t operator()(MarkerAttrNamePair const &s) const noexcept {
        size_t result = 0;
        size_t h1 = hash<string>{}(s.marker_name);
        size_t h2 = hash<string>{}(s.attr_name);
        hash_combine(result, h1);
        hash_combine(result, h2);
        return result;
    }
};

}  // namespace std

struct AffectsResult {
    typedef AffectsResult Self;

    std::unordered_map<MarkerAttrNamePair, bool> marker_affects_attribute;

    AffectsResult() = default;

    void fill(const MarkerPtrList &markerList, const AttrPtrList &attrList,
              const mmsolver::MatrixBool2D &markerToAttrMatrix) {
        for (uint32_t markerIndex = 0; markerIndex < markerToAttrMatrix.width();
             ++markerIndex) {
            for (uint32_t attrIndex = 0;
                 attrIndex < markerToAttrMatrix.height(); ++attrIndex) {
                MarkerPtr marker = markerList[markerIndex];
                AttrPtr attr = attrList[attrIndex];

                // Get node names.
                const MString markerNodeName = marker->getNodeName();
                const char *markerName = markerNodeName.asChar();

                // Get attribute full path.
                MPlug plug = attr->getPlug();
                MObject attrNode = plug.node();
                MFnDagNode attrFnDagNode(attrNode);
                MString attrNodeName = attrFnDagNode.fullPathName();

                const bool includeNodeName = false;
                const bool includeNonMandatoryIndices = true;
                const bool includeInstancedIndices = true;
                const bool useAlias = false;
                const bool useFullAttributePath = false;
                const bool useLongNames = true;
                MString attrAttrName = plug.partialName(
                    includeNodeName, includeNonMandatoryIndices,
                    includeInstancedIndices, useAlias, useFullAttributePath,
                    useLongNames);

                MString attrNameString = attrNodeName + "." + attrAttrName;
                const char *attrName = attrNameString.asChar();

                auto key = MarkerAttrNamePair(markerName, attrName);
                const bool value =
                    markerToAttrMatrix.at(markerIndex, attrIndex);
                Self::marker_affects_attribute.insert({key, value});
            }
        }
    }

    void add(const Self &other) {
        for (const auto &kv : other.marker_affects_attribute) {
            auto search = Self::marker_affects_attribute.find(kv.first);
            bool value = kv.second;
            if (search != Self::marker_affects_attribute.end()) {
                value = std::max(kv.second, search->second);
            }
            Self::marker_affects_attribute.insert({kv.first, value});
        }
    }

    void appendToMStringArray(MStringArray &result) {
        std::string str;
        for (const auto &kv : Self::marker_affects_attribute) {
            const std::string &marker_name = kv.first.marker_name;
            const std::string &attr_name = kv.first.attr_name;
            const int value = kv.second;

            str = "marker_affects_attribute=";
            str += marker_name;
            str += CMD_RESULT_SPLIT_CHAR;
            str += attr_name;
            str += CMD_RESULT_SPLIT_CHAR;
            str += mmstring::numberToString<int>(value);
            // str += CMD_RESULT_SPLIT_CHAR;
            // TODO: Should this also contain the frame number's that
            // are valid?

            result.append(MString(str.c_str()));
        }
    }
};

namespace {

void add_marker_names_to_unordered_set(
    MarkerPtrList &markerList,
    std::unordered_set<std::string> &out_marker_names) {
    // Reserve memory up-front.
    auto new_count = markerList.size();
    auto old_count = out_marker_names.size();
    out_marker_names.reserve(old_count + new_count);

    for (auto mit = markerList.cbegin(); mit != markerList.cend(); ++mit) {
        MarkerPtr marker = *mit;
        MString marker_name = marker->getLongNodeName();
        auto marker_name_char = marker_name.asChar();
        out_marker_names.insert(std::string(marker_name_char));
    }
}

void add_attribute_names_to_unordered_set(
    AttrPtrList &attrList, std::unordered_set<std::string> &out_attr_names) {
    // Reserve memory up-front.
    auto new_count = attrList.size();
    auto old_count = out_attr_names.size();
    out_attr_names.reserve(old_count + new_count);

    for (auto mit = attrList.cbegin(); mit != attrList.cend(); ++mit) {
        AttrPtr attr = *mit;
        MString attr_name = attr->getLongName();
        auto attr_name_char = attr_name.asChar();
        out_attr_names.insert(std::string(attr_name_char));
    }
}

template <typename T>
void combine_used_unordered_set_values(
    std::unordered_set<T> &used, std::unordered_set<T> &unused,
    const std::unordered_set<T> &other_used,
    const std::unordered_set<T> &other_unused) {
    for (const auto &value : other_used) {
        used.insert(value);

        // If the value is now used, we must ensure it's removed
        // from the '_unused' set.
        auto search_unused = unused.find(value);
        if (search_unused != unused.end()) {
            unused.erase(search_unused);
        }
    }

    for (const auto &value : other_unused) {
        unused.insert(value);
    }
}

}  // namespace

struct SolverObjectUsageResult {
    typedef SolverObjectUsageResult Self;

    std::unordered_set<std::string> markers_used;
    std::unordered_set<std::string> markers_unused;
    std::unordered_set<std::string> attributes_used;
    std::unordered_set<std::string> attributes_unused;

    SolverObjectUsageResult() = default;

    void fill(MarkerPtrList &usedMarkerList, MarkerPtrList &unusedMarkerList,
              AttrPtrList &usedAttrList, AttrPtrList &unusedAttrList) {
        add_marker_names_to_unordered_set(usedMarkerList, Self::markers_used);
        add_marker_names_to_unordered_set(unusedMarkerList,
                                          Self::markers_unused);

        add_attribute_names_to_unordered_set(usedAttrList,
                                             Self::attributes_used);
        add_attribute_names_to_unordered_set(unusedAttrList,
                                             Self::attributes_unused);
    }

    void add(const Self &other) {
        combine_used_unordered_set_values<std::string>(
            Self::markers_used, Self::markers_unused, other.markers_used,
            other.markers_unused);
        combine_used_unordered_set_values<std::string>(
            Self::attributes_used, Self::attributes_unused,
            other.attributes_used, other.attributes_unused);
    }

    void appendToMStringArray(MStringArray &result) {
        MString str;
        if (!Self::markers_used.empty()) {
            str = "markers_used=";
            for (const auto &value : Self::markers_used) {
                str += MString(value.c_str());
                str += CMD_RESULT_SPLIT_CHAR;
            }
            result.append(str);
        }

        if (!Self::markers_unused.empty()) {
            str = "markers_unused=";
            for (const auto &value : Self::markers_unused) {
                str += MString(value.c_str());
                str += CMD_RESULT_SPLIT_CHAR;
            }
            result.append(str);
        }

        if (!Self::attributes_used.empty()) {
            str = "attributes_used=";
            for (const auto &value : Self::attributes_used) {
                str += MString(value.c_str());
                str += CMD_RESULT_SPLIT_CHAR;
            }
            result.append(str);
        }

        if (!Self::attributes_unused.empty()) {
            str = "attributes_unused=";
            for (const auto &value : Self::attributes_unused) {
                str += MString(value.c_str());
                str += CMD_RESULT_SPLIT_CHAR;
            }
            result.append(str);
        }
    }
};

struct SolverObjectCountResult {
    typedef SolverObjectCountResult Self;

    int count;
    int parameter_count;
    int error_count;
    int marker_error_count;
    int attr_stiffness_error_count;
    int attr_smoothness_error_count;

    SolverObjectCountResult()
        : count(0)
        , parameter_count(0)
        , error_count(0)
        , marker_error_count(0)
        , attr_stiffness_error_count(0)
        , attr_smoothness_error_count(0) {}

    void fill(const int numberOfParameters, const int numberOfErrors,
              const int numberOfMarkerErrors,
              const int numberOfAttrStiffnessErrors,
              const int numberOfAttrSmoothnessErrors) {
        Self::count = 1;
        Self::parameter_count = numberOfParameters;
        Self::error_count = numberOfErrors;
        Self::marker_error_count = numberOfMarkerErrors;
        Self::attr_stiffness_error_count = numberOfAttrStiffnessErrors;
        Self::attr_smoothness_error_count = numberOfAttrSmoothnessErrors;
    }

    void add(const Self &other) {
        Self::parameter_count += other.parameter_count;
        Self::error_count += other.error_count;
        Self::marker_error_count += other.marker_error_count;
        Self::attr_stiffness_error_count += other.attr_stiffness_error_count;
        Self::attr_smoothness_error_count += other.attr_smoothness_error_count;

        Self::count += other.count;
    }

    void divide() {
        if (Self::count > 1) {
            Self::parameter_count /= count;
            Self::error_count /= count;
            Self::marker_error_count /= count;
            Self::attr_stiffness_error_count /= count;
            Self::attr_smoothness_error_count /= count;
        }
        Self::count = 1;
    }

    void appendToMStringArray(MStringArray &result) {
        std::string str;

        str = "numberOfParameters=";
        str += mmstring::numberToString<int>(Self::parameter_count);
        result.append(MString(str.c_str()));

        str = "numberOfErrors=";
        str += mmstring::numberToString<int>(Self::error_count);
        result.append(MString(str.c_str()));

        str = "numberOfMarkerErrors=";
        str += mmstring::numberToString<int>(Self::marker_error_count);
        result.append(MString(str.c_str()));

        str = "numberOfAttrStiffnessErrors=";
        str += mmstring::numberToString<int>(Self::attr_stiffness_error_count);
        result.append(MString(str.c_str()));

        str = "numberOfAttrSmoothnessErrors=";
        str += mmstring::numberToString<int>(Self::attr_smoothness_error_count);
        result.append(MString(str.c_str()));
    }
};

struct SolverFramesResult {
    typedef SolverFramesResult Self;

    std::unordered_set<int32_t> valid_frames;
    std::unordered_set<int32_t> invalid_frames;

    SolverFramesResult() : valid_frames(), invalid_frames() {}

    void fill(const size_t total_frame_count,
              std::unordered_set<int32_t> &&valid_frames_,
              std::unordered_set<int32_t> &&invalid_frames_) {
        Self::valid_frames = std::move(valid_frames_);
        Self::invalid_frames = std::move(invalid_frames_);
    }

    void add(const Self &other) {
        combine_used_unordered_set_values<int32_t>(
            Self::valid_frames, Self::invalid_frames, other.valid_frames,
            other.invalid_frames);
    }

    void appendToMStringArray(MStringArray &result) {
        MString str;
        std::string number_str;

        number_str = mmstring::numberToString<int>(Self::valid_frames.size());
        str = "number_of_valid_frames=";
        str += MString(number_str.c_str());
        result.append(str);

        number_str = mmstring::numberToString<int>(Self::invalid_frames.size());
        str = "number_of_invalid_frames=";
        str += MString(number_str.c_str());
        result.append(str);

        if (!Self::valid_frames.empty()) {
            str = "valid_frames=";
            for (const auto &value : Self::valid_frames) {
                number_str = mmstring::numberToString<int>(value);
                str += MString(number_str.c_str());
                str += CMD_RESULT_SPLIT_CHAR;
            }
            result.append(str);
        }

        if (!Self::invalid_frames.empty()) {
            str = "invalid_frames=";
            for (const auto &value : Self::invalid_frames) {
                number_str = mmstring::numberToString<int>(value);
                str += MString(number_str.c_str());
                str += CMD_RESULT_SPLIT_CHAR;
            }
            result.append(str);
        }
    }
};

struct CommandResult {
    typedef CommandResult Self;

    // Used to control what parts of the command result are used.
    PrintStatOptions printStats;

    SolverResult solverResult;
    TimerResult timerResult;
    SolveValuesResult solveValuesResult;
    ErrorMetricsResult errorMetricsResult;
    AffectsResult affectsResult;
    SolverObjectUsageResult solverObjectUsageResult;
    SolverObjectCountResult solverObjectCountResult;
    SolverFramesResult solverFramesResult;

    CommandResult() = default;

    void add(const CommandResult &other) {
        if (Self::printStats.affects) {
            Self::affectsResult.add(other.affectsResult);
        }

        if (Self::printStats.usedSolveObjects) {
            Self::solverObjectUsageResult.add(other.solverObjectUsageResult);
        }

        if (Self::printStats.input) {
            Self::solverObjectCountResult.add(other.solverObjectCountResult);
        }

        Self::solverResult.add(other.solverResult);
        Self::timerResult.add(other.timerResult);
        Self::errorMetricsResult.add(other.errorMetricsResult);
        Self::solveValuesResult.add(other.solveValuesResult);
        Self::solverFramesResult.add(other.solverFramesResult);
    }

    void divide() {
        if (Self::printStats.input) {
            Self::solverObjectCountResult.divide();
        }

        Self::solverResult.divide();
        Self::timerResult.divide();
        Self::errorMetricsResult.divide();
        Self::solveValuesResult.divide();
    }

    void appendToMStringArray(MStringArray &result) {
        // The order of each print out is specific and is for
        // backwards compatibility.

        if (Self::printStats.input) {
            Self::solverObjectCountResult.appendToMStringArray(result);
        }

        if (Self::printStats.usedSolveObjects) {
            Self::solverObjectUsageResult.appendToMStringArray(result);
        }

        if (Self::printStats.affects) {
            Self::affectsResult.appendToMStringArray(result);
        }

        Self::solverResult.appendToMStringArray(result);
        Self::timerResult.appendToMStringArray(result);
        Self::errorMetricsResult.appendToMStringArray(result);
        Self::solveValuesResult.appendToMStringArray(result);
        Self::solverFramesResult.appendToMStringArray(result);
    }
};

#endif  // MM_SOLVER_CORE_BUNDLE_ADJUST_RESULTS_H
