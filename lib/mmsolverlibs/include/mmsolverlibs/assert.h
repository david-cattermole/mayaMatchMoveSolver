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
#include <ostream>
#include <sstream>
#include <string>
#include <thread>

// Define our own debug flag if not already defined.
#ifndef MMSOLVER_DEBUG
#if defined(_DEBUG) || defined(DEBUG) || !defined(NDEBUG)
#define MMSOLVER_DEBUG 1
#else
#define MMSOLVER_DEBUG 0
#endif
#endif

// Project's name string.
#ifndef MMASSERT_PROJECT_NAME
#define MMASSERT_PROJECT_NAME ::mmsolverlibs::build_info::project_name()
#endif

// Project's version string.
#ifndef MMASSERT_PROJECT_VERSION
#define MMASSERT_PROJECT_VERSION ::mmsolverlibs::build_info::project_version()
#endif

// Project's System.
#ifndef MMASSERT_SYSTEM
#define MMASSERT_SYSTEM ::mmsolverlibs::build_info::system()
#endif

// Define your project root directory path
#ifndef MMASSERT_SOURCE_DIR
#define MMASSERT_SOURCE_DIR ::mmsolverlibs::build_info::source_dir()
#endif

// Project's build type.
#ifndef MMASSERT_BUILD_TYPE
#define MMASSERT_BUILD_TYPE ::mmsolverlibs::build_info::build_type()
#endif

// Project's build date/time.
#ifndef MMASSERT_BUILD_DATE_TIME
#define MMASSERT_BUILD_DATE_TIME ::mmsolverlibs::build_info::build_date_time()
#endif

// Project's git branch name string.
#ifndef MMASSERT_GIT_BRANCH
#define MMASSERT_GIT_BRANCH ::mmsolverlibs::build_info::git_branch()
#endif

// Project's git commit long hash string.
#ifndef MMASSERT_GIT_COMMIT_HASH_LONG
#define MMASSERT_GIT_COMMIT_HASH_LONG \
    ::mmsolverlibs::build_info::git_commit_hash_long()
#endif

// Project's git commit short hash string.
#ifndef MMASSERT_GIT_COMMIT_HASH_SHORT
#define MMASSERT_GIT_COMMIT_HASH_SHORT \
    ::mmsolverlibs::build_info::git_commit_hash_short()
#endif

// Project's CMake version.
#ifndef MMASSERT_CMAKE_VERSION
#define MMASSERT_CMAKE_VERSION ::mmsolverlibs::build_info::cmake_version()
#endif

// Project's CMake generator.
#ifndef MMASSERT_CMAKE_GENERATOR
#define MMASSERT_CMAKE_GENERATOR ::mmsolverlibs::build_info::cmake_generator()
#endif

// Project's C++ compiler details string.
#ifndef MMASSERT_CXX_COMPILER
#define MMASSERT_CXX_COMPILER ::mmsolverlibs::build_info::cxx_compiler()
#endif

// Project's C++ compiler linker details string.
#ifndef MMASSERT_CXX_LINKER
#define MMASSERT_CXX_LINKER ::mmsolverlibs::build_info::cxx_linker()
#endif

