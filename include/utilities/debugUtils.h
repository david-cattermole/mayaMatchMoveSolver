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

#ifndef DEBUG_UTILS_H
#define DEBUG_UTILS_H

// STL
#include <iostream> // cout, cerr, endl
#include <iomanip>  // setfill, setw
#include <string>   // string

// Maya
#include <maya/MTypes.h>
#include <maya/MStreamUtils.h>

#ifdef _WIN32
    #include <intrin.h>
    #include <Windows.h>  // GetSystemTime
    #ifdef max
        // On Windows max is defined as a macro, but this
        // conflicts with the C++ standard, so we undef it after
        // including it in 'Windows.h'.
        #undef max
    #endif
#else
    // Linux Specific Functions
    #include <sys/time.h>  // gettimeofday
    #include <sys/types.h> // uint32_t, uint64_t, etc
#endif

// Debug defines...
//#ifndef NDEBUG
//#  define MMSOLVER_DBG(x)
//#else
#ifdef _WIN32  // Windows MSVC
#define MMSOLVER_DBG(x)                                                          \
    __pragma(warning(push))                                             \
    __pragma(warning(disable:4127))                                     \
    do { MStreamUtils::stdErrorStream() << __FILE__  << ':' << __LINE__ << ' ' << x << std::endl; } while (0); \
    __pragma(warning(pop))
#else  // Linux and MacOS
#define MMSOLVER_DBG(x) do { MStreamUtils::stdErrorStream() << __FILE__  << ':' << __LINE__ << ' ' << x << std::endl; } while (0)
#endif
//#endif // NDEBUG

#ifdef _WIN32  // Windows MSVC
#define MMSOLVER_VRB(x)                                                       \
    __pragma(warning(push))                                          \
    __pragma(warning(disable:4127))                                  \
    do { if (verbose) { MStreamUtils::stdErrorStream() << x << std::endl; } } while (0);       \
    __pragma(warning(pop))
#else  // Linux and MacOS
#define MMSOLVER_VRB(x) do { if (verbose) { MStreamUtils::stdErrorStream() << x << std::endl; } } while (0)
#endif

#ifdef _WIN32  // Windows MSVC
#define MMSOLVER_ERR(x)                                              \
    __pragma(warning(push))                                 \
    __pragma(warning(disable:4127))                         \
    do { MStreamUtils::stdErrorStream() << "ERROR: " << x << std::endl; } while (0);  \
    __pragma(warning(pop))
#else  // Linux and MacOS
#define MMSOLVER_ERR(x) do { MStreamUtils::stdErrorStream()  << "ERROR: " << x << std::endl; } while (0)
#endif

#ifdef _WIN32  // Windows MSVC
#define MMSOLVER_WRN(x)                                                  \
    __pragma(warning(push))                                     \
    __pragma(warning(disable:4127))                             \
    do { MStreamUtils::stdErrorStream()  << "WARNING: " << x << std::endl; } while (0);    \
    __pragma(warning(pop))
#else  // Linux and MacOS
#define MMSOLVER_WRN(x) do { MStreamUtils::stdErrorStream() << "WARNING: " << x << std::endl; } while (0)
#endif

#ifdef _WIN32  // Windows MSVC
#define MMSOLVER_INFO(x)                                                     \
    __pragma(warning(push))                                         \
    __pragma(warning(disable:4127))                                 \
    do { MStreamUtils::stdErrorStream() << x << std::endl; } while (0);                       \
    __pragma(warning(pop))
#else  // Linux and MacOS
#define MMSOLVER_INFO(x) do { MStreamUtils::stdErrorStream() << x << std::endl; } while (0)
#endif

// Used to indicate to the user that a variable is not used, and
// avoids the compilier from printing warnings/errors about unused
// variables.
//
// https://stackoverflow.com/questions/308277/what-are-the-consequences-of-ignoring-warning-unused-parameter/308286#308286
#ifdef _WIN32  // Windows MSVC

#define UNUSED(expr)                                                \
    __pragma(warning(push))                                         \
    __pragma(warning(disable:4127))                                 \
    do { (void)(expr); } while (0);                                 \
    __pragma(warning(pop))
#else  // Linux and MacOS
#define UNUSED(expr) do { (void)(expr); } while (0)
#endif

