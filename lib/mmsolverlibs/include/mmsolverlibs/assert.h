/*
 * Copyright (C) 2023 David Cattermole.
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
 * Tools to assert and panic.
 */

#ifndef MM_SOLVER_LIBS_ASSERT_H
#define MM_SOLVER_LIBS_ASSERT_H

#include <cstdlib>
#include <iostream>

// The assert happens at runtime, even for release mode, so we can
// catch bugs as soon as possible.
#define MMSOLVER_ASSERT(condition, message)                             \
    do {                                                                \
        if (!(condition)) {                                             \
            std::cerr << __FILE__ << '(' << __LINE__                    \
                      << "): ASSERT: " << #condition << "; " << message \
                      << std::endl;                                     \
            std::abort();                                               \
        }                                                               \
    } while (0)

// Quit the program, showing a message why and where the failure
// happened.
//
// Similar to the "panic!()" macro in Rust.
#define MMSOLVER_PANIC(message)                                             \
    do {                                                                    \
        std::cerr << __FILE__ << '(' << __LINE__ << "): PANIC: " << message \
                  << std::endl;                                             \
        std::abort();                                                       \
    } while (0)

// Quit the program, showing a message why and where the failure
// happened.
//
// Similar to the "todo!()" macro in Rust.
#define MMSOLVER_TODO(message)                                             \
    do {                                                                   \
        std::cerr << __FILE__ << '(' << __LINE__ << "): TODO: " << message \
                  << std::endl;                                            \
        std::abort();                                                      \
    } while (0)

#endif  // MM_SOLVER_LIBS_ASSERT_H