namespace mmsolverlibs {
namespace assert {

namespace {

std::string to_canonical_path(const char* input) {
    if (!static_cast<bool>(input)) {
        // Handle null pointer.
        return "";
    }

    std::string result(input);

    // Replace all forward slashes with backslashes.
    for (size_t i = 0; i < result.length(); ++i) {
        if (result[i] == '\\') {
            result[i] = '/';
        }
    }
    return result;
}

// Helper function to get relative file path
inline const char* get_relative_path(const char* file_path) {
    const char* project_root = MMASSERT_SOURCE_DIR;
    if (project_root[0] == '\0') {
        // No project root defined.
        return file_path;
    }

    // Convert both paths to use UNIX slashes. MSVC gives
    // back-slashes, CMake gives forward-slashes... so lets just
    // convert to using the same.
    const std::string file_path_clean = to_canonical_path(file_path);
    const std::string project_root_clean = to_canonical_path(project_root);

    const size_t index = file_path_clean.find(project_root_clean);
    const bool found = index != std::string::npos;
    if (!found && index == 0) {
        // Project root not found in path.
        return file_path;
    }

    // NOTE: We add one to remove the leading slash.
    return file_path + project_root_clean.size() + 1;
}

inline void ostream_add_function_line(std::ostream& ostream, const char* file,
                                      int line, const char* func) {
    ostream << "- Function: '" << func << "'\n"
            << "- File: " << get_relative_path(file) << '(' << line << ")\n";
}

inline void ostream_add_build_info_end(std::ostream& ostream) {
    const auto* const project_name = MMASSERT_PROJECT_NAME;
    const auto* const project_version = MMASSERT_PROJECT_VERSION;
    const auto* const system = MMASSERT_SYSTEM;
    const auto* const build_type = MMASSERT_BUILD_TYPE;
    const auto* const build_date_time = MMASSERT_BUILD_DATE_TIME;
    const auto* const git_branch = MMASSERT_GIT_BRANCH;
    const auto* const git_commit_hash_long = MMASSERT_GIT_COMMIT_HASH_LONG;
    const auto* const cmake_version = MMASSERT_CMAKE_VERSION;
    const auto* const cmake_generator = MMASSERT_CMAKE_GENERATOR;
    const auto* const cxx_compiler = MMASSERT_CXX_COMPILER;
    const auto* const cxx_linker = MMASSERT_CXX_LINKER;

    ostream << "- Project: " << project_name << "\n"
            << "- Project Version: " << project_version << "\n"
            << "- System: " << system << "\n"
            << "- Build Type: " << build_type << "\n"
            << "- Build Date-Time: " << build_date_time << "\n"
            << "- Git Branch: " << git_branch << "\n"
            << "- Git Commit: " << git_commit_hash_long << "\n"
            << "- CMake Version: " << cmake_version << "\n"
            << "- CMake Generator: " << cmake_generator << "\n"
            << "- C++ Compiler: " << cxx_compiler << "\n"
            << "- C++ Linker: " << cxx_linker << "\n";
}

}  // namespace

inline void print_assert(std::ostream& ostream, const char* file,
                         const int line, const char* func, const char* expr,
                         const std::string& msg) {
    ostream << "ASSERT FAILED! '" << msg << "'\n"
            << "- Condition: " << expr << "\n";
    ostream_add_function_line(ostream, file, line, func);
    ostream_add_build_info_end(ostream);
    ostream << std::flush;
}

inline void print_check(std::ostream& ostream, const char* file, const int line,
                        const char* func, const char* expr,
                        const std::string& msg) {
    ostream << "CHECK FAILED! '" << msg << "'\n"
            << "- Condition: " << expr << "\n";
    ostream_add_function_line(ostream, file, line, func);
    ostream_add_build_info_end(ostream);
    ostream << std::flush;
}

inline void print_panic(std::ostream& ostream, const char* file, const int line,
                        const char* func, const std::string& msg) {
    ostream << "PANIC! '" << msg << "'\n";
    ostream_add_function_line(ostream, file, line, func);
    ostream_add_build_info_end(ostream);
    ostream << std::flush;
}

inline void print_todo(std::ostream& ostream, const char* file, const int line,
                       const char* func, const std::string& msg) {
    ostream << "TODO! '" << msg << "'\n";
    ostream_add_function_line(ostream, file, line, func);
    ostream_add_build_info_end(ostream);
    ostream << std::flush;
}

inline void wait_abort() {
    // Give the OS a moment to flush buffers.
    std::this_thread::sleep_for(std::chrono::milliseconds(1000));

    std::abort();
}

}  // namespace assert
}  // namespace mmsolverlibs

