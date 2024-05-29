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
 * Debugging Utils - printing and benchmarking.
 */

#ifndef MM_SOLVER_LIBS_DEBUG_H
#define MM_SOLVER_LIBS_DEBUG_H

#include <cstdint>   // uint32_t, uint64_t
#include <iomanip>   // setfill, setw
#include <iostream>  // cout, cerr, endl
#include <ostream>   // ostream
#include <string>    // string

#ifdef _WIN32
#include <Windows.h>  // GetSystemTime
#include <intrin.h>
#ifdef max
// On Windows max is defined as a macro, but this
// conflicts with the C++ standard, so we undef it after
// including it in 'Windows.h'.
#undef max
#endif
#else
// Linux Specific Functions
#include <sys/time.h>  // gettimeofday
#endif

// Debug defines...
#ifdef _WIN32  // Windows MSVC
#define MMSOLVER_CORE_DBG(stream, x)                                    \
    __pragma(warning(push)) __pragma(warning(disable : 4127)) do {      \
        stream << __FILE__ << ':' << __LINE__ << ' ' << x << std::endl; \
    }                                                                   \
    while (0)                                                           \
        ;                                                               \
    __pragma(warning(pop))
#else  // Linux and MacOS
#define MMSOLVER_CORE_DBG(stream, x)                                    \
    do {                                                                \
        stream << __FILE__ << ':' << __LINE__ << ' ' << x << std::endl; \
    } while (0)
#endif

#ifdef _WIN32  // Windows MSVC
#define MMSOLVER_CORE_VRB(stream, x)                               \
    __pragma(warning(push)) __pragma(warning(disable : 4127)) do { \
        if (verbose) {                                             \
            stream << x << std::endl;                              \
        }                                                          \
    }                                                              \
    while (0)                                                      \
        ;                                                          \
    __pragma(warning(pop))
#else  // Linux and MacOS
#define MMSOLVER_CORE_VRB(stream, x)  \
    do {                              \
        if (verbose) {                \
            stream << x << std::endl; \
        }                             \
    } while (0)
#endif

#ifdef _WIN32  // Windows MSVC
#define MMSOLVER_CORE_ERR(stream, x)                               \
    __pragma(warning(push)) __pragma(warning(disable : 4127)) do { \
        stream << "ERROR: " << x << std::endl;                     \
    }                                                              \
    while (0)                                                      \
        ;                                                          \
    __pragma(warning(pop))
#else  // Linux and MacOS
#define MMSOLVER_CORE_ERR(stream, x)           \
    do {                                       \
        stream << "ERROR: " << x << std::endl; \
    } while (0)
#endif

#ifdef _WIN32  // Windows MSVC
#define MMSOLVER_CORE_WRN(stream, x)                               \
    __pragma(warning(push)) __pragma(warning(disable : 4127)) do { \
        stream << "WARNING: " << x << std::endl;                   \
    }                                                              \
    while (0)                                                      \
        ;                                                          \
    __pragma(warning(pop))
#else  // Linux and MacOS
#define MMSOLVER_CORE_WRN(stream, x)             \
    do {                                         \
        stream << "WARNING: " << x << std::endl; \
    } while (0)
#endif

#ifdef _WIN32  // Windows MSVC
#define MMSOLVER_CORE_INFO(stream, x)                              \
    __pragma(warning(push)) __pragma(warning(disable : 4127)) do { \
        stream << x << std::endl;                                  \
    }                                                              \
    while (0)                                                      \
        ;                                                          \
    __pragma(warning(pop))
#else  // Linux and MacOS
#define MMSOLVER_CORE_INFO(stream, x) \
    do {                              \
        stream << x << std::endl;     \
    } while (0)
#endif

// Used to indicate to the user that a variable is not used, and
// avoids the compilier from printing warnings/errors about unused
// variables.
//
// https://stackoverflow.com/questions/308277/what-are-the-consequences-of-ignoring-warning-unused-parameter/308286#308286
#ifdef _WIN32  // Windows MSVC

#define MMSOLVER_CORE_UNUSED(expr)                                 \
    __pragma(warning(push)) __pragma(warning(disable : 4127)) do { \
        (void)(expr);                                              \
    }                                                              \
    while (0)                                                      \
        ;                                                          \
    __pragma(warning(pop))
#else  // Linux and MacOS
#define MMSOLVER_CORE_UNUSED(expr) \
    do {                           \
        (void)(expr);              \
    } while (0)
#endif

