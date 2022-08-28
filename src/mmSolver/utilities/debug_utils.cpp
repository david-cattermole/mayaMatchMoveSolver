/*
 * Copyright (C) 2018, 2019 David Cattermole.
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
 */

#include "debug_utils.h"

// STL
#include <iomanip>   // setfill, setw
#include <iostream>  // cout, cerr, endl
#include <string>    // string

// Maya
#include <maya/MStreamUtils.h>

namespace debug {

#ifdef _WIN32
//  Windows
#pragma intrinsic(__rdtsc)
DWORD64 rdtsc() { return __rdtsc(); }
#else
//  Linux/GCC
uint64_t rdtsc() {
    uint32_t lo, hi;
    __asm__ __volatile__("rdtsc" : "=a"(lo), "=d"(hi));
    return ((uint64_t)hi << 32) | lo;
}
#endif

Timestamp get_timestamp() {
#ifdef _WIN32
    // Windows
    FILETIME ft;
    LARGE_INTEGER li;

    // Get the amount of 100 nano seconds intervals elapsed since
    // January 1, 1601 (UTC) and copy it to a LARGE_INTEGER
    // structure.
    GetSystemTimeAsFileTime(&ft);
    li.LowPart = ft.dwLowDateTime;
    li.HighPart = ft.dwHighDateTime;

    Timestamp ret = li.QuadPart;
    // Convert from file time to UNIX epoch time.
    ret -= 116444736000000000LL;
    // From 100 nano seconds (10^-7) to 1 millisecond (10^-3)
    // intervals
    ret /= 10000;

    return ret;
#else
    // For Linux
    struct timeval now;
    gettimeofday(&now, nullptr);
    Timestamp ret = tv.tv_usec;

    // Convert from micro seconds (10^-6) to milliseconds (10^-3)
    ret /= 1000;

    // Adds the seconds (10^0) after converting them to milliseconds (10^-3)
    ret += (tv.tv_sec * 1000);
    return ret;
#endif
}

double timestamp_as_seconds(Timestamp timestamp) {
    return static_cast<double>(timestamp) / 1000.0;
}

void CPUBenchmark::start() { ticktime = rdtsc(); }

Ticks CPUBenchmark::stop() { return ticktimeTotal += rdtsc() - ticktime; }

Ticks CPUBenchmark::get_ticks(uint32_t loopNums) {
    Ticks total = ticktimeTotal;
    if (loopNums > 0) {
        total /= loopNums;
    }
    return total;
}

void CPUBenchmark::print(std::string heading, uint32_t loopNums) {
    Ticks ticks = get_ticks(loopNums);
    if (loopNums <= 1) {
        MStreamUtils::stdErrorStream() << heading << " Ticks: ";
    } else if (loopNums > 0) {
        MStreamUtils::stdErrorStream() << heading << " Ticks (per-loop): ";
    }
    MStreamUtils::stdErrorStream() << ticks << " ticks";
    MStreamUtils::stdErrorStream() << std::endl;
}

void TimestampBenchmark::start() { timestamp = get_timestamp(); }

Timestamp TimestampBenchmark::stop() {
    return timestampTotal += get_timestamp() - timestamp;
}

double TimestampBenchmark::get_seconds(uint32_t loopNums) {
    double secs = timestamp_as_seconds(timestampTotal);
    if (loopNums > 0) {
        secs /= loopNums;
    }
    return secs;
}

void TimestampBenchmark::print(std::string heading, uint32_t loopNums) {
    return printInSec(heading, loopNums);
}

void TimestampBenchmark::printInSec(std::string heading, uint32_t loopNums) {
    double secs = get_seconds(loopNums);
    if (loopNums <= 1) {
        MStreamUtils::stdErrorStream() << heading << " Time: ";
    } else if (loopNums > 0) {
        MStreamUtils::stdErrorStream() << heading << " Time (per-loop): ";
    }
    MStreamUtils::stdErrorStream() << secs << " seconds";
    MStreamUtils::stdErrorStream() << std::endl;
}

}  // namespace debug
