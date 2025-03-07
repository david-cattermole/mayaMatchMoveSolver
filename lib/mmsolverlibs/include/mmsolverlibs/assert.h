/*
 * Copyright (C) 2023, 2025 David Cattermole.
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
 * Tools to assert, check, panic and todo.
 */

#ifndef MM_SOLVER_LIBS_ASSERT_H
#define MM_SOLVER_LIBS_ASSERT_H

#include <mmsolverlibs/buildConstant.h>

// STL
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <sstream>
#include <string>

// Define our own debug flag if not already defined.
#ifndef MMSOLVER_DEBUG
#if defined(_DEBUG) || defined(DEBUG) || !defined(NDEBUG)
#define MMSOLVER_DEBUG 1
#else
#define MMSOLVER_DEBUG 0
#endif
#endif

// Project's name string.
#ifndef PROJECT_NAME
#define PROJECT_NAME MMSOLVER_CORE_PROJECT_NAME
#endif

// Project's version string.
#ifndef PROJECT_VERSION
#define PROJECT_VERSION MMSOLVER_CORE_PROJECT_VERSION
#endif

// Define your project root directory path
#ifndef PROJECT_SOURCE_DIR
#define PROJECT_SOURCE_DIR MMSOLVER_CORE_PROJECT_SOURCE_DIR
#endif

// Project's build date/time.
#ifndef PROJECT_BUILD_DATE_TIME
#define PROJECT_BUILD_DATE_TIME MMSOLVER_CORE_PROJECT_BUILD_DATE_TIME
#endif

// Project's git branch name string.
#ifndef PROJECT_GIT_BRANCH
#define PROJECT_GIT_BRANCH MMSOLVER_CORE_PROJECT_GIT_BRANCH
#endif

// Project's git commit long hash string.
#ifndef PROJECT_GIT_COMMIT_HASH_LONG
#define PROJECT_GIT_COMMIT_HASH_LONG MMSOLVER_CORE_PROJECT_GIT_COMMIT_HASH_LONG
#endif

// Project's git commit short hash string.
#ifndef PROJECT_GIT_COMMIT_HASH_SHORT
#define PROJECT_GIT_COMMIT_HASH_SHORT \
    MMSOLVER_CORE_PROJECT_GIT_COMMIT_HASH_SHORT
#endif

namespace mmsolverlibs {
namespace assert {

// Helper function to get relative file path
inline const char* get_relative_path(const char* file) {
    const char* project_root = PROJECT_SOURCE_DIR;
    if (project_root[0] == '\0') {
        return file;  // No project root defined, return full path
    }

    const char* found = std::strstr(file, project_root);
    if (found == nullptr) {
        return file;  // Project root not found in path, return full path
    }

    // Return path relative to project root
    return found + std::strlen(project_root);
}

// TODO: Do not hard-code 'std::cerr', and instead this should be similar to 'debug.h'
//  and allow a stream object to be passed in. This would allow Maya to print asserts
//  and checks to the Output Window on Windows.
inline void print_assert(const char* file, int line, const char* func,
                         const char* expr, const std::string& msg) {
    std::cerr << "ASSERT FAILED! '" << msg << "'\n"
              << "- Condition: " << expr << "\n"
              << "- File: " << get_relative_path(file) << '(' << line << ")\n"
              << "- Function: '" << func << "'\n"
              << "- Project: " << PROJECT_NAME << "\n"
              << "- Project Version: " << PROJECT_VERSION << "\n"
              << "- Build Date-Time: " << PROJECT_BUILD_DATE_TIME << "\n"
              << "- Git Branch: " << PROJECT_GIT_BRANCH << "\n"
              << "- Git Commit: " << PROJECT_GIT_COMMIT_HASH_LONG << std::endl;
}

inline void print_check(const char* file, int line, const char* func,
                        const char* expr, const std::string& msg) {
    std::cerr << "CHECK FAILED! '" << msg << "'\n"
              << "- Condition: " << expr << "\n"
              << "- File: " << get_relative_path(file) << '(' << line << ")\n"
              << "- Function: '" << func << "'\n"
              << "- Project: " << PROJECT_NAME << "\n"
              << "- Project Version: " << PROJECT_VERSION << "\n"
              << "- Build Date-Time: " << PROJECT_BUILD_DATE_TIME << "\n"
              << "- Git Branch: " << PROJECT_GIT_BRANCH << "\n"
              << "- Git Commit: " << PROJECT_GIT_COMMIT_HASH_LONG << std::endl;
}

inline void print_panic(const char* file, int line, const char* func,
                        const std::string& msg) {
    std::cerr << "PANIC! '" << msg << "'\n"
              << "- File: " << get_relative_path(file) << '(' << line << ")\n"
              << "- Function: '" << func << "'\n"
              << "- Project: " << PROJECT_NAME << "\n"
              << "- Project Version: " << PROJECT_VERSION << "\n"
              << "- Build Date-Time: " << PROJECT_BUILD_DATE_TIME << "\n"
              << "- Git Branch: " << PROJECT_GIT_BRANCH << "\n"
              << "- Git Commit: " << PROJECT_GIT_COMMIT_HASH_LONG << std::endl;
}

inline void print_todo(const char* file, int line, const char* func,
                       const std::string& msg) {
    std::cerr << "TODO! '" << msg << "'\n"
              << "- File: " << get_relative_path(file) << '(' << line << ")\n"
              << "- Function: '" << func << "'\n"
              << "- Project: " << PROJECT_NAME << "\n"
              << "- Project Version: " << PROJECT_VERSION << "\n"
              << "- Build Date-Time: " << PROJECT_BUILD_DATE_TIME << "\n"
              << "- Git Branch: " << PROJECT_GIT_BRANCH << "\n"
              << "- Git Commit: " << PROJECT_GIT_COMMIT_HASH_LONG << std::endl;
}

}  // namespace assert
}  // namespace mmsolverlibs

