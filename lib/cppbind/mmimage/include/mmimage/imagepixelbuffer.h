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

#ifndef MM_IMAGE_IMAGE_PIXEL_BUFFER_H
#define MM_IMAGE_IMAGE_PIXEL_BUFFER_H

#include <memory>
#include <string>

#include "_cxx.h"
#include "_cxxbridge.h"
#include "_symbol_export.h"
#include "_types.h"

namespace mmimage {

class ImagePixelBuffer {
public:
    MMIMAGE_API_EXPORT
    ImagePixelBuffer() noexcept;

    MMIMAGE_API_EXPORT
    rust::Box<ShimImagePixelBuffer> get_inner() noexcept;

    MMIMAGE_API_EXPORT
    void set_inner(rust::Box<ShimImagePixelBuffer> &value) noexcept;

    MMIMAGE_API_EXPORT
    BufferDataType data_type() noexcept;

    MMIMAGE_API_EXPORT
    size_t image_width() noexcept;

    MMIMAGE_API_EXPORT
    size_t image_height() noexcept;

    MMIMAGE_API_EXPORT
    size_t num_channels() noexcept;

    MMIMAGE_API_EXPORT
    size_t element_count() noexcept;

    MMIMAGE_API_EXPORT
    size_t pixel_count() noexcept;

    MMIMAGE_API_EXPORT
    const rust::Slice<const PixelF32x4> as_slice_f32x4() noexcept;

    MMIMAGE_API_EXPORT
    rust::Slice<PixelF32x4> as_slice_f32x4_mut() noexcept;

    MMIMAGE_API_EXPORT
    void resize(const BufferDataType data_type, const size_t image_width,
                const size_t image_height, const size_t num_channels) noexcept;

private:
    rust::Box<ShimImagePixelBuffer> inner_;
};

}  // namespace mmimage

#endif  // MM_IMAGE_IMAGE_PIXEL_BUFFER_H
