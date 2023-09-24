# Copyright (C) 2023 David Cattermole.
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

# Do not allow using GNU extensions (such as '-std=g++11'), because
# it's not compatible with Maya.
set(CXX_EXTENSIONS OFF)

# Project configuration.
project(mmsolverlibs)
set(PROJECT_VERSION_MAJOR 0)
set(PROJECT_VERSION_MINOR 1)
set(PROJECT_VERSION_PATCH 0)
set(PROJECT_VERSION_TWEAK 0)
set(PROJECT_VERSION "${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}.${PROJECT_VERSION_PATCH}.${PROJECT_VERSION_TWEAK}")
set(PROJECT_HOMEPAGE_URL "https://github.com/david-cattermole/mayaMatchMoveSolver")
set(PROJECT_DESCRIPTION "mmSolver libraries.")
set(PROJECT_AUTHOR "David Cattermole")
set(PROJECT_COPYRIGHT "2023, David Cattermole.")

set(MMSOLVERLIBS_LIB_DIR "/path/to/rust/build/directory/" CACHE PATH
  "The path to the directory containing the compiled library.")

# Add custom modules to the module path
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH}
  ${CMAKE_CURRENT_SOURCE_DIR}/../share/cmake/modules)

set(target_release_lib_name "mmsolverlibs")
set(rust_lib_name "mmsolverlibs_rust")

set(CMAKE_CXX_STANDARD 11)

include(MMSolverUtils)
set_global_maya_plugin_compile_options()

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

# Finds and builds external (third-party) LDPK dependencies.
option(MMSOLVER_DOWNLOAD_DEPENDENCIES "Automatically download and build missing dependencies?" ON)
include(FindAndBuildLdpkPackages)

add_subdirectory(mmsolverlibs/src)

option(MMSOLVERLIBS_BUILD_TESTS "Do you want to build the test files for mmsolverlibs?" OFF)
if (MMSOLVERLIBS_BUILD_TESTS)
  add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/cppbind/mmlens/tests)
  add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/cppbind/mmimage/tests)
  add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/cppbind/mmscenegraph/tests)
endif()

include(MMCommonUtils)
mm_common_add_install_target("mmsolverlibs" ${CMAKE_CURRENT_SOURCE_DIR}/Config.cmake.in)
