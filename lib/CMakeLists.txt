# Copyright (C) 2023, 2024, 2025 David Cattermole.
#
# This file is part of mmSolver.
#
# mmSolver is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# mmSolver is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
# ---------------------------------------------------------------------
#

cmake_minimum_required(VERSION 3.15)

# TODO: This relies on the '${mmsolverlibs_rust_DIR}' variable being set,
# which is not ideal at all. Instead this should be a default value
# (such as "/path/to/rust/build/directory/").
set(MMSOLVERLIBS_LIB_DIR "${mmsolverlibs_rust_DIR}" CACHE PATH
  "The path to the directory containing the compiled library.")

# Add custom modules to the module path.
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH}
  ${CMAKE_CURRENT_SOURCE_DIR}/../share/cmake/modules
  ${CMAKE_CURRENT_SOURCE_DIR}/share/cmake/modules)

set(cpp_lib_name "mmsolverlibs_cpp")
set(rust_lib_name "mmsolverlibs_rust")

include(MMCommonUtils)
option(MMSOLVER_DEBUG "Enable mmSolver debug mode; prints details and enables debug assertions." OFF)
mm_common_set_global_compile_options(MMSOLVER_DEBUG)

include(MMRustUtils)
set(rust_linktime_file "NOT-FOUND")
mm_rust_find_rust_library(${rust_lib_name} ${MMSOLVERLIBS_LIB_DIR} rust_linktime_file)
message(STATUS "Rust Linktime Library: ${rust_linktime_file}")
if(NOT EXISTS "${rust_linktime_file}")
  message(FATAL_ERROR "mmsolverlibs rust linktime library was not found.")
endif()

set(rust_depend_on_libraries "NOT-FOUND")
mm_rust_get_depend_on_libraries(rust_depend_on_libraries)
message(STATUS "Rust Depend On Libraries: ${rust_depend_on_libraries}")

# Build options for mmsolverlibs dependencies are inherited from
# parent scope.

# Set up vendored Eigen variables for external dependencies that need
# them.
set(eigen_vendored_dir "${CMAKE_CURRENT_SOURCE_DIR}/thirdparty/eigen")
if(EXISTS "${eigen_vendored_dir}")
  set(Eigen3_FOUND TRUE)
  set(Eigen3_VERSION "3.4.0")
  set(Eigen3_INCLUDE_DIR "${eigen_vendored_dir}")
  set(Eigen3_INCLUDE_DIRS "${eigen_vendored_dir}")
  message(STATUS "Set up vendored Eigen variables for dependencies: ${eigen_vendored_dir}")
endif()

add_subdirectory(thirdparty)

# Finds and builds external (third-party) dependencies for
# mmsolverlibs.
include(FindAndBuildMmsolverDependencies)

# Finds and builds external (third-party) LDPK dependencies.
include(FindAndBuildLdpkPackages)
add_subdirectory(mmsolverlibs/src)

option(MMSOLVERLIBS_BUILD_TESTS "Do you want to build the test files for mmsolverlibs?" OFF)
if (MMSOLVERLIBS_BUILD_TESTS)
  add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/cppbind/mmlens/tests)
  add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/cppbind/mmimage/tests)
  add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/cppbind/mmscenegraph/tests)
endif()
