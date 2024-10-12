/*
 * Copyright (C) 2020, 2024 David Cattermole.
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
 * Unchanging texture data to be used as hard-coded images that are
 * embedded in mmSolver.
 */

#ifndef MM_SOLVER_CONSTANT_TEXTURE_DATA_H
#define MM_SOLVER_CONSTANT_TEXTURE_DATA_H

namespace mmsolver {

/*
 * Color Bars Texture, for debug.
 *
 * https://en.wikipedia.org/wiki/SMPTE_color_bars
 *
 * ------------------------------
 *  R  -  G  -  B   - COLOR NAME
 * ------------------------------
 * 235 - 235 - 235  - 100% White
 * 180 - 180 - 180  - 75% White
 * 235 - 235 - 16   - Yellow
 * 16  - 235 - 235  - Cyan
 * 16  - 235 - 16   - Green
 * 235 - 16  - 235  - Magenta
 * 235 - 16  - 16   - Red
 * 16  - 16  - 235  - Blue
 * 16  - 16  - 16   - Black
 * ------------------------------
 *
 * The texture block (below) starts at the lower-left (zeroth index)
 * and continues the upper-right (last index).
 *
 * Note: To make things even (only 8 entries), we skip the "75% white"
 * value.
 */
static const float COLOR_BARS_F32_4X4[] = {
    // Row 0
    //
    // 235, 16, 235  - Magenta
    0.9215f, 0.0627f, 0.9215f, 1.0f,

    // 235, 16, 16   - Red
    0.9215f, 0.0627f, 0.0627f, 1.0f,

    // 16, 16, 235   - Blue
    0.0627f, 0.0627f, 0.9215f, 1.0f,

    // 16, 16, 16    - Black
    0.0627f, 0.0627f, 0.0627f, 1.0f,

    // Row 1
    //
    // 235, 16, 235  - Magenta
    0.9215f, 0.0627f, 0.9215f, 0.8f,

    // 235, 16, 16   - Red
    0.9215f, 0.0627f, 0.0627f, 0.6f,

    // 16, 16, 235   - Blue
    0.0627f, 0.0627f, 0.9215f, 0.4f,

    // 16, 16, 16    - Black
    0.0627f, 0.0627f, 0.0627f, 0.2f,

    // Row 2
    //
    // 235, 235, 235 - 100% White
    0.9215f, 0.9215f, 0.9215f, 1.0f,

    // 235, 235, 16  - Yellow
    0.9215f, 0.9215f, 0.0627f, 1.0f,

    // 16, 235, 235  - Cyan
    0.0627f, 0.9215f, 0.9215f, 1.0f,

    // 16, 235, 16   - Green
    0.0627f, 0.9215f, 0.0627f, 1.0f,

    // Row 3
    //
    // 235, 235, 235 - 100% White
    0.9215f, 0.9215f, 0.9215f, 0.2f,

    // 235, 235, 16  - Yellow
    0.9215f, 0.9215f, 0.0627f, 0.4f,

    // 16, 235, 235  - Cyan
    0.0627f, 0.9215f, 0.9215f, 0.6f,

    // 16, 235, 16   - Green
    0.0627f, 0.9215f, 0.0627f, 0.8f};
static const uint32_t COLOR_BARS_F32_4X4_PIXEL_WIDTH = 4;
static const uint32_t COLOR_BARS_F32_4X4_PIXEL_HEIGHT = 4;
static const uint32_t COLOR_BARS_F32_4X4_PIXEL_COUNT =
    COLOR_BARS_F32_4X4_PIXEL_WIDTH * COLOR_BARS_F32_4X4_PIXEL_HEIGHT;
static const uint32_t COLOR_BARS_F32_4X4_CHANNEL_COUNT = 4;
// float data type has 4 bytes.
static const uint32_t COLOR_BARS_F32_4X4_CHANNEL_BYTE_COUNT = 4;
static const uint32_t COLOR_BARS_F32_4X4_PIXEL_BYTE_COUNT =
    COLOR_BARS_F32_4X4_CHANNEL_COUNT * COLOR_BARS_F32_4X4_CHANNEL_BYTE_COUNT;

}  // namespace mmsolver

#endif  // MM_SOLVER_CONSTANT_TEXTURE_DATA_H
