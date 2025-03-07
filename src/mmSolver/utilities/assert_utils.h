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

// Quit the program, showing a message why and where the failure
// happened.
//
// Similar to the "panic!()" macro in Rust.
#define MMSOLVER_PANIC(...) MMSOLVER_CORE_PANIC(##__VA_ARGS__)

// Quit the program, showing a message why and where the failure happened.
#define MMSOLVER_TODO(...) MMSOLVER_CORE_TODO(##__VA_ARGS__)

#endif  // MM_SOLVER_ASSERT_UTILS_H
