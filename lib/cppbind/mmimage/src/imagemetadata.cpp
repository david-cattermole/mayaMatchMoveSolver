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

#include <mmimage/imagemetadata.h>
#include <mmimage/lib.h>

#include <iostream>
#include <string>

namespace mmimage {

ImageMetaData::ImageMetaData() noexcept
    : inner_(shim_create_image_meta_data_box()) {}

rust::Box<ShimImageMetaData> ImageMetaData::get_inner() noexcept {
    return std::move(inner_);
}

void ImageMetaData::set_inner(rust::Box<ShimImageMetaData> &value) noexcept {
    inner_ = std::move(value);
    return;
}

ImageRegionRectangle ImageMetaData::get_display_window() noexcept {
    return inner_->get_display_window();
}

float ImageMetaData::get_pixel_aspect() noexcept {
    return inner_->get_pixel_aspect();
}

rust::Str ImageMetaData::get_layer_name() noexcept {
    return inner_->get_layer_name();
}

Vec2I32 ImageMetaData::get_layer_position() noexcept {
    return inner_->get_layer_position();
}

Vec2F32 ImageMetaData::get_screen_window_center() noexcept {
    return inner_->get_screen_window_center();
}

float ImageMetaData::get_screen_window_width() noexcept {
    return inner_->get_screen_window_width();
}

rust::Str ImageMetaData::get_owner() noexcept { return inner_->get_owner(); }

rust::Str ImageMetaData::get_comments() noexcept {
    return inner_->get_comments();
}

rust::Str ImageMetaData::get_capture_date() noexcept {
    return inner_->get_capture_date();
}

OptionF32 ImageMetaData::get_utc_offset() noexcept {
    return inner_->get_utc_offset();
}

OptionF32 ImageMetaData::get_longitude() noexcept {
    return inner_->get_longitude();
}

OptionF32 ImageMetaData::get_latitude() noexcept {
    return inner_->get_latitude();
}

OptionF32 ImageMetaData::get_altitude() noexcept {
    return inner_->get_altitude();
}

OptionF32 ImageMetaData::get_focus() noexcept { return inner_->get_focus(); }

OptionF32 ImageMetaData::get_exposure() noexcept {
    return inner_->get_exposure();
}

OptionF32 ImageMetaData::get_aperture() noexcept {
    return inner_->get_aperture();
}

OptionF32 ImageMetaData::get_iso_speed() noexcept {
    return inner_->get_iso_speed();
}

OptionF32 ImageMetaData::get_frames_per_second() noexcept {
    return inner_->get_frames_per_second();
}

rust::Vec<rust::String> ImageMetaData::all_named_attribute_names() noexcept {
    return inner_->all_named_attribute_names();
}

bool ImageMetaData::has_named_attribute(rust::Str &attribute_name) noexcept {
    return inner_->has_named_attribute(attribute_name);
}

uint8_t ImageMetaData::get_named_attribute_type_index(
    rust::Str &attribute_name) noexcept {
    return inner_->get_named_attribute_type_index(attribute_name);
}

int32_t ImageMetaData::get_named_attribute_as_i32(
    rust::Str &attribute_name) noexcept {
    return inner_->get_named_attribute_as_i32(attribute_name);
}

float ImageMetaData::get_named_attribute_as_f32(
    rust::Str &attribute_name) noexcept {
    return inner_->get_named_attribute_as_f32(attribute_name);
}

double ImageMetaData::get_named_attribute_as_f64(
    rust::Str &attribute_name) noexcept {
    return inner_->get_named_attribute_as_f64(attribute_name);
}

rust::String ImageMetaData::get_named_attribute_as_string(
    rust::Str &attribute_name) noexcept {
    return inner_->get_named_attribute_as_string(attribute_name);
}

rust::String ImageMetaData::as_string() noexcept { return inner_->as_string(); }

}  // namespace mmimage
