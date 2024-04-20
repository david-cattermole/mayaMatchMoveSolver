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
 */

#ifndef MM_SOLVER_LENS_DISTORTION_CONSTANTS_H
#define MM_SOLVER_LENS_DISTORTION_CONSTANTS_H

const char* TOOL_EXECUTABLE_NAME = "mmsolver-lensdistortion";
const char* TOOL_DESCRIPTION = "Create lens distortion ST-Maps.";
const char* EXR_METADATA_SOFTWARE_NAME = "mayaMatchMoveSolver (mmSolver)";

// The coordinates around the edges of an image bounding box. These
// coordinates are used to sample the lens distortion at the edges to
// find the maximum/minimum extent of the distorted bounding box.
const size_t BOUNDING_BOX_COORD_COUNT = 32;
const double BOUNDING_BOX_IDENTITY_COORDS[BOUNDING_BOX_COORD_COUNT * 2] = {
    // Bottom Edge
    -0.5, -0.5,    //
    -0.375, -0.5,  //
    -0.25, -0.5,   //
    -0.125, -0.5,  //
    0.0, -0.5,     //
    0.125, -0.5,   //
    0.25, -0.5,    //
    0.375, -0.5,   //
    0.5, -0.5,     //

    // Left Edge
    -0.5, -0.375,  //
    -0.5, -0.25,   //
    -0.5, -0.125,  //
    -0.5, 0.0,     //
    -0.5, 0.125,   //
    -0.5, 0.25,    //
    -0.5, 0.375,   //
    -0.5, 0.5,     //

    // Right Edge
    -0.375, 0.5,  //
    -0.25, 0.5,   //
    -0.125, 0.5,  //
    0.0, 0.5,     //
    0.125, 0.5,   //
    0.25, 0.5,    //
    0.375, 0.5,   //

    // Top Edge   //
    0.5, -0.375,  //
    0.5, -0.25,   //
    0.5, -0.125,  //
    0.5, 0.0,     //
    0.5, 0.125,   //
    0.5, 0.25,    //
    0.5, 0.375,   //
    0.5, 0.5,     //
};

#endif  // MM_SOLVER_LENS_DISTORTION_CONSTANTS_H
