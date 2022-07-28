# Copyright (C) 2021 David Cattermole.
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
#

cmake_minimum_required(VERSION 3.15)

# Project configuration.
project(mmscenegraph)
set(PROJECT_VERSION_MAJOR 0)
set(PROJECT_VERSION_MINOR 1)
set(PROJECT_VERSION_PATCH 0)
set(PROJECT_VERSION_TWEAK 0)
set(PROJECT_VERSION "${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}.${PROJECT_VERSION_PATCH}.${PROJECT_VERSION_TWEAK}")
set(PROJECT_HOMEPAGE_URL "https://github.com/david-cattermole/mayaMatchMoveSolver")
set(PROJECT_DESCRIPTION "Optimised DAG Scene Graph for matchmove evaluation.")
set(PROJECT_AUTHOR "David Cattermole")
set(PROJECT_COPYRIGHT "2020-2022, David Cattermole.")

# Add custom modules to the module path
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH}
        ${CMAKE_CURRENT_SOURCE_DIR}/../share/cmake/modules)

add_subdirectory(cppbind)

include(GNUInstallDirs)

# Generate CMaka Targets file.
install(EXPORT mmscenegraphTargets
  FILE mmscenegraphTargets.cmake
  DESTINATION "${CMAKE_INSTALL_LIBDIR}/cmake/mmscenegraph"
  NAMESPACE mmscenegraph::
  )

# Generate and install a CMake target config files.
include(CMakePackageConfigHelpers)
configure_package_config_file(${CMAKE_CURRENT_SOURCE_DIR}/Config.cmake.in
  "${CMAKE_CURRENT_BINARY_DIR}/mmscenegraphConfig.cmake"
  INSTALL_DESTINATION "${CMAKE_INSTALL_LIBDIR}/cmake/mmscenegraph"
  )
write_basic_package_version_file(
  "${CMAKE_CURRENT_BINARY_DIR}/mmscenegraphConfigVersion.cmake"
  VERSION ${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}
  COMPATIBILITY AnyNewerVersion
  )
install(FILES
  "${CMAKE_CURRENT_BINARY_DIR}/mmscenegraphConfig.cmake"
  "${CMAKE_CURRENT_BINARY_DIR}/mmscenegraphConfigVersion.cmake"
  DESTINATION "${CMAKE_INSTALL_LIBDIR}/cmake/mmscenegraph")
export(EXPORT mmscenegraphTargets
  FILE "${CMAKE_INSTALL_LIBDIR}/mmscenegraphTargets.cmake"
  )
