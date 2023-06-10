/*
 * Copyright (C) 2020, 2021, 2023 David Cattermole.
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

#pragma once

#include <iostream>

namespace mmlens {

// enum class LensModelState {
//     kUninitialized = 0,
//     kClean = 1,
//     kDirty = 2,
//     kNumLensModelState,
// };

// // Warning: Do not change the numbers assigned to the different
// // types. These numbers are exposed to the user via the
// // "mmLensModel3de" node, with attribute 'lensModel'.
// enum class LensModelType {
//     // The lens model type is uninitialized.
//     kUninitialized = 0,

//     // Does nothing but passes through to the next lens model (if
//     // there is one).
//     kPassthrough = 1,

//     // "3DE Classic LD Model"
//     k3deClassic = 2,

//     // "3DE4 Radial - Standard, Degree 4"
//     k3deRadialStdDeg4 = 3,

//     // "3DE4 Anamorphic - Standard, Degree 4"
//     k3deAnamorphicStdDeg4 = 4,

//     // "3DE4 Anamorphic - Rescaled, Degree 4"
//     k3deAnamorphicStdDeg4Rescaled = 5,

//     // // "3DE4 Anamorphic - Standard, Degree 6"
//     // k3deAnamorphicStdDeg4 = 6,

//     // // "3DE4 Anamorphic - Rescaled, Degree 6"
//     // k3deAnamorphicStdDeg4Rescaled = 7,

//     // // "3DE4 Anamorphic, Degree 6"
//     // k3deAnamorphicDeg6 = 8,

//     kNumLensModelType,
// };

}  // namespace mmlens
