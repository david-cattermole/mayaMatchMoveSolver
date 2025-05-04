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
#include <iostream>  // cout, cerr, endl

// Maya
//
// Maya 2019 (on Linux) requires this include happens first, but Maya
// 2020+ doesn't seem to mind.
#include <maya/MTypes.h>
//
#include <maya/MStreamUtils.h>

// MM Solver Libs
#include <mmsolverlibs/debug.h>

// Debug defines...
#ifdef _WIN32  // Windows MSVC
#define MMSOLVER_MAYA_DBG(x)                                         \
    __pragma(warning(push)) __pragma(warning(disable : 4127)) do {   \
        MStreamUtils::stdErrorStream()                               \
            << __FILE__ << ':' << __LINE__ << ' ' << x << std::endl; \
    }                                                                \
    while (0)                                                        \
        ;                                                            \
    __pragma(warning(pop))
#else  // Linux and MacOS
#define MMSOLVER_MAYA_DBG(x)                                         \
    do {                                                             \
        MStreamUtils::stdErrorStream()                               \
            << __FILE__ << ':' << __LINE__ << ' ' << x << std::endl; \
    } while (0);
#endif

#ifdef _WIN32  // Windows MSVC
#define MMSOLVER_MAYA_VRB(x)                                       \
    __pragma(warning(push)) __pragma(warning(disable : 4127)) do { \
        if (verbose) {                                             \
            MStreamUtils::stdErrorStream() << x << std::endl;      \
        }                                                          \
    }                                                              \
    while (0)                                                      \
        ;                                                          \
    __pragma(warning(pop))
#else  // Linux and MacOS
#define MMSOLVER_MAYA_VRB(x)                                  \
    do {                                                      \
        if (verbose) {                                        \
            MStreamUtils::stdErrorStream() << x << std::endl; \
        }                                                     \
    } while (0);
#endif

#ifdef _WIN32  // Windows MSVC
#define MMSOLVER_MAYA_ERR(x)                                           \
    __pragma(warning(push)) __pragma(warning(disable : 4127)) do {     \
        MStreamUtils::stdErrorStream() << "ERROR: " << x << std::endl; \
    }                                                                  \
    while (0)                                                          \
        ;                                                              \
    __pragma(warning(pop))
#else  // Linux and MacOS
#define MMSOLVER_MAYA_ERR(x)                                           \
    do {                                                               \
        MStreamUtils::stdErrorStream() << "ERROR: " << x << std::endl; \
    } while (0);
#endif

#ifdef _WIN32  // Windows MSVC
#define MMSOLVER_MAYA_WRN(x)                                             \
    __pragma(warning(push)) __pragma(warning(disable : 4127)) do {       \
        MStreamUtils::stdErrorStream() << "WARNING: " << x << std::endl; \
    }                                                                    \
    while (0)                                                            \
        ;                                                                \
    __pragma(warning(pop))
#else  // Linux and MacOS
#define MMSOLVER_MAYA_WRN(x)                                             \
    do {                                                                 \
        MStreamUtils::stdErrorStream() << "WARNING: " << x << std::endl; \
    } while (0);
#endif

#ifdef _WIN32  // Windows MSVC
#define MMSOLVER_MAYA_INFO(x)                                      \
    __pragma(warning(push)) __pragma(warning(disable : 4127)) do { \
        MStreamUtils::stdErrorStream() << x << std::endl;          \
    }                                                              \
    while (0)                                                      \
        ;                                                          \
    __pragma(warning(pop))
#else  // Linux and MacOS
#define MMSOLVER_MAYA_INFO(x)                             \
    do {                                                  \
        MStreamUtils::stdErrorStream() << x << std::endl; \
    } while (0);
#endif

namespace debug {}  // namespace debug

#endif  // DEBUG_UTILS_H
