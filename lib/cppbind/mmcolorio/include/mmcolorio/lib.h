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

#ifndef MM_COLOR_IO_LIB_H
#define MM_COLOR_IO_LIB_H

// STL
#include <memory>
#include <string>
#include <vector>

#include "_symbol_export.h"
#include "_types.h"

namespace mmcolorio {

const char *get_config_name();
const char *get_config_description();
const char *get_config_search_path();
const char *get_config_working_directory();

bool color_space_name_exists(const char *color_space_name);

const char *guess_color_space_name_from_file_path(const char *file_path);

const char *get_role_color_space_name(const ColorSpaceRole value);

std::vector<std::string> get_color_space_names(
    const ColorSpaceVisibility visibility);

void generate_shader_text(const char *input_color_space_name,
                          const char *output_color_space_name,
                          std::string &out_shader_text);

}  // namespace mmcolorio

#endif  // MM_COLOR_IO_LIB_H
