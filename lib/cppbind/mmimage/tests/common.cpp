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

#include <mmimage/mmimage.h>

#include <algorithm>
#include <iostream>
#include <sstream>
#include <string>

std::string join_path(const char *arg1, const char *arg2) {
    std::stringstream stream;
    stream << arg1;
    stream << arg2;
    return stream.str();
}

std::string join_path(const char *arg1, const char *arg2, const char *arg3) {
    std::stringstream stream;
    stream << arg1;
    stream << arg2;
    stream << arg3;
    return stream.str();
}

std::string join_path(const char *arg1, const char *arg2, const char *arg3,
                      const char *arg4) {
    std::stringstream stream;
    stream << arg1;
    stream << arg2;
    stream << arg3;
    stream << arg4;
    return stream.str();
}

bool test_print_metadata_named_attributes(const char *test_name,
                                          mmimage::ImageMetaData &meta_data) {
    rust::Vec<rust::String> all_attr_names =
        meta_data.all_named_attribute_names();

    std::cout << test_name << " attrs count: " << all_attr_names.size()
              << std::endl;
    for (auto value : all_attr_names) {
        std::cout << test_name << " attr_name: " << value.c_str() << std::endl;
    }
    return true;
}

bool test_print_metadata_fields(const char *test_name,
                                mmimage::ImageMetaData &meta_data) {
    float image_pixel_aspect = meta_data.get_pixel_aspect();
    mmimage::ImageRegionRectangle image_display_window =
        meta_data.get_display_window();
    rust::Str image_layer_name = meta_data.get_layer_name();
    mmimage::Vec2I32 image_layer_position = meta_data.get_layer_position();
    mmimage::Vec2F32 image_screen_window_center =
        meta_data.get_screen_window_center();
    float image_screen_window_width = meta_data.get_screen_window_width();
    rust::Str image_owner = meta_data.get_owner();
    rust::Str image_comments = meta_data.get_comments();
    rust::Str image_capture_date = meta_data.get_capture_date();
    mmimage::OptionF32 image_utc_offset = meta_data.get_utc_offset();
    mmimage::OptionF32 image_longitude = meta_data.get_longitude();
    mmimage::OptionF32 image_latitude = meta_data.get_latitude();
    mmimage::OptionF32 image_altitude = meta_data.get_altitude();
    mmimage::OptionF32 image_focus = meta_data.get_focus();
    mmimage::OptionF32 image_exposure = meta_data.get_exposure();
    mmimage::OptionF32 image_aperture = meta_data.get_aperture();
    mmimage::OptionF32 image_iso_speed = meta_data.get_iso_speed();
    mmimage::OptionF32 image_frames_per_second =
        meta_data.get_frames_per_second();
    std::cout << test_name << " image pixel_aspect: " << image_pixel_aspect
              << std::endl
              << test_name
              << " image display_window: " << image_display_window.position_x
              << ',' << image_display_window.position_y << ','
              << image_display_window.size_x << ','
              << image_display_window.size_y << std::endl
              << test_name << " image owner: " << image_owner << std::endl
              << test_name << " image comments: " << image_comments << std::endl
              << test_name << " image capture_date: " << image_capture_date
              << std::endl
              << test_name << " image utc_offset: " << image_utc_offset
              << std::endl
              << test_name << " image longitude: " << image_longitude
              << std::endl
              << test_name << " image latitude: " << image_latitude << std::endl
              << test_name << " image altitude: " << image_altitude << std::endl
              << test_name << " image focus: " << image_focus << std::endl
              << test_name << " image exposure: " << image_exposure << std::endl
              << test_name << " image aperture: " << image_aperture << std::endl
              << test_name << " image iso_speed: " << image_iso_speed
              << std::endl
              << test_name
              << " image frames_per_second: " << image_frames_per_second
              << std::endl;

    return true;
}