// Always enabled assert that will abort.
#define MMSOLVER_CORE_ASSERT(condition, ...)                                   \
    do {                                                                       \
        if (!(condition)) {                                                    \
            std::stringstream ss;                                              \
            ss << __VA_ARGS__;                                                 \
            ::mmsolverlibs::assert::print_assert(__FILE__, __LINE__, __func__, \
                                                 #condition, ss.str());        \
            std::abort();                                                      \
        }                                                                      \
    } while (0)

// Debug-only assert that will abort.
#if MMSOLVER_CORE_DEBUG
#define MMSOLVER_CORE_ASSERT_DEBUG(condition, ...)                             \
    do {                                                                       \
        if (!(condition)) {                                                    \
            std::stringstream ss;                                              \
            ss << __VA_ARGS__;                                                 \
            ::mmsolverlibs::assert::print_assert(__FILE__, __LINE__, __func__, \
                                                 #condition, ss.str());        \
            std::abort();                                                      \
        }                                                                      \
    } while (0)
#else
#define MMSOLVER_CORE_ASSERT_DEBUG(condition, ...) ((void)0)
#endif

// Always enabled check that will continue.
#define MMSOLVER_CORE_CHECK(condition, ...)                                   \
    do {                                                                      \
        if (!(condition)) {                                                   \
            std::stringstream ss;                                             \
            ss << __VA_ARGS__;                                                \
            ::mmsolverlibs::assert::print_check(__FILE__, __LINE__, __func__, \
                                                #condition, ss.str());        \
        }                                                                     \
    } while (0)

// Debug-only check that will continue.
#if MMSOLVER_CORE_DEBUG
#define MMSOLVER_CORE_CHECK_DEBUG(condition, ...)                             \
    do {                                                                      \
        if (!(condition)) {                                                   \
            std::stringstream ss;                                             \
            ss << __VA_ARGS__;                                                \
            ::mmsolverlibs::assert::print_check(__FILE__, __LINE__, __func__, \
                                                #condition, ss.str());        \
        }                                                                     \
    } while (0)
#else
#define MMSOLVER_CORE_CHECK_DEBUG(condition, ...) ((void)0)
#endif

// Quit the program, showing a message why and where the failure
// happened.
//
// Similar to the "panic!()" macro in Rust.
#define MMSOLVER_CORE_PANIC(...)                                          \
    do {                                                                  \
        std::stringstream ss;                                             \
        ss << __VA_ARGS__;                                                \
        ::mmsolverlibs::assert::print_panic(__FILE__, __LINE__, __func__, \
                                            ss.str());                    \
        std::abort();                                                     \
    } while (0)

// Quit the program, showing a message why and where the failure happened.
#define MMSOLVER_CORE_TODO(...)                                          \
    do {                                                                 \
        std::stringstream ss;                                            \
        ss << __VA_ARGS__;                                               \
        ::mmsolverlibs::assert::print_todo(__FILE__, __LINE__, __func__, \
                                           ss.str());                    \
        std::abort();                                                    \
    } while (0)

#endif  // MM_SOLVER_LIBS_ASSERT_H