// Always enabled assert that will abort.
#define MMSOLVER_CORE_ASSERT(condition, ...)                            \
    do {                                                                \
        if (!(condition)) {                                             \
            std::stringstream ss;                                       \
            ss << __VA_ARGS__;                                          \
            ::mmsolverlibs::assert::print_assert(std::cerr, __FILE__,   \
                                                 __LINE__, __func__,    \
                                                 #condition, ss.str()); \
            ::mmsolverlibs::assert::wait_abort();                       \
        }                                                               \
    } while (0)

// Debug-only assert that will abort.
#if MMSOLVER_CORE_DEBUG
#define MMSOLVER_CORE_ASSERT_DEBUG(condition, ...)                      \
    do {                                                                \
        if (!(condition)) {                                             \
            std::stringstream ss;                                       \
            ss << __VA_ARGS__;                                          \
            ::mmsolverlibs::assert::print_assert(std::cerr, __FILE__,   \
                                                 __LINE__, __func__,    \
                                                 #condition, ss.str()); \
            ::mmsolverlibs::assert::wait_abort();                       \
        }                                                               \
    } while (0)
#else
#define MMSOLVER_CORE_ASSERT_DEBUG(condition, ...) ((void)0)
#endif

// Always enabled check that will continue.
#define MMSOLVER_CORE_CHECK(condition, ...)                                    \
    do {                                                                       \
        if (!(condition)) {                                                    \
            std::stringstream ss;                                              \
            ss << __VA_ARGS__;                                                 \
            ::mmsolverlibs::assert::print_check(std::cerr, __FILE__, __LINE__, \
                                                __func__, #condition,          \
                                                ss.str());                     \
        }                                                                      \
    } while (0)

// Debug-only check that will continue.
#if MMSOLVER_CORE_DEBUG
#define MMSOLVER_CORE_CHECK_DEBUG(condition, ...)                              \
    do {                                                                       \
        if (!(condition)) {                                                    \
            std::stringstream ss;                                              \
            ss << __VA_ARGS__;                                                 \
            ::mmsolverlibs::assert::print_check(std::cerr, __FILE__, __LINE__, \
                                                __func__, #condition,          \
                                                ss.str());                     \
        }                                                                      \
    } while (0)
#else
#define MMSOLVER_CORE_CHECK_DEBUG(condition, ...) ((void)0)
#endif

// Quit the program, showing a message why and where the failure
// happened.
//
// Similar to the "panic!()" macro in Rust.
#define MMSOLVER_CORE_PANIC(...)                                           \
    do {                                                                   \
        std::stringstream ss;                                              \
        ss << __VA_ARGS__;                                                 \
        ::mmsolverlibs::assert::print_panic(std::cerr, __FILE__, __LINE__, \
                                            __func__, ss.str());           \
        ::mmsolverlibs::assert::wait_abort();                              \
    } while (0)

// Quit the program, showing a message why and where the failure happened.
#define MMSOLVER_CORE_TODO(...)                                           \
    do {                                                                  \
        std::stringstream ss;                                             \
        ss << __VA_ARGS__;                                                \
        ::mmsolverlibs::assert::print_todo(std::cerr, __FILE__, __LINE__, \
                                           __func__, ss.str());           \
        ::mmsolverlibs::assert::wait_abort();                             \
    } while (0)

// Clean up the defines made in this file.
#undef MMASSERT_PROJECT_NAME
#undef MMASSERT_PROJECT_VERSION
#undef MMASSERT_SYSTEM
#undef MMASSERT_SOURCE_DIR
#undef MMASSERT_BUILD_TYPE
#undef MMASSERT_BUILD_DATE_TIME
#undef MMASSERT_GIT_BRANCH
#undef MMASSERT_GIT_COMMIT_HASH_LONG
#undef MMASSERT_GIT_COMMIT_HASH_SHORT
#undef MMASSERT_CMAKE_VERSION
#undef MMASSERT_CMAKE_GENERATOR
#undef MMASSERT_CXX_COMPILER
#undef MMASSERT_CXX_LINKER

#endif  // MM_SOLVER_LIBS_ASSERT_H
