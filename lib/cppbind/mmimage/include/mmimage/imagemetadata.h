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

#ifndef MM_IMAGE_IMAGE_META_DATA_H
#define MM_IMAGE_IMAGE_META_DATA_H

#include <memory>
#include <string>

#include "_cxx.h"
#include "_cxxbridge.h"
#include "_symbol_export.h"
#include "_types.h"

namespace mmimage {

class ImageMetaData {
public:
    MMIMAGE_API_EXPORT
    ImageMetaData() noexcept;

    MMIMAGE_API_EXPORT
    rust::Box<ShimImageMetaData> get_inner() noexcept;

    MMIMAGE_API_EXPORT
    void set_inner(rust::Box<ShimImageMetaData> &value) noexcept;

    MMIMAGE_API_EXPORT
    ImageRegionRectangle get_display_window() noexcept;

    MMIMAGE_API_EXPORT
    float get_pixel_aspect() noexcept;

    MMIMAGE_API_EXPORT
    rust::Str get_layer_name() noexcept;

    MMIMAGE_API_EXPORT
    Vec2I32 get_layer_position() noexcept;

    MMIMAGE_API_EXPORT
    Vec2F32 get_screen_window_center() noexcept;

    MMIMAGE_API_EXPORT
    float get_screen_window_width() noexcept;

    MMIMAGE_API_EXPORT
    rust::Str get_owner() noexcept;

    MMIMAGE_API_EXPORT
    rust::Str get_comments() noexcept;

    MMIMAGE_API_EXPORT
    rust::Str get_capture_date() noexcept;

    MMIMAGE_API_EXPORT
    OptionF32 get_utc_offset() noexcept;

    MMIMAGE_API_EXPORT
    OptionF32 get_longitude() noexcept;

    MMIMAGE_API_EXPORT
    OptionF32 get_latitude() noexcept;

    MMIMAGE_API_EXPORT
    OptionF32 get_altitude() noexcept;

    MMIMAGE_API_EXPORT
    OptionF32 get_focus() noexcept;

    MMIMAGE_API_EXPORT
    OptionF32 get_exposure() noexcept;

    MMIMAGE_API_EXPORT
    OptionF32 get_aperture() noexcept;

    MMIMAGE_API_EXPORT
    OptionF32 get_iso_speed() noexcept;

    MMIMAGE_API_EXPORT
    OptionF32 get_frames_per_second() noexcept;

    MMIMAGE_API_EXPORT
    rust::Vec<rust::String> all_named_attribute_names() noexcept;

    MMIMAGE_API_EXPORT
    bool has_named_attribute(rust::Str &attribute_name) noexcept;

    MMIMAGE_API_EXPORT
    uint8_t get_named_attribute_type_index(rust::Str &attribute_name) noexcept;

    MMIMAGE_API_EXPORT
    int32_t get_named_attribute_as_i32(rust::Str &attribute_name) noexcept;

    MMIMAGE_API_EXPORT
    float get_named_attribute_as_f32(rust::Str &attribute_name) noexcept;

    MMIMAGE_API_EXPORT
    double get_named_attribute_as_f64(rust::Str &attribute_name) noexcept;

    MMIMAGE_API_EXPORT
    rust::String get_named_attribute_as_string(
        rust::Str &attribute_name) noexcept;

    MMIMAGE_API_EXPORT
    rust::String as_string() noexcept;

private:
    rust::Box<ShimImageMetaData> inner_;
};

}  // namespace mmimage

#endif  // MM_IMAGE_IMAGE_META_DATA_H
