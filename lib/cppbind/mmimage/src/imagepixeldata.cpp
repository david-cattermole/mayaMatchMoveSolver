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

ImagePixelDataRgbaF32::ImagePixelDataRgbaF32() noexcept
    : inner_(shim_create_image_pixel_data_rgba_f32_box()) {}

rust::Box<ShimImagePixelDataRgbaF32>
ImagePixelDataRgbaF32::get_inner() noexcept {
    return std::move(inner_);
}

void ImagePixelDataRgbaF32::set_inner(
    rust::Box<ShimImagePixelDataRgbaF32> &value) noexcept {
    inner_ = std::move(value);
    return;
}

size_t ImagePixelDataRgbaF32::width() noexcept { return inner_->width(); }

size_t ImagePixelDataRgbaF32::height() noexcept { return inner_->height(); }

const rust::Slice<const PixelRgbaF32> ImagePixelDataRgbaF32::data() noexcept {
    return inner_->data();
}

rust::Slice<PixelRgbaF32> ImagePixelDataRgbaF32::data_mut() noexcept {
    return inner_->data_mut();
}

}  // namespace mmimage