namespace debug {
    typedef unsigned int uint32;
    typedef unsigned long long uint64;
    typedef unsigned long long Ticks;

    // Measuring CPU Clock-Cycles on Windows or Linux.
    // http://stackoverflow.com/questions/13772567/get-cpu-cycle-count
#ifdef _WIN32
    //  Windows
    #pragma intrinsic(__rdtsc)
	static inline
	DWORD64 rdtsc(){
      return __rdtsc();
  }

#else

    //  Linux/GCC
    static inline
    uint64 rdtsc() {
        uint32 lo, hi;
        __asm__ __volatile__ ("rdtsc" : "=a" (lo), "=d" (hi));
        return ((uint64) hi << 32) | lo;
    }

#endif

    // Get time of day with high accuracy, on both Windows and Linux.
    //
    // http://stackoverflow.com/questions/1861294/how-to-calculate-execution-time-of-a-code-snippet-in-cw
    typedef unsigned long long Timestamp;

    // Get the current time - used for profiling and debug.
    inline
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

      uint64 ret = li.QuadPart;
      // Convert from file time to UNIX epoch time.
      ret -= 116444736000000000LL;
      // From 100 nano seconds (10^-7) to 1 millisecond (10^-3)
      // intervals
      ret /= 10000;

      return ret;
#else
      // For Linux
      struct timeval now;
      gettimeofday(&now, NULL);
      return now.tv_usec + (Timestamp) now.tv_sec * 1000000;
#endif
    }

    // CPU Clock-cycle timing.
    //
    // Article1: http://lemire.me/blog/2012/06/20/do-not-waste-time-with-stl-vectors/
    // Article2: http://stackoverflow.com/questions/13772567/get-cpu-cycle-count
    // Code: https://github.com/lemire/Code-used-on-Daniel-Lemire-s-blog/blob/master/2012/06/20/testvector.cpp
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

    // Wrapper class around assembly clock cycle timer.
    class CPUBenchmark {
    public:
        CPUBenchmark() :
                ticktime(0),
                ticktimeTotal(0){
            start();
        }

        Ticks ticktime;
        Ticks ticktimeTotal;

        void start() {
            ticktime = rdtsc();
        }

        Ticks stop() {
            return ticktimeTotal += rdtsc() - ticktime;
        }

        Ticks get_ticks(unsigned int loopNums = 0) {
            Ticks total = ticktimeTotal;
            if (loopNums > 0) {
                total /= loopNums;
            }
            return total;
        }

        void print(std::string heading, unsigned int loopNums = 0) {
            Ticks ticks = get_ticks(loopNums);
            if (loopNums <= 1) {
                MStreamUtils::stdErrorStream() << heading << " Ticks: ";
            } else if (loopNums > 0) {
                MStreamUtils::stdErrorStream() << heading << " Ticks (per-loop): ";
            }
            MStreamUtils::stdErrorStream() << ticks << " ticks";
            MStreamUtils::stdErrorStream() << std::endl;
        }
    };


    // Wrapper class around 'get_timestamp' timer.
    class TimestampBenchmark {
    public:
        TimestampBenchmark() :
                timestamp(0),
                timestampTotal(0) {
            start();
        }

        Timestamp timestamp;
        Timestamp timestampTotal;

        void start() {
            timestamp = get_timestamp();
        }

        Timestamp stop() {
            return timestampTotal += get_timestamp() - timestamp;
        }

        double get_seconds(unsigned int loopNums = 0) {
            double secs = (double) (timestampTotal / 1000000.0L);
            if (loopNums > 0) {
                secs /= loopNums;
            }
            return secs;
        }

        void print(std::string heading, unsigned int loopNums = 0) {
            return printInSec(heading, loopNums);
        }

        void printInSec(std::string heading, unsigned int loopNums = 0) {
            double secs = get_seconds(loopNums);
            if (loopNums <= 1) {
                MStreamUtils::stdErrorStream() << heading << " Time: ";
            } else if (loopNums > 0) {
                MStreamUtils::stdErrorStream() << heading << " Time (per-loop): ";
            }
            MStreamUtils::stdErrorStream() << secs << " seconds";
            MStreamUtils::stdErrorStream() << std::endl;
        }

    };

} // namespace debug

#endif // DEBUG_UTILS_H
