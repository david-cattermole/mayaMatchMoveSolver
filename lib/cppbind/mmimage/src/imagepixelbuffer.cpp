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

#include <mmimage/imagepixeldata.h>
#include <mmimage/lib.h>

#include <iostream>
#include <string>

namespace mmimage {

ImagePixelBuffer::ImagePixelBuffer() noexcept
    : inner_(shim_create_image_pixel_buffer_box()) {}

rust::Box<ShimImagePixelBuffer> ImagePixelBuffer::get_inner() noexcept {
    return std::move(inner_);
}

void ImagePixelBuffer::set_inner(
    rust::Box<ShimImagePixelBuffer> &value) noexcept {
    inner_ = std::move(value);
    return;
}

BufferDataType ImagePixelBuffer::data_type() noexcept {
    return inner_->data_type();
}

size_t ImagePixelBuffer::image_width() noexcept {
    return inner_->image_width();
}

size_t ImagePixelBuffer::image_height() noexcept {
    return inner_->image_height();
}

size_t ImagePixelBuffer::num_channels() noexcept {
    return inner_->num_channels();
}

size_t ImagePixelBuffer::element_count() noexcept {
    return inner_->element_count();
}

size_t ImagePixelBuffer::pixel_count() noexcept {
    return inner_->pixel_count();
}

void ImagePixelBuffer::resize(const BufferDataType data_type,
                              const size_t image_width,
                              const size_t image_height,
                              const size_t num_channels) noexcept {
    return inner_->resize(data_type, image_width, image_height, num_channels);
}

const rust::Slice<const PixelF32x4>
ImagePixelBuffer::as_slice_f32x4() noexcept {
    return inner_->as_slice_f32x4();
}

rust::Slice<PixelF32x4> ImagePixelBuffer::as_slice_f32x4_mut() noexcept {
    return inner_->as_slice_f32x4_mut();
}

}  // namespace mmimage
