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

#pragma once

#include <mmimage/mmimage.h>

#include <string>

std::string join_path(const char *arg1, const char *arg2);
std::string join_path(const char *arg1, const char *arg2, const char *arg3);
std::string join_path(const char *arg1, const char *arg2, const char *arg3,
                      const char *arg4);

bool test_print_metadata_named_attributes(const char *test_name,
                                          mmimage::ImageMetaData &meta_data);

bool test_print_metadata_fields(const char *test_name,
                                mmimage::ImageMetaData &meta_data);
