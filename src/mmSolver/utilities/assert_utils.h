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
 * Assertion utilities for mmSolver.
 */

#ifndef MM_SOLVER_ASSERT_UTILS_H
#define MM_SOLVER_ASSERT_UTILS_H

// Ensure the build constants are included first, so that the values
// here override the 'mmsolverlibs' default values.
#include <mmSolver/buildConstant.h>

// These defines are used in 'mmsolverlibs/assert.h' (and therefore
// must be defined before including 'mmsolverlibs/assert.h'), so
// defining these allows us to override so we configure the asserts to
// our needs.
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
#define MMASSERT_PROJECT_NAME ::mmsolver::build_info::project_name()
#define MMASSERT_PROJECT_VERSION ::mmsolver::build_info::project_version()
#define MMASSERT_SYSTEM ::mmsolver::build_info::system()
#define MMASSERT_SOURCE_DIR ::mmsolver::build_info::source_dir()
#define MMASSERT_BUILD_TYPE ::mmsolver::build_info::build_type()
#define MMASSERT_BUILD_DATE_TIME ::mmsolver::build_info::build_date_time()
#define MMASSERT_GIT_BRANCH ::mmsolver::build_info::git_branch()
#define MMASSERT_GIT_COMMIT_HASH_LONG \
    ::mmsolver::build_info::git_commit_hash_long()
#define MMASSERT_GIT_COMMIT_HASH_SHORT \
    ::mmsolver::build_info::git_commit_hash_short()
#define MMASSERT_CMAKE_VERSION ::mmsolver::build_info::cmake_version()
#define MMASSERT_CMAKE_GENERATOR ::mmsolver::build_info::cmake_generator()
#define MMASSERT_CXX_COMPILER ::mmsolver::build_info::cxx_compiler()
#define MMASSERT_CXX_LINKER ::mmsolver::build_info::cxx_linker()

// Maya
#include <maya/MStreamUtils.h>

// MM Solver Libs
#include <mmsolverlibs/assert.h>

// Always enabled assert that will abort.
#define MMSOLVER_ASSERT(condition, ...) \
    MMSOLVER_CORE_ASSERT(condition, ##__VA_ARGS__)

// Debug-only assert that will abort.
#define MMSOLVER_ASSERT_DEBUG(condition, ...) \
    MMSOLVER_CORE_ASSERT_DEBUG(condition, ##__VA_ARGS__)

// Always enabled check that will continue.
#define MMSOLVER_CHECK(condition, ...) \
    MMSOLVER_CORE_CHECK(condition, ##__VA_ARGS__)

// Debug-only check that will continue.
#define MMSOLVER_CHECK_DEBUG(condition, ...) \
    MMSOLVER_CORE_CHECK_DEBUG(condition, ##__VA_ARGS__)

// Always enabled check MStatus that will continue.
#define MMSOLVER_CHECK_MSTATUS(_status)                                       \
    do {                                                                      \
        if (MStatus::kSuccess != (_status)) {                                 \
            const MString _status_error_message = (_status).errorString();    \
            ::mmsolverlibs::assert::print_check(                              \
                MStreamUtils::stdErrorStream(), __FILE__, __LINE__, __func__, \
                "status != MStatus::kSuccess",                                \
                _status_error_message.asChar());                              \
        }                                                                     \
    } while (0)

// Always enabled check MStatus that will continue or return a value.
#define MMSOLVER_CHECK_MSTATUS_AND_RETURN(_status, _return_value)             \
    do {                                                                      \
        if (MStatus::kSuccess != (_status)) {                                 \
            const MString _status_error_message = (_status).errorString();    \
            ::mmsolverlibs::assert::print_check(                              \
                MStreamUtils::stdErrorStream(), __FILE__, __LINE__, __func__, \
                "status != MStatus::kSuccess",                                \
                _status_error_message.asChar());                              \
            return (_return_value);                                           \
        }                                                                     \
    } while (0)

// Always enabled check MStatus that will continue or return the MStatus.
#define MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(_status)                         \
    do {                                                                      \
        if (MStatus::kSuccess != (_status)) {                                 \
            const MString _status_error_message = (_status).errorString();    \
            ::mmsolverlibs::assert::print_check(                              \
                MStreamUtils::stdErrorStream(), __FILE__, __LINE__, __func__, \
                "status != MStatus::kSuccess",                                \
                _status_error_message.asChar());                              \
            return (_status);                                                 \
        }                                                                     \
    } while (0)

// Quit the program, showing a message why and where the failure
// happened.
//
// Similar to the "panic!()" macro in Rust.
#define MMSOLVER_PANIC(...) MMSOLVER_CORE_PANIC(__VA_ARGS__)

// Quit the program, showing a message why and where the failure happened.
#define MMSOLVER_TODO(...) MMSOLVER_CORE_TODO(__VA_ARGS__)

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

#endif  // MM_SOLVER_ASSERT_UTILS_H
