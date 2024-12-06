# Copyright (C) 2020, 2021, 2022, 2024 David Cattermole.
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
# CMake Build script for Science-D-Vision's Lens Distortion Plugin
# Kit.
#
cmake_minimum_required(VERSION 3.0)


# Project configuration.
project(ldpk)
set(PROJECT_VERSION_MAJOR 2)
set(PROJECT_VERSION_MINOR 12)
set(PROJECT_VERSION_PATCH 0)
set(PROJECT_VERSION "${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}")
set(PROJECT_HOMEPAGE_URL "https://www.3dequalizer.com/?site=tech_docs")
set(PROJECT_COPYRIGHT "Science-D-Visions, (c) 2011 - 2024")

include(GNUInstallDirs)

# Base LPDK ("header-only") library
add_library(ldpk INTERFACE)
target_include_directories(ldpk
  INTERFACE
  "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>"
  "$<INSTALL_INTERFACE:include>"
  )
install(TARGETS ldpk
  EXPORT ldpk-targets
  RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}"
  LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}"
  ARCHIVE DESTINATION "${CMAKE_INSTALL_LIBDIR}"
  INCLUDES DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}"
)
install(EXPORT ldpk-targets
  FILE ldpk-targets.cmake
  NAMESPACE ldpk::
  DESTINATION "${CMAKE_INSTALL_LIBDIR}/cmake/ldpk"
)

# Install headers
install(DIRECTORY
  ${CMAKE_CURRENT_SOURCE_DIR}/include/
  DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}"
  FILES_MATCHING PATTERN "*.h"
)

# Correctly export the location of installed includes in the target
target_include_directories(ldpk INTERFACE $<INSTALL_INTERFACE:include>)

# Export the targets to the build tree.
export(EXPORT ldpk-targets
  NAMESPACE ldpk::
  FILE "${CMAKE_CURRENT_BINARY_DIR}/cmake/ldpk-targets.cmake"
)

# Write the CMake config file
set(CMAKE_CONF_INSTALL_DIR "${CMAKE_INSTALL_DATAROOTDIR}/ldpk")
set(INCLUDE_INSTALL_DIR ${CMAKE_INSTALL_INCLUDEDIR})
include(CMakePackageConfigHelpers)
configure_package_config_file(
  ${CMAKE_CURRENT_SOURCE_DIR}/ldpk-config.cmake.in
  ${CMAKE_CURRENT_BINARY_DIR}/ldpk-config.cmake
  INSTALL_DESTINATION ${CMAKE_CONF_INSTALL_DIR}
  PATH_VARS INCLUDE_INSTALL_DIR
  NO_CHECK_REQUIRED_COMPONENTS_MACRO
)

# Install the targets (install)
install(EXPORT ldpk-targets
        FILE ldpk-targets.cmake
        NAMESPACE ldpk::
        DESTINATION ${CMAKE_CONF_INSTALL_DIR}
)

# Install the CMake config file
install(FILES
  ${CMAKE_CURRENT_BINARY_DIR}/ldpk-config.cmake
  DESTINATION ${CMAKE_CONF_INSTALL_DIR}
)
