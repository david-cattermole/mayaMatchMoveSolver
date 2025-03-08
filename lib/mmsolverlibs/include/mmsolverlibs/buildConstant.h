/*
 * Copyright (C) 2019, 2025 David Cattermole.
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
 * ===================================================================
 *
 * This file lists fields with build info for the mmSolverLibs
 * project.
 */

#ifndef MM_SOLVER_LIBS_BUILD_CONSTANT_H
#define MM_SOLVER_LIBS_BUILD_CONSTANT_H

namespace mmsolverlibs {
namespace build_info {

const char* const project_name();

const char* const project_version_major();
const char* const project_version_minor();
const char* const project_version_patch();
const char* const project_version_tweak();
const char* const project_version();

const char* const project_homepage_url();
const char* const project_description();
const char* const project_author();
const char* const project_copyright();

const char* const source_dir();
const char* const build_date_time();
const char* const git_branch();
const char* const git_commit_hash_long();
const char* const git_commit_hash_short();

const char* const cxx_compiler();
const char* const cxx_linker();

}  // namespace build_info
}  // namespace mmsolverlibs

#endif  // MM_SOLVER_LIBS_BUILD_CONSTANT_H
