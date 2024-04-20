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

#ifndef MM_SOLVER_LENS_DISTORTION_BUFFER_H
#define MM_SOLVER_LENS_DISTORTION_BUFFER_H

#include <mmimage/mmimage.h>

#include <vector>

class BufferSlice {
public:
    BufferSlice()
        : m_data_type(mmimage::BufferDataType::kNone)
        , m_data_ptr(nullptr)
        , m_image_width(0)
        , m_image_height(0)
        , m_num_channels(0) {}

    BufferSlice(const mmimage::BufferDataType data_type,
                const size_t image_width, const size_t image_height,
                const size_t num_channels, void* data_ptr)
        : m_data_type(data_type)
        , m_data_ptr(data_ptr)
        , m_image_width(image_width)
        , m_image_height(image_height)
        , m_num_channels(num_channels) {}

    mmimage::BufferDataType data_type() const noexcept { return m_data_type; }
    size_t image_width() const noexcept { return m_image_width; }
    size_t image_height() const noexcept { return m_image_height; }
    size_t num_channels() const noexcept { return m_num_channels; }

    size_t data_type_size() const noexcept {
        size_t count = 0;
        if (m_data_type == mmimage::BufferDataType::kNone) {
            // There is (conceptually) no size.
            count = 0;
        } else if (m_data_type == mmimage::BufferDataType::kF32) {
            count = sizeof(float);
        } else if (m_data_type == mmimage::BufferDataType::kF64) {
            count = sizeof(double);
        }
        return count;
    }

    size_t pixel_count() const noexcept {
        size_t count = 0;
        if (m_data_type == mmimage::BufferDataType::kNone) {
            // There is (conceptually) no count.
            count = 0;
        } else if (m_data_type == mmimage::BufferDataType::kF32) {
            count = m_image_width * m_image_height;
        } else if (m_data_type == mmimage::BufferDataType::kF64) {
            count = m_image_width * m_image_height;
        }
        return count;
    }

    size_t element_count() const noexcept {
        size_t count = 0;
        if (m_data_type == mmimage::BufferDataType::kNone) {
            // There is (conceptually) no count.
            count = 0;
        } else {
            count = m_image_width * m_image_height * m_num_channels;
        }
        return count;
    }

    void* data_mut() const noexcept { return m_data_ptr; }
    const void* data() const noexcept { return m_data_ptr; }

private:
    mmimage::BufferDataType m_data_type;
    void* m_data_ptr;
    size_t m_image_width;
    size_t m_image_height;
    size_t m_num_channels;
};

#endif  // MM_SOLVER_LENS_DISTORTION_BUFFER_H