namespace mmsolver {
namespace debug {

using Ticks = unsigned long long;

// Get time of day with high accuracy, on both Windows and Linux.
//
// http://stackoverflow.com/questions/1861294/how-to-calculate-execution-time-of-a-code-snippet-in-cw
using Timestamp = unsigned long long;

// Measuring CPU Clock-Cycles on Windows or Linux.
// http://stackoverflow.com/questions/13772567/get-cpu-cycle-count
#ifdef _WIN32
//  Windows
#pragma intrinsic(__rdtsc)
static DWORD64 current_cpu_cycle_count() { return __rdtsc(); }
#else
//  Linux/GCC
static uint64_t current_cpu_cycle_count() {
    uint32_t lo, hi;
    __asm__ __volatile__("rdtsc" : "=a"(lo), "=d"(hi));
    return ((uint64_t)hi << 32) | lo;
}
#endif

// Get the current time - used for profiling and debug.
//
// Returns the amount of milliseconds elapsed since the UNIX epoch.
static Timestamp get_timestamp() {
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
    Timestamp ret = now.tv_usec;

    // Convert from micro seconds (10^-6) to milliseconds (10^-3)
    ret /= 1000;

    // Adds the seconds (10^0) after converting them to milliseconds (10^-3)
    ret += (now.tv_sec * 1000);
    return ret;
#endif
}

static double timestamp_as_seconds(const Timestamp timestamp) {
    return static_cast<double>(timestamp) / 1000.0;
}

// CPU Clock-cycle timing.
//
// Article1:
// http://lemire.me/blog/2012/06/20/do-not-waste-time-with-stl-vectors/
// Article2: http://stackoverflow.com/questions/13772567/get-cpu-cycle-count
// Code:
// https://github.com/lemire/Code-used-on-Daniel-Lemire-s-blog/blob/master/2012/06/20/testvector.cpp
//
//
// Example Code Start:
//   CPUBenchmark time;
//   const size_t N = 100 * 1000 * 1000 ;
//   time.start();
//   std::cout.precision(3);
//   std::cout << " report speed in CPU cycles per integer" << std::endl;
//   std::cout << std::endl << "ignore this:" << runtestnice(N) << std::endl;
//   std::cout << "with push_back:"<<(time.stop()*1.0/N)<<std::endl;
// Example Code End:
//

// Wrapper struct around assembly clock cycle timer.
struct CPUBenchmark {
public:
    CPUBenchmark() : ticktime(0), ticktimeTotal(0) { start(); }

    Ticks ticktime;
    Ticks ticktimeTotal;

    void start() { ticktime = current_cpu_cycle_count(); };
    Ticks stop() {
        return ticktimeTotal += current_cpu_cycle_count() - ticktime;
    };
    Ticks get_ticks(const uint32_t loopNums = 0) const {
        Ticks total = ticktimeTotal;
        if (loopNums > 0) {
            total /= loopNums;
        }
        return total;
    }
    void print(std::ostream &stream, const std::string &heading,
               const uint32_t loopNums = 0) const {
        const Ticks ticks = get_ticks(loopNums);
        if (loopNums <= 1) {
            stream << heading << " Ticks: ";
        } else if (loopNums > 0) {
            stream << heading << " Ticks (per-loop): ";
        }
        stream << ticks << " ticks";
        stream << std::endl;
    }
};

// Wrapper struct around 'get_timestamp' timer.
struct TimestampBenchmark {
public:
    TimestampBenchmark() : timestamp(0), timestampTotal(0) { start(); }

    Timestamp timestamp;
    Timestamp timestampTotal;

    void start() { TimestampBenchmark::timestamp = get_timestamp(); };
    Timestamp stop() { return TimestampBenchmark::timestampTotal += get_timestamp() - TimestampBenchmark::timestamp; };

    double get_seconds(const uint32_t loopNums = 0) const {
        double secs = timestamp_as_seconds(TimestampBenchmark::timestampTotal);
        if (loopNums > 0) {
            secs /= loopNums;
        }
        return secs;
    }

    void print(std::ostream &stream, const std::string &heading,
               const uint32_t loopNums = 0) const {
        return printInSec(stream, heading, loopNums);
    }

    void printInSec(std::ostream &stream, const std::string &heading,
                    const uint32_t loopNums = 0) const {
        const double secs = get_seconds(loopNums);
        if (loopNums <= 1) {
            stream << heading << " Time: ";
        } else if (loopNums > 0) {
            stream << heading << " Time (per-loop): ";
        }
        stream << secs << " seconds";
        stream << std::endl;
    }
};

}  // namespace debug
}  // namespace mmsolver

#endif  // MM_SOLVER_LIBS_DEBUG_H
