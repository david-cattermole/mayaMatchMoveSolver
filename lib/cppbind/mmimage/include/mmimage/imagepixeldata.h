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

#ifndef MM_IMAGE_IMAGE_PIXEL_DATA_H
#define MM_IMAGE_IMAGE_PIXEL_DATA_H

#include <memory>
#include <string>

#include "_cxx.h"
#include "_cxxbridge.h"
#include "_symbol_export.h"
#include "_types.h"

namespace mmimage {

class ImagePixelDataRgbaF32 {
public:
    MMIMAGE_API_EXPORT
    ImagePixelDataRgbaF32() noexcept;

    MMIMAGE_API_EXPORT
    rust::Box<ShimImagePixelDataRgbaF32> get_inner() noexcept;

    MMIMAGE_API_EXPORT
    void set_inner(rust::Box<ShimImagePixelDataRgbaF32> &value) noexcept;

    MMIMAGE_API_EXPORT
    size_t width() noexcept;

    MMIMAGE_API_EXPORT
    size_t height() noexcept;

    MMIMAGE_API_EXPORT
    const rust::Slice<const PixelRgbaF32> data() noexcept;

    MMIMAGE_API_EXPORT
    rust::Slice<PixelRgbaF32> data_mut() noexcept;

private:
    rust::Box<ShimImagePixelDataRgbaF32> inner_;
};

class ImagePixelData2DF64 {
public:
    MMIMAGE_API_EXPORT
    ImagePixelData2DF64() noexcept;

    MMIMAGE_API_EXPORT
    rust::Box<ShimImagePixelData2DF64> get_inner() noexcept;

    MMIMAGE_API_EXPORT
    void set_inner(rust::Box<ShimImagePixelData2DF64> &value) noexcept;

    MMIMAGE_API_EXPORT
    size_t width() noexcept;

    MMIMAGE_API_EXPORT
    size_t height() noexcept;

    MMIMAGE_API_EXPORT
    const rust::Slice<const Pixel2DF64> data() noexcept;

    MMIMAGE_API_EXPORT
    rust::Slice<Pixel2DF64> data_mut() noexcept;

private:
    rust::Box<ShimImagePixelData2DF64> inner_;
};

}  // namespace mmimage

#endif  // MM_IMAGE_IMAGE_PIXEL_DATA_H
