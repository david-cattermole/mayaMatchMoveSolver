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
 * These are core type definitions that are used throughout mmSolver.
 */

namespace mmsolver {

// The 'Count' type is intended to be used to count 32-bit index
// values (Index32).
typedef uint32_t Count32;

// 'Index' value must be able to include negative values, such as
// '-1'.
typedef int32_t Index32;

typedef Index32 AttrIndex;
typedef Index32 ErrorIndex;
typedef Index32 MarkerIndex;
typedef Index32 ParamIndex;

}  // namespace mmsolver
