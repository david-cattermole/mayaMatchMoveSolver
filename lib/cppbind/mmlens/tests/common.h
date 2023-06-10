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

#include <mmlens/mmlens.h>

#include <algorithm>
#include <iostream>

const int kCoordinateSystemImage = 0;
const int kCoordinateSystemNDC = 1;

const int kDirectionUndistort = 0;
const int kDirectionRedistort = 1;

// Generate an "identity" ST-Map.
template <int COORDINATE_SYSTEM, typename T, bool DO_PRINT>
std::vector<T> generate_st_map_identity(const char* prefix_text,
                                        const size_t width, const size_t height,
                                        const size_t num_channels) {
    const size_t total_count = width * height;
    std::vector<T> buffer_data(total_count * num_channels);

    for (auto row = 0; row < height; row++) {
        for (auto column = 0; column < width; column++) {
            const size_t index =
                (row * width * num_channels) + (column * num_channels);
            const size_t index_x = index + 0;
            const size_t index_y = index + 1;

            // 0.0 to 1.0 in X and Y.
            T x = static_cast<T>(column) / static_cast<T>(width - 1);
            T y = static_cast<T>(row) / static_cast<T>(height - 1);

            const char* coordinate_system_text;
            if (COORDINATE_SYSTEM == kCoordinateSystemImage) {
                // Image Coordinates; 0.0 to 1.0.
                coordinate_system_text = "image";
                buffer_data[index_x] = x;
                buffer_data[index_y] = y;
            } else {
                // Normalized Device Coordinates; -0.5 to 0.5.
                coordinate_system_text = "NDC";
                x = -0.5 + x;
                y = -0.5 + y;
                buffer_data[index_x] = x;
                buffer_data[index_y] = y;
            }

            if (DO_PRINT) {
                // '\n' is used explicitly to avoid the std::flush that
                // happens when std::endl is used.
                std::cout << prefix_text << ' ' << coordinate_system_text
                          << " X : " << index_x << " : " << x << '\n'
                          << prefix_text << ' ' << coordinate_system_text
                          << " Y : " << index_y << " : " << y << '\n';
            }
        }
    }

    return buffer_data;
}

// Undistort (or re-distort) the input buffer, and write the result to
// the output buffer.
template <typename T1, typename T2, typename LENS_TYPE, int DIRECTION>
void apply_distortion_loop(const size_t width, const size_t height,
                           const size_t num_channels1,
                           const size_t num_channels2, const T1* in_buffer_data,
                           T2* out_buffer_data, LENS_TYPE& lens) {
    for (auto row = 0; row < height; row++) {
        for (auto column = 0; column < width; column++) {
            const size_t index1 =
                (row * width * num_channels1) + (column * num_channels1);
            const size_t index2 =
                (row * width * num_channels2) + (column * num_channels2);

            const size_t index1_x = index1 + 0;
            const size_t index1_y = index1 + 1;
            const size_t index2_x = index2 + 0;
            const size_t index2_y = index2 + 1;

            const double x = in_buffer_data[index1_x];
            const double y = in_buffer_data[index1_y];

            auto out_x = x;
            auto out_y = y;
            if (DIRECTION == kDirectionUndistort) {
                lens.applyModelUndistort(x, y, out_x, out_y);
            } else {
                lens.applyModelDistort(x, y, out_x, out_y);
            }

            out_buffer_data[index2_x] = out_x;
            out_buffer_data[index2_y] = out_y;
        }
    }
}

template <typename T>
void print_data_2d(const char* prefix_text, const size_t width,
                   const size_t height, const size_t num_channels,
                   const T* buffer_data) {
    for (auto row = 0; row < height; row++) {
        for (auto column = 0; column < width; column++) {
            const size_t index =
                (row * width * num_channels) + (column * num_channels);
            const size_t index_x = index + 0;
            const size_t index_y = index + 1;

            auto x = buffer_data[index_x];
            auto y = buffer_data[index_y];

            // '\n' is used explicitly to avoid the std::flush that
            // happens when std::endl is used.
            std::cout << prefix_text << " X : " << index_x << " : " << x << '\n'
                      << prefix_text << " Y : " << index_y << " : " << y
                      << '\n';
        }
    }
}

template <typename T1, typename T2>
void print_data_2d_compare(const char* prefix_text, const char* compare_text,
                           const size_t width, const size_t height,
                           const size_t num_channels1,
                           const size_t num_channels2, const T1* buffer_data1,
                           const T2* buffer_data2) {
    for (auto row = 0; row < height; row++) {
        for (auto column = 0; column < width; column++) {
            const size_t index1 =
                (row * width * num_channels1) + (column * num_channels1);
            const size_t index2 =
                (row * width * num_channels2) + (column * num_channels2);

            const size_t index1_x = index1 + 0;
            const size_t index1_y = index1 + 1;
            const size_t index2_x = index2 + 0;
            const size_t index2_y = index2 + 1;

            auto x1 = buffer_data1[index1_x];
            auto y1 = buffer_data1[index1_y];
            auto x2 = buffer_data2[index2_x];
            auto y2 = buffer_data2[index2_y];

            // '\n' is used explicitly to avoid the std::flush that
            // happens when std::endl is used.
            std::cout << prefix_text << " X : " << index1_x << '|' << index2_x
                      << " : " << x1 << compare_text << x2 << '\n'
                      << prefix_text << " Y : " << index1_y << '|' << index2_y
                      << " : " << y1 << compare_text << y2 << '\n';
        }
    }
}
